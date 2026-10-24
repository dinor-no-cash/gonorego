import sys
import os
import re
import wave
import subprocess

def sanitize_whisper_phonetics(text: str) -> str:
    """Eliminate English phonics mispronunciations for macOS Whisper voice and enforce authentic Gonorego speech."""
    if not text:
        return ""
    r = text.strip()

    word_map = [
        # 冒頭の日本語残り防止
        (r'そんな事より聞いてくれよ(?:１|1|一)?よ?', "sonna koto yori kiite kureyo ichi yo"),
        (r'昨日', "kino"),
        (r'サイゼリヤ', "Saizeriya"),
        (r'サイゼ', "Saize"),

        # ★重要：英単語のカタカナ化誤爆を英語スペルへ完全復元★
        (r'\b(?:toransufaamazu|toransufaamaa)\b', "Transformers"),
        (r'トランスフォーマーズ?', "Transformers"),

        # ★重要：カタカナ語・外来語を英語スペルへ置換（Whisperネイティブ発音）★
        (r'ローカル', "local"),
        (r'\b(?:rookaaru|rokaru|ro-karu)\b', "local"),
        (r'コミュニティ', "community"),
        (r'\b(?:komyunitei|komyuniti)\b', "community"),
        (r'チュートリアル', "tutorial"),
        (r'\b(?:chyuutoriaru|chuutoriaru)\b', "tutorial"),
        (r'モデル', "model"),
        (r'\b(?:moderu|mode\s*ru)\b', "model"),
        (r'ハードウェア', "hardware"),
        (r'\b(?:haado\s*uea|haadowea)\b', "hardware"),
        (r'ソフトウェア', "software"),
        (r'\b(?:sofutouea|sofutowea)\b', "software"),
        (r'データセット', "dataset"),
        (r'\b(?:deeta\s*setto)\b', "dataset"),
        (r'カスタム', "custom"),
        (r'\b(?:kasutamu)\b', "custom"),
        (r'キュー', "queue"),
        (r'\b(?:kyuu)\b', "queue"),
        (r'ワイン', "wine"),
        (r'\b(?:wain|wah\s*een)\b', "wine"),
        (r'マーケティング', "marketing"),
        (r'\b(?:maketingu)\b', "marketing"),
        (r'グラス', "glass"),
        (r'\b(?:gurasu)\b', "glass"),
        (r'デカンタ', "decanter"),
        (r'\b(?:dekanta)\b', "decanter"),
        (r'コスト', "cost"),
        (r'\b(?:kosuto)\b', "cost"),
        (r'リスク', "risk"),
        (r'\b(?:risuku)\b', "risk"),
        (r'フルーツジュース', "fruit juice"),
        (r'\b(?:furu-tsu\s*ju-su|furuutsu\s*juusu)\b', "fruit juice"),
        (r'カベルネ・ソーヴィニヨン', "Cabernet Sauvignon"),
        (r'\b(?:kaberune\s*so-viniyon|kabuerune\s*souviniyon)\b', "Cabernet Sauvignon"),
        (r'ビオディナミック', "biodynamic"),
        (r'\b(?:biodinamikku)\b', "biodynamic"),
        (r'エンジニア', "engineer"),
        (r'セキュリティ', "security"),

        # ★重要：日本語の読み間違い・ゴノレゴ構文の厳格固定★
        (r'\b(?:toikurumetai|toitsumetai|toishimetai|toi\s*tsume\s*tai)\b', "toi tsume tai"),
        (r'問(?:い)?(?:詰|くる)めたい', "toi tsume tai"),
        (r'\b(?:sho\s*ichi\s*jikan|shoichijikan|shouichijikan|ko\s*ichi\s*jikan|koichijikan)\b', "ko ichi jikan"),
        (r'小一時間', "ko ichi jikan"),
        (r'\b(?:moro\s*no\s*yaiba|moronoyaiba|moroha\s*no\s*tsurugi|morohanotsurugi)\b', "moroha no tsurugi"),
        (r'諸刃の(?:剣|刃)', "moroha no tsurugi"),
        (r'\b(?:buchikire|buchi\s*kire|buchikeereh|buchi\s*kee\s*reh)\b', "buchi kee reh"),
        (r'(?:ブチ|ぶち)(?:切|き)れ', "buchi kee reh"),
        (r'\b(?:do\s*sujin|doshirouto|do\s*shirouto|doh\s*shee\s*roh\s*oo\s*toh)\b', "do shirouto"),
        (r'\b(?:sujin|shirouto|shee\s*roh\s*oo\s*toh)\b', "shirouto"),
        (r'ド素人', "do shirouto"),
        (r'素人', "shirouto"),
        (r'\b(?:hayari|hayarin|ryuukou|ryoukou)\b', "ryuukou"),
        (r'最新流行', "saishin ryuukou"),
        (r'流行', "ryuukou"),
        (r'\b(?:tsu)\b', "tsuu"),
        (r'ワイン通', "wine tsuu"),
        (r'通', "tsuu"),
        (r'\bichi\s*yo\b', "ichi yo"),
        (r'\b(?:tte\s+)?kotta\b', "tte kotta"),
        (r'\bboke\s*ga\b', "boke gah"),
        (r'\baho\s*ka\s*to\b', "aho kah toh"),
        (r'\bbaka\s*ka\s*to\b', "baka kah toh"),

        # 日本語ローマ字が英語フォニックスでサイレントE誤読される問題の防止
        (r'\bmade\b', "mah deh"),
        (r'\bmake\b', "mah keh"),
        (r'\bsake\b', "sah keh"),
        (r'\bname\b', "nah meh"),
        (r'\btame\b', "tah meh"),
        (r'\bsame\b', "sah meh"),
        (r'\bkame\b', "kah meh"),
        (r'\byome\b', "yoh meh"),
        (r'\bhime\b', "hee meh"),
        (r'\bdate\b', "dah teh"),
        (r'\blate\b', "rah teh"),
        (r'\bgate\b', "gah teh"),
        (r'\bhate\b', "hah teh"),
        (r'\bmate\b', "mah teh"),
        (r'\bkite\b', "kee teh"),
        (r'\bbite\b', "bee teh"),
        (r'\bsite\b', "shee teh"),
        (r'\bhome\b', "hoh meh"),
        (r'\bcome\b', "koh meh"),
        (r'\bsome\b', "soh meh"),
        (r'\btome\b', "toh meh"),
        (r'\brose\b', "roh seh"),
        (r'\bnose\b', "noh seh"),
        (r'\bcure\b', "koo reh"),
        (r'\bpure\b', "poo reh"),
        (r'\bsure\b', "soo reh"),
        (r'\brude\b', "roo deh"),
        (r'\btube\b', "tsoo beh"),
        (r'\bmore\b', "moh reh"),
        (r'\bsore\b', "soh reh"),
        (r'\bkore\b', "koh reh"),
        (r'\bare\b', "ah reh"),
        (r'\bore\b', "oh reh"),
        (r'\bomae\b', "oh mah eh"),
        (r'\bomae-ra\b', "oh mah eh rah"),
        (r'\bsono\b', "soh noh"),
        (r'\bsoko\b', "soh koh"),
        (r'\bakero\b', "ah keh roh"),
    ]

    for pat, rep in word_map:
        r = re.sub(pat, rep, r, flags=re.IGNORECASE)

    r = re.sub(r'[ \t]+', ' ', r)
    return r

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def get_wav_duration_and_params(wav_path: str):
    with wave.open(wav_path, 'rb') as w:
        frames = w.getnframes()
        rate = w.getframerate()
        params = w.getparams()
        duration = frames / float(rate)
        return duration, params

