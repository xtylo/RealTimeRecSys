"""Build the AWS Lambda deployment package.

Output:
    build/lambda/      unzipped package (mounted by docker-compose to run the Lambda locally)
    build/lambda.zip   zip file that Terraform uploads to AWS

Dependencies are installed for the Lambda runtime (Linux x86_64, Python 3.12),
so the build works the same from Windows, macOS or Linux.

Usage:
    uv run python src/scripts/build_lambda.py
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
BUILD = ROOT / "build"
PACKAGE_DIR = BUILD / "lambda"
ZIP_PATH = BUILD / "lambda.zip"
REQUIREMENTS = BUILD / "requirements-lambda.txt"

PYTHON_VERSION = "3.12"
PLATFORM = "x86_64-manylinux_2_28"  # the python3.12 Lambda runtime runs on Amazon Linux 2023
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def main() -> None:
    shutil.rmtree(PACKAGE_DIR, ignore_errors=True)
    ZIP_PATH.unlink(missing_ok=True)
    PACKAGE_DIR.mkdir(parents=True)

    # 1) Runtime dependencies only (no dev tools), pinned by uv.lock
    run([
        "uv", "export", "--quiet", "--frozen", "--no-dev", "--no-hashes", "--no-emit-project",
        "--format", "requirements-txt", "--output-file", str(REQUIREMENTS),
    ])
    run([
        "uv", "pip", "install", "--quiet",
        "--requirements", str(REQUIREMENTS),
        "--target", str(PACKAGE_DIR),
        "--python-platform", PLATFORM,
        "--python-version", PYTHON_VERSION,
        "--only-binary", ":all:",
    ])

    # 2) Application code + Lambda entry point at the package root
    shutil.copytree(SRC / "app", PACKAGE_DIR / "app", ignore=IGNORE)
    shutil.copy2(SRC / "lambda" / "handler.py", PACKAGE_DIR / "handler.py")

    # 3) Zip it
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(PACKAGE_DIR).as_posix())

    unzipped_mb = sum(p.stat().st_size for p in PACKAGE_DIR.rglob("*") if p.is_file()) / 1024**2
    zipped_mb = ZIP_PATH.stat().st_size / 1024**2
    print(f"\nPackage: {PACKAGE_DIR.relative_to(ROOT)} ({unzipped_mb:.1f} MB, Lambda limit 250 MB unzipped)")
    print(f"Zip:     {ZIP_PATH.relative_to(ROOT)} ({zipped_mb:.1f} MB)")


if __name__ == "__main__":
    main()
