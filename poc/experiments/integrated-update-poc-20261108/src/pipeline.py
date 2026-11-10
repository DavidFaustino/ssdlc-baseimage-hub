"""Bind producer event to verified archived package and a durable local receipt."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import tarfile

from .state import State


HUB = Path(__file__).resolve().parents[3]
CONSUMER_PATH = HUB / "experiments/tool-architecture-evaluation-20261108/evidence/A3-H4/consumer-contract.py"
SPEC = importlib.util.spec_from_file_location("a3h4_consumer", CONSUMER_PATH)
CONSUMER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONSUMER)
OCI_SPEC = importlib.util.spec_from_file_location(
    "oci_observer", HUB / "experiments/oci-observation-20261108/observe.py")
OCI = importlib.util.module_from_spec(OCI_SPEC)
OCI_SPEC.loader.exec_module(OCI)
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


class Pipeline:
    def __init__(self, state: State):
        self.state = state

    def unknown(self, reason: str) -> dict:
        self.state.record_failure(reason)
        return {"status": "unknown", "action": "unknown", "reason": reason,
                "image_approved": False}

    def _verified_public(self, public_case: dict) -> dict:
        """Recheck retained bytes so callers cannot alter a loader result before policy."""
        from .public_inputs import load_public_case
        if not isinstance(public_case, dict):
            raise ValueError('public case missing')
        verified = load_public_case(Path(public_case['evidence_root']), public_case['route'],
                                    public_case['feed_revision'])
        if verified != public_case:
            raise ValueError('public case differs from verified evidence')
        return verified

    @staticmethod
    def _public_evidence(case: dict) -> dict:
        return {'route': case['route'], 'platform_digest': case['observation']['platform_digest'],
                'feed_sha256': case['feed_sha256'],
                'package_result_sha256': case['proof']['package_result_sha256'],
                'package_status_sha256': case['proof']['package_status_sha256'],
                'diun_receipt_sha256': case['proof']['diun_receipt_sha256'],
                'vunnel_row_sha256': case['proof']['vunnel_row_sha256'],
                'image_approved': False}

    def process_public_stable(self, public_case: dict, event: dict | None = None) -> dict:
        """Admit a verified stable public observation; never create an image decision."""
        try:
            if event is not None:
                return self.unknown('public stable digest has no verified image event')
            case = self._verified_public(public_case)
            obs = case['observation']
            prior = self.state.get_observation(obs)
            if prior is None:
                self.state.set_observation(obs)
                return {'status': 'baseline', 'action': 'none', **self._public_evidence(case)}
            if prior['platform_digest'] != obs['platform_digest'] or prior['index_digest'] != obs['index_digest']:
                return self.unknown('public digest changed without verified image event')
            return {'status': 'unchanged', 'action': 'none', **self._public_evidence(case)}
        except (AttributeError, IndexError, KeyError, TypeError, ValueError, OSError,
                sqlite3.Error, tarfile.TarError) as error:
            return self.unknown(f'invalid public observation: {error}')

    def reassess_public_stable(self, public_case: dict) -> dict:
        """Reassess one raw DSA revision for an admitted public child digest."""
        try:
            case = self._verified_public(public_case)
            obs, package, advisory = case['observation'], case['package'], case['advisory']
            prior = self.state.get_observation(obs)
            if prior is None or prior['platform_digest'] != obs['platform_digest'] or prior['index_digest'] != obs['index_digest']:
                return self.unknown('stable public digest not present in state')
            comparison = CONSUMER.COMPARATOR.classify({
                'package_suite': package['suite'], 'advisory_suite': advisory['suite'],
                'package_arch': package['architecture'], 'target_arch': 'amd64',
                'package_source': package['source'], 'advisory_source': advisory['source'],
                'platform_digest': obs['platform_digest'], 'fix_state': 'fixed_version_known',
                'source_version_basis': package['source_version_basis'],
                'installed': package['binary_version'], 'source_version': package['source_version'],
                'fixed': advisory['fixed_source_version']})
            if comparison == 'unknown':
                return self.unknown('public package/advisory comparison unknown')
            identity = {'image': obs['image'], 'tag': obs['tag'], 'platform': obs['platform'],
                        'digest': obs['platform_digest'], 'cve': advisory['cve'], 'dsa': advisory['dsa'],
                        'feed_sha256': case['feed_sha256'], 'fixed': advisory['fixed_source_version']}
            revision_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            if self.state.get_reassessment(revision_key) is not None:
                return {'status': 'duplicate', 'action': 'none', 'revision_key': revision_key,
                        **self._public_evidence(case)}
            action = 'already_satisfies_fix' if comparison == 'at_or_above_fix' else 'wait'
            receipt = {'status': 'reassessed', 'action': action, 'comparison': comparison,
                       'revision_key': revision_key, **self._public_evidence(case),
                       'revision': case['feed_revision'], 'feed_sha256': case['feed_sha256'],
                       'cve': advisory['cve'], 'dsa': advisory['dsa'], 'source_package': package['source'],
                       'suite': package['suite'], 'fixed_source_version': advisory['fixed_source_version'],
                       'installed_source_version': package['source_version'],
                       'platform_digest': obs['platform_digest'],
                       'package_result_sha256': case['proof']['package_result_sha256'],
                       'package_status_sha256': case['proof']['package_status_sha256'],
                       'vunnel_row_sha256': case['proof']['vunnel_row_sha256'], 'image_approved': False}
            return self.state.commit_reassessment(revision_key, obs['platform_digest'], receipt)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError, OSError,
                sqlite3.Error, tarfile.TarError) as error:
            return self.unknown(f'invalid public reassessment: {error}')

    def process_index_notice(self, item: dict, index_body: bytes,
                             notified_index_digest: str, case: dict) -> dict:
        """A Diun index update is only a hint; resolve exactly one child first."""
        try:
            observation = item["observation"]
            selected = OCI.select_platform(index_body, observation["index_media_type"],
                                           notified_index_digest, observation["platform"])
            if (observation["index_digest"] != notified_index_digest or
                    observation["platform_digest"] != selected["platform_digest"]):
                return self.unknown("Diun notice and OCI child differ")
        except (KeyError, TypeError, ValueError) as error:
            return self.unknown(f"OCI child resolution failed: {error}")
        return self.process(item, case)

    def reassess_stable(self, case: dict, revision: str, fixed_version: str | None) -> dict:
        """Reevaluate the archived post digest without inventing a new image event."""
        try:
            if not revision or fixed_version is None:
                return self.unknown("advisory revision or fix missing")
            observation = case["observations"][1]["observation"]
            current = self.state.get_observation(observation)
            if current is None or current["platform_digest"] != observation["platform_digest"]:
                return self.unknown("stable digest not present in state")
            bundle = case["bundle"]
            CONSUMER.validate_bundle(bundle)
            package = CONSUMER.record_by_id(bundle, "pkg-post")
            advisory = CONSUMER.record_by_id(bundle, "advisory-expat")
            p, a = package["data"], advisory["data"]
            if p["platform_digest"] != current["platform_digest"] or p["suite"] != a["suite"] or p["source_package"] != a["source_package"]:
                return self.unknown("advisory and package identity differ")
            CONSUMER.require_raw_package_binding(package)
            CONSUMER.require_suite_proof(case["proof"], p["platform_digest"], p["suite"])
            revision_key = hashlib.sha256(json.dumps({"revision": revision,
                "digest": p["platform_digest"], "fixed_version": fixed_version,
                "fixture_manifest_sha256": case["manifest_sha256"]}, sort_keys=True).encode()).hexdigest()
            if self.state.get_reassessment(revision_key):
                return {"status": "duplicate", "action": "none", "image_approved": False}
            comparison = CONSUMER.COMPARATOR.classify({
                "package_suite": p["suite"], "advisory_suite": a["suite"],
                "package_arch": p["architecture"], "target_arch": "amd64",
                "package_source": p["source_package"], "advisory_source": a["source_package"],
                "platform_digest": p["platform_digest"], "fix_state": "fixed_version_known",
                "source_version_basis": p["source_version_basis"],
                "installed": p["binary_version"], "source_version": p["source_version"],
                "fixed": fixed_version})
            if comparison == "unknown":
                return self.unknown("invalid revised fix version")
            action = "already_satisfies_fix" if comparison == "at_or_above_fix" else "wait"
            return self.state.commit_reassessment(revision_key, p["platform_digest"], {
                "status": "reassessed", "action": action, "comparison": comparison,
                "revision": revision, "platform_digest": p["platform_digest"],
                "fixed_source_version": fixed_version, "image_approved": False,
                "scope": "local_fixture", "fixture_manifest_sha256": case["manifest_sha256"]})
        except (KeyError, TypeError, ValueError, OSError, IndexError) as error:
            return self.unknown(f"invalid advisory reassessment: {error}")

    def process(self, item: dict | None, case: dict) -> dict:
        if item is None:
            return self.unknown("producer unavailable")
        if not isinstance(item, dict):
            return self.unknown("invalid producer envelope")
        if "error" in item:
            if not isinstance(item["error"], dict):
                return self.unknown("invalid producer error envelope")
            status = item["error"].get("http_status", "unknown")
            return self.unknown(f"producer HTTP {status}")
        try:
            obs, event = item["observation"], item["event"]
            if obs["image"] != "fixture.local/distroless/java21-debian13" or obs["tag"] != "local-replay":
                return self.unknown("not the archived local fixture")
            if obs["platform"] != "linux/amd64" or not all(
                    DIGEST.fullmatch(obs[field]) for field in ("platform_digest", "index_digest")):
                return self.unknown("invalid platform or digest")
            if obs not in [entry["observation"] for entry in case["observations"]]:
                return self.unknown("observation not in verified archived fixture")
            if event is not None and event != case["observations"][1]["event"]:
                return self.unknown("event not in verified archived fixture")
            prior = self.state.get_observation(obs)
            if event is None:
                if prior is None:
                    self.state.set_observation(obs)
                    return {"status": "baseline", "action": "none", "image_approved": False}
                if prior["platform_digest"] == obs["platform_digest"]:
                    return {"status": "unchanged", "action": "none", "image_approved": False}
                return self.unknown("changed digest without producer event")
            if prior is None:
                return self.unknown("event before baseline")
            previous_receipt = self.state.get_decision(event["event_id"])
            if previous_receipt:
                if (previous_receipt["image"] == obs["image"] and
                        previous_receipt["tag"] == obs["tag"] and
                        previous_receipt["platform"] == obs["platform"] and
                        previous_receipt["previous_digest"] == event["previous_digest"] and
                        previous_receipt["candidate_digest"] == event["candidate_digest"] and
                        previous_receipt["fixture_manifest_sha256"] == case["manifest_sha256"] and
                        previous_receipt["source_ledger_sha256"] == case["proof"]["source_ledger_sha256"]):
                    return {"status": "duplicate", "action": "none", "image_approved": False}
                return self.unknown("event id reused with different payload or evidence")
            if (event["previous_digest"] != prior["platform_digest"] or
                    event["candidate_digest"] != obs["platform_digest"] or
                    event["image"] != obs["image"] or event["tag"] != obs["tag"] or
                    event["platform"] != obs["platform"]):
                return self.unknown("event and baseline relation broken")
            result = CONSUMER.decide(case["bundle"], event, case["proof"])
            if result["action"] not in ("wait", "validate_candidate"):
                return self.unknown(result["reason"])
            return self.state.commit_decision(obs, event, result, case)
        except (KeyError, TypeError, ValueError, sqlite3.Error) as error:
            return self.unknown(f"invalid producer record: {error}")
