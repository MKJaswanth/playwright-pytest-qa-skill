---
name: playwright-pytest-qa
description: Build or improve Python Playwright and pytest UI/API test suites, including test data cleanup, failure artifacts, HTML reports, and CI. Use for Python browser automation and QA framework requests.
---

# Playwright + pytest QA

Build tests against observed UI and API contracts. Inspect an existing suite
before changing its fixtures or structure. Preserve the user's stack.

## Executable Starter

`assets/starter/` contains a local HTTP demo app, page objects, UI/API tests,
per-test cleanup, HTML reporting, and a runner that preserves pytest's exit code.
It needs no account or external app. Copy the starter for new suites; adapt only
needed parts for existing projects. Replace demo contracts with observed ones.

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python run_tests.py
```

## Browser Fixtures And Failure Evidence

Use pytest-playwright's `page`, `context`, or `new_context` fixtures. Customize
`browser_context_args` as needed. Manually launching a browser or calling
`browser.new_context()` bypasses the plugin's CLI-managed artifact capture.

```python
import os
import pytest
from playwright.sync_api import expect

@pytest.fixture
def super_admin_page(page, base_url):
    page.goto(f"{base_url}/login")
    page.get_by_label("Email").fill(os.environ["SUPER_ADMIN_EMAIL"])
    page.get_by_label("Password").fill(os.environ["SUPER_ADMIN_PASSWORD"])
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page).to_have_url(f"{base_url}/dashboard")
    return page
```

Adapt the example paths and labels. Store credentials in environment variables;
keep them out of reports.

```ini
[pytest]
testpaths = tests
addopts =
    --tb=short
    --screenshot=only-on-failure
    --video=retain-on-failure
    --tracing=retain-on-failure
    --output=reports/failures
    --html=reports/report.html
    --self-contained-html
```

Install `pytest-html` for HTML options. Browser failures should retain screenshots,
video, and traces. API-only tests and failures before a page exists cannot provide
browser evidence. See [report.md](references/report.md).

## Test Writing And Cleanup

Use page objects for repeated actions, role/label/test-id locators, and retrying
assertions. Avoid positional selectors for newly created resources. The starter
defines all fixtures and page objects used here:

```python
from pages.roles_page import RolesPage

def test_create_role(page, base_url, track):
    roles = RolesPage(page)
    roles.open(base_url)
    role_id = roles.create("Demo role")
    track("role", role_id)
    roles.expect_role("Demo role")

def test_create_role_api(api, track):
    response = api.post("/api/roles", json={"name": "API demo role"})
    assert response.status_code == 201
    track("role", response.json()["id"])

def test_empty_roles(page, base_url):
    roles = RolesPage(page)
    roles.open(base_url)
    roles.expect_empty()
```

`track` owns its per-test registry and teardown. Register only this test's created
resources immediately after creation. Delete dependents before parents. Surface
cleanup failures as teardown errors. Read [cleanup.md](references/cleanup.md)
when adapting cleanup to real APIs.

## Run And Debug

`python run_tests.py` archives the current HTML report and preserves pytest's exit
code. Direct `python -m pytest` also works. Share retained artifacts alongside
the HTML report when debugging is needed.

```bash
python run_tests.py -k create
python -m playwright show-trace reports/failures/path/to/trace.zip
```

Check exit status and report contents. Tests, collection errors, and teardown
errors must not be described as successful runs.

## Optional References

Load only references relevant to the request:

- [cleanup.md](references/cleanup.md): resource ownership and deletion endpoints.
- [report.md](references/report.md): HTML reports and artifact validation.
- [terminal.md](references/terminal.md): optional Rich display; validate its hooks
  before combining with retries or parallel workers.
- [flakiness.md](references/flakiness.md): opt-in retries and stabilization.
- [cicd.md](references/cicd.md): CI execution and artifact upload.
- [visual-regression.md](references/visual-regression.md): Python screenshot
  comparison dependencies and baseline review.
- [api-mocking.md](references/api-mocking.md): frontend isolation; mocks do not
  establish backend coverage.

Keep retries off by default. Add parallel execution after data isolation and
report aggregation are checked. Python screenshot comparison requires an
explicit comparison plugin; do not use JavaScript-only APIs.
