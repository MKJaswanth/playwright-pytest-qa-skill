"""Exercise passing tests, failed-test evidence, cleanup, and exit codes."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "playwright-pytest-qa" / "assets" / "starter"

FAILURE_CASES = '''
import pytest

def test_failure_evidence(page, base_url, api, track):
    response = api.post("/api/roles", json={"name": "Failing test role"})
    track("role", response.json()["id"])
    page.goto(base_url)
    assert False, "Intentional failure to verify evidence and runner status"

def test_cleanup_after_failure(api):
    assert api.get("/api/roles").json() == []

@pytest.mark.skip(reason="Verification of skipped result handling")
def test_skipped():
    pass
'''


def run(project, arguments, expected):
    result = subprocess.run(
        [sys.executable, "run_tests.py", *arguments],
        cwd=project, capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    assert result.returncode == expected, (result.returncode, expected)
    return result


def verify():
    with tempfile.TemporaryDirectory(prefix="qa-skill-verify-") as temp:
        project = Path(temp) / "starter"
        shutil.copytree(STARTER, project, ignore=shutil.ignore_patterns(
            "__pycache__", ".pytest_cache", "reports", "test-results",
        ))
        run(project, ["-q"], 0)
        assert (project / "reports" / "report.html").is_file()
        assert len(list((project / "reports" / "history").glob("*.html"))) == 1

        (project / "tests" / "test_evidence.py").write_text(FAILURE_CASES, encoding="utf-8")
        run(project, ["tests/test_evidence.py", "-q"], 1)
        artifacts = project / "reports" / "failures"
        for pattern in ("*.png", "*.webm", "trace.zip"):
            assert list(artifacts.rglob(pattern)), f"Missing failure evidence: {pattern}"
        assert len(list((project / "reports" / "history").glob("*.html"))) == 2

        run(project, ["-k", "does_not_match_any_test", "-q"], 5)
        run(project, ["--unknown-option-for-verification"], 4)
        assert not (project / "reports" / "report.html").exists()
        print("Verified pass/fail/no-tests/usage exit codes, cleanup after failure, HTML, screenshot, video, and trace.")


if __name__ == "__main__":
    verify()
