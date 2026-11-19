
import platform
import subprocess
import json
from datetime import datetime


def run_powershell(command):
    """Execute a read-only local PowerShell security query."""

    if platform.system() != "Windows":
        return {
            "status": "UNSUPPORTED",
            "details": "Windows only"
        }

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False
        )

        if result.returncode != 0:
            return {
                "status": "ERROR",
                "details": result.stderr.strip()[:500]
            }

        return {
            "status": "OK",
            "details": result.stdout.strip()
        }

    except (subprocess.TimeoutExpired, OSError) as error:
        return {
            "status": "ERROR",
            "details": str(error)
        }


def check_firewall():
    command = (
        "Get-NetFirewallProfile | "
        "Select-Object Name, Enabled | "
        "ConvertTo-Json -Compress"
    )

    result = run_powershell(command)

    if result["status"] != "OK":
        return result

    try:
        profiles = json.loads(result["details"])

        if isinstance(profiles, dict):
            profiles = [profiles]

        enabled = all(
            str(profile.get("Enabled", "")).lower()
            in ("true", "1")
            for profile in profiles
        )

        return {
            "status": "PASS" if enabled else "WARNING",
            "details": profiles
        }

    except (json.JSONDecodeError, AttributeError):
        return {
            "status": "ERROR",
            "details": "Could not parse firewall information"
        }


def check_windows_defender():
    command = (
        "Get-MpComputerStatus | "
        "Select-Object AntivirusEnabled, "
        "RealTimeProtectionEnabled, "
        "AntispywareEnabled | "
        "ConvertTo-Json -Compress"
    )

    result = run_powershell(command)

    if result["status"] != "OK":
        return result

    try:
        data = json.loads(result["details"])

        protected = (
            data.get("AntivirusEnabled") is True
            and data.get("RealTimeProtectionEnabled") is True
            and data.get("AntispywareEnabled") is True
        )

        return {
            "status": "PASS" if protected else "WARNING",
            "details": data
        }

    except (json.JSONDecodeError, AttributeError):
        return {
            "status": "ERROR",
            "details": "Could not parse Defender information"
        }


def check_system_information():
    return {
        "status": "INFO",
        "details": {
            "operating_system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        }
    }


def run_security_assessment():
    return {
        "assessment": "NEMESIS LOCAL SECURITY ASSESSMENT",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "firewall": check_firewall(),
            "windows_defender": check_windows_defender(),
            "system_information": check_system_information()
        }
    }


if __name__ == "__main__":
    print(json.dumps(
        run_security_assessment(),
        indent=4
    ))
