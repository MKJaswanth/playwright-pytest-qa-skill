# Flaky Tests

The starter has no retries. Investigate failures before adding a retry policy.
For selected known transient failures, explicitly install `pytest-rerunfailures`
and use its documented marker or CLI options. Broad retries can mask product bugs.

For example, after installing the plugin:

```python
import pytest

@pytest.mark.flaky(reruns=1, reruns_delay=1)
def test_known_transient_flow(page):
    # Implement the actual observed flow and assertions.
    page.goto("http://127.0.0.1:8000")
```

Record the issue and reason for any retry. Keep test-owned data unique and use
retrying Playwright assertions rather than arbitrary sleeps.

Use a distinct `quarantined` marker for quarantine, rather than reusing the
retry plugin's `flaky` marker. Declare it in pytest configuration and run the
quarantine separately with `-m quarantined`; exclude with `-m "not quarantined"`.
Validate report totals and failure evidence when adding retries or xdist.
