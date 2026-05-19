from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import error, request

from .collector import DEFAULT_SESSIONS_DIR, collect_snapshot
from .hub import serve


def write_json(snapshot: dict, output: str) -> None:
    text = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output == "-":
        print(text, end="")
        return
    output_path = Path(output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(output_path)


def post_snapshot(hub_url: str, snapshot: dict, token: str | None) -> dict:
    url = hub_url.rstrip("/") + "/snapshot"
    body = json.dumps(snapshot, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Hub returned HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Failed to reach hub: {exc.reason}") from exc


def add_common_collect_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--sessions-dir",
        default=str(DEFAULT_SESSIONS_DIR),
        help="Codex sessions directory. Defaults to ~/.codex/sessions.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Source device name shown in the widget. Defaults to hostname.",
    )
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=3,
        help="Mark data stale after this many hours. Defaults to 3.",
    )


def cmd_collect(args: argparse.Namespace) -> int:
    snapshot = collect_snapshot(
        Path(args.sessions_dir).expanduser(),
        source_device=args.device,
        stale_after_hours=args.stale_hours,
    )
    write_json(snapshot, args.output)
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    snapshot = collect_snapshot(
        Path(args.sessions_dir).expanduser(),
        source_device=args.device,
        stale_after_hours=args.stale_hours,
    )
    if args.output:
        write_json(snapshot, args.output)
    response = post_snapshot(args.hub_url, snapshot, args.token or os.environ.get("QUOTA_HUB_TOKEN"))
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    serve(
        host=args.host,
        port=args.port,
        store_path=Path(args.store).expanduser(),
        token=args.token or os.environ.get("QUOTA_HUB_TOKEN"),
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-quota-coach",
        description="Codex Quota Coach Lite collector and hub.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Read local Codex logs and emit a snapshot JSON.")
    add_common_collect_args(collect)
    collect.add_argument(
        "--output",
        default="-",
        help="Output JSON path. Use '-' for stdout. Defaults to stdout.",
    )
    collect.set_defaults(func=cmd_collect)

    submit = subparsers.add_parser("submit", help="Collect local usage and submit it to a Quota Hub.")
    add_common_collect_args(submit)
    submit.add_argument("--hub-url", required=True, help="Quota Hub base URL, for example http://host:8765.")
    submit.add_argument("--token", default=None, help="Bearer token. Defaults to QUOTA_HUB_TOKEN.")
    submit.add_argument("--output", default=None, help="Optional local copy of the generated snapshot JSON.")
    submit.set_defaults(func=cmd_submit)

    serve_parser = subparsers.add_parser("serve", help="Run the central Quota Hub HTTP server.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind host. Use 0.0.0.0 for LAN access.")
    serve_parser.add_argument("--port", type=int, default=8765, help="Bind port. Defaults to 8765.")
    serve_parser.add_argument(
        "--store",
        default="./data/latest-quota.json",
        help="Path to the stored latest snapshot JSON.",
    )
    serve_parser.add_argument("--token", default=None, help="Read/write token. Defaults to QUOTA_HUB_TOKEN.")
    serve_parser.set_defaults(func=cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        parser.exit(1, f"error: {exc}\n")
