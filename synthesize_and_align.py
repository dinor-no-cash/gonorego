import sys
import os
import re
import wave
import subprocess


# ★一元フォニックス音節変換エンジン (Syllabic Phonics Transliteration Engine)★
# ★辞書完全撤廃：大文字を含む単語（Title Case外来語・英単語・略称）を100%自動保護★
def is_protected_english(token: str) -> bool:
    clean = re.sub(r'[^a-zA-Z\-]', '', token)
    if not clean:
        return True
    # 大文字が含まれている（例: Transformers, LLM, Local, Community, Wine, Model, Framework等）は100%英語として無条件保護
    return any(c.isupper() for c in clean)

ALREADY_PHONETIC_REGEX = re.compile(r'(?:[aeo]h|ee|oo|tsoo|ghee|gheh)\b', re.IGNORECASE)

SYLLABLE_MAP = [
    # 拗音・特殊音節 (3文字)
    ('kya', 'kyah'), ('kyu', 'kyoo'), ('kyo', 'kyoh'),
    ('sha', 'shah'), ('shu', 'shoo'), ('sho', 'shoh'),
    ('cha', 'chah'), ('chu', 'choo'), ('cho', 'choh'),
    ('nya', 'nyah'), ('nyu', 'nyoo'), ('nyo', 'nyoh'),
    ('hya', 'hyah'), ('hyu', 'hyoo'), ('hyo', 'hyoh'),
    ('mya', 'myah'), ('myu', 'myoo'), ('myo', 'myoh'),
    ('rya', 'ryah'), ('ryu', 'ryoo'), ('ryo', 'ryoh'),
    ('gya', 'gyah'), ('gyu', 'gyoo'), ('gyo', 'gyoh'),
    ('bya', 'byah'), ('byu', 'byoo'), ('byo', 'byoh'),
    ('pya', 'pyah'), ('pyu', 'pyoo'), ('pya', 'pyoh'),
    ('tsu', 'tsoo'), ('chi', 'chee'), ('shi', 'shee'),

    # 二重母音 (最重要：英語フォニックスでエイ/アウ/オイ等になるのを音節分解で物理阻止)
    ('dai', 'dah ee'), ('kai', 'kah ee'), ('sai', 'sah ee'), ('tai', 'tah ee'),
    ('nai', 'nah ee'), ('hai', 'hah ee'), ('mai', 'mah ee'), ('yai', 'yah ee'),
    ('rai', 'rah ee'), ('wai', 'wah ee'), ('gai', 'gah ee'), ('zai', 'zah ee'),
    ('bai', 'bah ee'), ('pai', 'pah ee'), ('ai', 'ah ee'),

    ('toi', 'toh ee'), ('koi', 'koh ee'), ('soi', 'soh ee'), ('noi', 'noh ee'),
    ('hoi', 'hoh ee'), ('moi', 'moh ee'), ('yoi', 'yoh ee'), ('roi', 'roh ee'),
    ('goi', 'goh ee'), ('zoi', 'zoh ee'), ('boi', 'boh ee'), ('poi', 'poh ee'),
    ('oi', 'oh ee'),

    ('tui', 'too ee'), ('kui', 'koo ee'), ('sui', 'soo ee'), ('tsui', 'tsoo ee'),
    ('nui', 'noo ee'), ('rui', 'roo ee'), ('gui', 'goo ee'), ('ui', 'oo ee'),

    ('tei', 'teh ee'), ('kei', 'keh ee'), ('sei', 'seh ee'), ('nei', 'neh ee'),
    ('hei', 'heh ee'), ('mei', 'meh ee'), ('rei', 'reh ee'), ('gei', 'gheh ee'),
    ('zei', 'zeh ee'), ('bei', 'beh ee'), ('pei', 'peh ee'), ('ei', 'eh ee'),

    # 長音 ou / uu
    ('ryuu', 'ryoo'), ('chuu', 'choo'), ('shuu', 'shoo'), ('kyuu', 'kyoo'),
    ('kou', 'koh'), ('sou', 'soh'), ('tou', 'toh'), ('nou', 'noh'),
    ('hou', 'hoh'), ('mou', 'moh'), ('you', 'yoh'), ('rou', 'roh'),
    ('gou', 'goh'), ('zou', 'zoh'), ('dou', 'doh'), ('bou', 'boh'),
    ('shou', 'shoh'), ('chou', 'choh'), ('ryou', 'ryoh'), ('kyou', 'kyoh'),

    # 2文字（子音 + 母音）
    ('ka', 'kah'), ('ki', 'kee'), ('ku', 'koo'), ('ke', 'keh'), ('ko', 'koh'),
    ('sa', 'sah'), ('si', 'shee'), ('su', 'soo'), ('se', 'seh'), ('so', 'soh'),
    ('ta', 'tah'), ('ti', 'chee'), ('tu', 'tsoo'), ('te', 'teh'), ('to', 'toh'),
    ('na', 'nah'), ('ni', 'nee'), ('nu', 'noo'), ('ne', 'neh'), ('no', 'noh'),
    ('ha', 'hah'), ('hi', 'hee'), ('hu', 'foo'),  ('he', 'heh'), ('ho', 'hoh'),
    ('ma', 'mah'), ('mi', 'mee'), ('mu', 'moo'), ('me', 'meh'), ('mo', 'moh'),
    ('ya', 'yah'), ('yu', 'yoo'), ('yo', 'yoh'),
    ('ra', 'rah'), ('ri', 'ree'), ('ru', 'roo'), ('re', 'reh'), ('ro', 'roh'),
    ('wa', 'wah'), ('wo', 'woh'),
    # 濁音・半濁音（ghee, gheh で軟音化ジェ/ジを物理阻止）
    ('ga', 'gah'), ('gi', 'ghee'), ('gu', 'goo'), ('ge', 'gheh'), ('go', 'goh'),
    ('za', 'zah'), ('ji', 'jee'),  ('zu', 'zoo'), ('ze', 'zeh'),  ('zo', 'zoh'),
    ('da', 'dah'), ('di', 'jee'),  ('du', 'zoo'), ('de', 'deh'),  ('do', 'doh'),
    ('ba', 'bah'), ('bi', 'bee'),  ('bu', 'boo'), ('be', 'beh'),  ('bo', 'boh'),
    ('pa', 'pah'), ('pi', 'pee'),  ('pu', 'poo'), ('pe', 'peh'),  ('po', 'poh'),
    ('fu', 'foo'),

    # 単独母音（1文字）
    ('a', 'ah'), ('i', 'ee'), ('u', 'oo'), ('e', 'eh'), ('o', 'oh')
]

