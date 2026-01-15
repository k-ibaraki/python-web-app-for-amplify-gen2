# ============================================================================
# ビルドステージ: 依存関係のインストール
# ============================================================================
FROM python:3.12-slim-bookworm AS builder

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピー（キャッシュ効率化のため先にコピー）
COPY pyproject.toml uv.lock ./

# 依存関係を仮想環境にインストール
# --frozen: uv.lockを更新せずにインストール
# --no-install-project: プロジェクト本体は後でインストールするため、依存関係のみ
# --no-dev: 本番環境では開発用パッケージは不要
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ============================================================================
# 実行ステージ: 軽量な本番環境
# ============================================================================
FROM python:3.12-slim-bookworm

# Lambda Web Adapter（Lambda環境での実行に必要）
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

# 作業ディレクトリの設定
WORKDIR /app

# ビルドステージから仮想環境のみをコピー（uvは含まれない）
COPY --from=builder /app/.venv /app/.venv

# 仮想環境のPythonをパスに追加
ENV PATH="/app/.venv/bin:$PATH"

# アプリケーションコードのコピー
COPY src/ ./src/

# Lambda Web Adapter設定
ENV PORT=8080
ENV AWS_LWA_READINESS_CHECK_PATH=/health
ENV AWS_LWA_READINESS_CHECK_PORT=8080

# Python環境設定
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# サーバー起動（仮想環境のPythonを直接使用）
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
