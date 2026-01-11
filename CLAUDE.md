# CLAUDE.md

Claude Code instructions for this Flet + FastAPI web application.

## Project Overview

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。

### Technology Stack

- **Frontend**: Flet 1.0 Beta (CSR)
- **Backend**: FastAPI
- **Tools**: ruff, ty

## Architecture

```
frontend/
├── src/        → main.py, api_client.py, schemas.py
└── scripts/    → 開発スクリプト

backend/
├── src/        → main.py, schemas.py
└── scripts/    → 開発スクリプト
```

フロントエンドとバックエンドは完全に独立したプロジェクト。

## Development Commands

### Backend（`backend/`ディレクトリで実行）

```bash
uv sync           # 依存関係インストール
uv run dev        # 開発サーバー起動
uv run check      # lint + typecheck
uv run fix        # 自動修正 + フォーマット
```

### Frontend（`frontend/`ディレクトリで実行）

```bash
uv sync           # 依存関係インストール
uv run dev        # 開発サーバー起動（Web）
uv run build      # Webビルド（src/requirements.txt自動生成）
uv run fix        # 自動修正 + フォーマット
```

## Coding Guidelines

### 必須チェック

コミット前に各ディレクトリで品質チェックを実行:

```bash
# backend
cd backend && uv run check && uv run fix

# frontend
cd frontend && uv run fix
```
