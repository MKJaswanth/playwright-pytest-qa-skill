from threading import Thread
from urllib.parse import quote
from uuid import uuid4
import os
from pathlib import Path

import pytest
import requests

from demo_app import DEFAULT_EMAIL, DEFAULT_PASSWORD, make_server
from pages.login_page import LoginPage

os.environ.setdefault("SUPER_ADMIN_EMAIL", DEFAULT_EMAIL)
os.environ.setdefault("SUPER_ADMIN_PASSWORD", DEFAULT_PASSWORD)

AUTH_DIR = Path(__file__).resolve().parent / ".auth"


def _xdist_worker(config):
    workerinput = getattr(config, "workerinput", None) or {}
    worker = workerinput.get("workerid")
    return str(worker) if worker else None


def login_through_ui(page, base_url):
    """Sign in through the form. Use this for login-flow tests, not for every test."""
    LoginPage(page).sign_in(
        base_url,
        os.environ["SUPER_ADMIN_EMAIL"],
        os.environ["SUPER_ADMIN_PASSWORD"],
    )
    return page


@pytest.fixture(scope="session")
def base_url():
    server = make_server()
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture(scope="session")
def worker_id(request):
    return _xdist_worker(request.config) or "gw0"


@pytest.fixture(scope="session")
def auth_state_path(browser, base_url, request):
    worker = _xdist_worker(request.config) or "master"
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    path = AUTH_DIR / f"super_admin_{worker}.json"
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    try:
        login_through_ui(page, base_url)
        context.storage_state(path=str(path))
    finally:
        context.close()
    return path


@pytest.fixture
def browser_context_args(browser_context_args, base_url):
    return {**browser_context_args, "base_url": base_url}


@pytest.fixture
def authenticated_context(browser, base_url, auth_state_path):
    # Separate context. Override browser_context_args to keep failure artifacts.
    context = browser.new_context(base_url=base_url, storage_state=str(auth_state_path))
    try:
        yield context
    finally:
        context.close()


@pytest.fixture
def super_admin_page(authenticated_context):
    page = authenticated_context.new_page()
    try:
        yield page
    finally:
        page.close()


@pytest.fixture
def login_page(page, base_url):
    LoginPage(page).open(base_url)
    return page


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.trust_env = False

    def get(self, path):
        return self.session.get(self.base_url + path, timeout=10)

    def post(self, path, **kwargs):
        return self.session.post(self.base_url + path, timeout=10, **kwargs)

    def delete(self, path):
        return self.session.delete(self.base_url + path, timeout=10)


@pytest.fixture
def api(base_url):
    client = ApiClient(base_url)
    try:
        yield client
    finally:
        client.session.close()


@pytest.fixture
def resource_name(worker_id):
    def build(prefix):
        label = str(prefix).strip() or "resource"
        return f"{label}-{worker_id}-{uuid4().hex[:6]}"

    return build


@pytest.fixture
def track(api, worker_id):
    registry = []

    def register(resource_type, resource_id):
        if resource_type != "role" or resource_id is None or resource_id == "":
            raise ValueError("Expected a role created by this test and its ID")
        registry.append((resource_type, str(resource_id), worker_id))

    register.worker_id = worker_id
    yield register
    errors = []
    for resource_type, resource_id, owner in reversed(registry):
        try:
            response = api.delete(f"/api/roles/{quote(resource_id, safe='')}")
            if response.status_code not in (200, 204, 404):
                errors.append(f"{owner} {resource_type}/{resource_id}: HTTP {response.status_code}")
        except requests.RequestException as exc:
            errors.append(f"{owner} {resource_type}/{resource_id}: {type(exc).__name__}")
    if errors:
        pytest.fail("Cleanup failed: " + "; ".join(errors))
