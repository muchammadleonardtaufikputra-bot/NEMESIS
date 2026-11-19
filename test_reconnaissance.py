
import unittest
import json
import sqlite3

from modules.reconnaissance import (
    get_system_info,
    get_network_info,
    get_mac_address,
    run_reconnaissance
)

from modules.recon_database import (
    initialize_database,
    save_reconnaissance,
    get_reconnaissance_history,
    DB_PATH
)


class TestReconnaissance(unittest.TestCase):

    def test_system_info(self):
        data = get_system_info()
        self.assertIn("hostname", data)
        self.assertIn("operating_system", data)

    def test_network_info(self):
        data = get_network_info()
        self.assertIn("local_ip", data)

    def test_mac_address(self):
        data = get_mac_address()
        self.assertRegex(
            data,
            r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$"
        )

    def test_reconnaissance(self):
        data = run_reconnaissance()
        self.assertIn("system", data)
        self.assertIn("network", data)
        self.assertIn("network_configuration", data)

    def test_database_storage(self):
        data = run_reconnaissance()

        initialize_database()
        record_id = save_reconnaissance(data)

        self.assertGreater(record_id, 0)

        history = get_reconnaissance_history()
        self.assertGreaterEqual(len(history), 1)

        saved_data = json.loads(history[0]["result_json"])
        self.assertEqual(
            saved_data["system"]["hostname"],
            data["system"]["hostname"]
        )


if __name__ == "__main__":
    unittest.main()
