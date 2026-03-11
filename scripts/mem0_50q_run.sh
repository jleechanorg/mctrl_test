#!/usr/bin/env bash
set -euo pipefail

MODE="run"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-run}"
      shift 2
      ;;
    dry-run)
      MODE="dry-run"
      shift
      ;;
    run)
      MODE="run"
      shift
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

ROOT="/tmp/openclaw-mem0-fastpath"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/$STAMP-50q-agent"
mkdir -p "$OUT"
ln -sfn "$OUT" "$ROOT/latest-50q"

if [[ "$MODE" == "dry-run" ]]; then
  echo '{"ok":true,"mode":"dry-run"}' > "$OUT/dry-run.json"
  echo "$OUT"
  exit 0
fi

# Build canonical expected prompts from slack-history memory export.
python3 -u <<'PY'
import json
import pathlib
import re
from collections import defaultdict

base = pathlib.Path('/Users/jleechan/.openclaw/memory/slack-history')
mds = sorted(base.glob('*.md'))
text = '\n'.join(p.read_text(errors='ignore') for p in mds)

pairs = []
for m in re.finditer(r'(ORCH-[A-Za-z0-9\-]+).*?`(ai-orch-\d+)`', text, flags=re.I|re.S):
    orch = m.group(1)
    if orch.lower().startswith('orch-'):
        orch = 'ORCH-' + orch.split('-', 1)[1]
    pairs.append((orch, m.group(2)))

# stable de-dupe
seen = set()
dedup = []
for p in pairs:
    if p in seen:
        continue
    seen.add(p)
    dedup.append(p)

# Canonical seeds that should always be present
canonical = [
    ('ORCH-e2e-029c50', 'ai-orch-56066'),
    ('ORCH-e2e-2cfd73', 'ai-orch-55438'),
    ('ORCH-self-hosted-runner-001', 'ai-orch-92020'),
]
for p in canonical:
    if p not in seen:
        dedup.append(p)
        seen.add(p)

branch_to_orch = defaultdict(set)
orch_to_branches = defaultdict(set)
for orch, branch in dedup:
    orch_to_branches[orch].add(branch)
    branch_to_orch[branch].add(orch)

# Keep only strict one-to-one mappings to avoid ambiguous scoring.
strict_pairs = []
for orch, branches in orch_to_branches.items():
    if len(branches) != 1:
        continue
    branch = next(iter(branches))
    if len(branch_to_orch[branch]) != 1:
        continue
    strict_pairs.append((orch, branch))
strict_pairs = sorted(strict_pairs, key=lambda x: x[0])

# Build 50 questions, mixing forward and reverse lookups.
expected = []

# 25 forward lookups (exact ORCH -> branch)
for orch, branch in strict_pairs[:25]:
    expected.append({
        'kind': 'orch_to_branch',
        'question': f'Which branch was {orch} committed to?',
        'must_contain': [branch],
        'must_contain_any': [],
    })

# 25 reverse lookups (branch -> ORCH) from strict one-to-one mappings.
for orch, branch in strict_pairs[25:50]:
    expected.append({
        'kind': 'branch_to_orch',
        'question': f'Find the ORCH token associated with branch {branch}.',
        'must_contain': [orch],
        'must_contain_any': [orch],
    })

expected = expected[:50]
out_dir = pathlib.Path('/tmp/openclaw-mem0-fastpath/latest-50q')
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'expected-50.json').write_text(json.dumps(expected, indent=2))
(out_dir / 'pair-map.json').write_text(json.dumps({k: sorted(v) for k, v in branch_to_orch.items()}, indent=2))

print(f'wrote {len(expected)} expected queries -> {out_dir / "expected-50.json"}')
PY

# Refresh memory index before running agent QA.
openclaw memory index --force > "$OUT/reindex.log" 2>&1 || true

# Ask openclaw agent directly for each question and score extracted identifiers.
python3 - <<'PY'
import json
import os
import pathlib
import re
import subprocess

out_dir = pathlib.Path('/tmp/openclaw-mem0-fastpath/latest-50q')
expected = json.loads((out_dir / 'expected-50.json').read_text())
agent_id = os.environ.get('OPENCLAW_50Q_AGENT', 'memqa')

