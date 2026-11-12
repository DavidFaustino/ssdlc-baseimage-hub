"""Fetch every archived-manifest layer and reconstruct selected final paths.

This is a targeted OCI changeset replay, not a materialized complete rootfs.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import tarfile
import tempfile
from urllib.request import Request, urlopen


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[3]
HIST = EXPERIMENTS / "historical-image-case-20261107" / "evidence" / "digests"
CACHE = Path(os.environ.get("BASE_IMAGE_BLOB_CACHE", Path(tempfile.gettempdir()) / "base-image-hub-a4-full-blobs"))
REFRESH = os.environ.get("A4_REFRESH") == "1"
TARGETS = ("etc/os-release", "usr/lib/os-release", "var/lib/dpkg/status.d/base-files")
MANIFESTS = {label: json.loads((HIST / f"{label}-manifest.json").read_text())
             for label in ("pre", "post")}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def check_file(path: Path, digest: str, size: int) -> bool:
    return path.is_file() and path.stat().st_size == size and sha256(path.read_bytes()) == digest


def fetch_one(item: tuple[str, int]) -> dict:
    digest, size = item
    path = CACHE / digest.split(":", 1)[1]
    if not REFRESH and check_file(path, digest, size):
        return {"digest": digest, "size": size, "source": "verified_temp_cache"}
    for source in (HERE / "source" / "base-files-layer.blob",
                   HIST / "pre-layer.blob", HIST / "post-layer.blob"):
        if check_file(source, digest, size):
            path.write_bytes(source.read_bytes())
            return {"digest": digest, "size": size, "source": str(source)}
    url = f"https://gcr.io/v2/distroless/java21-debian13/blobs/{digest}"
    with urlopen(Request(url, headers={"Accept": "application/octet-stream"}), timeout=45) as response:
        body = response.read()
        http_status = response.status
    if len(body) != size or sha256(body) != digest:
        raise ValueError(f"download digest/size mismatch: {digest}")
    with tempfile.NamedTemporaryFile(dir=CACHE, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return {"digest": digest, "size": size, "source": url, "http_status": http_status}


def normalized(name: str) -> str:
    path = name.removeprefix("./").rstrip("/")
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe tar path: {name}")
    return str(pure)


def invalidated(target: str, members: dict[str, tarfile.TarInfo]) -> list[str]:
    parts = target.split("/")
    reasons = []
    # A whiteout on the file or any ancestor removes lower-layer content.
    for count in range(1, len(parts) + 1):
        parent = "/".join(parts[:count - 1])
        name = f"{parent + '/' if parent else ''}.wh.{parts[count - 1]}"
        if name in members:
            reasons.append(name)
    # Opaque ancestor directories hide all lower-layer descendants.
    for count in range(1, len(parts)):
        directory = "/".join(parts[:count])
        opaque = f"{directory}/.wh..wh..opq"
        if opaque in members:
            reasons.append(opaque)
        ancestor = members.get(directory)
        if ancestor is not None and not ancestor.isdir():
            raise ValueError(f"tracked ancestor replaced by non-directory: {directory}")
    return reasons


def replay(label: str) -> dict:
    states: dict[str, dict | None] = {target: None for target in TARGETS}
    transitions = []
    layers = MANIFESTS[label]["layers"]
    for index, descriptor in enumerate(layers):
        assert descriptor["mediaType"] == "application/vnd.oci.image.layer.v1.tar+gzip"
        blob = CACHE / descriptor["digest"].split(":", 1)[1]
        assert check_file(blob, descriptor["digest"], descriptor["size"])
        with tarfile.open(blob, "r:gz") as archive:
            entries = archive.getmembers()
            names = [normalized(member.name) for member in entries]
            if len(names) != len(set(names)):
                raise ValueError(f"duplicate tar path in layer {index}")
            members = dict(zip(names, entries))
            for target in TARGETS:
                removed_by = invalidated(target, members)
                if removed_by:
                    states[target] = None
                    transitions.append({"layer": index, "digest": descriptor["digest"],
                                        "path": target, "operation": "removed", "by": removed_by})
                member = members.get(target)
                if member is None:
                    continue
                if member.isfile():
                    data = archive.extractfile(member).read()
                    states[target] = {"kind": "file", "sha256": sha256(data), "bytes": len(data),
                                      "text": data.decode("utf-8", errors="replace")}
                elif member.issym():
                    states[target] = {"kind": "symlink", "linkname": member.linkname}
                else:
                    raise ValueError(f"unsupported target type {target} in layer {index}")
                transitions.append({"layer": index, "digest": descriptor["digest"],
                                    "path": target, "operation": states[target]["kind"]})
    link = states["etc/os-release"]
    assert link and link["kind"] == "symlink"
    resolved = posixpath.normpath(posixpath.join("etc", link["linkname"]))
    assert resolved == "usr/lib/os-release"
    os_release = states[resolved]
    base_files = states["var/lib/dpkg/status.d/base-files"]
    assert os_release and os_release["kind"] == "file"
    assert base_files and base_files["kind"] == "file"
    suite_checks = {
        "os_release_id_debian": 'ID="debian"' in os_release["text"],
        "os_release_version_13": 'VERSION_ID="13"' in os_release["text"],
        "os_release_trixie": 'VERSION="Debian GNU/Linux 13 (trixie)"' in os_release["text"],
        "base_files_package": "Package: base-files" in base_files["text"],
        "base_files_amd64": "Architecture: amd64" in base_files["text"],
    }
    assert all(suite_checks.values())
    return {"label": label, "layers_verified": len(layers), "tracked_paths": states,
            "etc_os_release_resolves_to": resolved, "transitions": transitions,
            "suite_checks": suite_checks, "targeted_replay_only": True}


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    unique = {}
    for manifest in MANIFESTS.values():
        for layer in manifest["layers"]:
            prior = unique.setdefault(layer["digest"], layer["size"])
            assert prior == layer["size"]
    ledger, failures = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_one, item): item[0] for item in unique.items()}
        for future in as_completed(futures):
            try:
                ledger.append(future.result())
            except Exception as error:
                failures.append({"digest": futures[future], "error": repr(error)})
    output = {"unique_layers": len(unique), "total_compressed_bytes": sum(unique.values()),
              "downloads": sorted(ledger, key=lambda item: item["digest"]), "failures": failures,
              "cache": str(CACHE), "cache_is_transient": True, "refresh_requested": REFRESH}
    if not failures:
        output["replay"] = [replay(label) for label in ("pre", "post")]
    (HERE / "full-suite-replay.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    if failures:
        raise SystemExit(f"PARTIAL: {len(failures)} layer downloads failed")
    print(f"PASS {len(unique)} unique layer hashes; targeted final path replay pre/post; bytes={sum(unique.values())}; suite_checks=true")


if __name__ == "__main__":
    main()
