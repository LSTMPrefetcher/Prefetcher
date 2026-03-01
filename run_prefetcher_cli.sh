#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "[!] Root privileges required. Re-launching with sudo..."
  exec sudo "$0" "$@"
fi

if [[ -x "$SCRIPT_DIR/AiFilePrefetcher" ]]; then
  exec "$SCRIPT_DIR/AiFilePrefetcher" "$@"
fi

if [[ -f "$SCRIPT_DIR/app_standalone.py" ]]; then
  exec python3 "$SCRIPT_DIR/app_standalone.py" "${@:-run}"
fi

echo "[!] Could not find Linux binary or app_standalone.py in $SCRIPT_DIR"
exit 1
