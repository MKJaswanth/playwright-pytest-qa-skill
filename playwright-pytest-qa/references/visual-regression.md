# Visual Regression Testing Reference

Use Playwright visual comparisons for stable pages, critical layouts, and high-value UI states.

## Basic screenshot assertion

```python
from playwright.sync_api import expect

def test_dashboard_visual(super_admin_page):
    super_admin_page.goto("/dashboard")
    expect(super_admin_page).to_have_screenshot("dashboard.png")
```

## Component or region screenshot

Prefer region screenshots when the full page contains dynamic content:

```python
from playwright.sync_api import expect

def test_roles_table_visual(super_admin_page):
    super_admin_page.goto("/roles")
    table = super_admin_page.get_by_test_id("roles-table")
    expect(table).to_have_screenshot("roles-table.png")
```

## Mask dynamic regions

Mask timestamps, counters, generated avatars, random IDs, ads, charts with live data, and user-specific content:

```python
from playwright.sync_api import expect

def test_profile_visual(super_admin_page):
    super_admin_page.goto("/profile")
    expect(super_admin_page).to_have_screenshot(
        "profile.png",
        mask=[
            super_admin_page.get_by_test_id("last-login"),
            super_admin_page.get_by_test_id("avatar"),
        ],
    )
```

## Generate or update baselines

```bash
pytest tests/visual/ --update-snapshots
```

Commit baseline screenshots only after review.

## CI guidance

Visual baselines are sensitive to OS, browser, fonts, rendering, viewport size, and timezone.

For reliable CI:

- Generate baselines in the same environment where CI runs.
- Pin browser choice and viewport size.
- Avoid full-page screenshots when content is dynamic.
- Use deterministic test data.
- Mask or stabilize clocks, animations, charts, and third-party widgets.
- Disable animations where possible.

## Suggested viewport fixture

```python
@pytest.fixture
def visual_page(browser_instance):
    ctx = browser_instance.new_context(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    page = ctx.new_page()
    yield page
    ctx.close()
```

## When to use visual tests

Good candidates:

- dashboards
- forms
- navigation layouts
- role/permission tables
- invoice or report screens
- empty/error/loading states

Poor candidates:

- pages with constantly changing data
- highly animated screens
- third-party embedded widgets
- dashboards with live charts unless mocked or masked
