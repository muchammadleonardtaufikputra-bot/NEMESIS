
"""
NEMESIS - Threat Intelligence Catalog

Purpose:
- Defensive threat reference catalog.
- Candidate MITRE ATT&CK mapping.
- Evidence requirements and defensive recommendations.

All mappings are candidates, not proof of malicious activity.
"""

from copy import deepcopy


CATALOG_VERSION = "1.0.0"

THREAT_CATALOG = {
    "failed_login": {
        "event_code": "AUTH-001",
        "scenario_name": "Failed Login Event",
        "category": "Authentication",
        "title": "Authentication Failure Pattern",
        "description": (
            "A simulated authentication failure event "
            "for defensive detection validation."
        ),
        "severity": "MEDIUM",

        "mitre": {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "mapping_status": "CANDIDATE",
            "confidence": "LOW",
            "source_url": (
                "https://attack.mitre.org/techniques/T1110/"
            ),
            "evidence_required": (
                "Repeated authentication failures with "
                "relevant account, source, and time correlation."
            ),
        },

        "defensive_guidance": [
            "Review authentication logs.",
            "Check account protection settings.",
            "Review multi-factor authentication coverage.",
            "Correlate repeated failures before classifying an incident.",
        ],
    },

    "firewall_alert": {
        "event_code": "FW-001",
        "scenario_name": "Firewall Configuration Alert",
        "category": "Network Security",
        "title": "Firewall Configuration Change",
        "description": (
            "A simulated firewall configuration alert "
            "for defensive monitoring validation."
        ),
        "severity": "HIGH",

        "mitre": {
            "technique_id": "T1686",
            "technique_name": "Disable or Modify System Firewall",
            "tactic": "Defense Impairment",
            "mapping_status": "CANDIDATE",
            "confidence": "LOW",
            "source_url": (
                "https://attack.mitre.org/techniques/T1686/"
            ),
            "evidence_required": (
                "Verified firewall profile, policy, or rule "
                "modification with supporting audit records."
            ),
        },

        "defensive_guidance": [
            "Review firewall configuration changes.",
            "Verify that firewall profiles remain enabled.",
            "Review administrative change records.",
            "Investigate unexpected configuration changes.",
        ],
    },

    "suspicious_process": {
        "event_code": "EDR-001",
        "scenario_name": "Unusual Process Alert",
        "category": "Endpoint Security",
        "title": "Unusual Process Activity",
        "description": (
            "A simulated endpoint process alert "
            "for defensive detection validation."
        ),
        "severity": "HIGH",

        "mitre": {
            "technique_id": "T1059",
            "technique_name": (
                "Command and Scripting Interpreter"
            ),
            "tactic": "Execution",
            "mapping_status": "CANDIDATE",
            "confidence": "LOW",
            "source_url": (
                "https://attack.mitre.org/techniques/T1059/"
            ),
            "evidence_required": (
                "Verified interpreter execution and process "
                "context supporting suspicious behavior."
            ),
        },

        "defensive_guidance": [
            "Review endpoint security alerts.",
            "Validate process identity and publisher.",
            "Review available process execution records.",
            "Correlate process alerts with surrounding events.",
        ],
    },

    "privilege_change": {
        "event_code": "ACCESS-001",
        "scenario_name": "Privilege Change Event",
        "category": "Access Control",
        "title": "Account Permission Change",
        "description": (
            "A simulated privilege change event "
            "for defensive access monitoring."
        ),
        "severity": "HIGH",

        "mitre": {
            "technique_id": "T1098",
            "technique_name": "Account Manipulation",
            "tactic": "Persistence / Privilege Escalation",
            "mapping_status": "CANDIDATE",
            "confidence": "LOW",
            "source_url": (
                "https://attack.mitre.org/techniques/T1098/"
            ),
            "evidence_required": (
                "Verified account attribute, permission, "
                "or group membership modification."
            ),
        },

        "defensive_guidance": [
            "Review account permission changes.",
            "Verify administrative role assignments.",
            "Check whether changes were authorized.",
            "Review account modification audit records.",
        ],
    },
}


def get_all_threats():
    """
    Return the complete defensive threat catalog.
    """
    return deepcopy(THREAT_CATALOG)


def get_threat_by_scenario(scenario_id):
    """
    Retrieve threat intelligence for a scenario.
    """
    if not isinstance(scenario_id, str):
        raise ValueError("Scenario ID must be a string.")

    scenario_id = scenario_id.strip()

    if not scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    threat = THREAT_CATALOG.get(scenario_id)

    if threat is None:
        raise ValueError("Unknown threat scenario.")

    return deepcopy(threat)


def get_catalog_summary():
    """
    Return catalog statistics.
    """
    return {
        "catalog_version": CATALOG_VERSION,
        "total_entries": len(THREAT_CATALOG),
        "mapping_status": "CANDIDATE_ONLY",
        "mitre_mappings": len(THREAT_CATALOG),
        "scenarios": list(THREAT_CATALOG.keys()),
    }
