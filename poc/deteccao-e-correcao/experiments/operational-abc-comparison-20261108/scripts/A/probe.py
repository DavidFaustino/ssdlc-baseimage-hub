#!/usr/bin/env python3
"""Reproducible local direct-OCI operational probe; output must be new or empty."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, resource, shutil, subprocess, sys, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen as real_urlopen

ROOT=Path(__file__).resolve().parents[4] if 'experiments' in Path(__file__).parts else Path.cwd()
OBS=ROOT/'experiments/oci-observation-20261108/observe.py'
FIX=ROOT/'experiments/tool-architecture-evaluation-20261108/evidence/A3-H2/replay'
I0=ROOT/'experiments/integrated-update-poc-20261108/evidence/I0-H1/manifest.json'
SHA=lambda b:'sha256:'+hashlib.sha256(b).hexdigest()
def save(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m;s.loader.exec_module(m);return m
obs=load(OBS,'operational_a_obs')
pre=(FIX/'01-pre/tag-index.json').read_bytes(); post=(FIX/'02-post/tag-index.json').read_bytes()
children={}
for v in ('01-pre','02-post'):
 b=(FIX/v/'platform-manifest.json').read_bytes();children[SHA(b)]=b
assert hashlib.sha256((FIX/'replay.json').read_bytes()).hexdigest()==json.loads(I0.read_text())['sources'][0]['sha256']

def aux_index(raw, kind):
 d=json.loads(raw); one=d['manifests'][0].copy();one['platform']={'os':'linux','architecture':'arm64'}
 if kind=='missing': d['manifests']=[]
 elif kind=='duplicate':d['manifests']=[one,one]
 else:d['manifests']=[one]
 return json.dumps(d,sort_keys=True,separators=(',',':')).encode()

class Server(ThreadingHTTPServer):
 daemon_threads=True
 def __init__(self):super().__init__(('127.0.0.1',0),Handler);self.mode='pre';self.fault=None;self.fault_left=0;self.logs=[];self.token='Basic dGVzdDp0ZXN0'
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.reply(head=True)
 def do_GET(self):self.reply(head=False)
 def reply(self,head=False):
  s=self.server; ref=self.path.rsplit('/',1)[-1];status=200;body=b'';headers={};fault=s.fault
  request_row={'method':'HEAD' if head else 'GET','path':self.path,'mode':s.mode,'fault':fault,'status':None,'body_bytes':None,'body_sha256':None};s.logs.append(request_row)
  if fault and s.fault_left>0:
   s.fault_left-=1
   if fault in ('401','403','429','503'):status=int(fault);headers={'Retry-After':'0'} if status==429 else {}
   elif fault=='timeout':time.sleep(.3);status=503
  if status==200 and s.mode in ('auth','auth-post') and self.headers.get('Authorization')!=s.token:status=401;headers={'WWW-Authenticate':'Basic realm="local-test"'}
  if status==200:
   if ref in ('local-replay','arm-control'):
    raw=pre if s.mode in ('pre','auth','index-only') else post
    if s.mode=='index-only':
     d=json.loads(raw);d['annotations']={'probe':'index-only'};raw=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
    body=raw if ref=='local-replay' else aux_index(raw,'normal');mime=obs.OCI_INDEX
   elif ref in ('missing','duplicate'):
    body=aux_index(pre,ref);mime=obs.OCI_INDEX
   elif ref in children:body=children[ref];mime=obs.OCI_MANIFEST
   else:status=404
   if status==200:headers.update({'Content-Type':mime,'Docker-Content-Digest':SHA(body),'Content-Length':str(len(body))})
  if fault=='truncated' and s.fault_left==0 and status==200 and ref=='local-replay':
   sent=body[:max(1,len(body)//2)];headers['Content-Length']=str(len(body))
  else:sent=body
  self.send_response(status)
  for k,v in headers.items():self.send_header(k,v)
  self.end_headers()
  if not head:
   try:self.wfile.write(sent)
   except (BrokenPipeError,ConnectionResetError):pass
  request_row.update({'status':status,'body_bytes':0 if head else len(sent),'body_sha256':SHA(sent)})
 def log_message(self,*a):pass

def child(args):
 port,tag,platform,out,auth,retries,timeout=args
 out=Path(out);obs.TAG=tag;obs.PLATFORM=platform;obs.IMAGE='fixture.local/distroless/java21-debian13';calls=[];request_timeout=timeout
 def loopback(req,timeout=15):
  url=f'http://127.0.0.1:{port}/v2/test/image/manifests/{tag if req.full_url.endswith("/"+tag) else req.full_url.rsplit("/",1)[-1]}'
  h={'Accept':req.get_header('Accept')}
  if auth!='none':h['Authorization']='Basic dGVzdDp0ZXN0' if auth=='valid' else 'Basic aW52YWxpZDppbnZhbGlk'
  local=Request(url,headers=h)
  for attempt in range(retries+1):
   start=time.perf_counter_ns()
   try:
    response=real_urlopen(local,timeout=float(request_timeout));calls.append({'url':url,'attempt':attempt,'status':response.status,'elapsed_ns':time.perf_counter_ns()-start});return response
   except HTTPError as e:
    calls.append({'url':url,'attempt':attempt,'status':e.code,'retry_after':e.headers.get('Retry-After'),'www_authenticate':e.headers.get('WWW-Authenticate'),'elapsed_ns':time.perf_counter_ns()-start})
    if attempt>=retries or e.code not in (429,503):raise
    time.sleep(min(float(e.headers.get('Retry-After') or 0),.1))
   except Exception as e:
    calls.append({'url':url,'attempt':attempt,'error':type(e).__name__,'elapsed_ns':time.perf_counter_ns()-start})
    if attempt>=retries:raise
  raise RuntimeError('unreachable')
 obs.urlopen=loopback
 start=time.perf_counter_ns();ru0=resource.getrusage(resource.RUSAGE_SELF);error=None;row=None;event=None
 try:row,event=obs.observe_live(out/'raw',out.parent/'state.json',out.parent/'events.jsonl')
 except Exception as e:error={'type':type(e).__name__,'message':str(e),'status':getattr(e,'code',None)}
 ru1=resource.getrusage(resource.RUSAGE_SELF)
 result={'tag':tag,'platform':platform,'elapsed_ns':time.perf_counter_ns()-start,'cpu_s':(ru1.ru_utime+ru1.ru_stime)-(ru0.ru_utime+ru0.ru_stime),'peak_rss_bytes':ru1.ru_maxrss,'calls':calls,'observation':row,'event':event,'error':error,'pid':os.getpid()}
 save(out/'result.json',result);print(json.dumps({'error':error,'event':bool(event)}));return 0

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.expanduser()
 if out.is_symlink() or (out.exists() and (not out.is_dir() or any(out.iterdir()))):ap.error('output must be new or empty and not a symlink')
 out.mkdir(parents=True,exist_ok=True)
 server=Server();thread=Thread(target=server.serve_forever,daemon=True);thread.start();runs=[]
 def run(name,mode='pre',tag='local-replay',platform='linux/amd64',fault=None,fault_count=0,auth=False,retries=0,timeout=.15,group='main'):
  server.mode=mode;server.fault=fault;server.fault_left=fault_count;start_logs=len(server.logs);where=out/group/name;where.mkdir(parents=True)
  state=out/group/'state.json';events=out/group/'events.jsonl'
  before={'state_sha256':SHA(state.read_bytes()) if state.exists() else None,'event_count':len(events.read_text().splitlines()) if events.exists() else 0}
  p=subprocess.run([sys.executable,__file__,'child',str(server.server_port),tag,platform,str(where),'valid' if auth is True else ('invalid' if auth=='invalid' else 'none'),str(retries),str(timeout)],capture_output=True,text=True,timeout=20)
  result=json.loads((where/'result.json').read_text());after={'state_sha256':SHA(state.read_bytes()) if state.exists() else None,'event_count':len(events.read_text().splitlines()) if events.exists() else 0}
  result.update({'baseline_before':before,'baseline_after':after,'action':'event' if result['event'] else ('error' if result['error'] else 'no_change'),'event_id':result['event']['event_id'] if result['event'] else None,'name':name,'mode':mode,'fault':fault,'process_returncode':p.returncode,'process_stdout':p.stdout,'process_stderr':p.stderr,'server_requests':server.logs[start_logs:],'disk_bytes':sum(x.stat().st_size for x in where.rglob('*') if x.is_file())});save(where/'metric.json',result);runs.append(result);return result
 try:
  for cycle in range(1,4):
   group=f'cycle-{cycle}'
   for name,mode in [('baseline','pre'),('changed','post'),('repeat','post')]:run(name,mode,group=group)
   ev=(out/group/'events.jsonl').read_text().splitlines();assert len(ev)==1
  # Aux control has a distinct tag/platform/state and no package proof.
  for name,mode in [('baseline','pre'),('changed','post'),('repeat','post')]:run(name,mode,'arm-control','linux/arm64',group='aux')
  for name in ('missing','duplicate'):run(name,'pre',name,'linux/arm64',group='identity')
  run('baseline','pre',group='index-only');run('index-change','index-only',group='index-only')
  run('baseline','pre',group='cross-tag');run('cross-tag','pre','arm-control','linux/arm64',group='cross-tag')
  run('cross-platform','pre','local-replay','linux/arm64',group='identity')
  for status in ('401','403','429','503','timeout','truncated'):
   run(status,'pre',fault=status,fault_count=1,group='faults')
  run('auth-denied','auth',group='auth');run('auth-invalid','auth',auth='invalid',group='auth');run('auth-granted','auth',auth=True,group='auth');run('403-valid-token','auth',fault='403',fault_count=1,auth=True,group='auth')
  run('429-retry','pre',fault='429',fault_count=1,retries=2,group='retry')
  run('503-retry','pre',fault='503',fault_count=1,retries=2,group='retry')
  run('429-exhaust','pre',fault='429',fault_count=10,retries=2,group='retry')
  run('503-exhaust','pre',fault='503',fault_count=10,retries=2,group='retry')
  # Restart after a missed poll: state remains pre until restarted observer sees post.
  run('before-stop','pre',group='recovery');run('after-restart','post',group='recovery');run('repeat-after-commit','post',group='recovery')
 finally:server.shutdown();server.server_close();thread.join()
 summary={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'source_paths':{'observer':str(OBS),'historical':str(FIX),'I0_manifest':str(I0)},'fixture_hashes':{'pre_index':SHA(pre),'post_index':SHA(post),'children':list(children)},'runs':[{k:v for k,v in r.items() if k not in ('observation','event','server_requests','calls')}|{'request_count':len(r['server_requests']),'body_bytes':sum(x['body_bytes'] for x in r['server_requests'] if x['body_bytes'] is not None),'event':bool(r['event']),'error':r['error']} for r in runs]}
 save(out/'summary.json',summary)
 all_files=[p for p in out.rglob('*') if p.is_file() and p.name!='hashes.json'];save(out/'hashes.json',{str(p.relative_to(out)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(all_files)})
 print(json.dumps({'output':str(out),'runs':len(runs),'cycles':3,'hashes':len(all_files)}))
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='child':sys.exit(child([sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7]),sys.argv[8]]))
 main()
