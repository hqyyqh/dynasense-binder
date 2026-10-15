"""Sample whole-container memory during interactive Binder acceptance (Linux)."""
import argparse
import datetime
import json
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("output", type=Path)
parser.add_argument("--seconds", type=int, default=600)
args = parser.parse_args()
if args.seconds < 1 or args.seconds > 3600:
    parser.error("--seconds must be between 1 and 3600")
cgroup = Path("/sys/fs/cgroup")
paths = {"currentBytes": cgroup / "memory.current", "peakBytes": cgroup / "memory.peak",
         "limitBytes": cgroup / "memory.max"}
if not paths["currentBytes"].exists():
    paths = {"currentBytes": cgroup / "memory/memory.usage_in_bytes",
             "peakBytes": cgroup / "memory/memory.max_usage_in_bytes",
             "limitBytes": cgroup / "memory/memory.limit_in_bytes"}
if not paths["currentBytes"].exists():
    raise SystemExit("Container memory counters are unavailable; no memory result recorded.")
args.output.parent.mkdir(parents=True, exist_ok=True)
start = time.monotonic()
with args.output.open("x", encoding="utf-8") as stream:
    while time.monotonic() - start < args.seconds:
        row = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "elapsedSeconds": time.monotonic() - start, "scope": "visible container cgroup"}
        for key, path in paths.items():
            raw = path.read_text().strip() if path.exists() else None
            row[key] = int(raw) if raw and raw.isdigit() else raw
        # File cache is included in memory.current and can be reclaimed by Linux.
        stat_path = cgroup / "memory.stat"
        if stat_path.exists():
            counters = dict(line.split() for line in stat_path.read_text().splitlines())
            row["anonymousBytes"] = int(counters["anon"]) if "anon" in counters else None
            row["fileCacheBytes"] = int(counters["file"]) if "file" in counters else None
        events_path = cgroup / "memory.events"
        if events_path.exists():
            row["events"] = {key: int(value) for key, value in
                             (line.split() for line in events_path.read_text().splitlines())}
        stream.write(json.dumps(row) + "\n")
        stream.flush()
        time.sleep(1)
