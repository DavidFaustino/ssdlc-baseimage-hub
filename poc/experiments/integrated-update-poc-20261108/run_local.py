"""Execute the frozen local OCI→Debian→package decision with SQLite receipts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import tempfile

from src.inputs import load_archived_case
from src.pipeline import Pipeline
from src.state import State


def _write_exports(output: Path, documents: dict[str, dict]) -> None:
    """Publish receipts atomically, preserving malformed prior exports."""
    for name, document in documents.items():
        target = output / name
        if not target.exists():
            continue
        try:
            current = json.loads(target.read_text())
        except (ValueError, UnicodeError):
            if target.with_name(name + ".corrupt").exists():
                raise ValueError(f"corrupt receipt archive already exists: {name}")
        else:
            if current != document:
                raise ValueError(f"conflicting receipt: {name}")
    for name, document in documents.items():
        target = output / name
        if target.exists():
            try:
                json.loads(target.read_text())
            except (ValueError, UnicodeError):
                target.rename(target.with_name(name + ".corrupt"))
            else:
                continue
        payload = json.dumps(document, indent=2, sort_keys=True) + "\n"
        fd, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=output)
        try:
            with os.fdopen(fd, "w") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def recover_receipts(output: Path, case: dict) -> None:
    """Re-export one committed fixture decision; never re-run the model or decision."""
    output = Path(output)
    database = output / "state.sqlite"
    if not database.is_file():
        raise ValueError("committed state.sqlite is missing")
    try:
        with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
            decisions = db.execute("SELECT event_id, receipt_json FROM decisions").fetchall()
            reassessments = db.execute("SELECT receipt_json FROM reassessments").fetchall()
            observations = db.execute("SELECT platform_digest FROM observations").fetchall()
    except (sqlite3.Error, ValueError) as error:
        raise ValueError(f"invalid committed state: {error}") from error
    try:
        receipt = json.loads(decisions[0][1])
        advisory_receipt = json.loads(reassessments[0][0])
        expected_event = case["observations"][1]["event"]
        expected_obs = case["observations"][1]["observation"]
        expected_advisory = next(record["data"] for record in case["bundle"]["records"]
                                 if record["record_id"] == "advisory-expat")
        matches = (len(decisions) == len(reassessments) == len(observations) == 1 and
                   decisions[0][0] == expected_event["event_id"] and
                   observations[0][0] == expected_obs["platform_digest"] and
                   receipt["event_id"] == expected_event["event_id"] and
                   receipt["previous_digest"] == expected_event["previous_digest"] and
                   receipt["candidate_digest"] == expected_event["candidate_digest"] and
                   receipt["image"] == expected_obs["image"] and
                   receipt["tag"] == expected_obs["tag"] and
                   receipt["platform"] == expected_obs["platform"] and
                   receipt["fixture_manifest_sha256"] == case["manifest_sha256"] and
                   receipt["source_ledger_sha256"] == case["proof"]["source_ledger_sha256"] and
                   receipt["status"] == "decided" and receipt["action"] == "validate_candidate" and
                   receipt["image_approved"] is False and
                   advisory_receipt["platform_digest"] == expected_obs["platform_digest"] and
                   advisory_receipt["revision"] == expected_advisory["advisory_id"] and
                   advisory_receipt["fixed_source_version"] == expected_advisory["fixed_source_version"] and
                   advisory_receipt["fixture_manifest_sha256"] == case["manifest_sha256"] and
                   advisory_receipt["status"] == "reassessed" and
                   advisory_receipt["action"] == "already_satisfies_fix" and
                   advisory_receipt["image_approved"] is False)
    except (IndexError, KeyError, TypeError, ValueError, StopIteration):
        matches = False
    if not matches:
        raise ValueError("state does not match archived fixture")
    run = {"scope": case["scope"], "statuses": ["baseline", "decided", "unchanged"],
           "decision_count": 1, "reassessment_count": 1, "image_approved": False}
    _write_exports(output, {"receipt.json": receipt,
                            "advisory-receipt.json": advisory_receipt,
                            "run.json": run})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True,
                        help="new output directory for state.sqlite and receipt.json")
    parser.add_argument("--recover", action="store_true",
                        help="re-export receipts from a committed state.sqlite")
    args = parser.parse_args()
    case = load_archived_case()
    if args.recover:
        recover_receipts(args.output, case)
        print("PASS recovered receipts from committed state; no new decision")
        return
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("output directory must be new and empty")
    args.output.mkdir(parents=True, exist_ok=True)
    with State(args.output / "state.sqlite") as state:
        pipeline = Pipeline(state)
        results = [pipeline.process(item, case) for item in case["observations"]]
        if [item["status"] for item in results] != ["baseline", "decided", "unchanged"]:
            raise RuntimeError(f"unexpected sequence: {results}")
        if state.count_decisions() != 1:
            raise RuntimeError("expected exactly one decision")
        advisory = next(r for r in case["bundle"]["records"] if r["record_id"] == "advisory-expat")
        reassessment = pipeline.reassess_stable(
            case, advisory["data"]["advisory_id"], advisory["data"]["fixed_source_version"])
        if reassessment["action"] != "already_satisfies_fix" or state.count_reassessments() != 1:
            raise RuntimeError(f"unexpected stable-digest reassessment: {reassessment}")
        recover_receipts(args.output, case)
    print("PASS baseline→validate_candidate→unchanged; stable digest reassessed; no approval")


if __name__ == "__main__":
    main()
