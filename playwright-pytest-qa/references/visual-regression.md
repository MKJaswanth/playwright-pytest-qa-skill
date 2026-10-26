# Python Visual Regression

Python Playwright supports taking screenshots, but the JavaScript Playwright
Test `toHaveScreenshot` assertion is not provided by Python's `expect(page)`.
Do not generate `expect(page).to_have_screenshot()`.

For pixel comparison, explicitly install a Python comparison plugin, for example
`pytest-playwright-visual`, and follow its version-specific fixture and baseline
options. It is optional and is not installed or validated by the starter.
Verify the chosen plugin's API before generating tests.

Without a comparison plugin, capturing a screenshot is evidence, not a visual
regression assertion:

```python
def test_capture_roles(page, base_url, tmp_path):
    page.goto(base_url)
    page.get_by_role("heading", name="Roles", exact=True).wait_for()
    page.screenshot(path=tmp_path / "roles.png", animations="disabled")
```

For comparisons, generate and review baselines under the same OS, browser,
fonts, viewport, scale, and locale as CI. Stabilize data and clocks, disable
animations, and mask dynamic regions using `page.screenshot(mask=[...])`.
Use pytest-managed page/context fixtures so failure artifacts remain available.

Keep pixel comparison distinct from accessibility tree snapshots. When using
supported Playwright versions, `to_match_aria_snapshot` checks accessible structure,
not rendered pixels.
