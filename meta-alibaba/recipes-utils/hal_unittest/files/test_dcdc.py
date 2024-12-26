import unittest
import time
import os
import sys

from hal.hal_dcdc import *
from hal.hal_sensor import *
import unittest_config


class TestHalDcdc(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(unittest_config.HAL_UNITTEST_TEST_LOG_PATH):
            os.mkdir(unittest_config.HAL_UNITTEST_TEST_LOG_PATH)
        path = os.path.join(unittest_config.HAL_UNITTEST_TEST_LOG_PATH, unittest_config.HAL_DCDC_TEST_LOG_FILE)
        self.fd = open(path, 'w')

        sensor = HalSensor()
        self.dcdc = HalDcdc(sensor)

    def test_get_dcdc_sensors(self):
        info = self.dcdc.get_dcdc_sensors()
        content = '{}: info = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        self.assertIsNotNone(info, msg='get_dcdc_sensors return none')
        for name in info:
            if name.find('_V') == -1 and name.find('_C') == -1 and name.find('_P') == -1 and name.find('_R') == -1:
                self.assertTrue(False, msg='The name not include _V/_C/_P/_R')

    def test_get_dcdc_sensor_value(self):
        info = self.dcdc.get_dcdc_sensors()
        self.assertIsNotNone(info, msg='get_dcdc_sensors return none')
        for name in info:
            dic = self.dcdc.get_dcdc_sensor_value(name)
            content = '{}: {} = {}\n'.format(sys._getframe().f_code.co_name, name, dic)
            self.fd.write(content)
            self.assertIsNotNone(dic, msg='get_dcdc_sensor_value return none')
            val = dic['Value']
            val_min = dic['Min']
            val_max = dic['Max']
            unit = dic['Unit']
            self.assertLessEqual(val, val_max)
            self.assertGreaterEqual(val, val_min)
            self.assertIn(unit, ['V', 'A', 'W', 'mOHM'])

    def test_get_dcdc_sensor_descr(self):
        info = self.dcdc.get_dcdc_sensors()
        self.assertIsNotNone(info, msg='get_dcdc_sensors return none')
        for name in info:
            dic = self.dcdc.get_dcdc_sensor_descr(name)
            content = '{}: {} = {}\n'.format(sys._getframe().f_code.co_name, name, dic)
            self.fd.write(content)
            self.assertIsNotNone(dic, msg='get_dcdc_sensor_descr return none')

    def test_get_dcdc_all_info(self):
        info = self.dcdc.get_dcdc_all_info()
        self.assertIsNotNone(info, msg='get_dcdc_all_info return none')
        for name, value in info.items():
            if name.find('_V') == -1 and name.find('_C') == -1 and name.find('_P') == -1 and name.find('_R') == -1:
                self.assertTrue(False, msg='The name not include _V/_C/_P/_R')
            self.assertIsNotNone(value)
            val = value['Value']
            val_min = value['Min']
            val_max = value['Max']
            unit = value['Unit']
            self.assertLessEqual(val, val_max)
            self.assertGreaterEqual(val, val_min)
            self.assertIn(unit, ['V', 'A', 'W', 'mOHM'])


    @classmethod
    def tearDownClass(self):
        self.fd.close()

