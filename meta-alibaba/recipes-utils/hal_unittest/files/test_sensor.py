import unittest
import time
import os
import sys


from hal.hal_sensor import *
import unittest_config


class TestHalSensor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(unittest_config.HAL_UNITTEST_TEST_LOG_PATH):
            os.mkdir(unittest_config.HAL_UNITTEST_TEST_LOG_PATH)
        path = os.path.join(unittest_config.HAL_UNITTEST_TEST_LOG_PATH, unittest_config.HAL_SENSOR_TEST_LOG_FILE)
        self.fd = open(path, 'w')

        self.sensor = HalSensor()

    def test_get_sensor_info(self):
        info = self.sensor.get_sensor_info()
        self.assertIsNotNone(info, msg='get_sensor_info return none')
        content = '{}: get_sensor_info = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        for name, value in info.items():
            msg = 'name is {}\n'.format(name)
            self.assertIsNotNone(value)
            val = value['Value']
            if 'Min' in value.keys():
                val_min = value['Min']
                val_max = value['Max']
            else:
                val_min = value['LowAlarm']
                val_max = value['HighAlarm']
            unit = value['Unit']
            self.assertLessEqual(val, val_max, msg)
            self.assertGreaterEqual(val, val_min, msg)
            self.assertIn(unit, ['V', 'A', 'W', 'RPM', 'C', 'mOHM'], msg)

    @classmethod
    def tearDownClass(self):
        self.fd.close()
