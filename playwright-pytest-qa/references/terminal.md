# Terminal Results

The starter uses pytest's native terminal reporter. Run `python run_tests.py -v`
to see each test and its outcome, or `-q` for compact output. Native reporting
includes setup/teardown errors, skipped tests, and final session exit status.

An optional Rich display can supplement it, but is not bundled as a validated
plugin. If implementing one, aggregate setup, call, and teardown results by
node ID and include setup skips, teardown errors, retries, xfail, and xpass.
Use pytest's final exit status when choosing a success banner.

Do not count each test phase or rerun as an independent final test. Under xdist,
aggregate results in the controller and do not let workers write the same report
or terminal UI. Test these cases before claiming parallel/retry support.

The historical sample transcript in `examples/` is illustrative.
