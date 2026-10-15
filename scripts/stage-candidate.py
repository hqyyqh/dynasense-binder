"""Update only the release references in a candidate branch."""
import json
from pathlib import Path


def stage(root):
    candidate = json.loads((root / "candidate/release.json").read_text())
    if candidate["repository"] != "hqyyqh/vscode-lsdyna":
        raise ValueError("Unexpected release repository")
    lock = json.loads((root / "runtime-assets.json").read_text())
    lock["extension"] = {key: candidate[key] for key in
                         ("releaseId", "assetId", "tag", "version", "url", "sha256")}
    lock["extension"]["source"] = "github-release"
    policy = json.loads((root / "release-policy.json").read_text())
    policy.update(source="github-release", acceptedReleaseId=candidate["releaseId"],
                  acceptedAssetId=candidate["assetId"], acceptedPublishedAt=candidate["publishedAt"],
                  note="Candidate release reference. Promote only after runtime and bilingual UI acceptance.")
    for name, value in (("runtime-assets.json", lock), ("release-policy.json", policy)):
        (root / name).write_text(json.dumps(value, indent=2)+"\n")
    body = (f"Update the demo to the unmodified official {candidate['tag']} Linux x64 VSIX.\n\n"
            f"Asset SHA-256: `{candidate['sha256']}`. The manual asset remains unchanged.\n\n"
            "The runtime workflow is dispatched on this branch. Before merging, complete the Chinese/English "
            "walkthrough and startup/session checks. Update the homepage reference only after acceptance.\n")
    (root / "candidate/pr-body.md").write_text(body)


if __name__ == "__main__":
    stage(Path(__file__).resolve().parents[1])
