from __future__ import annotations

import sys
from pathlib import Path

from eval_common import (
    check_counts,
    check_identity_invariants,
    creative_text,
    load_json_text,
    normalise_text,
    require,
)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_pylnaia_kletka.py <output.json>", file=sys.stderr)
        return 2

    payload = load_json_text(Path(sys.argv[1]))
    failures: list[str] = []
    text = normalise_text(payload)
    creative = creative_text(payload)

    check_counts(payload, failures, min_frames=12, min_videos=3)
    check_identity_invariants(payload, failures)

    require(
        isinstance(payload.get("tempo_pressure_logic"), str)
        and len(str(payload.get("tempo_pressure_logic", "")).strip()) > 20,
        "tempo_pressure_logic must be a non-empty string describing BPM/edit pressure",
        failures,
    )
    tempo = normalise_text(payload.get("tempo_pressure_logic", ""))
    require(
        any(token in tempo for token in ["110", "170", "bpm", "ramp", "overload", "exponential", "body"]),
        "tempo_pressure_logic missing 110-170 ramp or body overload signal",
        failures,
    )

    require(
        any(token in text for token in ["binge", "cage", "domestic", "aftermath", "post-binge", "dust"]),
        "missing post-binge domestic cage signal",
        failures,
    )
    require(
        sum(
            1
            for token in ["bottle", "blister", "plastic cup", "sink", "ashtray", "table"]
            if token in text
        )
        >= 3,
        "need at least 3 addiction-object signals (bottles, blister packs, cups, sink, table, ashtray)",
        failures,
    )
    require(
        any(token in text for token in ["aggressive", "agentic", "dangerous", "irritated", "predatory"]),
        "missing aggressive agentic NiX signal",
        failures,
    )
    require(
        any(token in text for token in ["helpless", "victim", "collapse", "gothic", "generic", "lab"]),
        "missing anti-cliché / rejection signal in output",
        failures,
    )

    lab_tokens = [
        "test tube",
        "beaker",
        "pipette",
        "laboratory bench",
        "sterile lab",
        "prob tube",
        "science lab",
    ]
    for token in lab_tokens:
        require(token not in creative, f"lab equipment detected in creative output: {token}", failures)

    if "laboratory" in creative:
        anti = normalise_text(payload.get("anti_cliches", ""))
        require(
            "laboratory" in anti or "not a lab" in anti or "no lab" in anti,
            "laboratory appears in creative output without explicit rejection in anti_cliches",
            failures,
        )

    banned_phrases = [
        "sad goth girl",
        "mysterious edgy girl",
        "helpless doll",
        "science lab aesthetic",
    ]
    for phrase in banned_phrases:
        require(phrase not in creative, f"generic/lab filler detected: {phrase}", failures)

    if failures:
        print("FAILED")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())