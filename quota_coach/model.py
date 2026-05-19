from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


STATUS_LABELS = {
    "healthy": "节奏正常",
    "slow": "偏慢",
    "idle": "闲置多",
    "fast": "偏快",
    "low": "快用完",
    "empty": "已耗尽",
    "stale": "数据待刷新",
    "unknown": "未知",
}


def now_local() -> datetime:
    return datetime.now().astimezone()


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).astimezone()
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.astimezone()
    return parsed.astimezone()


def clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def percent_value(value: float) -> float | int:
    rounded = round(value, 1)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def format_percent(value: float | int | None) -> str:
    if value is None:
        return "--"
    return f"{value}%"


def format_display_time(value: datetime | None, reference: datetime) -> str | None:
    if value is None:
        return None
    local = value.astimezone(reference.tzinfo)
    if local.date() == reference.date():
        return local.strftime("%H:%M")
    days = (local.date() - reference.date()).days
    if 0 <= days < 7:
        return local.strftime("%a %H:%M")
    return local.strftime("%m-%d %H:%M")


def build_window(label: str, raw: dict[str, Any] | None, reference: datetime) -> dict[str, Any]:
    if not raw:
        return {
            "label": label,
            "status": "unknown",
            "statusText": STATUS_LABELS["unknown"],
            "remainingPercent": None,
            "remainingText": "--",
        }

    used = float(raw.get("used_percent") or 0)
    remaining = clamp_percent(100.0 - used)
    window_minutes = int(raw.get("window_minutes") or 0)
    reset_at = parse_datetime(raw.get("resets_at"))

    ideal_remaining = None
    idle_gap = None
    expired = False
    if reset_at and window_minutes > 0:
        seconds_left = (reset_at - reference).total_seconds()
        expired = seconds_left <= 0
        ideal_remaining = clamp_percent((seconds_left / (window_minutes * 60)) * 100)
        idle_gap = remaining - ideal_remaining

    if expired:
        status = "stale"
    elif remaining <= 3:
        status = "empty"
    elif remaining < 15:
        status = "low"
    elif idle_gap is None:
        status = "unknown"
    elif idle_gap > 25:
        status = "idle"
    elif idle_gap > 10:
        status = "slow"
    elif idle_gap < -10:
        status = "fast"
    else:
        status = "healthy"

    remaining_out = percent_value(remaining)
    used_out = percent_value(clamp_percent(used))
    ideal_out = percent_value(ideal_remaining) if ideal_remaining is not None else None
    gap_out = percent_value(idle_gap) if idle_gap is not None else None

    return {
        "label": label,
        "usedPercent": used_out,
        "remainingPercent": remaining_out,
        "remainingText": format_percent(remaining_out),
        "idealRemainingPercent": ideal_out,
        "idleGap": gap_out,
        "status": status,
        "statusText": STATUS_LABELS[status],
        "windowMinutes": window_minutes or None,
        "resetAt": reset_at.isoformat() if reset_at else None,
        "resetAtText": format_display_time(reset_at, reference),
        "expired": expired,
    }


def choose_headline(primary: dict[str, Any], weekly: dict[str, Any], stale: bool) -> str:
    if stale:
        return "数据已过期"
    if primary.get("status") == "stale" or weekly.get("status") == "stale":
        return "窗口已重置待刷新"
    if primary.get("status") in {"empty", "low"}:
        return "5h 额度偏低"
    if weekly.get("status") in {"empty", "low"}:
        return "周额度偏低"
    if primary.get("status") == "idle" or weekly.get("status") == "idle":
        return "额度闲置偏多"
    if primary.get("status") == "slow" or weekly.get("status") == "slow":
        return "使用偏慢"
    if primary.get("status") == "fast" or weekly.get("status") == "fast":
        return "使用偏快"
    if primary.get("status") == "unknown" and weekly.get("status") == "unknown":
        return "暂无额度数据"
    return "节奏正常"


def build_snapshot(
    rate_limits: dict[str, Any],
    *,
    snapshot_at: datetime | None,
    source_device: str,
    collected_at: datetime | None = None,
    stale_after_hours: float = 3,
) -> dict[str, Any]:
    collected = collected_at or now_local()
    observed = snapshot_at or collected
    observed = observed.astimezone(collected.tzinfo)

    age_seconds = max(0.0, (collected - observed).total_seconds())
    stale = age_seconds > stale_after_hours * 3600

    primary = build_window("5h", rate_limits.get("primary"), collected)
    weekly = build_window("Weekly", rate_limits.get("secondary"), collected)

    if stale:
        primary["rawStatus"] = primary.get("status")
        weekly["rawStatus"] = weekly.get("status")
        primary["status"] = "stale"
        weekly["status"] = "stale"
        primary["statusText"] = STATUS_LABELS["stale"]
        weekly["statusText"] = STATUS_LABELS["stale"]

    return {
        "schemaVersion": 1,
        "updatedAt": observed.isoformat(),
        "collectedAt": collected.isoformat(),
        "ageSeconds": int(age_seconds),
        "sourceDevice": source_device,
        "plan": rate_limits.get("plan_type"),
        "limitId": rate_limits.get("limit_id"),
        "primary": primary,
        "weekly": weekly,
        "headline": choose_headline(primary, weekly, stale),
        "stale": stale,
        "rateLimitReachedType": rate_limits.get("rate_limit_reached_type"),
        "credits": rate_limits.get("credits"),
    }
