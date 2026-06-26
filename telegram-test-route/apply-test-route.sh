#!/usr/bin/env bash
set -euo pipefail

THREAD_ID="${1:-}"
PROJECT_ROOT="${2:-/home/user/nix/nix-eclipse-v010-project}"

if [[ -z "$THREAD_ID" || "$THREAD_ID" == "THREAD_ID_PENDING" ]]; then
  echo "Usage: $0 <test_topic_thread_id> [project_root]" >&2
  echo "Create topic 'NiX v010 Creative Smoke' in NiX PROJECT and pass its thread_id." >&2
  exit 1
fi

PROFILE_HOME="${HOME}/.hermes/profiles/nix-eclipse-v010"
CONFIG="${PROFILE_HOME}/config.yaml"
PREAMBLE="${PROJECT_ROOT}/telegram-v010-chat-preamble.txt"
BACKUP_DIR="${PROFILE_HOME}/.telegram-test-route-backups"
TS="$(date +%Y%m%d-%H%M%S)"

if [[ ! -f "$PREAMBLE" ]]; then
  echo "Missing preamble: $PREAMBLE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
cp -a "$CONFIG" "${BACKUP_DIR}/config.yaml.${TS}"

python3 - "$CONFIG" "$THREAD_ID" "$PREAMBLE" <<'PY'
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
thread_id = sys.argv[2]
preamble = Path(sys.argv[3]).read_text(encoding="utf-8").strip()
preamble_block = "\n".join("      " + line for line in preamble.splitlines())

text = config_path.read_text(encoding="utf-8")

block = f"""
telegram:
  reactions: false
  channel_prompts:
    '-1003880065902': |
{preamble_block}
  allowed_chats: '-1003880065902'
  group_allowed_chats: '-1003880065902'
  free_response_chats: ''
  free_response_topics:
    - '-1003880065902:{thread_id}'
  require_mention: true
  observe_unmentioned_group_messages: false
  mention_patterns:
    - "^\\\\s*(nix|nixie|niх|никс|nix,|nix:|никс,|никс:)\\\\b"
  allowed_users:
    - 457766287
    - 273232902

platforms:
  telegram:
    extra:
      rich_messages: true
      group_topics:
        - chat_id: '-1003880065902'
          topics:
            - name: NiX v010 Creative Smoke
              thread_id: '{thread_id}'
              skills: []
"""

if "telegram:" in text and "free_response_topics:" in text:
    raise SystemExit("config already has telegram routing — run rollback-test-route.sh first")

if not text.endswith("\n"):
    text += "\n"
text += block

config_path.write_text(text, encoding="utf-8")
print(f"Applied telegram test route: chat=-1003880065902 topic={thread_id}")
print(f"Channel prompt: conversation.md preamble ({len(preamble)} chars)")
PY

echo "Backup saved: ${BACKUP_DIR}/config.yaml.${TS}"
echo "Next: set TELEGRAM_BOT_TOKEN in ${PROFILE_HOME}/.env (dedicated test bot only)"
echo "Start gateway only after operator confirms: hermes -p nix-eclipse-v010 gateway run"