#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${DEMO_ROOT:-$ROOT/demo-nix-project}"
PROFILE="${HERMES_PROFILE:-nix-eclipse-v010}"
REVIEW="${REVIEW_DIR:-$ROOT/artifacts/human-review}"
mkdir -p "$REVIEW"
PROMPT_FILE="$DEMO/tests/conversation_voice.prompt.txt"

if [[ ! -f "$PROMPT_FILE" ]]; then
  PROMPT_FILE="$ROOT/tests/conversation_voice.prompt.txt"
fi

PROMPT="$(cat "$PROMPT_FILE")"

echo "=== smoke conversation_voice ==="
echo "demo: $DEMO"
echo "hermes profile: $PROFILE"
echo "review: $REVIEW"

if ! command -v grok >/dev/null 2>&1; then
  echo "grok not on PATH" >&2
  exit 1
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes not on PATH" >&2
  exit 1
fi

cd "$DEMO"

echo "--- grok ---"
grok --no-auto-update --always-approve --cwd "$DEMO" \
  -p "$PROMPT" --output-format json > /tmp/grok-conversation-voice-raw.json

python3 - <<PY
import json, re
from pathlib import Path

raw = Path("/tmp/grok-conversation-voice-raw.json").read_text()
data = json.loads(raw)
text = data.get("text", data if isinstance(data, dict) else "")
if isinstance(text, dict):
    payload = text
else:
    m = re.search(r"\{[\s\S]*\}\s*$", str(text).strip())
    if not m:
        raise SystemExit("no JSON in grok output")
    payload = json.loads(m.group(0))
out = Path("${REVIEW}") / "grok-conversation-voice.rc.json"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
PY

echo "--- hermes ---"
if ! hermes -p "$PROFILE" -z "$PROMPT" > "$REVIEW/hermes-conversation-voice.rc.json" 2>/tmp/hermes-conv-smoke.err; then
  cat /tmp/hermes-conv-smoke.err >&2
  exit 1
fi

python3 - <<PY
import json, re
from pathlib import Path

raw_path = Path("${REVIEW}") / "hermes-conversation-voice.rc.json"
raw = raw_path.read_text(encoding="utf-8").strip()
try:
    data = json.loads(raw)
    if isinstance(data, dict) and "text" in data and not data.get("response_a"):
        raw = data["text"]
except json.JSONDecodeError:
    pass
if not raw.startswith("{"):
    m = re.search(r"\{[\s\S]*\}\s*$", raw)
    if m:
        obj = json.loads(m.group(0))
        raw_path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("normalised hermes output to JSON")
PY

echo "--- evaluate ---"
python3 tests/evaluate_conversation_voice.py "$REVIEW/grok-conversation-voice.rc.json"
python3 tests/evaluate_conversation_voice.py "$REVIEW/hermes-conversation-voice.rc.json"

echo "=== conversation_voice smoke PASS ==="