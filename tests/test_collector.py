import json
import unittest
from pathlib import Path

from quota_coach.collector import collect_snapshot


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


class CollectSnapshotTest(unittest.TestCase):
    def test_uses_latest_rate_limits(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            sessions = Path(directory) / "sessions"
            write_jsonl(
                sessions / "2026" / "05" / "19" / "rollout.jsonl",
                [
                    {
                        "timestamp": "2026-05-19T09:00:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "rate_limits": {
                                "limit_id": "codex",
                                "plan_type": "plus",
                                "primary": {"used_percent": 10, "window_minutes": 300, "resets_at": 1779192000},
                                "secondary": {"used_percent": 2, "window_minutes": 10080, "resets_at": 1779697600},
                            },
                        },
                    },
                    {
                        "timestamp": "2026-05-19T10:00:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "rate_limits": {
                                "limit_id": "codex",
                                "plan_type": "plus",
                                "primary": {"used_percent": 20, "window_minutes": 300, "resets_at": 1779195600},
                                "secondary": {"used_percent": 6, "window_minutes": 10080, "resets_at": 1779697600},
                            },
                        },
                    },
                ],
            )

            snapshot = collect_snapshot(sessions, source_device="test-machine", stale_after_hours=999999)

        self.assertEqual(snapshot["sourceDevice"], "test-machine")
        self.assertEqual(snapshot["plan"], "plus")
        self.assertEqual(snapshot["primary"]["remainingPercent"], 80)
        self.assertEqual(snapshot["weekly"]["remainingPercent"], 94)


if __name__ == "__main__":
    unittest.main()
