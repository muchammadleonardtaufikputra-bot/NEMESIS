
import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from modules.assessment.assessment_database import (
    initialize_database,
    calculate_summary,
    save_assessment,
    get_assessment_history,
    get_assessment_count
)


class TestAssessmentDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.db_path = (
            Path(self.temp_directory.name) / "test_nemesis.db"
        )

        self.database_patcher = patch(
            "modules.assessment.assessment_database.DB_PATH",
            self.db_path
        )

        self.database_patcher.start()

        initialize_database()

        self.sample_data = {
            "assessment": "NEMESIS LOCAL SECURITY ASSESSMENT",
            "timestamp": "2026-11-19T13:00:00",
            "checks": {
                "firewall": {
                    "status": "PASS",
                    "details": "Firewall enabled"
                },
                "windows_defender": {
                    "status": "PASS",
                    "details": "Protection enabled"
                },
                "system_information": {
                    "status": "INFO",
                    "details": "Windows system"
                }
            }
        }

    def tearDown(self):
        self.database_patcher.stop()
        self.temp_directory.cleanup()

    def test_calculate_summary(self):
        summary = calculate_summary(self.sample_data)

        self.assertEqual(summary["total_checks"], 3)
        self.assertEqual(summary["pass_count"], 2)
        self.assertEqual(summary["warning_count"], 0)
        self.assertEqual(summary["error_count"], 0)

    def test_save_assessment(self):
        record_id = save_assessment(self.sample_data)

        self.assertGreater(record_id, 0)

    def test_get_assessment_history(self):
        save_assessment(self.sample_data)

        history = get_assessment_history()

        self.assertEqual(len(history), 1)

        self.assertEqual(
            history[0]["assessment"],
            self.sample_data["assessment"]
        )

        saved_data = json.loads(history[0]["result_json"])

        self.assertEqual(
            saved_data["checks"]["firewall"]["status"],
            "PASS"
        )

    def test_assessment_count(self):
        save_assessment(self.sample_data)
        save_assessment(self.sample_data)

        self.assertEqual(get_assessment_count(), 2)

    def test_history_limit(self):
        save_assessment(self.sample_data)
        save_assessment(self.sample_data)
        save_assessment(self.sample_data)

        history = get_assessment_history(limit=2)

        self.assertEqual(len(history), 2)

    def test_invalid_assessment_data(self):
        with self.assertRaises(ValueError):
            save_assessment({})

    def test_invalid_history_limit(self):
        with self.assertRaises(ValueError):
            get_assessment_history(limit=0)


if __name__ == "__main__":
    unittest.main()
