
"""
NEMESIS CORE
Detection Analytics Engine

Read-only analysis of inert simulation records.
Does not execute security actions or modify source records.
"""

from collections import Counter

from modules.simulation.simulation_database import (
    get_simulation_history,
    get_simulation_count,
)

from modules.threat_intelligence.catalog import (
    get_threat_by_scenario,
)


VALID_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}

VALID_DETECTION_STATUSES = {
    "DETECTED",
    "NOT_DETECTED",
}


def analyze_detection_coverage():
    """
    Analyze detection coverage across stored simulation scenarios.

    MITRE mappings are deduplicated by scenario and technique.
    Analysis is read-only and limited to stored inert events.
    """

    records = get_simulation_history(limit=100)
    total_records = get_simulation_count()

    detected = 0
    not_detected = 0
    ignored_events = 0

    scenario_stats = Counter()
    severity_stats = Counter()
    category_stats = Counter()

    scenario_detection_stats = {}

    # Dictionary prevents duplicate scenario/technique mappings.
    unique_mappings = {}

    for record in records:

        status = record.get("detection_status")
        scenario_id = record.get("scenario_id")
        severity = record.get("severity")

        if status == "DETECTED":
            detected += 1

        elif status == "NOT_DETECTED":
            not_detected += 1

        else:
            ignored_events += 1

        if not isinstance(scenario_id, str):
            scenario_id = "UNKNOWN"

        scenario_stats[scenario_id] += 1

        if severity in VALID_SEVERITIES:
            severity_stats[severity] += 1

        if scenario_id not in scenario_detection_stats:
            scenario_detection_stats[scenario_id] = {
                "total": 0,
                "detected": 0,
                "not_detected": 0,
                "ignored": 0,
            }

        scenario_result = scenario_detection_stats[scenario_id]
        scenario_result["total"] += 1

        if status == "DETECTED":
            scenario_result["detected"] += 1

        elif status == "NOT_DETECTED":
            scenario_result["not_detected"] += 1

        else:
            scenario_result["ignored"] += 1

        try:
            threat = get_threat_by_scenario(scenario_id)

            if not isinstance(threat, dict):
                raise ValueError("Invalid threat mapping")

            category = threat["category"]
            mitre = threat["mitre"]

            technique_id = mitre["technique_id"]
            technique_name = mitre["technique_name"]

            category_stats[category] += 1

            mapping_key = (
                scenario_id,
                technique_id,
            )

            if mapping_key not in unique_mappings:
                unique_mappings[mapping_key] = {
                    "scenario_id": scenario_id,
                    "event_code": mitre.get(
                        "event_code",
                        record.get("event_code"),
                    ),
                    "technique_id": technique_id,
                    "technique_name": technique_name,
                    "mapping_status": mitre["mapping_status"],
                    "confidence": mitre["confidence"],
                    "evidence_required": mitre[
                        "evidence_required"
                    ],
                }

        except (ValueError, KeyError, TypeError):
            category_stats["UNMAPPED"] += 1

    analyzed = detected + not_detected

    coverage = (
        round((detected / analyzed) * 100, 2)
        if analyzed else 0.0
    )

    return {
        "success": True,
        "analysis_mode": "READ_ONLY_SIMULATION_ANALYTICS",
        "data_scope": "INERT_LOCAL_EVENTS",

        "total_records": total_records,
        "analyzed_records": analyzed,
        "detected_events": detected,
        "not_detected_events": not_detected,
        "ignored_events": ignored_events,

        "detection_coverage_percent": coverage,

        "scenario_distribution": dict(scenario_stats),
        "severity_distribution": dict(severity_stats),
        "category_distribution": dict(category_stats),

        "scenario_detection_stats": scenario_detection_stats,

        "mitre_candidate_mappings": list(
            unique_mappings.values()
        ),

        "unique_mitre_mapping_count": len(unique_mappings),

        "interpretation": (
            "Coverage measures detection results among stored "
            "simulation records only. It is not a measure of "
            "real-world threat detection effectiveness."
        ),
    }


def get_analytics_summary():
    """
    Return compact analytics summary.
    """

    result = analyze_detection_coverage()

    return {
        "success": result["success"],
        "total_records": result["total_records"],
        "analyzed_records": result["analyzed_records"],
        "detected_events": result["detected_events"],
        "not_detected_events": result["not_detected_events"],
        "detection_coverage_percent": (
            result["detection_coverage_percent"]
        ),
        "analysis_mode": result["analysis_mode"],
    }
