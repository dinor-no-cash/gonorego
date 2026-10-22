import re

# 極限まで聞き取りやすく調声した脆弱性コピペ正本テキスト（明瞭な分かち書き＆ポーズ調整済み）
TUNED_TEXT = """
kinoo, Twitter o mitan desu. Twitter.

soshitara nanka, fudan wa zeijakusei no hanashi nanka shinai renchuu made, P H P no zeijakusei de oosawagi shiterun desu.

de, yoku mitara nanka, P H P two shell toka kaite arun desu.

mou ne, aho ka to. baka ka to.

omaera na, P H P two shell ga wadai ni natta kurai de, fudan mimuki mo shinai zeijakusei taiou ni muragatten ja nee yo, boke ga.

Critical da yo, Critical.

omaera ga kinou made misugoshiteta zeijakusei mo Critical darou ga.

nanka fudan security ni kyoumi nai hito toka mo iru shi. zensha soude de zeijakusei taiou ka. omedetee na.

yooshi papa kinkyuu security taiou shichauzoo, toka itteru no. mou miterannai.

omaera na, C V S S ten point zero no ticket yaru kara sono seki akero to.

zeijakusei taiou tte no wa na, motto satsubatsu to shiteru beki nan da yo.

honban kankyou no version ichiran o hasande, kaihatsu tantou to infra tantou ga itsu kenka o hajimete mo okashiku nai, patch o ateru ka service o tomeru ka, sonna fun'iki ga iin ja nee ka.

niwaka yuushikisha wa, sukkondero.

de, yatto eikyou han'i no kakunin ga hajimatta ka to omottara, tonari no yatsu ga, toriaezu WAF de, toka itterun desu.

soko de mata buchigire desu yo.

ano na, WAF de fusegeru kamo kakunin sezu ni, toriaezu WAF nante kyoubi hayannain da yo. boke ga.

tokuige na kao shite nani ga, toriaezu WAF de, da.

omae wa hontou ni jisha ga eikyou o ukeru no ka haaku shiteru no ka to toitai. toitsumetai. shouichijikan toitsumetai.

omae, WAF tte iitai dake chaun ka to.

zeijakusei taiou tsuu no ore kara iwasete moraeba ima, tsuu no aida de no saishin ryuukou wa yappari, eikyou han'i no tanaoroshi, kore da ne.

eikyou han'i no tanaoroshi, akuyou kanousei no kakunin, patch tekiyou. kore ga tsuu no tanomikata.

tanaoroshi tte no wa tsukatteru software o haaku dekiru. son kawari houchi shiteru zeijakusei mo mitsukaru. kore.

de, sore ni akuyou kanousei to jigyou eikyou o fumaeta yuusen jun'izuke. kore saikyou.

shikashi kore o tanomu to ima made misugoshiteta zeijakusei ga tairyou ni mitsukatte taiou ni owareru to iu kiken mo tomonau, moroha no tsurugi.

shirouto ni wa osusume dekinai.

maa omaera doshirouto wa, mitaiou no Dependabot Alerts demo nagametenasai tte kotta.
"""

def main():
    cleaned = TUNED_TEXT.strip()
    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("=== Successfully wrote hand-tuned clear romaji.txt ===")
    print(cleaned[:300] + "...")

if __name__ == "__main__":
    main()
