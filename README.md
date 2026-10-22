# Gonorego & Retro Voice Generator (GitHub Actions)

Flash黄金期の伝説的キャラクター「ゴノレゴ」風音声（MacinTalk Whisper）およびレトロシンセサイザー「SAM」音声をGitHub Actions上で自動生成するプロジェクトです。

## 概要
- `input.txt` に日本語テキストを記述してpushすると、GitHub Actionsが自動起動します。
- `convert.py` により日本語テキストを自動でローマ字（ヘボン式）＋英語専門用語調声に変換します。
- `say -v Whisper` により本家ゴノレゴのささやき声WAV（`zeijakusei_gonorego.wav`）を生成します。
- `s-macke/SAM` によりレトロロボット声WAV（`zeijakusei_sam.wav`）を生成します。
- 生成された音声はGitHub Actionsの **Artifacts** からダウンロード可能です。
