import unittest
import time
import os
import sys

from hal.hal_temp import *
from hal.hal_sensor import *
import unittest_config


class TestHalTemperature(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(unittest_config.HAL_UNITTEST_TEST_LOG_PATH):
            os.mkdir(unittest_config.HAL_UNITTEST_TEST_LOG_PATH)
        path = os.path.join(unittest_config.HAL_UNITTEST_TEST_LOG_PATH, unittest_config.HAL_TEMP_TEST_LOG_FILE)
        self.fd = open(path, 'w')

        sensor = HalSensor()
        self.temp = HalTemperature(sensor)

    def test_get_cpu_temp(self):
        info = self.temp.get_cpu_temp()
        content = '{}: info = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        self.assertIsNotNone(info, msg='get_cpu_temp return none')
        val = info['Value']
        val_min = info['Min']
        val_max = info['Max']
        unit = info['Unit']
        self.assertLessEqual(val, val_max)
        self.assertGreaterEqual(val, val_min)
        self.assertEqual(unit, 'C')

    def test_get_inlet_temp(self):
        info = self.temp.get_inlet_temp()
        content = '{}: info = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        self.assertIsNotNone(info, msg='get_inlet_temp return none')
        val = info['Value']
        val_min = info['Min']
        val_max = info['Max']
        unit = info['Unit']
        self.assertLessEqual(val, val_max)
        self.assertGreaterEqual(val, val_min)
        self.assertEqual(unit, 'C')

    def test_get_switch_temp(self):
        info = self.temp.get_switch_temp()
        content = '{}: info = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        self.assertIsNotNone(info, msg='get_switch_temp return none')
        val = info['Value']
        val_min = info['Min']
        val_max = info['Max']
        unit = info['Unit']
        self.assertLessEqual(val, val_max)
        self.assertGreaterEqual(val, val_min)
        self.assertEqual(unit, 'C')

    @classmethod
    def tearDownClass(self):
        self.fd.close()

