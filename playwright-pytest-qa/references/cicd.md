# CI Execution

The repository's `.github/workflows/validate.yml` installs the bundled starter,
runs verification, executes the demo, builds packages, and uploads evidence.
It uses no staging credentials and adds no recurring schedule.

For a generated application suite, adapt this workflow:

```yaml
name: QA tests
on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  tests:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements.txt
      - run: python -m playwright install --with-deps chromium
      - run: python run_tests.py --browser chromium
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: qa-reports
          path: reports/
```

Application suites need their actual base URL and authentication supplied through
Actions secrets and consumed by their fixtures. Do not commit credentials or
authentication state. Untrusted fork PRs do not receive repository secrets;
keep the local demo as a credential-free check.

Leave retries off by default. Add selected retries after investigating failures.
Use `--browser` for pytest-managed fixtures; arbitrary `BROWSER` or `HEADLESS`
environment variables do nothing unless your own configuration consumes them.
Upload artifacts after failures and preserve the test process's exit status.
