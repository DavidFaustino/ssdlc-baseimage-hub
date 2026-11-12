"""Fail-closed consumer for the frozen A3 evidence records; controlled tests only."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import jsonschema


HERE = Path(__file__).resolve().parent
HUB = HERE.parents[3]
EVIDENCE = HERE.parent
A3H1 = EVIDENCE / "A3-H1"
A3H2 = EVIDENCE / "A3-H2"
HIST = HUB / "experiments/historical-image-case-20261107/evidence/digests"
SCHEMA_PATH = A3H1 / "contract.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker())
SPEC = importlib.util.spec_from_file_location("a3h1_compare", A3H1 / "run-version-cases.py")
COMPARATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARATOR)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard(condition: bool, reason: str):
    if not condition:
        raise ValueError(reason)


def validate_bundle(bundle: dict):
    guard(bundle["schema_sha256"] == digest(SCHEMA_PATH), "schema hash mismatch")
    records = bundle["records"]
    ids = [record["record_id"] for record in records]
    guard(len(ids) == len(set(ids)), "duplicate record_id")
    guard(len({record["case_id"] for record in records}) == 1, "cross-case records")
    for record in records:
        VALIDATOR.validate(record)
        for source in record["sources"]:
            path = (HUB / source["uri"]).resolve()
            guard(path.is_relative_to(HUB.resolve()), "source path escaped hub")
            guard(path.is_file(), "missing source file")
            guard(source["sha256"] == digest(path), "source hash mismatch")


def record_by_id(bundle: dict, record_id: str) -> dict:
    matches = [record for record in bundle["records"] if record["record_id"] == record_id]
    guard(len(matches) == 1, f"missing/duplicate {record_id}")
    return matches[0]


def require_suite_proof(proof: dict, candidate_digest: str, package_suite: str):
    ledger_path = (HUB / proof["source_ledger"]).resolve()
    guard(ledger_path.is_relative_to(HUB.resolve()), "suite ledger path escaped hub")
    guard(ledger_path.is_file(), "suite ledger missing")
    guard(proof["source_ledger_sha256"] == digest(ledger_path), "suite ledger hash mismatch")
    guard(candidate_digest in proof["historical_platform_manifests"], "suite proof digest mismatch")
    guard(package_suite == "trixie", "suite mismatch")
    ledger = json.loads(ledger_path.read_text())
    guard(ledger["failures"] == [] and ledger["unique_layers"] == 34, "incomplete suite replay")
    guard(len(ledger["replay"]) == 2, "missing suite replay path")
    downloads = {item["digest"]: item["size"] for item in ledger["downloads"]}
    guard({item["label"] for item in ledger["replay"]} == {"pre", "post"},
          "suite replay labels mismatch")
    for index, label in enumerate(("pre", "post")):
        manifest_path = HIST / f"{label}-manifest.json"
        guard("sha256:" + digest(manifest_path) == proof["historical_platform_manifests"][index],
              "suite replay manifest binding mismatch")
        manifest = json.loads(manifest_path.read_text())
        layers = manifest["layers"]
        guard(all(downloads.get(layer["digest"]) == layer["size"] for layer in layers),
              "suite replay layers not bound to manifest")
        result = next(item for item in ledger["replay"] if item["label"] == label)
        guard(result["layers_verified"] == 33 and all(result["suite_checks"].values()),
              "suite final path not verified")
        guard(all(0 <= transition["layer"] < len(layers)
                  and transition["digest"] == layers[transition["layer"]]["digest"]
                  for transition in result["transitions"]),
              "suite transitions not bound to manifest")


def require_raw_package_binding(candidate: dict):
    """Recheck normalized package fields against hashed archived evidence."""
    data = candidate["data"]
    sources = {Path(source["uri"]).name: HUB / source["uri"] for source in candidate["sources"]}
    manifest = sources["post-manifest.json"]
    status = sources["post-libexpat1.status"]
    guard("sha256:" + digest(manifest) == data["platform_digest"],
          "archived manifest digest mismatch")
    fields = dict(line.split(": ", 1) for line in status.read_text().splitlines() if ": " in line)
    guard(fields["Package"] == data["binary_package"]
          and fields["Version"] == data["binary_version"]
          and fields["Architecture"] == data["architecture"], "archived package fields mismatch")
    match = re.fullmatch(r"([^ ()]+)(?: \(([^()]+)\))?", fields["Source"])
    guard(match is not None and match.group(1) == data["source_package"],
          "archived Source field mismatch")
    source_version = match.group(2) or fields["Version"]
    basis = "explicit_source_field" if match.group(2) else "debian_policy_same_as_binary"
    guard(data["source_version"] == source_version and data["source_version_basis"] == basis,
          "archived source version mismatch")


def decide(bundle: dict, raw_event: dict | None, suite_proof: dict) -> dict:
    """Return an action only after schema, provenance and cross-record checks."""
    try:
        validate_bundle(bundle)
        advisory = record_by_id(bundle, "advisory-expat")
        candidate = record_by_id(bundle, "pkg-post")
        observation = record_by_id(bundle, "oci-local-replay-change")
        guard(advisory["kind"] == "debian_advisory" and candidate["kind"] == "image_package"
              and observation["kind"] == "oci_observation", "record kind mismatch")
        a, p, o = advisory["data"], candidate["data"], observation["data"]
        guard(raw_event is not None, "missing raw OCI event")
        guard(o["state"] == "changed" and o["tag"] == "local-replay"
              and o["image"].startswith("fixture.local/"), "not a controlled change")
        guard(raw_event["candidate_digest"] == p["platform_digest"] == o["platform_digest"],
              "candidate digest relation broken")
        guard(raw_event["previous_digest"] != raw_event["candidate_digest"],
              "same digest is not change")
        guard(raw_event["platform"] == o["platform"] == f"linux/{p['architecture']}",
              "architecture relation broken")
        guard(raw_event["image"] == o["image"] and raw_event["tag"] == o["tag"],
              "event reference mismatch")
        guard(p["suite"] == a["suite"] and p["source_package"] == a["source_package"],
              "suite/source relation broken")
        guard(p["inspection_state"] == "observed" and p["binary_package"] == "libexpat1",
              "package inspection missing")
        require_raw_package_binding(candidate)
        require_suite_proof(suite_proof, p["platform_digest"], p["suite"])
        comparison = COMPARATOR.classify({
            "package_suite": p["suite"], "advisory_suite": a["suite"],
            "package_arch": p["architecture"], "target_arch": o["platform"].split("/", 1)[1],
            "package_source": p["source_package"], "advisory_source": a["source_package"],
            "platform_digest": p["platform_digest"], "fix_state": a["fix_state"],
            "source_version_basis": p["source_version_basis"],
            "installed": p["binary_version"], "source_version": p["source_version"],
            "fixed": a["fixed_source_version"],
        })
        guard(comparison != "unknown", "invalid or missing Debian fix version")
        return {"action": "validate_candidate" if comparison == "at_or_above_fix" else "wait",
                "comparison": comparison, "reason": "validated inputs", "image_approved": False}
    except jsonschema.ValidationError as error:
        return {"action": "unknown", "comparison": "unknown",
                "reason": f"schema {error.validator} at {error.json_path}", "image_approved": False}
    except (ValueError, KeyError, OSError, IndexError, StopIteration) as error:
        return {"action": "unknown", "comparison": "unknown", "reason": str(error),
                "image_approved": False}


def explicit_source_status(path: Path) -> dict:
    fields = dict(line.split(": ", 1) for line in path.read_text().splitlines() if ": " in line)
    match = re.fullmatch(r"([^ ()]+) \(([^()]+)\)", fields["Source"])
    guard(match is not None, "synthetic explicit Source field malformed")
    return {"binary_package": fields["Package"], "source_package": match.group(1),
            "source_version": match.group(2), "binary_version": fields["Version"],
            "architecture": fields["Architecture"], "source_version_basis": "explicit_source_field"}


def explicit_classification(status: dict, fix: str) -> str:
    return COMPARATOR.classify({"package_suite": "trixie", "advisory_suite": "trixie",
        "package_arch": status["architecture"], "target_arch": "amd64",
        "package_source": status["source_package"], "advisory_source": "expat",
        "platform_digest": "sha256:" + "9" * 64,
        "fix_state": "fixed_version_known", "source_version_basis": status["source_version_basis"],
        "installed": status["binary_version"], "source_version": status["source_version"],
        "fixed": fix})


def main():
    original = json.loads((A3H2 / "inputs.json").read_text())
    raw_event = json.loads((A3H2 / "replay" / "replay.json").read_text())["observations"][1]["event"]
    suite_proof = json.loads((HERE / "suite-proof.json").read_text())
    cases = []

    def run(name: str, mutate, expected: str, reason_contains: str | None = None):
        bundle, event, proof = deepcopy(original), deepcopy(raw_event), deepcopy(suite_proof)
        mutate(bundle, event, proof)
        result = decide(bundle, event, proof)
        guard(result["action"] == expected, f"{name}: {result}")
        if reason_contains:
            guard(reason_contains in result["reason"], f"{name}: wrong rejection reason {result}")
        cases.append({"case": name, "expected": expected, "result": result,
                      "synthetic_mutation": name != "valid_archived_local_event"})

    noop = lambda bundle, event, proof: None
    run("valid_archived_local_event", noop, "validate_candidate")
    run("candidate_digest_mismatch", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "platform_digest", "sha256:" + "1" * 64), "unknown", "candidate digest relation broken")
    run("architecture_mismatch", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "architecture", "arm64"), "unknown", "architecture relation broken")
    run("source_mismatch", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "source_package", "zlib"), "unknown", "suite/source relation broken")
    run("suite_mismatch", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "suite", "bookworm"), "unknown", "suite/source relation broken")
    run("invalid_fixed_version", lambda b, e, p: record_by_id(b, "advisory-expat")["data"].__setitem__(
        "fixed_source_version", "invalid!"), "unknown", "invalid or missing Debian fix version")
    run("missing_required_schema_field", lambda b, e, p: record_by_id(b, "pkg-post")["data"].pop(
        "source_package"), "unknown", "schema")
    run("broken_source_hash", lambda b, e, p: record_by_id(b, "pkg-post")["sources"][0].__setitem__(
        "sha256", "0" * 64), "unknown", "source hash mismatch")
    run("suite_evidence_hash_broken", lambda b, e, p: p.__setitem__(
        "source_ledger_sha256", "0" * 64), "unknown", "suite ledger hash mismatch")
    run("suite_manifest_binding_swapped", lambda b, e, p: p["historical_platform_manifests"].reverse(),
        "unknown", "suite replay manifest binding mismatch")
    run("suite_ledger_missing", lambda b, e, p: p.__setitem__("source_ledger", "missing.json"),
        "unknown", "suite ledger missing")
    run("suite_uncertain", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "suite", None), "unknown", "schema")
    run("normalized_package_version_tampered", lambda b, e, p: record_by_id(b, "pkg-post")["data"].__setitem__(
        "binary_version", "9.9-1"), "unknown", "archived package fields mismatch")
    # Missing event is passed directly, because mutate cannot rebind a caller's event.
    missing = decide(deepcopy(original), None, deepcopy(suite_proof))
    guard(missing["action"] == "unknown", "missing event should be unknown")
    cases.append({"case": "raw_event_absent", "expected": "unknown", "result": missing,
                  "synthetic_mutation": True})
    explicit = []
    for name, expected in (("synthetic-source-fixed.status", "at_or_above_fix"),
                           ("synthetic-source-below.status", "below_fix")):
        path = HERE / name
        parsed = explicit_source_status(path)
        compared = explicit_classification(parsed, "2.8.2-1~deb13u1")
        guard(compared == expected, f"{name}: {compared}")
        explicit.append({"case": name, "sha256": digest(path), "synthetic": True,
                         "parsed": parsed, "comparison": compared, "image_approved": False,
                         "recommendation": "unknown: synthetic status has no verified OCI digest binding"})
    output = {"consumer_cases": cases, "explicit_source_cases": explicit,
              "schema_sha256": digest(SCHEMA_PATH),
              "source_bundle_sha256": digest(A3H2 / "inputs.json"),
              "suite_proof_sha256": digest(HERE / "suite-proof.json")}
    (HERE / "consumer-results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(cases)} consumer cases; {len(explicit)} explicit Source comparisons; no approval")


if __name__ == "__main__":
    main()
