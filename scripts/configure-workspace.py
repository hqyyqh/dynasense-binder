"""Configure two locale entry points backed by one installed extension and case."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
home = Path.home()
base = json.loads((root / "demo/.vscode/settings.json").read_text())
base["lsdyna.manualsDir"] = str(root / "manual-pack")
servers = {}
for suffix, locale in (("zh", "zh-cn"), ("en", "en")):
    profile = home / ".local/share/code-server" / ("profile-" + suffix)
    user = profile / "User"
    user.mkdir(parents=True, exist_ok=True)
    settings = {**base, "lsdyna.language": locale}
    (user / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2))
    servers["vscode-" + suffix] = {
        "command": ["code-server", "--auth", "none", "--disable-telemetry",
                    "--locale", locale, "--user-data-dir", str(profile),
                    "--extensions-dir", str(home / ".local/share/code-server/extensions"),
                    "--port", "{port}", str(root / "demo")],
        "timeout": 300,
        "launcher_entry": {"title": "DynaSense · " + ("中文" if suffix == "zh" else "English")},
        "new_browser_tab": True,
    }
# code-server is reached through the authenticated Binder/Jupyter proxy.
config = home / ".jupyter/jupyter_server_config.d/dynasense.json"
config.parent.mkdir(parents=True, exist_ok=True)
config.write_text(json.dumps({"ServerProxy": {"servers": servers}}, ensure_ascii=False, indent=2))
