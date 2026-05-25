# Flaky Test Management Reference

Use retries as a controlled safety net for infrastructure noise, not as a substitute for fixing unstable tests.

## Dependency

Add this to `requirements.txt`:

```text
pytest-rerunfailures>=14.0
```

## Recommended command

```bash
pytest tests/ -v --reruns 2 --reruns-delay 1
```

Use this in CI when the environment can have occasional network, browser, or backend latency spikes.

## pytest.ini option

For teams that want retries enabled by default:

```ini
[pytest]
addopts =
    -v
    --tb=short
    --reruns 2
    --reruns-delay 1
    --screenshot=only-on-failure
    --video=retain-on-failure
    --tracing=retain-on-failure
    --output=reports/failures
```

Prefer command-line retries in CI if local developers should see first-failure behavior.

## Rules

- Retry only known nondeterministic failure classes: transient HTTP failures, browser startup issues, network timeouts, CI load spikes.
- Do not retry deterministic validation failures, wrong text, broken permissions, missing records, or real product bugs.
- Track repeated reruns as technical debt. A test that passes only on retry should be investigated.
- Keep retries low: `--reruns 1` or `--reruns 2` is usually enough.
- Add stable waits based on UI state, not arbitrary sleeps.

## Quarantine pattern

For unstable tests that block releases, mark them clearly instead of silently absorbing failures:

```python
import pytest

@pytest.mark.flaky(reason="Intermittent backend 504 on staging; tracked in QA-123")
def test_export_report(super_admin_page):
    ...
```

Add this to `pytest.ini`:

```ini
markers =
    flaky(reason): known flaky test requiring investigation
```

Run quarantined tests separately when needed:

```bash
pytest tests/ -v -m flaky --reruns 2
```

Run the main suite without quarantined tests:

```bash
pytest tests/ -v -m "not flaky"
```

## Stabilization checklist

- Prefer `page.get_by_role()`, `page.get_by_test_id()`, and stable locators.
- Wait for business state: success toast, URL change, table row, API response, or button enabled state.
- Avoid `time.sleep()` except for explicit investigation.
- Ensure each test owns its data and does not depend on execution order.
- Clean up created resources in pass, fail, and error cases.
- Capture trace, screenshot, and video on failure.
