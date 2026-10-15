"""Check the exact VSIX and full manual pack selected for this validation run."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / "assets/manifest.json").read_text())
for relative, expected in lock["files"].items():
    target = (root / relative).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError(f"Missing or invalid asset: {relative}")
    with target.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise ValueError(f"Changed asset: {relative}")
if "assets/dynasense-linux-x64.vsix" not in lock["files"]:
    raise ValueError("A verified Linux VSIX is required")
if "manual-pack/manifest.json" not in lock["files"]:
    raise ValueError("The complete manual pack is required for this measurement")
print(f"Verified {len(lock['files'])} files")
