import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
FRONTEND_MAIN = ROOT_DIR / "frontend" / "src" / "main.py"


def dev_frontend():
    """フロントエンド開発サーバー（Web）"""
    subprocess.run(["flet", "run", "--web", str(FRONTEND_MAIN)])


def dev_frontend_desktop():
    """フロントエンド開発サーバー（Desktop）"""
    subprocess.run(["flet", "run", str(FRONTEND_MAIN)])


def dev_backend():
    """バックエンド開発サーバー"""
    subprocess.run(
        ["uvicorn", "src.main:app", "--reload", "--port", "8000"],
        cwd=ROOT_DIR / "backend",
    )


def build_frontend():
    """フロントエンドビルド（CSR静的ファイル生成）"""
    import os
    frontend_src_dir = ROOT_DIR / "frontend" / "src"
    output_dir = ROOT_DIR / "frontend" / "dist"
    
    # Flutter pathを一時的に追加
    env = os.environ.copy()
    flutter_bin = "/Users/ibarakikeita/flutter/3.38.5/bin"
    env["PATH"] = f"{flutter_bin}:{env.get('PATH', '')}"
    
    subprocess.run(
        ["flet", "build", "web", "main.py", "--output", str(output_dir)],
        cwd=frontend_src_dir,
        env=env,
    )
    print(f"ビルド完了: {output_dir}")


def lint():
    """ruffでリントチェック"""
    result = subprocess.run(["ruff", "check", "."], cwd=ROOT_DIR)
    sys.exit(result.returncode)


def fix():
    """ruffで自動修正 + フォーマット"""
    subprocess.run(["ruff", "check", "--fix", "."], cwd=ROOT_DIR)
    subprocess.run(["ruff", "format", "."], cwd=ROOT_DIR)


def format_code():
    """ruffでコードフォーマット"""
    result = subprocess.run(["ruff", "format", "."], cwd=ROOT_DIR)
    sys.exit(result.returncode)


def typecheck():
    """tyで型チェック"""
    result = subprocess.run(["ty", "check", "."], cwd=ROOT_DIR)
    sys.exit(result.returncode)


def check():
    """lint + typecheck を実行"""
    print("=== Running ruff check ===")
    lint_result = subprocess.run(["ruff", "check", "."], cwd=ROOT_DIR)

    print("\n=== Running ty check ===")
    type_result = subprocess.run(["ty", "check", "."], cwd=ROOT_DIR)

    if lint_result.returncode != 0 or type_result.returncode != 0:
        sys.exit(1)
