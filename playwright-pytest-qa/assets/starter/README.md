+# Runnable QA Demo

Requires Python 3.10+ and a Playwright-supported operating system.

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python run_tests.py
```

Run these commands in this directory, preferably in a virtual environment.
Five tests exercise a temporary local HTTP app and its API. No external service
or credentials are needed. The server binds to 127.0.0.1 on an available port
and shuts down when pytest finishes.

View reports/report.html for results; reports/history/ holds timestamped copies.
Failed browser tests retain screenshots, videos, and traces in reports/failures/.
API-only failures have no browser evidence.

The track fixture deletes this test's created roles after pass or failure and
reports deletion errors. Tests run serially with retries disabled.

Adapt demo_app.py, page objects, base_url, authentication, and API endpoints for
your own application. This server is a local demonstration, not a production app.
