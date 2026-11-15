# X 定期投稿システム

X (Twitter) への定期投稿を管理する **完全無料** のシステムです。

## 費用: $0

| 項目 | 費用 | 備考 |
|------|------|------|
| X投稿 (twikit) | **$0** | APIキー不要、通常のアカウントで投稿 |
| Render Web Service | **$0** | Free プラン |
| Render PostgreSQL | **$0** | Free プラン (256MB) |

> **注意**: X公式APIのFree tierは2026年2月に廃止されました。
> 本システムは [twikit](https://github.com/d60/twikit) を使い、
> APIキーなしでXの内部APIを通じて投稿します。

## 機能

- 投稿の予約・編集・キャンセル
- 予約時刻に自動投稿（30秒間隔チェック）
- 失敗時のリトライ
- 投稿履歴の閲覧
- ステータスフィルター（予約中 / 投稿済み / 失敗 / キャンセル）
- Web UI（ダークテーマ）+ REST API
- Renderワンクリックデプロイ

## Renderへのデプロイ (推奨)

### 1. リポジトリをFork/Clone

```bash
git clone https://github.com/your-username/X_toko.git
```

### 2. Renderにデプロイ

1. [Render Dashboard](https://dashboard.render.com/) にログイン
2. **New** → **Blueprint** を選択
3. このリポジトリを接続
4. `render.yaml` が自動検出されるので **Apply** をクリック
5. 環境変数を設定:
   - `X_USERNAME`: Xのユーザー名
   - `X_EMAIL`: Xに登録したメールアドレス
   - `X_PASSWORD`: Xのパスワード

### 3. スリープ防止 (任意)

Render Free プランは15分間アクセスがないとスリープします。
予約投稿を確実にするには、無料のcronサービスで定期的にアクセスします:

1. [cron-job.org](https://cron-job.org/) に登録（無料）
2. 新規ジョブを作成:
   - URL: `https://your-app.onrender.com/health`
   - スケジュール: 14分ごと

## ローカル開発

```bash
pip install -r requirements.txt
cp .env.example .env
# .env を編集
uvicorn src.main:app --reload
```

http://localhost:8000 にアクセス

## API

| Method | Path | 説明 |
|--------|------|------|
| GET | `/health` | ヘルスチェック |
| GET | `/api/posts` | 投稿一覧 |
| POST | `/api/posts` | 投稿作成 |
| PUT | `/api/posts/{id}` | 投稿編集 |
| DELETE | `/api/posts/{id}` | 投稿キャンセル/削除 |
| POST | `/api/posts/{id}/retry` | 失敗した投稿をリトライ |

## 注意事項

- twikit はXの内部APIを利用するため、X側の変更で動作しなくなる可能性があります
- 初回ログイン時にCAPTCHAが求められる場合があります。その場合はローカルでログインしてから再デプロイしてください
- Render Free PostgreSQL は256MBまで。通常の利用では十分です
