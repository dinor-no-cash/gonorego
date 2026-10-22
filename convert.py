import re
import pykakasi

# 手動で極限まで聞き取りやすく調声した脆弱性コピペ正本辞書
KNOWN_CORRECTIONS = {
    "普段は": "fudan wa",
    "脆弱性の": "zeijakusei no",
    "脆弱性で": "zeijakusei de",
    "脆弱性対応": "zeijakusei taiou",
    "脆弱性も": "zeijakusei mo",
    "脆弱性が": "zeijakusei ga",
    "大騒ぎしてるんです": "oosawagi shiterun desu",
    "書いてあるんです": "kaite arun desu",
    "アホかと": "aho ka to",
    "馬鹿かと": "baka ka to",
    "ボケが": "boke ga",
    "だろうが": "darou ga",
    "見てらんない": "miterannai",
    "殺伐としてるべきなんだよ": "satsubatsu to shiteru beki nan da yo",
    "いいんじゃねーか": "iin ja nee ka",
    "すっこんでろ": "sukkondero",
    "ぶち切れですよ": "buchigire desu yo",
    "流行んねーんだよ": "hayannain da yo",
    "問い詰めたい": "toitsumetai",
    "小一時間問い詰めたい": "shouichijikan toitsumetai",
    "言いたいだけちゃうんかと": "iitai dake chaun ka to",
    "棚卸し": "tanaoroshi",
    "これだね": "kore da ne",
    "これ最強": "kore saikyou",
    "諸刃の剣": "moroha no tsurugi",
    "眺めてなさいってこった": "nagametenasai tte kotta",
}

def clean_romaji(text):
    # IT専門用語の発音置換
    text = re.sub(r'php2shell', ' P H P two shell ', text, flags=re.IGNORECASE)
    text = re.sub(r'PHP', ' P H P ', text)
    text = re.sub(r'CVSS\s*10(\.0)?', ' C V S S ten point zero ', text, flags=re.IGNORECASE)
    text = re.sub(r'Critical', ' Critical ', text, flags=re.IGNORECASE)
    text = re.sub(r'Dependabot\s+Alerts', ' Dependabot Alerts ', text, flags=re.IGNORECASE)
    text = re.sub(r'Twitter', ' Twitter ', text, flags=re.IGNORECASE)
    text = re.sub(r'WAF', ' WAF ', text)

    # 熟語置換
    for k, v in KNOWN_CORRECTIONS.items():
        text = text.replace(k, f" {v} ")

    kks = pykakasi.kakasi()
    lines = text.splitlines()
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            output_lines.append("")
            continue

        result = kks.convert(line)
        romaji_tokens = []
        for item in result:
            orig = item['orig']
            # 助詞の誤読補正
            if orig == 'は':
                romaji_tokens.append('wa')
            elif orig == 'を':
                romaji_tokens.append('o')
            elif orig == 'へ':
                romaji_tokens.append('e')
            elif re.match(r'^[A-Za-z0-9\s\.,!\?\'"\-]+$', orig):
                romaji_tokens.append(orig.strip())
            else:
                romaji_tokens.append(item['hepburn'])

        conv_line = " ".join([t for t in romaji_tokens if t])
        # 句読点周り・連続スペースの整形
        conv_line = re.sub(r'\s+', ' ', conv_line)
        conv_line = re.sub(r'\s+([,\.\?!])', r'\1', conv_line)
        output_lines.append(conv_line.strip())

    final_text = "\n\n".join([l for l in output_lines if l])
    return final_text

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        text = f.read()

    final_text = clean_romaji(text)

    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    print("=== Successfully generated high-intelligibility romaji.txt ===")
    print(final_text[:350] + "...")

if __name__ == "__main__":
    main()
