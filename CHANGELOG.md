# Changelog

## v1.2.0 - 2026-10-26

- Added a runnable local UI/API starter and GitHub Actions verification.
- Replaced manual browser contexts with pytest-managed fixtures for failure artifacts.
- Added a cross-platform runner that archives reports and preserves pytest exit codes.
- Replaced the missing custom report implementation with pytest-html.
- Made cleanup per-test, reverse-ordered, and visible on errors.
- Corrected Python visual-regression guidance and removed default retries.
- Added reproducible marketplace ZIP and .skill builds plus Agensi listing copy.

All notable changes to this skill package are documented here.

## v1.1.0 - 2026-05-25

- Added enterprise readiness guidance.
- Added flaky test retry guidance with `pytest-rerunfailures`.
- Added GitHub Actions CI/CD workflow reference.
- Added visual regression testing guidance.
- Added API mocking patterns with `page.route()`.
- Added Playwright trace viewer debugging guidance.
- Added MIT license.
- Added root `requirements.txt`.
- Added sample terminal output and report preview for README visibility.

## v1.0.0 - 2026-05-25

- Initial Playwright + pytest QA skill package.
- Added setup, Page Object Model, cleanup, live terminal, and HTML report guidance.
- Added downloadable `playwright-pytest-qa.skill` bundle.
