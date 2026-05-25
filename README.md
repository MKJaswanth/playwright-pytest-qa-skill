# Playwright + pytest QA Skill

Reusable Codex skill for creating professional QA automation suites with
Playwright and pytest.

The downloadable file is:

```text
playwright-pytest-qa.skill
```

## What It Does

This skill guides Codex through a complete end-to-end QA automation workflow:

- Set up a Playwright + pytest project structure
- Write UI and API test cases using Page Object Model patterns
- Track test-created data and clean it up automatically after each run
- Add a live Rich terminal progress display while tests execute
- Generate manager/client-friendly HTML test reports
- Preserve failure screenshots, videos, and Playwright traces

It is intended for staging QA automation where tests may create roles, users,
leads, teams, projects, master data, or similar records that must not build up
over time.

## When To Use It

Use this skill when asking Codex to:

- Write Playwright test cases
- Automate UI test flows
- Build pytest fixtures for browser or API testing
- Create Page Object Model files
- Add cleanup after tests create data
- Generate QA reports for test runs
- Improve terminal output for large test suites

## Install

### Option 1: Install the `.skill` file

Download `playwright-pytest-qa.skill`, then install it into your Codex skills
folder using your Codex skill installation flow.

After installation, the skill name is:

```text
playwright-pytest-qa
```

### Option 2: Install from the folder

Copy the `playwright-pytest-qa/` folder into your Codex skills directory.

The folder contains:

```text
playwright-pytest-qa/
├── SKILL.md
└── references/
    ├── cleanup.md
    ├── terminal.md
    └── report.md
```

## Repository Layout

```text
playwright-pytest-qa-skill/
├── README.md
├── playwright-pytest-qa.skill
└── playwright-pytest-qa/
    ├── SKILL.md
    └── references/
        ├── cleanup.md
        ├── terminal.md
        └── report.md
```

## Skill Contents

`SKILL.md` contains the main workflow:

- Project setup
- Dependencies
- `pytest.ini`
- `config/config.py`
- Page Object Model conventions
- Test writing patterns
- Cleanup fixture wiring
- Live terminal plugin wiring
- HTML report plugin wiring
- Common commands

The `references/` folder contains implementation details:

- `cleanup.md`: cleanup registry and cleanup API client
- `terminal.md`: Rich-based live pytest terminal plugin
- `report.md`: HTML report generation behavior and setup notes

## Typical Prompt Examples

```text
Write Playwright pytest test cases for the role management module.
```

```text
Create a pytest automation framework with cleanup so staging data is deleted.
```

```text
Add HTML reporting and live terminal output to my Playwright tests.
```

## Notes

- Update API cleanup paths in `RESOURCE_DELETE_PATHS` to match your application.
- Store credentials and base URLs in `.env`; do not hardcode secrets in tests.
- Prefer stable selectors such as `data-testid`, IDs, ARIA labels, and names.
- Call `track("resource_type", id)` immediately after creating test data.