def create_silence_wav(out_wav: str, duration_sec: float, params):
    # params: (nchannels, sampwidth, framerate, nframes, comptype, compname)
    nchannels, sampwidth, framerate = params[0], params[1], params[2]
    n_frames = int(duration_sec * framerate)
    silence_data = b'\x00' * (n_frames * nchannels * sampwidth)

    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(nchannels)
        w.setsampwidth(sampwidth)
        w.setframerate(framerate)
        w.writeframes(silence_data)

def split_line_into_chunks(ja_line: str) -> list[str]:
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

def run_pipeline(ja_path: str, ro_path: str, rate: str, pbas: str, out_wav: str, out_ass: str):
    with open(ja_path, "r", encoding="utf-8") as f:
        ja_lines = [l.strip() for l in f if l.strip()]

    with open(ro_path, "r", encoding="utf-8") as f:
        ro_lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("[[rate") and not l.strip().startswith("[[pmod")]

    print(f"=== Synthesizing {len(ja_lines)} dialogue lines with line-by-line exact alignment ===")
    
    os.makedirs("parts", exist_ok=True)
    all_wav_parts = []
    events = []
    current_timeline = 0.35 # small breath before speech starts

    impact_keywords = [
        "アホかと", "馬鹿かと", "ボケが", "小一時間問い詰めたい", "問いたい",
        "すっこんでろ", "諸刃の剣", "素人にはおすすめしない", "ってこった", "その席空けろと",
        "ぶち切れですよ"
    ]
    sub_impact_keywords = [
        "よーしパパ", "とりあえず", "言いたいだけちゃうんかと", "殺伐としてるべきなんだよ", "Criticalだよ", "Criticalだろうが"
    ]

    last_params = None

    for i in range(len(ja_lines)):
        ja_line = ja_lines[i]
        ro_line = ro_lines[i] if i < len(ro_lines) else ja_line

        # Remove any internal slnc tags for clean per-line synthesis
        ro_clean = re.sub(r'\[\[slnc\s+\d+\]\]', '', ro_line).strip()
        ro_clean = sanitize_whisper_phonetics(ro_clean)

        part_script = f"parts/script_{i:03d}.txt"
        with open(part_script, "w", encoding="utf-8") as f:
            f.write(f"[[rate {rate}]][[pbas {pbas}]][[pmod 0]]{ro_clean}\n")

        part_aiff = f"parts/part_{i:03d}.aiff"
        part_wav = f"parts/part_{i:03d}.wav"

        # 1. Synthesize this exact line with macOS Whisper
        cmd_say = ["say", "-v", "Whisper", "-f", part_script, "-o", part_aiff]
        subprocess.run(cmd_say, check=True)

        # 2. Convert to 16-bit PCM WAV
        cmd_conv = ["afconvert", "-f", "WAVE", "-d", "LEI16", part_aiff, part_wav]
        subprocess.run(cmd_conv, check=True)

        # 3. Get exact actual audio duration
        dur, params = get_wav_duration_and_params(part_wav)
        last_params = params
        all_wav_parts.append(part_wav)

        line_start = current_timeline
        line_end = line_start + dur

        # 4. Allocate subtitles ONLY for iconic punchline/impact lines
        chunks = split_line_into_chunks(ja_line)
        chunk_weights = [max(len(c), 2) for c in chunks]
        total_w = sum(chunk_weights)

        c_start = line_start
        for c, w in zip(chunks, chunk_weights):
            c_dur = (w / total_w) * dur
            c_end = min(c_start + c_dur, line_end)

            is_impact = any(k in c for k in impact_keywords)
            
            # ONLY render subtitles for punchline / impact moments!
            if is_impact:
                disp_text = c
                if len(disp_text) > 13:
                    mid = len(disp_text) // 2
                    disp_text = disp_text[:mid] + "\\N" + disp_text[mid:]

                disp_text = f"{{\\b1}}{disp_text}{{\\b0}}"
                events.append(f"Dialogue: 0,{format_ass_time(c_start)},{format_ass_time(c_end)},Impact,,0,0,0,,{disp_text}")

            c_start = c_end

        current_timeline = line_end

        # 5. Insert exact pause (silence) after line
        is_line_impact = any(k in ja_line for k in impact_keywords)
        pause_sec = 0.65 if is_line_impact else 0.42
        pause_wav = f"parts/pause_{i:03d}.wav"
        create_silence_wav(pause_wav, pause_sec, params)
        all_wav_parts.append(pause_wav)
        current_timeline += pause_sec

    # 6. Concatenate all wav parts into single output.wav
    print(f"Concatenating {len(all_wav_parts)} audio fragments into {out_wav}...")
    with wave.open(out_wav, 'wb') as outfile:
        outfile.setparams(last_params)
        for part in all_wav_parts:
            with wave.open(part, 'rb') as infile:
                outfile.writeframes(infile.readframes(infile.getnframes()))

    total_final_dur, _ = get_wav_duration_and_params(out_wav)
    print(f"=== Successfully built {out_wav} (Exact duration: {total_final_dur:.2f}s) ===")

    # 7. Write ASS file
    ass_content = f"""[Script Info]
Title: Instant Gonorego Flash Subtitles (True Synchronized)
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

    print(f"=== Successfully wrote {len(events)} perfectly synchronized ASS events to {out_ass} ===")

if __name__ == "__main__":
    ja_path = sys.argv[1] if len(sys.argv) > 1 else "input_japanese.txt"
    ro_path = sys.argv[2] if len(sys.argv) > 2 else "raw_script.txt"
    rate = sys.argv[3] if len(sys.argv) > 3 else "128"
    pbas = sys.argv[4] if len(sys.argv) > 4 else "-15"
    out_wav = sys.argv[5] if len(sys.argv) > 5 else "output.wav"
    out_ass = sys.argv[6] if len(sys.argv) > 6 else "subtitles.ass"

    run_pipeline(ja_path, ro_path, rate, pbas, out_wav, out_ass)
