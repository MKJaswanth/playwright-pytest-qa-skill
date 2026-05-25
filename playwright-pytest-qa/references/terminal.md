# Live Terminal Display Reference

Full implementation of `utils/live_terminal.py`.
Requires: `pip install rich`

```python
from __future__ import annotations
import time, re
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class LiveTerminalPlugin:
    def __init__(self):
        self._results = []
        self._start   = time.time()
        self._total   = 0
        self._counter = 0

    def pytest_collection_finish(self, session):
        self._total = len(session.items)
        console.print()
        console.rule(
            f"[bold cyan]🚀  Lead Management — Milestone 1[/]  [dim]{self._total} tests collected[/]",
            style="cyan")
        console.print()

    def pytest_runtest_logreport(self, report):
        if report.when != "call" and not (report.when == "setup" and report.failed):
            return
        if report.when == "setup" and not report.failed:
            return

        self._counter += 1
        status = "passed" if report.passed else ("failed" if report.failed else "skipped")

        m = re.search(r"tc(\d+)", report.nodeid, re.IGNORECASE)
        tc_id = f"TC_{m.group(1).zfill(3)}" if m else "     "

        parts     = report.nodeid.split("::")
        test_name = parts[-1] if parts else report.nodeid
        short     = test_name.replace("test_", "").replace("_", " ").title()[:52]

        module_parts = report.nodeid.split("/")
        module = module_parts[-2].replace("test_", "").replace("_", " ").title()[:24] \
                 if len(module_parts) > 1 else ""

        duration = round(getattr(report, "duration", 0), 2)
        self._results.append({
            "n": self._counter, "tc_id": tc_id, "name": short,
            "module": module, "status": status, "duration": duration,
        })
        self._print_result(self._results[-1])

    def _print_result(self, r):
        n, total = r["n"], self._total
        color = {"passed": "green", "failed": "red", "skipped": "dim"}[r["status"]]
        icon  = {"passed": "✓",     "failed": "✗",   "skipped": "─"}[r["status"]]
        label = {"passed": "[bold green] PASSED [/]",
                 "failed": "[bold red] FAILED [/]",
                 "skipped":"[dim] SKIPPED[/]"}[r["status"]]

        filled  = int(20 * n / total) if total else 0
        bar     = f"[cyan]{'█' * filled}[/][dim]{'░' * (20 - filled)}[/]"
        passed  = sum(1 for x in self._results if x["status"] == "passed")
        failed  = sum(1 for x in self._results if x["status"] == "failed")

        console.print(
            f"[dim]{n:>3}/{total}[/]  {bar}  [{color}]{icon}[/]  "
            f"[bold cyan]{r['tc_id']}[/]  [{color}]{r['name']:<52}[/]  "
            f"[dim]{r['module']:<24}[/]  [dim]{r['duration']:>5}s[/]  {label}"
        )

        if n % 5 == 0 or n == total:
            skipped = sum(1 for x in self._results if x["status"] == "skipped")
            rate    = round(passed / n * 100) if n else 0
            elapsed = round(time.time() - self._start, 1)
            console.print(
                f"  [dim]── {n} run · [green]{passed} passed[/] · "
                f"[red]{failed} failed[/] · {skipped} skipped · "
                f"{rate}% pass rate · {elapsed}s elapsed ──[/]"
            )

    def pytest_sessionfinish(self, session, exitstatus):
        results  = self._results
        total    = len(results)
        passed   = sum(1 for r in results if r["status"] == "passed")
        failed   = sum(1 for r in results if r["status"] == "failed")
        skipped  = sum(1 for r in results if r["status"] == "skipped")
        elapsed  = round(time.time() - self._start, 1)
        rate     = round(passed / total * 100, 1) if total else 0

        console.print()
        console.rule(style="dim")
        console.print()

        status_text = Text("✓  ALL TESTS PASSED", style="bold green") \
                      if failed == 0 else \
                      Text(f"✗  {failed} TEST(S) FAILED", style="bold red")
        panel_style = "green" if failed == 0 else "red"

        body = Text()
        body.append(f"\n   Total   : {total}\n",   style="bold white")
        body.append(f"   Passed  : {passed}\n",    style="bold green")
        body.append(f"   Failed  : {failed}\n",    style="bold red" if failed else "dim")
        body.append(f"   Skipped : {skipped}\n",   style="dim")
        body.append(f"   Rate    : {rate}%\n",     style="bold cyan")
        body.append(f"   Time    : {elapsed}s\n",  style="dim")

        console.print(Panel(
            Text.assemble(status_text, body),
            title="[bold]Test Run Summary[/]",
            border_style=panel_style, padding=(1, 4)
        ))

        failures = [r for r in results if r["status"] == "failed"]
        if failures:
            console.print()
            console.rule("[bold red]  Failed Tests  ", style="red")
            for r in failures:
                console.print(
                    f"  [red]✗[/]  [bold cyan]{r['tc_id']}[/]  "
                    f"[red]{r['name']}[/]  [dim]({r['module']})[/]"
                )

        console.print()
        console.print(f"  [dim]📊 HTML report → reports/milestone1_report.html[/]")
        console.print()
```
