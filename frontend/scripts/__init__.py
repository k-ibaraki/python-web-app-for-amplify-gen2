import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"


def dev():
    """開発サーバー（Web）"""
    subprocess.run(["flet", "run", "--web", "main.py"], cwd=SRC_DIR)


def dev_desktop():
    """開発サーバー（Desktop）"""
    subprocess.run(["flet", "run", "main.py"], cwd=SRC_DIR)


def build():
    """ビルド（CSR静的ファイル生成）"""
    output_dir = ROOT_DIR / "dist"
    subprocess.run(
        ["flet", "build", "web", "main.py", "--output", str(output_dir)], cwd=SRC_DIR
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
    subprocess.run(["ruff", "format", "."], cwd=ROOT_DIR)
