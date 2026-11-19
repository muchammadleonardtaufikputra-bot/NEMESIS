
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "NEMESIS"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Adversary Research & Emulation System"

DATABASE_DIR = BASE_DIR / "database"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

SENTINEL_PATH = (
    Path.home() / "Documents" / "SENTINEL-X"
)

for directory in [
    DATABASE_DIR,
    REPORTS_DIR,
    LOGS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
