"""Adapter parity over archived, verified inputs only."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.adapters import normalize_vunnel_fix, process_diun_hint
from src.inputs import load_archived_case
from src.pipeline import Pipeline
from src.state import State


HUB = Path(__file__).resolve().parents[3]
EVIDENCE = HUB / "experiments/tool-architecture-evaluation-20261108/evidence"
POST_INDEX = EVIDENCE / "A3-H2/replay/02-post/tag-index.json"
POST_CHILD = EVIDENCE / "A3-H2/replay/02-post/platform-manifest.json"
DIUN_CAPTURE = EVIDENCE / "A1-H2/local-notifications.jsonl"
VUNNEL_SNAPSHOT = EVIDENCE / "A2-H2/selected-records.json"
FIXTURE_IMAGE = "fixture.local/distroless/java21-debian13"


class AdapterParityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "state.sqlite"
        self.case = load_archived_case()
        self.first, self.changed, self.repeated = self.case["observations"]
        self.index_body = POST_INDEX.read_bytes()
        self.child_body = POST_CHILD.read_bytes()
        self.notice = {
            "DIUN_ENTRY_STATUS": "update",
            "DIUN_ENTRY_IMAGE": FIXTURE_IMAGE + ":local-replay",
            "DIUN_ENTRY_PLATFORM": "linux/amd64",
            "DIUN_ENTRY_MIMETYPE": "application/vnd.oci.image.index.v1+json",
            "DIUN_ENTRY_DIGEST": "sha256:" + hashlib.sha256(self.index_body).hexdigest(),
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_archived_diun_schema_is_basis_for_synthetic_notice(self):
        archived = [json.loads(line) for line in DIUN_CAPTURE.read_text().splitlines()]
        update = next(row for row in archived if row["DIUN_ENTRY_STATUS"] == "update")
        self.assertTrue(set(self.notice).issubset(update))
        self.assertEqual("application/vnd.oci.image.index.v1+json", update["DIUN_ENTRY_MIMETYPE"])
        self.assertEqual("linux/amd64", update["DIUN_ENTRY_PLATFORM"])
        self.assertNotEqual(update["DIUN_ENTRY_DIGEST"], self.notice["DIUN_ENTRY_DIGEST"])

    def test_direct_diun_direct_same_state_one_decision_even_after_restart(self):
        with State(self.db) as state:
            p = Pipeline(state)
            self.assertEqual("baseline", p.process(self.first, self.case)["status"])
            self.assertEqual("validate_candidate", process_diun_hint(
                p, self.notice, self.changed, self.index_body, self.child_body, self.case,
                expected_image=FIXTURE_IMAGE)["action"])
            self.assertEqual("duplicate", p.process(self.changed, self.case)["status"])
            self.assertEqual("unchanged", p.process(self.repeated, self.case)["status"])
            self.assertEqual(1, state.count_decisions())
        with State(self.db) as state:
            self.assertEqual("duplicate", Pipeline(state).process(self.changed, self.case)["status"])
            self.assertEqual(1, state.count_decisions())

    def test_lost_diun_notice_direct_poll_recovers_without_duplication(self):
        with State(self.db) as state:
            p = Pipeline(state)
            p.process(self.first, self.case)
            # Deliberately omit the Diun notification; a direct OCI poll sees
            # the archived change. A late hint must be idempotent.
            self.assertEqual("validate_candidate", p.process(self.changed, self.case)["action"])
            self.assertEqual("duplicate", process_diun_hint(
                p, self.notice, self.changed, self.index_body, self.child_body, self.case,
                expected_image=FIXTURE_IMAGE)["status"])
            self.assertEqual(1, state.count_decisions())

    def test_diun_hint_bad_digest_or_ambiguous_child_fails_closed(self):
        with State(self.db) as state:
            p = Pipeline(state)
            p.process(self.first, self.case)
            forged = deepcopy(self.notice)
            forged["DIUN_ENTRY_DIGEST"] = "sha256:" + "0" * 64
            self.assertEqual("unknown", process_diun_hint(
                p, forged, self.changed, self.index_body, self.child_body, self.case,
                expected_image=FIXTURE_IMAGE)["action"])
            duplicate = json.loads(self.index_body)
            target = next(row for row in duplicate["manifests"]
                          if row.get("platform", {}).get("architecture") == "amd64")
            duplicate["manifests"].append(target)
            body = json.dumps(duplicate, separators=(",", ":")).encode()
            forged["DIUN_ENTRY_DIGEST"] = "sha256:" + hashlib.sha256(body).hexdigest()
            self.assertEqual("unknown", process_diun_hint(
                p, forged, self.changed, body, self.child_body, self.case,
                expected_image=FIXTURE_IMAGE)["action"])
            self.assertEqual(0, state.count_decisions())
            self.assertEqual(self.first["observation"]["platform_digest"],
                             state.get_observation(self.first["observation"])["platform_digest"])

    def test_archived_vunnel_fix_matches_debian_case_and_rejects_divergence(self):
        snapshot = json.loads(VUNNEL_SNAPSHOT.read_text())
        fix = normalize_vunnel_fix(snapshot, "CVE-2026-24515", self.case)
        self.assertEqual("2.8.2-1~deb13u1", fix["fixed_source_version"])
        self.assertEqual("archived_fixture", fix["scope"])
        divergent = deepcopy(snapshot)
        row = divergent["selected_records"]["CVE-2026-24515"]["vunnel"]["item"]["Vulnerability"]["FixedIn"][0]
        row["Version"] = "2.8.3-1~deb13u1"
        with self.assertRaisesRegex(ValueError, "diverges"):
            normalize_vunnel_fix(divergent, "CVE-2026-24515", self.case)
        stale = deepcopy(snapshot)
        stale["provider_metadata"]["stale"] = True
        with self.assertRaisesRegex(ValueError, "stale"):
            normalize_vunnel_fix(stale, "CVE-2026-24515", self.case)


if __name__ == "__main__":
    unittest.main()
