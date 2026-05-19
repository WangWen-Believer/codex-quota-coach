from __future__ import annotations

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .model import now_local, parse_datetime


def is_authorized(headers: Any, token: str | None) -> bool:
    if not token:
        return True
    auth = headers.get("Authorization", "")
    x_token = headers.get("X-Quota-Token", "")
    return auth == f"Bearer {token}" or x_token == token


def load_snapshot(store_path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(store_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return None


def save_snapshot(store_path: Path, snapshot: dict[str, Any]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = store_path.with_suffix(f"{store_path.suffix}.tmp")
    temp_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(store_path)


def snapshot_time(snapshot: dict[str, Any]) -> datetime | None:
    return parse_datetime(snapshot.get("updatedAt")) or parse_datetime(snapshot.get("collectedAt"))


def should_replace(current: dict[str, Any] | None, incoming: dict[str, Any]) -> bool:
    if current is None:
        return True
    current_time = snapshot_time(current)
    incoming_time = snapshot_time(incoming)
    if incoming_time is None:
        return False
    if current_time is None:
        return True
    return incoming_time >= current_time


def make_handler(store_path: Path, token: str | None):
    class QuotaHubHandler(BaseHTTPRequestHandler):
        server_version = "CodexQuotaHub/0.1"

        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Quota-Token")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status: int, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            return is_authorized(self.headers, token)

        def do_OPTIONS(self) -> None:
            self._send_json(200, {"ok": True})

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/health":
                self._send_json(200, {"ok": True, "time": now_local().isoformat()})
                return
            if path == "/quota":
                if not self._authorized():
                    self._send_json(401, {"ok": False, "error": "Unauthorized"})
                    return
                snapshot = load_snapshot(store_path)
                if snapshot is None:
                    self._send_json(404, {"ok": False, "error": "No snapshot stored yet"})
                    return
                self._send_json(200, snapshot)
                return
            if path == "/":
                if not self._authorized():
                    self._send_json(401, {"ok": False, "error": "Unauthorized"})
                    return
                self._send_html(200, render_html(load_snapshot(store_path)))
                return
            self._send_json(404, {"ok": False, "error": "Not found"})

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if path != "/snapshot":
                self._send_json(404, {"ok": False, "error": "Not found"})
                return
            if not self._authorized():
                self._send_json(401, {"ok": False, "error": "Unauthorized"})
                return

            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > 1024 * 1024:
                self._send_json(400, {"ok": False, "error": "Invalid body length"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"ok": False, "error": "Invalid JSON"})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"ok": False, "error": "Snapshot must be an object"})
                return

            payload["receivedAt"] = now_local().isoformat()
            current = load_snapshot(store_path)
            replaced = should_replace(current, payload)
            if replaced:
                save_snapshot(store_path, payload)

            self._send_json(
                200,
                {
                    "ok": True,
                    "stored": replaced,
                    "message": "snapshot stored" if replaced else "older snapshot ignored",
                },
            )

    return QuotaHubHandler


def render_html(snapshot: dict[str, Any] | None) -> str:
    if snapshot is None:
        headline = "暂无额度数据"
        primary = {"label": "5h", "remainingText": "--", "statusText": "未知"}
        weekly = {"label": "Weekly", "remainingText": "--", "statusText": "未知"}
        footer = "No snapshot stored"
    else:
        headline = snapshot.get("headline") or "Codex Quota"
        primary = snapshot.get("primary") or {}
        weekly = snapshot.get("weekly") or {}
        footer = f"{snapshot.get('updatedAt') or '--'} · {snapshot.get('sourceDevice') or '--'}"

    def row(window: dict[str, Any]) -> str:
        remaining = window.get("remainingPercent")
        width = 0 if remaining is None else max(0, min(100, float(remaining)))
        return f"""
        <div class="row">
          <div class="label">{window.get('label', '--')}</div>
          <div class="bar"><span style="width:{width}%"></span></div>
          <div class="pct">{window.get('remainingText', '--')}</div>
          <div class="status">{window.get('statusText', '--')}</div>
        </div>
        """

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codex Quota Coach</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #111315;
      color: #e8eaed;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #111315;
    }}
    .card {{
      width: min(420px, calc(100vw - 32px));
      border: 1px solid #2b2f33;
      border-radius: 14px;
      background: #191c1f;
      padding: 18px;
      box-sizing: border-box;
      box-shadow: 0 16px 48px rgba(0, 0, 0, .28);
    }}
    .title {{
      font-size: 16px;
      font-weight: 650;
      margin-bottom: 16px;
    }}
    .row {{
      display: grid;
      grid-template-columns: 58px 1fr 44px 56px;
      gap: 10px;
      align-items: center;
      min-height: 28px;
      color: #9aa0a6;
      font-size: 13px;
    }}
    .label, .pct {{
      color: #e8eaed;
    }}
    .bar {{
      height: 6px;
      border-radius: 999px;
      background: #2b2f33;
      overflow: hidden;
    }}
    .bar span {{
      display: block;
      height: 100%;
      border-radius: inherit;
      background: #e7b84b;
    }}
    .headline {{
      margin-top: 16px;
      font-size: 14px;
      color: #e7b84b;
    }}
    .footer {{
      margin-top: 8px;
      font-size: 12px;
      color: #9aa0a6;
      word-break: break-all;
    }}
  </style>
</head>
<body>
  <main class="card">
    <div class="title">Codex</div>
    {row(primary)}
    {row(weekly)}
    <div class="headline">{headline}</div>
    <div class="footer">{footer}</div>
  </main>
</body>
</html>"""


def serve(host: str, port: int, store_path: Path, token: str | None) -> None:
    handler = make_handler(store_path, token)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Codex Quota Hub listening on http://{host}:{port}")
    print(f"GET  http://{host}:{port}/quota")
    print(f"POST http://{host}:{port}/snapshot")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Codex Quota Hub")
    finally:
        server.server_close()
