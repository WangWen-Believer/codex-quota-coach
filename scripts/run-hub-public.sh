#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -z "${QUOTA_HUB_TOKEN:-}" ]; then
  echo "QUOTA_HUB_TOKEN is required for public tunnel mode." >&2
  exit 1
fi

cd "$ROOT_DIR"
python3 -m quota_coach serve \
  --host 127.0.0.1 \
  --port "${QUOTA_HUB_PORT:-8765}" \
  --store ./data/latest-quota.json
