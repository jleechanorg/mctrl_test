#!/usr/bin/env python3
"""Ralph Dashboard Server — standalone Python HTTP server.

Serves the dashboard HTML and /api/status JSON endpoint.
Reads PRD_FILE, PROGRESS_FILE, DASHBOARD_HTML, REPO_ROOT from env vars.

Usage:
  python3 dashboard.py [--port PORT]
  # Or via env: DASHBOARD_PORT=9450 python3 dashboard.py
"""
import http.server, json, subprocess, os, time, socketserver, argparse, sys


def get_config():
    return {
        'prd_file': os.environ.get('PRD_FILE', 'prd.json'),
        'progress_file': os.environ.get('PROGRESS_FILE', 'progress.txt'),
        'dashboard_html': os.environ.get('DASHBOARD_HTML', 'dashboard.html'),
        'repo_root': os.environ.get('REPO_ROOT', '.'),
    }


def get_status(config):
    prd_file = config['prd_file']
    repo = config['repo_root']

    try:
        with open(prd_file) as f:
            prd = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        return {'error': f'Cannot read prd.json: {e}'}

    stories = prd.get('userStories', [])
    total = len(stories)
    passed = sum(1 for s in stories if s.get('passes'))

    prefix_groups = {}
    for s in stories:
        sid = s.get('id', '')
        prefix = sid.split('-')[0] + '-' if '-' in sid else sid
        if prefix not in prefix_groups:
            prefix_groups[prefix] = []
        prefix_groups[prefix].append(s)

    phases = []
    for prefix in sorted(prefix_groups.keys()):
        ph_stories = prefix_groups[prefix]
        phases.append({
            'name': prefix.rstrip('-'),
            'total': len(ph_stories),
            'done': sum(1 for s in ph_stories if s.get('passes'))
        })

    next_s = next((s for s in stories if not s.get('passes')), None)
    next_story = f"{next_s['id']}: {next_s['title']}" if next_s else None

    commits = []
    try:
        out = subprocess.check_output(
            ['git', 'log', '--format=%h|%ar|%ct|%s', '-10'],
            cwd=repo, text=True, timeout=5
        )
        for line in out.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 3)
                commits.append({
                    'hash': parts[0], 'ago': parts[1],
                    'ts': int(parts[2]), 'message': parts[3]
                })
    except Exception:
        pass

    elapsed = None
    if commits:
        elapsed = int(time.time()) - commits[0]['ts']

    ralph_running = False
    ralph_pid = None
    try:
        out = subprocess.check_output(['pgrep', '-f', 'ralph.sh'], text=True, timeout=3)
        pids = out.strip().split('\n')
        if pids and pids[0]:
            ralph_running = True
            ralph_pid = pids[0]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    return {
        'total': total,
        'passed': passed,
        'phases': phases,
        'next_story': next_story,
        'commits': commits,
        'last_commit_elapsed_sec': elapsed,
        'ralph_running': ralph_running,
        'ralph_pid': ralph_pid,
        'stories': [
            {'id': s['id'], 'title': s['title'], 'passes': s.get('passes', False)}
            for s in stories
        ],
    }


def make_handler(config):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split('?')[0]
            if path == '/api/status':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(get_status(config)).encode())
            elif path == '/' or path == '/index.html':
                try:
                    with open(config['dashboard_html'], 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Dashboard HTML not found')
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser(description='Ralph Dashboard Server')
    ap.add_argument('--port', type=int, default=int(os.environ.get('DASHBOARD_PORT', '9450')))
    args = ap.parse_args()

    config = get_config()
    Handler = make_handler(config)

    with socketserver.TCPServer(('127.0.0.1', args.port), Handler) as httpd:
        print(f"Dashboard: http://localhost:{args.port}")
        httpd.serve_forever()


if __name__ == '__main__':
    main()
