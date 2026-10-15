import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('language', Path(__file__).with_name('configure-language.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LanguageTest(unittest.TestCase):
    def test_installed_translation_is_indexed_and_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            data = home / '.local/share/code-server'
            extension = data / 'extensions/ms-ceintl.vscode-language-pack-zh-hans-1.131.0'
            extension.mkdir(parents=True)
            translation = extension / 'main.json'
            translation.write_text('{}')
            (extension / 'package.json').write_text(json.dumps({
                'publisher': 'MS-CEINTL', 'name': 'vscode-language-pack-zh-hans', 'version': '1.131.0',
                'contributes': {'localizations': [{'languageId': 'zh-cn', 'languageName': 'Chinese',
                    'translations': [{'id': 'vscode', 'path': './main.json'}]}]},
            }))
            module.configure(home)
            for suffix in ('zh', 'en'):
                pack = json.loads((data / ('profile-' + suffix) / 'languagepacks.json').read_text())
                self.assertEqual(pack['zh-cn']['translations']['vscode'], str(translation.resolve()))
            translation.unlink()
            with self.assertRaises(AssertionError):
                module.configure(home)
