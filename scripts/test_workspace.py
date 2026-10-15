import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


class LocaleWorkspaceCheck(unittest.TestCase):
    def test_two_profiles_share_one_case_without_resetting_it(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(Path, "home", return_value=Path(temporary)):
            home = Path(temporary)
            runpy.run_path(str(Path(__file__).with_name("configure-workspace.py")))
            servers = json.loads((home / ".jupyter/jupyter_server_config.json").read_text())["ServerProxy"]["servers"]
            self.assertEqual(servers["vscode-zh"]["command"][-1], servers["vscode-en"]["command"][-1])
            for suffix, locale in (("zh", "zh-cn"), ("en", "en")):
                settings = json.loads((home / f".local/share/code-server/profile-{suffix}/User/settings.json").read_text())
                self.assertEqual(settings["lsdyna.language"], locale)
                self.assertFalse(settings["security.workspace.trust.enabled"])
                command = servers["vscode-" + suffix]["command"]
                self.assertEqual(command[command.index("--locale") + 1], locale)
                self.assertEqual(command[command.index("--extensions-dir") + 1], str(home / ".local/share/code-server/extensions"))
                self.assertTrue(settings["lsdyna.manualsDir"].endswith("manual-pack"))


if __name__ == "__main__":
    unittest.main()
