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

def generate_ass(japanese_text: str, total_duration: float, output_ass_path: str):
    # Split text into meaningful dialog chunks
    raw_lines = [l.strip() for l in japanese_text.split("\n") if l.strip()]
    
    # Further split long lines by full stop or exclamation if needed
    chunks = []
    for line in raw_lines:
        # Match sentences
        parts = re.split(r'(?<=。)|\s{2,}', line)
        for p in parts:
            p = p.strip()
            if p:
                chunks.append(p)

    if not chunks:
        chunks = ["そんなことより聞いてくれよ１よ。"]

    # Calculate weight for each chunk based on character length and punchline importance
    weights = []
    styles = []

    # Iconic flash punchline markers
    impact_keywords = [
        "アホかと", "馬鹿かと", "ボケが", "小一時間問い詰めたい", "問いたい",
        "すっこんでろ", "諸刃の剣", "素人にはおすすめしない", "ってこった", "その席空けろと"
    ]
    sub_impact_keywords = [
        "よーしパパ", "とりあえず", "言いたいだけちゃうんかと", "ぶち切れですよ", "殺伐としてるべきなんだよ"
    ]

    for c in chunks:
        # Base weight: length of text (min 4 chars)
        w = max(len(c), 4)

        # Style determination
        is_impact = any(k in c for k in impact_keywords)
        is_sub_impact = any(k in c for k in sub_impact_keywords)

        if is_impact:
            styles.append("Impact")
            w *= 1.4  # Dramatic pause & emphasis
        elif is_sub_impact:
            styles.append("SubImpact")
            w *= 1.2
        else:
            styles.append("Default")

        weights.append(w)

    total_weight = sum(weights)
    
    # Allocate timeline proportionally with small gaps
    start_sec = 0.5 # start after a slight breath
    usable_duration = max(total_duration - 1.0, total_duration * 0.95)

    events = []
    for i, (chunk, weight, style) in enumerate(zip(chunks, weights, styles)):
        duration = (weight / total_weight) * usable_duration
        # minimum duration 1.2s, max 6.0s
        duration = max(1.2, duration)
        end_sec = min(start_sec + duration, total_duration)

        # Format text for ASS
        # For Impact lines like "アホかと。馬鹿かと。", make them punchy
        display_text = chunk
        if style == "Impact":
            # Add subtle flash scale/punch
            display_text = f"{{\\b1}}{display_text}{{\\b0}}"

        start_str = format_ass_time(start_sec)
        end_str = format_ass_time(end_sec)

        events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{display_text}")
        start_sec = end_sec + 0.08  # slight 80ms gap

    # ASS Header with early 2000s Flash typography styles
    ass_content = f"""[Script Info]
Title: Instant Gonorego Flash Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
; Normal Dialog (Flash yellow with thick black outline at bottom)
Style: Default,Hiragino Sans,44,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.0,2.5,2,40,40,45,1
; Impact / Punchline Dialog (Iconic giant red text with white outline & heavy shadow dead center)
Style: Impact,Hiragino Sans,74,&H000000FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,105,105,1,0,1,6.0,4.0,5,30,30,30,1
; Sub-Impact Dialog (Amber orange emphasis at bottom-center)
Style: SubImpact,Hiragino Sans,52,&H0000AAFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4.5,3.0,2,30,30,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    print(f"=== Generated {len(events)} subtitle events to {output_ass_path} (Total duration: {total_duration:.2f}s) ===")

if __name__ == "__main__":
    jp_path = sys.argv[1] if len(sys.argv) > 1 else "input_japanese.txt"
    wav_path = sys.argv[2] if len(sys.argv) > 2 else "output.wav"
    out_ass = sys.argv[3] if len(sys.argv) > 3 else "subtitles.ass"

    with open(jp_path, "r", encoding="utf-8") as f:
        japanese_text = f.read()

    duration = get_audio_duration(wav_path)
    generate_ass(japanese_text, duration, out_ass)
