# CI/CD Reference

Use CI/CD to run the suite on every pull request, scheduled test run, or release candidate.

## GitHub Actions workflow

Create this file in the generated QA project:

```text
.github/workflows/tests.yml
```

```yaml
name: Playwright Pytest QA

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "30 2 * * *"

jobs:
  tests:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install Playwright browsers
        run: playwright install --with-deps chromium

      - name: Run tests
        run: pytest tests/ -v --reruns 2 --reruns-delay 1
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
          API_BASE_URL: ${{ secrets.API_BASE_URL }}
          SUPER_ADMIN_EMAIL: ${{ secrets.SUPER_ADMIN_EMAIL }}
          SUPER_ADMIN_PASSWORD: ${{ secrets.SUPER_ADMIN_PASSWORD }}
          SUPER_ADMIN_TOKEN: ${{ secrets.SUPER_ADMIN_TOKEN }}
          HEADLESS: "true"
          BROWSER: "chromium"
          CLEANUP_MODE: "per_resource"

      - name: Upload reports and failure artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: qa-reports
          path: |
            reports/
            test-results/
```

## Required GitHub secrets

Configure these in GitHub:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Recommended secrets:

```text
BASE_URL
API_BASE_URL
SUPER_ADMIN_EMAIL
SUPER_ADMIN_PASSWORD
SUPER_ADMIN_TOKEN
AGENT_EMAIL
AGENT_TOKEN
```

Never commit `.env` files, tokens, passwords, session storage files, or authentication cookies.

## CI artifact strategy

Always upload reports even when tests fail:

```yaml
if: always()
```

The artifact should include:

- `reports/milestone1_report.html`
- `reports/history.json`
- failure screenshots
- videos
- `trace.zip`

## Debugging CI trace files locally

After a failed run:

1. Open the GitHub Actions run.
2. Download the `qa-reports` artifact.
3. Unzip it locally.
4. Run:

```bash
playwright show-trace path/to/trace.zip
```

Use the trace viewer to inspect actions, DOM snapshots, network requests, console logs, and timing.

## Matrix testing option

Use this only when the suite is stable enough to justify cross-browser coverage:

```yaml
strategy:
  fail-fast: false
  matrix:
    browser: [chromium, firefox, webkit]
```

Then pass the browser into the test run:

```yaml
env:
  BROWSER: ${{ matrix.browser }}
```

Start with Chromium in CI. Add other browsers after selectors, waits, and visual baselines are stable.
