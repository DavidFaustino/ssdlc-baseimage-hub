"""Single-writer SQLite state and append-only decision receipts."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3


class State:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.db: sqlite3.Connection | None = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS observations (
              image TEXT NOT NULL, tag TEXT NOT NULL, platform TEXT NOT NULL,
              platform_digest TEXT NOT NULL, index_digest TEXT NOT NULL,
              observed_at TEXT NOT NULL,
              PRIMARY KEY (image, tag, platform));
            CREATE TABLE IF NOT EXISTS decisions (
              event_id TEXT PRIMARY KEY, image TEXT NOT NULL, tag TEXT NOT NULL,
              platform TEXT NOT NULL, previous_digest TEXT NOT NULL,
              candidate_digest TEXT NOT NULL, action TEXT NOT NULL,
              receipt_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS failures (
              id INTEGER PRIMARY KEY AUTOINCREMENT, reason TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reassessments (
              revision_key TEXT PRIMARY KEY, digest TEXT NOT NULL,
              action TEXT NOT NULL, receipt_json TEXT NOT NULL);
        """)
        return self

    def __exit__(self, *_):
        self.db.close()

    @staticmethod
    def key(obs: dict) -> tuple[str, str, str]:
        return obs["image"], obs["tag"], obs["platform"]

    def get_observation(self, obs: dict) -> dict | None:
        row = self.db.execute(
            "SELECT platform_digest, index_digest, observed_at FROM observations WHERE image=? AND tag=? AND platform=?",
            self.key(obs)).fetchone()
        return dict(zip(("platform_digest", "index_digest", "observed_at"), row)) if row else None

    def set_observation(self, obs: dict):
        with self.db:
            self.db.execute("""INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)
              ON CONFLICT(image, tag, platform) DO UPDATE SET
              platform_digest=excluded.platform_digest,
              index_digest=excluded.index_digest,
              observed_at=excluded.observed_at""",
              (*self.key(obs), obs["platform_digest"], obs["index_digest"], obs["observed_at_utc"]))

    def get_decision(self, event_id: str) -> dict | None:
        row = self.db.execute("SELECT receipt_json FROM decisions WHERE event_id=?", (event_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def count_decisions(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]

    def count_reassessments(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM reassessments").fetchone()[0]

    def get_reassessment(self, revision_key: str) -> dict | None:
        row = self.db.execute("SELECT receipt_json FROM reassessments WHERE revision_key=?",
                              (revision_key,)).fetchone()
        return json.loads(row[0]) if row else None

    def commit_reassessment(self, revision_key: str, digest: str, receipt: dict) -> dict:
        with self.db:
            self.db.execute("INSERT INTO reassessments VALUES (?, ?, ?, ?)",
                            (revision_key, digest, receipt["action"], json.dumps(receipt, sort_keys=True)))
        return receipt

    def record_failure(self, reason: str):
        with self.db:
            self.db.execute("INSERT INTO failures(reason) VALUES (?)", (reason,))

    def commit_decision(self, obs: dict, event: dict, result: dict, case: dict) -> dict:
        receipt = {"status": "decided", "action": result["action"],
                   "comparison": result["comparison"], "image_approved": False,
                   "event_id": event["event_id"], "image": obs["image"], "tag": obs["tag"],
                   "platform": obs["platform"], "previous_digest": event["previous_digest"],
                   "candidate_digest": event["candidate_digest"],
                   "observed_at_utc": obs["observed_at_utc"], "scope": "local_fixture",
                   "fixture_manifest_sha256": case["manifest_sha256"],
                   "source_ledger_sha256": case["proof"]["source_ledger_sha256"]}
        with self.db:
            self.db.execute("INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (event["event_id"], *self.key(obs), event["previous_digest"],
                             event["candidate_digest"], result["action"], json.dumps(receipt, sort_keys=True)))
            self.db.execute("""UPDATE observations SET platform_digest=?, index_digest=?, observed_at=?
              WHERE image=? AND tag=? AND platform=?""",
              (obs["platform_digest"], obs["index_digest"], obs["observed_at_utc"], *self.key(obs)))
        return receipt
