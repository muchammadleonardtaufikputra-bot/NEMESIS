
import platform
import socket
import uuid
import getpass
import subprocess
from datetime import datetime


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat()
    }


def get_network_info():
    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "Unavailable"

    return {
        "hostname": hostname,
        "local_ip": local_ip
    }


def get_mac_address():
    mac = uuid.getnode()

    return ":".join(
        f"{(mac >> shift) & 0xff:02x}"
        for shift in range(40, -1, -8)
    )


def get_windows_network_config():
    if platform.system() != "Windows":
        return {"error": "Windows only"}

    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        return {
            "return_code": result.returncode,
            "output": result.stdout[:12000]
        }

    except (subprocess.TimeoutExpired, OSError) as error:
        return {"error": str(error)}


def run_reconnaissance():
    return {
        "system": get_system_info(),
        "network": get_network_info(),
        "mac_address": get_mac_address(),
        "network_configuration": get_windows_network_config()
    }


if __name__ == "__main__":
    import json

    print(json.dumps(
        run_reconnaissance(),
        indent=4
    ))
