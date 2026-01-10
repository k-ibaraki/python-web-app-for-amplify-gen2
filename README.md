# Python Web App for Amplify Gen2

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。

## プロジェクト構成

```
.
├── frontend/          # Flet CSRアプリ（独立プロジェクト）
│   ├── src/           # ソースコード
│   │   ├── main.py
│   │   ├── api_client.py
│   │   └── schemas.py
│   └── scripts/       # 開発スクリプト
└── backend/           # FastAPI サーバー（独立プロジェクト）
    ├── src/           # ソースコード
    │   ├── main.py
    │   └── schemas.py
    └── scripts/       # 開発スクリプト
```

フロントエンドとバックエンドは完全に独立したプロジェクトとして管理されています。

## セットアップ

### Backend

```bash
cd backend
uv sync
```

### Frontend

```bash
cd frontend
uv sync
```

## 開発コマンド

### Backend（`backend/`ディレクトリで実行）

| コマンド | 説明 |
|---------|------|
| `uv run dev` | 開発サーバー起動（port 8000） |
| `uv run lint` | リントチェック |
| `uv run fix` | 自動修正 + フォーマット |
| `uv run typecheck` | 型チェック |
| `uv run check` | lint + typecheck |

### Frontend（`frontend/`ディレクトリで実行）

| コマンド | 説明 |
|---------|------|
| `uv run dev` | 開発サーバー（Web） |
| `uv run dev-desktop` | 開発サーバー（Desktop） |
| `uv run build` | ビルド（CSR静的ファイル） |
| `uv run lint` | リントチェック |
| `uv run fix` | 自動修正 + フォーマット |

## 開発の始め方

```bash
# ターミナル1: バックエンド起動
cd backend && uv run dev

# ターミナル2: フロントエンド起動
cd frontend && uv run dev
```

- バックエンド: http://localhost:8000
- バックエンドAPI docs: http://localhost:8000/docs
