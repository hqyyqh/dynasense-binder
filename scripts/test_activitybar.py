import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("activitybar", Path(__file__).with_name("configure-activitybar.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ActivityBarCheck(unittest.TestCase):
    def test_both_host_changes_and_rerun_are_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbench.js"
            path.write_text("before;" + module.ORIGINAL + ";" + module.ACCOUNTS_ORIGINAL + ";after")
            module.configure(path)
            result = path.read_text()
            self.assertEqual(result, "before;" + module.REPLACEMENT + ";" + module.ACCOUNTS_REPLACEMENT + ";after")
            module.configure(path)
            self.assertEqual(path.read_text(), result)
            self.assertEqual(sum(item["pinned"] for item in module.DEFAULTS), 4)

    def test_unknown_host_stops_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workbench.js"
            for source in ["different host", module.ORIGINAL, module.ORIGINAL * 2 + module.ACCOUNTS_ORIGINAL]:
                path.write_text(source)
                with self.assertRaises(ValueError):
                    module.configure(path)
                self.assertEqual(path.read_text(), source)

    def test_layout_migration_in_javascript(self):
        script = r'''
const assert = require('node:assert/strict');
const I1 = { ACCOUNTS_VISIBILITY_PREFERENCE_KEY: 'workbench.activity.showAccounts' };
const readAccounts = eval('(' + accounts + ')');
const key = 'workbench.activity.pinnedViewlets2';
function host(saved, otherKey = key) {
    const data = new Map(Object.entries(saved));
    const storageService = {
        get: (key, scope, fallback) => data.has(key) ? data.get(key) : fallback,
        getBoolean: (key, scope, fallback) => data.has(key) ? data.get(key) : fallback,
        store: (key, value) => data.set(key, value),
    };
    return Object.assign(eval('({' + pins + '})'), {
        options: { pinnedViewContainersKey: otherKey }, storageService, data,
    });
}
for (const saved of [{}, {[key]: '[]'}, {[key]: JSON.stringify([
    {id: 'workbench.view.scm', pinned: true, order: 7},
    {id: 'workbench.view.debug', pinned: true, order: 8},
    {id: 'custom.view', pinned: false, order: 1},
])}]) {
    const h = host({...saved, 'editor.state': 'untouched'});
    const views = JSON.parse(h.getStoredPinnedViewContainersValue());
    for (const id of ['workbench.view.scm', 'workbench.view.debug']) {
        assert.equal(views.find(v => v.id === id).pinned, false);
    }
    if (views.some(v => v.id === 'custom.view')) {
        assert.deepEqual(views.find(v => v.id === 'custom.view'), {id: 'custom.view', pinned: false, order: 1});
        assert.equal(views.find(v => v.id === 'workbench.view.scm').order, 7);
    }
    assert.equal(h.data.get('editor.state'), 'untouched');
    views.find(v => v.id === 'workbench.view.debug').pinned = true;
    h.data.set(key, JSON.stringify(views));
    assert.equal(JSON.parse(h.getStoredPinnedViewContainersValue()).find(v => v.id === 'workbench.view.debug').pinned, true);
}
const panel = host({'panel.pins': '[]'}, 'panel.pins');
assert.equal(panel.getStoredPinnedViewContainersValue(), '[]');
assert.deepEqual([...panel.data.keys()], ['panel.pins']);
for (const saved of [{}, {[I1.ACCOUNTS_VISIBILITY_PREFERENCE_KEY]: true}]) {
    const h = host(saved);
    assert.equal(readAccounts(h.storageService), false);
    h.data.set(I1.ACCOUNTS_VISIBILITY_PREFERENCE_KEY, true);
    assert.equal(readAccounts(h.storageService), true);
}
'''
        subprocess.run(["node", "-e", "const pins=" + json.dumps(module.REPLACEMENT)
                        + ";const accounts=" + json.dumps(module.ACCOUNTS_REPLACEMENT)
                        + ";" + script], check=True)
