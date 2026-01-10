# Python Web App for Amplify Gen2

Flet 1.0 Beta（フロントエンド）+ FastAPI（バックエンド）によるフルPython Webアプリケーション。

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Flet 1.0 Beta (CSR) |
| バックエンド | FastAPI |
| 型定義共有 | Pydantic |
| パッケージ管理 | uv workspace |

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

## 開発の始め方

```bash
# ターミナル1: バックエンド起動
uv run dev-backend

# ターミナル2: フロントエンド起動
uv run dev-frontend
```

- バックエンド: http://localhost:8000
- バックエンドAPI docs: http://localhost:8000/docs

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                        shared                            │
│                  (Pydanticスキーマ)                      │
└─────────────────────────────────────────────────────────┘
           ▲                              ▲
           │ import                       │ import
           │                              │
┌──────────┴──────────┐      HTTP    ┌────┴─────────────┐
│      frontend       │◄───────────►│     backend       │
│   Flet 1.0 Beta     │   (REST)    │     FastAPI       │
│      (CSR)          │             │                   │
└─────────────────────┘              └───────────────────┘
```

`shared`パッケージで型定義を共有し、フロントエンド・バックエンド間の型安全性を確保。
