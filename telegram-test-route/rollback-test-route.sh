#!/usr/bin/env bash
set -euo pipefail

PROFILE_HOME="${HOME}/.hermes/profiles/nix-eclipse-v010"
CONFIG="${PROFILE_HOME}/config.yaml"
BACKUP_DIR="${PROFILE_HOME}/.telegram-test-route-backups"

latest="$(ls -1t "${BACKUP_DIR}"/config.yaml.* 2>/dev/null | head -1 || true)"
if [[ -z "$latest" ]]; then
  echo "No backup found in ${BACKUP_DIR}" >&2
  echo "Manual rollback: remove telegram: and platforms: telegram: blocks from ${CONFIG}" >&2
  exit 1
fi

cp -a "$latest" "$CONFIG"
echo "Restored ${CONFIG} from ${latest}"