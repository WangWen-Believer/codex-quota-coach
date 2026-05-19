from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .model import build_snapshot, now_local, parse_datetime


DEFAULT_SESSIONS_DIR = Path.home() / ".codex" / "sessions"


@dataclass(frozen=True)
class RateLimitRecord:
    timestamp: Any
    rate_limits: dict[str, Any]
    path: Path
    line_number: int

    @property
    def observed_at(self):
        return parse_datetime(self.timestamp)


def iter_session_files(sessions_dir: Path) -> Iterable[Path]:
    if not sessions_dir.exists():
        return []
    return sorted(
        sessions_dir.glob("**/*.jsonl"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )


def iter_rate_limit_records(sessions_dir: Path) -> Iterable[RateLimitRecord]:
    for path in iter_session_files(sessions_dir):
        try:
            handle = path.open("r", encoding="utf-8", errors="replace")
        except OSError:
            continue

        with handle:
            for line_number, line in enumerate(handle, start=1):
                if '"rate_limits"' not in line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = item.get("payload") if isinstance(item, dict) else None
                if not isinstance(payload, dict):
                    continue
                rate_limits = payload.get("rate_limits")
                if not isinstance(rate_limits, dict):
                    continue
                yield RateLimitRecord(
                    timestamp=item.get("timestamp"),
                    rate_limits=rate_limits,
                    path=path,
                    line_number=line_number,
                )


def find_latest_record(sessions_dir: Path) -> RateLimitRecord | None:
    latest: RateLimitRecord | None = None
    latest_at = None
    for record in iter_rate_limit_records(sessions_dir):
        observed_at = record.observed_at
        if observed_at is None:
            continue
        if latest_at is None or observed_at > latest_at:
            latest = record
            latest_at = observed_at
    return latest


def collect_snapshot(
    sessions_dir: Path = DEFAULT_SESSIONS_DIR,
    *,
    source_device: str | None = None,
    stale_after_hours: float = 3,
) -> dict[str, Any]:
    record = find_latest_record(sessions_dir)
    collected_at = now_local()
    if record is None:
        return {
            "schemaVersion": 1,
            "updatedAt": None,
            "collectedAt": collected_at.isoformat(),
            "ageSeconds": None,
            "sourceDevice": source_device or socket.gethostname(),
            "plan": None,
            "limitId": None,
            "primary": {"label": "5h", "status": "unknown", "statusText": "未知"},
            "weekly": {"label": "Weekly", "status": "unknown", "statusText": "未知"},
            "headline": "暂无额度数据",
            "stale": True,
            "error": f"No rate_limits records found under {sessions_dir}",
        }

    snapshot = build_snapshot(
        record.rate_limits,
        snapshot_at=record.observed_at,
        source_device=source_device or socket.gethostname(),
        collected_at=collected_at,
        stale_after_hours=stale_after_hours,
    )
    snapshot["sourcePath"] = str(record.path)
    snapshot["sourceLine"] = record.line_number
    return snapshot
