# Codex Quota Coach Lite

Codex Quota Coach Lite is a small self-hosted quota monitor for Codex usage limits. It reads local Codex session logs, stores the latest quota snapshot in a lightweight Hub, and exposes JSON for an Android home screen widget.

It focuses on three jobs:

1. Show `5h` and `Weekly` remaining quota.
2. Label the current usage pace.
3. Keep the Android widget updated without third-party automation apps.

It does not include task recommendations, account systems, or broad analytics dashboards.

## Architecture

```text
~/.codex/sessions/*.jsonl
  -> quota_coach collect
  -> quota_coach submit
  -> Quota Hub POST /snapshot
  -> Quota Hub GET /quota
  -> Android Widget
```

For public access, put Cloudflare Tunnel or another private tunnel in front of the Hub:

```text
Android Widget
  -> https://quota.example.com/quota
  -> Cloudflare Tunnel
  -> http://127.0.0.1:8765/quota
```

## Project Layout

```text
android/                 Native Android AppWidget project
quota_coach/             Python collector, model, Hub, and CLI
tests/                   Python unit tests
examples/                Example quota snapshot JSON
scripts/                 Local helper scripts
deploy/systemd-user/     systemd user service templates
docs/                    Android, Cloudflare, systemd, and research notes
```

## Quick Start

Collect a snapshot from local Codex logs:

```bash
python3 -m quota_coach collect
```

Run the Hub on LAN:

```bash
python3 -m quota_coach serve --host 0.0.0.0 --port 8765 --store ./data/latest-quota.json
```

Submit local quota data into the Hub:

```bash
python3 -m quota_coach submit --hub-url http://127.0.0.1:8765 --device laptop-home
```

Read the latest snapshot:

```text
http://localhost:8765/quota
```

## Token Protection

If the Hub is reachable outside your machine, set a token:

```bash
export QUOTA_HUB_TOKEN="$(openssl rand -hex 24)"
python3 -m quota_coach serve --host 127.0.0.1 --port 8765 --token "$QUOTA_HUB_TOKEN"
python3 -m quota_coach submit --hub-url http://127.0.0.1:8765 --token "$QUOTA_HUB_TOKEN"
```

With a token configured:

- `GET /quota` requires `Authorization: Bearer <token>`
- `GET /` requires `Authorization: Bearer <token>`
- `POST /snapshot` requires `Authorization: Bearer <token>`
- `GET /health` remains public

## Android Widget

The Android widget is the recommended phone client. It supports:

- Hub URL and optional Bearer token configuration
- one-hour background refresh through WorkManager
- manual refresh from the widget
- cached display when the Hub is temporarily unavailable

Build with Android Studio or Gradle:

```bash
cd android
./gradlew assembleDebug
```

More details: [docs/android-widget.md](docs/android-widget.md).

## Public Access

The recommended public setup is Cloudflare Tunnel:

```text
https://quota.example.com -> http://127.0.0.1:8765
```

See [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md).

## Background Services

For always-on usage, use the systemd user templates:

- `codex-quota-hub.service`
- `codex-quota-cloudflared.service`
- `codex-quota-submit.timer`

See [docs/systemd-user.md](docs/systemd-user.md).

## Output Shape

Example fields:

```json
{
  "headline": "额度闲置偏多",
  "sourceDevice": "laptop-home",
  "updatedAt": "2026-05-19T17:34:30+08:00",
  "primary": {
    "label": "5h",
    "remainingPercent": 80,
    "remainingText": "80%",
    "status": "slow",
    "statusText": "偏慢",
    "resetAtText": "22:15"
  },
  "weekly": {
    "label": "Weekly",
    "remainingPercent": 94,
    "remainingText": "94%",
    "status": "idle",
    "statusText": "闲置多",
    "resetAtText": "Mon 09:47"
  },
  "stale": false
}
```

## Status Labels

| Status | Meaning |
| --- | --- |
| `healthy` | On pace |
| `slow` | Slightly under-used |
| `idle` | Very under-used |
| `fast` | Spending faster than ideal |
| `low` | Low remaining quota |
| `empty` | Exhausted |
| `stale` | Data needs refresh |
| `unknown` | No usable data |

## Tests

```bash
python3 -B -m unittest discover -s tests
```

## License

MIT. See [LICENSE](LICENSE).
