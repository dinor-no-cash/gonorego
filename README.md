# ★ インスタント・ゴノレゴ生成器 (Instant Gonorego) ★

2000年代初頭の伝説的なFlash黄金期を飾った元祖「ゴノレゴ（吉野家コピペ）」の怒涛の漫談動画を、ブラウザから任意のテーマを入力するだけで約35秒で完全自動生成するWebアプリケーション＆レンダリングパイプラインです。

---

## 🌟 主な特徴

1. **AI 吉野家コピペ台本自動執筆**:
   - 任意のテーマ（例: Docker環境、新NISA、PHP脆弱性など）を入力するだけで、AI（Workers AI）が吉野家コピペの黄金構成（「そんなことより聞いてくれよ１よ」「アホかとバカかと」「諸刃の剣」「〜ってこった」）に即したパロディ台本を自動生成。
2. **英語フォニックス誤読の完全撲滅 (Syllabic Phonics Engine)**:
   - macOSの実機合成音声エンジン（`say -v Whisper`）が日本語を英語フォニックス規則（サイレントEや二重母音 /eɪ/、長母音 /aɪ/ 等）で誤読する現象を音節レベルで完全に回避（例: `開発` ➔ `kah ee hah tsoo`、`大規模` ➔ `dah ee kee boh`、`にわか` ➔ `nee wah kah`）。
   - カタカナ外来語や技術用語（`Transformers`, `LLM`, `Local`, `Community` 等）はTitle Caseで英語スペルを完全維持。
3. **macOS実機 Whisper音声合成 ＆ Flash完全再現レンダリング**:
   - GitHub Actions（`macos-latest`）上で実機 Whisper 音声を合成。
   - 2コマFlash風動画（ワインを傾けながらぼやくゴノレゴ風ビジュアル）を同期レンダリング。
4. **ブラウザ完結・高速プレビュー ＆ 直接保存**:
   - 生成された MP4 動画および WAV 音声は Cloudflare KV を通じてブラウザ上で即座にインライン再生・単体ダウンロード可能（zip展開の手間ゼロ）。

---

## 🏗️ システムアーキテクチャ

* **フロントエンド ＆ API**: Cloudflare Workers (`cloudflare/`)
  * `/api/generate-script`: テーマから台本を自動生成 (Workers AI)
  * `/api/convert`: 日本語台本をWhisper用ローマ字に調声変換 (Workers AI)
  * `/api/generate`: GitHub Actions (`instant_gonorego.yml`) をディスパッチキック
  * `/api/status`: ジョブ進捗ポーリング
  * `/media/:job_id.(mp4|wav)`: 生成メディアの直接ストリーミング配信
* **レンダリングエンジン**: GitHub Actions (`.github/workflows/instant_gonorego.yml`)
  * `synthesize_and_align.py`: Whisper実機音声合成 ＆ 毫秒単位字幕アライメント
  * `render_gonorego_video.py`: 2コマFlashアニメーション動画レンダリング (ffmpeg)

---

## 📜 ライセンス

MIT License
