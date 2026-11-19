
import unittest

from config import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    DATABASE_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    SENTINEL_PATH,
)


class TestNemesisConfig(unittest.TestCase):

    def test_app_name(self):
        self.assertEqual(APP_NAME, "NEMESIS")

    def test_version(self):
        self.assertEqual(APP_VERSION, "1.0.0")

    def test_project_directory(self):
        self.assertTrue(BASE_DIR.exists())

    def test_storage_directories(self):
        self.assertTrue(DATABASE_DIR.exists())
        self.assertTrue(REPORTS_DIR.exists())
        self.assertTrue(LOGS_DIR.exists())

    def test_sentinel_path(self):
        self.assertEqual(SENTINEL_PATH.name, "SENTINEL-X")


if __name__ == "__main__":
    unittest.main()
