import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location("cadence", Path(__file__).with_name("release-check-due.py"))
cadence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cadence)


class CadenceTests(unittest.TestCase):
    def test_thirty_days_and_manual_override(self):
        start = datetime(2026, 1, 31, tzinfo=timezone.utc)
        records = [{"created_at": start.isoformat(), "expired": False}]
        self.assertFalse(cadence.is_due("schedule", records, start + timedelta(days=29)))
        self.assertTrue(cadence.is_due("schedule", records, start + timedelta(days=30)))
        self.assertTrue(cadence.is_due("workflow_dispatch", records, start))
        self.assertTrue(cadence.is_due("schedule", [], start))
        records[0]["expired"] = True
        self.assertTrue(cadence.is_due("schedule", records, start))
