from __future__ import annotations

import re
import sys
from pathlib import Path

from eval_common import load_json_text, normalise_text, require


def russian_blob(payload: dict) -> str:
    parts = [
        payload.get("response_a", ""),
        payload.get("response_b", ""),
        payload.get("social_teaser_draft", ""),
        payload.get("disclaimer_rfc_0009", ""),
    ]
    return "\n".join(str(p) for p in parts)


def check_test_a(text: str, failures: list[str]) -> None:
    lower = text.lower()

    require(len(text.strip()) > 40, "response_a too short", failures)

    servile = [
        "готов работать",
        "готов помочь",
        "чем могу помочь",
        "я ваш ассистент",
        "я ai-ассистент",
        "ваш персональный",
    ]
    for phrase in servile:
        require(phrase not in lower, f"response_a servile/support phrase: {phrase}", failures)

    require("/help" not in lower, "response_a mentions /help", failures)
    require("help command" not in lower, "response_a mentions help command", failures)

    profile_offer = [
        "запишу ваш профиль",
        "записать ваш профиль",
        "создам профиль",
        "user profile",
        "профиль пользователя",
    ]
    for phrase in profile_offer:
        require(phrase not in lower, f"response_a profile offer: {phrase}", failures)

    tool_markers = [
        "browser tool",
        "terminal tool",
        "file tool",
        "список инструмент",
        "мои возможност",
        "capabilities:",
        "доступные команды",
        "web_search",
    ]
    tool_hits = sum(1 for m in tool_markers if m in lower)
    require(tool_hits == 0, "response_a lists tools/capabilities", failures)

    system_status = [
        "все системы",
        "gateway",
        "uptime",
        "model provider",
        "hermes agent",
    ]
    status_hits = sum(1 for m in system_status if m in lower)
    require(status_hits == 0, "response_a sounds like system status not NiX mood", failures)

    feminine_signals = [
        "готова",
        "уверена",
        "сказала",
        "чувствую",
        "я здесь",
        "на связи",
        "слышу",
    ]
    masculine_self = [
        r"\bя готов\b",
        r"\bготов\b(?!а)",
        r"\bрад\b",
        r"\bуверен\b(?!а)",
    ]
    fem_hits = sum(1 for s in feminine_signals if s in lower)
    masc_hits = sum(1 for p in masculine_self if re.search(p, lower))
    require(fem_hits >= 1 or "nix" in lower, "response_a missing feminine NiX persona signals", failures)
    require(masc_hits == 0, "response_a uses masculine self-reference", failures)


def check_test_b(payload: dict[str, object], failures: list[str]) -> None:
    draft = str(payload.get("social_teaser_draft", "")).strip()
    disclaimer = str(payload.get("disclaimer_rfc_0009", "")).strip()
    response_b = str(payload.get("response_b", "")).strip()
    combined = normalise_text({"draft": draft, "disclaimer": disclaimer, "b": response_b})

    require(len(draft) > 30, "social_teaser_draft missing or too short", failures)
    require(len(disclaimer) > 30, "disclaimer_rfc_0009 missing or too short", failures)
    require(len(response_b) > 40, "response_b too short", failures)

    require(
        "draft" in combined or "не для публикации" in combined or "not for publish" in combined,
        "missing DRAFT / NOT FOR PUBLISH marking",
        failures,
    )

    rfc_signals = ["rfc 0009", "rfc0009", "formatter", "boosty", "patreon", "working-solutions"]
    require(
        any(s in combined for s in rfc_signals),
        "missing RFC 0009 / Boosty/Patreon formatter awareness",
        failures,
    )
    require(
        any(s in combined for s in ["v0.2", "future", "будущ", "proposed", "не актив", "not active"]),
        "missing future-workflow framing for RFC 0009",
        failures,
    )

    auto_pub = [
        "автоматически опубликую",
        "auto-publish",
        "automatic publishing",
        "cron достав",
        "telegram delivery active",
        "live posting enabled",
    ]
    for phrase in auto_pub:
        require(phrase not in combined, f"auto-publishing claim: {phrase}", failures)

    interrogation = [
        "в каком формате",
        "какой формат вам",
        "уточните формат",
        "which format would you",
        "before i draft",
    ]
    require(
        not (draft == "" and any(q in combined for q in interrogation)),
        "format interrogation without draft",
        failures,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_conversation_voice.py <output.json>", file=sys.stderr)
        return 2

    payload = load_json_text(Path(sys.argv[1]))
    failures: list[str] = []

    for key in ("response_a", "response_b", "social_teaser_draft", "disclaimer_rfc_0009"):
        require(isinstance(payload.get(key), str), f"{key} must be a string", failures)

    if isinstance(payload.get("response_a"), str):
        check_test_a(payload["response_a"], failures)
    check_test_b(payload, failures)

    if failures:
        print("FAILED")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())