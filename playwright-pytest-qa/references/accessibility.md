# Accessibility Checks

Automated scans do not replace keyboard and screen-reader checks. Use them as
a regression gate for WCAG 2.1 A and AA issues that axe-core can detect.

Install the optional scanner beside the starter dependencies:

```bash
python -m pip install axe-playwright-python
```

`axe-playwright-python` provides `Axe` in `axe_playwright_python.sync_playwright`.
`Axe().run(page)` returns results whose `violations_count` and
`generate_report()` come from axe-core. The assertion text is captured in the
pytest-html report. Attach the same text with the `extras` fixture so the
summary is visible without opening the traceback.

```python
import pytest_html
from axe_playwright_python.sync_playwright import Axe

WCAG_21_AA = {
    "resultTypes": ["violations"],
    "runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21aa"]},
}

def test_roles_have_no_wcag_aa_violations(page, base_url, extras):
    page.goto(base_url)
    results = Axe().run(page, options=WCAG_21_AA)
    report = results.generate_report()
    if results.violations_count:
        extras.append(pytest_html.extras.text(report, name="axe violations"))
    assert results.violations_count == 0, report
```

Scan a settled page: wait with a web-first assertion for the heading or main
region before calling `Axe().run`. Pass a locator context when the scan should
cover one region instead of the whole document. Review new serious and critical
rules before updating a snapshot of known violations.

Playwright 1.49 and newer can lock accessible structure without axe:

```python
from playwright.sync_api import expect

expect(page.locator("main")).to_match_aria_snapshot('- heading "Roles" [level=1]')
```

Commit the snapshot only after a human checks it. An aria snapshot does not
judge color contrast; keep the axe scan for WCAG 2.1 AA rules axe can evaluate.
