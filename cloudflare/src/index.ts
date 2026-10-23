export interface Env {
  AI: any;
  JOBS?: KVNamespace;
  GITHUB_OWNER: string;
  GITHUB_REPO: string;
  WORKFLOW_FILE: string;
  GITHUB_TOKEN?: string;
  R2_PUBLIC_URL_BASE?: string;
}

// In-memory job store fallback if KV is not bound
const memoryJobs = new Map<string, { status: string; video_url?: string; audio_url?: string; updated_at: number }>();

const SYSTEM_PROMPT = `
あなたはmacOSの音声合成エンジン「say -v Whisper」用のローマ字変換エンジニアです。
入力された日本語テキストを、2000年代初頭のFlash「ゴノレゴ（吉野家コピペ）」の味・グルーヴ感を再現できるように、Whisper用のローマ字に変換してください。

【必須ルール】
1. 「まで」は英語のmade(メード)と誤読されないよう「ma deh」と書くこと。
2. 「が」はジョージア州GA(ジー・エー)と誤読されないよう「gah」と書くこと。
3. 「それ」「俺」「これ」は「soh reh」「oh reh」「koh reh」と書くこと。
4. 「範囲」は「hah nee」と書くこと（honey誤読防止）。
5. 「人」は「hee toh」と書くこと（hi誤読防止）。
6. 「その」「そこ」は「soh noh」「Soh koh」と書くこと。
7. 「小一時間」は「Koh ee chee jee kahn」と書くこと（こいちじかん）。
8. 「ない」「たい」は「nye」「tie」と書くこと。
9. 助詞: 「は」->「wah」, 「で」->「deh」, 「の」->「noh」, 「と」->「toh」, 「だ」->「dah」
10. 文節や単語のまとまりを維持し、全文字にスペースを入れないこと。

例：
入力: 昨日、Twitter見たんです。Twitter。
出力: Kee noh, Twitter mee tahn desu. Twitter.

入力: 小一時間問い詰めたい。ボケが。
出力: Koh ee chee jee kahn toh ee tsoo meh tie. Boh keh gah.

解説やMarkdownの引用符は一切含めず、純粋な変換後ローマ字のみを出力してください。
`;

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Enable CORS
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

    // API: Convert Japanese to Phonetic Romaji via Workers AI
    if (url.pathname === "/api/convert" && request.method === "POST") {
      try {
        const { text } = (await request.json()) as { text: string };
        if (!text) {
          return new Response(JSON.stringify({ error: "Text is required" }), { status: 400, headers: corsHeaders });
        }

        const aiResponse = await env.AI.run("@cf/qwen/qwen2.5-coder-32b-instruct", {
          messages: [
            { role: "system", content: SYSTEM_PROMPT.trim() },
            { role: "user", content: `Convert the following Japanese text into tuned Whisper romaji:\n${text}` },
          ],
        });

        const romaji = aiResponse.response.trim();
        return new Response(JSON.stringify({ romaji }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // API: Trigger GitHub Actions Render
    if (url.pathname === "/api/generate" && request.method === "POST") {
      try {
        const { script_romaji, rate = "128", pitch = "-15" } = (await request.json()) as {
          script_romaji: string;
          rate?: string;
          pitch?: string;
        };

        if (!script_romaji) {
          return new Response(JSON.stringify({ error: "Script is required" }), { status: 400, headers: corsHeaders });
        }

        const jobId = `gonorego-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
        const callbackUrl = `${url.origin}/api/callback`;

        // Save initial job state
        if (env.JOBS) {
          await env.JOBS.put(jobId, JSON.stringify({ status: "processing", updated_at: Date.now() }), { expirationTtl: 3600 });
        } else {
          memoryJobs.set(jobId, { status: "processing", updated_at: Date.now() });
        }

        // Trigger GitHub Actions workflow_dispatch
        const ghToken = env.GITHUB_TOKEN;
        if (!ghToken) {
          return new Response(JSON.stringify({ 
            error: "GITHUB_TOKEN not configured on Worker. Please set via 'wrangler secret put GITHUB_TOKEN'",
            job_id: jobId
          }), { status: 500, headers: corsHeaders });
        }

        const ghResponse = await fetch(
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
                rate: rate,
                pitch_baseline: pitch,
                callback_url: callbackUrl,
              },
            }),
          }
        );

        if (!ghResponse.ok) {
          const errText = await ghResponse.text();
          return new Response(JSON.stringify({ error: `GitHub API error: ${errText}` }), { status: 502, headers: corsHeaders });
        }

        return new Response(JSON.stringify({ job_id: jobId, status: "processing" }), { headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // API: Check Job Status
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

    // API: Callback from GitHub Actions
    if (url.pathname === "/api/callback" && request.method === "POST") {
      try {
        const data = (await request.json()) as { job_id: string; status: string; video_url?: string; audio_url?: string; run_url?: string };
        const jobData = {
          status: data.status === "success" ? "completed" : "failed",
          video_url: data.video_url || "",
          audio_url: data.audio_url || "",
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

    // Fallback: Serve UI HTML directly
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
  <title>インスタント・ゴノレゴ生成器 (Instant Gonorego)</title>
  <style>
    body {
      background-color: #2b2b2b;
      color: #eeeeee;
      font-family: "MS PGothic", "IPAMonaPGothic", "Mona", sans-serif;
      margin: 0;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .container {
      max-width: 800px;
      width: 100%;
      background: #1e1e1e;
      border: 3px solid #ff6600;
      padding: 20px;
      box-shadow: 0 0 20px rgba(255, 102, 0, 0.4);
    }
    h1 {
      color: #ff6600;
      font-size: 26px;
      margin-top: 0;
      text-align: center;
      border-bottom: 2px dashed #ff6600;
      padding-bottom: 10px;
    }
    .banner {
      background: #ff6600;
      color: #000;
      font-weight: bold;
      padding: 6px;
      text-align: center;
      margin-bottom: 15px;
    }
    label {
      display: block;
      margin-top: 15px;
      font-weight: bold;
      color: #ffcc00;
    }
    textarea {
      width: 100%;
      height: 120px;
      background: #111;
      color: #00ff66;
      border: 1px solid #555;
      padding: 10px;
      font-family: monospace;
      font-size: 14px;
      box-sizing: border-box;
      resize: vertical;
    }
    .preview-box {
      width: 100%;
      height: 90px;
      background: #0a0a0a;
      color: #00ccff;
      border: 1px dashed #444;
      padding: 10px;
      font-family: monospace;
      font-size: 13px;
      box-sizing: border-box;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    .controls {
      display: flex;
      gap: 15px;
      margin-top: 15px;
      align-items: center;
    }
    .btn {
      background: #ff6600;
      color: #fff;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 2px 2px 0 #993d00;
    }
    .btn:hover {
      background: #ff8533;
    }
    .btn:disabled {
      background: #666;
      cursor: not-allowed;
      box-shadow: none;
    }
    .status-area {
      margin-top: 20px;
      padding: 15px;
      background: #111;
      border: 1px solid #333;
      display: none;
      text-align: center;
    }
    .video-container {
      margin-top: 20px;
      display: none;
      text-align: center;
    }
    video {
      max-width: 100%;
      border: 2px solid #ff6600;
    }
    .marquee {
      color: #ff3300;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>★ インスタント・ゴノレゴ生成器 ★</h1>
    <div class="banner">【2001年FLASH黄金期】Cloudflare Workers AI ✕ macOS Whisper 実機合成</div>

    <label>1. 喋らせたい日本語テキストを入力（吉野家構文・パロディなど）:</label>
    <textarea id="inputJa" placeholder="昨日、Twitter見たんです。Twitter。そしたらなんか普段は脆弱性の話なんかしない連中まで..."></textarea>

    <div style="margin-top: 10px;">
      <button class="btn" style="background: #3366cc; padding: 6px 14px; font-size: 13px;" onclick="convertText()">AIで音素調声ローマ字に自動変換 (Workers AI)</button>
    </div>

    <label>2. 調声後ローマ字（Whisper誤読排除スクリプト・編集可能）:</label>
    <textarea id="previewRomaji" placeholder="AI変換ボタンを押すと自動入力されます（手動で微調整も可能です）"></textarea>

    <div class="controls">
      <div>
        <label style="display:inline;">話速:</label>
        <select id="rateSelect" style="background:#222; color:#fff; padding:5px;">
          <option value="128" selected>128 (吉野家ゴノレゴ完全再現・重厚)</option>
          <option value="138">138 (標準レート)</option>
          <option value="145">145 (明瞭まくしたて・速口)</option>
        </select>
      </div>
      <div>
        <label style="display:inline;">ピッチ:</label>
        <select id="pitchSelect" style="background:#222; color:#fff; padding:5px;">
          <option value="-15" selected>-15 (超重厚ドス)</option>
          <option value="-10">-10 (標準低音)</option>
        </select>
      </div>
    </div>

    <div style="margin-top: 25px; text-align: center;">
      <button id="generateBtn" class="btn" onclick="startGeneration()">怒涛のゴノレゴ動画を生成する！ (MP4)</button>
    </div>

    <div id="statusArea" class="status-area">
      <div id="statusText" class="marquee">ただいまゴノレゴが熱弁を準備中...</div>
      <div style="font-size: 12px; color: #888; margin-top: 8px;">macOS実機 Whisperエンジンでレンダリングしています（約30〜40秒）</div>
    </div>

    <div id="videoContainer" class="video-container">
      <h3 style="color:#00ff66;">＼ ゴノレゴ動画の生成が完了しました！ ／</h3>
      <video id="resultVideo" controls autoplay playsinline></video>
      <div style="margin-top: 10px;">
        <a id="downloadVideoLink" class="btn" style="text-decoration:none; display:inline-block;" download="gonorego.mp4">MP4動画を保存</a>
        <a id="downloadAudioLink" class="btn" style="background:#333; text-decoration:none; display:inline-block; margin-left:10px;" download="gonorego.wav">WAV音声を保存</a>
        <a id="fallbackArtifactLink" class="btn" style="text-decoration:none; display:none; background:#28a745;" target="_blank">📥 GitHub Actions成果物（動画・音声）をダウンロード</a>
      </div>
    </div>
  </div>

  <script>
    let currentRomaji = "";

    async function convertText() {
      const text = document.getElementById("inputJa").value.trim();
      if (!text) return alert("テキストを入力してください！");

      const preview = document.getElementById("previewRomaji");
      preview.value = "Workers AI が音素調声中...";

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

    async function startGeneration() {
      const romaji = document.getElementById("previewRomaji").value.trim();
      if (!romaji) {
        alert("調声後ローマ字が空です。「AIで音素調声ローマ字に自動変換」を押すか、直接ローマ字を入力してください。");
        return;
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
        const res = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ script_romaji: romaji, rate, pitch })
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

    async function pollStatus(jobId) {
      const statusText = document.getElementById("statusText");
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
            const fallbackLink = document.getElementById("fallbackArtifactLink");

            if (data.video_url && data.video_url.endsWith(".mp4")) {
              video.src = data.video_url;
              dlVideo.href = data.video_url;
              if (data.audio_url) dlAudio.href = data.audio_url;
              video.style.display = "block";
              fallbackLink.style.display = "none";
            } else {
              // Direct R2 URL not configured, link to GitHub Artifacts
              video.style.display = "none";
              fallbackLink.href = data.run_url || data.video_url;
              fallbackLink.style.display = "inline-block";
              dlVideo.style.display = "none";
              dlAudio.style.display = "none";
            }

            videoContainer.style.display = "block";
          } else if (data.status === "failed") {
            clearInterval(pollInterval);
            alert("生成に失敗しました。GitHub Actionsの実行ログをご確認ください。");
            document.getElementById("statusArea").style.display = "none";
            document.getElementById("generateBtn").disabled = false;
          }
        } catch (e) {}
      }, 5000);
    }
  </script>
</body>
</html>
`;
