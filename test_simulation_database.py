
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from modules.simulation.simulation_engine import run_simulation
from modules.simulation.detection_engine import analyze_event
from modules.simulation.simulation_database import (
    save_simulation,
    get_simulation_history,
    get_simulation_count,
)


class TestSimulationDatabase(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()

        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.path_patcher = patch(
            "modules.simulation.simulation_database.DB_PATH",
            self.db_path,
        )

        self.path_patcher.start()

        self.event = run_simulation("failed_login")
        self.detection = analyze_event(self.event)

    def tearDown(self):

        self.path_patcher.stop()
        self.temp_dir.cleanup()

    def test_save_simulation(self):

        record_id = save_simulation(
            self.event,
            self.detection,
        )

        self.assertGreater(record_id, 0)

    def test_get_simulation_history(self):

        save_simulation(self.event, self.detection)

        history = get_simulation_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(
            history[0]["detection_status"],
            "DETECTED",
        )

    def test_simulation_count(self):

        save_simulation(self.event, self.detection)

        self.assertEqual(get_simulation_count(), 1)

    def test_invalid_limit(self):

        with self.assertRaises(ValueError):
            get_simulation_history(0)

    def test_non_simulated_event_rejected(self):

        invalid_event = dict(self.event)
        invalid_event["status"] = "REAL"

        with self.assertRaises(ValueError):
            save_simulation(
                invalid_event,
                self.detection,
            )


if __name__ == "__main__":
    unittest.main()
