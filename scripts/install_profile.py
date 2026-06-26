from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_contracts import check_package

BLOCKERS = [".hermes.md", "HERMES.md"]
PROJECT_MANAGED = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "MODEL_ROUTING.md",
    "nix_context",
    "rfc",
    "tests",
]


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
):
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def parse_profile_home(show_output: str) -> Path:
    for line in show_output.splitlines():
        if line.strip().startswith("Path:"):
            return Path(line.split("Path:", 1)[1].strip()).expanduser()
    raise RuntimeError("Could not parse profile path from `hermes profile show` output.")


def copy_with_backup(src: Path, dst: Path, backup_root: Path) -> None:
    if dst.exists():
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_target = backup_root / dst.name
        if dst.is_dir():
            shutil.copytree(dst, backup_target, dirs_exist_ok=True)
            shutil.rmtree(dst)
        else:
            shutil.copy2(dst, backup_target)
            dst.unlink()

    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--profile-name", default="nix-eclipse")
    parser.add_argument("--alias", action="store_true")
    parser.add_argument("--force-context", action="store_true")
    parser.add_argument("--provider", default=os.getenv("NIX_HERMES_PROVIDER", ""))
    parser.add_argument("--model", default=os.getenv("NIX_HERMES_MODEL", ""))
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    project_root = Path(args.project_root).resolve()
    profile_src = package_root / "profile"
    project_src = package_root / "project"

    if not shutil.which("hermes"):
        raise SystemExit("`hermes` is not on PATH.")

    errors = check_package(package_root)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        raise SystemExit(1)

    blockers_found = [name for name in BLOCKERS if (project_root / name).exists()]
    if blockers_found and not args.force_context:
        raise SystemExit(
            "Higher-priority Hermes project context files exist at target root: "
            + ", ".join(blockers_found)
            + ". Remove them or pass --force-context if this is intentional."
        )

    ts = time.strftime("%Y%m%d-%H%M%S")
    backup_root = project_root / ".nix-hermes-backups" / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    try:
        run(["hermes", "profile", "show", args.profile_name], check=True)
        export_path = backup_root / f"{args.profile_name}.tar.gz"
        run(
            ["hermes", "profile", "export", args.profile_name, "-o", str(export_path)],
            check=True,
        )
    except subprocess.CalledProcessError:
        pass

    install_cmd = [
        "hermes",
        "profile",
        "install",
        str(profile_src),
        "--name",
        args.profile_name,
        "--force",
        "--yes",
    ]
    if args.alias:
        install_cmd.append("--alias")
    run(install_cmd, check=True)

    show = run(["hermes", "profile", "show", args.profile_name], check=True)
    info = run(["hermes", "profile", "info", args.profile_name], check=True)
    profile_home = parse_profile_home(show.stdout)

    hermes_env = os.environ.copy()
    hermes_env["HERMES_HOME"] = str(profile_home)

    run(
        ["hermes", "config", "set", "terminal.cwd", str(project_root)],
        env=hermes_env,
        check=True,
    )
    if args.provider:
        run(
            ["hermes", "config", "set", "model.provider", args.provider],
            env=hermes_env,
            check=True,
        )
    if args.model:
        run(
            ["hermes", "config", "set", "model.default", args.model],
            env=hermes_env,
            check=True,
        )

    for name in PROJECT_MANAGED:
        src = project_src / name
        dst = project_root / name
        if src.exists():
            copy_with_backup(src, dst, backup_root)

    tests_src = package_root / "tests"
    if tests_src.exists():
        copy_with_backup(tests_src, project_root / "tests", backup_root)

    (project_root / ".nix-hermes-install.json").write_text(
        json.dumps(
            {
                "profile_name": args.profile_name,
                "profile_home": str(profile_home),
                "project_root": str(project_root),
                "package_root": str(package_root),
                "backup_root": str(backup_root),
                "profile_info": info.stdout,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if shutil.which("grok"):
        inspect = run(["grok", "inspect"], cwd=project_root, check=False)
        (project_root / ".nix-hermes-grok-inspect.txt").write_text(
            inspect.stdout + "\n\nSTDERR:\n" + inspect.stderr,
            encoding="utf-8",
        )

    print(show.stdout.strip())
    print(f"Installed into project: {project_root}")
    print(f"Backup root: {backup_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())