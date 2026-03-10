#!/usr/bin/env python3
"""
agento-notifier: Minimal HTTP server that receives AO webhook events
and posts them to Slack #ai-slack-test as the openclaw bot.

Run: python3 scripts/agento-notifier.py
Port: 18800
"""
from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

os.environ.setdefault("PYTHONUNBUFFERED", "1")

SLACK_CHANNEL = os.environ.get("OPENCLAW_SLACK_CHANNEL", "C0AKALZ4CKW")  # #ai-slack-test
PORT = 18800
WEBHOOK_SECRET = os.environ.get("OPENCLAW_AO_NOTIFY_TOKEN", "")


def post_to_slack(text: str) -> None:
    # Prefer bot token for service notifier; fall back to user token if not available
    token = (
        os.environ.get("OPENCLAW_SLACK_BOT_TOKEN")
        or os.environ.get("SLACK_BOT_TOKEN")
        or os.environ.get("SLACK_USER_TOKEN")
    )
    if not token:
        print(f"[agento-notifier] No Slack token in env, would have posted: {text}")
        return
    payload = json.dumps({"channel": SLACK_CHANNEL, "text": text}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
        if not body.get("ok"):
            print(f"[agento-notifier] Slack post failed: {body}")
        else:
            print(f"[agento-notifier] Posted to Slack: {text[:80]}")
    except Exception as exc:
        print(f"[agento-notifier] Slack request error: {exc}")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/ao-notify":
            self.send_response(404)
            self.end_headers()
            return

        # Optional webhook authentication
        if WEBHOOK_SECRET:
            auth_header = self.headers.get("Authorization", "")
            if auth_header != f"Bearer {WEBHOOK_SECRET}":
                self.send_response(401)
                self.end_headers()
                return

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length < 0:
                length = 0
        except ValueError:
            length = 0
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        if not isinstance(data, dict):
            self.send_response(400)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

        event = data.get("event")
        if not isinstance(event, dict):
            event = {}
        msg_type = data.get("type", "notification")

        if msg_type == "message":
            text = f":robot_face: *agento* | {data.get('message', '') or ''}"
        else:
            priority = event.get("priority") or "info"
            event_type = event.get("type") or "unknown"
            message = event.get("message") or ""
            session = event.get("sessionId") or ""
            project = event.get("projectId") or ""
            event_data = event.get("data")
            if isinstance(event_data, dict):
                pr_url = event_data.get("prUrl", "")
            else:
                pr_url = ""
            pr_part = f" | <{pr_url}|PR>" if pr_url else ""
            emoji = {"urgent": ":rotating_light:", "action": ":point_right:",
                     "warning": ":warning:", "info": ":information_source:"}.get(priority, ":bell:")
            text = f"{emoji} *agento* `{event_type}` [{project}/{session}]{pr_part}\n{message}"

        post_to_slack(text)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[agento-notifier] {fmt % args}")


if __name__ == "__main__":
    print(f"[agento-notifier] Listening on port {PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
