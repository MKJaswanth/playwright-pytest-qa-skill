# HTML Reports And Failure Evidence

The bundled starter uses `pytest-html>=4.1,<5`, with
`--html=reports/report.html --self-contained-html` in `pytest.ini`.
No custom report plugin or files from another conversation are required.

The HTML report contains pytest outcomes, durations, errors, and captured output.
Screenshots, videos, and traces are separate artifacts; sharing only the HTML file
does not include these. Do not promise trend dashboards or embedded videos.

## Retained Browser Artifacts

```ini
[pytest]
addopts =
    --screenshot=only-on-failure
    --video=retain-on-failure
    --tracing=retain-on-failure
    --output=reports/failures
    --html=reports/report.html
    --self-contained-html
```

Use pytest-playwright's managed `page`, `context`, or `new_context` fixtures.
Direct calls to `browser.new_context()` and manual browser launch do not inherit
the plugin's CLI-managed evidence capture. API-only tests and errors before page
creation cannot supply browser screenshots.

## Runner And History

Copy `../assets/starter/run_tests.py` into the generated project.
It removes a stale latest report before execution, invokes pytest with the current
Python interpreter, archives the report with a UTC timestamp, and returns pytest's
exit status. An archive error also produces a nonzero status. When
`APP_START_CMD` is set, the same process starts the app, waits for
`HEALTHCHECK_URL` or `BASE_URL`, and stops the process tree before returning
that status. Accessibility assertion text from
[accessibility.md](accessibility.md) is part of the pytest failure captured here.

```bash
python run_tests.py
python -m playwright show-trace reports/failures/path/to/trace.zip
```

Upload the complete reports directory in CI with `if: always()`. Check retained
files with an intentionally failed browser test before claiming artifact support.
The repository's `scripts/verify_starter.py` performs this check in a temporary
copy and also verifies cleanup after failure and runner exit codes.
