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
| `uv run build` | Webビルド（CSR静的ファイル生成） |
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

## Webビルド

```bash
cd frontend && uv run build
```

ビルド時に`pyproject.toml`から`src/requirements.txt`が自動生成され、`dist/`に静的ファイルが出力されます。

## デプロイ

### ローカル開発環境（Sandbox）

```bash
# 依存関係インストール
npm ci

# Amplify sandboxでバックエンドをデプロイ
npx ampx sandbox --once
```

`amplify_outputs.json`が生成され、フロントエンドビルド時にAPI URLが自動設定されます。

### 本番環境（CI/CD）

`main`ブランチへのpushで自動デプロイが実行されます。

**デプロイフロー:**
```
GitHub push → GitHub Actions (Backend) → Webhook → Amplify CD (Frontend)
```

| コンポーネント | 担当 | 処理内容 |
|--------------|------|---------|
| Backend | GitHub Actions | Docker build → ECR → Lambda + API Gateway |
| Frontend | Amplify CD | Webhookトリガー → Flet build → Amplify Hosting |

**初回セットアップ手順:**
1. Amplifyコンソールで GitHub連携してアプリを作成
2. 自動ビルドを無効化
3. Webhookを作成してGitHub Secretsに設定
4. OIDC認証用のIAMロールを作成
5. GitHub Secretsを設定（`AWS_IAM_ROLE_ARN`、`AMPLIFY_APP_ID`、`AMPLIFY_WEBHOOK_URL`）

詳細なセットアップ手順は [`DEPLOY.md`](./DEPLOY.md) を参照してください。
