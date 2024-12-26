import unittest
import time

from hal.hal_cpu import *
from hal.hal_misc import HalMisc
import unittest_config

class TestHalCPU(unittest.TestCase):
    def setUp(self):
        self.cpu = HalCPU()
        self.misc = HalMisc()

    def test_get_state(self):
        cpu_ret = self.misc.set_host_cpu_power("on")
        self.assertEqual(cpu_ret, 0)
        time.sleep(30)
        cpu_status = self.cpu.get_state()
        self.assertIn(cpu_status, ["S0","S1","S2","S3","S4","S5"])
        cpu_ret = self.misc.set_host_cpu_power("off")
        self.assertEqual(cpu_ret, 0)
        time.sleep(30)
        cpu_status = self.cpu.get_state()
        self.assertEqual(cpu_status, "S5")
        cpu_ret = self.misc.set_host_cpu_power("on")
        self.assertEqual(cpu_ret, 0)
        time.sleep(30)
        cpu_status = self.cpu.get_state()
        self.assertEqual(cpu_status, "S0")
        #Wait 60s to ensure that the cpu is powered on finish.
        time.sleep(60)

    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_get_mca_error(self):
        err_arr = self.cpu.get_mca_error()
        self.assertNotEqual(err_arr["MCErr"], -99999)
        self.assertNotEqual(err_arr["IErr"], -99999)

    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_get_aer_error(self):
        aer_arr = self.cpu.get_aer_error()
        self.assertNotEqual(aer_arr[0], -1)
        self.assertNotEqual(aer_arr[1], -1)
        self.assertNotEqual(aer_arr[2], -1)

    def test_get_last_reset(self):
        cpu_last_status = self.cpu.get_last_reset()
        self.assertIn(cpu_last_status, ['WARM', 'COLD'])
    def tearDown(self):
        pass
