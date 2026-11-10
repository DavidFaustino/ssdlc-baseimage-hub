"""Verify retained public OCI, package and advisory evidence without network access."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import tarfile
import tempfile

from .pipeline import DIGEST

CVE = 'CVE-2026-24515'
DSA = 'DSA-6404-1'
INDEX_TYPE = 'application/vnd.oci.image.index.v1+json'
CHILD_TYPE = 'application/vnd.oci.image.manifest.v1+json'
LAYER_TYPE = 'application/vnd.oci.image.layer.v1.tar+gzip'
CAPTURED = {
    'observation': 'sha256:fbb56d50aaaf4826725d46db9008ad598b089fc0e3a368082edc3a7147c66d9b',
    'index': 'sha256:b22857e939bd95abd69d9d747f0421a274f9f70855ecfc335f7d97f6eeef578d',
    'child': 'sha256:0749f5f7461a573740f1fefe4775b6419467e986e7b36929888295f7205c6849',
    'A_result': 'sha256:471c7c66a5243dc4dd73aca4299a3b27487db95ddd3c29a860ab242acbe4dce4',
    'B_result': 'sha256:2b51f9bde6b365d952b5f8a3cb0d124c93a9c8b7012bd255b73f64e744444ea7',
    'package_status': 'sha256:1a332bef6dc36bea908193809c1c63164fb4c307cf26bcc9c280db9a608b86b8',
    'prior_feed': 'sha256:96b3a207fb07548e4cff08c5d7cbdd600a1c1818a42dba933f8fd2e0459400b1',
    'current_feed': 'sha256:c1ef0b8d711362e6a1bf2da00b6de36546e5dfaf68028bd4f5a22ebf82f44775',
    'vunnel_db': 'sha256:0bbde7d2ea0a33cd400df6fa03350cd77afd5046f880ebb9d3bf8e0246e7c205',
}


def _bytes(path: Path, expected: str | None = None) -> tuple[bytes, str]:
    try:
        body = path.read_bytes()
    except OSError as error:
        raise ValueError(f'raw evidence unavailable: {path}') from error
    digest = 'sha256:' + hashlib.sha256(body).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError(f'raw evidence hash differs: {path}')
    return body, digest


def _json(path: Path, expected: str | None = None) -> tuple[dict, str]:
    body, digest = _bytes(path, expected)
    return json.loads(body), digest


def _dsa(feed: bytes) -> dict:
    lines = feed.decode('utf-8').splitlines()
    for i, line in enumerate(lines):
        if line.startswith('[30 Jul 2026] DSA-6404-1 expat - '):
            block = lines[i:i+3]
            if len(block) == 3 and CVE in block[1] and block[2].startswith('\t[trixie] - expat '):
                return {'cve': CVE, 'dsa': DSA, 'source': 'expat', 'suite': 'trixie',
                        'fixed_source_version': block[2].split('expat ', 1)[1], 'source_lines': block}
    raise ValueError('selected DSA/CVE/suite missing from raw feed')


def _fields(body: bytes) -> dict:
    result = {}
    for line in body.decode('utf-8').splitlines():
        if line and not line[0].isspace() and ': ' in line:
            k, v = line.split(': ', 1)
            result[k] = v
    return result


def package_from_status(body: bytes) -> dict:
    status = _fields(body)
    if (status.get('Package'), status.get('Source'), status.get('Architecture')) != (
            'libexpat1', 'expat', 'amd64') or not status.get('Version'):
        raise ValueError('libexpat1 raw package identity differs')
    return {'binary': 'libexpat1', 'binary_version': status['Version'], 'source': 'expat',
            'source_version': status['Version'], 'source_version_basis': 'debian_policy_same_as_binary',
            'suite': 'trixie', 'architecture': 'amd64'}


def _extract_targets(blobs: Path, layers: list) -> dict:
    wanted = {'usr/lib/os-release', 'var/lib/dpkg/status.d/base-files',
              'var/lib/dpkg/status.d/libexpat1'}
    found = {}
    for layer in layers:
        with tarfile.open(blobs / layer['digest'][7:], 'r:gz') as archive:
            for member in archive:
                name = member.name.lstrip('./')
                if name in wanted and member.isfile():
                    found[name] = archive.extractfile(member).read()
    if set(found) != wanted:
        raise ValueError('package or suite files absent from verified layers')
    return found


def load_public_case(evidence_root: Path, route: str, feed_revision: str) -> dict:
    """Return a normalized, byte-verified captured public case for A or B."""
    root = Path(evidence_root)
    if route not in ('A', 'B') or feed_revision not in ('prior-I4-H1', 'current-A'):
        raise ValueError('unsupported route or feed revision')
    ev = root / 'evidence'
    a = ev / 'A/public-20261108'
    base = a if route == 'A' else ev / 'B/operational-b-public-v2-20261108'
    inspection = a / 'inspection' if route == 'A' else ev / 'B/operational-b-public-inspection-20261108'
    index_file = base / ('observation/tag-index.json' if route == 'A' else 'tag-index.json')
    child_file = base / ('observation/platform-manifest.json' if route == 'A' else 'platform-manifest.json')
    observation, observation_hash = _json(a / 'observation/observation.json')
    binding, _ = _json(a / 'binding.json')
    if observation_hash != CAPTURED['observation'] or observation_hash[7:] != binding['observation_sha256']:
        raise ValueError('observation binding differs')
    index, index_hash = _json(index_file, observation['index_digest'])
    child_bytes, child_hash = _bytes(child_file, observation['platform_digest'])
    child = json.loads(child_bytes)
    if index_hash != CAPTURED['index'] or child_hash != CAPTURED['child']:
        raise ValueError('public OCI digest differs from captured evidence')
    if (observation['image'], observation['tag'], observation['platform']) != (
            'gcr.io/distroless/java21-debian13', 'nonroot', 'linux/amd64'):
        raise ValueError('public image identity differs')
    if (observation['index_media_type'], observation['platform_media_type'],
            index.get('mediaType'), child.get('mediaType')) != (INDEX_TYPE, CHILD_TYPE, INDEX_TYPE, CHILD_TYPE):
        raise ValueError('OCI media type differs')
    selected = [x for x in index['manifests'] if x.get('platform') == {'os': 'linux', 'architecture': 'amd64'}]
    if len(selected) != 1 or selected[0] != {'mediaType': CHILD_TYPE, 'digest': child_hash,
                                             'size': len(child_bytes), 'platform': {'os': 'linux', 'architecture': 'amd64'}}:
        raise ValueError('OCI child descriptor differs')
    layers = child['layers']
    if len(layers) != 34:
        raise ValueError('unexpected layer count')
    for layer in layers:
        if layer['mediaType'] != LAYER_TYPE or not DIGEST.fullmatch(layer['digest']):
            raise ValueError('layer descriptor differs')
        blob = inspection / 'blobs' / layer['digest'][7:]
        if blob.stat().st_size != layer['size']:
            raise ValueError('layer size differs')
        _bytes(blob, layer['digest'])
    files = _extract_targets(inspection / 'blobs', layers)
    package = package_from_status(files['var/lib/dpkg/status.d/libexpat1'])
    status_hash = 'sha256:' + hashlib.sha256(files['var/lib/dpkg/status.d/libexpat1']).hexdigest()
    if status_hash != CAPTURED['package_status']:
        raise ValueError('package status differs from captured evidence')
    base_status = _fields(files['var/lib/dpkg/status.d/base-files'])
    os_release = {key: value.strip('"') for key, value in (
        line.split('=', 1) for line in files['usr/lib/os-release'].decode().splitlines() if '=' in line)}
    if (base_status.get('Package'), base_status.get('Architecture'),
            os_release.get('ID'), os_release.get('VERSION_ID')) != (
            'base-files', 'amd64', 'debian', '13') or 'trixie' not in os_release.get('VERSION', ''):
        raise ValueError('package or suite raw files differ')
    result, result_hash = _json(inspection / 'result.json')
    if result_hash != CAPTURED[f'{route}_result']:
        raise ValueError('inspection differs from captured evidence')
    if (result['package'] != {k: package[k] for k in ('binary','binary_version','source','source_version','source_version_basis')}
            or result['platform_digest'] != child_hash or result['index_digest'] != index_hash
            or result['layers_verified'] != len(layers) or not all(result['suite_checks'].values())):
        raise ValueError('inspection result differs from raw layers')
    if route == 'A':
        if result_hash[7:] != binding['image_result_sha256'] or binding['package'] != result['package']:
            raise ValueError('A package binding differs')
    else:
        b_binding, _ = _json(ev / 'B/public-binding.json')
        diun_receipt, diun_hash = _json(base / 'receipt.json')
        rows = diun_receipt.get('rows', [])
        if (diun_receipt.get('tag') != 'gcr.io/distroless/java21-debian13:nonroot'
                or diun_receipt.get('platform') != 'linux/amd64'
                or diun_receipt.get('index_digest') != index_hash
                or diun_receipt.get('child_digest') != child_hash
                or diun_receipt.get('index_bytes') != index_file.stat().st_size
                or diun_receipt.get('child_bytes') != len(child_bytes)
                or diun_receipt.get('index_http_status') != 200
                or diun_receipt.get('child_http_status') != 200
                or diun_receipt.get('notice_count') != 0
                or len(rows) != 2
                or [(row.get('step'), row.get('exit_code'), row.get('job')) for row in rows] != [
                    ('baseline', 0, {'added': 1, 'failed': 0, 'unchanged': 0, 'updated': 0}),
                    ('repeat', 0, {'added': 0, 'failed': 0, 'unchanged': 1, 'updated': 0})]):
            raise ValueError('B Diun stable observation receipt differs')
        raw_status, raw_hash = _bytes(ev / 'B/operational-b-public-libexpat1-status.raw', b_binding['package_raw_status_sha256'])
        if (b_binding['child_digest'] != child_hash or b_binding['index_digest'] != index_hash
                or b_binding['package_result_sha256'] != result_hash or raw_status != files['var/lib/dpkg/status.d/libexpat1']
                or b_binding['package'] != result['package']):
            raise ValueError('B package/OCI binding differs')
    feed_path = (root.parent / 'integrated-update-poc-20261108/evidence/I4-H1/feed-expat-trixie.raw'
                 if feed_revision == 'prior-I4-H1' else
                 ev / ('A/feed-20261108/feed.raw' if route == 'A' else 'B/operational-b-feed-20261108.raw'))
    feed, feed_hash = _bytes(feed_path)
    if feed_hash != CAPTURED['prior_feed' if feed_revision == 'prior-I4-H1' else 'current_feed']:
        raise ValueError('feed differs from captured evidence')
    if feed_revision == 'current-A' and feed_hash != 'sha256:' + binding['feed_sha256']:
        raise ValueError('public captured feed hash differs')
    advisory = _dsa(feed)
    if route == 'B':
        selected_data, _ = _json(ev / 'B/operational-b-selected-20261108.json')
        source_feed, source_hash = _bytes(ev / 'B/operational-b-feed-20261108.raw')
        row, row_hash = _json(ev / 'B/operational-b-selected-record.raw')
        row_proof, _ = _json(ev / 'B/operational-b-vunnel-row-proof.json')
        if (source_hash != feed_hash
                or source_hash != CAPTURED['current_feed']
                or source_hash != b_binding['feed_sha256']
                or selected_data['full_source_files']['DSA'] != {'bytes': len(source_feed), 'sha256': source_hash}
                or selected_data['full_source_files']['results.db']['sha256'] != CAPTURED['vunnel_db']
                or row_proof['sqlite_db_sha256'] != CAPTURED['vunnel_db']):
            raise ValueError('B raw DSA/Vunnel source binding differs')
        archive = ev / 'B/operational-b-vunnel-results-20261108.db.zst'
        with tempfile.TemporaryDirectory(prefix='public-vunnel-') as temp_dir:
            db_path = Path(temp_dir) / 'results.db'
            try:
                with db_path.open('wb') as stream:
                    subprocess.run(['zstd', '-d', '-c', str(archive.resolve())], stdout=stream,
                                   stderr=subprocess.PIPE, check=True)
            except (OSError, subprocess.CalledProcessError) as error:
                raise ValueError('retained Vunnel database unavailable or corrupt') from error
            _bytes(db_path, row_proof['sqlite_db_sha256'])
            if db_path.stat().st_size != selected_data['full_source_files']['results.db']['bytes']:
                raise ValueError('B Vunnel database size differs')
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            try:
                database_row = conn.execute(row_proof['query'], (row_proof['parameter'],)).fetchone()
            finally:
                conn.close()
            if database_row is None or database_row[0] != (ev / 'B/operational-b-selected-record.raw').read_bytes():
                raise ValueError('Vunnel row differs from retained results database')
        vunnel = selected_data['selected_records'][CVE]['vunnel']
        fixes = [f for f in row['item']['Vulnerability']['FixedIn'] if f.get('Name') == 'expat' and f.get('NamespaceName') == 'debian:13']
        if (row != vunnel or row_hash != row_proof['raw_record_sha256'] or len(fixes) != 1
                or fixes[0]['Version'] != advisory['fixed_source_version'] or fixes[0]['VersionFormat'] != 'dpkg'
                or fixes[0]['Available']['Kind'] != 'advisory'
                or fixes[0]['VendorAdvisory']['AdvisorySummary'][0]['ID'] != DSA
                or selected_data['dsa_lines'] != advisory['source_lines']):
            raise ValueError('Vunnel row and raw DSA differ')
    return {'evidence_root': str(root.resolve()), 'route': route, 'observation': observation, 'package': package, 'advisory': advisory,
            'feed_revision': feed_revision, 'feed_sha256': feed_hash,
            'proof': {'verified': True, 'index_sha256': index_hash, 'child_sha256': child_hash,
                      'package_result_sha256': result_hash, 'package_status_sha256': status_hash,
                      'layers_verified': len(layers), 'observation_sha256': observation_hash,
                      'vunnel_row_sha256': row_hash if route == 'B' else None,
                      'diun_receipt_sha256': diun_hash if route == 'B' else None}}
