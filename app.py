#!/usr/bin/env python3
"""Local web dashboard for the safe H4CK-B0T assessment pipeline."""

import json
from datetime import datetime
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from modules import correlation, discovery, evidence, report, risk, scanner, validation
from run import load_config
from utils.logger import setup_logger
from utils.safety import is_authorized_target, is_denylisted, normalize_target, validate_target

RESULTS = ROOT / "results"
SCAN_LOCK = threading.Lock()
ASSESSMENT_PROGRESS_LOCK = threading.Lock()
ASSESSMENT_PROGRESS = {"run_id": None, "stage": None, "status": "idle"}


def _set_assessment_progress(run_id, stage, status):
    with ASSESSMENT_PROGRESS_LOCK:
        ASSESSMENT_PROGRESS.update({"run_id": run_id, "stage": stage, "status": status})


def _assessment_progress_snapshot():
    with ASSESSMENT_PROGRESS_LOCK:
        return dict(ASSESSMENT_PROGRESS)


def _mark_assessment_failed(run_id):
    with ASSESSMENT_PROGRESS_LOCK:
        if ASSESSMENT_PROGRESS.get("run_id") == run_id:
            ASSESSMENT_PROGRESS["status"] = "failed"


def read_json(name, default=None):
    try:
        with (RESULTS / name).open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return default


