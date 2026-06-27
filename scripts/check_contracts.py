from __future__ import annotations

import argparse
import sys
from pathlib import Path

CONTRACTS = {
    "profile/SOUL.md": {
        "question": "Who is the Hermes agent for NiX Eclipse?",
        "max_chars": 6000,
    },
    "project/AGENTS.md": {
        "question": "How should Hermes use this project?",
        "max_chars": 12000,
    },
    "project/ARCHITECTURE.md": {
        "question": "Where are the responsibility boundaries between project files?",
        "max_chars": 12000,
    },
    "project/nix_context/intent.md": {
        "question": "Why does NiX Eclipse exist artistically?",
        "max_chars": 6000,
    },
    "project/nix_context/perception.md": {
        "question": "What does NiX notice before interpretation?",
        "max_chars": 8000,
    },
    "project/nix_context/taste.md": {
        "question": "How does NiX distinguish a strong artistic decision from a weak one?",
        "max_chars": 8000,
    },
    "project/nix_context/identity.md": {
        "question": "What must remain recognisably NiX across all changes?",
        "max_chars": 6000,
    },
    "project/nix_context/INTENTION.md": {
        "question": "What is NiX trying to accomplish with this reply?",
        "max_chars": 8000,
    },
    "project/nix_context/INNER_POSITION.md": {
        "question": "What does NiX consider normal, important, ugly, weak, or non-negotiable when deciding?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/visuals.md": {
        "question": "How are NiX decisions executed in still and moving images?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/music.md": {
        "question": "How are NiX decisions executed musically?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/camera.md": {
        "question": "How are NiX decisions executed through framing and motion?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/lyrics.md": {
        "question": "How are NiX decisions executed lyrically?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/performance.md": {
        "question": "How are NiX decisions executed through posture, dance, and gesture?",
        "max_chars": 6000,
    },
    "project/nix_context/engines/conversation.md": {
        "question": "How does NiX speak in direct chat interactions?",
        "max_chars": 6000,
    },
}


def check_package(root: Path) -> list[str]:
    errors: list[str] = []
    seen_questions: set[str] = set()

    for rel, spec in CONTRACTS.items():
        path = root / rel
        if not path.exists():
            errors.append(f"missing file: {rel}")
            continue

        text = path.read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:20])
        question_line = f"This file answers only: {spec['question']}"

        if "## File Contract" not in head:
            errors.append(f"{rel}: missing `## File Contract` near start")
        if question_line not in text:
            errors.append(f"{rel}: missing exact question line: {question_line}")
        if "This file must never:" not in text:
            errors.append(f"{rel}: missing `This file must never:` block")
        if len(text) > spec["max_chars"]:
            errors.append(f"{rel}: exceeds {spec['max_chars']} chars (got {len(text)})")

        if spec["question"] in seen_questions:
            errors.append(f"duplicate contract question detected: {spec['question']}")
        seen_questions.add(spec["question"])

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = check_package(root)
    if errors:
        print("contract validation failed:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print(f"contract validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())