def transliterate_syllables(romaji_word: str) -> str:
    w = romaji_word.lower()

    # 語頭の促音（例: tte -> teh, tto -> toh）
    if re.match(r'^([bcdfghjklmpqrstvwxyz])\1', w):
        w = w[1:]

    tokens = []
    i = 0
    n = len(w)

    while i < n:
        # 1. 促音検出（子音重複：kk, tt, ss, pp 等 ※nnは撥音）
        # ★重要：英語に実在しない「ht」などの異常子音結合を防ぐため、直前音節末尾の長母音hを除去して純粋な短母音閉音節（CVC: kot, sook, eet）にする★
        if i + 1 < n and w[i] == w[i+1] and w[i] in 'bcdfghjklmpqrstvwxyz' and w[i] != 'n':
            coda_char = w[i]
            if tokens:
                prev = tokens[-1]
                if prev.endswith('h'):
                    prev = prev[:-1]
                tokens[-1] = prev + coda_char
            i += 1
            continue

        # 2. 撥音検出（ん: n）
        # 直前音節の末尾'h'を除去して鼻音nを結合（例: non, kan, hon）
        if w[i] == 'n':
            if i + 1 == n or (w[i+1] not in 'aiueoy' and not (i + 2 <= n and w[i+1:i+3] in ['ya','yu','yo'])):
                if tokens:
                    prev = tokens[-1]
                    if prev.endswith('h'):
                        prev = prev[:-1]
                    tokens[-1] = prev + 'n'
                else:
                    tokens.append('un') # 英語に実在しない語頭nnではなく実在の感嘆詞un
                i += 1
                continue

        matched = False
        for syl, rep in SYLLABLE_MAP:
            if w.startswith(syl, i):
                tokens.append(rep)
                i += len(syl)
                matched = True
                break
        if not matched:
            tokens.append(w[i])
            i += 1
    return ' '.join(tokens)

