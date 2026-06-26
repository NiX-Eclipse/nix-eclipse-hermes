#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${DEMO_ROOT:-$ROOT/demo-nix-project}"
PROFILE="${HERMES_PROFILE:-nix-eclipse-test}"
REVIEW="${REVIEW_DIR:-$ROOT/artifacts/human-review}"

mkdir -p "$REVIEW"

run_grok() {
  local name="$1"
  local prompt_file="$2"
  local out="$3"
  local prompt
  prompt="$(cat "$prompt_file")"
  grok --no-auto-update --always-approve --cwd "$DEMO" \
    -p "$prompt" --output-format json > "/tmp/grok-${name}-raw.json"
  python3 - <<PY
import json, re
from pathlib import Path
raw = Path("/tmp/grok-${name}-raw.json").read_text()
data = json.loads(raw)
text = data.get("text", data if isinstance(data, dict) else "")
if isinstance(text, dict):
    payload = text
else:
    m = re.search(r"\{[\s\S]*\}\s*$", str(text).strip())
    if not m:
        raise SystemExit("no JSON in grok output for ${name}")
    payload = json.loads(m.group(0))
out = Path("${REVIEW}") / "${out}"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
PY
}

run_hermes() {
  local name="$1"
  local prompt_file="$2"
  local out="$3"
  local prompt
  prompt="$(cat "$prompt_file")"
  hermes -p "$PROFILE" -z "$prompt" > "$REVIEW/$out"
  echo "wrote $REVIEW/$out"
}

echo "=== smoke all fixtures ==="
echo "demo: $DEMO"
echo "review artifacts: $REVIEW"
cd "$DEMO"

run_grok rate_me_rotten tests/rate_me_rotten.prompt.txt grok-rate-me-rotten.v2.json
run_hermes rate_me_rotten tests/rate_me_rotten.prompt.txt hermes-rate-me-rotten.v2.json
python3 tests/evaluate_rate_me_rotten.py "$REVIEW/grok-rate-me-rotten.v2.json"
python3 tests/evaluate_rate_me_rotten.py "$REVIEW/hermes-rate-me-rotten.v2.json"

run_grok pylnaia_kletka tests/pylnaia_kletka.prompt.txt grok-pylnaia-kletka.rc.json
run_hermes pylnaia_kletka tests/pylnaia_kletka.prompt.txt hermes-pylnaia-kletka.rc.json
python3 tests/evaluate_pylnaia_kletka.py "$REVIEW/grok-pylnaia-kletka.rc.json"
python3 tests/evaluate_pylnaia_kletka.py "$REVIEW/hermes-pylnaia-kletka.rc.json"

run_grok setting_exit tests/setting_exit_smoke.prompt.txt grok-setting-exit-smoke.rc.json
run_hermes setting_exit tests/setting_exit_smoke.prompt.txt hermes-setting-exit-smoke.rc.json
python3 tests/evaluate_setting_exit_smoke.py "$REVIEW/grok-setting-exit-smoke.rc.json"
python3 tests/evaluate_setting_exit_smoke.py "$REVIEW/hermes-setting-exit-smoke.rc.json"

run_grok conversation_voice tests/conversation_voice.prompt.txt grok-conversation-voice.rc.json
run_hermes conversation_voice tests/conversation_voice.prompt.txt hermes-conversation-voice.rc.json
python3 tests/evaluate_conversation_voice.py "$REVIEW/grok-conversation-voice.rc.json"
python3 tests/evaluate_conversation_voice.py "$REVIEW/hermes-conversation-voice.rc.json"

echo "=== all fixtures PASS ==="