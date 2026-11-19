
import unittest

from modules.simulation.simulation_engine import (
    get_available_scenarios,
    run_simulation,
)


class TestSimulationEngine(unittest.TestCase):

    def test_available_scenarios(self):
        scenarios = get_available_scenarios()

        self.assertEqual(len(scenarios), 4)
        self.assertIn("failed_login", scenarios)
        self.assertIn("firewall_alert", scenarios)

    def test_run_valid_simulation(self):
        result = run_simulation("failed_login")

        self.assertEqual(result["scenario_id"], "failed_login")
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(
            result["execution_mode"],
            "INERT_LOCAL_EVENT"
        )

    def test_simulation_has_unique_id(self):
        first = run_simulation("failed_login")
        second = run_simulation("failed_login")

        self.assertNotEqual(
            first["simulation_id"],
            second["simulation_id"]
        )

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):
            run_simulation("unknown_scenario")

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            run_simulation(None)


if __name__ == "__main__":
    unittest.main()