def apply_phonetic_transliteration(text: str) -> str:
    tokens = re.split(r'([a-zA-Z0-9_\-]+|[^\s\w]+|\s+)', text)
    out = []
    for t in tokens:
        if not t:
            continue
        if re.match(r'^[a-zA-Z0-9_\-]+$', t):
            if is_protected_english(t) or ALREADY_PHONETIC_REGEX.search(t):
                out.append(t)
            else:
                out.append(transliterate_syllables(t))
        else:
            out.append(t)
    return re.sub(r'[ \t]+', ' ', ''.join(out))

def sanitize_whisper_phonetics(text: str) -> str:
    """Eliminate English phonics mispronunciations for macOS Whisper voice, destroying silent-E and ambiguous vowels."""
    if not text:
        return ""
    r = text.strip()

    word_map = [
        # 冒頭の日本語残り防止
        (r'そんな事より聞いてくれよ(?:１|1|一)?よ?', "sonna koto yori kiite kure yo ichi yo"),
        (r'昨日', "kino"),
        (r'サイゼリヤ', "Saizeriya"),
        (r'サイゼ', "Saize"),

        # 「みて」が英語の「mite（マイト）」になるのを完全防止
        (r'\bmite\b', "mee teh"),
        (r'\bmita\b', "mee tah"),
        (r'\bmiteran\b', "mee teh rahn"),
        # 「きて」が英語の「kite（カイト）」になるのを完全防止
        (r'\bkite\b', "kee teh"),
        (r'\bkita\b', "kee tah"),
        # 「して」が英語の「site/shite」になるのを完全防止
        (r'\bshite\b', "shee teh"),
        (r'\bshita\b', "shee tah"),
        # 「あけて」が英語の「ake（エイク）」になるのを完全防止
        (r'\bakete\b', "ah keh teh"),
        (r'\bakero\b', "ah keh roh"),
        # 「まけて」が英語の「make（メイク）」になるのを完全防止
        (r'\bmake\b', "mah keh"),
        (r'\bmakete\b', "mah keh teh"),
        # 「まで」が英語の「made（メイド）」になるのを完全防止
        (r'\bmade\b', "mah deh"),
        # 「さけ」が英語の「sake（セイク）」になるのを完全防止
        (r'\bsake\b', "sah keh"),
        # 「ため」が英語の「tame（テイム）」になるのを完全防止
        (r'\btame\b', "tah meh"),
        # 「だれ」が英語の「dare（デア）」になるのを完全防止
        (r'\bdare\b', "dah reh"),
        # 「これ」「それ」「あれ」「おれ」
        (r'\bkore\b', "koh reh"),
        (r'\bsore\b', "soh reh"),
        (r'\bare\b', "ah reh"),
        (r'\bore\b', "oh reh"),
        # 「お前」「お前ら」
        (r'\bomae\b', "oh mah eh"),
        (r'\bomaera\b', "oh mah eh rah"),
        (r'\bomae-ra\b', "oh mah eh rah"),
        # 「なさい」「ながめて」
        (r'\bnasai\b', "nah sah ee"),
        (r'\bnagamete\b', "nah gah meh teh"),

        # 誤爆したToransufaamazuの救済
        (r'\b(?:toransufaamazu|toransufaamaa)\b', "Transformers"),
        (r'トランスフォーマーズ?', "Transformers"),

        # 頻出キーワードの固定ガード
        (r'\b(?:toikurumetai|toitsumetai|toishimetai)\b', "toi tsume tai"),
        (r'\b(?:sho\s*ichi\s*jikan|shoichijikan|shouichijikan)\b', "ko ichi jikan"),
        (r'\b(?:moro\s*no\s*yaiba|moronoyaiba)\b', "moroha no tsurugi"),
        (r'\b(?:buchikire|buchi\s*kire)\b', "buchi kee reh"),
        (r'\b(?:sujin)\b', "shee roh oo toh"),
        (r'\b(?:do\s*sujin|dosujin)\b', "do shee roh oo toh"),
        (r'\b(?:shirouto)\b', "shee roh oo toh"),
        # 流行んねーの誤読（りゅうこうんねー）救済
        (r'\b(?:ryuukou\s*n\s*nee|ryuukou\s*nee|ryuukounnee)\b', "hayannee"),
        (r'\b(?:ryuukou\s*n\s*nai|ryuukounai)\b', "hayaranai"),
        (r'\b(?:tte\s+)?kotta\b', "tte kotta"),
        (r'\bichi\s*yo\b', "ichi yo"),

        # ★最重要：「ai」を英語の「エイ」と誤読させない音節分解★
        # 「開発（kaihatsu）」がrain/waitと同じaiで「ケイハツ」になるのを完全根絶
        (r'\b(?:kaihatsu|keihatsu)\b', "kah ee hah tsoo"),
        (r'開発', "kah ee hah tsoo"),

        # 「アイ」母音のエイ誤読防止
        (r'\biitai\b', "ee tah ee"),
        (r'\bmitai\b', "mee tah ee"),
        (r'\btoitai\b', "toh ee tah ee"),
        (r'\btsumetai\b', "tsoo meh tah ee"),

        # ★最重要：助詞の英語略称・フォニックス誤読の機械的撲滅★
        # 「が」がジョージア州GA「ジー・エー」になるのを完全排除
        (r'\bga\b', "gah"),
        # 「は」
        (r'\bha\b', "wah"),
        (r'\bwa\b', "wah"),
        # 「で」がデラウェア州DE「ディー・イー」になるのを完全排除
        (r'\bde\b', "deh"),
        # 「だ」
        (r'\bda\b', "dah"),
        # 「と」が前置詞to「トゥー」になるのを防止
        (r'\bto\b', "toh"),
        # 「の」がno「ノー」になるのを防止
        (r'\bno\b', "noh"),
        # 「も」がミズーリ州MO「エム・オー」になるのを防止
        (r'\bmo\b', "moh"),
        # 「へ」が英語he「ヒー」になるのを防止
        (r'\bhe\b', "eh"),
    ]

    for pat, rep in word_map:
        r = re.sub(pat, rep, r, flags=re.IGNORECASE)

    # ★一元フォニックス音節変換：残ったすべての未変換ローマ字単語を一網打尽に変換★
    r = apply_phonetic_transliteration(r)

    # ★英語実在音節（Phonotactics）準拠：架空子音クラスタ（ht, 語頭nn等）の完全根絶★
    # 1. 促音（っ）の英語実在音節化（kot ta, it ta, suk kon de ro, te kot ta）
    r = re.sub(r'\bkoht\b', 'kot', r, flags=re.IGNORECASE)
    r = re.sub(r'\bsooh?\b', 'soo', r, flags=re.IGNORECASE)
    r = re.sub(r'\b(?:sook|soo)\s*(?:kohn|kon)\b', 'suk kon', r, flags=re.IGNORECASE)
    r = re.sub(r'\b(?:teh\s+)?(?:koht|kot)\s+tah?\b', 'te kot ta', r, flags=re.IGNORECASE)
    r = re.sub(r'\b(?:eet|it)\s+tah?\b', 'it ta', r, flags=re.IGNORECASE)
    r = re.sub(r'\b(?:eet|it)\s+teh?\b', 'it te', r, flags=re.IGNORECASE)
    # 2. 撥音（ん）の英語実在音節化（un de su, non de, kan kyo）
    r = re.sub(r'\bnn\b', 'un', r, flags=re.IGNORECASE)
    r = re.sub(r'\bn\s+desu\b', 'un de su', r, flags=re.IGNORECASE)
    r = re.sub(r'\bn\s+da\b', 'un da', r, flags=re.IGNORECASE)
    r = re.sub(r'\bn\s+ka\b', 'un ka', r, flags=re.IGNORECASE)
    r = re.sub(r'\bn\b', 'un', r, flags=re.IGNORECASE)
    r = re.sub(r'\btte\b', 'te', r, flags=re.IGNORECASE)
    # 3. 孤立子音・孤立hの完全除去
    r = re.sub(r'\s+h\b', '', r, flags=re.IGNORECASE)
    r = re.sub(r'\b([a-z]+)\s+([tkps])\s+([a-z]+)', r'\1\2 \3', r, flags=re.IGNORECASE)

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
