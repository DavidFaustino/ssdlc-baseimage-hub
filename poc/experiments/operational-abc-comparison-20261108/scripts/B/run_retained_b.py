"""Run real Diun against A3-H2's byte-identical historical OCI replay on loopback."""
from __future__ import annotations
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread
from time import perf_counter

HUB = Path(__file__).resolve().parents[4]
A3 = HUB / 'experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/replay'
HIST = HUB / 'experiments/historical-image-case-20261107/evidence/digests'
CAPTURE = HUB / 'experiments/tool-architecture-evaluation-20261108/evidence/A1-H2/capture-local.py'
DIUN = Path(os.environ.get('DIUN_BIN', 'diun'))
OCI_INDEX = 'application/vnd.oci.image.index.v1+json'
OCI_MANIFEST = 'application/vnd.oci.image.manifest.v1+json'
OCI_CONFIG = 'application/vnd.oci.image.config.v1+json'

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
out = args.output_dir.resolve()
if out.exists():
    parser.error('output directory must be new')
out.mkdir(parents=True)

artifacts = {}
indexes = {}
children = {}
for mode, folder in (('pre','01-pre'),('post','02-post')):
    index = (A3/folder/'tag-index.json').read_bytes()
    child = (A3/folder/'platform-manifest.json').read_bytes()
    config = (HIST/f'{mode}-config.blob').read_bytes()
    idx_obj = json.loads(index)
    child_obj = json.loads(child)
    idx_digest = 'sha256:' + hashlib.sha256(index).hexdigest()
    child_digest = 'sha256:' + hashlib.sha256(child).hexdigest()
    cfg_digest = 'sha256:' + hashlib.sha256(config).hexdigest()
    assert len(idx_obj['manifests']) == 1
    assert idx_obj['manifests'][0]['digest'] == child_digest
    assert idx_obj['manifests'][0]['size'] == len(child)
    assert idx_obj['manifests'][0]['platform'] == {'os':'linux','architecture':'amd64'}
    assert child_obj['config']['digest'] == cfg_digest
    assert child_obj['config']['size'] == len(config)
    artifacts[mode] = {idx_digest:(index,OCI_INDEX),child_digest:(child,OCI_MANIFEST),cfg_digest:(config,OCI_CONFIG)}
    indexes[mode] = idx_digest
    children[mode] = child_digest
(out/'which.txt').write_text('pre\n')
requests = []
class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.respond(True)
    def do_HEAD(self): self.respond(False)
    def respond(self, body_enabled):
        mode = (out/'which.txt').read_text().strip()
        if self.path in ('/v2','/v2/'):
            self.send_response(200); self.send_header('Content-Length','0'); self.end_headers()
            requests.append({'mode':mode,'method':self.command,'path':self.path,'status':200,'body_bytes':0})
            return
        prefix = '/v2/test/image/'
        ref = self.path.rsplit('/',1)[-1]
        if self.path.startswith(prefix+'manifests/') and ref == 'local-replay': ref = indexes[mode]
        artifact = artifacts[mode].get(ref)
        if artifact and body_enabled:
            served = out/'served'/mode
            served.mkdir(parents=True, exist_ok=True)
            (served/(ref.replace(':','_')+'.bin')).write_bytes(artifact[0])
        status = 200 if artifact else 404
        body = artifact[0] if artifact else b''
        requests.append({'mode':mode,'method':self.command,'path':self.path,'status':status,'body_bytes':len(body) if body_enabled else 0})
        if not artifact:
            self.send_error(404); return
        self.send_response(200)
        self.send_header('Content-Type',artifact[1])
        self.send_header('Docker-Content-Digest','sha256:'+hashlib.sha256(body).hexdigest())
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        if body_enabled: self.wfile.write(body)
    def log_message(self,*args): pass
