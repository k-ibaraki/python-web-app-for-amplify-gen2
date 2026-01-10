# CLAUDE.md

Claude Code instructions for this Flet + FastAPI web application.

## Project Overview

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。

### Technology Stack

- **Frontend**: Flet 1.0 Beta (CSR)
- **Backend**: FastAPI
- **Shared Types**: Pydantic schemas
- **Package Management**: uv workspace
- **Tools**: ruff, ty

## Architecture

```
shared/     → 共有型定義（Pydanticスキーマ）
frontend/   → Flet CSRアプリ
backend/    → FastAPI サーバー
scripts/    → 起動・ビルドスクリプト
```

フロントエンドとバックエンドは分離されており、`shared`パッケージで型定義を共有。

## Development Commands

```bash
uv sync --all-packages    # 依存関係インストール
uv run dev-backend        # バックエンド開発サーバー
uv run dev-frontend       # フロントエンド開発サーバー（Web）
uv run check              # lint + typecheck
uv run fix                # 自動修正 + フォーマット
```

## Coding Guidelines

### 必須チェック

コミット前に必ず品質チェックを実行:

```bash
uv run check     # lint + typecheck
uv run fix       # 自動修正 + フォーマット
```

### 重要な原則

- コードの品質を保つため、常に品質チェックツールを使用する
- インポートは必ずファイルの先頭に配置する
- 不要なコードは削除する（コメントアウトではなく完全に削除）
