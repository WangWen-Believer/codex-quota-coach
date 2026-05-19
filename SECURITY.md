# Security

Codex Quota Coach Lite reads local Codex session logs and exposes a small HTTP API. Treat the generated snapshot as private usage metadata.

## Public Exposure

When exposing Quota Hub outside your LAN:

- always set `QUOTA_HUB_TOKEN`
- prefer Cloudflare Tunnel, Tailscale, or another private tunnel over router port forwarding
- do not commit `~/.config/codex-quota-coach/env`
- verify that unauthenticated `GET /quota` returns `401 Unauthorized`

With a token configured:

- `GET /quota` requires `Authorization: Bearer <token>`
- `GET /` requires `Authorization: Bearer <token>`
- `POST /snapshot` requires `Authorization: Bearer <token>`
- `GET /health` remains public for connectivity checks

## Reporting

For now, open a private issue or contact the maintainer directly before publishing a vulnerability. Avoid including real tokens, session file paths, or quota snapshots in public reports.
