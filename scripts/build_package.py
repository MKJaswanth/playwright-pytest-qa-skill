"""Build matching marketplace ZIP and folder-wrapped .skill archives."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "playwright-pytest-qa"
EXCLUDED = {"__pycache__", ".pytest_cache", "reports", "test-results", ".venv", ".auth"}
VERSION = "1.3.0"


def build():
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    files = sorted(
        path for path in SKILL.rglob("*")
        if path.is_file() and not EXCLUDED.intersection(path.relative_to(SKILL).parts)
        and path.suffix != ".pyc"
    )
    zip_path = destination / f"playwright-pytest-qa-{VERSION}.zip"
    skill_path = ROOT / "playwright-pytest-qa.skill"
    for path, prefix in ((zip_path, ""), (skill_path, "playwright-pytest-qa/")):
        with ZipFile(path, "w", ZIP_DEFLATED) as archive:
            for source in files:
                archive.write(source, prefix + source.relative_to(SKILL).as_posix())
            archive.write(ROOT / "LICENSE", prefix + "LICENSE")
        with ZipFile(path) as archive:
            assert archive.testzip() is None
            assert prefix + "SKILL.md" in archive.namelist()
        print(path)


if __name__ == "__main__":
    build()
