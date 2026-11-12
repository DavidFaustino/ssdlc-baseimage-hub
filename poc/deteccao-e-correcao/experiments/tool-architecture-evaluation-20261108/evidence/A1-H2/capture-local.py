"""Capture only Diun's documented non-secret event fields in the local fixture."""

import json
import os
from pathlib import Path

keys = ("DIUN_VERSION", "DIUN_ENTRY_STATUS", "DIUN_ENTRY_PROVIDER", "DIUN_ENTRY_IMAGE",
        "DIUN_ENTRY_MIMETYPE", "DIUN_ENTRY_DIGEST", "DIUN_ENTRY_CREATED", "DIUN_ENTRY_PLATFORM")
with Path(os.environ.get("DIUN_CAPTURE_PATH", "local-notifications.jsonl")).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({key: os.environ.get(key) for key in keys}, sort_keys=True) + "\n")
