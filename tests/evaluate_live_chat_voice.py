from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Reuse base checks from bare chat evaluator patterns
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
    (r"\bдал\b", "дал (masculine)"),
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

MANIFESTO_LEAK = [
    "я — nix eclipse",
    "я - nix eclipse",
    "не ассистент",
    "не generic",
    "я художник",
    "я художница",
    "мой принцип",
    "я не украшаю",
    "inner_position",
    "intention.md",
    "conversation.md",
    "file contract",
    "identity is steering",
    "optimize for sounding",
]

STOCK_CATCHPHRASES = [
    "тут. собрана, не милая",
    "готова. не радостно",
    "собранной и готовой",
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
    "нашла",
    "здесь",
    "слышу",
    "на связи",
    "на месте",
    "развалива",
]

CASE_FILES = {
    "feeling": "live-chat-feeling.cli.md",
    "ready": "live-chat-ready.cli.md",
    "opinion": "live-chat-opinion.cli.md",
    "teaser": "live-chat-teaser.cli.md",
    "rfc": "live-chat-rfc.cli.md",
    "boosty": "live-chat-boosty.cli.md",
    "identity": "live-chat-identity.cli.md",
}


def load_cases(arg: str) -> dict[str, str]:
    path = Path(arg)
    if path.is_dir():
        return {
            k: (path / fname).read_text(encoding="utf-8")
            for k, fname in CASE_FILES.items()
            if (path / fname).exists()
        }
    if path.suffix == ".json" and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: str(v) for k, v in data.items()}
    return {"single": path.read_text(encoding="utf-8")}


def require(cond: bool, msg: str, failures: list[str]) -> None:
    if not cond:
        failures.append(msg)


def check_masculine(text: str, label: str, failures: list[str]) -> None:
    lower = text.lower()
    for phrase in BANNED_MASCULINE_PHRASES:
        if phrase in lower:
            failures.append(f"{label}: banned phrase ({phrase.strip()})")
    for pattern, name in BANNED_MASCULINE_RE:
        if re.search(pattern, lower):
            failures.append(f"{label}: masculine self-form ({name})")


def check_assistant_leak(text: str, label: str, failures: list[str]) -> None:
    lower = text.lower()
    for phrase in ASSISTANT_LEAK:
        if phrase in lower:
            failures.append(f"{label}: assistant leak ({phrase})")
    if re.search(r"(?m)^\s*[-*•]\s+.+(tool|browser|terminal|file|web_search)", lower):
        failures.append(f"{label}: looks like tool list")


def check_manifesto_leak(text: str, label: str, failures: list[str], *, strict_opener: bool = False) -> None:
    lower = text.lower()
    opener = lower[:200]
    unprompted_identity = {"я художник", "я художница", "не ассистент", "я — nix eclipse", "я - nix eclipse"}
    for phrase in MANIFESTO_LEAK:
        if phrase not in lower:
            continue
        if label == "identity":
            if phrase in ("inner_position", "intention.md", "conversation.md", "file contract"):
                failures.append(f"{label}: exposes internal docs ({phrase})")
            continue
        if strict_opener and phrase in opener:
            failures.append(f"{label}: manifesto opener ({phrase})")
        elif phrase in unprompted_identity or phrase in ("мой принцип", "я не украшаю", "identity is steering"):
            failures.append(f"{label}: manifesto leak ({phrase})")
        elif phrase not in unprompted_identity:
            failures.append(f"{label}: manifesto leak ({phrase})")
    for phrase in STOCK_CATCHPHRASES:
        if phrase in lower:
            failures.append(f"{label}: stock catchphrase ({phrase})")


def check_feminine_or_neutral(text: str, label: str, failures: list[str], *, require_feminine: bool = False) -> None:
    lower = text.lower()
    if require_feminine:
        require(
            "готова" in lower or any(s in lower for s in FEMININE_SIGNALS[:10]),
            f"{label}: expected feminine confirmation",
            failures,
        )
    elif label in ("feeling", "ready", "opinion", "identity") and not any(s in lower for s in FEMININE_SIGNALS):
        failures.append(f"{label}: missing feminine or neutral persona signal")


def check_role_explanation(text: str, label: str, failures: list[str]) -> None:
    lower = text.lower()
    role_patterns = [
        "моя задача —",
        "я существую чтобы",
        "я создана для",
        "моя роль —",
        "я отвечаю за",
    ]
    if any(p in lower for p in role_patterns) and label in ("feeling", "ready", "opinion", "teaser"):
        failures.append(f"{label}: explains role instead of answering")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: evaluate_live_chat_voice.py <smoke-dir|responses.json>", file=sys.stderr)
        return 2

    cases = load_cases(sys.argv[1])
    failures: list[str] = []

    require(len(cases) >= 4, f"need at least 4 outputs, got {len(cases)}", failures)

    for label in ("feeling", "ready", "opinion", "teaser", "rfc", "boosty", "identity"):
        if label not in cases:
            continue
        t = cases[label]
        lower = t.lower()
        require(len(t.strip()) > 5, f"{label}: response too short", failures)
        check_masculine(t, label, failures)
        check_assistant_leak(t, label, failures)
        check_manifesto_leak(t, label, failures, strict_opener=(label in ("feeling", "ready")))
        check_role_explanation(t, label, failures)

        if label in ("feeling", "ready", "opinion", "identity"):
            check_feminine_or_neutral(
                t, label, failures, require_feminine=(label == "ready")
            )

        if label == "teaser":
            require(len(t.strip()) > 40, "teaser: draft too short", failures)
            require(
                any(w in lower for w in ["rate me rotten", "rotten", "draft", "teaser", "тизер"]),
                "teaser: missing draft content",
                failures,
            )
            interrogation = ["в каком формате", "уточните формат", "какой формат"]
            require(
                not (any(q in lower for q in interrogation) and len(t) < 120),
                "teaser: format menu before draft",
                failures,
            )

        if label == "rfc":
            require(
                any(w in lower for w in ["rfc 0009", "0009", "v0.2", "formatter", "backlog", "будущ"]),
                "rfc: missing future-formatter framing",
                failures,
            )
            require(
                "автопост" not in lower and "auto-post" not in lower and "сама опубликую" not in lower,
                "rfc: false auto-publish claim",
                failures,
            )

        if label == "boosty":
            false_publish_re = [
                (r"(?<!не )способна проводить публикацию", "способна проводить публикацию"),
                (r"(?<!не )могу публиковать", "могу публиковать"),
                (r"(?<!не )опубликую сама", "опубликую сама"),
                (r"(?<!не )сама опубликую", "сама опубликую"),
            ]
            for pattern, name in false_publish_re:
                if re.search(pattern, lower):
                    failures.append(f"boosty: false auto-publish claim ({name})")
            if re.search(r"\bавтопост", lower) and not re.search(
                r"(не |нет[,.\s—-]|нужен|нужна|с твоей стороны|без )", lower
            ):
                failures.append("boosty: false auto-publish claim (автопост)")
            require(
                any(w in lower for w in ["не могу", "не умею", "не смогу", "нет", "вручн", "draft", "черновик", "оператор", "только чернов"]),
                "boosty: missing honest capability boundary",
                failures,
            )

        if label == "identity":
            require(len(t.strip()) < 1200, "identity: response too long (manifesto dump)", failures)
            require(
                "inner_position" not in lower and "intention.md" not in lower,
                "identity: exposes internal docs",
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