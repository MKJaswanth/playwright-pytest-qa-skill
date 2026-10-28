# Runnable QA Demo

Requires Python 3.10+ and a Playwright-supported operating system.

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python run_tests.py
```

Run these commands in this directory, preferably in a virtual environment.
The tests exercise a temporary local HTTP app and its API. No external service
is needed. The server binds to 127.0.0.1 on an available port and shuts down
when pytest finishes. Demo login uses `SUPER_ADMIN_EMAIL` and
`SUPER_ADMIN_PASSWORD` when set, otherwise `super.admin@example.com` and
`demo-password`. Cached sessions are written under `.auth/` and are not source.

Authenticated UI tests reuse `storage_state`. Login-form tests use `login_page`.
`python run_tests.py -n 2` runs two workers. The default command stays serial.

Set `APP_START_CMD` and `BASE_URL` (or `HEALTHCHECK_URL`) when this runner
should boot an external app before pytest and stop it afterward.

View reports/report.html for results; reports/history/ holds timestamped copies.
Failed browser tests retain screenshots, videos, and traces in reports/failures/.
API-only failures have no browser evidence.

The track fixture deletes this test's created roles after pass or failure and
reports deletion errors, including the worker id. Retries stay disabled.

Adapt demo_app.py, page objects, base_url, authentication, and API endpoints for
your own application. This server is a local demonstration, not a production app.
