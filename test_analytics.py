
import unittest
from unittest.mock import patch

from modules.detection_analytics.analytics_engine import (
    analyze_detection_coverage,
    get_analytics_summary,
)


class TestDetectionAnalytics(unittest.TestCase):

    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_count",
        return_value=2,
    )
    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_history",
    )
    def test_detection_coverage(
        self, mock_history, mock_count
    ):
        mock_history.return_value = [
            {
                "scenario_id": "failed_login",
                "event_code": "AUTH-001",
                "severity": "MEDIUM",
                "detection_status": "DETECTED",
            },
            {
                "scenario_id": "firewall_alert",
                "event_code": "FW-001",
                "severity": "HIGH",
                "detection_status": "NOT_DETECTED",
            },
        ]

        result = analyze_detection_coverage()

        self.assertEqual(result["total_records"], 2)
        self.assertEqual(result["detected_events"], 1)
        self.assertEqual(result["not_detected_events"], 1)
        self.assertEqual(
            result["detection_coverage_percent"], 50.0
        )

    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_count",
        return_value=0,
    )
    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_history",
        return_value=[],
    )
    def test_empty_database(
        self, mock_history, mock_count
    ):
        result = analyze_detection_coverage()

        self.assertEqual(result["total_records"], 0)
        self.assertEqual(result["analyzed_records"], 0)
        self.assertEqual(
            result["detection_coverage_percent"], 0.0
        )

    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_count",
        return_value=1,
    )
    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_history",
    )
    def test_unknown_scenario(
        self, mock_history, mock_count
    ):
        mock_history.return_value = [
            {
                "scenario_id": "unknown_scenario",
                "event_code": "UNKNOWN",
                "severity": "LOW",
                "detection_status": "DETECTED",
            }
        ]

        result = analyze_detection_coverage()

        self.assertEqual(
            result["category_distribution"]["UNMAPPED"], 1
        )

    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_count",
        return_value=1,
    )
    @patch(
        "modules.detection_analytics.analytics_engine."
        "get_simulation_history",
        return_value=[
            {
                "scenario_id": "failed_login",
                "event_code": "AUTH-001",
                "severity": "MEDIUM",
                "detection_status": "DETECTED",
            }
        ],
    )
    def test_summary(
        self, mock_history, mock_count
    ):
        result = get_analytics_summary()

        self.assertTrue(result["success"])
        self.assertEqual(result["total_records"], 1)
        self.assertEqual(
            result["detection_coverage_percent"], 100.0
        )


if __name__ == "__main__":
    unittest.main()
