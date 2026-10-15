"""Index the installed Chinese language pack for code-server's two profiles.

Schema: microsoft/vscode src/vs/platform/languagePacks/node/languagePacks.ts.
The headless install does not create languagepacks.json in this host build.
"""
import hashlib
import json
from pathlib import Path


def configure(home):
    data = home / '.local/share/code-server'
    manifests = list((data / 'extensions').glob('ms-ceintl.vscode-language-pack-zh-hans-*/package.json'))
    assert len(manifests) == 1, 'Expected one installed Chinese language pack'
    manifest = manifests[0]
    metadata = json.loads(manifest.read_text())
    identifier = metadata['publisher'] + '.' + metadata['name']
    localization = next(item for item in metadata['contributes']['localizations'] if item['languageId'] == 'zh-cn')
    translations = {}
    for item in localization['translations']:
        path = (manifest.parent / item['path']).resolve()
        assert path.is_relative_to(manifest.parent.resolve()) and path.is_file(), path
        translations[item['id']] = str(path)
    assert 'vscode' in translations
    pack = {'zh-cn': {
        'hash': hashlib.md5((identifier + metadata['version']).encode()).hexdigest(),
        'label': localization.get('localizedLanguageName', localization['languageName']),
        'extensions': [{'extensionIdentifier': {'id': identifier}, 'version': metadata['version']}],
        'translations': translations,
    }}
    for suffix in ('zh', 'en'):
        profile = data / ('profile-' + suffix)
        profile.mkdir(parents=True, exist_ok=True)
        (profile / 'languagepacks.json').write_text(json.dumps(pack, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    configure(Path.home())
