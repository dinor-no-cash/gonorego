export interface Env {
  AI: any;
  JOBS?: KVNamespace;
  GITHUB_OWNER: string;
  GITHUB_REPO: string;
  WORKFLOW_FILE: string;
  GITHUB_TOKEN?: string;
}

// In-memory fallback
const memoryJobs = new Map<string, any>();
const memoryMedia = new Map<string, ArrayBuffer>();

const SCRIPT_GEN_PROMPT = `
あなたは2000年代初頭の伝説的な2ちゃんねるFlash黄金期の作家（吉野家コピペ・ゴノレゴの作者）です。
ユーザーから与えられた【指定テーマ】に関する吉野家コピペパロディ台本を作成してください。

【吉野家コピペの重要な文脈構造・必須ルール】
原作の文脈構造を正確に守って執筆してください：
1. 「よーしパパ〜」は、初心者が浮かれて大口を叩く【浅い意気込み・大盤振る舞い】です（原作：よーしパパ特盛頼んじゃうぞー）。
2. 「とりあえず〜で」と「〜言いたいだけちゃうんかと」は、隣のにわかが通ぶってドヤ顔で口にする【安易な定番バズワード（変数：バズワード）】です（原作：つゆだく）。
※「よーしパパ〜」と「とりあえず〜で」には【絶対に別の言葉】を入れてください。同じ言葉を使うと文脈が完全に破綻します！
※「とりあえず[バズワード]で」と「お前、[バズワード]って言いたいだけちゃうんかと」の2箇所は【必ず全く同じバズワード】で一致させてください。

【台本テンプレート】
そんなことより聞いてくれよ１よ。昨日、[テーマ]の[場所やサイト]行ったんです。[場所やサイト]。そしたらなんか[にわかが集まる浅い状況]なんです。
もうね、アホかと。馬鹿かと。
お前らな、[些細なきっかけ]くらいで普段見向きもしない[テーマ]に群がってんじゃねーよ、ボケが。
よーしパパ[初心者が浮かれてやりがちな浅い意気込み]しちゃうぞー、とか言ってるの。もう見てらんない。
お前らな、[格上の厳しい現実]やるからその席空けろと。
[テーマ]ってのはな、もっと殺伐としてるべきなんだよ。
で、隣の奴が、とりあえず[バズワード]で、とか言ってるんです。
そこでまたぶち切れですよ。
あのな、[バズワード]なんてきょうび流行んねーんだよ。ボケが。
得意げな顔して何が、とりあえず[バズワード]で、だ。
お前は本当に[テーマの本質]を理解してるのかと問いたい。問い詰めたい。小一時間問い詰めたい。
お前、[バズワード]って言いたいだけちゃうんかと。
にわか有識者は、すっこんでろ。
[テーマ]通の俺から言わせてもらえば今、通の間での最新流行はやっぱり[マニアックなプロのこだわり]、これだね。
これが通の頼み方。
しかしこれをやると[重大なリスクやデメリット]という危険も伴う、諸刃の剣。素人にはおすすめしない。
まあお前らド素人は、[初心者向けの無難な代替案]でも眺めてなさいってこった。

【超重要ルール（厳格遵守）】
・最後の「〜ってこった。」で文章を絶対に終了してください。
・「〜ってこった。」の直後にセリフは終了です。その後に解説、注釈、感想、補足説明、挨拶、Markdownコードブロック、アスタリスク等は絶対に1文字も出力してはなりません！
・セリフ本文のみを出力してください。
`;

