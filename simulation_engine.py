
"""
NEMESIS CORE
Local Security Event Simulation Engine

This module generates inert security events for defensive
detection testing. It does not execute attacks or modify
system security settings.
"""

from datetime import datetime, timezone
from uuid import uuid4


SIMULATION_NAME = "NEMESIS DEFENSIVE EVENT SIMULATOR"
SIMULATION_VERSION = "1.0.0"


SCENARIOS = {
    "failed_login": {
        "name": "Failed Login Event",
        "category": "Authentication",
        "severity": "MEDIUM",
        "description": (
            "A simulated authentication failure event "
            "was generated for detection testing."
        ),
        "event_code": "AUTH-001",
    },
    "firewall_alert": {
        "name": "Firewall Configuration Alert",
        "category": "Network Security",
        "severity": "HIGH",
        "description": (
            "A simulated firewall configuration alert "
            "was generated for detection testing."
        ),
        "event_code": "FW-001",
    },
    "suspicious_process": {
        "name": "Unusual Process Alert",
        "category": "Endpoint Security",
        "severity": "MEDIUM",
        "description": (
            "A simulated unusual process alert "
            "was generated for detection testing."
        ),
        "event_code": "EDR-001",
    },
    "privilege_change": {
        "name": "Privilege Change Event",
        "category": "Access Control",
        "severity": "HIGH",
        "description": (
            "A simulated privilege change event "
            "was generated for detection testing."
        ),
        "event_code": "ACCESS-001",
    },
}


def get_available_scenarios():
    """Return available inert simulation scenarios."""

    return {
        key: {
            "name": value["name"],
            "category": value["category"],
            "severity": value["severity"],
            "event_code": value["event_code"],
        }
        for key, value in SCENARIOS.items()
    }


def run_simulation(scenario_id):
    """
    Generate one inert security event.

    No operating-system commands, network requests,
    authentication attempts, or configuration changes
    are performed.
    """

    if not isinstance(scenario_id, str):
        raise ValueError("Scenario ID must be a string.")

    scenario_id = scenario_id.strip().lower()

    if scenario_id not in SCENARIOS:
        raise ValueError("Unknown simulation scenario.")

    scenario = SCENARIOS[scenario_id]

    return {
        "simulation_id": str(uuid4()),
        "simulation_name": SIMULATION_NAME,
        "simulation_version": SIMULATION_VERSION,
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "category": scenario["category"],
        "severity": scenario["severity"],
        "event_code": scenario["event_code"],
        "description": scenario["description"],
        "status": "SIMULATED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "INERT_LOCAL_EVENT",
    }
