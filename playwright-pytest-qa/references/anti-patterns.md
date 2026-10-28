# E2E Anti-Patterns

Do not generate these. They hide failures or pass for the wrong reason.

## Fixed sleeps

`time.sleep()` and `page.wait_for_timeout()` pause for a guess. Use a web-first
assertion such as `expect(locator).to_be_visible()` or `expect(page).to_have_url(...)`.
Waiting on a specific response is appropriate when the test must observe that
request. A server-readiness poll in `run_tests.py` is not a UI assertion.

## Assertions that do not retry

`assert locator.is_visible()` checks once. `expect(locator).to_be_visible()`
retries until the timeout. Use `expect` for UI conditions, including text,
URL, and enabled state.

## Swallowed failures

A `try` / `except` that prints and continues makes a broken journey pass.
Let the assertion fail. Catch an exception only when the product contract says
that condition is success, and assert that condition directly.

## Brittle selectors

Do not locate new UI by CSS classes, XPath, or nth-child positions.
Prefer `get_by_role`, `get_by_label`, `get_by_placeholder`, and
`get_by_test_id`. Filter a role by accessible name or text when several
matches exist. Avoid positional selectors for rows created during the test.

## Untracked data

Every application row, user, or file the test creates must be passed to
`track` immediately with the id the API returned. Teardown cannot delete an
id that was never registered. Do not leave cleanup to a later test or a
manual pass.

## Mocks that replace the system under test

`page.route()` is for exercising a frontend empty or error state.
A test that mocks the same API it claims to cover does not prove that API.
Cover the real contract with `api` against a running app, as described in
[api-mocking.md](api-mocking.md).
