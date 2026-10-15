"""Fetch the immutable release assets selected for this Binder build."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile


def extract_manual(archive_path, root):
    with zipfile.ZipFile(archive_path) as archive:
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in entry.filename
                    or not path.parts or path.parts[0] != "manual-pack"
                    or (entry.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError("Invalid manual archive member: " + entry.filename)
            if not (root / entry.filename).resolve().is_relative_to(root.resolve()):
                raise ValueError("Manual member leaves the deployment directory")
        archive.extractall(root)


def main():
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / "runtime-assets.json").read_text())
    (root / "assets").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dynasense-assets-") as temporary:
        for kind in ("extension", "manual"):
            asset = lock[kind]
            if not asset["url"].startswith("https://github.com/hqyyqh/dynasense-binder/releases/download/"):
                raise ValueError("Unexpected deployment asset URL")
            path = Path(temporary) / kind
            with urllib.request.urlopen(asset["url"], timeout=120) as response, path.open("wb") as target:
                shutil.copyfileobj(response, target)
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != asset["sha256"]:
                raise ValueError("Asset hash mismatch: " + kind)
            if kind == "manual":
                extract_manual(path, root)
            else:
                shutil.copyfile(path, root / "assets/dynasense-linux-x64.vsix")
    files = {}
    for path in [root / "assets/dynasense-linux-x64.vsix", *sorted((root / "manual-pack").rglob("*"))]:
        if path.is_file():
            with path.open("rb") as stream:
                files[path.relative_to(root).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
    (root / "assets/manifest.json").write_text(json.dumps({"files": files}, indent=2))


if __name__ == "__main__":
    main()
