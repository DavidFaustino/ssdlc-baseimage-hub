"""Observe one public OCI tag and emit a candidate only after a changed baseline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen


OCI_INDEX = "application/vnd.oci.image.index.v1+json"
DOCKER_INDEX = "application/vnd.docker.distribution.manifest.list.v2+json"
OCI_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
DOCKER_MANIFEST = "application/vnd.docker.distribution.manifest.v2+json"
ACCEPT = ", ".join((OCI_INDEX, DOCKER_INDEX, OCI_MANIFEST, DOCKER_MANIFEST))
IMAGE = "gcr.io/distroless/java21-debian13"
TAG = "nonroot"
PLATFORM = "linux/amd64"


def digest_of(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


def select_platform(body: bytes, content_type: str, header_digest: str, platform: str) -> dict:
    if digest_of(body) != header_digest:
        raise ValueError("index digest differs from response bytes")
    content_type = content_type.split(";", 1)[0].strip()
    if content_type not in {OCI_INDEX, DOCKER_INDEX}:
        raise ValueError("expected OCI/Docker image index")
    index = json.loads(body)
    if index.get("schemaVersion") != 2 or index.get("mediaType") != content_type:
        raise ValueError("index media type or schema differs from response")
    os_name, arch = platform.split("/", 1)
    matches = [item for item in index.get("manifests", [])
               if item.get("platform", {}).get("os") == os_name
               and item.get("platform", {}).get("architecture") == arch
               and item.get("mediaType") in {OCI_MANIFEST, DOCKER_MANIFEST}]
    if len(matches) != 1:
        raise ValueError("expected exactly one platform manifest")
    item = matches[0]
    return {"index_digest": header_digest, "platform_digest": item["digest"],
            "platform_size": item["size"], "platform_media_type": item["mediaType"]}


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def record(observation: dict, state_path: Path, events_path: Path) -> dict | None:
    state_path, events_path = Path(state_path), Path(events_path)
    previous = json.loads(state_path.read_text()) if state_path.exists() else None
    key = ("image", "tag", "platform")
    if previous and any(previous.get(field) != observation.get(field) for field in key):
        raise ValueError("reference differs from stored baseline")
    event = None
    if previous and previous["platform_digest"] != observation["platform_digest"]:
        event_key = "|".join(str(observation[field]) for field in key)
        event_key += "|" + previous["platform_digest"] + "|" + observation["platform_digest"]
        event = {
            "event_id": hashlib.sha256(event_key.encode()).hexdigest(),
            "image": observation["image"], "tag": observation["tag"],
            "platform": observation["platform"],
            "previous_digest": previous["platform_digest"],
            "candidate_digest": observation["platform_digest"],
            "previous_observed_at_utc": previous["observed_at_utc"],
            "candidate_observed_at_utc": observation["observed_at_utc"],
            "fix_status": "unknown", "image_approved": False,
        }
        events_path.parent.mkdir(parents=True, exist_ok=True)
        existing = set()
        if events_path.exists():
            existing = {json.loads(line)["event_id"] for line in events_path.read_text().splitlines() if line}
        if event["event_id"] not in existing:
            with events_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
    _write_json_atomic(state_path, observation)
    return event


def _get_manifest(reference: str) -> tuple[bytes, str, str, str | None]:
    url = f"https://gcr.io/v2/distroless/java21-debian13/manifests/{reference}"
    request = Request(url, headers={"Accept": ACCEPT})
    with urlopen(request, timeout=15) as response:
        body = response.read()
        return body, response.headers.get("Content-Type", ""), response.headers.get("Docker-Content-Digest", ""), response.headers.get("Date")


def observe_live(evidence_dir: Path, state_path: Path, events_path: Path) -> tuple[dict, dict | None]:
    index_body, index_type, index_digest, registry_date = _get_manifest(TAG)
    descriptor = select_platform(index_body, index_type, index_digest, PLATFORM)
    child_body, child_type, child_digest, child_date = _get_manifest(descriptor["platform_digest"])
    if digest_of(child_body) != descriptor["platform_digest"] or child_digest != descriptor["platform_digest"]:
        raise ValueError("platform manifest digest differs from descriptor")
    if len(child_body) != descriptor["platform_size"]:
        raise ValueError("platform manifest size differs from descriptor")
    if child_type.split(";", 1)[0].strip() != descriptor["platform_media_type"]:
        raise ValueError("platform manifest media type differs from descriptor")
    child_manifest = json.loads(child_body)
    if child_manifest.get("schemaVersion") != 2 or child_manifest.get("mediaType") != descriptor["platform_media_type"]:
        raise ValueError("platform manifest body differs from response media type")
    observation = {"image": IMAGE, "tag": TAG, "platform": PLATFORM,
                   "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                   "index_digest": descriptor["index_digest"],
                   "platform_digest": descriptor["platform_digest"],
                   "index_media_type": index_type.split(";", 1)[0].strip(),
                   "platform_media_type": descriptor["platform_media_type"],
                   "request_accept": ACCEPT,
                   "registry_date_index": registry_date, "registry_date_platform": child_date,
                   "fix_status": "unknown", "image_approved": False}
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "tag-index.json").write_bytes(index_body)
    (evidence_dir / "platform-manifest.json").write_bytes(child_body)
    _write_json_atomic(evidence_dir / "response-headers.json", {
        "tag": {"Content-Type": index_type, "Docker-Content-Digest": index_digest,
                "Content-Length": len(index_body), "Date": registry_date},
        "platform": {"Content-Type": child_type, "Docker-Content-Digest": child_digest,
                     "Content-Length": len(child_body), "Date": child_date},
    })
    _write_json_atomic(evidence_dir / "observation.json", observation)
    event = record(observation, state_path, events_path)
    return observation, event


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    observation, event = observe_live(args.evidence_dir, args.state, args.events)
    print(json.dumps({"observation": observation, "candidate_event": event}, indent=2, sort_keys=True))
