#!/usr/bin/env python3
"""Measure fresh Vunnel Debian provider acquisition and warm selected-CVE lookup."""
import argparse,hashlib,json,os,resource,sqlite3,subprocess,tempfile,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.exists():p.error('output must be new')
out.mkdir(parents=True)
root=out/'workspace'
config=out/'vunnel.yaml'
config.write_text(f'''root: {root}\nlog:\n  level: INFO\nproviders:\n  debian:\n    runtime:\n      existing_input: keep\n      existing_results: delete-before-write\n      on_error:\n        action: fail\n        input: keep\n        results: keep\n        retry_count: 1\n        retry_delay: 2\n''')
env=os.environ.copy();env['UV_CACHE_DIR']=os.environ.get('UV_CACHE_DIR',str(Path(tempfile.gettempdir())/'vunnel-uv-cache'))
ru0=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.perf_counter_ns()
run=subprocess.run(['uv','run','--no-project','--python','3.13','--with','vunnel==0.66.0','vunnel','-c',str(config),'run','debian'],env=env,text=True,capture_output=True,timeout=180)
wall_ns=time.perf_counter_ns()-start;ru1=resource.getrusage(resource.RUSAGE_CHILDREN)
(out/'vunnel.log').write_text(run.stdout+run.stderr)
if run.returncode:p.error(f'Vunnel failed with exit {run.returncode}; see log')
raw=root/'debian/input/debian.json';dsa=root/'debian/input/DSA';db=root/'debian/results/results.db'
sha=lambda path:'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
meta=json.loads((root/'debian/metadata.json').read_text())
lookup=[]
for i in range(3):
 t=time.perf_counter_ns();r0=resource.getrusage(resource.RUSAGE_SELF)
 conn=sqlite3.connect(f'file:{db}?mode=ro',uri=True)
 row=conn.execute('select record from results where id=?',('debian:13/cve-2026-24515',)).fetchone()
 conn.close();record=json.loads(row[0]);elapsed=time.perf_counter_ns()-t;r1=resource.getrusage(resource.RUSAGE_SELF)
 lookup.append({'wall_ns':elapsed,'cpu_s':(r1.ru_utime+r1.ru_stime)-(r0.ru_utime+r0.ru_stime),'record_sha256':'sha256:'+hashlib.sha256(row[0] if isinstance(row[0],bytes) else row[0].encode()).hexdigest(),'fixed_source_version':record['item']['Vulnerability']['FixedIn'][0]['Version']})
receipt={'provider':'vunnel@0.66.0/debian','scope':'fresh full provider refresh: Debian tracker JSON + DSA + fix-date source, processing all records; uv warm package cache','workspace':str(root),'exit_code':run.returncode,'wall_ns':wall_ns,'cpu_child_s':(ru1.ru_utime+ru1.ru_stime)-(ru0.ru_utime+ru0.ru_stime),'peak_rss_child_bytes':ru1.ru_maxrss,'workspace_bytes':sum(x.stat().st_size for x in root.rglob('*') if x.is_file()),'metadata':meta,'input':{'debian.json':{'bytes':raw.stat().st_size,'sha256':sha(raw)},'DSA':{'bytes':dsa.stat().st_size,'sha256':sha(dsa)},'results.db':{'bytes':db.stat().st_size,'sha256':sha(db)}},'lookup':lookup,'cache':'provider workspace fresh per run; uv/Python package cache warm; HTTP CDN cache and host filesystem cache uncontrolled'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'output':str(out),'wall_s':round(wall_ns/1e9,3),'dsa_sha256':receipt['input']['DSA']['sha256'],'records':meta.get('listing')}))