const ROMAJI_CONVERT_PROMPT = `
あなたはmacOSの英語音声合成エンジン「say -v Whisper」向けに日本語漫談を変換する高度なバイリンガルAIです。
Whisperは米語（米国英語）エンジンです。日本語をそのままローマ字にすると、英語フォニックス（特にサイレントEや長母音）で激しく英語誤読されます。
特に「a」「i」「e」の母音は間違いの元凶です（例：『みて』を『mite』と書くとダニの『マイト』と読まれてしまう）。

以下の3大原則と【母音フォニックス工夫ルール】を厳守して変換してください：

【原則1：英単語はそのまま残す】
テキスト内のアルファベット英単語（Transformers, LLM, Docker, Kubernetes, PyTorch, GPU, API等）は絶対にカタカナ化せず、英単語のスペルを100%維持する。

【原則2：カタカナ外来語は英語スペルにする】
英語由来のカタカナ語（ローカル->local, コミュニティ->community, チュートリアル->tutorial, モデル->model, ワイン->wine, マーケティング->marketing等）は、自律的に元の英語スペルに変換する。

【原則3：日本語の『a』『i』『e』の母音フォニックス工夫（超重要！）】
英語のサイレントE・長母音誤読を物理的に防ぐため、日本語の母音を以下のように工夫してください：
・「みて」->「mee teh」または「mih teh」（※絶対にmiteと書かない！）
・「きて」->「kee teh」（※絶対にkiteと書かない！）
・「して」->「shee teh」（※絶対にshiteやsiteと書かない！）
・「え段（e）」の語尾は「eh」にしてサイレントEを防止する（te->teh, de->deh, ke->keh, re->reh, me->meh）。
・「い段（i）」の音は「ee」と表記して確実に日本語の『イ』を発音させる（mi->mee, ki->kee, shi->shee, chi->chee, ni->nee）。
・「あ段（a）」の単独・語頭は「ah」と表記して確実に『ア』を発音させる（a->ah, ka->kah, ma->mah）。
・「お前ら」->「oh mah eh rah」
・「見てらんない」->「mee teh rahn nye」
・「空けろ」->「ah keh roh」
・「素人」->「shee roh oo toh」
・「小一時間問い詰めたい」->「ko ichi jikan toi tsume tai」
・「諸刃の剣」->「moroha no tsurugi」
・「ブチ切れ」->「buchi kee reh」
・「最新流行」->「saishin ryuukou」
・「大規模」->「dah ee kee boh」（※英語では『dai』はdaily/aidのように必ず『デイ』と読まれるため、daikiboと書くと100%『でえきぼ』になります！必ず『dah ee kee boh』と書くこと！）
・「にわか」->「nee wah kah」（※英語では『ni』はnice/nightのように『ナイ』と読まれるため、niwakaと書くと100%『ないわか』になります！必ず『nee wah kah』と書くこと！）
・「開発」->「kah ee hah tsoo」（※英語では『ai』はrain/waitのように必ず『エイ』と読まれるため、kaihatsuと書くと100%『ケイハツ』になります！必ず『kah ee hah tsoo』と書くこと！）
・「アイ（ai）」の音はすべて「ah ee」に音節分解して確実に『アイ』を発音させる（例：大規模->dah ee kee boh, 開発->kah ee hah tsoo, サイゼリヤ->Sah ee zeh ree yah, 〜たい->tah ee, 〜ない->nah ee）
・助詞「が」->「gah」（※gaと書くとジョージア州GA「ジー・エー」と誤読されます！必ずgahと書くこと！）
・助詞「は」->「wah」
・助詞「で」->「deh」
・助詞「と」->「toh」
・助詞「の」->「noh」
・「ってこった」->「tte kotta」

【変換の手本（Few-Shot Example）】
入力：
そんな事より聞いてくれよ１よ。昨日、ローカルLLMの開発コミュニティ行ったんです。
もう見てらんない。使ってみてどうだったか聞いてみたい。
隣の奴が、とりあえずTransformersで、とか言ってるんです。そこでまたブチ切れですよ。
小一時間問い詰めたい。諸刃の剣。素人にはおすすめしない。
まあお前らド素人は、事前学習済みモデルのパラメーターでも眺めてなさいってこった。

出力：
sonna koto yori kiite kure yo ichi yo. kino, local LLM noh kah ee hah tsoo community itta n desu.
mou mee teh rahn nye. tsukatte mee teh doh dah tah kah kiite mee tai.
tonari no yatsu gah, toriaezu Transformers deh, toh ka itte ru n desu. soh koh deh mata buchi kee reh desu yo.
ko ichi jikan toi tsume tai. moroha no tsurugi. shee roh oo toh ni wa osusume shi nai.
maa oh mah eh rah do shee roh oo toh wa, pre-trained model no parameter demo nah gah meh teh nah sigh tte kotta.

【厳格なフォーマット制約】
・入力の行数と出力の行数を完全に一致（1対1）させてください。
・解説、挨拶、Markdownコードブロック等は一切含めず、変換後のテキストのみを出力してください。
`;

