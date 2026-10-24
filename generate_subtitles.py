import sys
import re
import wave

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

def split_into_flash_chunks(text: str) -> list[str]:
    # Normalize
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = [l.strip() for l in text.split("\n") if l.strip()]

    chunks = []
    for line in raw_lines:
        # Split by punctuation (including commas and exclamation)
        parts = re.split(r'([。、，,！？!?]+)', line)
        current = ""
        for i in range(0, len(parts), 2):
            seg = parts[i].strip()
            punct = parts[i+1] if i+1 < len(parts) else ""
            comb = (seg + punct).strip()
            if not comb:
                continue
            
            # If a single segment is still too long (> 16 chars), split it intelligently
            if len(comb) > 16:
                # Split around Japanese particles or natural pause points
                sub_parts = re.split(r'(?<=[はがをにでとのからて])', comb)
                buf = ""
                for sp in sub_parts:
                    if len(buf) + len(sp) > 14 and len(buf) >= 4:
                        chunks.append(buf.strip())
                        buf = sp
                    else:
                        buf += sp
                if buf.strip():
                    chunks.append(buf.strip())
            else:
                chunks.append(comb)

    cleaned_chunks = []
    for c in chunks:
        c_str = c.strip()
        if not c_str:
            continue
        # If it's just punctuation, merge into previous chunk
        if re.fullmatch(r'[。、，,！？!?]+', c_str) and cleaned_chunks:
            cleaned_chunks[-1] += c_str
        else:
            cleaned_chunks.append(c_str)

    return cleaned_chunks

def generate_ass(japanese_text: str, total_duration: float, output_ass_path: str):
    chunks = split_into_flash_chunks(japanese_text)
    if not chunks:
        chunks = ["そんなことより", "聞いてくれよ１よ。"]

    weights = []
    styles = []

    # Iconic flash punchline markers
    impact_keywords = [
        "アホかと", "馬鹿かと", "ボケが", "小一時間問い詰めたい", "問いたい",
        "すっこんでろ", "諸刃の剣", "素人にはおすすめしない", "ってこった", "その席空けろと",
        "ぶち切れですよ"
    ]
    sub_impact_keywords = [
        "よーしパパ", "とりあえず", "言いたいだけちゃうんかと", "殺伐としてるべきなんだよ", "Criticalだよ", "Criticalだろうが"
    ]

    for c in chunks:
        # Base weight proportional to characters
        w = max(len(c), 3)

        is_impact = any(k in c for k in impact_keywords)
        is_sub_impact = any(k in c for k in sub_impact_keywords)

        if is_impact:
            styles.append("Impact")
            w *= 1.45
        elif is_sub_impact:
            styles.append("SubImpact")
            w *= 1.25
        else:
            styles.append("Default")

        weights.append(w)

    total_weight = sum(weights)
    
    start_sec = 0.4
    usable_duration = max(total_duration - 0.8, total_duration * 0.96)

    events = []
    for i, (chunk, weight, style) in enumerate(zip(chunks, weights, styles)):
        duration = (weight / total_weight) * usable_duration
        # Each short chunk lasts 0.8s - 3.5s
        duration = max(0.8, min(duration, 3.8))
        end_sec = min(start_sec + duration, total_duration)

        display_text = chunk
        # If chunk is still more than 14 chars, insert a line break \N
        if len(display_text) > 14:
            mid = len(display_text) // 2
            # Find best split near middle
            display_text = display_text[:mid] + "\\N" + display_text[mid:]

        if style == "Impact":
            display_text = f"{{\\b1}}{display_text}{{\\b0}}"

        start_str = format_ass_time(start_sec)
        end_str = format_ass_time(end_sec)

        events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{display_text}")
        start_sec = end_sec + 0.05  # snappy 50ms transition

    # ASS Header with early 2000s Flash typography
    # WrapStyle 2 = strict no overflow, PlayResX 1280
    ass_content = f"""[Script Info]
Title: Instant Gonorego Flash Subtitles
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
; Normal Dialog (Flash yellow with thick black outline at bottom center, generous margins)
Style: Default,Hiragino Sans,48,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,80,80,50,1
; Impact / Punchline Dialog (Iconic giant red text with white outline & heavy shadow dead center)
Style: Impact,Hiragino Sans,76,&H000000FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,105,105,1,0,1,6.5,4.0,5,60,60,40,1
; Sub-Impact Dialog (Amber orange emphasis at bottom center)
Style: SubImpact,Hiragino Sans,54,&H0000AAFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,3.0,2,80,80,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    print(f"=== Generated {len(events)} punchy Flash subtitle chunks to {output_ass_path} ===")

if __name__ == "__main__":
    jp_path = sys.argv[1] if len(sys.argv) > 1 else "input_japanese.txt"
    wav_path = sys.argv[2] if len(sys.argv) > 2 else "output.wav"
    out_ass = sys.argv[3] if len(sys.argv) > 3 else "subtitles.ass"

    with open(jp_path, "r", encoding="utf-8") as f:
        japanese_text = f.read()

    duration = get_audio_duration(wav_path)
    generate_ass(japanese_text, duration, out_ass)
