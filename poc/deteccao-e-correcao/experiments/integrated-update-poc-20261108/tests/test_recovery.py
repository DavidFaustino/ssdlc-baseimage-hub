"""Recover exported receipts after SQLite committed but JSON export was interrupted."""

import json
from pathlib import Path
import tempfile
import unittest

from src.inputs import load_archived_case
from src.pipeline import Pipeline
from src.state import State
from run_local import recover_receipts


class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name)
        self.case = load_archived_case()
        first, changed, repeated = self.case["observations"]
        with State(self.output / "state.sqlite") as state:
            pipe = Pipeline(state)
            self.assertEqual("baseline", pipe.process(first, self.case)["status"])
            self.assertEqual("decided", pipe.process(changed, self.case)["status"])
            self.assertEqual("unchanged", pipe.process(repeated, self.case)["status"])
            advisory = next(r for r in self.case["bundle"]["records"]
                            if r["record_id"] == "advisory-expat")
            result = pipe.reassess_stable(self.case, advisory["data"]["advisory_id"],
                                          advisory["data"]["fixed_source_version"])
            self.assertEqual("reassessed", result["status"])

    def tearDown(self):
        self.temp.cleanup()

    def test_after_commit_recovers_missing_and_partial_json_without_new_decision(self):
        (self.output / "receipt.json").write_text('{"status":')
        before = (self.output / "state.sqlite").read_bytes()
        recover_receipts(self.output, self.case)
        self.assertEqual("decided", json.loads((self.output / "receipt.json").read_text())["status"])
        self.assertEqual("reassessed", json.loads((self.output / "advisory-receipt.json").read_text())["status"])
        self.assertEqual(1, json.loads((self.output / "run.json").read_text())["decision_count"])
        self.assertEqual('{"status":', (self.output / "receipt.json.corrupt").read_text())
        self.assertEqual(before, (self.output / "state.sqlite").read_bytes())
        recover_receipts(self.output, self.case)
        with State(self.output / "state.sqlite") as state:
            self.assertEqual(1, state.count_decisions())
            self.assertEqual(1, state.count_reassessments())

    def test_conflicting_valid_receipt_is_never_overwritten(self):
        conflicting = {"status": "decided", "action": "wait"}
        (self.output / "receipt.json").write_text(json.dumps(conflicting))
        with self.assertRaisesRegex(ValueError, "conflicting receipt"):
            recover_receipts(self.output, self.case)
        self.assertEqual(conflicting, json.loads((self.output / "receipt.json").read_text()))

    def test_unrelated_state_is_rejected(self):
        with State(self.output / "state.sqlite") as state:
            state.db.execute("UPDATE decisions SET receipt_json=?", ('{"status":"decided"}',))
            state.db.commit()
        with self.assertRaisesRegex(ValueError, "state does not match archived fixture"):
            recover_receipts(self.output, self.case)
        self.assertFalse((self.output / "receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
