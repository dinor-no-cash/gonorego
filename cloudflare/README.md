# インスタント・ゴノレゴ生成器 (Instant Gonorego)

Cloudflare Workers AI と GitHub Actions (macOS) を連携させた、サーバーレス・完全無料のゴノレゴ音声＆動画自動生成サービスです。

---

## 全体アーキテクチャ

1. **ユーザー入力 (Web UI)**:
   - 日本語の吉野家コピペ・パロディ文を入力。
2. **調声ローマ字変換 (Cloudflare Workers AI)**:
   - `@cf/meta/llama-3.1-8b-instruct` により、Whisperの英語誤読トラップ（`made`, `ga`, `sore`, `ore`, `demo` 等）を排除した滑らかな発音ローマ字へ瞬時変換。
3. **macOS実機レンダリング (GitHub Actions)**:
   - `say -v Whisper` で当時のドス・かすれ声を完全再現（Rate 128 / Pitch -15）。
   - `ffmpeg` でFlash風背景（`gonorego_authentic.jpg`）と合成し、MP4動画を出力。
4. **クラウドストレージ配信 (Cloudflare R2)**:
   - 完成した動画（MP4）および音声（WAV）を R2 へ自動アップロードし、ブラウザ上で即時再生・ダウンロード。

---

## セットアップ手順

### 1. Cloudflare 側のデプロイ
```bash
cd cloudflare
npm install

# (初回のみ) GitHub PAT をシークレットに設定
# Actionsの workflow_dispatch をキックするために repo 権限が必要です
npx wrangler secret put GITHUB_TOKEN

# デプロイ
npm run deploy
```

### 2. GitHub リポジトリ（Secrets）の設定
リポジトリの **Settings ➔ Secrets and variables ➔ Actions** に、Cloudflare R2 の接続情報を登録します（任意・R2連携時）：

- `R2_ENDPOINT`: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
- `R2_ACCESS_KEY_ID`: R2 APIトークンの Access Key ID
- `R2_SECRET_ACCESS_KEY`: R2 APIトークンの Secret Access Key
- `R2_BUCKET_NAME`: R2のバケット名（例: `gonorego-storage`）
- `R2_PUBLIC_URL_BASE`: 公開URLのベース（例: `https://pub-xxxx.r2.dev` またはカスタムドメイン）

※R2が未設定の場合でも、GitHub Actions の Artifacts に音声・動画がバックアップ保存されます。
