
from collections import Counter

from modules.simulation.simulation_database import (
    get_simulation_history,
    get_simulation_count,
)


MAX_TIMELINE_RECORDS = 100


def _normalize_limit(limit):
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 50

    return max(1, min(limit, MAX_TIMELINE_RECORDS))


def get_monitoring_timeline(limit=50):
    """
    Read-only timeline of previously stored inert simulation events.
    Does not monitor or modify the operating system.
    """

    safe_limit = _normalize_limit(limit)

    records = get_simulation_history(limit=safe_limit)

    events = []

    for record in records:
        events.append({
            "record_id": record.get("id"),
            "simulation_id": record.get("simulation_id"),
            "scenario_id": record.get("scenario_id", "unknown"),
            "scenario_name": record.get(
                "scenario_name", "Unknown Scenario"
            ),
            "event_code": record.get("event_code", "UNKNOWN"),
            "severity": record.get("severity", "UNKNOWN"),
            "detection_status": record.get(
                "detection_status", "UNKNOWN"
            ),
            "matched_rule": record.get("matched_rule"),
            "timestamp": record.get("timestamp"),
            "source": "INERT_LOCAL_SIMULATION",
        })

    events.sort(
        key=lambda item: item["timestamp"] or "",
        reverse=True
    )

    return {
        "success": True,
        "monitoring_mode": "READ_ONLY",
        "data_scope": "INERT_LOCAL_EVENTS",
        "total_records": get_simulation_count(),
        "returned_events": len(events),
        "events": events,
    }


def get_monitoring_summary():
    """
    Summarize stored simulation events.
    """

    timeline = get_monitoring_timeline(
        limit=MAX_TIMELINE_RECORDS
    )

    events = timeline["events"]

    detection_counts = Counter(
        event["detection_status"]
        for event in events
    )

    severity_counts = Counter(
        event["severity"]
        for event in events
    )

    scenario_counts = Counter(
        event["scenario_id"]
        for event in events
    )

    return {
        "success": True,
        "monitoring_mode": "READ_ONLY",
        "data_scope": "INERT_LOCAL_EVENTS",
        "total_records": timeline["total_records"],
        "analyzed_events": len(events),
        "detected_events": detection_counts.get(
            "DETECTED", 0
        ),
        "not_detected_events": detection_counts.get(
            "NOT_DETECTED", 0
        ),
        "detection_distribution": dict(
            detection_counts
        ),
        "severity_distribution": dict(
            severity_counts
        ),
        "scenario_distribution": dict(
            scenario_counts
        ),
        "interpretation": (
            "This monitoring summary describes stored inert "
            "simulation events only. It is not live system "
            "monitoring or real-world threat detection."
        ),
    }
