import unittest
import time
import os
import sys

from hal.hal_psu import *
from hal.hal_sensor import *
from hal.hal_misc import *
import unittest_config


class TestHalPsu(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(unittest_config.HAL_UNITTEST_TEST_LOG_PATH):
            os.mkdir(unittest_config.HAL_UNITTEST_TEST_LOG_PATH)
        path = os.path.join(unittest_config.HAL_UNITTEST_TEST_LOG_PATH, unittest_config.HAL_PSU_TEST_LOG_FILE)
        self.fd = open(path, 'w')

        self.psu = HalPsu()
        self.misc = HalMisc()

    def test_get_total_number(self):
        num = self.psu.get_total_number()
        content = '{}: number = {}\n'.format(sys._getframe().f_code.co_name, num)
        self.fd.write(content)
        self.assertNotEqual(num, -1)
        # self.assertIn(num, range(unittest_config.PSU_NUMS_MAX + 1))

    def test_get_presence(self):
        value = [True, False]
        num = self.psu.get_total_number()
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            status = self.psu.get_presence(name)
            content = '{}: {} get_presence = {}\n'.format(sys._getframe().f_code.co_name, name, status)
            self.fd.write(content)
            self.assertIn(status, value)

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  True, "PSU is Fruless, Skip this case!")
    def test_get_fru_info(self):
        num = self.psu.get_total_number()
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            fru = self.psu.get_fru_info(name)
            content = '{}: {} get_fru_info = {}\n'.format(sys._getframe().f_code.co_name, name, fru)
            self.fd.write(content)
            self.assertEqual(fru['Name'], name)
            self.assertIsNotNone(fru['SN'], 'SN is None')
            self.assertIsNotNone(fru['PN'], 'PN is None')
            self.assertIn(fru['AirFlow'], ['F2B', 'B2F', 'LIQUID'])

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  False, "PSU is not Fruless, Skip this case!")
    def test_get_psu_fruless_info(self):
        num = self.psu.get_total_number()
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            fru = self.psu.get_fru_info(name)
            content = '{}: {} get_fru_info = {}\n'.format(sys._getframe().f_code.co_name, name, fru)
            self.fd.write(content)
            self.assertEqual(fru['Name'], name)
            self.assertIsNotNone(fru['SN'], 'Builtin')
            self.assertIsNotNone(fru['PN'], 'Builtin')

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  True, "PSU is Fruless, Skip this case!")
    def test_get_status(self):
        num = self.psu.get_total_number()
        airflow = self.misc.get_system_airflow()
        self.assertIsNotNone(airflow, msg='get_system_airflow return none')
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            status = self.psu.get_status(name)
            content = '{}: {} get_status = {}\n'.format(sys._getframe().f_code.co_name, name, status)
            self.fd.write(content)
            self.assertEqual(status['Name'], name)
            self.assertIn(status['InputType'], ['AC', 'DC', 'N/A'])
            self.assertIn(status['InputStatus'], [True, False])
            self.assertIn(status['OutputStatus'], [True, False])
            if not status['InputStatus']:
                break
            if "LIQUID" not in airflow:
                fanspeed = status['FanSpeed']
                self.assertGreater(fanspeed['Value'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Value'], unittest_config.PSU_SPEED_MAX)
                self.assertGreaterEqual(fanspeed['Min'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Min'], unittest_config.PSU_SPEED_MAX)
                self.assertGreater(fanspeed['Max'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Max'], unittest_config.PSU_SPEED_MAX)
            temp = status['Temperature']
            self.assertGreater(temp['Value'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Value'], unittest_config.PSU_TEMP_MAX)
            self.assertGreaterEqual(temp['Min'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Min'], unittest_config.PSU_TEMP_MAX)
            self.assertGreater(temp['Max'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Max'], unittest_config.PSU_TEMP_MAX)

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  True, "PSU is Fruless, Skip this case!")
    def test_get_power_status(self):
        num = self.psu.get_total_number()
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            status = self.psu.get_power_status(name)
            content = '{}: {} get_power_status = {}\n'.format(sys._getframe().f_code.co_name, name, status)
            self.fd.write(content)
            self.assertEqual(status['Name'], name)
            input_info = status['Inputs']
            self.assertIn(input_info['Status'], [True, False])
            self.assertIn(input_info['Type'], ['AC', 'DC', 'N/A'])
            if not input_info['Status']:
                break
            vol_input = input_info['Voltage']
            self.assertGreater(vol_input['Value'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['Value'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertGreaterEqual(vol_input['LowAlarm'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['LowAlarm'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertGreater(vol_input['HighAlarm'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['HighAlarm'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertEqual(vol_input['Unit'], 'V')
            curr_input = input_info['Current']
            self.assertGreater(curr_input['Value'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['Value'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertGreaterEqual(curr_input['LowAlarm'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['LowAlarm'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertGreater(curr_input['HighAlarm'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['HighAlarm'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertEqual(curr_input['Unit'], 'A')
            power_input = input_info['Power']
            self.assertGreater(power_input['Value'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['Value'], unittest_config.PSU_POWER_IN_MAX)
            self.assertGreaterEqual(power_input['LowAlarm'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['LowAlarm'], unittest_config.PSU_POWER_IN_MAX)
            self.assertGreater(power_input['HighAlarm'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['HighAlarm'], unittest_config.PSU_POWER_IN_MAX)
            self.assertEqual(power_input['Unit'], 'W')

            output_info = status['Outputs']
            self.assertIn(output_info['Status'], [True, False])
            vol_output = output_info['Voltage']
            self.assertGreater(vol_output['Value'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['Value'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertGreaterEqual(vol_output['LowAlarm'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['LowAlarm'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertGreater(vol_output['HighAlarm'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['HighAlarm'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertEqual(vol_output['Unit'], 'V')
            curr_output = output_info['Current']
            self.assertGreater(curr_output['Value'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['Value'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertGreaterEqual(curr_output['LowAlarm'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['LowAlarm'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertGreater(curr_output['HighAlarm'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['HighAlarm'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertEqual(curr_output['Unit'], 'A')
            power_output = output_info['Power']
            self.assertGreater(power_output['Value'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['Value'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertGreaterEqual(power_output['LowAlarm'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['LowAlarm'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertGreater(power_output['HighAlarm'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['HighAlarm'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertEqual(power_output['Unit'], 'W')

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  True, "PSU is Fruless, Skip this case!")
    def test_set_psu_fan_speed_pwm(self):
        num = self.psu.get_total_number()
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            pwm = self.psu.set_psu_fan_speed_pwm(name, 48)
            msg = '{} set pwm return {}'.format(name, pwm)
            self.assertGreaterEqual(pwm, 0, msg)

    @unittest.skipIf(unittest_config.PRODUCT_INFO["PSU_FRULESS"] ==  True, "PSU is Fruless, Skip this case!")
    def test_get_info_all(self):
        info = self.psu.get_info_all()
        content = '{}: get_info_all = {}\n'.format(sys._getframe().f_code.co_name, info)
        self.fd.write(content)
        num = self.psu.get_total_number()
        self.assertIn(num, range(unittest_config.PSU_NUMS_MAX + 1))
        self.assertEqual(info['Number'],num)
        for i in range(num):
            name = 'PSU{}'.format(i + 1)
            status = info[name]
            self.assertIsNotNone(status['SN'], 'SN is None')
            self.assertIsNotNone(status['PN'], 'PN is None')
            self.assertIn(status['AirFlow'], ['F2B', 'B2F', 'LIQUID'])
            self.assertIn(status['Present'], ['yes', 'no'])
            if not  status['Inputs']['Status']:
                break
            if "LIQUID" not in status['AirFlow']:
                fanspeed = status['FanSpeed']
                self.assertGreater(fanspeed['Value'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Value'], unittest_config.PSU_SPEED_MAX)
                self.assertGreaterEqual(fanspeed['Min'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Min'], unittest_config.PSU_SPEED_MAX)
                self.assertGreater(fanspeed['Max'], unittest_config.PSU_SPEED_MIN)
                self.assertLessEqual(fanspeed['Max'], unittest_config.PSU_SPEED_MAX)
            temp = status['Temperature']
            self.assertGreater(temp['Value'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Value'], unittest_config.PSU_TEMP_MAX)
            self.assertGreaterEqual(temp['Min'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Min'], unittest_config.PSU_TEMP_MAX)
            self.assertGreater(temp['Max'], unittest_config.PSU_TEMP_MIN)
            self.assertLessEqual(temp['Max'], unittest_config.PSU_TEMP_MAX)
            input_info = status['Inputs']
            self.assertIn(input_info['Status'], [True, False])
            self.assertIn(input_info['Type'], ['AC', 'DC', 'N/A'])
            vol_input = input_info['Voltage']
            self.assertGreater(vol_input['Value'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['Value'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertGreaterEqual(vol_input['LowAlarm'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['LowAlarm'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertGreater(vol_input['HighAlarm'], unittest_config.PSU_VOLTAGE_IN_MIN)
            self.assertLessEqual(vol_input['HighAlarm'], unittest_config.PSU_VOLTAGE_IN_MAX)
            self.assertEqual(vol_input['Unit'], 'V')
            curr_input = input_info['Current']
            self.assertGreater(curr_input['Value'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['Value'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertGreaterEqual(curr_input['LowAlarm'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['LowAlarm'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertGreater(curr_input['HighAlarm'], unittest_config.PSU_CURRENT_IN_MIN)
            self.assertLessEqual(curr_input['HighAlarm'], unittest_config.PSU_CURRENT_IN_MAX)
            self.assertEqual(curr_input['Unit'], 'A')
            power_input = input_info['Power']
            self.assertGreater(power_input['Value'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['Value'], unittest_config.PSU_POWER_IN_MAX)
            self.assertGreaterEqual(power_input['LowAlarm'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['LowAlarm'], unittest_config.PSU_POWER_IN_MAX)
            self.assertGreater(power_input['HighAlarm'], unittest_config.PSU_POWER_IN_MIN)
            self.assertLessEqual(power_input['HighAlarm'], unittest_config.PSU_POWER_IN_MAX)
            self.assertEqual(power_input['Unit'], 'W')

            output_info = status['Outputs']
            self.assertIn(output_info['Status'], [True, False])
            vol_output = output_info['Voltage']
            self.assertGreater(vol_output['Value'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['Value'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertGreaterEqual(vol_output['LowAlarm'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['LowAlarm'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertGreater(vol_output['HighAlarm'], unittest_config.PSU_VOLTAGE_OUT_MIN)
            self.assertLessEqual(vol_output['HighAlarm'], unittest_config.PSU_VOLTAGE_OUT_MAX)
            self.assertEqual(vol_output['Unit'], 'V')
            curr_output = output_info['Current']
            self.assertGreater(curr_output['Value'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['Value'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertGreaterEqual(curr_output['LowAlarm'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['LowAlarm'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertGreater(curr_output['HighAlarm'], unittest_config.PSU_CURRENT_OUT_MIN)
            self.assertLessEqual(curr_output['HighAlarm'], unittest_config.PSU_CURRENT_OUT_MAX)
            self.assertEqual(curr_output['Unit'], 'A')
            power_output = output_info['Power']
            self.assertGreater(power_output['Value'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['Value'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertGreaterEqual(power_output['LowAlarm'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['LowAlarm'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertGreater(power_output['HighAlarm'], unittest_config.PSU_POWER_OUT_MIN)
            self.assertLessEqual(power_output['HighAlarm'], unittest_config.PSU_POWER_OUT_MAX)
            self.assertEqual(power_output['Unit'], 'W')



    @classmethod
    def tearDownClass(self):
        self.fd.close()
