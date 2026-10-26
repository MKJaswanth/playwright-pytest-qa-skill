from pages.roles_page import RolesPage


def test_create_role_ui(page, base_url, track):
    roles = RolesPage(page)
    roles.open(base_url)
    role_id = roles.create("UI demo role")
    track("role", role_id)
    roles.expect_role("UI demo role")


def test_created_role_was_cleaned_up(api):
    assert api.get("/api/roles").json() == []


def test_create_role_api(api, track):
    response = api.post("/api/roles", json={"name": "API demo role"})
    assert response.status_code == 201
    track("role", response.json()["id"])
    assert response.json()["name"] == "API demo role"


def test_empty_roles_ui(page, base_url):
    roles = RolesPage(page)
    roles.open(base_url)
    roles.expect_empty()


def test_reject_empty_role_name(api):
    response = api.post("/api/roles", json={"name": ""})
    assert response.status_code == 400
