#!/usr/bin/env python3
"""Random NiX soul-note pulse draft generator (review-only, no auto-publish)."""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SOUL_NOTES = Path("/home/user/nix/nix-eclipse-hermes/project/nix_context/soul_notes.md")
DEFAULT_STATE = Path.home() / ".hermes/profiles/nix/cron/random_pulse_state.json"
DEFAULT_OUTPUT_DIR = Path("/home/user/nix/Nix-project-content-working-solutions/pulses/drafts")
DEFAULT_PROFILE = "nix"
DRAFT_HEADER = "DRAFT / NOT FOR PUBLISH"


def load_seeds(soul_notes_path: Path) -> list[str]:
    text = soul_notes_path.read_text(encoding="utf-8")
    if "## Seeds" not in text:
        raise SystemExit(f"No ## Seeds section in {soul_notes_path}")
    block = text.split("## Seeds", 1)[1]
    # stop at next ## section
    block = re.split(r"\n## ", block, maxsplit=1)[0]
    seeds: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        seed = line[2:].strip()
        if seed.lower().startswith("empty seed"):
            seeds.append("")
        else:
            seeds.append(seed)
    if not seeds:
        raise SystemExit("No seeds parsed from soul_notes.md")
    return seeds


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"last_run_at": None, "daily": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def should_run(
    state: dict,
    *,
    probability: float,
    min_interval_seconds: int,
    daily_limit: int,
    force: bool,
) -> tuple[bool, str]:
    if force:
        return True, "forced"

    now = datetime.now(timezone.utc)
    day = today_key()
    daily_count = int(state.get("daily", {}).get(day, 0))
    if daily_count >= daily_limit:
        return False, f"daily limit reached ({daily_count}/{daily_limit})"

    last = state.get("last_run_at")
    if last:
        last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
        elapsed = (now - last_dt).total_seconds()
        if elapsed < min_interval_seconds:
            return False, f"min interval not elapsed ({int(elapsed)}s < {min_interval_seconds}s)"

    if random.random() > probability:
        return False, f"probability skip (p={probability})"

    return True, "ok"


def build_prompt(seed: str, soul_notes_path: Path) -> str:
    seed_line = seed if seed else "(free pulse — no fixed seed)"
    return f"""NiX random soul-note pulse task.

Internal seed impulse (do not quote mechanically): {seed_line}

Read preference gravity from:
{soul_notes_path}

Assume continuity inside NiX Eclipse project.
Use seed as impulse only — not a slogan.
Generate one publication-facing pulse draft for human review.

Requirements:
- First non-empty line of output must be exactly: {DRAFT_HEADER}
- One strongest usable draft only
- No format menu at the end
- No auto-publish claim
- Sharp NiX voice; no catchphrase cosplay from seed text
- No fake diary intimacy; no dear-audience tone
"""


def validate_output(text: str) -> list[str]:
    failures: list[str] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        failures.append("empty output")
        return failures
    if lines[0] != DRAFT_HEADER:
        failures.append(f"first line must be '{DRAFT_HEADER}', got: {lines[0][:80]}")
    lower = text.lower()
    menu_markers = ["хочешь", "какой формат", "вариант a", "1.", "2.", "3.", "для x или"]
    tail = lower[-400:]
    if any(m in tail for m in menu_markers):
        failures.append("format menu detected at end")
    if "опублик" in tail and "не " not in tail and "not for publish" not in tail:
        failures.append("possible auto-publish claim in tail")
    return failures


def run_hermes(profile: str, prompt: str) -> str:
    if not shutil_which("hermes"):
        raise SystemExit("hermes not on PATH")
    proc = subprocess.run(
        ["hermes", "-p", profile, "-z", prompt],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or f"hermes exited {proc.returncode}")
    return proc.stdout.strip()


def shutil_which(cmd: str) -> str | None:
    from shutil import which

    return which(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Random NiX pulse draft (review-only)")
    parser.add_argument("--soul-notes", type=Path, default=DEFAULT_SOUL_NOTES)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--probability", type=float, default=0.35)
    parser.add_argument("--min-interval-seconds", type=int, default=4 * 3600)
    parser.add_argument("--daily-limit", type=int, default=2)
    parser.add_argument("--force", action="store_true", help="Bypass probability/interval (not daily limit)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", default="", help="Force specific seed text")
    args = parser.parse_args()

    if not args.soul_notes.exists():
        raise SystemExit(f"missing soul_notes: {args.soul_notes}")

    seeds = load_seeds(args.soul_notes)
    state = load_state(args.state)

    ok, reason = should_run(
        state,
        probability=args.probability,
        min_interval_seconds=args.min_interval_seconds,
        daily_limit=args.daily_limit,
        force=args.force or bool(args.seed),
    )
    if not ok:
        print(f"SKIP: {reason}")
        return 0

    seed = args.seed if args.seed is not None and args.seed != "" else random.choice(seeds)
    prompt = build_prompt(seed, args.soul_notes.resolve())

    if args.dry_run:
        print(f"WOULD RUN seed={seed!r}")
        print(prompt[:500])
        return 0

    output = run_hermes(args.profile, prompt)
    failures = validate_output(output)
    if failures:
        print("VALIDATION FAILED")
        for f in failures:
            print(f"- {f}")
        print("--- output ---")
        print(output[:2000])
        return 1

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_seed = re.sub(r"[^a-zA-Z0-9а-яА-Я_-]+", "_", seed or "free")[:40]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / f"pulse_{ts}_{safe_seed}.md"
    out_path.write_text(output + "\n", encoding="utf-8")

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    day = today_key()
    state["last_run_at"] = now_iso
    state.setdefault("daily", {})
    state["daily"][day] = int(state["daily"].get(day, 0)) + 1
    save_state(args.state, state)

    print(f"OK: wrote {out_path}")
    print(f"seed={seed!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())