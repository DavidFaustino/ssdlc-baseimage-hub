"""A3-H1 isolated comparator harness; does not modify the existing correlator."""

import json
import re
from pathlib import Path

from debian.debian_support import Version


def classify(case):
    required = (
        "package_suite", "advisory_suite", "package_arch", "target_arch",
        "package_source", "advisory_source", "platform_digest", "fix_state",
        "source_version_basis", "installed", "fixed",
    )
    if any(key not in case or case[key] is None for key in required):
        return "unknown"
    if case["package_suite"] != case["advisory_suite"] or not case["package_suite"]:
        return "unknown"
    if case["package_arch"] != case["target_arch"] or not case["package_arch"]:
        return "unknown"
    if case["package_source"] != case["advisory_source"] or not case["package_source"]:
        return "unknown"
    if not isinstance(case["platform_digest"], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", case["platform_digest"]):
        return "unknown"
    if case["fix_state"] != "fixed_version_known":
        return "unknown"
    if not case["fixed"] or not case["installed"]:
        return "unknown"
    if case["source_version_basis"] == "debian_policy_same_as_binary":
        source_version = case["installed"]
    elif case["source_version_basis"] == "explicit_source_field":
        source_version = case.get("source_version")
    else:
        return "unknown"
    if not source_version:
        return "unknown"
    if not all(valid_debian_version(value) for value in (source_version, case["fixed"])):
        return "unknown"
    try:
        return "at_or_above_fix" if Version(source_version) >= Version(case["fixed"]) else "below_fix"
    except ValueError:
        return "unknown"


def valid_debian_version(value):
    """Validate Debian Policy shape; split upstream/revision at the LAST hyphen."""
    if not isinstance(value, str) or not value:
        return False
    if ":" in value:
        epoch, value = value.split(":", 1)
        if not epoch.isascii() or not epoch.isdecimal():
            return False
    if "-" in value:
        upstream, revision = value.rsplit("-", 1)
        return bool(re.fullmatch(r"[0-9][A-Za-z0-9.+~-]*", upstream) and re.fullmatch(r"[A-Za-z0-9.+~]+", revision))
    return bool(re.fullmatch(r"[0-9][A-Za-z0-9.+~]*", value))


if __name__ == "__main__":
    cases = json.loads(Path(__file__).with_name("version-cases.json").read_text())
    fixture_context = {
        "package_suite": "trixie", "advisory_suite": "trixie",
        "package_arch": "amd64", "target_arch": "amd64",
        "package_source": "expat", "advisory_source": "expat",
        "platform_digest": "sha256:" + "1" * 64,
        "fix_state": "fixed_version_known",
        "source_version_basis": "debian_policy_same_as_binary",
    }
    failed = 0
    for case in cases:
        candidate = {**fixture_context, **{k: v for k, v in case.items() if k not in ("id", "expected", "omit_fields")}}
        for field in case.get("omit_fields", []):
            candidate.pop(field, None)
        result = classify(candidate)
        success = result == case["expected"]
        print(f"{'PASS' if success else 'FAIL'} {case['id']}: {result} (expected {case['expected']})")
        failed += not success
    print(f"RESULT: {len(cases) - failed}/{len(cases)} passed")
    raise SystemExit(1 if failed else 0)
