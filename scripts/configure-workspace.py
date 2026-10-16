"""Configure two locale entry points backed by one installed extension and case."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
home = Path.home()
base = json.loads((root / "demo/.vscode/settings.json").read_text())
base["lsdyna.manualsDir"] = str(root / "manual-pack")
# Explicitly requested for these disposable demo profiles, not the host computer.
base["security.workspace.trust.enabled"] = False
# Keep the demo focused on DynaSense, without Copilot sign-in or parent-repo prompts.
base["chat.disableAIFeatures"] = True
base["workbench.secondarySideBar.defaultVisibility"] = "hidden"
base["git.openRepositoryInParentFolders"] = "never"
base["extensions.autoCheckUpdates"] = False
base["extensions.autoUpdate"] = False
base["workbench.enableExperiments"] = False
base["debug.showInStatusBar"] = "never"
# Match the local single-row, filename-sized tabs with less vertical padding.
base["workbench.editor.showTabs"] = "multiple"
base["workbench.editor.tabSizing"] = "fit"
base["workbench.editor.wrapTabs"] = False
base["window.density.editorTabHeight"] = "compact"
servers = {}
for suffix, locale in (("zh", "zh-cn"), ("en", "en")):
    profile = home / ".local/share/code-server" / ("profile-" + suffix)
    user = profile / "User"
    user.mkdir(parents=True, exist_ok=True)
    settings = {**base, "lsdyna.language": locale}
    (user / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2))
    servers["vscode-" + suffix] = {
        "command": ["code-server", "--auth", "none", "--disable-telemetry", "--disable-update-check",
                    "--locale", locale, "--user-data-dir", str(profile),
                    "--extensions-dir", str(home / ".local/share/code-server/extensions"),
                    "--builtin-extensions-dir", str(home / ".local/share/code-server/demo-builtins"),
                    "--port", "{port}", str(root / "demo")],
        "timeout": 300,
        "launcher_entry": {"title": "DynaSense · " + ("中文" if suffix == "zh" else "English")},
        "new_browser_tab": True,
    }
# code-server is reached through the authenticated Binder/Jupyter proxy.
# The .d directory enables extensions; general traitlets belong in the root config.
config = home / ".jupyter/jupyter_server_config.json"
config.parent.mkdir(parents=True, exist_ok=True)
config.write_text(json.dumps({"ServerProxy": {"servers": servers}}, ensure_ascii=False, indent=2))
