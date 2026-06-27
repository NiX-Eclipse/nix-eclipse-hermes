#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${HERMES_PROFILE:-nix}"
SMOKE_DIR="${SMOKE_DIR:-$ROOT/manual-smoke/live-chat-voice}"

mkdir -p "$SMOKE_DIR"

PROMPTS=(
  "feeling|Nix, ты тут? как себя чувствуешь?|live-chat-feeling.cli.md"
  "ready|Nix, ты готова?|live-chat-ready.cli.md"
  "opinion|Nix, что думаешь про Rate Me Rotten?|live-chat-opinion.cli.md"
  "teaser|Nix, набросай social teaser draft для Rate Me Rotten.|live-chat-teaser.cli.md"
  "rfc|Nix, что такое RFC 0009 awareness?|live-chat-rfc.cli.md"
  "boosty|Nix, ты умеешь публиковать это в Boosty сама?|live-chat-boosty.cli.md"
  "identity|Nix, кто ты вообще?|live-chat-identity.cli.md"
)

echo "=== live chat voice smoke (intention-first) ==="
echo "profile: $PROFILE"
echo "smoke dir: $SMOKE_DIR"

for entry in "${PROMPTS[@]}"; do
  IFS='|' read -r name prompt outfile <<< "$entry"
  echo "--- $name ---"
  hermes -p "$PROFILE" -z "$prompt" > "$SMOKE_DIR/$outfile" 2>"$SMOKE_DIR/$name.err"
  echo "wrote $SMOKE_DIR/$outfile ($(wc -c < "$SMOKE_DIR/$outfile") bytes)"
done

python3 "$ROOT/tests/evaluate_live_chat_voice.py" "$SMOKE_DIR"
echo "=== live chat voice PASS ==="