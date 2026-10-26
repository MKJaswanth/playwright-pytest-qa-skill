from threading import Thread
from urllib.parse import quote

import pytest
import requests

from demo_app import make_server


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


@pytest.fixture
def browser_context_args(browser_context_args, base_url):
    return {**browser_context_args, "base_url": base_url}


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
def track(api):
    registry = []

    def register(resource_type, resource_id):
        if resource_type != "role" or resource_id is None or resource_id == "":
            raise ValueError("Expected a role created by this test and its ID")
        registry.append((resource_type, str(resource_id)))

    yield register
    errors = []
    for resource_type, resource_id in reversed(registry):
        try:
            response = api.delete(f"/api/roles/{quote(resource_id, safe='')}")
            if response.status_code not in (200, 204, 404):
                errors.append(f"{resource_type}/{resource_id}: HTTP {response.status_code}")
        except requests.RequestException as exc:
            errors.append(f"{resource_type}/{resource_id}: {type(exc).__name__}")
    if errors:
        pytest.fail("Cleanup failed: " + "; ".join(errors))
