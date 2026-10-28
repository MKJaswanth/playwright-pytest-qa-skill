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
Actions secrets and consumed by their fixtures. Map `SUPER_ADMIN_EMAIL` and
`SUPER_ADMIN_PASSWORD` from secrets. Do not commit credentials or files under
`.auth/`. Untrusted fork PRs do not receive repository secrets; keep the local
demo as a check that does not need an external account.

## App Process

`run_tests.py` starts `APP_START_CMD` and each non-empty line of `APP_START_CMDS`
when those variables are set. It polls `HEALTHCHECK_URL`, or `BASE_URL` when
no health URL is set, using exponential backoff until `APP_START_TIMEOUT`
seconds (default 60). Pytest then runs, and the runner always terminates the
server process group, including child processes. A process that exits early or
never becomes ready fails the job before pytest and returns a nonzero status.
The bundled demo starts its own server inside the `base_url` fixture, so CI
for this repository leaves `APP_START_CMD` unset.

```yaml
      - run: python run_tests.py --browser chromium
        env:
          APP_START_CMD: npm run dev
          BASE_URL: http://127.0.0.1:3000
          SUPER_ADMIN_EMAIL: ${{ secrets.SUPER_ADMIN_EMAIL }}
          SUPER_ADMIN_PASSWORD: ${{ secrets.SUPER_ADMIN_PASSWORD }}
```

Leave retries off by default. Add selected retries after investigating failures.
Add `-n` only after worker-isolated names and cleanup are in place; see
[parallelism.md](parallelism.md). Use `--browser` for pytest-managed fixtures;
arbitrary `BROWSER` or `HEADLESS` environment variables do nothing unless your
own configuration consumes them. Upload artifacts after failures and preserve
the test process's exit status.
