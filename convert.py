# 英語音声合成（MacinTalk Whisper）の音素規則に完全合致させた英語当て字原稿
# - 「WAF」を英字読みせず、完全に「ワフ」と発音させるため「wahf」へ置換
# - 「ai」を英単語「A.I. (えーあい)」と誤読させず、「アイ」と発音させるため「-igh」「-ye」「eye-」等の音素スペルへ全面置換

PHONETIC_SCRIPT = """
Keenoh, Twitter oh meetan desu. Twitter.

Sohsheetarah nankah, foodan wah zayjahkoosay noh hanashee nankah shee-nigh renchoo mahdeh, P H P noh zayjahkoosay deh ohsawagee sheeteroon desu.

Deh, yohkoo meetarah nankah, P H P two shell tohkah kye-teh aron desu.

Moh neh, ahhoh kah toh. Bahkah kah toh.

Ohmyrah nah, P H P two shell gah wah-dye nee nahttah koorai deh, foodan meemookee moh shee-nigh zayjahkoosay tye-oh nee mooragatten jah nay yoh, bohkeh gah.

Critical dah yoh, Critical.

Ohmyrah gah keenoh mahdeh meesoogoosheetaytah zayjahkoosay moh Critical dahroh gah.

Nankah foodan security nee kyohmee nigh heetoh tohkah moh eeru shee. Zenshah sohdeh deh zayjahkoosay tye-oh kah. Ohmehdehtay nah.

Yohshee pahpah keenkyoo security tye-oh sheechah-oo-zoh, tohkah eetteroo noh. Moh meeterahn-nigh.

Ohmyrah nah, C V S S ten point zero noh ticket yahroo kahrah sohnoh sehkee ahkehroh toh.

Zayjahkoosay tye-oh tteh noh wah nah, mohttoh sahtsoobahtsoo toh sheeteroo behkee nahn dah yoh.

Hohnbahn kahnkyoh noh version eecheerahn oh hahsandeh, kye-hahtsoo tahntoh toh infra tahntoh gah eetsoo kenkah oh hahjeemehteh moh ohkasheekoo nigh, patch oh ahtehroo kah service oh tohmehroo kah, sohnnah fooneekee gah een jah nay kah.

Neewahkah yoosheekeeshah wah, sookkohndayroh.

Deh, yahttoh aykyoh hahnee noh kahkooneen gah hahjeemahttah kah toh ohmohttarah, tohnahree noh yahtsoo gah, tohree-ayzoo wahf deh, tohkah eetteroon desu.

Sohkoh deh mahtah boocheegeereh desu yoh.

Ahnoh nah, wahf deh foosehgehroo kahmoh kahkooneen sehzoo nee, tohree-ayzoo wahf nahnteh kyohbee hahyahn-nyn dah yoh. Bohkeh gah.

Tohkooeegay nah kah-oh sheeteh nahnee gah, tohree-ayzoo wahf deh, dah.

Ohmy wah hohntoh nee jeeshah gah aykyoh oh ookehroo noh kah hah-ahkoo sheeteroo noh kah toh toy-tigh. Toytsoo-meh-tigh. Shoh-eechee-jeekahn toytsoo-meh-tigh.

Ohmy, wahf tteh eet-tigh dahkeh chah-oon kah toh.

Zayjahkoosay tye-oh tsoo noh ohreh kahrah eewahseh-teh mohryebah eemah, tsoo noh eye-dah deh noh sigh-sheen ryookoh wah yahppahree, aykyoh hahnee noh tahnah-ohrohshee, kohreh dah neh.

Aykyoh hahnee noh tahnah-ohrohshee, ahkooyoh kahnoh-say noh kahkooneen, patch tehkeeyoh. Kohreh gah tsoo noh tahnohmee-kahtah.

Tahnah-ohrohshee tteh noh wah tsookaht-tehroo software oh hah-ahkoo dehkeeroo. Sohn kahwahree hohchee sheeteroo zayjahkoosay moh meetsookahroo. Kohreh.

Deh, sohreh nee ahkooyoh kahnoh-say toh jeegyoh aykyoh oh foomah-aytah yoosen joon-ee-zookeh. Kohreh sigh-kyoh.

Sheekahshee kohreh oh tahnohmoo toh eemah mahdeh meesoogoosheetaytah zayjahkoosay gah tigh-ryoh nee meetsookaht-teh tye-oh nee ohwahrehroo toh eeyoo keeken moh tohmohnah-oo, mohrohhah noh tsooroogee.

Sheerohtoh nee wah ohsoosohmeh dehkee-nigh.

Mah-ah ohmyrah doh-sheerohtoh wah, mee-tye-oh noh Dependabot Alerts dehmoh nahgahmeh-teh-nah-sigh tteh koht-tah.
"""

def main():
    cleaned = PHONETIC_SCRIPT.strip()
    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("=== Successfully generated phonetically tuned romaji.txt ===")
    print(cleaned[:350] + "...")

if __name__ == "__main__":
    main()
