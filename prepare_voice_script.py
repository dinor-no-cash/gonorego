import re
import sys

def inject_pauses(text: str) -> str:
    # If the user already manually provided [[slnc tags, respect them
    if "[[slnc" in text:
        return text

    # Standardize newlines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    processed_lines = []

    for line in lines:
        # Check for iconic punchlines/climax phrases to add dramatic pauses
        # 1. "ah hoh kah toh. Bah kah kah toh."
        line = re.sub(r'(?i)\b(ah\s+hoh\s+kah\s+toh)\b\.?', r'[[slnc 250]] \1. [[slnc 350]]', line)
        line = re.sub(r'(?i)\b(Bah\s+kah\s+kah\s+toh)\b\.?', r'\1. [[slnc 650]]', line)

        # 2. "boh keh gah"
        line = re.sub(r'(?i)\b(boh\s+keh\s+gah)\b\.?', r'[[slnc 250]] \1. [[slnc 550]]', line)

        # 3. "Koh ee chee jee kahn toh ee tsoo meh tie"
        line = re.sub(r'(?i)\b(Koh\s+ee\s+chee\s+jee\s+kahn)\b', r'[[slnc 300]] \1', line)
        line = re.sub(r'(?i)\b(toh\s+ee\s+tsoo\s+meh\s+tie)\b\.?', r'\1. [[slnc 600]]', line)

        # 4. "sook kohn deh roh"
        line = re.sub(r'(?i)\b(sook\s+kohn\s+deh\s+roh)\b\.?', r'[[slnc 250]] \1. [[slnc 600]]', line)

        # 5. "moh roh hah noh tsoo roo ghee"
        line = re.sub(r'(?i)\b(moh\s+roh\s+hah\s+noh\s+tsoo\s+roo\s+ghee)\b\.?', r'[[slnc 300]] \1. [[slnc 600]]', line)

        # 6. "Shee roh toh nee wah oh soo soo meh deh kee nye"
        line = re.sub(r'(?i)\b(Shee\s+roh\s+toh\s+nee\s+wah\s+oh\s+soo\s+soo\s+meh\s+deh\s+kee\s+nye)\b\.?', r'[[slnc 400]] \1. [[slnc 700]]', line)

        # 7. Commas -> slight pause 220ms
        line = re.sub(r',(?!\s*\[\[slnc)(\s*)', r', [[slnc 220]] \1', line)

        # 8. Periods -> end of sentence pause 450ms
        line = re.sub(r'\.(?!\s*\[\[slnc)(\s*)', r'. [[slnc 450]] \1', line)

        # 9. Clean up whitespace
        line = re.sub(r'\s{2,}', ' ', line).strip()

        processed_lines.append(line)

    # Join lines with paragraph pause
    return " [[slnc 650]]\n\n".join(processed_lines)

if __name__ == "__main__":
    in_path = sys.argv[1] if len(sys.argv) > 1 else "input_script_raw.txt"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "input_script.txt"

    with open(in_path, "r", encoding="utf-8") as f:
        content = f.read()

    tuned = inject_pauses(content)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tuned)

    print(f"=== Successfully prepared tuned voice script with pauses -> {out_path} ===")
