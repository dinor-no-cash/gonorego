# 英語音声合成エンジンの短縮語判定・英単語衝突を完全排除した調声原稿
# - 「脆弱性」: 「zeijakusei」を解体し、確実に発音される英単語単位「zay jaku say」（ゼイ・ジャク・セイ）へ置換
# - 「まで」: 英語過去形「made（メード）」と誤読されないよう「ma deh」へ置換
# - 「が」: 米国ジョージア州略称「GA（ジー・エー）」と誤読されないよう「gah」へ置換
# - 助詞「で」「は」「と」「だ」: 英略語判定を避けるため「deh」「wah」「toh」「dah」へ完全防護

TUNED_SCRIPT = """
Kino, Twitter mitan desu. Twitter.

Soshitara nanka, fudan wah zay jaku say no hanashi nanka she nye renchu ma deh, P H P no zay jaku say deh osawagi shiterun desu.

Deh, yoku mitara nanka, php2shell toka kaite arun desu.

Mou neh, aho kah toh. Baka kah toh.

Omaera nah, php2shell gah wadai nee natta kurai deh, fudan mimuki moh she nye zay jaku say taio nee muragatten jah neh yoh, boke gah.

Critical dah yoh, Critical.

Omaera gah kino ma deh misugoshiteta zay jaku say moh Critical darou gah.

Nanka fudan security nee kyomi nai hito toka moh iru shi. Zensha soude deh zay jaku say taio kah. Omedete nah.

Yoshi papa kinkyu security taio shichau zoh, toka itteru no. Mou miterannai.

Omaera nah, C V S S ten point zero no ticket yaru kara sono seki akero toh.

Zay jaku say taio tteh no wah nah, motto satsubatsu toh shiteru beki nan dah yoh.

Honban kankyo no version ichiran oh hasande, kaihatsu tanto toh infra tanto gah itsu kenka oh hajimete moh okashiku nai, patch oh ateru kah service oh tomeru kah, sonna funiki gah een jah neh kah.

Niwaka yushikisha wah, sukkondero.

Deh, yatto eikyo hani no kakunin gah hajimatta kah toh omottara, tonari no yatsu gah, toriaezu waff deh, toka itterun desu.

Soko deh mata buchigire desu yoh.

Ano nah, waff deh fusegeru kamo kakunin sezu nee, toriaezu waff nante kyobi hayannain dah yoh. Boke gah.

Tokuige nah kao shite nani gah, toriaezu waff deh, dah.

Omae wah honto nee jisha gah eikyo oh ukeru no kah haaku shiteru no kah toh toitai. Toitsumetai. Shoichijikan toitsumetai.

Omae, waff tteh iitai dake chaun kah toh.

Zay jaku say taio tsu no ore kara iwasete moraeba ima, tsu no aida deh no saishin ryuko wah yappari, eikyo hani no tanaoroshi, kore dah neh.

Eikyo hani no tanaoroshi, akuyo kanosei no kakunin, patch tekiyo. Kore gah tsu no tanomikata.

Tanaoroshi tteh no wah tsukatteru software oh haaku dekiru. Son kawari hochi shiteru zay jaku say moh mitsukaru. Kore.

Deh, sore nee akuyo kanosei toh jigyo eikyo oh fumaeta yusen junizuke. Kore saikyo.

Shikashi kore oh tanomu toh ima ma deh misugoshiteta zay jaku say gah tairyo nee mitsukatte taio nee owareru toh iu kiken moh tomonau, moroha no tsurugi.

Shiroto nee wah osusume dekinai.

Mah omaera doshiroto wah, mitaio no Dependabot Alerts demo nagametenasai tteh kotta.
"""

def main():
    cleaned = TUNED_SCRIPT.strip()
    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("=== Successfully wrote bulletproof tuned romaji.txt ===")
    print(cleaned[:300] + "...")

if __name__ == "__main__":
    main()
