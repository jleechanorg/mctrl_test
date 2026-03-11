#!/bin/bash
# ralph/lib/terminal_recorder.sh — Terminal session recording with captions
# Records tmux pane output, generates SRT captions, renders to video.

_TERMINAL_RECORD_PID=""
_TERMINAL_LOG_FILE=""

# Start recording a tmux session's output
# Usage: terminal_record_start <session_name> <log_file>
terminal_record_start() {
  local session="$1" log_file="$2"
  _TERMINAL_LOG_FILE="$log_file"

  if ! command -v tmux >/dev/null 2>&1; then
    echo "  ⚠️  tmux not available; skipping terminal recording"
    return 0
  fi

  if ! tmux has-session -t "$session" 2>/dev/null; then
    echo "  ⚠️  tmux session '$session' not found; skipping terminal recording"
    return 0
  fi

  mkdir -p "$(dirname "$log_file")"
  touch "$log_file"
  
  # Capture tmux pane in a background loop with timestamps
  (
    while true; do
      ts=$(date '+[%Y-%m-%d %H:%M:%S]')
      content=$(tmux capture-pane -t "$session" -p 2>/dev/null || break)
      if [ -n "$content" ]; then
        echo "$ts" >> "$log_file"
        echo "$content" >> "$log_file"
        echo "---" >> "$log_file"
      fi
      sleep 3
    done
  ) &
  _TERMINAL_RECORD_PID=$!
  echo "  🎥 Terminal recording: PID $_TERMINAL_RECORD_PID → $log_file"
}

# Stop terminal recording
# Usage: terminal_record_stop
terminal_record_stop() {
  if [ -n "$_TERMINAL_RECORD_PID" ]; then
    kill "$_TERMINAL_RECORD_PID" 2>/dev/null || true
    wait "$_TERMINAL_RECORD_PID" 2>/dev/null || true
    _TERMINAL_RECORD_PID=""
    echo "  🛑 Terminal recording stopped"
  fi
}

# Capture a single snapshot of a tmux pane
# Usage: terminal_snapshot <session_name> <output_file>
terminal_snapshot() {
  local session="$1" output="$2"
  tmux capture-pane -t "$session" -p > "$output" 2>/dev/null
}

# Convert terminal log to SRT captions
# Usage: terminal_to_srt <log_file> <srt_file>
terminal_to_srt() {
  local log_file="$1" srt_file="$2"
  python3 -c "
import re
lines = []
with open('$log_file') as f:
    for line in f:
        line = line.strip()
        if not line or line == '---':
            continue
        # Keep timestamp lines and non-empty content
        if line.startswith('[20'):
            lines.append(line)
        elif len(line) > 2:
            # Take interesting lines (skip blank tmux content)
            clean = line.replace('\t', ' ').strip()
            if clean and not all(c in ' ─═│┌┐└┘├┤' for c in clean):
                lines.append(clean)

# Group into SRT entries (every 5 lines = 1 caption, 3 seconds each)
srt = []
idx = 0
for i in range(0, len(lines), 5):
    idx += 1
    chunk = lines[i:i+5]
    caption = ' | '.join(chunk[:3])  # First 3 lines as caption
    if len(caption) > 120:
        caption = caption[:117] + '...'
    a = (idx - 1) * 3
    b = idx * 3
    at = f'{a//3600:02d}:{a%3600//60:02d}:{a%60:02d},000'
    bt = f'{b//3600:02d}:{b%3600//60:02d}:{b%60:02d},000'
    srt.append(f'{idx}\n{at} --> {bt}\n{caption}\n')

with open('$srt_file', 'w') as f:
    f.write('\n'.join(srt))
print(f'  📝 Terminal SRT: {len(srt)} captions → $srt_file')
" 2>/dev/null || echo "  ⚠️ SRT generation failed"
}

# Render terminal log as a captioned WebM video using Playwright
# Usage: terminal_render_video <log_file> <video_file> [srt_file]
terminal_render_video() {
  local log_file="$1" video_file="$2" srt_file="${3:-}"
  
  # Check Playwright availability
  if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "  ⚠️ Playwright not available for terminal video"
    return 1
  fi

  python3 -c "
import time, os
from playwright.sync_api import sync_playwright

log_file = '$log_file'
video_file = '$video_file'
video_dir = os.path.dirname(video_file) or '/tmp'

# Parse log into frames
frames = []
current_frame = []
current_ts = ''
with open(log_file) as f:
    for line in f:
        line = line.rstrip()
        if line == '---':
            if current_frame:
                frames.append((current_ts, '\n'.join(current_frame)))
            current_frame = []
            current_ts = ''
        elif line.startswith('[20'):
            current_ts = line
        else:
            current_frame.append(line)
    if current_frame:
        frames.append((current_ts, '\n'.join(current_frame)))

if not frames:
    frames = [('', 'No terminal output captured')]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        record_video_dir=video_dir,
        record_video_size={'width': 1280, 'height': 720},
        viewport={'width': 1280, 'height': 720}
    )
    page = ctx.new_page()
    
    # Create terminal-styled page
    page.set_content('''<html><head><style>
      body { background: #1e1e2e; color: #cdd6f4; font-family: \"SF Mono\", \"Fira Code\", monospace;
             font-size: 14px; padding: 20px; margin: 0; white-space: pre-wrap; word-wrap: break-word; }
      #header { color: #f9e2af; font-size: 16px; font-weight: bold; margin-bottom: 10px;
                border-bottom: 1px solid #45475a; padding-bottom: 8px; }
      #content { line-height: 1.4; }
      #caption { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.9);
                 color: #a6e3a1; font-size: 16px; padding: 10px 20px; border-top: 2px solid #f9e2af; }
    </style></head><body>
      <div id=\"header\">🐺 Ralph Terminal Recording</div>
      <div id=\"content\"></div>
      <div id=\"caption\"></div>
    </body></html>''')
    time.sleep(1)

    for i, (ts, content) in enumerate(frames[:30]):  # Cap at 30 frames
        # Escape for JS
        safe = content.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"').replace('\\n', '\\\\n')
        safe_ts = ts.replace('\"', '\\\\\"') if ts else f'Frame {i+1}/{len(frames)}'
        
        page.evaluate(f'''() => {{
            document.getElementById('content').innerText = \"{safe}\";
            document.getElementById('caption').innerText = \"{safe_ts}\";
        }}''')
        time.sleep(1.5)

    # Final frame
    page.evaluate('''() => {
        document.getElementById('caption').innerText = '🏁 Terminal recording complete';
        document.getElementById('caption').style.color = '#f9e2af';
    }''')
    time.sleep(2)
    
    ctx.close()
    browser.close()

# Rename video
import glob
vids = glob.glob(os.path.join(video_dir, '*.webm'))
if vids:
    target = video_file
    if os.path.exists(target):
        os.unlink(target)
    os.rename(vids[-1], target)
    size = os.path.getsize(target)
    print(f'  🎬 Terminal video: {target} ({size//1024}KB)')
" 2>/dev/null || echo "  ⚠️ Terminal video rendering failed"
}
