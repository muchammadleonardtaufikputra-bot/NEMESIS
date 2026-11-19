
"""
NEMESIS CORE
Local Project Backup Utility

Creates a timestamped ZIP archive of the NEMESIS project.
No network access. No source database modification.
"""

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = PROJECT_ROOT / "backups"

EXCLUDED_DIRECTORIES = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "backups",
    "logs",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
}


def should_exclude(path: Path) -> bool:
    """Check whether a project path should be excluded."""

    relative_path = path.relative_to(PROJECT_ROOT)

    if any(
        part in EXCLUDED_DIRECTORIES
        for part in relative_path.parts
    ):
        return True

    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True

    if path.is_symlink():
        return True

    return False


def collect_project_files() -> list[Path]:
    """Collect eligible project files."""

    files = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if should_exclude(path):
            continue

        files.append(path)

    return sorted(files)


def create_backup() -> Path:
    """Create a timestamped ZIP backup."""

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    archive_path = (
        BACKUP_DIR / f"NEMESIS_BACKUP_{timestamp}.zip"
    )

    files = collect_project_files()

    if not files:
        raise RuntimeError("No project files found.")

    archived_count = 0

    with ZipFile(
        archive_path,
        mode="w",
        compression=ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:

        for file_path in files:
            relative_path = file_path.relative_to(
                PROJECT_ROOT
            )

            archive.write(
                file_path,
                arcname=relative_path.as_posix(),
            )

            archived_count += 1

    print("=" * 55)
    print("NEMESIS LOCAL BACKUP")
    print("=" * 55)
    print(f"Archive : {archive_path.name}")
    print(f"Files   : {archived_count}")
    print(f"Size    : {archive_path.stat().st_size:,} bytes")
    print(f"Status  : SUCCESS")
    print("=" * 55)
    print("Keep this archive private.")

    return archive_path


if __name__ == "__main__":
    try:
        create_backup()
    except (OSError, RuntimeError) as error:
        print(f"BACKUP FAILED: {error}")
        raise SystemExit(1)
