FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Lambda Web Adapter
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

# Working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Copy source code
COPY src/ ./src/

# Lambda Web Adapter listens on port 8080 by default
ENV PORT=8080

# Start the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
