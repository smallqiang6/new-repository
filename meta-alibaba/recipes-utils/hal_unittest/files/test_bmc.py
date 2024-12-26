import unittest
import time

from hal.hal_bmc import *

class TestHalBmc(unittest.TestCase):
    def setUp(self):
        self.bmc = HalBmc()

    def test_get_state(self):
        bmc_info = self.bmc.get_info()
        self.assertIsNotNone(bmc_info["Version"], 'Version is None')
        self.assertNotEqual(bmc_info["Version"], "N/A")
        self.assertIn(bmc_info["Flash"], ['master', 'slave'])
        self.assertIn(bmc_info["Next"], ['master', 'slave'])

    def test_get_version_all(self):
        all_ver = self.bmc.get_version_all()
        self.assertIsNotNone(all_ver["MasterVersion"], 'MasterVersion is None')
        self.assertNotEqual(all_ver["MasterVersion"], "N/A")
        self.assertIsNotNone(all_ver["SlaveVersion"], 'SlaveVersion is None')
        self.assertNotEqual(all_ver["SlaveVersion"], "N/A")

    def test_get_status(self):
        status = self.bmc.get_status()
        self.assertIsNotNone(status["CPU"], "cpu IS None")
        self.assertNotEqual(status["CPU"], "N/A")
        self.assertIsNotNone(status["MEMORY"], "MEMORY IS None")
        self.assertNotEqual(status["MEMORY"], "N/A")
        self.assertIsNotNone(status["DISK"], "DISK IS None")
        self.assertNotEqual(status["DISK"], "N/A")

    def test_get_next_boot(self):
        nex_boot = self.bmc.get_next_boot()
        self.assertIn(nex_boot, ['master', 'slave'])

    def test_set_next_boot(self):
        ret = self.bmc.set_next_boot("both")
        self.assertEqual(ret, -1)
        ret = self.bmc.set_next_boot(None)
        self.assertEqual(ret, -1)
        ret = self.bmc.set_next_boot("master")
        self.assertEqual(ret, 0)
        nex_boot = self.bmc.get_next_boot()
        self.assertEqual(nex_boot, 'master')
        ret = self.bmc.set_next_boot("slave")
        self.assertEqual(ret, 0)
        nex_boot = self.bmc.get_next_boot()
        self.assertEqual(nex_boot, 'slave')

    def tearDown(self):
        pass
