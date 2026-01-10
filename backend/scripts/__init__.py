import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def dev():
    """開発サーバー"""
    subprocess.run(
        ["uvicorn", "src.main:app", "--reload", "--port", "8000"],
        cwd=ROOT_DIR,
    )


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
    subprocess.run(["ruff", "format", "."], cwd=ROOT_DIR)


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
