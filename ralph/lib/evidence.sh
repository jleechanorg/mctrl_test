#!/bin/bash
# ralph/lib/evidence.sh — Evidence capture functions
# Sourced by ralph.sh. All functions are side-effect-free (take args, not globals).

# Initialize evidence directory structure
# Usage: evidence_init <evidence_dir>
evidence_init() {
  local edir="$1"
  mkdir -p "$edir/screenshots" "$edir/recordings" "$edir/captions"
  echo "  📸 Evidence: $edir"
}

# Take a macOS screenshot
# Usage: evidence_screenshot <evidence_dir> <label>
evidence_screenshot() {
  local edir="$1" label="$2"
  local f="$edir/screenshots/${label}_$(date +%Y%m%d_%H%M%S).png"
  command -v screencapture >/dev/null 2>&1 && screencapture -x "$f" 2>/dev/null && echo "  📸 $f" || true
}

# Snapshot the dashboard API
# Usage: evidence_dashboard_snapshot <evidence_dir> <label> <dashboard_port>
evidence_dashboard_snapshot() {
  local edir="$1" label="$2" port="$3"
  local f="$edir/screenshots/dashboard_${label}_$(date +%Y%m%d_%H%M%S).txt"
  python3 -c "
import urllib.request, json
try:
    r = urllib.request.urlopen('http://localhost:$port/api/status', timeout=3)
    s = json.loads(r.read())
    t, p = s.get('total',0), s.get('passed',0)
    with open('$f','w') as out:
        out.write(f'Dashboard: {p}/{t} ({p*100//t if t else 0}%)\n')
        for x in s.get('stories',[]): out.write(f\"  {'✅' if x['passes'] else '⬜'} {x['id']}: {x['title']}\n\")
    print(f'  📊 $f')
except Exception as e: print(f'  ⚠️ Snapshot: {e}')
" 2>/dev/null || true
}

# Generate SRT captions + markdown for an iteration
# Usage: evidence_captions <iteration> <prd_file> <evidence_dir>
evidence_captions() {
  local iteration="$1" prd_file="$2" edir="$3"
  python3 -c "
import json
try:
    with open('$prd_file') as f: prd=json.load(f)
except: prd={'userStories':[]}
ss=prd.get('userStories',[])
t,p=len(ss),sum(1 for s in ss if s.get('passes'))
pct=p*100//t if t else 0
srt=[]
srt.append(f'1\n00:00:00,000 --> 00:00:05,000\nRalph Iteration $iteration — {p}/{t} ({pct}%)\n')
for i,s in enumerate(ss):
    m='PASS' if s.get('passes') else 'TODO'
    a=5+i*3; b=a+3
    srt.append(f'{i+2}\n00:{a//60:02d}:{a%60:02d},000 --> 00:{b//60:02d}:{b%60:02d},000\n[{m}] {s[\"id\"]}: {s[\"title\"]}\n')
with open('$edir/captions/iteration_$iteration.srt','w') as f: f.write('\n'.join(srt))
md=[f'# Iteration $iteration — {p}/{t} ({pct}%)','']
for s in ss: md.append(f\"- {'✅' if s.get('passes') else '⬜'} **{s['id']}**: {s['title']}\")
with open('$edir/captions/iteration_$iteration.md','w') as f: f.write('\n'.join(md))
print(f'  📝 Captions: iteration_$iteration.srt + .md')
" 2>/dev/null || true
}

# Run browser proof video (Playwright first, then agent-browser)
# Usage: evidence_browser_proof <script_dir> <evidence_dir> [url]
evidence_browser_proof() {
  local script_dir="$1" edir="$2" url="${3:-http://localhost:${RALPH_APP_PORT:-5555}}"
  local py_recorder="$script_dir/evidence_recorder.py"
  local sh_recorder="$script_dir/evidence_recorder.sh"
  echo "  🌐 Running browser proof video..."
  if [ -f "$py_recorder" ] && python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    python3 "$py_recorder" --url "$url" --evidence-dir "$edir" 2>&1 | sed 's/^/    /' || echo "  ⚠️ Playwright browser proof failed"
  elif [ -f "$sh_recorder" ] && command -v agent-browser >/dev/null 2>&1; then
    bash "$sh_recorder" --url "$url" --evidence-dir "$edir" 2>&1 | sed 's/^/    /' || echo "  ⚠️ agent-browser proof failed"
  else
    echo "  ⚠️ No browser recorder available (need playwright or agent-browser)"
  fi
}

# Write evidence_summary.md
# Usage: evidence_finalize <prd_file> <metrics_file> <evidence_dir>
evidence_finalize() {
  local prd_file="$1" metrics_file="$2" edir="$3"
  python3 -c "
import json, os, glob
try:
    with open('$prd_file') as f: prd=json.load(f)
except: prd={'userStories':[]}
ss=prd.get('userStories',[])
t,p=len(ss),sum(1 for s in ss if s.get('passes'))
m={}
if os.path.exists('$metrics_file'):
    try:
        with open('$metrics_file') as f: m=json.load(f)
    except: pass
lines=['# Ralph Evidence Summary','',f'**Result:** {p}/{t}',f'**Duration:** {m.get(\"duration_human\",\"?\")}','','## Recordings']
for r in sorted(glob.glob('$edir/recordings/*')): lines.append(f'- \`{os.path.basename(r)}\`')
lines.extend(['','## Screenshots'])
for s in sorted(glob.glob('$edir/screenshots/*')): lines.append(f'- \`{os.path.basename(s)}\`')
lines.extend(['','## Captions'])
for c in sorted(glob.glob('$edir/captions/*')): lines.append(f'- \`{os.path.basename(c)}\`')
webm=glob.glob('$edir/*.webm')
if webm: lines.extend(['','## Browser Proof Video']+[f'- \`{os.path.basename(w)}\`' for w in webm])
with open('$edir/evidence_summary.md','w') as f: f.write('\n'.join(lines))
print(f'📋 Evidence: $edir/evidence_summary.md')
" 2>/dev/null || true
}
