"""Daily scheduler gate; only successful main checks restart the 30-day clock."""
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


def is_due(event, artifacts, now):
    if event == "workflow_dispatch":
        return True
    successful = [datetime.fromisoformat(a["created_at"].replace("Z", "+00:00"))
                  for a in artifacts if not a["expired"]]
    return not successful or now >= max(successful) + timedelta(days=30)


if __name__ == "__main__":
    event = os.environ["GITHUB_EVENT_NAME"]
    artifacts = []
    if event != "workflow_dispatch":
        url = (f'https://api.github.com/repos/{os.environ["GITHUB_REPOSITORY"]}'
               '/actions/artifacts?name=release-check-success&per_page=100')
        request = Request(url, headers={"Authorization": f'Bearer {os.environ["GH_TOKEN"]}',
                                        "Accept": "application/vnd.github+json"})
        with urlopen(request, timeout=30) as response:
            artifacts = json.load(response)["artifacts"]
    due = is_due(event, artifacts, datetime.now(timezone.utc))
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"due={str(due).lower()}\n")
    print("Release check due" if due else "Last successful check is less than 30 days old")
