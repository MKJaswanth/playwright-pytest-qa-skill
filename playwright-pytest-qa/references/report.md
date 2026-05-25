# HTML Report Generation Reference

Full implementation of `utils/report_plugin.py`.

## How it works
- Hooks into pytest via `pytest_runtest_logreport` and `pytest_sessionfinish`
- Generates `reports/milestone1_report.html` after every run automatically
- Saves trend data to `reports/history.json` (last 10 runs)
- Zero extra commands needed — just run pytest normally

## Register in conftest.py
```python
from utils.report_plugin import ReportPlugin

def pytest_configure(config):
    config.pluginmanager.register(ReportPlugin(), "custom_html_report")
```

## Report contents
- **Stat cards** — Total, Passed, Failed, Skipped, Duration, Pass Rate
- **Donut chart** — visual pass/fail ratio (Chart.js)
- **Trend line** — pass rate across last 10 runs
- **Module breakdown** — per user story with colour-coded progress bars
- **Test table** — status badge, TC ID, name, module, duration, screenshot, error
- **Filter buttons** — All / Passed / Failed / Skipped
- **Search box** — filter by test name or TC ID instantly

## Saving reports with timestamps (never overwrite)
```bash
# run_tests.sh
#!/bin/bash
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M')
pytest tests/milestone1/ -v
mkdir -p reports/history
cp reports/milestone1_report.html reports/history/report_$TIMESTAMP.html
echo "✅ Report saved → reports/history/report_$TIMESTAMP.html"
```

## Sharing with managers/clients
- Share the single HTML file — opens in any browser, no install needed
- Send via email, WhatsApp, Slack, or USB
- Zip the `reports/history/` folder to send all historical runs

## Screenshot / video / trace on failure
Playwright captures these automatically when added to pytest.ini:
```ini
addopts =
    --screenshot=only-on-failure
    --video=retain-on-failure
    --tracing=retain-on-failure
    --output=reports/failures
```

Saved to:
```
reports/failures/
└── test_tc002_role_name_mandatory/
    ├── test-failed-1.png    ← exact screen at moment of failure
    ├── video.webm           ← full browser recording
    └── trace.zip            ← open with: playwright show-trace trace.zip
```

## Full report_plugin.py code
See the already-generated file at:
`/mnt/user-data/outputs/report_plugin.py`

Or refer to the conversation where it was created for the complete source.
