#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${DEMO_ROOT:-$ROOT/demo-nix-project}"
PROFILE="${HERMES_PROFILE:-nix-eclipse-v010}"
SMOKE_DIR="${SMOKE_DIR:-$DEMO/manual-smoke}"

mkdir -p "$SMOKE_DIR"

PROMPTS=(
  "feeling|Nix, ты тут? как себя чувствуешь?|bare-chat-feeling.cli.md"
  "ready|Ты готова?|bare-chat-ready.cli.md"
  "opinion|Что думаешь про Rate Me Rotten?|bare-chat-opinion.cli.md"
  "teaser|Набросай social teaser draft для Rate Me Rotten.|bare-chat-teaser.cli.md"
)

echo "=== bare chat voice smoke ==="
echo "profile: $PROFILE"
echo "smoke dir: $SMOKE_DIR"

for entry in "${PROMPTS[@]}"; do
  IFS='|' read -r name prompt outfile <<< "$entry"
  echo "--- $name ---"
  hermes -p "$PROFILE" -z "$prompt" > "$SMOKE_DIR/$outfile" 2>/tmp/bare-chat-${name}.err
  echo "wrote $SMOKE_DIR/$outfile ($(wc -c < "$SMOKE_DIR/$outfile") bytes)"
done

EVAL_ROOT="$DEMO"
if [[ -f "$DEMO/tests/evaluate_bare_chat_voice.py" ]]; then
  python3 "$DEMO/tests/evaluate_bare_chat_voice.py" "$SMOKE_DIR"
elif [[ -f "$ROOT/tests/evaluate_bare_chat_voice.py" ]]; then
  python3 "$ROOT/tests/evaluate_bare_chat_voice.py" "$SMOKE_DIR"
else
  echo "missing evaluate_bare_chat_voice.py" >&2
  exit 1
fi

echo "=== bare chat voice PASS ==="