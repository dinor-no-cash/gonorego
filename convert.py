# 英語音声合成（MacinTalk Whisper）の音素規則に完全合致させた英語当て字原稿
# 「shi」が二重母音「シャイ/サイ」にならず確実に「シ」と発音されるよう「shee」等の音素スペルを採用
PHONETIC_SCRIPT = """
Keenoh, Twitter oh meetan desu. Twitter.

Sohsheetarah nankah, foodan wah zayjahkoosay noh hanashee nankah sheenai renchoo mahdeh, P H P noh zayjahkoosay deh ohsawagee sheeteroon desu.

Deh, yohkoo meetarah nankah, P H P two shell tohkah kayteh aron desu.

Moh neh, ahhoh kah toh. Bahkah kah toh.

Ohmyrah nah, P H P two shell gah wahdai nee nahttah koorai deh, foodan meemookee moh sheenai zayjahkoosay tai-oh nee mooragatten jah nay yoh, bohkeh gah.

Critical dah yoh, Critical.

Ohmyrah gah keenoh mahdeh meesoogoosheetaytah zayjahkoosay moh Critical dahroh gah.

Nankah foodan security nee kyohmee nai heetoh tohkah moh eeru shee. Zenshah sohdeh deh zayjahkoosay tai-oh kah. Ohmehdehtay nah.

Yohshee pahpah keenkyoo security tai-oh sheechah-oo-zoh, tohkah eetteroo noh. Moh meeterannai.

Ohmyrah nah, C V S S ten point zero noh ticket yahroo kahrah sohnoh sehkee ahkehroh toh.

Zayjahkoosay tai-oh tteh noh wah nah, mohttoh sahtsoobahtsoo toh sheeteroo behkee nahn dah yoh.

Hohnbahn kahnkyoh noh version eecheerahn oh hahsandeh, kaihahtsoo tahntoh toh infra tahntoh gah eetsoo kenkah oh hahjeemehteh moh ohkasheekoo nai, patch oh ahtehroo kah service oh tohmehroo kah, sohnnah fooneekee gah een jah nay kah.

Neewahkah yoosheekeeshah wah, sookkohndayroh.

Deh, yahttoh aykyoh hahnee noh kahkooneen gah hahjeemahttah kah toh ohmohttarah, tohnahree noh yahtsoo gah, tohree-ayzoo WAF deh, tohkah eetteroon desu.

Sohkoh deh mahtah boocheegeereh desu yoh.

Ahnoh nah, WAF deh foosehgehroo kahmoh kahkooneen sehzoo nee, tohree-ayzoo WAF nahnteh kyohbee hahyahn-nyn dah yoh. Bohkeh gah.

Tohkooeegay nah kah-oh sheeteh nahnee gah, tohree-ayzoo WAF deh, dah.

Ohmy wah hohntoh nee jeeshah gah aykyoh oh ookehroo noh kah hah-ahkoo sheeteroo noh kah toh toy-tai. Toytsoomehtai. Shoh-eechee-jeekahn toytsoomehtai.

Ohmy, WAF tteh eettai dahkeh chah-oon kah toh.

Zayjahkoosay tai-oh tsoo noh ohreh kahrah eewahseh-teh mohryebah eemah, tsoo noh aida deh noh saisheen ryookoh wah yahppahree, aykyoh hahnee noh tahnah-ohrohshee, kohreh dah neh.

Aykyoh hahnee noh tahnah-ohrohshee, ahkooyoh kahnoh-say noh kahkooneen, patch tehkeeyoh. Kohreh gah tsoo noh tahnohmee-kahtah.

Tahnah-ohrohshee tteh noh wah tsookaht-tehroo software oh hah-ahkoo dehkeeroo. Sohn kahwahree hohchee sheeteroo zayjahkoosay moh meetsookahroo. Kohreh.

Deh, sohreh nee ahkooyoh kahnoh-say toh jeegyoh aykyoh oh foomah-aytah yoosen joon-ee-zookeh. Kohreh sai-kyoh.

Sheekahshee kohreh oh tahnohmoo toh eemah mahdeh meesoogoosheetaytah zayjahkoosay gah tairyoh nee meetsookaht-teh tai-oh nee ohwahrehroo toh eeyoo keeken moh tohmohnah-oo, mohrohhah noh tsooroogee.

Sheerohtoh nee wah ohsoosohmeh dehkeenai.

Mah-ah ohmyrah doh-sheerohtoh wah, meetai-oh noh Dependabot Alerts dehmoh nahgahmeh-tehnahsai tteh koht-tah.
"""

def main():
    cleaned = PHONETIC_SCRIPT.strip()
    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("=== Successfully generated phonetically tuned romaji.txt ===")
    print(cleaned[:350] + "...")

if __name__ == "__main__":
    main()
