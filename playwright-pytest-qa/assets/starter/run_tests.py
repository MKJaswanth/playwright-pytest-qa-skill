"""Archive this run's report while preserving pytest's exit status."""

from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    project = Path(__file__).resolve().parent
    report = project / "reports" / "report.html"
    report.unlink(missing_ok=True)
    result = subprocess.run([sys.executable, "-m", "pytest", *sys.argv[1:]], cwd=project)
    if report.exists():
        try:
            archive = project / "reports" / "history"
            archive.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_%f")
            destination = archive / f"report_{stamp}.html"
            shutil.copy2(report, destination)
            print(f"Report saved: {destination}")
        except OSError as exc:
            print(f"Report archive failed: {exc}", file=sys.stderr)
            return result.returncode or 1
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
