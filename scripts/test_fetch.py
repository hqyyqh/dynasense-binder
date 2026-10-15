import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("fetch", Path(__file__).with_name("fetch-assets.py"))
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


class ExtractionCheck(unittest.TestCase):
    def test_only_manual_paths_are_extracted(self):
        for member in ["manual-pack/manifest.json", "../escape", "/escape", "manual-pack/../../escape", "demo/main.k"]:
            with self.subTest(member=member), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive = root / "manual.zip"
                with zipfile.ZipFile(archive, "w") as output:
                    output.writestr(member, "fixture")
                if member == "manual-pack/manifest.json":
                    fetch.extract_manual(archive, root)
                    self.assertEqual((root / member).read_text(), "fixture")
                else:
                    with self.assertRaises(ValueError):
                        fetch.extract_manual(archive, root)


if __name__ == "__main__":
    unittest.main()
