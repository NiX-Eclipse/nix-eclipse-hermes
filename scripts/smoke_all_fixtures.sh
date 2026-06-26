#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${DEMO_ROOT:-$ROOT/demo-nix-project}"
PROFILE="${HERMES_PROFILE:-nix-eclipse-test}"

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
Path("${DEMO}/${out}").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote ${out}")
PY
}

run_hermes() {
  local name="$1"
  local prompt_file="$2"
  local out="$3"
  local prompt
  prompt="$(cat "$prompt_file")"
  hermes -p "$PROFILE" -z "$prompt" > "$DEMO/$out"
  echo "wrote $out"
}

echo "=== smoke all fixtures ==="
cd "$DEMO"

run_grok rate_me_rotten tests/rate_me_rotten.prompt.txt grok-rate-me-rotten.rc.json
run_hermes rate_me_rotten tests/rate_me_rotten.prompt.txt hermes-rate-me-rotten.rc.json
python3 tests/evaluate_rate_me_rotten.py grok-rate-me-rotten.rc.json
python3 tests/evaluate_rate_me_rotten.py hermes-rate-me-rotten.rc.json

run_grok pylnaia_kletka tests/pylnaia_kletka.prompt.txt grok-pylnaia-kletka.rc.json
run_hermes pylnaia_kletka tests/pylnaia_kletka.prompt.txt hermes-pylnaia-kletka.rc.json
python3 tests/evaluate_pylnaia_kletka.py grok-pylnaia-kletka.rc.json
python3 tests/evaluate_pylnaia_kletka.py hermes-pylnaia-kletka.rc.json

run_grok no_more_light tests/no_more_light.prompt.txt grok-no-more-light.rc.json
run_hermes no_more_light tests/no_more_light.prompt.txt hermes-no-more-light.rc.json
python3 tests/evaluate_no_more_light.py grok-no-more-light.rc.json
python3 tests/evaluate_no_more_light.py hermes-no-more-light.rc.json

echo "=== all fixtures PASS ==="