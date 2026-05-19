import unittest
from datetime import datetime, timedelta, timezone

from quota_coach.model import build_snapshot


class BuildSnapshotTest(unittest.TestCase):
    def test_computes_remaining_and_idle_status(self):
        now = datetime(2026, 5, 19, 10, 0, tzinfo=timezone.utc)
        reset = now + timedelta(hours=1)
        snapshot = build_snapshot(
            {
                "limit_id": "codex",
                "plan_type": "plus",
                "primary": {
                    "used_percent": 20,
                    "window_minutes": 300,
                    "resets_at": int(reset.timestamp()),
                },
                "secondary": {
                    "used_percent": 6,
                    "window_minutes": 10080,
                    "resets_at": int((now + timedelta(days=6)).timestamp()),
                },
            },
            snapshot_at=now,
            collected_at=now,
            source_device="test-machine",
        )

        self.assertEqual(snapshot["primary"]["remainingPercent"], 80)
        self.assertEqual(snapshot["weekly"]["remainingPercent"], 94)
        self.assertEqual(snapshot["primary"]["status"], "idle")
        self.assertEqual(snapshot["headline"], "额度闲置偏多")

    def test_marks_old_data_stale(self):
        now = datetime(2026, 5, 19, 10, 0, tzinfo=timezone.utc)
        snapshot = build_snapshot(
            {
                "primary": {
                    "used_percent": 20,
                    "window_minutes": 300,
                    "resets_at": int((now + timedelta(hours=1)).timestamp()),
                },
                "secondary": {
                    "used_percent": 6,
                    "window_minutes": 10080,
                    "resets_at": int((now + timedelta(days=6)).timestamp()),
                },
            },
            snapshot_at=now - timedelta(hours=4),
            collected_at=now,
            source_device="test-machine",
            stale_after_hours=3,
        )

        self.assertIs(snapshot["stale"], True)
        self.assertEqual(snapshot["headline"], "数据已过期")
        self.assertEqual(snapshot["primary"]["status"], "stale")


if __name__ == "__main__":
    unittest.main()
