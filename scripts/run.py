import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
FRONTEND_MAIN = ROOT_DIR / "frontend" / "src" / "frontend" / "main.py"


def dev_frontend():
    """フロントエンド開発サーバー（Web）"""
    subprocess.run(["flet", "run", "--web", str(FRONTEND_MAIN)])


def dev_frontend_desktop():
    """フロントエンド開発サーバー（Desktop）"""
    subprocess.run(["flet", "run", str(FRONTEND_MAIN)])


def dev_backend():
    """バックエンド開発サーバー"""
    subprocess.run(
        ["uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        cwd=ROOT_DIR,
    )


def build_frontend():
    """フロントエンドビルド（CSR静的ファイル生成）"""
    output_dir = ROOT_DIR / "frontend" / "dist"
    subprocess.run(
        ["flet", "build", "web", str(FRONTEND_MAIN), "--output", str(output_dir)]
    )
    print(f"ビルド完了: {output_dir}")