rows = []
passed = 0
run_session_id = f"mem0-qa-run-{pathlib.Path('/tmp/openclaw-mem0-fastpath/latest-50q').resolve().name}"

def extract_identifier(kind: str, text: str) -> str:
    if kind == 'orch_to_branch':
        m = re.search(r'ai-orch-\d+', text, flags=re.I)
        return (m.group(0).lower() if m else '')
    m = re.search(r'ORCH-[A-Za-z0-9\-]+', text, flags=re.I)
    if not m:
        return ''
    token = m.group(0)
    return 'ORCH-' + token.split('-', 1)[1]

for i, e in enumerate(expected, 1):
    q = e['question']
    kind = e['kind']
    if kind == 'orch_to_branch':
        prompt = (
            'Memory-only recall test.\\n'
            'Reply with exactly one token in format ai-orch-<digits>.\\n'
            'If unknown, reply I_DONT_KNOW.\\n'
            f'Question: {q}'
        )
    else:
        prompt = (
            'Memory-only recall test.\\n'
            'Reply with exactly one token in format ORCH-<token>.\\n'
            'If unknown, reply I_DONT_KNOW.\\n'
            f'Question: {q}'
        )

    attempts = []
    extracted = ''
    raw_answer = ''
    for attempt in range(1, 4):
        session_id = run_session_id
        try:
            p = subprocess.run(
                ['openclaw', '--log-level', 'fatal', 'agent', '--local', '--agent', agent_id, '--session-id', session_id, '--timeout', '120', '--json', '--thinking', 'off', '-m', prompt],
                capture_output=True,
                text=True,
                env=os.environ.copy(),
                timeout=140,
            )
            raw = (p.stdout or '').strip()
            stderr = (p.stderr or '').strip()
            answer = ''
            try:
                payload = json.loads(raw)
                payloads = payload.get('payloads') or payload.get('result', {}).get('payloads', [])
                if payloads:
                    answer = str(payloads[0].get('text') or '')
            except Exception:
                answer = raw
            if stderr:
                answer = (answer + '\n' + stderr).strip()
            err_l = (stderr or "").lower()
            if p.returncode != 0 and (
                "session file locked" in err_l
                or "rate limit" in err_l
                or "timed out" in err_l
                or "all models failed" in err_l
            ):
                # Runtime/transient failure: repair session metadata and retry.
                subprocess.run(
                    ['openclaw', 'sessions', 'cleanup'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                attempts.append({
                    'attempt': attempt,
                    'answer': answer[:2000],
                    'extracted': '',
                    'returncode': p.returncode,
                    'transient_retry': True,
                })
                continue
        except subprocess.TimeoutExpired:
            answer = 'I_DONT_KNOW'

        token = extract_identifier(kind, answer)
        attempts.append({'attempt': attempt, 'answer': answer[:2000], 'extracted': token, 'returncode': p.returncode if 'p' in locals() else None})
        raw_answer = answer
        if token:
            extracted = token
            break

    expected_primary = [x.lower() for x in e.get('must_contain', [])]
    expected_any = [x.lower() for x in e.get('must_contain_any', [])]

    ok = False
    if extracted:
        if kind == 'orch_to_branch':
            ok = extracted in expected_primary
        else:
            ok = extracted in expected_any if expected_any else extracted in expected_primary

    if ok:
        passed += 1

    rows.append({
        'n': i,
        'question': q,
        'kind': kind,
        'expected': e.get('must_contain', []),
        'expected_any': e.get('must_contain_any', []),
        'answer': raw_answer[:8000],
        'extracted': extracted,
        'passed': ok,
        'attempts': attempts,
    })

    status = 'OK' if ok else 'MISS'
    print(f"{i:02d} {status} {extracted or 'NO_ID'}", flush=True)

score = {
    'passed': passed,
    'total': len(expected),
    'pass_rate': (passed / len(expected)) if expected else 0.0,
}
(out_dir / 'qa-50.json').write_text(json.dumps(rows, indent=2))
(out_dir / 'score.json').write_text(json.dumps(score, indent=2))
(out_dir / 'failures.json').write_text(json.dumps([r for r in rows if not r['passed']], indent=2))
print('FINAL', json.dumps(score))
PY

echo "$OUT"
