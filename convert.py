import re
import pykakasi

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    kks = pykakasi.kakasi()
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            output_lines.append("")
            continue

        # Pre-substitutions for known IT / security terms to ensure correct English pronunciation
        line = re.sub(r'php2shell', ' P H P two shell ', line, flags=re.IGNORECASE)
        line = re.sub(r'PHP', ' P H P ', line)
        line = re.sub(r'CVSS\s*10(\.0)?', ' C V S S ten point zero ', line, flags=re.IGNORECASE)
        line = re.sub(r'Critical', ' Critical ', line, flags=re.IGNORECASE)
        line = re.sub(r'Dependabot\s+Alerts', ' Dependabot Alerts ', line, flags=re.IGNORECASE)
        line = re.sub(r'Twitter', ' Twitter ', line, flags=re.IGNORECASE)
        line = re.sub(r'WAF', ' WAF ', line)
        line = re.sub(r'10\.0', ' ten point zero ', line)

        result = kks.convert(line)
        romaji_tokens = []
        for item in result:
            orig = item['orig']
            # If token is English / numbers / punctuation, keep as is
            if re.match(r'^[A-Za-z0-9\s\.,!\?\'"\-]+$', orig):
                romaji_tokens.append(orig.strip())
            else:
                romaji_tokens.append(item['hepburn'])

        conv_line = " ".join([t for t in romaji_tokens if t])
        conv_line = re.sub(r'\s+', ' ', conv_line)
        conv_line = re.sub(r'\s+([,\.\?!])', r'\1', conv_line)
        output_lines.append(conv_line.strip())

    final_text = "\n\n".join([l for l in output_lines if l])

    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    print("=== Successfully generated romaji.txt ===")
    print(final_text[:300] + "...")

if __name__ == "__main__":
    main()
