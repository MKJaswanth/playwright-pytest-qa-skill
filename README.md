# Playwright + pytest QA Skill

[![Validate skill and starter](https://github.com/MKJaswanth/playwright-pytest-qa-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/MKJaswanth/playwright-pytest-qa-skill/actions/workflows/validate.yml)

A reusable skill for Codex, Claude Code, Cursor, and QASkills.sh that builds
Python UI/API test suites with Playwright, pytest, cached authentication,
worker-isolated test data, HTML reports, and retained failure evidence.

Version: **1.3.0**. MIT licensed. Created by [MKJaswanth](https://github.com/MKJaswanth).

## Install

From a checkout of this repository:

```bash
npx skills add MKJaswanth/playwright-pytest-qa-skill
./scripts/install.sh
```

`./scripts/install.sh` copies `playwright-pytest-qa/` into each detected agent
skills directory. Choose one with `--codex`, `--claude`, `--cursor`, or
`--agents`. `--all` writes every location:

| Agent | Skills path |
| --- | --- |
| Codex | `~/.codex/skills/playwright-pytest-qa` |
| Claude Code | `~/.claude/skills/playwright-pytest-qa` |
| Cursor | `~/.cursor/skills/playwright-pytest-qa` |
| Agents | `~/.agents/skills/playwright-pytest-qa` |

On Windows, the same folders live under `%USERPROFILE%`. Manual install is a
copy of the `playwright-pytest-qa/` directory into one of those paths.
`playwright-pytest-qa.skill` is a ZIP of that directory; extract it if the
client has no archive installer. Reload skills or restart the client afterward.

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

The demo starts a temporary server on 127.0.0.1, runs the UI, API, auth-cache,
and server-lifecycle tests, and shuts the server down. No external application
or API token is required. The demo account is local to that server. Each test
deletes the roles it created.

Open `reports/report.html` for results. Timestamped copies are saved under
`reports/history/`. Browser test failures retain screenshots, videos, and traces
under `reports/failures/`.

To boot your own app before pytest:

```bash
APP_START_CMD="npm run dev" BASE_URL="http://127.0.0.1:3000" python run_tests.py
```

Set `HEALTHCHECK_URL` when the base URL is not the readiness probe.
`APP_START_CMDS` accepts extra commands, one per line. `APP_START_TIMEOUT`
seconds defaults to 60.

## Prompts

Copy one of these to invoke the skill:

> Use $playwright-pytest-qa to add UI and API tests for my staging app, with storage_state login, cleanup, HTML reporting, and failure traces.

> Use playwright-pytest-qa to cache the super-admin session and isolate pytest-xdist data with worker-specific role names.

> Use playwright-pytest-qa to start my dev server from run_tests.py, then run the Playwright pytest suite and keep the pytest exit code.

> Use playwright-pytest-qa to add a WCAG 2.1 AA axe scan and remove sleep-based waits from these tests.

Adapt selectors, authentication, and cleanup endpoints to the actual app.
The bundled server is a test demonstration, not a production application.

## Why This Skill

| Capability | This skill | Playwright Python docs | Playwright Test (JS) |
| --- | --- | --- | --- |
| Python pytest suites and page objects | Runnable starter | API reference | JavaScript runner |
| Per-test cleanup after failures | `track` fixture | — | — |
| Session `storage_state` login cache | Yes, worker-specific file | Documented API | `storageState` in config |
| `pytest-xdist` worker-isolated names | `resource_name` and `track` | — | Worker index in config |
| HTML report plus screenshot, video, trace | pytest-html and pytest-playwright | Trace viewer docs | HTML reporter |
| Local process lifecycle around pytest | `APP_START_CMD` in `run_tests.py` | — | `webServer` config |
| WCAG 2.1 AA scan guidance | axe-playwright-python reference | — | `@axe-core/playwright` |
| E2E anti-pattern guardrails | `references/anti-patterns.md` | — | — |
| Codex, Claude Code, Cursor, agents install | `./scripts/install.sh` | — | — |

Cells marked — mean that topic is outside that project's starter, not that the tool cannot do it.

## What Is Included

- A runnable local example with page objects, role tests, and cached UI login.
- A function-scoped cleanup registry that also runs after assertion failures.
- Session auth state at `.auth/super_admin_<worker>.json`, gitignored.
- pytest-managed browser fixtures for automatic failure artifacts.
- An opt-in `pytest-xdist` guide. The default run stays serial.
- A runner that can start a dev server, archive HTML, and return pytest's status.
- References for accessibility, anti-patterns, CI, retries, terminal output,
  API mocking, and Python visual regression setup.

Advanced integrations require their documented optional dependencies.
`axe-playwright-python` is optional and is not installed by the base requirements.
HTML reporting uses pytest-html; the illustrative SVG and terminal transcript
under `docs/` and `examples/` are design examples, not measured execution results.

## Verify The Release

From the repository root, with the same virtual environment active:

```bash
python scripts/verify_starter.py
python scripts/package_skill.py
```

`scripts/build_package.py` is the same packaging step. Verification runs the
starter, including a two-worker xdist run, then deliberately fails a browser
test and checks that cleanup still occurred. It requires a screenshot, video,
and trace, and checks exit codes for failing tests, empty selection, and
invalid arguments. Intentional failures appear in its output; the verifier
itself exits zero only when all expected outcomes are confirmed.

GitHub Actions (`.github/workflows/validate.yml`) repeats verification and
uploads reports and packages. A badge is evidence only once its linked workflow
has actually run.

## Agensi Package

`python scripts/package_skill.py` produces:

- `dist/playwright-pytest-qa-1.3.0.zip`: marketplace upload with `SKILL.md` at root.
- `playwright-pytest-qa.skill`: folder-wrapped skill archive.

Both include the MIT license and the same source files. Generated reports,
auth state, virtual environments, and caches are excluded. Listing copy is in
[docs/agensi-listing.md](docs/agensi-listing.md).

See [CHANGELOG.md](CHANGELOG.md) for changes.
