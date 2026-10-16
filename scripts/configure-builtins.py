"""Expose only relevant built-ins to the demo; keep the installed originals intact."""
import json
from pathlib import Path
import sys


EXCLUDED = {
    "GitHub.copilot-chat", "vscode.debug-auto-launch", "vscode.merge-conflict",
    "vscode.git", "vscode.git-base", "vscode.github",
    "vscode.github-authentication", "vscode.microsoft-authentication",
    "vscode.emmet", "vscode.extension-editing", "vscode.npm",
    "vscode.grunt", "vscode.gulp", "vscode.jake",
    "vscode.css-language-features", "vscode.html-language-features",
    "vscode.typescript-language-features", "vscode.php-language-features",
    "ms-vscode.js-debug", "ms-vscode.js-debug-companion",
    "ms-vscode.vscode-js-profile-table", "vscode.terminal-suggest",
    "vscode.ipynb", "vscode.builtin-notebook-renderers",
}


def configure(source, destination):
    manifests = {}
    for manifest in source.glob("*/package.json"):
        package = json.loads(manifest.read_text())
        manifests[package["publisher"] + "." + package["name"]] = (manifest.parent, package)
    if not {"vscode.markdown-language-features", "vscode.references-view"} <= manifests.keys():
        raise ValueError("Expected code-server built-ins were not found")
    retained = manifests.keys() - EXCLUDED
    for identifier in retained:
        for dependency in manifests[identifier][1].get("extensionDependencies", []):
            if dependency in EXCLUDED:
                raise ValueError(f"{identifier} requires excluded {dependency}")
    destination.mkdir(parents=True, exist_ok=True)
    for identifier in sorted(retained):
        original = manifests[identifier][0]
        link = destination / original.name
        if not link.is_symlink():
            link.symlink_to(original, target_is_directory=True)
        elif link.resolve() != original.resolve():
            raise ValueError(f"Unexpected built-in link: {link}")
    print(json.dumps({"excluded": sorted(manifests.keys() & EXCLUDED), "retained": len(retained)}))


if __name__ == "__main__":
    configure(Path(sys.prefix) / "share/code-server/lib/vscode/extensions",
              Path.home() / ".local/share/code-server/demo-builtins")
