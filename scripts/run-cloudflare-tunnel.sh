#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLOUDFLARED="$ROOT_DIR/.tools/cloudflared/cloudflared"

if [ ! -x "$CLOUDFLARED" ]; then
  echo "cloudflared is missing. Expected: $CLOUDFLARED" >&2
  exit 1
fi

if [ -z "${CLOUDFLARED_TUNNEL_TOKEN:-}" ]; then
  echo "CLOUDFLARED_TUNNEL_TOKEN is required. Copy it from the Cloudflare Tunnel connector command." >&2
  exit 1
fi

export TUNNEL_TOKEN="$CLOUDFLARED_TUNNEL_TOKEN"
unset CLOUDFLARED_TUNNEL_TOKEN

exec "$CLOUDFLARED" tunnel --no-autoupdate run
