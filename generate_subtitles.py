import sys
import re
import wave
import os

def get_audio_duration(wav_path: str) -> float:
    try:
        with wave.open(wav_path, 'r') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return frames / float(rate)
    except Exception as e:
        print(f"Error reading wav duration: {e}")
        return 60.0

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def estimate_line_duration(romaji_line: str) -> float:
    # 1. Sum up all [[slnc <ms>]] tags
    slnc_ms = sum(int(m) for m in re.findall(r'\[\[slnc\s+(\d+)\]\]', romaji_line))

    # 2. Extract spoken text without tags
    clean_text = re.sub(r'\[\[[^\]]+\]\]', '', romaji_line).strip()
    
    # At Rate 128, roughly ~48ms per character for Whisper phonetic romaji
    speech_ms = len(clean_text) * 48.0

    # 3. Inter-line breath pause (~400ms)
    total_ms = slnc_ms + speech_ms + 400.0
    return total_ms / 1000.0

def split_japanese_line_into_chunks(ja_line: str) -> list[str]:
    # Split by punctuation (commas, periods, exclamation, questions)
    parts = re.split(r'([。、，,！？!?]+)', ja_line)
    chunks = []
    for i in range(0, len(parts), 2):
        seg = parts[i].strip()
        punct = parts[i+1] if i+1 < len(parts) else ""
        comb = (seg + punct).strip()
        if not comb:
            continue
        
        # If segment is still > 14 chars, split by particle
        if len(comb) > 14:
            sub_parts = re.split(r'(?<=[はがをにでとのからて])', comb)
            buf = ""
            for sp in sub_parts:
                if len(buf) + len(sp) > 13 and len(buf) >= 4:
                    chunks.append(buf.strip())
                    buf = sp
                else:
                    buf += sp
            if buf.strip():
                chunks.append(buf.strip())
        else:
            chunks.append(comb)

    # Merge isolated punctuation
    cleaned = []
    for c in chunks:
        c_str = c.strip()
        if not c_str:
            continue
        if re.fullmatch(r'[。、，,！？!?]+', c_str) and cleaned:
            cleaned[-1] += c_str
        else:
            cleaned.append(c_str)

    return cleaned if cleaned else [ja_line.strip()]

def generate_synchronized_subtitles(ja_path: str, romaji_path: str, wav_path: str, out_ass: str):
    with open(ja_path, "r", encoding="utf-8") as f:
        ja_raw = [l.strip() for l in f if l.strip()]

    # Read romaji script (ignore initial rate/pbas headers)
    ro_raw = []
    if os.path.exists(romaji_path):
        with open(romaji_path, "r", encoding="utf-8") as f:
            for l in f:
                l_s = l.strip()
                if l_s and not l_s.startswith("[[rate") and not l_s.startswith("[[pmod"):
                    ro_raw.append(l_s)

    actual_duration = get_audio_duration(wav_path)
    print(f"Total Audio Duration: {actual_duration:.2f}s | JA lines: {len(ja_raw)} | Romaji lines: {len(ro_raw)}")

    # Estimate duration for each line
    line_durations = []
    for i in range(len(ja_raw)):
        ro_line = ro_raw[i] if i < len(ro_raw) else ""
        if ro_line:
            d = estimate_line_duration(ro_line)
        else:
            # Fallback estimation based on JA characters + punctuation
            slnc_est = (ja_raw[i].count("、") * 220 + ja_raw[i].count("。") * 450) / 1000.0
            d = (len(ja_raw[i]) * 0.15) + slnc_est + 0.4
        line_durations.append(d)

    total_est = sum(line_durations)
    if total_est <= 0:
        total_est = 1.0

    # Scale to match actual audio duration exactly
    # Give a tiny 0.3s breath at the start and 0.5s at end
    effective_audio_time = max(actual_duration - 0.8, actual_duration * 0.96)
    scale = effective_audio_time / total_est

    # Flash punchline keywords
    impact_keywords = [
        "アホかと", "馬鹿かと", "ボケが", "小一時間問い詰めたい", "問いたい",
        "すっこんでろ", "諸刃の剣", "素人にはおすすめしない", "ってこった", "その席空けろと",
        "ぶち切れですよ"
    ]
    sub_impact_keywords = [
        "よーしパパ", "とりあえず", "言いたいだけちゃうんかと", "殺伐としてるべきなんだよ", "Criticalだよ", "Criticalだろうが"
    ]

    events = []
    current_line_start = 0.35 # start just as audio begins

    for i, (ja_line, est_dur) in enumerate(zip(ja_raw, line_durations)):
        actual_line_dur = est_dur * scale
        line_end = min(current_line_start + actual_line_dur, actual_duration)

        # Break line into short snappy chunks
        chunks = split_japanese_line_into_chunks(ja_line)
        chunk_weights = [max(len(c), 2) for c in chunks]
        total_chunk_weight = sum(chunk_weights)

        # Usable time within this line (leave small breath at line end)
        usable_line_time = max(actual_line_dur - 0.15, actual_line_dur * 0.9)
        c_start = current_line_start

        for c, w in zip(chunks, chunk_weights):
            c_dur = (w / total_chunk_weight) * usable_line_time
            c_end = min(c_start + c_dur, line_end)

            # Determine style
            is_impact = any(k in c for k in impact_keywords)
            is_sub = any(k in c for k in sub_impact_keywords)

            style = "Impact" if is_impact else ("SubImpact" if is_sub else "Default")
            disp_text = c
            if len(disp_text) > 13:
                mid = len(disp_text) // 2
                disp_text = disp_text[:mid] + "\\N" + disp_text[mid:]

            if style == "Impact":
                disp_text = f"{{\\b1}}{disp_text}{{\\b0}}"

            start_str = format_ass_time(c_start)
            end_str = format_ass_time(c_end)

            events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{disp_text}")
            c_start = c_end + 0.04

        current_line_start = line_end

    # Build ASS file
    ass_content = f"""[Script Info]
Title: Instant Gonorego Flash Subtitles (Synchronized)
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
; Normal Dialog (Flash yellow with thick black outline at bottom center)
Style: Default,Hiragino Sans,48,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,80,80,50,1
; Impact / Punchline Dialog (Iconic giant red text with white outline & heavy shadow dead center)
Style: Impact,Hiragino Sans,76,&H000000FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,105,105,1,0,1,6.5,4.0,5,60,60,40,1
; Sub-Impact Dialog (Amber orange emphasis at bottom center)
Style: SubImpact,Hiragino Sans,54,&H0000AAFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,3.0,2,80,80,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"

    with open(out_ass, "w", encoding="utf-8") as f:
        f.write(ass_content)

    print(f"=== Generated {len(events)} synchronized Flash subtitle events -> {out_ass} ===")

if __name__ == "__main__":
    jp_path = sys.argv[1] if len(sys.argv) > 1 else "input_japanese.txt"
    wav_path = sys.argv[2] if len(sys.argv) > 2 else "output.wav"
    out_ass = sys.argv[3] if len(sys.argv) > 3 else "subtitles.ass"
    romaji_path = sys.argv[4] if len(sys.argv) > 4 else "input_script_tuned.txt"

    generate_synchronized_subtitles(jp_path, romaji_path, wav_path, out_ass)