server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread = Thread(target=server.serve_forever,daemon=True);thread.start()
host = f'127.0.0.1:{server.server_port}'
(out/'images.yml').write_text(f'- name: {host}/test/image:local-replay\n  regopt: local\n  platform:\n    os: linux\n    arch: amd64\n')
(out/'diun.yml').write_text(f'db:\n  path: {out}/diun.db\nwatch:\n  workers: 1\n  firstCheckNotif: false\n  compareDigest: true\nproviders:\n  file:\n    filename: {out}/images.yml\nregopts:\n  - name: local\n    insecureTLS: true\nnotif:\n  script:\n    cmd: {sys.executable}\n    args:\n      - {CAPTURE}\n')
rows=[]
try:
    for step,mode in (('baseline','pre'),('changed','post'),('repeat_after_restart','post')):
        (out/'which.txt').write_text(mode+'\n')
        before_req=len(requests)
        db_file=out/'diun.db'
        db_before=('sha256:'+hashlib.sha256(db_file.read_bytes()).hexdigest()) if db_file.exists() else None
        capture=out/'notifications.jsonl'
        before_notice=len(capture.read_text().splitlines()) if capture.exists() else 0
        env=os.environ.copy();env['DIUN_CAPTURE_PATH']=str(capture)
        start=perf_counter()
        run=subprocess.run([str(DIUN),'serve','--config',str(out/'diun.yml'),'--log-json'],cwd=out,env=env,text=True,capture_output=True,timeout=40)
        duration=round((perf_counter()-start)*1000,3)
        (out/f'diun-{step}.jsonl').write_text(run.stdout+run.stderr)
        job=next((json.loads(line) for line in run.stdout.splitlines() if '"message":"Jobs completed"' in line),{})
        req=requests[before_req:]
        after_notice=len(capture.read_text().splitlines()) if capture.exists() else 0
        db_after=('sha256:'+hashlib.sha256(db_file.read_bytes()).hexdigest()) if db_file.exists() else None
        rows.append({'baseline_before':{'diun_db_sha256':db_before},'baseline_after':{'diun_db_sha256':db_after},'action':('event' if after_notice-before_notice else 'no_change'),'step':step,'mode':mode,'exit_code':run.returncode,'duration_ms':duration,'requests':req,'request_count':len(req),'body_bytes':sum(x['body_bytes'] for x in req),'notifications_delta':after_notice-before_notice,'job':{k:job.get(k) for k in ('added','updated','unchanged','failed')}})
finally:
    server.shutdown();server.server_close();thread.join(timeout=5)
result={'fixture':'A3-H2 exact index/child bytes and historical config blobs','indexes':indexes,'children':children,'rows':rows,'notifications':len((out/'notifications.jsonl').read_text().splitlines()) if (out/'notifications.jsonl').exists() else 0}
(out/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
canonical='fixture.local/distroless/java21-debian13:local-replay'
receipt={'canonical_image':canonical,'observed_registry_image':f'{host}/test/image:local-replay',
         'platform':'linux/amd64','indexes':indexes,'children':children,
         'cases':[{k:r[k] for k in ('step','mode','action','baseline_before','baseline_after','notifications_delta','job')}
                  for r in rows],
         'raw_notice':'notifications.jsonl','served_bodies':{
             mode:{'index':'served/'+mode+'/'+indexes[mode].replace(':','_')+'.bin',
                   'child':'served/'+mode+'/'+children[mode].replace(':','_')+'.bin'}
             for mode in ('pre','post')}}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
assert [r['exit_code'] for r in rows] == [0,0,0]
assert [r['notifications_delta'] for r in rows] == [0,1,0]
assert [r['job'] for r in rows] == [
    {'added':1,'updated':0,'unchanged':0,'failed':0},
    {'added':0,'updated':1,'unchanged':0,'failed':0},
    {'added':0,'updated':0,'unchanged':1,'failed':0}]
print(json.dumps({'output':str(out),'indexes':indexes,'children':children,'notifications':result['notifications']}))
