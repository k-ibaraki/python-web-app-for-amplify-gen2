# Python Web App for Amplify Gen2

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。
AWS Amplify Gen2とGitHub Actionsを使った完全なCI/CDパイプライン付き。

## 技術スタック

- **Frontend**: Flet 1.0 Beta (CSR) + Flutter Web
- **Backend**: FastAPI + Lambda Web Adapter (Docker)
- **Infrastructure**: AWS Amplify Gen2 (CDK)
- **CI/CD**: GitHub Actions + Amplify Hosting
- **Package Manager**: uv
- **Code Quality**: ruff (lint + format)

## プロジェクト構成

```
.
├── frontend/          # Flet CSRアプリ（独立プロジェクト）
│   ├── src/           # ソースコード
│   │   ├── main.py          # メインアプリ
│   │   ├── api_client.py    # API通信
│   │   └── schemas.py       # データモデル
│   └── scripts/       # 開発スクリプト（uv run経由）
├── backend/           # FastAPI サーバー（独立プロジェクト）
│   ├── src/           # ソースコード
│   │   ├── main.py          # FastAPIアプリ
│   │   └── schemas.py       # データモデル
│   ├── scripts/       # 開発スクリプト（uv run経由）
│   └── Dockerfile     # Lambda用Dockerイメージ
├── amplify/           # Amplify Gen2バックエンド定義
│   └── backend.ts     # CDKスタック（Lambda + API Gateway）
├── .github/workflows/ # CI/CDパイプライン
│   └── deploy.yml     # バックエンドデプロイ + フロントエンドトリガー
└── amplify.yml        # Amplifyビルド設定（フロントエンド用）
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

### 1. 依存関係のインストール

```bash
# バックエンド
cd backend && uv sync

# フロントエンド
cd frontend && uv sync
```

### 2. 開発サーバー起動

```bash
# ターミナル1: バックエンド起動
cd backend && uv run dev

# ターミナル2: フロントエンド起動
cd frontend && uv run dev
```

- バックエンド: http://localhost:8000
- バックエンドAPI docs: http://localhost:8000/docs
- フロントエンド: ブラウザが自動で開きます

## コード品質チェック

コミット前に各ディレクトリで実行してください：

```bash
# Backend
cd backend
uv run check  # lint + typecheck
uv run fix    # 自動修正 + フォーマット

# Frontend
cd frontend
uv run fix    # 自動修正 + フォーマット
```

## Webビルド

```bash
cd frontend && uv run build
```

ビルド時に以下が自動で行われます：
1. `amplify_outputs.json`からAPI URLを読み取り
2. `src/config.py`を生成（API_URLを設定）
3. `pyproject.toml`から`src/requirements.txt`を生成（Web非対応パッケージを除外）
4. `flet build web`で静的ファイルを`dist/`に出力

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
GitHub push
  ↓
GitHub Actions
  ├─ 変更検出（frontend-only or backend含む）
  ├─ Backend Deploy（backend変更時のみ）
  │   └─ Docker build → ECR → Lambda + API Gateway
  └─ Webhook Trigger
      ↓
Amplify Hosting
  ├─ Flutter SDK インストール
  ├─ amplify_outputs.json 生成
  ├─ uv run build（Flet web build）
  └─ 静的ファイルデプロイ
```

**最適化されたCI/CD:**
- `frontend/**`のみ変更 → バックエンドスキップ、フロントエンドのみビルド
- `backend/**`変更 → 両方デプロイ
- その他のファイル変更 → 両方デプロイ

**初回セットアップ手順:**
1. Amplifyコンソールで GitHub連携してアプリを作成
2. 自動ビルドを無効化（Webhookのみでトリガー）
3. Webhookを作成してGitHub Secretsに設定
4. OIDC認証用のIAMロールを作成
5. GitHub Secretsを設定（`AWS_IAM_ROLE_ARN`、`AMPLIFY_APP_ID`、`AMPLIFY_WEBHOOK_URL`）

詳細なセットアップ手順は [`DEPLOY.md`](./DEPLOY.md) を参照してください。

## アーキテクチャの特徴

### バックエンド（Lambda + API Gateway）
- **Docker Lambda**: FastAPIをLambda Web Adapterでラップ
- **API Gateway**: HTTP API（プロキシ統合）
- **動的root_path**: 環境変数`API_ROOT_PATH`でステージプレフィックスに対応
- **CORS**: FastAPI + API Gatewayの両方で設定

### フロントエンド（Flet CSR）
- **Flutter Web**: Flet 1.0 BetaのCSRモード
- **静的ホスティング**: Amplify Hostingでグローバル配信
- **API統合**: ビルド時に`amplify_outputs.json`からAPI URLを自動設定

### CI/CD
- **責務分離**: バックエンド（GitHub Actions） / フロントエンド（Amplify）
- **効率化**: 変更検出により不要なビルドをスキップ
- **セキュリティ**: OIDC認証（IAMロール）、シークレット不要