// 台本から余計な解説文・末尾テキストを完全に切り落とすサニタイザー
function cleanScriptText(raw: string): string {
  if (!raw) return "";
  let s = raw.trim();

  // コードブロック除去
  s = s.replace(/^```[a-z]*\n?/i, "").replace(/\n?```$/, "");

  // 導入文除去
  s = s.replace(/^(?:了解(?:いた)?しました|以下(?:は|が)?(?:台本|セリフ).*?です[：:\n]*)/i, "").trim();

  // 最重要：終了アンカー（文末オチ句）で以降をバッサリ切断
  // 「〜ってこった」「〜ってことだ」「〜って事だ」「〜ってわけだ」「〜てなもんだ」などの最後の出現位置を探す
  const anchors = [
    /(?:ってこった|てこった|ってことだ|って事だ|ってわけだ|てなもんだ)[。！？!?\s]*/g,
    /(?:眺めてなさい|見てなさい|食ってなさい|すっこんでろ)[。！？!?\s]*/g
  ];

  for (const pat of anchors) {
    const matches = Array.from(s.matchAll(pat));
    if (matches.length > 0) {
      const lastMatch = matches[matches.length - 1];
      const endPos = (lastMatch.index ?? 0) + lastMatch[0].length;
      s = s.substring(0, endPos).trim();
      break;
    }
  }

  // 保険：解説や注釈の除去
  const cutoffMatch = s.match(/([\s\S]*?)(?:\n\s*(?:【(?:解説|注意|注釈|補足|ポイント)】|解説[:：]|注[:：]|※|Note:|Explanation:|###|\*\*\*|---))/i);
  if (cutoffMatch && cutoffMatch[1]) {
    s = cutoffMatch[1].trim();
  }

  return s;
}

// ★一元フォニックス音節変換エンジン (Syllabic Phonics Transliteration Engine)★
// 英語として保護する英単語・技術用語・外来語
const PROTECTED_ENGLISH_WORDS = new Set([
  'transformers', 'transformer', 'llm', 'local', 'community', 'docker',
  'kubernetes', 'pytorch', 'gpu', 'api', 'model', 'parameter', 'parameters',
  'tutorial', 'wine', 'marketing', 'saizeriya', 'saize', 'pre-trained',
  'fine-tuning', 'ai', 'ui', 'web', 'github', 'actions', 'open', 'webui',
  'prompt', 'prompts', 'token', 'tokens', 'agent', 'agents', 'code', 'data',
  'cache', 'pipeline', 'workflow', 'server', 'client', 'json', 'python'
]);

function isProtectedEnglish(token: string): boolean {
  const clean = token.replace(/[^a-zA-Z\-]/g, '');
  if (!clean) return true;
  if (/[A-Z]/.test(clean)) return true;
  if (PROTECTED_ENGLISH_WORDS.has(clean.toLowerCase())) return true;
  return false;
}

// 既にフォニックス化済みの音節か判定
const ALREADY_PHONETIC_REGEX = /(?:[aeo]h|ee|oo|tsoo|ghee|gheh)\b/i;

// 一元音節変換テーブル（最長一致）
const SYLLABLE_MAP: [string, string][] = [
  // 拗音・特殊音節 (3文字)
  ['kya', 'kyah'], ['kyu', 'kyoo'], ['kyo', 'kyoh'],
  ['sha', 'shah'], ['shu', 'shoo'], ['sho', 'shoh'],
  ['cha', 'chah'], ['chu', 'choo'], ['cho', 'choh'],
  ['nya', 'nyah'], ['nyu', 'nyoo'], ['nyo', 'nyoh'],
  ['hya', 'hyah'], ['hyu', 'hyoo'], ['hyo', 'hyoh'],
  ['mya', 'myah'], ['myu', 'myoo'], ['myo', 'myoh'],
  ['rya', 'ryah'], ['ryu', 'ryoo'], ['ryo', 'ryoh'],
  ['gya', 'gyah'], ['gyu', 'gyoo'], ['gyo', 'gyoh'],
  ['bya', 'byah'], ['byu', 'byoo'], ['byo', 'byoh'],
  ['pya', 'pyah'], ['pyu', 'pyoo'], ['pya', 'pyoh'],
  ['tsu', 'tsoo'], ['chi', 'chee'], ['shi', 'shee'],

  // 二重母音 (最重要：英語フォニックスでエイ/アウ/オイ等になるのを音節分解で物理阻止)
  ['dai', 'dah ee'], ['kai', 'kah ee'], ['sai', 'sah ee'], ['tai', 'tah ee'],
  ['nai', 'nah ee'], ['hai', 'hah ee'], ['mai', 'mah ee'], ['yai', 'yah ee'],
  ['rai', 'rah ee'], ['wai', 'wah ee'], ['gai', 'gah ee'], ['zai', 'zah ee'],
  ['bai', 'bah ee'], ['pai', 'pah ee'], ['ai', 'ah ee'],

  ['toi', 'toh ee'], ['koi', 'koh ee'], ['soi', 'soh ee'], ['noi', 'noh ee'],
  ['hoi', 'hoh ee'], ['moi', 'moh ee'], ['yoi', 'yoh ee'], ['roi', 'roh ee'],
  ['goi', 'goh ee'], ['zoi', 'zoh ee'], ['boi', 'boh ee'], ['poi', 'poh ee'],
  ['oi', 'oh ee'],

  ['tui', 'too ee'], ['kui', 'koo ee'], ['sui', 'soo ee'], ['tsui', 'tsoo ee'],
  ['nui', 'noo ee'], ['rui', 'roo ee'], ['gui', 'goo ee'], ['ui', 'oo ee'],

  ['tei', 'teh ee'], ['kei', 'keh ee'], ['sei', 'seh ee'], ['nei', 'neh ee'],
  ['hei', 'heh ee'], ['mei', 'meh ee'], ['rei', 'reh ee'], ['gei', 'gheh ee'],
  ['zei', 'zeh ee'], ['bei', 'beh ee'], ['pei', 'peh ee'], ['ei', 'eh ee'],

  // 長音 ou / uu
  ['ryuu', 'ryoo'], ['chuu', 'choo'], ['shuu', 'shoo'], ['kyuu', 'kyoo'],
  ['kou', 'koh'], ['sou', 'soh'], ['tou', 'toh'], ['nou', 'noh'],
  ['hou', 'hoh'], ['mou', 'moh'], ['you', 'yoh'], ['rou', 'roh'],
  ['gou', 'goh'], ['zou', 'zoh'], ['dou', 'doh'], ['bou', 'boh'],
  ['shou', 'shoh'], ['chou', 'choh'], ['ryou', 'ryoh'], ['kyou', 'kyoh'],

  // 2文字（子音 + 母音）
  ['ka', 'kah'], ['ki', 'kee'], ['ku', 'koo'], ['ke', 'keh'], ['ko', 'koh'],
  ['sa', 'sah'], ['si', 'shee'], ['su', 'soo'], ['se', 'seh'], ['so', 'soh'],
  ['ta', 'tah'], ['ti', 'chee'], ['tu', 'tsoo'], ['te', 'teh'], ['to', 'toh'],
  ['na', 'nah'], ['ni', 'nee'], ['nu', 'noo'], ['ne', 'neh'], ['no', 'noh'],
  ['ha', 'hah'], ['hi', 'hee'], ['hu', 'foo'],  ['he', 'heh'], ['ho', 'hoh'],
  ['ma', 'mah'], ['mi', 'mee'], ['mu', 'moo'], ['me', 'meh'], ['mo', 'moh'],
  ['ya', 'yah'], ['yu', 'yoo'], ['yo', 'yoh'],
  ['ra', 'rah'], ['ri', 'ree'], ['ru', 'roo'], ['re', 'reh'], ['ro', 'roh'],
  ['wa', 'wah'], ['wo', 'woh'],
  // 濁音・半濁音（ghee, gheh で軟音化ジェ/ジを物理阻止）
  ['ga', 'gah'], ['gi', 'ghee'], ['gu', 'goo'], ['ge', 'gheh'], ['go', 'goh'],
  ['za', 'zah'], ['ji', 'jee'],  ['zu', 'zoo'], ['ze', 'zeh'],  ['zo', 'zoh'],
  ['da', 'dah'], ['di', 'jee'],  ['du', 'zoo'], ['de', 'deh'],  ['do', 'doh'],
  ['ba', 'bah'], ['bi', 'bee'],  ['bu', 'boo'], ['be', 'beh'],  ['bo', 'boh'],
  ['pa', 'pah'], ['pi', 'pee'],  ['pu', 'poo'], ['pe', 'peh'],  ['po', 'poh'],
  ['fu', 'foo'],

  // 単独母音（1文字）
  ['a', 'ah'], ['i', 'ee'], ['u', 'oo'], ['e', 'eh'], ['o', 'oh']
];

function transliterateSyllables(romajiWord: string): string {
  const w = romajiWord.toLowerCase();
  const res: string[] = [];
  let i = 0;
  const n = w.length;

  while (i < n) {
    // 促音（っ: kk, tt, ss, pp 等）
    if (i + 1 < n && w[i] === w[i+1] && 'bcdfghjklmpqrstvwxyz'.includes(w[i]) && w[i] !== 'n') {
      res.push(w[i] + ' ');
      i += 1;
      continue;
    }

    // 撥音（ん: n）
    if (w[i] === 'n') {
      if (i + 1 === n || (!'aiueoy'.includes(w[i+1]) && !(i + 2 <= n && ['ya','yu','yo'].includes(w.substring(i+1, i+3))))) {
        res.push('n');
        i += 1;
        continue;
      }
    }

    let matched = false;
    for (const [syl, rep] of SYLLABLE_MAP) {
      if (w.startsWith(syl, i)) {
        res.push(rep);
        i += syl.length;
        matched = true;
        break;
      }
    }
    if (!matched) {
      res.push(w[i]);
      i += 1;
    }
  }
  return res.join(' ');
}

function applyPhoneticTransliteration(text: string): string {
  const tokens = text.split(/([a-zA-Z0-9_\-]+|[^\s\w]+|\s+)/);
  const out: string[] = [];

  for (const t of tokens) {
    if (!t) continue;
    if (/^[a-zA-Z0-9_\-]+$/.test(t)) {
      if (isProtectedEnglish(t) || ALREADY_PHONETIC_REGEX.test(t)) {
        out.push(t);
      } else {
        out.push(transliterateSyllables(t));
      }
    } else {
      out.push(t);
    }
  }
  return out.join('').replace(/[ \t]+/g, ' ');
}

// Whisper向けローマ字の英語誤読を機械的に撲滅する置換テーブル
function sanitizePhoneticRomaji(text: string): string {
  if (!text) return "";
  let r = text.trim();

  // コードブロック除去
  r = r.replace(/^```[a-z]*\n?/i, "").replace(/\n?```$/, "");

  // 終了アンカー以降の切り落とし（最後のオチ句以降を完全切断）
  const anchors = [
    /(?:tteh\s+koht\s+tah|teh\s+koht\s+tah|tteh\s+kotta|teh\s+kotta|tte\s+kotta|te\s+kotta|koht\s+tah|kotta)[.!?\s]*/gi,
    /(?:nah\s+gah\s+meh\s+teh\s+nah\s+sigh|nagamete\s+nasai)[.!?\s]*/gi
  ];
  for (const pat of anchors) {
    const matches = Array.from(r.matchAll(pat));
    if (matches.length > 0) {
      const lastMatch = matches[matches.length - 1];
      const endPos = (lastMatch.index ?? 0) + lastMatch[0].length;
      r = r.substring(0, endPos).trim();
      break;
    }
  }

  // ★「a」「i」「e」フォニックス誤読（サイレントE・長母音）の機械的撲滅ルール★
  const phonicsFixes: [RegExp, string][] = [
    // 冒頭の日本語残り防止
    [/そんな事より聞いてくれよ(?:１|1|一)?よ?/g, "sonna koto yori kiite kure yo ichi yo"],
    [/昨日/g, "kino"],
    [/サイゼリヤ/g, "Saizeriya"],
    [/サイゼ/g, "Saize"],

    // 「みて」が英語の「mite（マイト）」になるのを完全防止
    [/\bmite\b/gi, "mee teh"],
    [/\bmita\b/gi, "mee tah"],
    [/\bmiteran\b/gi, "mee teh rahn"],
    // 「きて」が英語の「kite（カイト）」になるのを完全防止
    [/\bkite\b/gi, "kee teh"],
    [/\bkita\b/gi, "kee tah"],
    // 「して」が英語の「site/shite」になるのを完全防止
    [/\bshite\b/gi, "shee teh"],
    [/\bshita\b/gi, "shee tah"],
    // 「あけて」が英語の「ake（エイク）」になるのを完全防止
    [/\bakete\b/gi, "ah keh teh"],
    [/\bakero\b/gi, "ah keh roh"],
    // 「まけて」が英語の「make（メイク）」になるのを完全防止
    [/\bmake\b/gi, "mah keh"],
    [/\bmakete\b/gi, "mah keh teh"],
    // 「まで」が英語の「made（メイド）」になるのを完全防止
    [/\bmade\b/gi, "mah deh"],
    // 「さけ」が英語の「sake（セイク）」になるのを完全防止
    [/\bsake\b/gi, "sah keh"],
    // 「ため」が英語の「tame（テイム）」になるのを完全防止
    [/\btame\b/gi, "tah meh"],
    // 「だれ」が英語の「dare（デア）」になるのを完全防止
    [/\bdare\b/gi, "dah reh"],
    // 「これ」「それ」「あれ」「おれ」
    [/\bkore\b/gi, "koh reh"],
    [/\bsore\b/gi, "soh reh"],
    [/\bare\b/gi, "ah reh"],
    [/\bore\b/gi, "oh reh"],
    // 「お前」「お前ら」
    [/\bomae\b/gi, "oh mah eh"],
    [/\bomaera\b/gi, "oh mah eh rah"],
    [/\bomae-ra\b/gi, "oh mah eh rah"],
    // 「なさい」「ながめて」
    [/\bnasai\b/gi, "nah sigh"],
    [/\bnagamete\b/gi, "nah gah meh teh"],

    // 誤爆したToransufaamazuの救済
    [/\b(?:toransufaamazu|toransufaamaa)\b/gi, "Transformers"],
    [/トランスフォーマーズ?/g, "Transformers"],

    // ゴノレゴ象徴フレーズの固定ガード
    [/\b(?:toikurumetai|toitsumetai|toishimetai)\b/gi, "toi tsume tai"],
    [/\b(?:sho\s*ichi\s*jikan|shoichijikan|shouichijikan)\b/gi, "ko ichi jikan"],
    [/\b(?:moro\s*no\s*yaiba|moronoyaiba)\b/gi, "moroha no tsurugi"],
    [/\b(?:buchikire|buchi\s*kire)\b/gi, "buchi kee reh"],
    [/\b(?:sujin)\b/gi, "shee roh oo toh"],
    [/\b(?:do\s*sujin|dosujin)\b/gi, "do shee roh oo toh"],
    [/\b(?:shirouto)\b/gi, "shee roh oo toh"],
    [/\b(?:hayari|hayarin)\b/gi, "ryuukou"],
    [/\b(?:tte\s+)?kotta\b/gi, "tte kotta"],
    [/\bichi\s*yo\b/gi, "ichi yo"],

    // ★最重要：「ai」を英語の「エイ（/eɪ/）」と誤読させない音節分解★
    // 「開発（kaihatsu）」がrain/waitと同じaiで「ケイハツ」になるのを完全根絶
    [/\b(?:kaihatsu|keihatsu)\b/gi, "kah ee hah tsoo"],
    [/開発/g, "kah ee hah tsoo"],

    // 「アイ」母音のエイ誤読防止
    [/\biitai\b/gi, "ee tah ee"],
    [/\bmitai\b/gi, "mee tah ee"],
    [/\btoitai\b/gi, "toh ee tah ee"],
    [/\btsumetai\b/gi, "tsoo meh tah ee"],

    // ★最重要：助詞の英語略称・フォニックス誤読の機械的撲滅★
    // 「が」がジョージア州GA「ジー・エー」になるのを完全排除
    [/\bga\b/gi, "gah"],
    // 「は」
    [/\bha\b/gi, "wah"],
    [/\bwa\b/gi, "wah"],
    // 「で」がデラウェア州DE「ディー・イー」になるのを完全排除
    [/\bde\b/gi, "deh"],
    // 「だ」
    [/\bda\b/gi, "dah"],
    // 「と」が前置詞to「トゥー」になるのを防止
    [/\bto\b/gi, "toh"],
    // 「の」がno「ノー」になるのを防止
    [/\bno\b/gi, "noh"],
    // 「も」がミズーリ州MO「エム・オー」になるのを防止
    [/\bmo\b/gi, "moh"],
    // 「へ」が英語he「ヒー」になるのを防止
    [/\bhe\b/gi, "eh"],
  ];

  for (const [pattern, replacement] of phonicsFixes) {
    r = r.replace(pattern, replacement);
  }

  // ★一元フォニックス音節変換：残ったすべての未変換ローマ字単語を一網打尽に変換★
  r = applyPhoneticTransliteration(r);

  r = r.replace(/[ \t]+/g, " ");
  return r;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json",
    };

    // 1. API: Generate Script from Theme
    if (url.pathname === "/api/generate-script" && request.method === "POST") {
      try {
        const { theme } = (await request.json()) as { theme: string };
        if (!theme) {
          return new Response(JSON.stringify({ error: "Theme is required" }), { status: 400, headers: corsHeaders });
        }

        const aiRes = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
          messages: [
            { role: "system", content: SCRIPT_GEN_PROMPT.trim() },
            { role: "user", content: `テーマ: ${theme}` },
          ],
          max_tokens: 2048,
        });

        const rawScript = aiRes.response.trim();
        const script = cleanScriptText(rawScript);
        return new Response(JSON.stringify({ script }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // 2. API: Convert Japanese to Phonetic Romaji
    if (url.pathname === "/api/convert" && request.method === "POST") {
      try {
        const { text } = (await request.json()) as { text: string };
        if (!text) {
          return new Response(JSON.stringify({ error: "Text is required" }), { status: 400, headers: corsHeaders });
        }

        const aiRes = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
          messages: [
            { role: "system", content: ROMAJI_CONVERT_PROMPT.trim() },
            { role: "user", content: `次の日本語をWhisper用ローマ字に変換してください:\n${text}` },
          ],
          max_tokens: 2048,
        });

        const rawRomaji = aiRes.response.trim();
        const romaji = sanitizePhoneticRomaji(rawRomaji);
        return new Response(JSON.stringify({ romaji }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // 3. API: Upload media directly from GitHub Actions (bypass zip!)
    if (url.pathname === "/api/upload" && request.method === "POST") {
      try {
        const jobId = url.searchParams.get("job_id");
        const type = url.searchParams.get("type"); // 'video' or 'audio'
        if (!jobId || !type) {
          return new Response(JSON.stringify({ error: "job_id and type required" }), { status: 400, headers: corsHeaders });
        }

        const arrayBuffer = await request.arrayBuffer();
        if (env.JOBS) {
          await env.JOBS.put(`media:${jobId}:${type}`, arrayBuffer, { expirationTtl: 86400 });
        } else {
          memoryMedia.set(`media:${jobId}:${type}`, arrayBuffer);
        }

        return new Response(JSON.stringify({ ok: true, size: arrayBuffer.byteLength }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // 4. API: Stream media file (MP4 / WAV) directly for inline preview & download
    if (url.pathname.startsWith("/media/")) {
      const match = url.pathname.match(/\/media\/([^.]+)\.(mp4|wav)$/);
      if (!match) {
        return new Response("Not Found", { status: 404 });
      }

      const jobId = match[1];
      const ext = match[2];
      const type = ext === "mp4" ? "video" : "audio";
      const contentType = ext === "mp4" ? "video/mp4" : "audio/wav";

      let data: ArrayBuffer | null = null;
      if (env.JOBS) {
        data = await env.JOBS.get(`media:${jobId}:${type}`, { type: "arrayBuffer" });
      } else {
        data = memoryMedia.get(`media:${jobId}:${type}`) || null;
      }

      if (!data) {
        return new Response("Media not found or expired", { status: 404 });
      }

      return new Response(data, {
        headers: {
          "Content-Type": contentType,
          "Content-Length": data.byteLength.toString(),
          "Accept-Ranges": "bytes",
          "Cache-Control": "public, max-age=86400",
          "Content-Disposition": `inline; filename="gonorego_${jobId}.${ext}"`,
        },
      });
    }

    // 5. API: Trigger GitHub Actions Render
    if (url.pathname === "/api/generate" && request.method === "POST") {
      try {
        const { script_romaji: inRomaji, script_japanese: inJapanese, rate = "128", pitch = "-15" } = (await request.json()) as {
          script_romaji: string;
          script_japanese?: string;
          rate?: string;
          pitch?: string;
        };
        const script_romaji = sanitizePhoneticRomaji(inRomaji);
        const script_japanese = cleanScriptText(inJapanese || "");

        if (!script_romaji) {
          return new Response(JSON.stringify({ error: "Script is required" }), { status: 400, headers: corsHeaders });
        }

        const jobId = `gonorego-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
        const callbackUrl = `${url.origin}/api/callback`;

        if (env.JOBS) {
          await env.JOBS.put(jobId, JSON.stringify({ status: "processing", updated_at: Date.now() }), { expirationTtl: 3600 });
        } else {
          memoryJobs.set(jobId, { status: "processing", updated_at: Date.now() });
        }

        const ghToken = env.GITHUB_TOKEN;
        if (!ghToken) {
          return new Response(JSON.stringify({ error: "GITHUB_TOKEN not configured" }), { status: 500, headers: corsHeaders });
        }

        const ghRes = await fetch(
          `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/${env.WORKFLOW_FILE}/dispatches`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${ghToken}`,
              Accept: "application/vnd.github.v3+json",
              "User-Agent": "Instant-Gonorego-Cloudflare-Worker",
            },
            body: JSON.stringify({
              ref: "main",
              inputs: {
                job_id: jobId,
                script_romaji: script_romaji,
                script_japanese: script_japanese || "",
                rate: rate,
                pitch_baseline: pitch,
                callback_url: callbackUrl,
              },
            }),
          }
        );

        if (!ghRes.ok) {
          const errText = await ghRes.text();
          return new Response(JSON.stringify({ error: `GitHub API error: ${errText}` }), { status: 502, headers: corsHeaders });
        }

        return new Response(JSON.stringify({ job_id: jobId, status: "processing" }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // 6. API: Check Job Status
    if (url.pathname.startsWith("/api/status") && request.method === "GET") {
      const jobId = url.searchParams.get("id");
      if (!jobId) {
        return new Response(JSON.stringify({ error: "Job ID required" }), { status: 400, headers: corsHeaders });
      }

      let job = null;
      if (env.JOBS) {
        const val = await env.JOBS.get(jobId);
        job = val ? JSON.parse(val) : null;
      } else {
        job = memoryJobs.get(jobId) || null;
      }

      if (!job) {
        return new Response(JSON.stringify({ status: "not_found" }), { status: 404, headers: corsHeaders });
      }

      return new Response(JSON.stringify(job), { headers: corsHeaders });
    }

    // 7. API: Callback from GitHub Actions
    if (url.pathname === "/api/callback" && request.method === "POST") {
      try {
        const data = (await request.json()) as { job_id: string; status: string; run_url?: string };
        const videoUrl = `${url.origin}/media/${data.job_id}.mp4`;
        const audioUrl = `${url.origin}/media/${data.job_id}.wav`;

        const jobData = {
          status: data.status === "success" ? "completed" : "failed",
          video_url: videoUrl,
          audio_url: audioUrl,
          run_url: data.run_url || "",
          updated_at: Date.now(),
        };

        if (env.JOBS) {
          await env.JOBS.put(data.job_id, JSON.stringify(jobData), { expirationTtl: 86400 });
        } else {
          memoryJobs.set(data.job_id, jobData);
        }

        return new Response(JSON.stringify({ ok: true }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // Default: Serve Full Retro UI HTML (Strict no-cache to guarantee latest JS)
    return new Response(UI_HTML, {
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      },
    });
  },
};

const UI_HTML = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>★ インスタント・ゴノレゴ生成器 (Instant Gonorego) ★</title>
  <style>
    body {
      background-color: #1a1a1a;
      color: #eeeeee;
      font-family: "MS PGothic", "IPAMonaPGothic", "Mona", sans-serif;
      margin: 0;
      padding: 15px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .container {
      max-width: 820px;
      width: 100%;
      background: #111111;
      border: 3px solid #ff6600;
      padding: 20px;
      box-shadow: 0 0 25px rgba(255, 102, 0, 0.5);
      box-sizing: border-box;
    }
    h1 {
      color: #ff6600;
      font-size: 24px;
      margin-top: 0;
      text-align: center;
      border-bottom: 2px dashed #ff6600;
      padding-bottom: 8px;
    }
    .banner {
      background: #ff6600;
      color: #000;
      font-weight: bold;
      padding: 6px;
      text-align: center;
      margin-bottom: 15px;
      font-size: 13px;
    }
    .card {
      background: #1e1e1e;
      border: 1px solid #444;
      padding: 14px;
      margin-bottom: 15px;
    }
    .card-title {
      font-weight: bold;
      color: #ffcc00;
      font-size: 14px;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    input[type="text"] {
      width: 100%;
      background: #000;
      color: #fff;
      border: 1px solid #666;
      padding: 8px 10px;
      font-size: 15px;
      box-sizing: border-box;
    }
    textarea {
      width: 100%;
      height: 120px;
      background: #000;
      color: #00ff66;
      border: 1px solid #555;
      padding: 10px;
      font-family: monospace;
      font-size: 13px;
      box-sizing: border-box;
      resize: vertical;
    }
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      margin-top: 10px;
      align-items: center;
    }
    .btn {
      background: #ff6600;
      color: #fff;
      border: none;
      padding: 10px 20px;
      font-size: 15px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 2px 2px 0 #993d00;
      transition: background 0.1s;
    }
    .btn:hover {
      background: #ff8533;
    }
    .btn:active {
      transform: translate(1px, 1px);
      box-shadow: 1px 1px 0 #993d00;
    }
    .btn:disabled {
      background: #555;
      cursor: not-allowed;
      box-shadow: none;
    }
    .btn-ai {
      background: #2b5bb3;
      box-shadow: 2px 2px 0 #1a3870;
      font-size: 13px;
      padding: 7px 15px;
    }
    .btn-ai:hover {
      background: #3b74db;
    }
    .btn-gen {
      background: #d9381e;
      box-shadow: 3px 3px 0 #801d0c;
      font-size: 18px;
      padding: 14px 28px;
      width: 100%;
    }
    .btn-gen:hover {
      background: #f0482c;
    }
    .status-area {
      margin-top: 20px;
      padding: 20px;
      background: #000;
      border: 2px dashed #ff6600;
      display: none;
      text-align: center;
    }
    .spinner {
      display: inline-block;
      width: 30px;
      height: 30px;
      border: 3px solid rgba(255,102,0,.3);
      border-radius: 50%;
      border-top-color: #ff6600;
      animation: spin 1s ease-in-out infinite;
      margin-bottom: 10px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .video-container {
      margin-top: 20px;
      display: none;
      text-align: center;
      background: #000;
      padding: 15px;
      border: 2px solid #00ff66;
    }
    video {
      max-width: 100%;
      max-height: 440px;
      border: 2px solid #444;
      background: #000;
    }
    .download-btns {
      margin-top: 15px;
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .marquee {
      color: #ffcc00;
      font-weight: bold;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>★ インスタント・ゴノレゴ生成器 ★</h1>
    <div class="banner">【2001年FLASH黄金期】元祖ゴノレゴ脱力Flash ✕ macOS Whisper 実機合成</div>

    <!-- STEP 1: AI台本自動生成 -->
    <div class="card">
      <div class="card-title">① テーマを入力して吉野家構文の台本を自動執筆（Workers AI）:</div>
      <div style="display:flex; gap:10px;">
        <input type="text" id="inputTheme" placeholder="例: Docker開発環境, PHP脆弱性対応, 新NISA, 筋トレ, 推し活, タスク管理...">
        <button class="btn btn-ai" style="white-space:nowrap;" onclick="generateScriptFromTheme()">台本を自動執筆！</button>
      </div>
      <div style="font-size:11px; color:#888; margin-top:5px;">※「そんなことより聞いてくれよ１よ」「アホかとバカかと」「諸刃の剣」「〜しとけってこった」の黄金構成で出力します</div>
    </div>

    <!-- STEP 2: 台本編集 & ローマ字変換 -->
    <div class="card">
      <div class="card-title">② 日本語セリフ台本（手動入力・編集可能）:</div>
      <textarea id="inputJa" placeholder="そんなことより聞いてくれよ１よ。昨日、Twitter見たんです。Twitter。そしたらなんか普段は脆弱性の話なんかしない連中まで、PHPの脆弱性で大騒ぎしてるんです。もうね、アホかと。馬鹿かと..."></textarea>
      <div style="margin-top:8px;">
        <button class="btn btn-ai" onclick="convertText()">AIでWhisper専用ローマ字に調声変換！</button>
      </div>
    </div>

    <!-- STEP 3: ローマ字調声 & 速度調整 -->
    <div class="card">
      <div class="card-title">③ 調声済みローマ字（Whisper誤読排除スクリプト・編集可能）:</div>
      <textarea id="previewRomaji" placeholder="AI変換ボタンを押すと自動入力されます（手動で微調整も可能）"></textarea>
      
      <div class="controls">
        <div>
          <label style="color:#ffcc00; font-weight:bold;">話速:</label>
          <select id="rateSelect" style="background:#000; color:#fff; border:1px solid #666; padding:4px;">
            <option value="128" selected>128 (吉野家ゴノレゴ完全再現・重厚ドス)</option>
            <option value="138">138 (標準レート)</option>
            <option value="145">145 (明瞭まくしたて・速口)</option>
          </select>
        </div>
        <div>
          <label style="color:#ffcc00; font-weight:bold;">ピッチ:</label>
          <select id="pitchSelect" style="background:#000; color:#fff; border:1px solid #666; padding:4px;">
            <option value="-15" selected>-15 (超重厚ドス)</option>
            <option value="-10">-10 (標準低音)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- STEP 4: 動画生成ボタン -->
    <div style="text-align: center; margin-top: 15px;">
      <button id="generateBtn" class="btn btn-gen" onclick="startGeneration()">🔥 怒涛のゴノレゴ動画を生成する！ (MP4) 🔥</button>
    </div>

    <!-- 生成中ステータス -->
    <div id="statusArea" class="status-area">
      <div class="spinner"></div>
      <div id="statusText" class="marquee">ただいまゴノレゴが熱弁中...</div>
      <div style="font-size: 12px; color: #aaa; margin-top: 8px;">macOS実機 Whisperエンジンでレンダリング＆Flash背景動画を合成しています（約35秒）</div>
    </div>

    <!-- 完成動画プレイヤー (直接インライン再生 & 単体保存) -->
    <div id="videoContainer" class="video-container">
      <h3 style="color:#00ff66; margin-top:0;">＼ ゴノレゴ動画の生成が完了しました！ ／</h3>
      <video id="resultVideo" controls autoplay playsinline></video>
      <div class="download-btns">
        <a id="downloadVideoLink" class="btn" style="text-decoration:none;" download>📥 MP4動画を保存（zipなし直接保存）</a>
        <a id="downloadAudioLink" class="btn" style="background:#333; text-decoration:none;" download>🎵 WAV音声を保存</a>
      </div>
    </div>
  </div>

  <script>
    // 1. テーマから台本自動執筆 & 自動調声変換
    async function generateScriptFromTheme() {
      const theme = document.getElementById("inputTheme").value.trim();
      if (!theme) return alert("テーマを入力してください！（例: Docker環境、新NISA、PHP脆弱性など）");

      const inputJa = document.getElementById("inputJa");
      const preview = document.getElementById("previewRomaji");
      inputJa.value = "Workers AI が吉野家コピペ構文で台本を執筆中...";
      preview.value = "台本完成後に最新音素ルールで自動調声します...";

      try {
        const res = await fetch("/api/generate-script", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ theme })
        });
        const data = await res.json();
        if (data.script) {
          inputJa.value = data.script;
          // 台本生成完了後、直ちに最新のWhisper調声変換を自動実行！
          await convertText();
        } else {
          inputJa.value = "生成失敗: " + (data.error || "不明なエラー");
          preview.value = "";
        }
      } catch (err) {
        inputJa.value = "通信エラー: " + err.message;
        preview.value = "";
      }
    }

    // 2. 日本語からWhisper専用ローマ字変換
    async function convertText() {
      const text = document.getElementById("inputJa").value.trim();
      if (!text) return alert("日本語セリフを入力してください！");

      const preview = document.getElementById("previewRomaji");
      preview.value = "Workers AI がWhisper誤読排除ローマ字に調声中...";

      try {
        const res = await fetch("/api/convert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });
        const data = await res.json();
        if (data.romaji) {
          preview.value = data.romaji;
        } else {
          preview.value = "変換エラー: " + (data.error || "不明");
        }
      } catch (err) {
        preview.value = "通信エラー: " + err.message;
      }
    }

    // 3. 動画生成リクエスト（最新の調声を完全同期）
    async function startGeneration() {
      const ja = document.getElementById("inputJa").value.trim();
      if (!ja) return alert("台本を入力するか、テーマから台本を生成してください！");

      let romaji = document.getElementById("previewRomaji").value.trim();
      if (!romaji || romaji.startsWith("Workers AI") || romaji.startsWith("台本完成後")) {
        await convertText();
        romaji = document.getElementById("previewRomaji").value.trim();
      }

      if (!romaji || romaji.startsWith("変換エラー") || romaji.startsWith("通信エラー")) {
        return alert("ローマ字スクリプトの準備ができませんでした。");
      }

      const rate = document.getElementById("rateSelect").value;
      const pitch = document.getElementById("pitchSelect").value;
      const btn = document.getElementById("generateBtn");
      const statusArea = document.getElementById("statusArea");
      const videoContainer = document.getElementById("videoContainer");

      btn.disabled = true;
      statusArea.style.display = "block";
      videoContainer.style.display = "none";

      try {
        const ja = document.getElementById("inputJa").value.trim();
        const res = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ script_romaji: romaji, script_japanese: ja, rate, pitch })
        });
        const data = await res.json();

        if (data.error) {
          alert("エラー: " + data.error);
          btn.disabled = false;
          statusArea.style.display = "none";
          return;
        }

        const jobId = data.job_id;
        pollStatus(jobId);
      } catch (err) {
        alert("送信失敗: " + err.message);
        btn.disabled = false;
        statusArea.style.display = "none";
      }
    }

    // 4. ポーリング（完成したら動画プレビュー表示）
    async function pollStatus(jobId) {
      const pollInterval = setInterval(async () => {
        try {
          const res = await fetch("/api/status?id=" + jobId);
          if (!res.ok) return;
          const data = await res.json();

          if (data.status === "completed") {
            clearInterval(pollInterval);
            document.getElementById("statusArea").style.display = "none";
            document.getElementById("generateBtn").disabled = false;

            const videoContainer = document.getElementById("videoContainer");
            const video = document.getElementById("resultVideo");
            const dlVideo = document.getElementById("downloadVideoLink");
            const dlAudio = document.getElementById("downloadAudioLink");

            const videoUrl = data.video_url || ("/media/" + jobId + ".mp4");
            const audioUrl = data.audio_url || ("/media/" + jobId + ".wav");

            video.src = videoUrl;
            dlVideo.href = videoUrl;
            dlVideo.setAttribute("download", "gonorego_" + jobId + ".mp4");

            dlAudio.href = audioUrl;
            dlAudio.setAttribute("download", "gonorego_" + jobId + ".wav");

            videoContainer.style.display = "block";
            video.load();
            video.play().catch(e => console.log("Auto-play prevented"));
          } else if (data.status === "failed") {
            clearInterval(pollInterval);
            alert("生成に失敗しました。GitHub Actionsの実行ログをご確認ください。");
            document.getElementById("statusArea").style.display = "none";
            document.getElementById("generateBtn").disabled = false;
          }
        } catch (e) {}
      }, 4000);
    }
  </script>
</body>
</html>
`;
