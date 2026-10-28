# Cleanup

The executable implementation is in `../assets/starter/conftest.py`, in the
`track` fixture. Its registry is local to a test; it deletes tracked roles in
reverse order during teardown, including after assertion failures.

## Adapt To An Application

Replace the demo `/api/roles/{id}` path with documented deletion endpoints.
Use the configured API base URL consistently: if it already includes `/api`,
do not prepend `/api` again. Supply the app's authentication through environment
configuration, with credentials absent from logs.

Register each resource immediately after creation, using its actual returned ID.
Use unique names for real shared staging environments. Register parents before
children so reversed cleanup removes dependents first. Track only this test's
resources and use per-test fixture state, not a module-global list.

Attempt all cleanup operations even if one fails. Accept 404 as already removed
when that matches the application's contract. Other unexpected status codes and
request exceptions should surface as teardown errors, not just log messages.
A passing assertion with failed cleanup must not appear as a clean passing run.

If a test creates data and crashes before registering its ID, fixture teardown
cannot discover that resource automatically. Use application-supported run IDs
or isolated tenants for recovery when needed. Do not promise unconditional cleanup
after forced process termination.

`track` stores the xdist worker id with each resource and includes it in
teardown errors. Generated names should use `resource_name`, which prefixes
`{label}-{worker_id}-{short id}`. See [parallelism.md](parallelism.md) before
running with `-n`. The default all-tests run checks that a role from the
preceding UI test is gone; `scripts/verify_starter.py` separately checks
cleanup after a deliberate failure.
