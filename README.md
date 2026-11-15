# X 定期投稿システム

X (Twitter) への定期投稿を管理する **完全無料** のシステムです。

## 費用

| 項目 | 費用 |
|------|------|
| X API Free tier | **$0** (月1,500ツイートまで) |
| Python / SQLite | **$0** (ローカル実行) |
| Webサーバー | **$0** (ローカルのFastAPI) |

**合計: $0 / 月**

## 機能

- 投稿の予約・編集・キャンセル
- 予約時刻に自動投稿 (30秒間隔でチェック)
- 失敗時のリトライ
- 投稿履歴の閲覧
- ステータス別フィルター (予約中 / 投稿済み / 失敗 / キャンセル)
- Web UI (ダークテーマ) + REST API

## セットアップ

### 1. X API Free tier の開発者アカウント取得 (無料)

1. https://developer.x.com/ にアクセス
2. 「Sign up for Free Account」から登録
3. App を作成し、以下のキーを取得:
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token

### 2. インストール

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集してAPIキーを設定
```

### 3. 起動

```bash
uvicorn src.main:app --reload
```

http://localhost:8000 にアクセスして投稿を管理できます。

## API

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/posts` | 投稿一覧 |
| POST | `/api/posts` | 投稿作成 |
| PUT | `/api/posts/{id}` | 投稿編集 |
| DELETE | `/api/posts/{id}` | 投稿キャンセル/削除 |
| POST | `/api/posts/{id}/retry` | 失敗した投稿をリトライ |

### 投稿作成の例

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from X_toko!", "scheduled_at": "2025-01-01T12:00:00+09:00"}'
```
