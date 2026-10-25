"""Hide demo-only distractions once, then keep visitor layout choices.

The web workbench stores pinned views in browser storage, not User/settings.json.
Migrate only activity-bar pins and account visibility, including existing browser
state. Does not modify the DynaSense VSIX. Checked against code-server 4.132.0.
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
REPLACEMENT = ('getStoredPinnedViewContainersValue(){let value=this.storageService.get('
               'this.options.pinnedViewContainersKey,0,this.options.pinnedViewContainersKey==='
               '"workbench.activity.pinnedViewlets2"?' + FALLBACK + ':"[]");'
               'if(this.options.pinnedViewContainersKey==="workbench.activity.pinnedViewlets2"'
               '&&!this.storageService.getBoolean("dynasense.activitybar.hiddenViews.v1",0,!1)){'
               'let views=JSON.parse(value);'
               'for(let id of ["workbench.view.scm","workbench.view.debug"]){'
               'let view=views.find(item=>item.id===id);'
               'if(view)view.pinned=false;else views.push({id,pinned:false,visible:true});}'
               'value=JSON.stringify(views);'
               'this.storageService.store(this.options.pinnedViewContainersKey,value,0,0);'
               'this.storageService.store("dynasense.activitybar.hiddenViews.v1",true,0,1);}'
               'return value}')
ACCOUNTS_ORIGINAL = 'function Xrt(s){return s.getBoolean(y1.ACCOUNTS_VISIBILITY_PREFERENCE_KEY,0,!0)}'
ACCOUNTS_REPLACEMENT = (
    'function Xrt(s){'
    'if(!s.getBoolean("dynasense.activitybar.accountsHidden.v1",0,!1)){'
    's.store(y1.ACCOUNTS_VISIBILITY_PREFERENCE_KEY,false,0,0);'
    's.store("dynasense.activitybar.accountsHidden.v1",true,0,1);}'
    'return s.getBoolean(y1.ACCOUNTS_VISIBILITY_PREFERENCE_KEY,0,!1)}'
)


def configure(path):
    source = path.read_text(encoding="utf-8")
    for original, replacement in [(ORIGINAL, REPLACEMENT), (ACCOUNTS_ORIGINAL, ACCOUNTS_REPLACEMENT)]:
        if source.count(replacement) == 1 and original not in source:
            continue
        if source.count(original) != 1 or replacement in source:
            raise ValueError("Host sidebar implementation changed; review defaults before publishing")
        source = source.replace(original, replacement)
    path.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    configure(Path(sys.prefix) / "share/code-server/lib/vscode/out/vs/workbench/workbench.web.main.internal.js")
