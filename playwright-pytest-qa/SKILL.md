---
name: playwright-pytest-qa
description: >
  Full end-to-end QA automation skill for writing, running, and reporting test cases
  using Playwright and pytest. Use this skill whenever the user says "write test cases",
  "automate test cases", "create automated tests", "write automation", or anything related
  to writing UI or API test cases with Playwright and pytest. Covers the complete workflow:
  project setup, Page Object Model structure, test writing with cleanup (no data buildup
  on staging), live terminal display, and professional HTML report generation for managers
  and clients. Always trigger this skill when test case writing or automation is mentioned
  — even casually like "can you write tests for this" or "automate this flow".
  Also covers enterprise QA practices such as flaky test retries, CI/CD execution,
  visual regression testing, Playwright trace debugging, and API mocking with page.route().
---

# Playwright + pytest QA Automation Skill

Complete workflow for building a professional test automation suite from scratch.
Covers 6 pillars: **Setup → Test Writing → Cleanup → Terminal Display → Reports → Enterprise Readiness**

---

## PILLAR 1 — PROJECT SETUP

### Folder Structure
```
project/
├── conftest.py                  ← fixtures, plugins, browser setup
├── pytest.ini                   ← pytest config
├── requirements.txt
├── run_tests.sh                 ← one-command test runner
├── config/
│   └── config.py                ← base URL, credentials, tokens
├── pages/                       ← Page Object Models (one file per page)
├── utils/
│   ├── cleanup_registry.py      ← tracks created resource IDs
│   ├── cleanup_client.py        ← calls DELETE endpoints after each test
│   ├── live_terminal.py         ← Rich-based scoreboard display
│   └── report_plugin.py         ← auto-generates HTML report
├── fixtures/
│   └── test_data.py             ← reusable test data / Faker helpers
└── tests/
    └── milestone1/              ← one file per user story
        ├── test_us001_roles.py
        ├── test_us002_permissions.py
        └── ...
```

### requirements.txt
```
playwright>=1.44.0
pytest>=8.0.0
pytest-playwright>=0.5.0
pytest-xdist>=3.5.0
python-dotenv>=1.0.0
requests>=2.31.0
faker>=24.0.0
rich>=13.0.0
pytest-rerunfailures>=14.0
```

### pytest.ini
```ini
[pytest]
addopts =
    -v
    --tb=short
    --reruns 2                   ; retry flaky tests 2 times
    --reruns-delay 1             ; wait 1s between retries
    --screenshot=only-on-failure
    --video=retain-on-failure
    --tracing=retain-on-failure
    --output=reports/failures

testpaths = tests
```

### config/config.py pattern
```python
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    BASE_URL         = os.getenv("BASE_URL", "https://your-staging-url.com")
    API_BASE_URL     = os.getenv("API_BASE_URL", "https://your-staging-url.com/api")
    BROWSER          = os.getenv("BROWSER", "chromium")
    HEADLESS         = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO          = int(os.getenv("SLOW_MO", "0"))
    CLEANUP_MODE     = os.getenv("CLEANUP_MODE", "per_resource")  # or "bulk"

    SUPER_ADMIN_EMAIL    = os.getenv("SUPER_ADMIN_EMAIL")
    SUPER_ADMIN_PASSWORD = os.getenv("SUPER_ADMIN_PASSWORD")
    SUPER_ADMIN_TOKEN    = os.getenv("SUPER_ADMIN_TOKEN")
    AGENT_EMAIL          = os.getenv("AGENT_EMAIL")
    AGENT_TOKEN          = os.getenv("AGENT_TOKEN")
    # add more roles as needed
```

---

## PILLAR 2 — TEST WRITING

### Page Object Model (POM)
All selectors live in `pages/` — never hardcode selectors inside tests.

```python
# pages/roles_page.py
class RolesPage:
    ADD_BTN    = '[data-testid="add-role-btn"]'
    NAME_INPUT = '[data-testid="role-name-input"]'
    SAVE_BTN   = '[data-testid="save-role-btn"]'
    SUCCESS    = '[data-testid="role-created-success"]'
    ROLE_ROW   = '[data-testid="role-row"]:last-child'

    def __init__(self, page):
        self.page = page

    def create_role(self, name, permission_selector):
        self.page.click(self.ADD_BTN)
        self.page.fill(self.NAME_INPUT, name)
        self.page.check(permission_selector)
        self.page.click(self.SAVE_BTN)
        self.page.wait_for_selector(self.SUCCESS)
        return self.page.get_attribute(self.ROLE_ROW, "data-id")
```

### Selector priority (best → worst)
```
data-testid="submit"   ← best, never changes
id="submit-btn"        ← very good
aria-label="Submit"    ← good
name="email"           ← good for form fields
text("Submit")         ← ok for buttons
.css-class             ← avoid, changes often
```

### 3 Test Patterns

