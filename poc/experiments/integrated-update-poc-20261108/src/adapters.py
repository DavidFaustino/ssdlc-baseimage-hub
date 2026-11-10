"""Narrow adapters for archived Diun and Vunnel evidence.

These adapters compare producer contracts on one frozen case. They are not
listeners for live Diun notifications or a live Vunnel provider workspace.
"""

from __future__ import annotations

import hashlib
import json
import re

from .pipeline import OCI, Pipeline


SHA256 = re.compile(r"sha256:[0-9a-f]{64}\Z")
INDEX_MEDIA = {"application/vnd.oci.image.index.v1+json",
               "application/vnd.docker.distribution.manifest.list.v2+json"}


def process_diun_hint(pipeline: Pipeline, notification: dict, item: dict,
                      index_body: bytes, child_body: bytes | None, case: dict,
                      *, expected_image: str) -> dict:
    """Resolve a Diun index hint to the one verified OCI child, then correlate.

    The archived replay supplies the package/event. The notice alone cannot
    establish either and cannot authorize an image.
    """
    try:
        obs = item["observation"]
        expected_ref = f'{expected_image}:{obs["tag"]}'
        if (notification["DIUN_ENTRY_STATUS"] != "update" or
                notification["DIUN_ENTRY_IMAGE"] != expected_ref or
                notification["DIUN_ENTRY_PLATFORM"] != obs["platform"] or
                notification["DIUN_ENTRY_MIMETYPE"] not in INDEX_MEDIA or
                notification["DIUN_ENTRY_MIMETYPE"] != obs["index_media_type"]):
            return pipeline.unknown("Diun hint scope or media type differs")
        digest = notification["DIUN_ENTRY_DIGEST"]
        if (not isinstance(digest, str) or not SHA256.fullmatch(digest) or
                digest != "sha256:" + hashlib.sha256(index_body).hexdigest()):
            return pipeline.unknown("Diun index digest does not match fetched bytes")
        if not isinstance(child_body, bytes):
            return pipeline.unknown("Diun child manifest bytes missing")
        selected = OCI.select_platform(index_body, obs["index_media_type"],
                                       digest, obs["platform"])
        child_digest = "sha256:" + hashlib.sha256(child_body).hexdigest()
        if (child_digest != selected["platform_digest"] or
                len(child_body) != selected["platform_size"] or
                selected["platform_media_type"] != obs["platform_media_type"]):
            return pipeline.unknown("Diun child digest, size, or media type differs")
        child = json.loads(child_body)
        if (not isinstance(child, dict) or child.get("schemaVersion") != 2 or
                child.get("mediaType") != selected["platform_media_type"]):
            return pipeline.unknown("Diun child schema or media type differs")
    except (KeyError, TypeError, ValueError):
        return pipeline.unknown("malformed Diun hint")
    return pipeline.process_index_notice(item, index_body, digest, case)


def normalize_vunnel_fix(snapshot: dict, cve: str, case: dict) -> dict:
    """Compare one frozen Vunnel fix with the archived Debian advisory.

    Refuse ambiguous or divergent records. A returned fix is evidence of the
    archived snapshot only; this function never claims feed freshness.
    """
    metadata = snapshot["provider_metadata"]
    if (metadata["provider"] != "debian" or metadata["stale"] is not False or
            not metadata["timestamp"]):
        raise ValueError("Vunnel provider metadata missing or stale")
    selected = snapshot["selected_records"][cve]["vunnel"]
    if selected["identifier"] != f"debian:13/{cve.lower()}":
        raise ValueError("Vunnel record identifier differs")
    vulnerability = selected["item"]["Vulnerability"]
    if vulnerability["Name"] != cve or vulnerability["NamespaceName"] != "debian:13":
        raise ValueError("Vunnel CVE or namespace differs")
    fixes = vulnerability["FixedIn"]
    matches = [row for row in fixes if row.get("Name") == "expat" and
               row.get("NamespaceName") == "debian:13"]
    if len(matches) != 1:
        raise ValueError("Vunnel fix missing or ambiguous")
    fix = matches[0]
    if fix["VersionFormat"] != "dpkg" or fix["Available"]["Kind"] != "advisory":
        raise ValueError("Vunnel version basis or availability differs")
    summaries = fix["VendorAdvisory"]["AdvisorySummary"]
    if len(summaries) != 1 or summaries[0]["ID"] != "DSA-6404-1":
        raise ValueError("Vunnel advisory identity differs")
    advisory = next(row["data"] for row in case["bundle"]["records"]
                    if row["record_id"] == "advisory-expat")
    if (advisory["suite"] != "trixie" or advisory["source_package"] != "expat" or
            advisory["fixed_source_version"] != fix["Version"]):
        raise ValueError("Vunnel fix diverges from archived Debian advisory")
    return {"source": "vunnel_debian_snapshot", "provider_timestamp": metadata["timestamp"],
            "cve": cve, "advisory": summaries[0]["ID"], "source_package": "expat",
            "suite": "trixie", "fixed_source_version": fix["Version"],
            "version_format": "dpkg", "scope": "archived_fixture"}
