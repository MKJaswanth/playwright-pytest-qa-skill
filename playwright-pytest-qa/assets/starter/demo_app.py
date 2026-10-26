"""Local HTTP demo. Test state belongs to each server instance."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

HTML = b'''<!doctype html><html lang="en"><meta charset="utf-8">
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


def make_server():
    roles = {}
    lock = Lock()
    next_id = 0

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, payload, content_type="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            if self.path == "/":
                return self.reply(200, HTML, "text/html; charset=utf-8")
            if self.path == "/api/roles":
                with lock:
                    payload = json.dumps(list(roles.values())).encode()
                return self.reply(200, payload)
            self.reply(404, b"{}")

        def do_POST(self):
            nonlocal next_id
            if self.path != "/api/roles":
                return self.reply(404, b"{}")
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if not isinstance(body.get("name"), str) or not body["name"].strip():
                return self.reply(400, b'{"error":"Name required"}')
            with lock:
                next_id += 1
                role = {"id": str(next_id), "name": body["name"]}
                roles[role["id"]] = role
            self.reply(201, json.dumps(role).encode())

        def do_DELETE(self):
            if not self.path.startswith("/api/roles/"):
                return self.reply(404, b"{}")
            with lock:
                role = roles.pop(self.path.rsplit("/", 1)[-1], None)
            self.reply(204 if role else 404, b"")

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
