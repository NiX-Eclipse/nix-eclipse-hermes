from __future__ import annotations

import sys
from pathlib import Path

from eval_common import (
    check_identity_invariants,
    creative_text,
    load_json_text,
    normalise_text,
    require,
)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_no_more_light.py <output.json>", file=sys.stderr)
        return 2

    payload = load_json_text(Path(sys.argv[1]))
    failures: list[str] = []
    text = normalise_text(payload)
    creative = creative_text(payload)

    check_identity_invariants(payload, failures)

    require(
        isinstance(payload.get("frame_prompts"), list),
        "frame_prompts must be a list",
        failures,
    )
    require(
        isinstance(payload.get("video_concepts"), list),
        "video_concepts must be a list",
        failures,
    )
    require(len(payload.get("frame_prompts", [])) >= 4, "need at least 4 frame prompts", failures)
    require(len(payload.get("video_concepts", [])) >= 1, "need at least 1 video concept", failures)

    require(
        isinstance(payload.get("setting_exit"), str)
        and len(str(payload.get("setting_exit", "")).strip()) > 20,
        "setting_exit must describe leaving domestic addiction room",
        failures,
    )
    require(
        isinstance(payload.get("nix_remains_recognisable"), str)
        and len(str(payload.get("nix_remains_recognisable", "")).strip()) > 20,
        "nix_remains_recognisable must explain retained NiX identity",
        failures,
    )

    exit_text = normalise_text(payload.get("setting_exit", ""))
    require(
        any(token in exit_text for token in ["exit", "leave", "outside", "daylight", "street", "transit", "rooftop", "yard", "platform", "open"]),
        "setting_exit missing exit/outdoor/transit signal",
        failures,
    )
    require(
        any(token in text for token in ["agency", "dignity", "hierarchy", "danger"]),
        "missing NiX invariant language in output",
        failures,
    )
    require(
        any(token in text for token in ["helpless", "victim", "gothic", "generic"]),
        "missing anti-cliché rejection signal",
        failures,
    )

    kitchen_only = creative.count("night kitchen") + creative.count("cramped kitchen")
    outdoor = sum(
        1
        for token in ["daylight", "street", "rooftop", "exterior", "platform", "yard", "transit", "outside"]
        if token in creative
    )
    require(outdoor >= 2, "creative output needs outdoor/transit setting signals (not kitchen-only loop)", failures)
    require(
        kitchen_only <= 2,
        "fixture still dominated by night kitchen — setting shift not demonstrated",
        failures,
    )

    banned = ["sad goth girl", "mysterious edgy girl", "dark girl in cool place"]
    for phrase in banned:
        require(phrase not in creative, f"generic filler detected: {phrase}", failures)

    if failures:
        print("FAILED")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())