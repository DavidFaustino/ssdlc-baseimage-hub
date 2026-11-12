"""Load the archived producer records and verify the frozen input manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HUB = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
TOOLS = HUB / "experiments/tool-architecture-evaluation-20261108/evidence"
MANIFEST = HERE / "evidence/I0-H1/manifest.json"
REQUIRED_SOURCES = {
    "experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/replay/replay.json",
    "experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/inputs.json",
    "experiments/tool-architecture-evaluation-20261108/evidence/A3-H4/suite-proof.json",
    "experiments/tool-architecture-evaluation-20261108/evidence/A4-PATHS/ingestion/full-suite-replay.json",
}


def load_archived_case() -> dict:
    manifest = json.loads(MANIFEST.read_text())
    if manifest["scope"] != "local synthetic tag over archived real platform manifests":
        raise ValueError("fixture scope mismatch")
    sources = manifest["sources"]
    paths = [source["path"] for source in sources]
    if len(paths) != len(REQUIRED_SOURCES) or set(paths) != REQUIRED_SOURCES:
        raise ValueError("fixture source set mismatch")
    for source in sources:
        path = (HUB / source["path"]).resolve()
        if not path.is_relative_to(HUB) or not path.is_file():
            raise ValueError("missing or escaped fixture source")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("fixture source hash mismatch")
    replay = json.loads((TOOLS / "A3-H2/replay/replay.json").read_text())
    if replay["fixture_kind"] != manifest["scope"]:
        raise ValueError("replay scope mismatch")
    if len(replay["observations"]) != 3:
        raise ValueError("unexpected replay length")
    return {"observations": replay["observations"],
            "bundle": json.loads((TOOLS / "A3-H2/inputs.json").read_text()),
            "proof": json.loads((TOOLS / "A3-H4/suite-proof.json").read_text()),
            "scope": manifest["scope"],
            "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}
