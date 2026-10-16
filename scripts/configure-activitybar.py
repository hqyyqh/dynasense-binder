"""Set code-server's first-use sidebar defaults; keep saved visitor choices.

The web workbench stores pinned views in browser storage, not User/settings.json.
This narrow host customization changes only the missing-storage fallback. It does
not modify the DynaSense VSIX. Checked against code-server 4.132.0.
"""
import json
from pathlib import Path
import sys

ORIGINAL = 'getStoredPinnedViewContainersValue(){return this.storageService.get(this.options.pinnedViewContainersKey,0,"[]")}'
DEFAULTS = [
    {"id": identifier, "pinned": pinned, "visible": True, "order": index}
    for index, (identifier, pinned) in enumerate([
        ("workbench.view.explorer", True), ("workbench.view.search", True),
        ("workbench.view.scm", False), ("workbench.view.debug", False),
        ("workbench.view.extensions", True),
        ("workbench.view.extension.lsdyna-includes", True),
    ])
]
FALLBACK = json.dumps(json.dumps(DEFAULTS, separators=(",", ":")))
REPLACEMENT = ('getStoredPinnedViewContainersValue(){return this.storageService.get('
               'this.options.pinnedViewContainersKey,0,this.options.pinnedViewContainersKey==='
               '"workbench.activity.pinnedViewlets2"?' + FALLBACK + ':"[]")}')


def configure(path):
    source = path.read_text()
    if source.count(REPLACEMENT) == 1:
        return
    if source.count(ORIGINAL) != 1:
        raise ValueError("Host sidebar implementation changed; review defaults before publishing")
    path.write_text(source.replace(ORIGINAL, REPLACEMENT))


if __name__ == "__main__":
    configure(Path(sys.prefix) / "share/code-server/lib/vscode/out/vs/workbench/workbench.web.main.internal.js")
