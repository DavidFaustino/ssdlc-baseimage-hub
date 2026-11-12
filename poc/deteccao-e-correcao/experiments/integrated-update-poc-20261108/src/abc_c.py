"""Bind the controlled direct OCI capture to the frozen historical case.

Only the byte-identical A3-H2 replay is accepted. The captured observation
has a new clock time, while the archived case supplies the package ledger and
canonical item required by the existing historical consumer.
"""

from __future__ import annotations

import hashlib
import json

from .pipeline import OCI


def bind_direct_capture(capture: dict, index_body: bytes, child_body: bytes,
                        case: dict) -> dict:
    obs, event = capture["observation"], capture["event"]
    descriptor = OCI.select_platform(index_body, obs["index_media_type"],
                                     obs["index_digest"], obs["platform"])
    child_digest = "sha256:" + hashlib.sha256(child_body).hexdigest()
    if (descriptor["platform_digest"] != child_digest or
            descriptor["platform_size"] != len(child_body) or
            descriptor["platform_media_type"] != obs["platform_media_type"] or
            obs["platform_digest"] != child_digest):
        raise ValueError("direct child bytes differ from index or observation")
    child = json.loads(child_body)
    if (child.get("schemaVersion") != 2 or
            child.get("mediaType") != descriptor["platform_media_type"]):
        raise ValueError("direct child media type differs")
    matches = [item for item in case["observations"]
               if item["observation"]["index_digest"] == obs["index_digest"] and
               item["observation"]["platform_digest"] == child_digest and
               (item["event"] is None) == (event is None)]
    if len(matches) != 1:
        raise ValueError("direct capture is outside frozen historical digest pair")
    canonical = matches[0]
    expected = canonical["observation"]
    for field in ("image", "tag", "platform", "index_media_type",
                  "platform_media_type", "fix_status", "image_approved"):
        if obs[field] != expected[field]:
            raise ValueError(f"direct capture {field} differs from frozen case")
    expected_event = canonical["event"]
    if (event is None) != (expected_event is None):
        raise ValueError("direct event presence differs from frozen case")
    if event is not None:
        for field in ("event_id", "image", "tag", "platform", "previous_digest",
                      "candidate_digest", "fix_status", "image_approved"):
            if event[field] != expected_event[field]:
                raise ValueError(f"direct event {field} differs from frozen case")
    return canonical
