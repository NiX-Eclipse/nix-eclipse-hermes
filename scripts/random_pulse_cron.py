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
MAX_PULSE_WORDS = 150

DIARY_MARKERS = [
    "keeping a diary",
    "for evidence",
    "closing transmission",
    "dear audience",
    "this is not an ending",
    "object list:",
    "preferred failure modes:",
    "дневник",
    "записываю",
    "окончание проекта",
    "closing transmission",
    "evidence.",
    "for attention.",
]

SECTION_LINE = re.compile(
    r"^\s*(?:i{1,3}|iv|v|vi{0,3}|[1-9])\.\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Major soul-note domains for kitchen-sink detection.
DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "weather": ("дожд", "гроз", "rain", "thunder", "шторм", "озон"),
    "metro": ("метро", "subway", "platform", "платформ", "вагон"),
    "tesla": ("tesla", "электрокар", "electric car"),
    "space": ("космос", "atmosphere", "орбит", "space"),
    "food": ("шаурм", "shawarma", "хачапур", "киндзмараули"),
    "flowers": ("ромашк", "daisies", "daisy"),
    "butterflies": ("бабочк", "butterfl", "moth", "пчел"),
    "music": ("трек на повтор", "track on repeat", "on permanent repeat"),
    "colors": ("бирюз", "сиренев", "teal", "lavender"),
    "transhuman": ("transhuman", "трансгуман"),
}


def load_seeds(soul_notes_path: Path) -> list[str]:
    text = soul_notes_path.read_text(encoding="utf-8")
    if "## Seeds" not in text:
        raise SystemExit(f"No ## Seeds section in {soul_notes_path}")
    block = text.split("## Seeds", 1)[1]
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


def seed_constraints(seed: str) -> str:
    if not seed:
        return """
EMPTY / FREE PULSE constraints (mandatory — read `## Seed-specific guidance` → `empty seed / free pulse`):
- Choose ONE impulse only: one object, one scene, or one pressure point.
- Default language: Russian.
- Target 40–120 words after the DRAFT header; one compact pulse only.
- Do NOT tour soul_notes; do NOT combine multiple preference domains.
- No diary framing, no evidence log, no transmission/closure, no roman/numbered sections.
- Sharp NiX; street-level or sensory; not literary monologue.
"""
    if "космос" in seed.lower():
        return """
SPACE SEED constraints (mandatory — read `## Seed-specific guidance` → `хочу в космос`):
- Pressure vector / scale / exit wound — not postcard rockets or cute fantasy.
- No clingy romance; no therapy-postcard soft closure.
- Do NOT end with a checklist of other likes (шаурма, ромашки, Tesla, metro, butterflies).
- One domain; at most one urban contrast. Compact pulse; do not quote seed as opening slogan.
"""
    return ""


def build_prompt(seed: str, soul_notes_path: Path) -> str:
    seed_line = seed if seed else "(free pulse — no fixed seed)"
    extra = seed_constraints(seed)
    return f"""NiX random soul-note pulse task.

Internal seed impulse (do not quote mechanically): {seed_line}

Read preference gravity from:
{soul_notes_path}

Assume continuity inside NiX Eclipse project.
Use seed as impulse only — not a slogan.
Generate one publication-facing pulse draft for human review.
{extra}
Requirements:
- First non-empty line of output must be exactly: {DRAFT_HEADER}
- One strongest usable draft only
- No format menu at the end
- No auto-publish claim
- Sharp NiX voice; no catchphrase cosplay from seed text
- No fake diary intimacy; no dear-audience tone
"""


def draft_body(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    if lines[0].strip() == DRAFT_HEADER:
        return "\n".join(lines[1:]).strip()
    return text.strip()


def matched_domains(text: str) -> set[str]:
    lower = text.lower()
    hits: set[str] = set()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            hits.add(domain)
    return hits


def validate_output(text: str, *, seed: str = "") -> list[str]:
    failures: list[str] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        failures.append("empty output")
        return failures
    if lines[0] != DRAFT_HEADER:
        failures.append(f"first line must be '{DRAFT_HEADER}', got: {lines[0][:80]}")

    body = draft_body(text)
    lower = body.lower()
    words = len(body.split())
    if words > MAX_PULSE_WORDS:
        failures.append(f"pulse too long ({words} words > {MAX_PULSE_WORDS})")

    for marker in DIARY_MARKERS:
        if marker in lower:
            failures.append(f"fake diary/transmission marker: {marker!r}")

    if SECTION_LINE.search(body):
        failures.append("multi-section structure detected (roman/numbered sections)")

    if re.search(r"[\u4e00-\u9fff]", body):
        failures.append("garbage CJK artifact detected")

    domains = matched_domains(body)
    if not seed:
        max_domains = 1
    elif "космос" in seed.lower():
        # Space pulse may use metro/Tesla as urban contrast; still no full preference tour.
        max_domains = 3
    else:
        max_domains = 2
    if len(domains) > max_domains:
        failures.append(
            f"kitchen-sink: {len(domains)} soul-note domains "
            f"({', '.join(sorted(domains))}); max {max_domains}"
        )

    if not seed and words < 15 and body:
        failures.append("free pulse too thin (< 15 words)")

    if seed and "космос" in seed.lower():
        # Checklist cosplay = unrelated likes stacked after cosmic pressure (food/flowers/etc.).
        unrelated = ("шаурм", "ромашк", "бабочк", "хачапур", "киндзмараули")
        unrelated_hits = [kw for kw in unrelated if kw in lower]
        if len(unrelated_hits) >= 2:
            failures.append(
                f"space seed checklist cosplay: {', '.join(unrelated_hits)}"
            )
        elif len(unrelated_hits) == 1 and "потом" in lower[-200:]:
            failures.append(
                f"space seed unrelated-like tail: {unrelated_hits[0]}"
            )

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
    parser.add_argument("--free", action="store_true", help="Force empty/free pulse seed")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", default="", help="Force specific seed text")
    args = parser.parse_args()

    if not args.soul_notes.exists():
        raise SystemExit(f"missing soul_notes: {args.soul_notes}")

    seeds = load_seeds(args.soul_notes)
    state = load_state(args.state)

    forced = args.force or args.free or bool(args.seed)
    ok, reason = should_run(
        state,
        probability=args.probability,
        min_interval_seconds=args.min_interval_seconds,
        daily_limit=args.daily_limit,
        force=forced,
    )
    if not ok:
        print(f"SKIP: {reason}")
        return 0

    if args.free:
        seed = ""
    elif args.seed:
        seed = args.seed
    else:
        seed = random.choice(seeds)

    prompt = build_prompt(seed, args.soul_notes.resolve())

    if args.dry_run:
        print(f"WOULD RUN seed={seed!r}")
        print(prompt[:800])
        return 0

    output = run_hermes(args.profile, prompt)
    failures = validate_output(output, seed=seed)
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