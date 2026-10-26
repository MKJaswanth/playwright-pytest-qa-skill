# API Mocking

Use mocked responses for frontend empty/error states, not to claim backend
integration coverage. Register routes before navigation and use exact endpoints.

These examples run against the bundled local demo:

```python
from playwright.sync_api import expect

def test_mock_empty_roles(page, base_url):
    page.route("**/api/roles", lambda route: route.fulfill(json=[]))
    page.goto(base_url)
    expect(page.get_by_text("No roles found", exact=True)).to_be_visible()

def test_mock_role(page, base_url):
    page.route("**/api/roles", lambda route: route.fulfill(
        json=[{"id": "demo", "name": "Mocked role"}],
    ))
    page.goto(base_url)
    expect(page.get_by_role("listitem")).to_have_text("Mocked role")
```

Adapt response shapes and UI expectations to the actual application's contract.
Blocking sleeps inside synchronous route handlers are not a reliable way to
assert loading states. Use an explicitly controlled pending request with an
async test setup if testing loading behavior.

Use real requests for authentication, resource creation/deletion, and critical
end-to-end flows. Keep mock payloads small and maintain them with the API schema.
