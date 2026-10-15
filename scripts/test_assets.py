import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class AssetCheck(unittest.TestCase):
    def test_changed_missing_and_escaping_assets(self):
        with tempfile.TemporaryDirectory(prefix="dynasense-binder-check-") as temporary:
            root = Path(temporary)
            for name in ["scripts", "assets", "manual-pack"]:
                (root / name).mkdir()
            script = root / "scripts/check-assets.py"
            shutil.copyfile(Path(__file__).with_name("check-assets.py"), script)
            files = {}
            for name in ["assets/dynasense-linux-x64.vsix", "manual-pack/manifest.json"]:
                (root / name).write_bytes(b"test fixture")
                files[name] = hashlib.sha256(b"test fixture").hexdigest()
            manifest = root / "assets/manifest.json"
            manifest.write_text(json.dumps({"files": files}))
            def run():
                return subprocess.run([sys.executable, str(script)], capture_output=True).returncode
            self.assertEqual(run(), 0)
            (root / "assets/dynasense-linux-x64.vsix").write_bytes(b"changed")
            self.assertNotEqual(run(), 0)
            (root / "assets/dynasense-linux-x64.vsix").unlink()
            self.assertNotEqual(run(), 0)
            manifest.write_text(json.dumps({"files": {"../outside": "invalid"}}))
            self.assertNotEqual(run(), 0)


if __name__ == "__main__":
    unittest.main()
