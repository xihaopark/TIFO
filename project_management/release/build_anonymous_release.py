#!/usr/bin/env python3
"""Build and audit a source-only anonymous TIFO release archive."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "release_artifacts"
ARCHIVE = OUTPUT_DIR / "tifo_anonymous_source.zip"
INCLUDE = (
    Path("README.md"),
    Path("requirements.txt"),
    Path("run.py"),
    Path("data_provider"),
    Path("exp"),
    Path("layers"),
    Path("models"),
    Path("utils"),
)
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".pth", ".pt", ".npy", ".npz", ".pkl"}
FORBIDDEN = {
    "local home path": re.compile(r"/(?:home|mnt)/[^/\s]+/"),
    "local username or lab credential": re.compile(r"park|sakurailab", re.I),
    "password assignment": re.compile(r"password\s*[:=]", re.I),
    "secret/token assignment": re.compile(r"(?:api[_-]?key|secret|token)\s*[:=]", re.I),
}


def tracked_files(path: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", str(path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def selected_files() -> list[Path]:
    files: set[Path] = set()
    for item in INCLUDE:
        source = ROOT / item
        if source.is_file():
            files.add(source)
        else:
            files.update(tracked_files(item))
    selected = []
    for path in sorted(files):
        relative = path.relative_to(ROOT)
        if any(part == "__pycache__" for part in relative.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES or " copy" in path.name:
            continue
        selected.append(path)
    if not selected:
        raise RuntimeError("anonymous release selection is empty")
    return selected


def audit_text(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    findings = [name for name, pattern in FORBIDDEN.items() if pattern.search(text)]
    if findings:
        raise RuntimeError(f"anonymous-release audit failed for {path}: {findings}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tifo-anonymous-") as temp:
        stage = Path(temp) / "TIFO"
        for source in selected_files():
            target = stage / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        for path in stage.rglob("*"):
            if path.is_file():
                audit_text(path)

        help_check = subprocess.run(
            ["python", "run.py", "--help"],
            cwd=stage,
            capture_output=True,
            text=True,
        )
        if help_check.returncode != 0:
            raise RuntimeError(f"release smoke test failed:\n{help_check.stderr}")
        for cache in stage.rglob("__pycache__"):
            shutil.rmtree(cache)
        for path in stage.rglob("*"):
            if path.is_file():
                audit_text(path)

        if ARCHIVE.exists():
            ARCHIVE.unlink()
        with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(stage.parent))

    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    print(f"archive={ARCHIVE}")
    print(f"sha256={digest}")


if __name__ == "__main__":
    main()
