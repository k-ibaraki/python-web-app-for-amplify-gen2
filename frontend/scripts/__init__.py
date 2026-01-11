import subprocess
import sys
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"

# ビルド時に除外するパッケージ（Web非対応）
WEB_EXCLUDED_PACKAGES = {"flet-cli", "flet-desktop", "flet-web"}


def dev():
    """開発サーバー（Web）"""
    subprocess.run(["flet", "run", "--web", "main.py"], cwd=SRC_DIR)


def dev_desktop():
    """開発サーバー（Desktop）"""
    subprocess.run(["flet", "run", "main.py"], cwd=SRC_DIR)


def _generate_web_requirements() -> Path:
    """pyproject.tomlからWeb用requirements.txtをsrc/に生成"""
    pyproject_path = ROOT_DIR / "pyproject.toml"
    requirements_path = SRC_DIR / "requirements.txt"

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    deps = pyproject.get("project", {}).get("dependencies", [])

    # Web非対応パッケージを除外し、バージョン指定を削除
    web_deps = []
    for dep in deps:
        # パッケージ名を抽出（バージョン指定を除去）
        pkg_name = dep.split("[")[0].split(">")[0].split("<")[0].split("=")[0].strip()
        if pkg_name.lower() not in WEB_EXCLUDED_PACKAGES:
            web_deps.append(pkg_name)

    with open(requirements_path, "w") as f:
        for dep in web_deps:
            f.write(f"{dep}\n")

    return requirements_path


def build():
    """ビルド（CSR静的ファイル生成）"""
    output_dir = ROOT_DIR / "dist"

    # Web用requirements.txtをsrc/に生成
    req_path = _generate_web_requirements()
    print(f"Generated: {req_path}")

    # src/からビルド実行（pyproject.tomlがないのでrequirements.txtが使われる）
    result = subprocess.run(
        ["flet", "build", "web", ".", "--output", str(output_dir)],
        cwd=SRC_DIR,
    )

    if result.returncode == 0:
        print(f"ビルド完了: {output_dir}")
    else:
        print("ビルドに失敗しました")
        sys.exit(result.returncode)


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
