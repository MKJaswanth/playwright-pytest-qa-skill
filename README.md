# Playwright + pytest QA Skill

[![Validate skill and starter](https://github.com/MKJaswanth/playwright-pytest-qa-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/MKJaswanth/playwright-pytest-qa-skill/actions/workflows/validate.yml)

A reusable Codex skill for building Python UI/API test suites with Playwright,
pytest, test data cleanup, HTML reports, and retained failure evidence.

Version: **1.2.0**. MIT licensed. Created by [MKJaswanth](https://github.com/MKJaswanth).

## Try The Working Example

Python 3.10+ and a Playwright-supported operating system are required.
From the repository root:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then run:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
cd playwright-pytest-qa/assets/starter
python run_tests.py
```

The demo starts a temporary server on 127.0.0.1, runs five UI/API tests,
and shuts the server down. No external application, API token, or account is needed.
It creates roles and deletes the resources created by each test.

Open `reports/report.html` for results. Timestamped copies are saved under
`reports/history/`. Browser test failures retain screenshots, videos, and traces
under `reports/failures/`.

## Install The Skill

Copy the `playwright-pytest-qa/` directory into your Codex skills directory,
typically `~/.codex/skills/` (on Windows, `%USERPROFILE%\.codex\skills\`).
The directory includes `SKILL.md`, references, and the runnable starter.

The root `playwright-pytest-qa.skill` file is a ZIP archive containing that
directory. Extract it into the skills directory if your client does not provide
an archive installation flow. Reload skills or restart your client as needed.

Example request:

> Use $playwright-pytest-qa to add UI and API tests for my staging app,
> with cleanup, HTML reporting, and failure traces.

Adapt selectors, authentication, and cleanup endpoints to your actual app.
The bundled server is a test demonstration, not a production application.

## What Is Included

- A runnable local example with page objects and five UI/API tests.
- A function-scoped cleanup registry that also runs after assertion failures.
- pytest-managed browser fixtures for automatic failure artifacts.
- Standalone HTML results using pytest-html.
- A Python runner that preserves pytest's exit status while archiving reports.
- References for CI, optional retries, terminal output, API mocking, and Python
  visual regression setup.

The starter runs serially with retries disabled. Advanced integrations require
their documented optional dependencies and application-specific configuration.
HTML reporting uses pytest-html; the illustrative SVG and terminal transcript
under `docs/` and `examples/` are design examples, not measured execution results.

## Verify The Release

From the repository root, with the same virtual environment active:

```bash
python scripts/verify_starter.py
python scripts/build_package.py
```

Verification runs passing tests, deliberately fails a browser test, checks that
cleanup still occurred, and requires a screenshot, video, and trace. It also
checks exit codes for failing tests, empty selection, and invalid arguments.
Intentional failures appear in its output; the verifier itself exits zero only
when all expected outcomes are confirmed.

GitHub Actions repeats this verification and uploads reports and packages.
A badge is evidence only once its linked workflow has actually run.

## Agensi Package

`python scripts/build_package.py` produces:

- `dist/playwright-pytest-qa-1.2.0.zip`: marketplace upload with `SKILL.md` at root.
- `playwright-pytest-qa.skill`: folder-wrapped skill archive.

Both include the MIT license and the same source files. Generated reports,
virtual environments, and caches are excluded. Listing copy is in
[docs/agensi-listing.md](docs/agensi-listing.md).

See [CHANGELOG.md](CHANGELOG.md) for changes.
