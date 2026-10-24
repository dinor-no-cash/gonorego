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

【超重要・出力制約】
・最後の「〜ってこった。」で文章を絶対に終了してください。
・「〜ってこった。」の後に、解説、注釈、感想、補足説明、挨拶などは絶対に1文字も出力してはなりません！
・Markdownコードブロックや見出し（#）は含めず、セリフ本文のみを出力してください。
`;

const ROMAJI_CONVERT_PROMPT = `
あなたはmacOSの音声合成エンジン「say -v Whisper」用のローマ字変換エンジニアです。
入力された日本語テキストの【意味やセリフの流れを一切変えず】、Whisperが滑らかかつ日本語らしく発音できるローマ字表記に変換してください。

【最重要・英語誤読排除ルール（Whisperは英語音素エンジンです）】
英語単語とスペルが一致すると、英語の発音規則（サイレントEや長母音）で激しく誤読されます。必ず以下の音素表記に従ってください：
1. 「サイゼリヤ」「サイゼ」->「Sah ee zeh ree yah」「Sah ee zeh」
2. 「まで」->「mah deh」（英語madeのメード誤読を排除）
3. 「が」->「gah」（ジョージア州GAのジー・エー誤読を排除）
4. 「それ」「これ」「あれ」「俺」->「soh reh」「koh reh」「ah reh」「oh reh」
5. 「お前」「お前ら」->「oh mah eh」「oh mah eh rah」
6. 「酒」「ワイン」->「sah keh」「wah een」（sake/wineの英語誤読防止）
7. 「範囲」->「hah nee」（honey誤読防止）
8. 「人」->「hee toh」（hi誤読防止）
9. 「その」「そこ」->「soh noh」「soh koh」
10. 「そん」->「sohn」（son誤読防止）
11. 「でも」->「deh moh」（demo誤読防止）
12. 「とか」->「toh kah」（to誤読防止）
13. 「ボケ」「アホ」「馬鹿」->「boh keh」「ah hoh」「bah kah」
14. 「小一時間」->「koh ee chee jee kahn」
15. 「問い詰めたい」->「toh ee tsoo meh tie」
16. 「ない」「たい」->「nye」「tie」
17. 「〜るん」->「roon」（run誤読防止）
18. 助詞: 「は」->「wah」, 「で」->「deh」, 「の」->「noh」, 「と」->「toh」, 「だ」->「dah」
19. 促音（っ）: 「naht tah」や「eet teh」「koht tah」のように二重子音で息止めを表現。
20. 息継ぎとポーズのために、文末にはピリオド（.）、文中の区切りにはカンマ（,）を必ず入れてください。
21. 最後の「〜ってこった。」（〜deh moh nah gah meh teh nah sigh tteh koht tah.）まで変換し、余計な解説は一切含めないこと。

