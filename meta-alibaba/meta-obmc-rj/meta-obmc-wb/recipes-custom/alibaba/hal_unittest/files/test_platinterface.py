import unittest
import time

from plat_hal.interface import interface

class TestPlatInterface(unittest.TestCase):
    def setUp(self):
        self.intf = interface()

    def test_get_state(self):
        ret = self.intf.get_bios_version()
        if ret != -1:
            self.assertIsNotNone(ret["MasterBiosVersion"], "SlaveBiosVersion is None")
            self.assertIsNotNone(ret["SlaveBiosVersion"], "SlaveBiosVersion is None")
            self.assertNotEqual(ret["MasterBiosVersion"], "N/A")
            self.assertNotEqual(ret["SlaveBiosVersion"], "N/A")
            ret = self.intf.get_bios_status()
            self.assertIsNotNone(ret["Flash"], "Flash is None")
            self.assertIsNotNone(ret["Result"], "Result is None")
        else:
            pass

    def test_get_mac_rov(self):
        ret, output = self.intf.get_bmc_mac_rov()
        if "unsupport" not in output:
            self.assertEqual(ret, 0)
            print(ret, output)
        else:
            pass

    def test_monitor_cpu_host_watchdog(self):
        ret = self.intf.monitor_cpu_host_watchdog("10")
        self.assertEqual(ret, 0)

    def tearDown(self):
        pass
