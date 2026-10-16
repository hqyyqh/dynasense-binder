import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("activitybar", Path(__file__).with_name("configure-activitybar.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ActivityBarCheck(unittest.TestCase):
    def test_only_missing_sidebar_state_changes_and_rerun_is_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbench.js"
            path.write_text("before;" + module.ORIGINAL + ";after")
            module.configure(path)
            result = path.read_text()
            self.assertEqual(result, "before;" + module.REPLACEMENT + ";after")
            module.configure(path)
            self.assertEqual(path.read_text(), result)
            self.assertEqual(sum(item["pinned"] for item in module.DEFAULTS), 4)

    def test_unknown_host_stops_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbench.js"
            path.write_text("different host")
            with self.assertRaises(ValueError):
                module.configure(path)
            self.assertEqual(path.read_text(), "different host")
