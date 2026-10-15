"""Exercise the real authenticated Jupyter proxy under a Binder-style prefix."""
import json
from html.parser import HTMLParser
import os
import secrets
import signal
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urljoin


base = "http://127.0.0.1:8899/user/binder-validation/"
token = secrets.token_hex(24)


def get(path):
    request = Request(urljoin(base, path), headers={"Authorization": "token " + token})
    with urlopen(request, timeout=120) as response:
        return response.status, response.read().decode("utf-8"), response.url


class WorkbenchAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.paths.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.paths.append(attrs["href"])


with tempfile.TemporaryFile(mode="w+") as log:
    server = subprocess.Popen([
        "jupyter", "lab", "--no-browser", "--ip=127.0.0.1", "--port=8899",
        "--ServerApp.port_retries=0", "--ServerApp.base_url=/user/binder-validation/",
        "--IdentityProvider.token=" + token,
    ], stdout=log, stderr=log, start_new_session=True)
    try:
        deadline = time.monotonic() + 60
        while True:
            try:
                get("api")
                break
            except URLError:
                if server.poll() is not None or time.monotonic() >= deadline:
                    raise
                time.sleep(1)
        for language in ("zh", "en"):
            for slash in ("", "/"):
                status, html, url = get("vscode-" + language + slash)
                assert status == 200 and 'id="vscode-workbench' in html, (status, url, html[:200])
                print(json.dumps({"route": "vscode-" + language + slash,
                                  "status": status, "workbench": True}), flush=True)
                if slash:
                    assets = WorkbenchAssets()
                    assets.feed(html)
                    assert assets.paths, 'Workbench must expose local scripts/styles'
                    if language == "zh":
                        assert any("zh-cn" in asset.lower() for asset in assets.paths), 'Chinese host translation was not loaded'
                    for asset in assets.paths:
                        target = urljoin(url, asset)
                        assert target.startswith(base), target
                        status, body, _ = get(target)
                        assert status == 200 and body.strip() and '<!DOCTYPE html>' not in body[:100]
                    print(json.dumps({"language": language, "assets": assets.paths, "status": "passed"}), flush=True)
    finally:
        os.killpg(server.pid, signal.SIGTERM)
        server.wait(timeout=20)
        log.seek(0)
        print(log.read().replace(token, "[REDACTED]"))
