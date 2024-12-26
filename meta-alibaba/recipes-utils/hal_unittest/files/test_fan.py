import unittest
import time
import os
import sys

from hal.hal_fan import *
from hal.hal_misc import *
import unittest_config


class TestHalFan(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(unittest_config.HAL_UNITTEST_TEST_LOG_PATH):
            os.mkdir(unittest_config.HAL_UNITTEST_TEST_LOG_PATH)
        path = os.path.join(unittest_config.HAL_UNITTEST_TEST_LOG_PATH, unittest_config.HAL_FAN_TEST_LOG_FILE)
        self.fd = open(path, 'w')

        self.fan = HalFan()
        self.misc = HalMisc()
        self.cl_image_flag = True if unittest_config.PRODUCT_INFO["VENDER_INFO"] == "CL" else False
        

    def test_get_total_number(self):
        num = self.fan.get_total_number()
        content = '{}: number = {}\n'.format(sys._getframe().f_code.co_name, num)
        self.fd.write(content)
        self.assertNotEqual(num, -1)

    def test_get_rotor_number(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            num = self.fan.get_rotor_number(name)
            content = '{}: {} rotor_number = {}\n'.format(sys._getframe().f_code.co_name, name, num)
            self.fd.write(content)
            self.assertNotEqual(num, -1)

    def test_get_speed(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            num = self.fan.get_rotor_number(name)
            for j in range(num):
                rpm = self.fan.get_speed(name, j + 1)
                content = '{}: {} speed = {}\n'.format(sys._getframe().f_code.co_name, name, rpm)
                self.fd.write(content)
                msg = '{} speed is {}, is not in range({},{})'.format(name, rpm, unittest_config.FAN_SPEED_MIN, unittest_config.FAN_SPEED_MAX)
                self.assertLessEqual(rpm, unittest_config.FAN_SPEED_MAX, msg)
                self.assertGreaterEqual(rpm, unittest_config.FAN_SPEED_MIN, msg)

    def sys_service_stop(self):
        #stop service for test
        os.system("systemctl stop cpumon;systemctl stop dcdcmon")
        os.system("systemctl stop powermon;systemctl stop fanctrl")

    def sys_service_start(self):
        #start service for normal control
        os.system("systemctl start cpumon;systemctl start dcdcmon")
        os.system("systemctl start powermon;systemctl start fanctrl")
        #waiting service start
        time.sleep(40)

    def test_set_speed(self):
        ### we need to stop services before testing
        if not self.cl_image_flag and self.misc.get_system_airflow() == "LIQUID":
            return
        self.sys_service_stop()
        self.fan.enable_watchdog(False)
        status = self.fan.get_watchdog_status()
        msg = 'fan watchdog current state: {}'.format(status)
        self.assertEqual(status, 'Normal', msg)
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            num = self.fan.get_rotor_number(name)
            for j in range(num):
                pwm = 48
                self.fan.set_speed_pwm(name, j + 1, pwm)
                time.sleep(5)
                rpm = self.fan.get_speed(name, j + 1)

                self.fan.set_speed_pwm(name, j + 1, pwm * 2)
                time.sleep(5)
                rpm_tmp = self.fan.get_speed(name, j + 1)
                content = '{}: {} set pwm {}, read rpm {}\n'.format(sys._getframe().f_code.co_name, name, pwm * 2, rpm_tmp)
                self.fd.write(content)
                msg = '{} previous speed is {}, after set pwm {}, the speed is {}'.format(name, rpm, pwm * 2, rpm_tmp)
                self.assertGreater(rpm_tmp - rpm, 1000, msg)

                self.fan.set_speed_pwm(name, j + 1, pwm / 2)
                time.sleep(10)
                rpm_tmp = self.fan.get_speed(name, j + 1)
                content = '{}: {} set pwm {}, read rpm {}\n'.format(sys._getframe().f_code.co_name, name, pwm / 2, rpm_tmp)
                self.fd.write(content)
                msg = '{} previous speed is {}, after set pwm {}, the speed is {}'.format(name, rpm, pwm / 2, rpm_tmp)
                self.assertGreater(rpm - rpm_tmp, 1000, msg)
        #if not self.cl_image_flag:
        self.sys_service_start()
        self.fan.enable_watchdog(True)
        status = self.fan.get_watchdog_status()
        msg = 'fan watchdog current state: {}'.format(status)
        self.assertEqual(status, 'Normal', msg)

    def test_get_speed_pwm(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            num = self.fan.get_rotor_number(name)
            for j in range(num):
                pwm = self.fan.get_speed_pwm(name, j + 1)
                content = '{}: {} get pwm = {}\n'.format(sys._getframe().f_code.co_name, name, pwm)
                self.fd.write(content)
                msg = '{} pwm is {}'.format(name, pwm)
                self.assertGreater(pwm, 0, msg)
                self.assertLessEqual(pwm, 255, msg)

    def test_set_speed_pwm(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            num = self.fan.get_rotor_number(name)
            for j in range(num):
                pwm = self.fan.set_speed_pwm(name, j + 1, 57)
                msg = '{} set pwm return {}'.format(name, pwm)
                self.assertGreaterEqual(pwm, 0, msg)

    def test_get_watchdog_status(self):
        if not self.cl_image_flag and self.misc.get_system_airflow() == "LIQUID":
            return
        expect_info = ['Normal', 'Abnormal', 'Failed']
        status = self.fan.get_watchdog_status()
        content = '{}: get status = {}\n'.format(sys._getframe().f_code.co_name, status)
        self.fd.write(content)
        self.assertIn(status, expect_info)

    def test_enable_watchdog(self):
        if not self.cl_image_flag and self.misc.get_system_airflow() == "LIQUID":
            return
        status = self.fan.get_watchdog_status()
        if status == 'Normal' or status == 'Abnormal':
            self.fan.enable_watchdog(False)
            status = self.fan.get_watchdog_status()
            content = '{}: set status Normal read status {}\n'.format(sys._getframe().f_code.co_name, status)
            self.fd.write(content)
            self.assertEqual(status, 'Normal')

            self.fan.enable_watchdog(True)
            ret = self.fan.feed_watchdog(27)
            self.assertGreaterEqual(ret, 0)
            status = self.fan.get_watchdog_status()
            content = '{}: set status Normal read status {}\n'.format(sys._getframe().f_code.co_name, status)
            self.fd.write(content)
            self.assertEqual(status, 'Normal')
        else:
            #self.assertIs(status, 'Normal')
            self.assertTrue(False, 'get watchdog status fail')

    def test_feed_watchdog(self):
        if not self.cl_image_flag and self.misc.get_system_airflow() == "LIQUID":
            return
        self.fan.enable_watchdog(True)
        ret = self.fan.feed_watchdog(27)
        self.assertGreaterEqual(ret, 0)

    def test_set_led(self):
        if unittest_config.determine_whether_test_is_required("is_support_fancpld") == True:
            value = ['green', 'yellow', 'off']
            fan_num = self.fan.get_total_number()
            for i in range(fan_num):
                name = 'FAN{}'.format(i + 1)
                for j in value:
                    ret = self.fan.set_led(name, j)
                    self.assertGreaterEqual(ret, 0)
        else:
            pass

    def test_get_presence(self):
        value = [True, False]
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            status = self.fan.get_presence(name)
            content = '{}: {} get_presence = {}\n'.format(sys._getframe().f_code.co_name, name, status)
            self.fd.write(content)
            self.assertIn(status, value)

    @unittest.skipIf(unittest_config.PRODUCT_INFO["FAN_FRULESS"] ==  True, "FAN MODULE is  Builtin,   Skip this case!")
    def test_get_fru_info(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            fru = self.fan.get_fru_info(name)
            content = '{}: {} get_fru_info = {}\n'.format(sys._getframe().f_code.co_name, name, fru)
            self.fd.write(content)
            self.assertEqual(fru['Name'], name)
            self.assertIsNotNone(fru['SN'], 'SN is None')
            self.assertIsNotNone(fru['PN'], 'PN is None')
            self.assertGreater(fru['Rotors'], 0)
            self.assertIn(fru['AirFlow'], ['F2B', 'B2F'])
            self.assertGreaterEqual(fru['SpeedMin'], unittest_config.FAN_SPEED_MIN)
            self.assertLessEqual(fru['SpeedMin'], unittest_config.FAN_SPEED_MAX)
            self.assertGreater(fru['SpeedMax'], unittest_config.FAN_SPEED_MIN)
            self.assertLessEqual(fru['SpeedMax'], unittest_config.FAN_SPEED_MAX)

    @unittest.skipIf(unittest_config.PRODUCT_INFO["FAN_FRULESS"] ==  False, "FAN MODULE is not Builtin,   Skip this case!")
    def test_get_fan_fruless_info(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            fru = self.fan.get_fru_info(name)
            content = '{}: {} get_fru_info = {}\n'.format(sys._getframe().f_code.co_name, name, fru)
            self.fd.write(content)
            self.assertEqual(fru['Name'], name)
            self.assertEqual(fru['SN'], 'Builtin')
            self.assertEqual(fru['PN'], 'Builtin')


    def test_get_status(self):
        fan_num = self.fan.get_total_number()
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            status = self.fan.get_status(name)
            content = '{}: {} get_status = {}\n'.format(sys._getframe().f_code.co_name, name, status)
            self.fd.write(content)
            rotor = self.fan.get_rotor_number(name)
            self.assertEqual(len(status), rotor,
            'the len of {} status({}) is not equal the len of rotor number({})'.format(name, len(status), rotor))
            for i in range(rotor):
                rotor_name = 'Rotor{}'.format(i + 1)
                rotor_info = status[rotor_name]
                self.assertIn(rotor_info['Running'], ['yes', 'no'])
                self.assertIn(rotor_info['HwAlarm'], ['yes', 'no'])
                self.assertGreater(rotor_info['Speed'], unittest_config.FAN_SPEED_MIN)
                self.assertLessEqual(rotor_info['Speed'], unittest_config.FAN_SPEED_MAX)

    def test_get_info_all(self):
        if not self.cl_image_flag and self.misc.get_system_airflow() == "LIQUID":
            return
        fru = self.fan.get_info_all()
        content = '{}: get_info_all = {}\n'.format(sys._getframe().f_code.co_name, fru)
        self.fd.write(content)
        fan_num = self.fan.get_total_number()
        self.assertEqual(fru['Number'],fan_num)
        self.assertIn(fru['WatchdogStatus'], ['Normal', 'Abnormal'])
        for i in range(fan_num):
            name = 'FAN{}'.format(i + 1)
            present = self.fan.get_presence(name)
            info = fru[name]
            self.assertEqual(info['Name'], name)
            self.assertIn(info['Present'], ['yes', 'no'])
            self.assertGreater(info['Rotors'], 0)
            if unittest_config.determine_whether_test_is_required("is_support_fancpld") == True:
                self.assertIsNotNone(info['SN'], 'SN is None')
                self.assertIsNotNone(info['PN'], 'PN is None')
                self.assertIn(info['AirFlow'], ['F2B', 'B2F'])
            rotor = self.fan.get_rotor_number(name)
            for j in range(rotor):
                rotor_name = 'Rotor{}'.format(j + 1)
                rotor_info = info[rotor_name]
                self.assertGreaterEqual(rotor_info['SpeedMin'], unittest_config.FAN_SPEED_MIN)
                self.assertLessEqual(rotor_info['SpeedMin'], unittest_config.FAN_SPEED_MAX)
                self.assertGreater(rotor_info['SpeedMax'], unittest_config.FAN_SPEED_MIN)
                self.assertLessEqual(rotor_info['SpeedMax'], unittest_config.FAN_SPEED_MAX)
                self.assertIn(rotor_info['Running'], ['yes', 'no'])
                self.assertIn(rotor_info['HwAlarm'], ['yes', 'no'])
                self.assertGreater(rotor_info['Speed'], unittest_config.FAN_SPEED_MIN)
                self.assertLessEqual(rotor_info['Speed'], unittest_config.FAN_SPEED_MAX)

    @classmethod
    def tearDownClass(self):
        self.fd.close()

