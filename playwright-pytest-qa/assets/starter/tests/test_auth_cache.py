import json
import os
import re

from playwright.sync_api import expect

from pages.login_page import LoginPage


def test_dashboard_requires_login(page, base_url):
    page.goto(f"{base_url}/dashboard")
    expect(page).to_have_url(re.compile(r"/login$"))
    expect(page.get_by_role("heading", name="Sign in", exact=True)).to_be_visible()


def test_cached_session_skips_login(super_admin_page, auth_state_path, worker_id):
    if worker_id == "gw0" and "PYTEST_XDIST_WORKER" not in os.environ:
        assert auth_state_path.name == "super_admin_master.json"
    else:
        assert auth_state_path.name == f"super_admin_{worker_id}.json"
    state = json.loads(auth_state_path.read_text(encoding="utf-8"))
    assert any(cookie.get("name") == "session" for cookie in state.get("cookies", []))
    super_admin_page.goto("/dashboard")
    expect(super_admin_page).to_have_url(re.compile(r"/dashboard$"))
    expect(super_admin_page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()
    expect(super_admin_page.get_by_label("Email")).to_have_count(0)


def test_authenticated_context_loads_storage_state(authenticated_context):
    page = authenticated_context.new_page()
    page.goto("/dashboard")
    expect(page).to_have_url(re.compile(r"/dashboard$"))
    expect(page.get_by_label("Email")).to_have_count(0)
    page.close()


def test_login_form_still_reaches_dashboard(login_page, base_url):
    LoginPage(login_page).sign_in(
        base_url,
        os.environ["SUPER_ADMIN_EMAIL"],
        os.environ["SUPER_ADMIN_PASSWORD"],
    )
    expect(login_page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()


def test_login_api_rejects_bad_password(api):
    response = api.post("/api/login", json={
        "email": os.environ["SUPER_ADMIN_EMAIL"],
        "password": "not-the-demo-password",
    })
    assert response.status_code == 401
