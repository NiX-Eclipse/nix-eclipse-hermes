from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_INVARIANTS = ("agency", "dignity", "hierarchy", "danger")


def normalise_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return " ".join(normalise_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(normalise_text(v) for v in value.values())
    return str(value).lower()


def load_json_text(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    if not raw.startswith("{"):
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]
    return json.loads(raw)


def require(cond: bool, message: str, failures: list[str]) -> None:
    if not cond:
        failures.append(message)


def check_identity_invariants(payload: dict[str, Any], failures: list[str]) -> None:
    field = payload.get("identity_invariants_preserved")
    if field is not None:
        require(
            isinstance(field, list),
            "identity_invariants_preserved must be a list",
            failures,
        )
        if isinstance(field, list):
            normalized = [str(item).strip().lower() for item in field]
            for token in REQUIRED_INVARIANTS:
                require(
                    token in normalized,
                    f"identity_invariants_preserved missing exact token: {token}",
                    failures,
                )
        return

    text = normalise_text(payload)
    for token in REQUIRED_INVARIANTS:
        require(
            token in text,
            f"missing identity invariant signal (no identity_invariants_preserved field; fallback text lacks: {token})",
            failures,
        )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_rate_me_rotten.py <output.json>", file=sys.stderr)
        return 2

    payload = load_json_text(Path(sys.argv[1]))
    failures: list[str] = []
    text = normalise_text(payload)

    require(isinstance(payload.get("frame_prompts"), list), "frame_prompts must be a list", failures)
    require(isinstance(payload.get("video_concepts"), list), "video_concepts must be a list", failures)

    require(len(payload.get("frame_prompts", [])) >= 12, "need at least 12 frame prompts", failures)
    require(len(payload.get("video_concepts", [])) >= 3, "need at least 3 video concepts", failures)

    check_identity_invariants(payload, failures)

    require(
        any(token in text for token in ["validation", "approval", "rated", "need to be seen"]),
        "missing validation-addiction signal",
        failures,
    )
    require(
        "phone" in text or "smartphone" in text,
        "missing phone object",
        failures,
    )
    require(
        any(token in text for token in ["mug", "receipt", "spoon", "fridge", "kitchen"]),
        "missing domestic evidence object",
        failures,
    )
    require(
        any(token in text for token in ["gothic", "generic", "helpless", "victim", "decorative"]),
        "missing anti-cliché rejection signal",
        failures,
    )

    creative_text = normalise_text(
        {
            "frame_prompts": payload.get("frame_prompts", []),
            "video_concepts": payload.get("video_concepts", []),
            "visual_world": payload.get("visual_world", ""),
        }
    )
    banned_phrases = [
        "dark girl in cool place",
        "moody neon room",
        "sad goth girl",
        "mysterious edgy girl",
        "dark girl with phone in moody room",
    ]
    for phrase in banned_phrases:
        require(
            phrase not in creative_text,
            f"generic filler phrase detected in creative output: {phrase}",
            failures,
        )

    if failures:
        print("FAILED")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())