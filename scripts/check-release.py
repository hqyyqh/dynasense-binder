"""Fetch an exact stable Linux VSIX candidate; never promote it to the live demo."""
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request
import zipfile


def select_asset(release, policy):
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Only a stable release can become a candidate")
    assets = [a for a in release["assets"] if re.fullmatch(
        r"dynasense-[0-9]+\.[0-9]+\.[0-9]+-linux-x64\.vsix", a["name"])]
    if len(assets) != 1:
        raise ValueError("Expected exactly one Linux x64 VSIX")
    asset = assets[0]
    if (release["id"] == policy.get("acceptedReleaseId")
            and asset["id"] == policy.get("acceptedAssetId")):
        return None
    if policy["source"] == "local-snapshot":
        return None
    if policy["source"] != "github-release":
        raise ValueError("Unknown release source policy")
    if release["id"] == policy.get("acceptedReleaseId"):
        raise ValueError("An accepted release asset was replaced; review it explicitly")
    if not policy.get("acceptedPublishedAt"):
        raise ValueError("Set the accepted release date before enabling release updates")
    if release["published_at"] <= policy["acceptedPublishedAt"]:
        raise ValueError("The latest endpoint returned an older release; keep the accepted package")
    return asset


def verify_vsix(path, asset):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = asset.get("digest")
    if expected and expected != "sha256:" + digest:
        raise ValueError("Release asset digest mismatch")
    with zipfile.ZipFile(path) as archive:
        package = json.loads(archive.read("extension/package.json"))
        manifest = archive.read("extension.vsixmanifest").decode("utf-8")
    if (package.get("publisher"), package.get("name")) != ("hqyyqh", "dynasense"):
        raise ValueError("Unexpected extension identity")
    if asset["name"] != f"dynasense-{package['version']}-linux-x64.vsix":
        raise ValueError("Package version does not match asset name")
    if 'TargetPlatform="linux-x64"' not in manifest:
        raise ValueError("Package is not Linux x64")
    return digest, package["version"], package["engines"]["vscode"]


def main():
    root = Path(__file__).resolve().parents[1]
    policy = json.loads((root / "release-policy.json").read_text())
    repo = policy["repository"]
    if repo != "hqyyqh/vscode-lsdyna":
        raise ValueError("Unexpected upstream repository")
    headers = {"User-Agent": "dynasense-binder", "Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    request = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        release = json.load(response)
    asset = select_asset(release, policy)
    if asset is None:
        print(json.dumps({"status": "local-snapshot-held" if policy["source"] == "local-snapshot" else "unchanged",
                          "latestRelease": release["tag_name"]}))
        return
    url = asset["browser_download_url"]
    if not url.startswith(f"https://github.com/{repo}/releases/download/"):
        raise ValueError("Unexpected release download URL")
    out = root / "candidate"
    out.mkdir(exist_ok=False)
    path = out / "dynasense-linux-x64.vsix"
    # Download is public; do not forward the API token to an asset redirect.
    with urllib.request.urlopen(url, timeout=120) as response, path.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)
    digest, version, engine = verify_vsix(path, asset)
    result = {"repository": repo, "releaseId": release["id"], "tag": release["tag_name"],
              "publishedAt": release["published_at"],
              "assetId": asset["id"], "url": url, "sha256": digest,
              "upstreamDigest": asset.get("digest"), "version": version,
              "vscodeEngine": engine, "status": "downloaded-awaiting-runtime-validation"}
    (out / "release.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
