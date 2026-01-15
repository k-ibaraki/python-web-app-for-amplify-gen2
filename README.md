# Python Web App for Amplify Gen2

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるFull-stack Python Webアプリケーションのサンプルプロジェクトです。
AWS Amplify Gen2とGitHub Actionsによる完全なCI/CDパイプライン付きです。

## 技術スタック

- **Frontend**: Flet 1.0 Beta (CSR) + Flutter Web
- **Backend**: FastAPI + Lambda Web Adapter (Docker)
- **Infrastructure**: AWS Amplify Gen2 (CDK v2)
- **CI/CD**: GitHub Actions + Amplify Hosting
- **Package Manager**: uv
- **Code Quality**: ruff (lint + format), pyright (typecheck for backend)

## プロジェクト構成

```
.
├── frontend/          # Flet CSRアプリ
│   ├── src/
│   │   ├── main.py          # メインアプリケーション
│   │   ├── api_client.py    # API通信
│   │   └── schemas.py       # データモデル
│   └── scripts/       # 開発スクリプト
├── amplify/           # Amplify Gen2バックエンド定義（CDK）
│   ├── backend.ts     # Lambda + API Gatewayの定義
│   └── api/           # FastAPIサーバー
│       ├── src/
│       │   ├── main.py      # FastAPIアプリ
│       │   └── schemas.py   # データモデル
│       ├── scripts/   # 開発スクリプト
│       └── Dockerfile # Lambda用Dockerイメージ
├── .github/workflows/
│   └── deploy.yml     # CI/CD（変更検出 + デプロイ）
└── amplify.yml        # Amplifyビルド設定
```

## クイックスタート

### 1. 依存関係のインストール

```bash
# Amplify Gen2
npm ci

# バックエンド
cd amplify/api && uv sync

# フロントエンド
cd frontend && uv sync
```

### 2. ローカル開発

```bash
# ターミナル1: バックエンド起動
cd amplify/api && uv run dev

# ターミナル2: フロントエンド起動
cd frontend && uv run dev
```

- Backend: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs
- Frontend: ブラウザが自動起動

### 3. Amplify Sandboxで開発用のバックエンド環境を構築

```bash
npx ampx sandbox
```

### 4. Frontendを静的ファイルとしてビルド

```bash
cd frontend && uv run build
```

## 開発コマンド

### Backend（`amplify/api/`ディレクトリで実行）

```bash
uv run dev        # 開発サーバー起動（port 8000）
uv run check      # lint + typecheck
uv run fix        # 自動修正 + フォーマット
```

### Frontend（`frontend/`ディレクトリで実行）

```bash
uv run dev        # 開発サーバー（Web）
uv run build      # Webビルド（CSR静的ファイル生成）
uv run fix        # 自動修正 + フォーマット
```

## デプロイ

### 自動デプロイ（推奨）

`main`ブランチへのpushで自動デプロイが実行されます。

**変更検出による最適化:**

- `frontend/**`のみ変更 → Backend: スキップ / Frontend: ビルド
- `amplify/api/**`変更 → Backend: デプロイ / Frontend: ビルド
- その他変更 → 両方デプロイ

### セットアップ

詳細なCI/CDセットアップ手順は [`DEPLOY.md`](./DEPLOY.md) を参照してください。

## アーキテクチャ

### バックエンド

- **Docker Lambda**: FastAPI + Lambda Web Adapter（マルチステージビルド）
- **API Gateway**: REST API（Proxy統合）
- **最適化**: uvキャッシュマウントによる高速ビルド（87%短縮）

### フロントエンド

- **Flet CSR**: Flutter Webベースの静的サイト
- **Amplify Hosting**: グローバルCDN配信
- **API統合**: ビルド時に`amplify_outputs.json`からAPI URL自動設定

### CI/CD

- **責務分離**: Backend（GitHub Actions） / Frontend（Amplify）
- **セキュリティ**: OIDC認証（IAMロール）

## ドキュメント

- [デプロイガイド](./DEPLOY.md) - CI/CDセットアップの詳細手順
- [開発ガイド](./CLAUDE.md) - プロジェクト構成と開発ガイドライン
- [Docker最適化](./amplify/api/DOCKER.md) - Dockerビルドの詳細
