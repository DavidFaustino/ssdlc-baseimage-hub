"""The first integrated slice uses archived evidence, never the public tag."""

import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from copy import deepcopy

from src.inputs import load_archived_case
from src.pipeline import Pipeline
from src.state import State


HUB = Path(__file__).resolve().parents[3]
POST_INDEX = HUB / "experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/replay/02-post/tag-index.json"


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "state.sqlite"
        self.case = load_archived_case()

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_missing_required_source_is_rejected(self):
        from src import inputs

        manifest = json.loads(inputs.MANIFEST.read_text())
        manifest["sources"] = manifest["sources"][:-1]
        candidate = Path(self.tmp.name) / "manifest.json"
        candidate.write_text(json.dumps(manifest))
        with patch.object(inputs, "MANIFEST", candidate):
            with self.assertRaisesRegex(ValueError, "fixture source set mismatch"):
                inputs.load_archived_case()

    def test_baseline_change_repeat_and_restart(self):
        first, changed, repeated = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            self.assertEqual("baseline", pipeline.process(first, self.case)["status"])
            self.assertEqual(0, state.count_decisions())
            result = pipeline.process(changed, self.case)
            self.assertEqual("validate_candidate", result["action"])
            self.assertFalse(result["image_approved"])
            self.assertEqual(64, len(result["fixture_manifest_sha256"]))
            self.assertEqual(self.case["proof"]["source_ledger_sha256"], result["source_ledger_sha256"])
            self.assertEqual(1, state.count_decisions())
            self.assertEqual("unchanged", pipeline.process(repeated, self.case)["status"])
            self.assertEqual(1, state.count_decisions())
        with State(self.db) as state:
            self.assertEqual(1, state.count_decisions())
            self.assertEqual("duplicate", Pipeline(state).process(changed, self.case)["status"])
            self.assertEqual(1, state.count_decisions())

    def test_missing_ledger_fails_closed_without_advancing_baseline(self):
        first, changed, _ = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            broken = dict(self.case)
            broken["proof"] = json.loads(json.dumps(self.case["proof"]))
            broken["proof"]["source_ledger"] = "missing/ledger.json"
            result = pipeline.process(changed, broken)
            self.assertEqual("unknown", result["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual(first["observation"]["platform_digest"],
                             state.get_observation(first["observation"])["platform_digest"])
            self.assertEqual("validate_candidate", pipeline.process(changed, self.case)["action"])
            self.assertEqual(1, state.count_decisions())

    def test_bad_event_and_transport_error_preserve_state(self):
        first, changed, _ = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            bad = json.loads(json.dumps(changed))
            bad["event"]["previous_digest"] = "sha256:" + "0" * 64
            self.assertEqual("unknown", pipeline.process(bad, self.case)["action"])
            self.assertEqual("unknown", pipeline.process(None, self.case)["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual(first["observation"]["platform_digest"],
                             state.get_observation(first["observation"])["platform_digest"])
            self.assertEqual("unknown", pipeline.process({"error": "bad"}, self.case)["action"])
            self.assertEqual(first["observation"]["platform_digest"],
                             state.get_observation(first["observation"])["platform_digest"])

    def test_reused_event_id_with_changed_payload_is_not_a_duplicate(self):
        first, changed, _ = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            pipeline.process(changed, self.case)
            forged = json.loads(json.dumps(changed))
            forged["event"]["candidate_digest"] = "sha256:" + "0" * 64
            result = pipeline.process(forged, self.case)
            self.assertEqual("unknown", result["action"])
            self.assertEqual(1, state.count_decisions())

    def test_http_failures_and_no_fix_keep_last_valid_digest(self):
        first, changed, _ = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            for status in (401, 403, 429, 503):
                result = pipeline.process({"error": {"http_status": status}}, self.case)
                self.assertEqual("unknown", result["action"])
                self.assertIn(str(status), result["reason"])
            no_fix = deepcopy(self.case)
            advisory = next(r for r in no_fix["bundle"]["records"] if r["record_id"] == "advisory-expat")
            advisory["data"]["fix_state"] = "no_fix_reported"
            advisory["data"]["fixed_source_version"] = None
            self.assertEqual("unknown", pipeline.process(changed, no_fix)["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual(first["observation"]["platform_digest"],
                             state.get_observation(first["observation"])["platform_digest"])
            self.assertEqual("validate_candidate", pipeline.process(changed, self.case)["action"])
            self.assertEqual(1, state.count_decisions())

    def test_diun_notice_requires_one_platform_child(self):
        first, changed, _ = self.case["observations"]
        valid_body = POST_INDEX.read_bytes()
        valid_digest = "sha256:" + hashlib.sha256(valid_body).hexdigest()
        duplicate = json.loads(valid_body)
        amd64 = next(m for m in duplicate["manifests"]
                     if m.get("platform", {}).get("architecture") == "amd64")
        duplicate["manifests"].append(amd64)
        duplicate_body = json.dumps(duplicate, separators=(",", ":")).encode()
        duplicate_digest = "sha256:" + hashlib.sha256(duplicate_body).hexdigest()
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            self.assertEqual("unknown", pipeline.process_index_notice(
                changed, duplicate_body, duplicate_digest, self.case)["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual("validate_candidate", pipeline.process_index_notice(
                changed, valid_body, valid_digest, self.case)["action"])
            self.assertEqual(1, state.count_decisions())

    def test_advisory_revision_reassesses_stable_digest_once(self):
        first, changed, _ = self.case["observations"]
        fix = next(r for r in self.case["bundle"]["records"]
                   if r["record_id"] == "advisory-expat")["data"]["fixed_source_version"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            pipeline.process(changed, self.case)
            self.assertEqual("already_satisfies_fix", pipeline.reassess_stable(
                self.case, "DSA-original", fix)["action"])
            self.assertEqual("duplicate", pipeline.reassess_stable(
                self.case, "DSA-original", fix)["status"])
            self.assertEqual("wait", pipeline.reassess_stable(
                self.case, "DSA-revised", "99:9999")["action"])
            self.assertEqual("unknown", pipeline.reassess_stable(
                self.case, "DSA-no-fix", None)["action"])
            self.assertEqual(2, state.count_reassessments())
            self.assertEqual(1, state.count_decisions())
        with State(self.db) as state:
            self.assertEqual(2, state.count_reassessments())
            self.assertEqual("duplicate", Pipeline(state).reassess_stable(
                self.case, "DSA-original", fix)["status"])

    def test_interrupted_commit_rolls_back_decision_and_observation(self):
        first, changed, _ = self.case["observations"]
        with State(self.db) as state:
            pipeline = Pipeline(state)
            pipeline.process(first, self.case)
            state.db.execute("""CREATE TRIGGER abort_observation BEFORE UPDATE ON observations
                BEGIN SELECT RAISE(ABORT, 'injected'); END""")
            result = pipeline.process(changed, self.case)
            self.assertEqual("unknown", result["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual(first["observation"]["platform_digest"],
                             state.get_observation(first["observation"])["platform_digest"])
            state.db.execute("DROP TRIGGER abort_observation")
        with State(self.db) as state:
            self.assertEqual("validate_candidate", Pipeline(state).process(changed, self.case)["action"])
            self.assertEqual(1, state.count_decisions())

    def test_unarchived_baseline_or_event_cannot_enter_fixture_state(self):
        first, changed, _ = self.case["observations"]
        forged_first = deepcopy(first)
        forged_first["observation"]["platform_digest"] = "sha256:" + "f" * 64
        with State(self.db) as state:
            pipeline = Pipeline(state)
            self.assertEqual("unknown", pipeline.process(forged_first, self.case)["action"])
            self.assertIsNone(state.get_observation(first["observation"]))
            pipeline.process(first, self.case)
            forged_change = deepcopy(changed)
            forged_change["event"]["event_id"] = "forged-new-id"
            self.assertEqual("unknown", pipeline.process(forged_change, self.case)["action"])
            self.assertEqual(0, state.count_decisions())


if __name__ == "__main__":
    unittest.main()
