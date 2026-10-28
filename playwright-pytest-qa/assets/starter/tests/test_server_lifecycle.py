import os
import shlex
import socket
import subprocess
import sys

import pytest
import requests

import run_tests


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _command(argv):
    if os.name == "nt":
        return subprocess.list2cmdline(argv)
    return shlex.join(argv)


def test_with_server_reaches_readiness_and_stops(tmp_path):
    port = _free_port()
    script = tmp_path / "health.py"
    script.write_text(
        "from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\n"
        "class Handler(BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        body = b'ok'\n"
        "        self.send_response(200)\n"
        "        self.send_header('Content-Length', str(len(body)))\n"
        "        self.end_headers()\n"
        "        self.wfile.write(body)\n"
        "    def log_message(self, *args):\n"
        "        return\n"
        f"ThreadingHTTPServer(('127.0.0.1', {port}), Handler).serve_forever()\n",
        encoding="utf-8",
    )
    url = f"http://127.0.0.1:{port}/health"
    command = _command([sys.executable, str(script)])
    session = requests.Session()
    session.trust_env = False
    with run_tests.with_server([command], url, timeout=15) as procs:
        response = session.get(url, timeout=2)
        response.raise_for_status()
        proc = procs[0]
        assert proc.poll() is None
    assert proc.poll() is not None


def test_with_server_times_out_and_stops_the_process():
    command = _command([sys.executable, "-c", "import time; time.sleep(30)"])
    with pytest.raises(TimeoutError):
        with run_tests.with_server([command], "http://127.0.0.1:9/health", timeout=1.2):
            raise AssertionError("readiness should fail before the suite starts")


def test_main_requires_ready_url_when_starting_a_server(monkeypatch):
    monkeypatch.setenv("APP_START_CMD", f'"{sys.executable}" -c "print(1)"')
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.delenv("HEALTHCHECK_URL", raising=False)
    monkeypatch.delenv("APP_START_CMDS", raising=False)
    assert run_tests.main() == 2


def test_multiple_commands_are_collected(monkeypatch):
    monkeypatch.setenv("APP_START_CMD", "npm run dev")
    monkeypatch.setenv("APP_START_CMDS", "uvicorn app:app\n\nflask run\n")
    assert run_tests.start_commands() == ["npm run dev", "uvicorn app:app", "flask run"]