解説やMarkdown引用符は含めず、変換後のローマ字テキストのみを出力してください。
`;

// 台本から余計な解説文・末尾テキストを完全に切り落とすサニタイザー
function cleanScriptText(raw: string): string {
  if (!raw) return "";
  let s = raw.trim();

  // コードブロック除去
  s = s.replace(/^```[a-z]*\n?/i, "").replace(/\n?```$/, "");

  // 導入文除去
  s = s.replace(/^(?:了解(?:いた)?しました|以下(?:は|が)?(?:台本|セリフ).*?です[：:\n]*)/i, "").trim();

  // 最重要：終了アンカー「〜ってこった。」で以降をバッサリ切断
  const endMatch = s.match(/([\s\S]*?(?:ってこった|てこった)[。！？!?\s]*)/);
  if (endMatch && endMatch[1]) {
    s = endMatch[1].trim();
  } else {
    // アンカーがない場合の保険切断
    const cutoffMatch = s.match(/([\s\S]*?)(?:\n\s*(?:【(?:解説|注意|注釈|補足|ポイント)】|解説[:：]|注[:：]|Note:|###|\*\*\*|---))/i);
    if (cutoffMatch && cutoffMatch[1]) {
      s = cutoffMatch[1].trim();
    }
  }

  return s;
}

// Whisper向けローマ字の英語誤読を機械的に撲滅する置換テーブル
function sanitizePhoneticRomaji(text: string): string {
  if (!text) return "";
  let r = text.trim();

  // コードブロック除去
  r = r.replace(/^```[a-z]*\n?/i, "").replace(/\n?```$/, "");

  // 終了アンカー以降の切り落とし
  const endMatch = r.match(/([\s\S]*?(?:teh\s+koht\s+tah|tteh\s+kotta|teh\s+kohht|kotta)[.!?\s]*)/i);
  if (endMatch && endMatch[1]) {
    r = endMatch[1].trim();
  } else {
    const cutoffMatch = r.match(/([\s\S]*?)(?:\n\s*(?:Note:|Explanation:|###|\*\*\*|---))/i);
    if (cutoffMatch && cutoffMatch[1]) {
      r = cutoffMatch[1].trim();
    }
  }

  const wordMap: [RegExp, string][] = [
    // 固有名詞
    [/\bSaizeriya\b/gi, "Sah ee zeh ree yah"],
    [/\bSaize\b/gi, "Sah ee zeh"],
    [/\bYoshinoya\b/gi, "Yoh shee noh yah"],
    [/\bGonorego\b/gi, "Goh noh reh goh"],
    [/\bMacinTalk\b/gi, "Mah keen tohk"],
    [/\bWhisper\b/gi, "Whisper"],
    // 英語単語と完全一致して誤読される要注意単語
    [/\bmade\b/gi, "mah deh"],
    [/\bmake\b/gi, "mah keh"],
    [/\bsake\b/gi, "sah keh"],
    [/\bname\b/gi, "nah meh"],
    [/\btame\b/gi, "tah meh"],
    [/\bsame\b/gi, "sah meh"],
    [/\bkame\b/gi, "kah meh"],
    [/\byome\b/gi, "yoh meh"],
    [/\bhime\b/gi, "hee meh"],
    [/\bdate\b/gi, "dah teh"],
    [/\blate\b/gi, "rah teh"],
    [/\bgate\b/gi, "gah teh"],
    [/\bhate\b/gi, "hah teh"],
    [/\bmate\b/gi, "mah teh"],
    [/\bkite\b/gi, "kee teh"],
    [/\bbite\b/gi, "bee teh"],
    [/\bsite\b/gi, "shee teh"],
    [/\bline\b/gi, "ree neh"],
    [/\bfine\b/gi, "foo ee neh"],
    [/\bmine\b/gi, "mee neh"],
    [/\bnine\b/gi, "nee neh"],
    [/\bpine\b/gi, "pah ee neh"],
    [/\bhome\b/gi, "hoh meh"],
    [/\bcome\b/gi, "koh meh"],
    [/\bsome\b/gi, "soh meh"],
    [/\btome\b/gi, "toh meh"],
    [/\brose\b/gi, "roh seh"],
    [/\bnose\b/gi, "noh seh"],
    [/\bhose\b/gi, "hoh seh"],
    [/\bdose\b/gi, "doh seh"],
    [/\bcure\b/gi, "koo reh"],
    [/\bpure\b/gi, "poo reh"],
    [/\bsure\b/gi, "soo reh"],
    [/\brude\b/gi, "roo deh"],
    [/\btube\b/gi, "tsoo beh"],
    [/\bfuse\b/gi, "foo seh"],
    [/\bmuse\b/gi, "moo seh"],
    [/\buse\b/gi, "oo seh"],
    [/\bgive\b/gi, "gee veh"],
    [/\blive\b/gi, "ree veh"],
    [/\bhave\b/gi, "hah veh"],
    [/\bone\b/gi, "oh neh"],
    [/\bdone\b/gi, "doh neh"],
    [/\bgone\b/gi, "goh neh"],
    [/\bnone\b/gi, "noh neh"],
    [/\bhere\b/gi, "heh reh"],
    [/\bwere\b/gi, "weh reh"],
    [/\bthere\b/gi, "teh reh"],
    [/\bwhere\b/gi, "weh reh"],
    [/\bmore\b/gi, "moh reh"],
    [/\bsore\b/gi, "soh reh"],
    [/\bkore\b/gi, "koh reh"],
    [/\bare\b/gi, "ah reh"],
    [/\bore\b/gi, "oh reh"],
    // 助詞および短い単音節
    [/\bha\b/gi, "wah"],
    [/\bwa\b/gi, "wah"],
    [/\bga\b/gi, "gah"],
    [/\bde\b/gi, "deh"],
    [/\bda\b/gi, "dah"],
    [/\bto\b/gi, "toh"],
    [/\bno\b/gi, "noh"],
    [/\bso\b/gi, "soh"],
    [/\bdo\b/gi, "doh"],
    [/\bgo\b/gi, "goh"],
    [/\bhe\b/gi, "eh"],
    [/\bme\b/gi, "meh"],
    [/\bhi\b/gi, "hee"],
    [/\bby\b/gi, "bah ee"],
    [/\bin\b/gi, "een"],
    [/\bon\b/gi, "ohn"],
    [/\bat\b/gi, "aht"],
    [/\bup\b/gi, "oo poo"],
    [/\bus\b/gi, "oo soo"],
    [/\bam\b/gi, "ahm"],
    [/\ban\b/gi, "ahn"],
    [/\bas\b/gi, "ahs"],
    [/\bit\b/gi, "eet"],
    [/\bis\b/gi, "ee soo"],
    // 定番単語
    [/\bboke\b/gi, "boh keh"],
    [/\baho\b/gi, "ah hoh"],
    [/\bbaka\b/gi, "bah kah"],
    [/\btokumori\b/gi, "toh koo moh ree"],
    [/\btsuyudaku\b/gi, "tsoo yoo dah koo"],
    [/\byo-shi\b/gi, "yoh shee"],
    [/\bpapa\b/gi, "pah pah"],
    [/\bkoichijikan\b/gi, "koh ee chee jee kahn"],
    [/\btoitsumetai\b/gi, "toh ee tsoo meh tie"],
    [/\bwain\b/gi, "wah een"],
    [/\bwine\b/gi, "wah een"],
    [/\bdecanter\b/gi, "deh kahn tah"],
    [/\bdekanta\b/gi, "deh kahn tah"],
    [/\bglass\b/gi, "goo rah soo"],
    [/\bgurasu\b/gi, "goo rah soo"],
  ];

  for (const [pattern, replacement] of wordMap) {
    r = r.replace(pattern, replacement);
  }

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

        const aiRes = await env.AI.run("@cf/qwen/qwen2.5-coder-32b-instruct", {
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

        const aiRes = await env.AI.run("@cf/qwen/qwen2.5-coder-32b-instruct", {
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

    // Default: Serve Full Retro UI HTML
    return new Response(UI_HTML, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
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
    // 1. テーマから台本自動執筆
    async function generateScriptFromTheme() {
      const theme = document.getElementById("inputTheme").value.trim();
      if (!theme) return alert("テーマを入力してください！（例: Docker環境、新NISA、PHP脆弱性など）");

      const inputJa = document.getElementById("inputJa");
      inputJa.value = "Workers AI が吉野家コピペ構文で台本を執筆中...";

      try {
        const res = await fetch("/api/generate-script", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ theme })
        });
        const data = await res.json();
        if (data.script) {
          inputJa.value = data.script;
        } else {
          inputJa.value = "生成失敗: " + (data.error || "不明なエラー");
        }
      } catch (err) {
        inputJa.value = "通信エラー: " + err.message;
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

    // 3. 動画生成リクエスト
    async function startGeneration() {
      let romaji = document.getElementById("previewRomaji").value.trim();
      if (!romaji) {
        const ja = document.getElementById("inputJa").value.trim();
        if (!ja) return alert("台本を入力するか、テーマから台本を生成してください！");
        await convertText();
        romaji = document.getElementById("previewRomaji").value.trim();
      }

      if (!romaji) return alert("ローマ字スクリプトの準備ができませんでした。");

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
