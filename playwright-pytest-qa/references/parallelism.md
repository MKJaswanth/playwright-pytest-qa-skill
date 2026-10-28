# Parallel Execution

The starter runs serially. Add `pytest-xdist` and enable workers only after
each test owns its data. The bundled requirements include `pytest-xdist`.

```bash
python run_tests.py -n auto
python run_tests.py -n 2 -q
```

`-n auto` uses one worker per CPU. Start with `-n 2` when confirming isolation.
Keep retries off while proving a parallel run. Do not enable `-n` in
`pytest.ini` until a full run is stable.

## Worker-isolated data

xdist gives each worker a `workerid` such as `gw0`. The starter's `worker_id`
fixture reads `request.config.workerinput["workerid"]` and uses `gw0` when the
suite is not under xdist. Name anything a shared environment can see with that
id and a short unique suffix:

```python
def test_create_role(api, track, resource_name):
    name = resource_name("role")  # role-gw0-a1b2c3
    response = api.post("/api/roles", json={"name": name})
    track("role", response.json()["id"])
```

`resource_name("role")` returns `role-{worker_id}-{uuid4().hex[:6]}`.
Use the same shape for users, orders, and files. Give each worker its own
account when the app cannot safely share one login. Saved browser state follows
the same split: `.auth/super_admin_master.json` outside xdist, and
`.auth/super_admin_gw0.json` (and `gw1`, ...) under xdist.

The demo server is session-scoped, so each worker process gets its own server
and port. A shared staging app does not. Unique names are what keep workers
from deleting each other's rows there.

## Cleanup and shared state

`track` records the worker id with every resource and includes it in teardown
errors. Teardown still runs only for the test that registered the resource.
Do not move the registry to a module global, a session fixture, or a file that
workers share. Do not let workers write one HTML report, trace directory, or
terminal UI unless that plugin aggregates on the controller. `pytest-html` 4
does this for `--html`; confirm it before treating a parallel report as complete.

Avoid fixtures that mutate a shared list, cache, or admin account across tests.
A test that needs a fresh login uses `login_through_ui` on `login_page` and
does not reuse another test's page.
