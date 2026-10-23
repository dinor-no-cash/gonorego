# 英語音声合成エンジンの短縮語判定・英単語衝突を完全排除した調声原稿
# - 「脆弱性」: 「zay jaku say」（ゼイ・ジャク・セイ）
# - 「まで」: 英語過去形「made」誤読防止 -> 「ma deh」
# - 「が」: 米国ジョージア州略称「GA」誤読防止 -> 「gah」
# - 「それ」「俺」「これ」: 英語「sore (痛い)」「ore (鉱石)」「core」誤読防止 -> 「soh reh」「oh reh」「koh reh」
# - 「範囲」: 英語「honey」誤読防止 -> 「hah nee」
# - 「人」: 英語「hi」誤読防止 -> 「hee toh」
# - 「その」「そこ」: 英語「so」「no」誤読防止 -> 「soh noh」「Soh koh」
# - 「そん」: 英語「son (息子)」誤読防止 -> 「Sohn」
# - 「でも」: 英語「demo」誤読防止 -> 「deh moh」
# - 「とか」: 英語「to」誤読防止 -> 「toh kah」
# - 「ボケ」: 英語「boke」誤読防止 -> 「boh keh」
# - 「〜るん」: 英語「run (走る)」誤読防止 -> 「roon」

TUNED_SCRIPT = """
Kee noh, Twitter mee tahn desu. Twitter.

Soshitara nahn kah, foo dahn wah zay jaku say noh hah nah she nahn kah she nye renchoo ma deh, P H P noh zay jaku say deh oh sah wah ghee she teh roon desu.

Deh, yoh koo mee tah rah nahn kah, php2shell toh kah kye teh ah roon desu.

Moh neh, ah hoh kah toh. Bah kah kah toh.

Oh mah eh rah nah, php2shell gah wah dye nee naht tah koo rye deh, foo dahn mee moo kee moh she nye zay jaku say tie oh nee moo rah gaht ten jah neh yoh, boh keh gah.

Critical dah yoh, Critical.

Oh mah eh rah gah kee noh ma deh mee soo goh she teh tah zay jaku say moh Critical dah roh gah.

Nahn kah foo dahn security nee kyoh mee nye hee toh toh kah moh ee roo she. Zen shah soh deh deh zay jaku say tie oh kah. Oh meh deh teh nah.

Yoh she papa keen kyoo security tie oh she chow zoh, toh kah eet teh roo noh. Moh mee teh rahn nye.

Oh mah eh rah nah, C V S S ten point zero noh ticket yah roo kah rah soh noh seh kee ah keh roh toh.

Zay jaku say tie oh tteh noh wah nah, mot toh sah tsoo bah tsoo toh she teh roo beh kee nahn dah yoh.

Hohn bahn kahn kyoh noh version ee chee rahn oh hah sahn deh, kye hah tsoo tahn toh toh infra tahn toh gah ee tsoo ken kah oh hah jee meh teh moh oh kah she koo nye, patch oh ah teh roo kah service oh toh meh roo kah, sohn nah foon ee kee gah een jah neh kah.

Nee wah kah yoo she kee shah wah, sook kohn deh roh.

Deh, yaht toh ay kyoh hah nee noh kah koo neen gah hah jee maht tah kah toh oh moht tah rah, toh nah ree noh yah tsoo gah, toh ree ah eh zoo waff deh, toh kah eet teh roon desu.

Soh koh deh mah tah boo chee ghee reh desu yoh.

Ah noh nah, waff deh foo seh geh roo kah moh kah koo neen seh zoo nee, toh ree ah eh zoo waff nahn teh kyoh bee hah yahn nye nahn dah yoh. Boh keh gah.

Toh koo ee geh nah kah oh she teh nah nee gah, toh ree ah eh zoo waff deh, dah.

Oh mah eh wah hohn toh nee jee shah gah ay kyoh oh oo keh roo noh kah hah ah koo she teh roo noh kah toh toy tie. Toy tsoo meh tie. Shoh ee chee jee kahn toy tsoo meh tie.

Oh mah eh, waff tteh ee ee tie dah keh chown kah toh.

Zay jaku say tie oh tsoo noh oh reh kah rah ee wah seh teh moh rah eh bah ee mah, tsoo noh ah ee dah deh noh sigh sheen ryoo koh wah yahp pah ree, ay kyoh hah nee noh tah nah oh roh she, koh reh dah neh.

Ay kyoh hah nee noh tah nah oh roh she, ah koo yoh kah noh say noh kah koo neen, patch teh kee yoh. Koh reh gah tsoo noh tah noh mee kah tah.

Tah nah oh roh she tteh noh wah tsukatteru software oh hah ah koo deh kee roo. Sohn kah wah ree hoh chee she teh roo zay jaku say moh mee tsoo kah roo. Koh reh.

Deh, soh reh nee ah koo yoh kah noh say toh jee gyoh ay kyoh oh foo my tah yoo sen joon ee zoo keh. Koh reh sigh kyoh.

She kah she koh reh oh tah noh moo toh ee mah ma deh mee soo goh she teh tah zay jaku say gah tie ryoh nee mee tsoo kaht teh tie oh nee oh wah reh roo toh ee oo kee ken moh toh moh now, moh roh hah noh tsoo roo ghee.

Shee roh toh nee wah oh soo soo meh deh kee nye.

Mah oh mah eh rah doh shee roh toh wah, mee tie oh noh Dependabot Alerts deh moh nah gah meh teh nah sigh tteh koht tah.
"""

def main():
    cleaned = TUNED_SCRIPT.strip()
    with open("romaji.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("=== Successfully wrote bulletproof tuned romaji.txt ===")
    print(cleaned[:300] + "...")

if __name__ == "__main__":
    main()
