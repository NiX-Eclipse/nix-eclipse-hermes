from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_contracts import check_package

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt", ".gitignore"}


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {
        "SOUL.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "distribution.yaml",
        ".gitignore",
        "config.yaml",
    }


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def substitute_tokens(root: Path, mapping: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in mapping.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--profile-name", default="nix-eclipse")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--out", default="build/nix-eclipse-package")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_root = Path(args.out).resolve()
    project_root = Path(args.project_root).resolve()

    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    for folder in ("profile", "project", "scripts", "tests"):
        src = repo_root / folder
        if not src.exists():
            raise SystemExit(f"missing source directory: {src}")
        copy_tree(src, out_root / folder)

    substitute_tokens(
        out_root,
        {
            "__PROJECT_ROOT__": str(project_root),
            "__DIST_VERSION__": args.version,
            "__PROFILE_NAME__": args.profile_name,
        },
    )

    meta = {
        "profile_name": args.profile_name,
        "version": args.version,
        "project_root": str(project_root),
        "package_root": str(out_root),
    }
    (out_root / "build-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    errors = check_package(out_root)
    if errors:
        for err in errors:
            print(err)
        raise SystemExit(1)

    print(f"built package: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())