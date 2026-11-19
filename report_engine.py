
from datetime import datetime, timezone
from typing import Any

from modules.assessment.assessment_database import (
    get_assessment_history,
)
from modules.simulation.simulation_database import (
    get_simulation_history,
)
from modules.detection_analytics.analytics_engine import (
    analyze_detection_coverage,
)
from modules.monitoring.monitoring_engine import (
    get_monitoring_summary,
)


def _safe_list(value: Any) -> list:
    """Return a list without modifying its source."""
    return value if isinstance(value, list) else []


def generate_unified_report() -> dict:
    """
    Combine existing local security assessment,
    inert simulation, analytics, and monitoring data.

    Read-only reporting. No system configuration changes.
    """

    assessments = _safe_list(get_assessment_history(limit=100))
    simulations = _safe_list(get_simulation_history(limit=100))

    analytics = analyze_detection_coverage()
    monitoring = get_monitoring_summary()

    return {
        "success": True,
        "report_type": "NEMESIS_UNIFIED_SECURITY_REPORT",
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "report_scope": {
            "assessment": "LOCAL_READ_ONLY_SECURITY_CHECKS",
            "simulation": "INERT_LOCAL_EVENTS",
            "analytics": "STORED_SIMULATION_RECORDS",
            "monitoring": "READ_ONLY_SIMULATION_RECORDS",
        },

        "summary": {
            "assessment_records": len(assessments),
            "simulation_records": len(simulations),
            "detected_events": analytics.get(
                "detected_events", 0
            ),
            "not_detected_events": analytics.get(
                "not_detected_events", 0
            ),
            "detection_coverage_percent": analytics.get(
                "detection_coverage_percent", 0
            ),
        },

        "assessment_history": assessments,
        "simulation_history": simulations,
        "analytics": analytics,
        "monitoring": monitoring,

        "limitations": [
            "Results represent local security checks and stored inert simulations only.",
            "Detection coverage does not measure real-world threat detection effectiveness.",
            "MITRE ATT&CK references are candidate mappings, not confirmed attack evidence.",
            "Monitoring reads stored simulation records and is not live endpoint monitoring.",
        ],
    }
