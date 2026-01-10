# Python Web App for Amplify Gen2

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。
TODOアプリのサンプル実装。

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Flet 1.0 Beta (CSR) |
| バックエンド | FastAPI |
| 型定義共有 | Pydantic |
| パッケージ管理 | uv workspace |
| 型チェック | ty (高速型チェッカー) |
| リンター/フォーマッター | ruff |

## プロジェクト構成

```
.
├── pyproject.toml      # ワークスペース定義・スクリプト
├── shared/             # 共有型定義（Pydanticスキーマ）
├── frontend/           # Flet CSRアプリ
├── backend/            # FastAPI サーバー
└── scripts/            # 起動・ビルドスクリプト
```

## セットアップ

```bash
# 依存関係インストール
uv sync --all-packages
```

## 開発コマンド

| コマンド | 説明 |
|---------|------|
| `uv run dev-frontend` | フロントエンド開発サーバー（Web） |
| `uv run dev-frontend-desktop` | フロントエンド開発サーバー（Desktop） |
| `uv run dev-backend` | バックエンド開発サーバー（port 8000） |
| `uv run build-frontend` | フロントエンドビルド（CSR静的ファイル） |
| `uv run lint` | コードリント |
| `uv run fix` | コード自動修正 |
| `uv run fmt` | コードフォーマット |
| `uv run typecheck` | 型チェック |
| `uv run check` | 全チェック（lint + typecheck） |

## 開発の始め方

```bash
# ターミナル1: バックエンド起動
uv run dev-backend

# ターミナル2: フロントエンド起動
uv run dev-frontend
```

- フロントエンド: http://localhost:8550
- バックエンド: http://localhost:8000
- バックエンドAPI docs: http://localhost:8000/docs

## 実装済み機能

- TODOの作成・表示・削除
- リアルタイムUI更新
- 型安全なAPI通信
- レスポンシブデザイン

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                        shared                            │
│                  (Pydanticスキーマ)                      │
│                   TodoCreate                             │
│                   TodoResponse                           │
└─────────────────────────────────────────────────────────┘
           ▲                              ▲
           │ import                       │ import
           │                              │
┌──────────┴──────────┐      HTTP    ┌────┴─────────────┐
│      frontend       │◄───────────►│     backend       │
│   Flet 1.0 Beta     │   (REST)    │     FastAPI       │
│      (CSR)          │             │   /todos API      │
└─────────────────────┘              └───────────────────┘
```

`shared`パッケージで型定義を共有し、フロントエンド・バックエンド間の型安全性を確保。