def run_assessment(target, run_id=None):
    run_id = run_id or uuid.uuid4().hex
    current_stage = "Authorization"
    _set_assessment_progress(run_id, current_stage, "running")
    try:
        config = load_config()
        if not config.get("safe_mode", True):
            raise ValueError("Safe mode is disabled. Enable safe mode before running an assessment.")
        target = validate_target(target, config)
        if not is_authorized_target(target, config):
            raise ValueError("Add this exact URL to the authorized targets list before assessing it.")
        if is_denylisted(target, config):
            raise ValueError("This target is on the denylist.")

        logger = setup_logger(config)
        audit = logger.audit_logger
        audit.info("Dashboard assessment started for target %s", target)
        current_stage = "Discovery"
        _set_assessment_progress(run_id, current_stage, "running")
        discovery_data = discovery.run_discovery(target, config, logger)
        endpoints = [item for item in discovery_data.get("discovered_endpoints", []) if item.get("url")]

        current_stage = "Header scan"
        _set_assessment_progress(run_id, current_stage, "running")
        scan_data = scanner.run_scan(endpoints or [target], config, logger)

        current_stage = "Validation"
        _set_assessment_progress(run_id, current_stage, "running")
        validation_data = validation.run_validation(scan_data, config, logger)

        current_stage = "Evidence"
        _set_assessment_progress(run_id, current_stage, "running")
        evidence_data = evidence.collect_evidence(discovery_data, scan_data, validation_data, config, logger)

        current_stage = "Risk scoring"
        _set_assessment_progress(run_id, current_stage, "running")
        risk_data = risk.calculate_risk(validation_data, config, logger)

        current_stage = "Correlation"
        _set_assessment_progress(run_id, current_stage, "running")
        correlation_data = correlation.correlate_findings(discovery_data, validation_data, risk_data, config, logger)

        current_stage = "Report"
        _set_assessment_progress(run_id, current_stage, "running")
        report_data = report.generate_report(target, discovery_data, scan_data, validation_data, evidence_data, risk_data, correlation_data, config, logger)
        audit.info("Dashboard assessment completed for target %s", target)
        _set_assessment_progress(run_id, current_stage, "completed")
        return report_data
    except Exception:
        _set_assessment_progress(run_id, current_stage, "failed")
        raise


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0a0e13"><title>H4CK-B0T | Security Validation</title>
<style>
:root{color-scheme:dark;--bg:#0a0e13;--panel:#101720;--panel2:#141e28;--line:#263440;--muted:#8a9aa8;--text:#e7edf2;--mint:#59e1b0;--amber:#f0bd67;--red:#f27c77;--blue:#8db9ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 85% -10%,#18332c 0,transparent 38%),var(--bg);color:var(--text);font:14px 'DM Sans',sans-serif;min-height:100vh}.shell{max-width:1220px;margin:auto;padding:34px 38px 56px}.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:22px}.brand{display:flex;gap:13px;align-items:center}.mark{width:38px;height:38px;border:1px solid #34715f;border-radius:12px;display:grid;place-items:center;color:var(--mint);font:500 15px 'DM Mono';background:#10231f}.brand strong{display:block;letter-spacing:.08em;font-size:13px}.brand small{display:block;color:var(--muted);margin-top:3px}.live{color:var(--mint);font:11px 'DM Mono';letter-spacing:.1em}.live:before{content:'';display:inline-block;width:7px;height:7px;background:var(--mint);border-radius:50%;margin-right:8px;box-shadow:0 0 12px #59e1b077}.hero{padding:33px 0 27px;display:flex;justify-content:space-between;align-items:end;gap:30px}.eyebrow{font:11px 'DM Mono';letter-spacing:.16em;text-transform:uppercase;color:var(--mint)}h1{font-size:31px;letter-spacing:-.04em;margin:9px 0 8px} .hero p{color:var(--muted);margin:0;max-width:580px;line-height:1.6}.safe{border:1px solid #315b50;color:#a1e8cf;padding:9px 12px;border-radius:9px;font-size:12px;white-space:nowrap}.layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(290px,.85fr);gap:18px}.card{background:linear-gradient(145deg,#111922,#0e151d);border:1px solid var(--line);border-radius:14px;padding:21px}.cardhead{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.cardhead h2{font-size:14px;margin:0;letter-spacing:.01em}.subtle{color:var(--muted);font-size:12px}.label{display:block;color:#aebbc5;font-size:12px;margin:0 0 8px}.row{display:flex;gap:10px}input[type=url],input[type=text]{width:100%;background:#0a1118;border:1px solid #32414d;border-radius:9px;padding:12px 13px;color:var(--text);font:13px 'DM Mono';outline:none}input:focus{border-color:#55c89f;box-shadow:0 0 0 3px #59e1b018}button{font:600 13px 'DM Sans';cursor:pointer;border:0;border-radius:9px;padding:0 17px;background:var(--mint);color:#07140f;white-space:nowrap}button:hover{filter:brightness(1.07)}button:disabled{opacity:.55;cursor:wait}.authorize{margin:12px 0 0;display:flex;align-items:center;gap:9px;color:var(--muted);font-size:12px}.authorize input{accent-color:var(--mint)}.notice{margin-top:16px;padding:11px 13px;border-radius:9px;background:#171f27;border:1px solid #263440;color:#aab8c2;font-size:12px;line-height:1.55}.notice b{color:#e2ebef;font-weight:600}.section-title{margin:24px 0 11px;display:flex;justify-content:space-between;align-items:center}.section-title h3{margin:0;font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:#aebbc5}.target-list{display:flex;flex-direction:column;gap:8px}.target{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 11px;background:#0b1218;border:1px solid #202d37;border-radius:8px;font:12px 'DM Mono';overflow-wrap:anywhere}.target .url{color:#c9d5dc}.target .tag{color:var(--mint);font:10px 'DM Sans';white-space:nowrap}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.metric{padding:13px;background:#0b1218;border:1px solid #202d37;border-radius:10px}.metric span{display:block;color:var(--muted);font-size:11px}.metric strong{display:block;font:22px 'DM Mono';margin-top:8px}.metric strong.warn{color:var(--amber)}.metric strong.good{color:var(--mint)}.empty{border:1px dashed #2a3944;border-radius:10px;padding:28px;text-align:center;color:var(--muted);line-height:1.6}.empty .icon{font-size:22px;margin-bottom:7px;color:#658273}.findings{display:flex;flex-direction:column;gap:8px}.finding{padding:12px;background:#0c141a;border:1px solid #263440;border-radius:9px}.findingtop{display:flex;justify-content:space-between;gap:12px;align-items:center}.finding strong{font-size:12px}.pill{font:10px 'DM Mono';border-radius:20px;padding:5px 8px;color:var(--amber);background:#322919}.pill.low{color:var(--blue);background:#19283d}.finding small{display:block;color:var(--muted);margin-top:8px;overflow-wrap:anywhere}.finding p{font-size:12px;line-height:1.5;color:#aab8c2;margin:8px 0 0}.foot{display:flex;justify-content:space-between;margin-top:21px;color:#71818c;font:10px 'DM Mono';letter-spacing:.05em}.status{margin-top:13px;font-size:12px;line-height:1.5;color:var(--muted);min-height:17px}.status.error{color:var(--red)}.spinner{display:inline-block;width:12px;height:12px;border:2px solid #35594e;border-top-color:var(--mint);border-radius:50%;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:7px}@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:820px){.shell{padding:22px 17px 40px}.layout{grid-template-columns:1fr}.hero{align-items:start;flex-direction:column}h1{font-size:27px}}@media(max-width:470px){.row{flex-direction:column}.row button{height:42px}.metrics{gap:6px}.metric{padding:10px}.metric strong{font-size:18px}}
</style></head><body><main class="shell"><header class="top"><div class="brand"><div class="mark">H:B</div><div><strong>H4CK-B0T</strong><small>Autonomous Security Validation</small></div></div><div class="live">LOCAL INSTANCE</div></header>
<section class="hero"><div><div class="eyebrow">Defensive assessment console</div><h1>Know your security posture.</h1><p>Run a careful review of HTTP security headers on targets you have explicitly authorized. Every request stays within the approved host scope.</p></div><div class="safe">◈ &nbsp;Safe mode required</div></section>
<div class="layout"><section><div class="card"><div class="cardhead"><h2>Start an assessment</h2><span class="subtle">Observation only</span></div><label class="label" for="target">Authorized target URL</label><div class="row"><input id="target" type="url" placeholder="https://your-domain.example" autocomplete="url"><button id="scan">Run assessment&nbsp; ↗</button></div><label class="authorize"><input id="confirm" type="checkbox"><span>I confirm I’m authorized to assess this target.</span></label><div class="notice"><b>Scope guard is active.</b> Only URLs already on your local authorization list can be assessed. The scanner checks response headers and cookie attributes; it does not exploit, alter, or submit data to the target.</div><div id="status" class="status"></div><div class="section-title"><h3>Authorized targets</h3><span id="target-count" class="subtle"></span></div><div id="targets" class="target-list"></div></div>
<div class="section-title"><h3>Latest assessment</h3><span id="last-run" class="subtle">No run yet</span></div><div class="card"><div id="metrics" class="metrics"></div><div class="section-title"><h3>Findings</h3><span id="finding-count" class="subtle"></span></div><div id="findings" class="findings"></div><div class="section-title"><h3>Unvalidated endpoints</h3></div><div id="unvalidated" class="target-list"></div><div class="section-title"><h3>Prioritized endpoints</h3></div><div id="prioritized" class="target-list"></div></div></section>
<aside><div class="card"><div class="cardhead"><h2>Assessment flow</h2><span class="subtle">7 stages</span></div><div id="stages"></div></div><div class="card" style="margin-top:16px"><div class="cardhead"><h2>Operating principles</h2></div><div style="display:grid;gap:14px"><div><div class="eyebrow" style="font-size:10px">01 / Authorization</div><div class="subtle" style="margin-top:5px;line-height:1.5">Allowlist and denylist checks run before any target request.</div></div><div><div class="eyebrow" style="font-size:10px">02 / Scope</div><div class="subtle" style="margin-top:5px;line-height:1.5">Discovery and redirects are restricted to the approved host and port.</div></div><div><div class="eyebrow" style="font-size:10px">03 / Evidence</div><div class="subtle" style="margin-top:5px;line-height:1.5">Observations remain clearly labeled; missing headers are not called confirmed vulnerabilities.</div></div><div><div class="eyebrow" style="font-size:10px">04 / Audit trail</div><div class="subtle" style="margin-top:5px;line-height:1.5">Assessment actions are recorded in the local audit log.</div></div></div></div></aside></div><footer class="foot"><span>H4CK-B0T / SAFE MODE</span><span>LOCAL DASHBOARD · RESULTS STORED ON THIS MACHINE</span></footer></main>
<script>
const stages=['Discovery','Header scan','Validation','Evidence','Risk scoring','Correlation','Report'];
const $=s=>document.querySelector(s);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
$('#stages').innerHTML=stages.map((s,i)=>`<div style="display:flex;gap:12px;align-items:center;padding:10px 0;border-bottom:${i===stages.length-1?'0':'1px solid #202d37'}"><span style="font:11px 'DM Mono';color:#59e1b0;width:20px">0${i+1}</span><span style="font-size:12px">${s}</span><span style="margin-left:auto;color:#60717d;font-size:11px">${i===0?'scope-aware':'→'}</span></div>`).join('');
function findingsList(r){const items=r?.risk?.risk_levels||{};return [...(items.critical||[]).map(x=>({...x,_level:'Critical'})),...(items.high||[]).map(x=>({...x,_level:'High'})),...(items.medium||[]).map(x=>({...x,_level:'Medium'})),...(items.low||[]).map(x=>({...x,_level:'Low'}))]}
function render(r,targets,lastRun){$('#target-count').textContent=`${targets.length} configured`;$('#targets').innerHTML=targets.length?targets.map(t=>`<div class="target"><span class="url">${esc(t)}</span><span class="tag">AUTHORIZED</span></div>`).join(''):'<div class="empty">No authorized targets are configured.<br>Update <code>config/config.yaml</code> to add an explicitly approved URL.</div>';if(!r){$('#metrics').innerHTML='<div class="empty" style="grid-column:1/-1">Your latest assessment summary will appear here.</div>';$('#findings').innerHTML='<div class="empty">No assessment has been run yet.</div>';$('#unvalidated').innerHTML='';$('#prioritized').innerHTML='';$('#finding-count').textContent='';return}const risks=r.risk?.risk_levels||{};const all=findingsList(r);const open=all.filter(f=>f['Validation status']==='Potential Finding');const evidenceEntries=Array.isArray(r?.evidence?.finding_evidence)?r.evidence.finding_evidence:[];const evidenceMapByFinding=new Map();for(const item of evidenceEntries){if(!item||typeof item!=='object')continue;const key=`${item.endpoint||''}|${item.finding_name||''}`;evidenceMapByFinding.set(key,true)}const level=(risks.high||[]).length?'HIGH':(risks.medium||[]).length?'MEDIUM':'LOW';const unvalidated=Array.isArray(r.validation?.unvalidated_endpoints)?r.validation.unvalidated_endpoints:[];const prioritized=Array.isArray(r.summary?.prioritized_endpoints)?r.summary.prioritized_endpoints:[];$('#metrics').innerHTML=`<div class="metric"><span>Reachable endpoints</span><strong>${Number(r.discovery?.reachable_endpoints||0)}</strong></div><div class="metric"><span>Potential findings</span><strong class="${open.length?'warn':'good'}">${open.length}</strong></div><div class="metric"><span>Risk level</span><strong class="${open.length?'warn':'good'}">${level}</strong><small style="display:block;color:#9fb3bf;font-size:10px;letter-spacing:.06em;text-transform:uppercase;margin-top:6px">Provisional risk</small></div>`;$('#last-run').textContent=`${lastRun||'Latest saved report'} · ${esc(r.target||'')}`;$('#finding-count').textContent=`${open.length} observations`;$('#findings').innerHTML=open.length?open.map(f=>{const remediation=typeof f['Recommended remediation']==='string'?f['Recommended remediation'].trim():'';const validationStatus=typeof f['Validation status']==='string'?f['Validation status']:'Unknown';const evidenceKey=`${f.Endpoint||f.endpoint||''}|${f['Finding name']||''}`;const hasEvidence=evidenceMapByFinding.has(evidenceKey);const label=['Critical','High','Medium','Low'].includes(f._level)?f._level.toUpperCase():'Potential Finding';const pillClass=f._level==='Low'?'pill low':'pill';return `<article class="finding"><div class="findingtop"><strong>${esc(f['Finding name'])}</strong><span class="${pillClass}">${label}</span></div><small>${esc(f.Endpoint||f.endpoint||'')}</small><div style="margin-top:8px;color:#aebbc5;font-size:11px;line-height:1.5"><strong style="color:#e7edf2">Validation status:</strong> ${esc(validationStatus)}</div>${hasEvidence?`<div style="margin-top:6px;color:#59e1b0;font-size:11px;letter-spacing:.04em;text-transform:uppercase">Evidence available</div>`:''}<p>${esc(f['Basic explanation']||f.Observation||'Review this configuration observation.')}</p>${remediation?`<p><strong>Recommended remediation:</strong> ${esc(remediation)}</p>`:''}</article>`}).join(''):'<div class="empty">No potential findings in the latest assessment.</div>';$('#unvalidated').innerHTML=unvalidated.length?`<div class="target-list">${unvalidated.map(item=>`<div class="target"><span class="url">${esc(item.endpoint||item.url||'')}</span><span class="tag">Not assessed</span></div>`).join('')}</div>`:'<div class="empty">No unvalidated endpoints in the latest assessment.</div>';$('#prioritized').innerHTML=prioritized.length?`<div class="target-list">${prioritized.map(item=>`<div class="target"><span class="url">${esc(item.endpoint||item.url||'')}</span><span class="tag">${esc(item.risk_level||'unknown')} · ${Number(item.potential_findings??0)} findings</span></div>`).join('')}</div>`:'<div class="empty">No prioritized endpoints in the latest assessment.</div>'}
const progressStages=new Set(['Authorization',...stages]);
const progressStatuses=new Set(['running','completed','failed']);
const maxProgressPollFailures=3;
const maxProgressMismatchMs=10000;
let progressPolling=false;
let progressPollFailures=0;
let progressPollTimer=null;
let progressDeadlineTimer=null;
let progressPollController=null;
let lastProgress=null;
let activeRunId=null;
let progressPollStartedAt=0;
function isValidProgressState(data){return Boolean(data&&typeof data==='object'&&!Array.isArray(data)&&data.progress&&typeof data.progress==='object'&&!Array.isArray(data.progress)&&typeof data.progress.run_id==='string'&&progressStatuses.has(data.progress.status)&&progressStages.has(data.progress.stage))}
function showProgress(progress){if(!progressStatuses.has(progress?.status)||!progressStages.has(progress?.stage))return;$('#status').textContent=`Assessment ${progress.status} · ${progress.stage}`;$('#status').className=progress.status==='failed'?'status error':'status'}
function stopProgressPolling(runId){if(runId&&activeRunId!==runId)return;progressPolling=false;if(progressPollTimer!==null){window.clearTimeout(progressPollTimer);progressPollTimer=null}if(progressDeadlineTimer!==null){window.clearTimeout(progressDeadlineTimer);progressDeadlineTimer=null}if(progressPollController){const controller=progressPollController;progressPollController=null;controller.abort()}}
async function refresh(){try{const r=await fetch('/api/state');if(!r.ok)throw new Error('Dashboard state unavailable');const d=await r.json();render(d.report,d.authorized_targets||[],d.last_run);if(isValidProgressState(d)&&d.progress.status==='running')showProgress(d.progress)}catch(e){$('#status').textContent='Could not load local dashboard data.';$('#status').className='status error'}}
async function pollProgress(runId){if(!progressPolling||activeRunId!==runId)return;const controller=new AbortController();progressPollController=controller;try{const response=await fetch('/api/state',{signal:controller.signal});if(!response.ok)throw new Error('Progress unavailable');const data=await response.json();if(!isValidProgressState(data))throw new Error('Malformed progress response');if(!progressPolling||activeRunId!==runId)return;if(data.progress.run_id!==runId){const elapsed=performance.now()-progressPollStartedAt;if(elapsed>=maxProgressMismatchMs){stopProgressPolling(runId);$('#status').textContent='Assessment progress could not be matched to this scan.';$('#status').className='status error';return}progressPollFailures=0;progressPollTimer=window.setTimeout(()=>pollProgress(runId),Math.min(500,maxProgressMismatchMs-elapsed));return}progressPollFailures=0;lastProgress={run_id:runId,stage:data.progress.stage,status:data.progress.status};showProgress(lastProgress);if(lastProgress.status!=='running'){stopProgressPolling(runId);return}}catch(e){if(e.name==='AbortError'||!progressPolling||activeRunId!==runId)return;progressPollFailures+=1;if(progressPollFailures>=maxProgressPollFailures){stopProgressPolling(runId);$('#status').textContent=lastProgress?`Progress unavailable · last update: Assessment ${lastProgress.status} · ${lastProgress.stage}`:'Progress unavailable · assessment is still running';$('#status').className='status error';return}}finally{if(progressPollController===controller)progressPollController=null}if(progressPolling&&activeRunId===runId)progressPollTimer=window.setTimeout(()=>pollProgress(runId),500*Math.min(2**progressPollFailures,4))}
$('#scan').onclick=async()=>{
const target=$('#target').value.trim();const status=$('#status');if(!target){status.textContent='Enter an authorized target URL.';status.className='status error';return}if(!$('#confirm').checked){status.textContent='Confirm that you are authorized before continuing.';status.className='status error';return}
const button=$('#scan');button.disabled=true;button.innerHTML='<span class="spinner"></span>Assessing';status.textContent='Authorization and scope checks are running before network requests. This may take a few seconds.';status.className='status';progressPollFailures=0;lastProgress=null;const runId=crypto.randomUUID().replace(/-/g,'');activeRunId=runId;progressPollStartedAt=performance.now();progressPolling=true;progressDeadlineTimer=window.setTimeout(()=>{if(!progressPolling||activeRunId!==runId)return;stopProgressPolling(runId);status.textContent='Assessment progress polling timed out.';status.className='status error'},maxProgressMismatchMs);pollProgress(runId);
let scanSucceeded=false;
try{
const res=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target,authorized:true,run_id:runId})});const data=await res.json();if(data.progress?.run_id===runId&&isValidProgressState(data))lastProgress=data.progress;if(!res.ok)throw new Error(data.error||'Assessment failed');scanSucceeded=true;render(data.report,data.authorized_targets||[],new Date().toLocaleString())
}catch(e){if(lastProgress?.status==='failed'){showProgress(lastProgress);status.textContent+=` · ${e.message}`}else{status.textContent=e.message}status.className='status error'}finally{stopProgressPolling(runId);if(scanSucceeded){lastProgress=lastProgress?.status==='completed'?lastProgress:{run_id:runId,stage:'Report',status:'completed'};showProgress(lastProgress)}button.disabled=false;button.textContent='Run assessment  ↗'}
};
refresh();
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    server_version = "H4CK-B0T/1.0"

    def log_message(self, format, *args):
        # Keep routine HTTP traffic out of the terminal; assessment events have an audit log.
        pass

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 8192)
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            raise ValueError("Request body must be valid JSON.")

    def _local_only(self):
        host = self.headers.get("Host", "").split(":")[0].strip("[]").lower()
        if host not in {"localhost", "127.0.0.1", "::1"}:
            self._json({"error": "This dashboard only accepts local connections."}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin:
            origin_host = urlparse(origin).hostname
            if origin_host not in {"localhost", "127.0.0.1", "::1"}:
                self._json({"error": "Cross-origin requests are not allowed."}, 403)
                return False
        return True

    def do_GET(self):
        if not self._local_only():
            return
        if self.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            config = load_config()
            report_data = read_json("report.json")
            try:
                last_run = datetime.fromtimestamp((RESULTS / "report.json").stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M") if report_data else None
            except OSError:
                last_run = None
            self._json({"authorized_targets": config.get("authorized_targets", []), "safe_mode": bool(config.get("safe_mode", True)), "report": report_data, "last_run": last_run, "progress": _assessment_progress_snapshot()})
        elif self.path == "/api/report":
            payload = read_json("report.json")
            self._json(payload or {"error": "No report is available yet."}, 200 if payload else 404)
        else:
            self._json({"error": "Not found."}, 404)

    def do_POST(self):
        if not self._local_only():
            return
        if self.path != "/api/scan":
            self._json({"error": "Not found."}, 404)
            return
        if not SCAN_LOCK.acquire(blocking=False):
            self._json({"error": "An assessment is already running.", "progress": _assessment_progress_snapshot()}, 409)
            return
        run_id = uuid.uuid4().hex
        _set_assessment_progress(run_id, "Authorization", "running")
        try:
            body = self._body()
            requested_run_id = body.get("run_id")
            if requested_run_id is not None:
                try:
                    run_id = uuid.UUID(requested_run_id).hex
                except (AttributeError, TypeError, ValueError) as exc:
                    raise ValueError("Assessment identifier must be a UUID.") from exc
                _set_assessment_progress(run_id, "Authorization", "running")
            if body.get("authorized") is not True:
                raise ValueError("Confirm authorization in the dashboard before starting an assessment.")
            target = normalize_target(body.get("target"))
            report_data = run_assessment(target, run_id)
            config = load_config()
            self._json({"report": report_data, "authorized_targets": config.get("authorized_targets", []), "progress": _assessment_progress_snapshot()})
        except (ValueError, PermissionError) as exc:
            _mark_assessment_failed(run_id)
            self._json({"error": str(exc), "progress": _assessment_progress_snapshot()}, 400)
        except Exception as exc:
            _mark_assessment_failed(run_id)
            self._json({"error": f"Assessment could not be completed: {exc}", "progress": _assessment_progress_snapshot()}, 500)
        finally:
            SCAN_LOCK.release()


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("H4CK-B0T dashboard is ready at http://127.0.0.1:8765")
    print("Press Ctrl+C to stop the local server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
