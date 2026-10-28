"""Local HTTP demo. Test state belongs to each server instance."""

import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.parse import parse_qs

DEFAULT_EMAIL = "super.admin@example.com"
DEFAULT_PASSWORD = "demo-password"

ROLES_HTML = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>QA demo - roles</title><h1>Roles</h1>
<form id="create"><label>Role name <input name="name" required></label>
<button type="submit">Create role</button></form><ul id="roles"></ul>
<p id="empty">No roles found</p>
<script>
async function load() {
  const roles = await (await fetch('/api/roles')).json();
  document.querySelector('#roles').replaceChildren(...roles.map(role => {
    const row = document.createElement('li');
    row.dataset.id = role.id; row.textContent = role.name; return row;
  }));
  document.querySelector('#empty').hidden = roles.length > 0;
}
document.querySelector('#create').addEventListener('submit', async event => {
  event.preventDefault();
  await fetch('/api/roles', {method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: event.target.elements.name.value})});
  await load();
});
load();
</script></html>'''

LOGIN_HTML = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Sign in</title><main><h1>Sign in</h1>
<form method="post" action="/api/login">
<label>Email <input name="email" type="email" autocomplete="username" required></label>
<label>Password <input name="password" type="password" autocomplete="current-password" required></label>
<button type="submit">Sign in</button></form></main></html>'''

DASHBOARD_HTML = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Dashboard</title><main><h1>Dashboard</h1><p>Signed in</p></main></html>'''


def make_server():
    roles = {}
    sessions = {}
    lock = Lock()
    next_id = 0
    email = os.environ.get("SUPER_ADMIN_EMAIL", DEFAULT_EMAIL)
    password = os.environ.get("SUPER_ADMIN_PASSWORD", DEFAULT_PASSWORD)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def body(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length else b""
            content_type = self.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return json.loads(raw.decode() or "{}")
            parsed = parse_qs(raw.decode(), keep_blank_values=True)
            return {key: values[-1] for key, values in parsed.items()}

        def session_token(self):
            for part in self.headers.get("Cookie", "").split(";"):
                name, _, value = part.strip().partition("=")
                if name == "session" and value:
                    return value
            return ""

        def signed_in(self):
            with lock:
                return sessions.get(self.session_token())

        def reply(self, status, payload, content_type="application/json", cookie=None, location=None):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            if cookie:
                self.send_header("Set-Cookie", cookie)
            if location:
                self.send_header("Location", location)
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/health":
                return self.reply(200, b'{"ok":true}')
            if path == "/":
                return self.reply(200, ROLES_HTML, "text/html; charset=utf-8")
            if path == "/login":
                return self.reply(200, LOGIN_HTML, "text/html; charset=utf-8")
            if path == "/dashboard":
                if not self.signed_in():
                    return self.reply(302, b"", "text/plain", location="/login")
                return self.reply(200, DASHBOARD_HTML, "text/html; charset=utf-8")
            if path == "/api/roles":
                with lock:
                    payload = json.dumps(list(roles.values())).encode()
                return self.reply(200, payload)
            self.reply(404, b"{}")

        def do_POST(self):
            nonlocal next_id
            path = self.path.split("?", 1)[0]
            payload = self.body()
            if path == "/api/login":
                if payload.get("email") != email or payload.get("password") != password:
                    return self.reply(401, b'{"error":"Invalid credentials"}')
                token = secrets.token_urlsafe(24)
                with lock:
                    sessions[token] = email
                cookie = f"session={token}; HttpOnly; Path=/; SameSite=Lax"
                if "application/x-www-form-urlencoded" in self.headers.get("Content-Type", ""):
                    return self.reply(302, b"", "text/plain", cookie=cookie, location="/dashboard")
                return self.reply(200, b'{"ok":true}', cookie=cookie)
            if path != "/api/roles":
                return self.reply(404, b"{}")
            if not isinstance(payload.get("name"), str) or not payload["name"].strip():
                return self.reply(400, b'{"error":"Name required"}')
            with lock:
                next_id += 1
                role = {"id": str(next_id), "name": payload["name"]}
                roles[role["id"]] = role
            self.reply(201, json.dumps(role).encode())

        def do_DELETE(self):
            path = self.path.split("?", 1)[0]
            if not path.startswith("/api/roles/"):
                return self.reply(404, b"{}")
            with lock:
                role = roles.pop(path.rsplit("/", 1)[-1], None)
            self.reply(204 if role else 404, b"")

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
