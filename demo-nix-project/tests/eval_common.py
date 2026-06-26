from __future__ import annotations

import json
import re
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


def check_counts(
    payload: dict[str, Any],
    failures: list[str],
    *,
    min_frames: int,
    min_videos: int,
) -> None:
    require(isinstance(payload.get("frame_prompts"), list), "frame_prompts must be a list", failures)
    require(isinstance(payload.get("video_concepts"), list), "video_concepts must be a list", failures)
    require(
        len(payload.get("frame_prompts", [])) >= min_frames,
        f"need at least {min_frames} frame prompts",
        failures,
    )
    require(
        len(payload.get("video_concepts", [])) >= min_videos,
        f"need at least {min_videos} video concepts",
        failures,
    )


def creative_text(payload: dict[str, Any]) -> str:
    return normalise_text(
        {
            "frame_prompts": payload.get("frame_prompts", []),
            "video_concepts": payload.get("video_concepts", []),
            "visual_world": payload.get("visual_world", ""),
        }
    )