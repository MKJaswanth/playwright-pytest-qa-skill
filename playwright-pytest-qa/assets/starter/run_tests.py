"""Archive this run's report while preserving pytest's exit status.

When APP_START_CMD or APP_START_CMDS is set, start those processes, wait until
BASE_URL or HEALTHCHECK_URL responds, run pytest, then stop the process tree.
"""

from datetime import datetime, timezone
from pathlib import Path
import os
import signal
import shutil
import subprocess
import sys
import time

import requests


class ServerStartupError(RuntimeError):
    pass


def start_commands():
    commands = []
    single = os.environ.get("APP_START_CMD", "").strip()
    if single:
        commands.append(single)
    for line in os.environ.get("APP_START_CMDS", "").splitlines():
        command = line.strip()
        if command:
            commands.append(command)
    return commands


def ready_url():
    return os.environ.get("HEALTHCHECK_URL", "").strip() or os.environ.get("BASE_URL", "").strip()


def startup_timeout():
    raw = os.environ.get("APP_START_TIMEOUT", "60").strip() or "60"
    try:
        value = float(raw)
    except ValueError as exc:
        raise ServerStartupError("APP_START_TIMEOUT must be a number of seconds") from exc
    if value <= 0:
        raise ServerStartupError("APP_START_TIMEOUT must be greater than zero")
    return value


def start_process(command, cwd):
    kwargs = {"args": command, "shell": True, "cwd": cwd}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(**kwargs)


def stop_process(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
            check=False,
        )
    else:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
        else:
            proc.kill()
        proc.wait(timeout=5)


def wait_until_ready(url, procs, timeout):
    deadline = time.monotonic() + timeout
    delay = 0.05
    last_error = "no response"
    session = requests.Session()
    session.trust_env = False
    try:
        while time.monotonic() < deadline:
            for proc in procs:
                if proc.poll() is not None:
                    raise ServerStartupError(
                        f"Server exited before {url} was ready (status {proc.returncode})"
                    )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                response = session.get(url, timeout=min(1.0, remaining))
                if response.status_code < 500:
                    return
                last_error = f"HTTP {response.status_code}"
            except requests.RequestException as exc:
                last_error = type(exc).__name__
            time.sleep(min(delay, max(0.0, deadline - time.monotonic())))
            delay = min(delay * 2, 2.0)
    finally:
        session.close()
    raise TimeoutError(f"Timed out after {timeout:.0f}s waiting for {url}: {last_error}")


class with_server:
    """Start one or more background servers and stop their process trees."""

    def __init__(self, commands, url, timeout=60, cwd=None):
        self.commands = list(commands)
        self.url = url
        self.timeout = timeout
        self.cwd = cwd
        self.procs = []

    def __enter__(self):
        if not self.commands:
            raise ServerStartupError("No server commands were provided")
        if not self.url:
            raise ServerStartupError("A readiness URL is required")
        try:
            for command in self.commands:
                self.procs.append(start_process(command, self.cwd))
            wait_until_ready(self.url, self.procs, self.timeout)
        except Exception:
            self._stop()
            raise
        return self.procs

    def __exit__(self, exc_type, exc, tb):
        self._stop()
        return False

    def _stop(self):
        for proc in reversed(self.procs):
            stop_process(proc)
        self.procs.clear()


def run_pytest(project):
    report = project / "reports" / "report.html"
    report.unlink(missing_ok=True)
    result = subprocess.run([sys.executable, "-m", "pytest", *sys.argv[1:]], cwd=project)
    if report.exists():
        try:
            archive = project / "reports" / "history"
            archive.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_%f")
            destination = archive / f"report_{stamp}.html"
            shutil.copy2(report, destination)
            print(f"Report saved: {destination}")
        except OSError as exc:
            print(f"Report archive failed: {exc}", file=sys.stderr)
            return result.returncode or 1
    return result.returncode


def main():
    project = Path(__file__).resolve().parent
    commands = start_commands()
    if not commands:
        return run_pytest(project)
    url = ready_url()
    if not url:
        print("Set BASE_URL or HEALTHCHECK_URL when APP_START_CMD is set.", file=sys.stderr)
        return 2
    try:
        with with_server(commands, url, timeout=startup_timeout(), cwd=project):
            return run_pytest(project)
    except (ServerStartupError, TimeoutError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
