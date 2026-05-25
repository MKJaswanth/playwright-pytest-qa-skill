# API Mocking Reference

Use `page.route()` when the test goal is frontend behavior, not backend integration.

## Decision rule

Use real APIs for:

- critical end-to-end flows
- authentication
- permissions
- cleanup verification
- API contract confidence

Use mocked APIs for:

- empty states
- error states
- loading states
- permission-specific frontend states
- hard-to-create backend conditions
- slow responses and timeout behavior
- frontend-only visual regression tests

## Mock a successful empty response

```python
def test_empty_roles_state(super_admin_page):
    super_admin_page.route(
        "**/api/roles**",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"data":[]}',
        ),
    )

    super_admin_page.goto("/roles")
    assert "No roles found" in super_admin_page.text_content("body")
```

## Mock a server error

```python
def test_roles_server_error(super_admin_page):
    super_admin_page.route(
        "**/api/roles**",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body='{"message":"Internal server error"}',
        ),
    )

    super_admin_page.goto("/roles")
    assert "Unable to load roles" in super_admin_page.text_content("body")
```

## Mock slow backend response

```python
import time

def test_roles_loading_state(super_admin_page):
    def slow_response(route):
        time.sleep(2)
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"data":[]}',
        )

    super_admin_page.route("**/api/roles**", slow_response)
    super_admin_page.goto("/roles")
    assert "Loading" in super_admin_page.text_content("body")
```

## Modify a real response

Use `route.fetch()` when you want most of the real backend response but need to alter one field:

```python
import json

def test_role_permission_banner(super_admin_page):
    def patch_roles(route):
        response = route.fetch()
        body = response.json()
        body["data"][0]["permission_count"] = 0
        route.fulfill(
            response=response,
            body=json.dumps(body),
        )

    super_admin_page.route("**/api/roles**", patch_roles)
    super_admin_page.goto("/roles")
    assert "No permissions assigned" in super_admin_page.text_content("body")
```

## Keep mocks maintainable

- Put repeated mock payloads in `fixtures/api_payloads.py`.
- Use route patterns that match the exact endpoint.
- Keep mocked tests separate from true end-to-end tests when possible.
- Name tests clearly so reports show whether a test is mocked or real API backed.
- Do not use mocks to claim backend coverage.
