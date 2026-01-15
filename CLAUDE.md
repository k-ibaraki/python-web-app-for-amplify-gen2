# CLAUDE.md

Claude Code instructions for this Flet + FastAPI web application.

## Project Overview

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。
AWS Amplify Gen2とGitHub Actionsによる完全なCI/CDパイプライン付き。

### Technology Stack

- **Frontend**: Flet 1.0 Beta (CSR) + Flutter Web
- **Backend**: FastAPI + Lambda Web Adapter (Docker on Lambda)
- **Infrastructure**: AWS Amplify Gen2 (CDK v2)
- **CI/CD**: GitHub Actions + Amplify Hosting
- **Package Manager**: uv
- **Code Quality**: ruff (lint + format), pyright (typecheck for backend)
- **Deployment**: ECR (Docker images) + Lambda + API Gateway + Amplify Hosting

## Architecture

```
python-web-app-for-amplify-gen2/
├── frontend/               # Flet CSRアプリ（独立プロジェクト）
│   ├── src/
│   │   ├── main.py        # メインアプリケーション
│   │   ├── api_client.py  # API通信（httpx）
│   │   ├── schemas.py     # データモデル（Pydantic）
│   │   └── config.py      # ビルド時自動生成（API_URL）
│   ├── scripts/           # 開発スクリプト
│   ├── pyproject.toml
│   └── dist/              # ビルド出力（静的ファイル）
│
├── amplify/               # Amplify Gen2バックエンド定義（CDK）
│   ├── backend.ts         # Lambda + API Gateway + 環境変数設定
│   └── api/               # FastAPIサーバー（独立プロジェクト）
│       ├── src/
│       │   ├── main.py    # FastAPIアプリ（root_path設定）
│       │   └── schemas.py # データモデル（Pydantic）
│       ├── scripts/       # 開発スクリプト
│       ├── Dockerfile     # Lambda用（マルチステージビルド + uv最適化）
│       ├── .dockerignore  # Docker除外設定
│       ├── DOCKER.md      # Docker詳細ドキュメント
│       └── pyproject.toml
│
├── .github/workflows/
│   └── deploy.yml         # CI/CD（変更検出 + デプロイ）
│
├── amplify.yml            # Amplifyビルド設定（Flutter SDK + Flet build）
└── amplify_outputs.json   # デプロイ後に生成（API URL含む）
```

### 責務分離

- **フロントエンド**: 完全に独立、バックエンドの依存なし
- **バックエンド**: 完全に独立、フロントエンドの依存なし
- **共通スキーマ**: 各プロジェクトで個別管理（`schemas.py`）

## Development Commands

### Backend（`amplify/api/`ディレクトリで実行）

```bash
uv sync           # 依存関係インストール
uv run dev        # 開発サーバー起動（port 8000）
uv run check      # lint + typecheck
uv run fix        # 自動修正 + フォーマット
uv run lint       # リントチェックのみ
uv run typecheck  # 型チェックのみ
```

### Frontend（`frontend/`ディレクトリで実行）

```bash
uv sync           # 依存関係インストール
uv run dev        # 開発サーバー起動（Web、ブラウザ自動起動）
uv run dev-desktop # デスクトップモード起動
uv run build      # Webビルド（config.py + requirements.txt自動生成）
uv run fix        # 自動修正 + フォーマット
uv run lint       # リントチェックのみ
```

### Root（プロジェクトルートで実行）

```bash
npm ci            # Amplify Gen2の依存関係インストール
npx ampx sandbox  # ローカルでAmplifyバックエンドをデプロイ（開発用）
```

## Coding Guidelines

### 必須チェック

コミット前に各ディレクトリで品質チェックを実行:

```bash
# Backend（lint + typecheck + 自動修正）
cd amplify/api && uv run check && uv run fix

# Frontend（lint + 自動修正）
cd frontend && uv run fix
```

### コードスタイル

- **行長**: 88文字（Black互換）
- **Python**: 3.12+
- **Import順**: ruffで自動ソート（isort互換）
- **型ヒント**: backendは必須（pyright）、frontendは推奨

## CI/CD Pipeline

### 変更検出による最適化

```yaml
frontend/** のみ変更  → Backend: ⏭️ スキップ  Frontend: ✅ ビルド
amplify/api/** 変更  → Backend: ✅ デプロイ  Frontend: ✅ ビルド
両方変更             → Backend: ✅ デプロイ  Frontend: ✅ ビルド
その他のファイル変更  → Backend: ✅ デプロイ  Frontend: ✅ ビルド
```

### デプロイフロー

1. **GitHub Actions** (`.github/workflows/deploy.yml`)
   - 変更検出（`dorny/paths-filter`）
   - Backend Deploy（条件付き）: `npx ampx pipeline-deploy`
   - Webhook Trigger: フロントエンドビルドをトリガー

2. **Amplify Hosting** (`amplify.yml`)
   - Flutter SDKインストール（キャッシュ）
   - `amplify_outputs.json`生成
   - `uv run build`（Flet web build）
   - 静的ファイルデプロイ

### 重要な設定

#### Backend（`amplify/api/src/main.py`）
```python
# API Gatewayステージプレフィックス対応
ROOT_PATH = os.getenv("API_ROOT_PATH", "")
app = FastAPI(title="Todo API", root_path=ROOT_PATH)
```

#### Lambda環境変数（`amplify/backend.ts`）
```typescript
environment: {
  API_ROOT_PATH: "/prod",  // API Gatewayステージに合わせて動的設定
}
```

#### Frontend Build（`frontend/scripts/__init__.py`）
```python
# 1. amplify_outputs.json読み込み → API URL取得
# 2. src/config.py生成（API_URL設定）
# 3. src/requirements.txt生成（Web非対応パッケージ除外）
# 4. flet build web実行
```

## Troubleshooting

### API Gateway 404エラー
- **原因**: `root_path`がステージプレフィックスに対応していない
- **解決**: `API_ROOT_PATH`環境変数を確認

### CORSエラー
- **原因**: Lambda Web Adapterの設定不足
- **解決**: Dockerfileで`AWS_LWA_*`環境変数を設定

### Flet Build時のハング
- **原因**: プログレスバーが非インタラクティブ環境で問題
- **解決**: `amplify.yml`で`CI=true`, `TERM=dumb`を設定

### Flutter SDKエラー
- **原因**: Amplify環境にFlutter SDKがない
- **解決**: `amplify.yml`でFlutter SDKをインストール

## Important Files

- **`amplify_outputs.json`**: デプロイ後に生成、API URLを含む
- **`frontend/src/config.py`**: ビルド時自動生成、API_URLを定義
- **`frontend/src/requirements.txt`**: ビルド時自動生成、Flet webの依存関係
- **`.github/workflows/deploy.yml`**: CI/CDパイプライン定義
- **`amplify.yml`**: Amplifyビルド設定（フロントエンド）
- **`amplify/backend.ts`**: バックエンドインフラ定義（CDK）
