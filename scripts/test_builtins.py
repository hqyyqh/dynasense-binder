import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

configure = runpy.run_path(str(Path(__file__).with_name("configure-builtins.py")))["configure"]


class BuiltinCheck(unittest.TestCase):
    def test_retains_reading_and_references_and_rejects_broken_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root / "source", root / "selected"
            for name in ("markdown-language-features", "references-view", "git"):
                folder = source / name
                folder.mkdir(parents=True)
                (folder / "package.json").write_text(json.dumps({"publisher": "vscode", "name": name}))
            with patch.object(Path, "symlink_to") as link:
                configure(source, destination)
                self.assertEqual({call.args[0].name for call in link.call_args_list},
                                 {"markdown-language-features", "references-view"})
            manifest = source / "references-view/package.json"
            package = json.loads(manifest.read_text())
            package["extensionDependencies"] = ["vscode.git"]
            manifest.write_text(json.dumps(package))
            with self.assertRaisesRegex(ValueError, "requires excluded vscode.git"):
                configure(source, destination)
            self.assertTrue((source / "git/package.json").exists())


if __name__ == "__main__":
    unittest.main()
