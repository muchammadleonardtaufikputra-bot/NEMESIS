
import unittest

from modules.simulation.simulation_engine import run_simulation
from modules.simulation.detection_engine import (
    get_detection_rules,
    analyze_event,
)


class TestDetectionEngine(unittest.TestCase):

    def test_detection_rules_available(self):
        rules = get_detection_rules()

        self.assertEqual(len(rules), 4)
        self.assertIn("AUTH-001", rules)
        self.assertIn("FW-001", rules)

    def test_valid_event_detected(self):
        event = run_simulation("failed_login")
        result = analyze_event(event)

        self.assertEqual(result["status"], "DETECTED")
        self.assertEqual(result["event_code"], "AUTH-001")

    def test_all_scenarios_detected(self):
        scenarios = [
            "failed_login",
            "firewall_alert",
            "suspicious_process",
            "privilege_change",
        ]

        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                event = run_simulation(scenario)
                result = analyze_event(event)

                self.assertEqual(
                    result["status"],
                    "DETECTED"
                )

    def test_invalid_event_rejected(self):
        with self.assertRaises(ValueError):
            analyze_event("invalid event")

    def test_non_simulated_event_rejected(self):
        event = run_simulation("failed_login")
        event["status"] = "REAL"

        with self.assertRaises(ValueError):
            analyze_event(event)

    def test_modified_event_not_detected(self):
        event = run_simulation("failed_login")
        event["severity"] = "LOW"

        result = analyze_event(event)

        self.assertEqual(result["status"], "NOT_DETECTED")


if __name__ == "__main__":
    unittest.main()