**Pattern A — UI test that creates data**
```python
def test_create_role(super_admin_page, track):
    # create via browser
    role_id = roles_page.create_role("TestRole", '[data-testid="perm-view"]')
    track("role", role_id)   # ← register for auto-cleanup
    assert role_id is not None
```

**Pattern B — API test that creates data**
```python
def test_audit_log(api, track):
    resp = api.post("/roles", payload={"name": "AuditRole"}, token=token)
    track("role", resp.json()["data"]["id"])   # ← register immediately
    assert resp.status_code == 201
```

**Pattern C — Read-only, no cleanup needed**
```python
def test_default_roles_visible(super_admin_page):
    # just read/assert — no track() needed
    assert "Super Admin" in page.text_content('[data-testid="roles-table"]')
```

### Apply autoclean to whole test file
Add this one line at the top of any test file that creates data:
```python
pytestmark = pytest.mark.usefixtures("autoclean")
```

---

## PILLAR 3 — CLEANUP (no data buildup on staging)

See → `references/cleanup.md` for full implementation.

**How it works in 4 steps:**
1. Test creates a resource → calls `track("type", id)`
2. Test finishes (pass/fail/error — doesn't matter)
3. `autoclean` fixture fires automatically
4. `CleanupClient` calls your DELETE API for each registered ID

**Two cleanup modes — set in `.env`:**
- `CLEANUP_MODE=per_resource` → `DELETE /api/roles/{id}` per item
- `CLEANUP_MODE=bulk` → `POST /api/test/cleanup` with full list

**Resource type map** (update paths to match your API):
```python
RESOURCE_DELETE_PATHS = {
    "role":        "/roles/{id}",
    "user":        "/users/{id}",
    "country":     "/masters/countries/{id}",
    "state":       "/masters/states/{id}",
    "city":        "/masters/cities/{id}",
    "lead_source": "/masters/lead-sources/{id}",
    "team":        "/masters/teams/{id}",
    "project":     "/masters/projects/{id}",
    "lead":        "/leads/{id}",
}
```

---

## PILLAR 4 — LIVE TERMINAL DISPLAY

See → `references/terminal.md` for full implementation.

Install: `pip install rich`

**What it shows as tests run:**
```
🚀  Lead Management — Milestone 1   480 tests collected

  1/480  █░░░░░░░░░░░░░░░░░░░  ✓  TC_001  Create Role Valid        Roles Mgmt   0.82s   PASSED
  2/480  ███░░░░░░░░░░░░░░░░░  ✓  TC_002  Role Name Mandatory      Roles Mgmt   1.10s   PASSED
  3/480  ████░░░░░░░░░░░░░░░░  ✗  TC_003  Duplicate Role           Roles Mgmt   1.55s   FAILED
  ── 5 run · 4 passed · 1 failed · 80% pass rate · 12s elapsed ──
```

**End of run summary panel:**
```
╭─────────────── Test Run Summary ───────────────╮
│  ✓  ALL TESTS PASSED                           │
│     Total   : 480                              │
│     Passed  : 478                              │
│     Failed  : 2                                │
│     Rate    : 99.6%                            │
│     Time    : 4m 32s                           │
╰────────────────────────────────────────────────╯
```

---

## PILLAR 5 — HTML REPORT GENERATION

See → `references/report.md` for full implementation.

Auto-generates `reports/milestone1_report.html` after every run.
No extra commands needed — wired into `conftest.py`.

**What the report contains:**
- Stat cards: Total, Passed, Failed, Skipped, Duration, Pass Rate
- Donut chart: visual pass/fail ratio
- Trend line: pass rate across last 10 runs
- Module breakdown: per user story with colour-coded progress bars
- Full test table: status badge, TC ID, duration, screenshot, error message
- Filter buttons: show only Passed / Failed / Skipped
- Search box: filter by test name or TC ID

**To save reports after each run (never overwrite):**
```bash
# run_tests.sh
#!/bin/bash
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M')
pytest tests/milestone1/ -v
mkdir -p reports/history
cp reports/milestone1_report.html reports/history/report_$TIMESTAMP.html
echo "✅ Report saved → reports/history/report_$TIMESTAMP.html"
```

**Report folder structure:**
```
reports/
├── milestone1_report.html        ← always the latest run
├── history.json                  ← trend data (last 10 runs)
├── failures/                     ← screenshots, videos, traces
│   └── test_tc002_role_name/
│       ├── test-failed-1.png
│       ├── video.webm
│       └── trace.zip
└── history/
    ├── report_2024-01-14_09-00.html
    ├── report_2024-01-14_14-30.html
    └── report_2024-01-15_09-15.html
```

---

## PILLAR 6 — ENTERPRISE READINESS

Use these practices for suites that must run reliably in CI/CD and produce actionable failure evidence.

**Flaky test management** — See `references/flakiness.md`.
- Add `pytest-rerunfailures` to requirements.
- Use retries only for infrastructure noise, network blips, and browser timing variance.
- Never use retries to hide deterministic product bugs.

**CI/CD execution** — See `references/cicd.md`.
- Add a GitHub Actions workflow under `.github/workflows/tests.yml`.
- Install Python dependencies and Playwright browsers in the pipeline.
- Store URLs, users, passwords, and tokens in GitHub Actions secrets.
- Upload `reports/` as an artifact with `if: always()`.

**Visual regression testing** — See `references/visual-regression.md`.
- Use `expect(page).to_have_screenshot()` for stable pages and critical UI states.
- Generate baselines in the same OS/browser/font environment used by CI.
- Mask dynamic regions such as timestamps, avatars, counters, ads, and random data.

**Trace viewer debugging** — See `references/report.md`.
- Keep `--tracing=retain-on-failure` enabled.
- Download `trace.zip` from CI artifacts and inspect it with `playwright show-trace`.

**API mocking** — See `references/api-mocking.md`.
- Use `page.route()` for frontend-only states, empty states, error states, slow responses, and hard-to-create backend scenarios.
- Use real APIs for end-to-end confidence paths and cleanup validation.

---

## CONFTEST.PY — WIRING EVERYTHING TOGETHER

```python
import os, sys, pytest
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__))

from config.config import Config
from utils.cleanup_registry import register as _register, pop_all
from utils.cleanup_client import CleanupClient
from utils.report_plugin import ReportPlugin
from utils.live_terminal import LiveTerminalPlugin


def pytest_configure(config):
    config.pluginmanager.register(ReportPlugin(),       "custom_html_report")
    config.pluginmanager.register(LiveTerminalPlugin(), "live_terminal")


@pytest.fixture(scope="session")
def cleanup_client():
    return CleanupClient()

@pytest.fixture(autouse=False)
def autoclean(cleanup_client):
    yield
    cleanup_client.delete_all(pop_all())

@pytest.fixture(autouse=False)
def track():
    return _register

@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = getattr(p, Config.BROWSER).launch(
            headless=Config.HEADLESS, slow_mo=Config.SLOW_MO)
        yield browser
        browser.close()

@pytest.fixture
def super_admin_page(browser_instance):
    ctx = browser_instance.new_context()
    p = ctx.new_page()
    p.goto(f"{Config.BASE_URL}/login")
    p.fill('input[name="email"]',    Config.SUPER_ADMIN_EMAIL)
    p.fill('input[name="password"]', Config.SUPER_ADMIN_PASSWORD)
    p.click('button[type="submit"]')
    p.wait_for_url(f"{Config.BASE_URL}/dashboard**", timeout=15_000)
    yield p
    ctx.close()

# add agent_page, admin_page, manager_page following same pattern

@pytest.fixture
def api():
    import requests
    class ApiClient:
        def __init__(self): self.base = Config.API_BASE_URL
        def _h(self, token=None):
            h = {"Content-Type": "application/json"}
            if token: h["Authorization"] = f"Bearer {token}"
            return h
        def get(self, path, token=None, params=None):
            return requests.get(f"{self.base}{path}", headers=self._h(token), params=params, timeout=30)
        def post(self, path, payload=None, token=None):
            return requests.post(f"{self.base}{path}", json=payload, headers=self._h(token), timeout=30)
        def delete(self, path, token=None):
            return requests.delete(f"{self.base}{path}", headers=self._h(token), timeout=30)
    return ApiClient()
```

---

## QUICK REFERENCE — COMMON COMMANDS

```bash
# Install everything
pip install -r requirements.txt
playwright install chromium

# Run all milestone 1 tests
pytest tests/milestone1/ -v

# Run with 2 retries for flaky tests
pytest --reruns 2 --reruns-delay 1

# Debug with Trace Viewer
playwright show-trace reports/failures/path/to/trace.zip

# Update visual snapshots
pytest --update-snapshots

# Run in parallel (faster)
pytest tests/milestone1/ -v -n auto

# Run and save timestamped report
./run_tests.sh
```

---

## DECISION GUIDE — WHICH PATTERN TO USE

| Situation | Use |
|-----------|-----|
| Test creates data via browser | Pattern A + `track()` |
| Test creates data via API | Pattern B + `track()` |
| Test only reads / asserts | Pattern C (no track) |
| Whole file creates data | `pytestmark = pytest.mark.usefixtures("autoclean")` at top |
| Read-only file | No autoclean marker needed |

---

## REFERENCES

- `references/cleanup.md`           — Full cleanup_registry.py + cleanup_client.py code
- `references/terminal.md`          — Full live_terminal.py code
- `references/report.md`            — Full report_plugin.py code
- `references/flakiness.md`         — Retry policies and stabilization rules
- `references/cicd.md`              — GitHub Actions workflow and artifact handling
- `references/visual-regression.md` — Screenshot comparison strategy
- `references/api-mocking.md`       — page.route() patterns for frontend-only states
