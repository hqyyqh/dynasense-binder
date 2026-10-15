import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("stage", Path(__file__).with_name("stage-candidate.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateCheck(unittest.TestCase):
    def test_candidate_preserves_manual_and_repeat_is_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "candidate").mkdir()
            data = dict(repository="hqyyqh/vscode-lsdyna", releaseId=9, assetId=10,
                        tag="v3.2.1", version="3.2.1", url="https://example.invalid/package",
                        sha256="a"*64, publishedAt="2026-10-16T00:00:00Z")
            (root / "candidate/release.json").write_text(json.dumps(data))
            (root / "runtime-assets.json").write_text(json.dumps({"extension": {}, "manual": {"sha256": "keep"}}))
            (root / "release-policy.json").write_text('{}')
            module.stage(root)
            before = (root / "runtime-assets.json").read_bytes()
            module.stage(root)
            self.assertEqual(before, (root / "runtime-assets.json").read_bytes())
            self.assertEqual(json.loads(before)["manual"], {"sha256": "keep"})
            self.assertEqual(json.loads((root / "release-policy.json").read_text())["acceptedAssetId"], 10)
