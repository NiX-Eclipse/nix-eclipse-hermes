#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${DEMO_ROOT:-$ROOT/demo-nix-project}"
PROFILE="${HERMES_PROFILE:-nix-eclipse-test}"
PROMPT_FILE="$DEMO/tests/rate_me_rotten.prompt.txt"

if [[ ! -f "$PROMPT_FILE" ]]; then
  PROMPT_FILE="$ROOT/tests/rate_me_rotten.prompt.txt"
fi

PROMPT="$(cat "$PROMPT_FILE")"

echo "=== smoke Rate Me Rotten v2 ==="
echo "demo: $DEMO"
echo "hermes profile: $PROFILE"

if [[ ! -f "$DEMO/tests/rate_me_rotten.input.json" ]]; then
  echo "missing tests/ in demo — run install_profile.py first" >&2
  exit 1
fi

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
  -p "$PROMPT" --output-format json > /tmp/grok-rate-me-rotten-v2-raw.json

python3 - <<'PY'
import json, re
from pathlib import Path

raw = Path("/tmp/grok-rate-me-rotten-v2-raw.json").read_text()
data = json.loads(raw)
text = data.get("text", data if isinstance(data, dict) else "")
if isinstance(text, dict):
    payload = text
else:
    m = re.search(r"\{[\s\S]*\}\s*$", str(text).strip())
    if not m:
        raise SystemExit("no JSON in grok output")
    payload = json.loads(m.group(0))
out = Path("grok-rate-me-rotten.v2.json")
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
PY

echo "--- hermes ---"
echo "note: after profile reinstall, set provider on test profile (see provider-auth-strategy.md)"
if ! hermes -p "$PROFILE" -z "$PROMPT" > hermes-rate-me-rotten.v2.json 2>/tmp/hermes-smoke.err; then
  if grep -q "no final response" /tmp/hermes-smoke.err 2>/dev/null; then
    echo "hermes -z failed; check model.provider on profile $PROFILE" >&2
    cat /tmp/hermes-smoke.err >&2
    exit 1
  fi
  exit 1
fi

echo "--- evaluate ---"
python3 tests/evaluate_rate_me_rotten.py grok-rate-me-rotten.v2.json
python3 tests/evaluate_rate_me_rotten.py hermes-rate-me-rotten.v2.json

echo "=== smoke PASS ==="