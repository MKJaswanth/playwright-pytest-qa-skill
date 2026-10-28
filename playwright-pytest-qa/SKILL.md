---
name: playwright-pytest-qa
description: >-
  Build and repair production Python Playwright and pytest UI/API test suites
  with page object model, storage_state login caching, pytest-xdist worker
  isolation, test-data cleanup, HTML reports, failure traces, accessibility
  scans, and CI. Use when the user mentions playwright, pytest, e2e, qa,
  api testing, page object model, or flaky tests.
license: MIT
compatibility: Python 3.10+ and Playwright. Optional axe-playwright-python for WCAG scans.
metadata:
  author: MKJaswanth
  version: "1.3.0"
---

# Playwright + pytest QA

Build tests against observed UI and API contracts. Inspect an existing suite
before changing its fixtures or structure. Preserve the user's stack.
Read [anti-patterns.md](references/anti-patterns.md) before writing or rewriting tests.

## Executable Starter

`assets/starter/` contains a local HTTP demo app, page objects, UI/API tests,
session-scoped auth caching, per-test cleanup, HTML reporting, and a runner
that preserves pytest's exit code. It needs no external account. Copy the
starter for new suites; adapt only needed parts for existing projects.

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python run_tests.py
```

The demo seeds `SUPER_ADMIN_EMAIL` and `SUPER_ADMIN_PASSWORD` when they are
unset. Real suites must set both variables and must not commit passwords or
`.auth/` files.

## Authentication

Log in once per worker and reuse Playwright `storage_state`. Do not repeat the
login form in every test. The executable fixtures are `auth_state_path`,
`authenticated_context`, `super_admin_page`, and `login_through_ui` in
`assets/starter/conftest.py`.

For a suite where almost every test is authenticated, load the saved state
from `browser_context_args` so pytest-playwright still records screenshots,
video, and traces:

```python
@pytest.fixture
def browser_context_args(browser_context_args, auth_state_path):
    return {**browser_context_args, "storage_state": str(auth_state_path)}
```

`auth_state_path` is session-scoped. It signs in through the UI with
`os.environ["SUPER_ADMIN_EMAIL"]` and `os.environ["SUPER_ADMIN_PASSWORD"]`,
checks the post-login URL, and writes `.auth/super_admin_<worker>.json`.
The worker segment is `master` outside xdist and the xdist `workerid` otherwise.

Leave `storage_state` off the default context in modules that test login itself.
Use `login_page` and `login_through_ui` for that flow only.
`authenticated_context` and `super_admin_page` open a context with
`storage_state=str(auth_state_path)`. A context created with `browser.new_context()`
does not inherit the plugin's failure artifacts; prefer the `browser_context_args`
override for those tests.

## Browser Fixtures And Failure Evidence

Use pytest-playwright's `page`, `context`, or `new_context` fixtures. Manually
launching a browser bypasses CLI-managed artifact capture.

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
assertions. Name data created on a shared environment with `resource_name`.
The starter defines the fixtures and page objects used here:

```python
from pages.roles_page import RolesPage

def test_create_role(page, base_url, track, resource_name):
    name = resource_name("role")
    roles = RolesPage(page)
    roles.open(base_url)
    role_id = roles.create(name)
    track("role", role_id)
    roles.expect_role(name)

def test_create_role_api(api, track, resource_name):
    name = resource_name("role")
    response = api.post("/api/roles", json={"name": name})
    assert response.status_code == 201
    track("role", response.json()["id"])
```

`track` owns its per-test registry and teardown, records the worker id, and
still runs after assertion failures. Register only this test's created
resources immediately after creation. Delete dependents before parents. Surface
cleanup failures as teardown errors. Read [cleanup.md](references/cleanup.md)
when adapting cleanup to real APIs.

## Local Servers

`python run_tests.py` archives the HTML report and preserves pytest's exit code.
If `APP_START_CMD` is set, the runner starts that process (and each line of
`APP_START_CMDS`), polls `HEALTHCHECK_URL` or `BASE_URL` with exponential backoff,
runs pytest, and terminates the process tree. `APP_START_TIMEOUT` seconds
defaults to 60. A dead process or a timed-out health check exits nonzero and
does not report the suite as passed.

```bash
APP_START_CMD="npm run dev" BASE_URL="http://127.0.0.1:3000" python run_tests.py
```

The demo does not need `APP_START_CMD`; its `base_url` fixture starts the
temporary app. See [cicd.md](references/cicd.md).

## Run And Debug

Direct `python -m pytest` also works. Share retained artifacts alongside the
HTML report when debugging is needed.

```bash
python run_tests.py -k create
python run_tests.py -n 2
python -m playwright show-trace reports/failures/path/to/trace.zip
```

Check exit status and report contents. Tests, collection errors, and teardown
errors must not be described as successful runs. Keep retries off by default.
Parallel workers are opt-in after data isolation; see
[parallelism.md](references/parallelism.md).

## Optional References

Load only references relevant to the request:

- [cleanup.md](references/cleanup.md): resource ownership and deletion endpoints.
- [parallelism.md](references/parallelism.md): `pytest -n` and worker-isolated names.
- [accessibility.md](references/accessibility.md): WCAG 2.1 AA scans and aria snapshots.
- [anti-patterns.md](references/anti-patterns.md): sleeps, non-retrying asserts, silent passes.
- [report.md](references/report.md): HTML reports and artifact validation.
- [terminal.md](references/terminal.md): optional Rich display; validate its hooks
  before combining with retries or parallel workers.
- [flakiness.md](references/flakiness.md): opt-in retries and stabilization.
- [cicd.md](references/cicd.md): CI execution, server startup, and artifact upload.
- [visual-regression.md](references/visual-regression.md): Python screenshot
  comparison dependencies and baseline review.
- [api-mocking.md](references/api-mocking.md): frontend isolation; mocks do not
  establish backend coverage.

Python screenshot comparison requires an explicit comparison plugin; do not use
JavaScript-only APIs.
