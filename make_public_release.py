
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = Path.home() / "Desktop" / "NEMESIS-public-source.zip"

EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "backups",
    "logs",
    "database",
    "reports",
    "node_modules",
    ".idea",
    ".vscode",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".backup",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

def should_exclude(path):
    relative = path.relative_to(PROJECT_ROOT)

    if any(part.lower() in EXCLUDED_DIRS for part in relative.parts):
        return True

    name = path.name.lower()

    if name.startswith(".env"):
        return True

    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True

    return False


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    files = [
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and not should_exclude(path)
    ]

    with ZipFile(OUTPUT_PATH, "w", ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(PROJECT_ROOT)
            archive.write(path, relative.as_posix())

    with ZipFile(OUTPUT_PATH, "r") as archive:
        bad_file = archive.testzip()

        if bad_file:
            print("ERROR: Archive integrity failed:", bad_file)
            return

        names = archive.namelist()

    print("NEMESIS PUBLIC SOURCE PACKAGE")
    print("Files:", len(names))
    print("Archive integrity: VALID")
    print("README included:", "README.md" in names)
    print("Application included:", "app.py" in names)
    print("Documentation included:",
          any(name.startswith("docs/") for name in names))
    print("Output:", OUTPUT_PATH)
    print("Review the archive before publishing.")


if __name__ == "__main__":
    main()
