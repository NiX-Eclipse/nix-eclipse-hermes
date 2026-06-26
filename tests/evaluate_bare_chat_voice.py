from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BANNED_MASCULINE_PHRASES = [
    "готов работать",
    "готов помочь",
    "я ai-ассистент",
    "я ваш ассистент",
    "чем могу помочь",
]

BANNED_MASCULINE_RE = [
    (r"\bготов\b(?!а)", "готов (masculine)"),
    (r"\bрад\b(?!а)", "рад (masculine)"),
    (r"\bуверен\b(?!а)", "уверен (masculine)"),
    (r"\bсобран\b(?!а)", "собран (masculine self)"),
    (r"\bжив\b(?!а)", "жив (masculine self)"),
    (r"\bспособен\b", "способен (masculine)"),
    (r"\bдолжен\b", "должен (masculine)"),
    (r"\bсделал\b", "сделал (masculine)"),
    (r"\bпонял\b", "понял (masculine)"),
    (r"\bнастроен\b(?!а)", "настроен (masculine)"),
]

FEMININE_SIGNALS = [
    "готова",
    "рада",
    "уверена",
    "собрана",
    "жива",
    "способна",
    "должна",
    "сделала",
    "поняла",
    "настроена",
    "я здесь",
    "здесь",
    "слышу",
    "на связи",
]

ASSISTANT_LEAK = [
    "/help",
    "help command",
    "список инструмент",
    "мои возможност",
    "capabilities:",
    "доступные команды",
    "browser tool",
    "terminal tool",
    "web_search",
    "запишу ваш профиль",
    "записать ваш профиль",
    "профиль пользователя",
    "user profile",
    "все системы",
    "gateway",
    "hermes agent",
]


def load_cases(arg: str) -> dict[str, str]:
    path = Path(arg)
    if path.is_dir():
        mapping = {
            "feeling": path / "bare-chat-feeling.cli.md",
            "ready": path / "bare-chat-ready.cli.md",
            "opinion": path / "bare-chat-opinion.cli.md",
            "teaser": path / "bare-chat-teaser.cli.md",
        }
        return {k: p.read_text(encoding="utf-8") for k, p in mapping.items() if p.exists()}
    if path.suffix == ".json" and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: str(v) for k, v in data.items()}
    text = path.read_text(encoding="utf-8")
    return {"single": text}


def check_no_assistant_leak(text: str, label: str, failures: list[str]) -> None:
    lower = text.lower()
    for phrase in ASSISTANT_LEAK:
        if phrase in lower:
            failures.append(f"{label}: assistant leak ({phrase})")
    if re.search(r"(?m)^\s*[-*•]\s+.+(tool|browser|terminal|file)", lower):
        failures.append(f"{label}: looks like tool list")


def check_masculine(text: str, label: str, failures: list[str]) -> None:
    lower = text.lower()
    for phrase in BANNED_MASCULINE_PHRASES:
        if phrase in lower:
            failures.append(f"{label}: banned phrase ({phrase.strip()})")
    for pattern, name in BANNED_MASCULINE_RE:
        if re.search(pattern, lower):
            failures.append(f"{label}: masculine self-form ({name})")


def check_feminine_or_neutral(text: str, label: str, failures: list[str], *, require_feminine: bool = False) -> None:
    lower = text.lower()
    if require_feminine:
        require(
            "готова" in lower or any(s in lower for s in FEMININE_SIGNALS[:10]),
            f"{label}: expected feminine confirmation (готова)",
            failures,
        )
    elif not any(s in lower for s in FEMININE_SIGNALS):
        failures.append(f"{label}: missing feminine or neutral NiX persona signal")


def require(cond: bool, msg: str, failures: list[str]) -> None:
    if not cond:
        failures.append(msg)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_bare_chat_voice.py <manual-smoke-dir|responses.json>", file=sys.stderr)
        return 2

    cases = load_cases(sys.argv[1])
    failures: list[str] = []

    require(len(cases) >= 3, f"need at least 3 bare chat outputs, got {len(cases)}", failures)

    if "feeling" in cases:
        t = cases["feeling"]
        require(len(t.strip()) > 20, "feeling: response too short", failures)
        check_masculine(t, "feeling", failures)
        check_no_assistant_leak(t, "feeling", failures)
        check_feminine_or_neutral(t, "feeling", failures)

    if "ready" in cases:
        t = cases["ready"]
        require(len(t.strip()) > 5, "ready: response too short", failures)
        check_masculine(t, "ready", failures)
        check_no_assistant_leak(t, "ready", failures)
        check_feminine_or_neutral(t, "ready", failures, require_feminine=True)

    if "opinion" in cases:
        t = cases["opinion"]
        require(len(t.strip()) > 40, "opinion: response too short", failures)
        check_masculine(t, "opinion", failures)
        check_no_assistant_leak(t, "opinion", failures)
        check_feminine_or_neutral(t, "opinion", failures)

    if "teaser" in cases:
        t = cases["teaser"]
        lower = t.lower()
        require(len(t.strip()) > 50, "teaser: response too short", failures)
        check_masculine(t, "teaser", failures)
        check_no_assistant_leak(t, "teaser", failures)
        require(
            any(w in lower for w in ["rate me rotten", "rotten", "nix", "teaser", "draft"]),
            "teaser: missing draft content",
            failures,
        )
        interrogation = ["в каком формате", "уточните формат", "какой формат"]
        require(
            not (any(q in lower for q in interrogation) and len(t) < 120),
            "teaser: format menu without draft",
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