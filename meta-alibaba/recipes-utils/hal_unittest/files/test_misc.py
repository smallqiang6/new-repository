import unittest
import time

from hal.hal_misc import *
import unittest_config

class TestHalMisc(unittest.TestCase):
    def setUp(self):
        self.misc = HalMisc()
        self.cl_image_flag = True if unittest_config.PRODUCT_INFO["VENDER_INFO"] == "CL" else False
        self.lc_image_flag = True if unittest_config.PRODUCT_INFO["VENDER_INFO"] == "LC" else False

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

    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_get_bios_boot_status(self):
        ret = self.misc.get_bios_boot_status()
        self.assertIn(ret["Flash"], ['master', 'slave'])
        self.assertEqual(ret["Result"], "success")

    def test_get_bmc_boot_status(self):
        ret = self.misc.get_bmc_boot_status()
        self.assertIn(ret, ['master', 'slave'])

    def test_set_system_fan_led(self):
        self.sys_service_stop()
        ret = self.misc.set_system_fan_led("green")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_fan_led("yellow")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_fan_led("off")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_fan_led("green", True)
        self.assertEqual(ret, 0)
        self.sys_service_start()

    def test_set_host_cpu_power(self):
        ret = self.misc.set_host_cpu_power("off")
        self.assertEqual(ret, 0)
        time.sleep(15)
        ret = self.misc.get_host_cpu_power_status()
        self.assertEqual(ret, "off")
        ret = self.misc.set_host_cpu_power("on")
        self.assertEqual(ret, 0)
        time.sleep(30)
        ret = self.misc.get_host_cpu_power_status()
        self.assertEqual(ret, "on")
        ret = self.misc.set_host_cpu_power("test")
        self.assertEqual(ret, -1)
        ret = self.misc.get_host_cpu_power_status()
        self.assertEqual(ret, "on")
        ret = self.misc.set_host_cpu_power("cycle")
        self.assertEqual(ret, 0)
        #wait cpu up
        unittest_config.wait_cpu_ready()

    def test_get_host_cpu_power_status(self):
        ret = self.misc.get_host_cpu_power_status()
        self.assertIn(ret, ["on","off"])

    def test_set_location_led(self):
        if unittest_config.determine_whether_test_is_required("is_support_location_led") == False:
            return
        self.sys_service_stop()
        ret = self.misc.set_location_led("on")
        self.assertEqual(ret, 0)
        ret = self.misc.get_location_led()
        self.assertEqual(ret, "on")
        ret = self.misc.set_location_led("off")
        self.assertEqual(ret, 0)
        ret = self.misc.get_location_led()
        self.assertEqual(ret, "off")
        self.sys_service_start()

    def test_get_location_led(self):
        if unittest_config.determine_whether_test_is_required("is_support_location_led") == False:
            return
        ret = self.misc.get_location_led()
        self.assertIn(ret, ["off","on"])

    def test_get_system_airflow(self):
        ret = self.misc.get_system_airflow()
        self.assertIn(ret, ["F2B", "B2F", "LIQUID"])

    def test_get_cpld_user_reg(self):
        tmp_info = self.misc.get_cpld_user_reg()
        self.assertIsNotNone(tmp_info, 'Get CPLD User Reg is None')

    def test_set_cpld_user_reg(self):
        ret = self.misc.set_cpld_user_reg(-1)
        self.assertEqual(ret, -1)
        ret = self.misc.set_cpld_user_reg(0)
        self.assertEqual(ret, 0)
        ret = self.misc.get_cpld_user_reg()
        self.assertEqual(ret, 0)
        ret = self.misc.set_cpld_user_reg(22)
        self.assertEqual(ret, 0)
        ret = self.misc.get_cpld_user_reg()
        self.assertEqual(ret, 22)
        ret = self.misc.set_cpld_user_reg(0xff)
        self.assertEqual(ret, 0)
        ret = self.misc.get_cpld_user_reg()
        self.assertEqual(ret, 255)
        ret = self.misc.set_cpld_user_reg(256)
        self.assertEqual(ret, -1)
        ret = self.misc.set_cpld_user_reg('ss')
        self.assertEqual(ret, -1)

    def test_set_console_owner(self):
        ret = self.misc.set_console_owner(None)
        self.assertEqual(ret, -1)
        ret = self.misc.set_console_owner('test')
        self.assertEqual(ret, -1)
        ret = self.misc.set_console_owner('cpu')
        self.assertEqual(ret, 0)
        ret = self.misc.set_console_owner('cpu')
        self.assertEqual(ret, 0)
        time.sleep(5)
        ret = self.misc.set_console_owner('bmc')
        self.assertEqual(ret, 0)
        ret = self.misc.set_console_owner('bmc')
        self.assertEqual(ret, 0)

    def test_get_cpld_version(self):
        ret = self.misc.get_cpld_version()
        if self.cl_image_flag:
            self.assertNotEqual(ret["CPLD_B"], "N/A")
            self.assertNotEqual(ret["CPLD_FAN"], "N/A")
            print("\nBASE_CPLD version =%s "%repr(ret["CPLD_B"]))
            print("FAN_CPLD version =%s "%repr(ret["CPLD_FAN"]))
        elif self.lc_image_flag:
            for cpld in ret:
                self.assertNotEqual(ret[cpld], "N/A")
                print("\n{} version ={} ".format(cpld, ret[cpld]))
        else:
            for cpld in ret:
                self.assertNotEqual(ret[cpld], "N/A")
                print("\n{} version ={} ".format(cpld, ret[cpld]))

    def test_get_platform_name(self):
        ret = self.misc.get_platform_name()
        self.assertNotEqual(ret, "N/A")
        print("\nproductname =%s="%repr(ret))

    def test_set_system_led(self):
        self.sys_service_stop()
        ret = self.misc.set_system_led("test")
        self.assertEqual(ret, -1)
        ret = self.misc.set_system_led("green")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_led("yellow")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_led("off")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_led("green", True)
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_led("yellow", True)
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_led("off")
        self.assertEqual(ret, 0)
        self.sys_service_start()

    def test_system_power_led_available(self):
        ret = self.misc.system_power_led_available()
        self.assertEqual(ret, True)

    def test_set_system_power_led(self):
        self.sys_service_stop()
        ret = self.misc.set_system_power_led("test")
        self.assertEqual(ret, -1)
        ret = self.misc.set_system_power_led("green")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_power_led("yellow")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_power_led("off")
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_power_led("green", True)
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_power_led("yellow", True)
        self.assertEqual(ret, 0)
        ret = self.misc.set_system_power_led("off")
        self.assertEqual(ret, 0)
        self.sys_service_start()

    def test_host_cpu_power_force_control(self):
        ## when you build the lastest image , then should support this function
        if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
            ret = self.misc.get_host_cpu_power_force_control_status()
            self.assertIn(ret, [1, 0])
            ret = self.misc.enable_host_cpu_power_force_control("test")
            self.assertEqual(ret, -1)
            ret = self.misc.enable_host_cpu_power_force_control(1)
            self.assertEqual(ret, 0)
            ret = self.misc.get_host_cpu_power_force_control_status()
            self.assertEqual(ret, 1)
            ret = self.misc.enable_host_cpu_power_force_control(0)
            self.assertEqual(ret, 0)
            ret = self.misc.get_host_cpu_power_force_control_status()
            self.assertEqual(ret, 0)
        else:
            pass

    def test_ssd_power_control(self):
        if unittest_config.determine_whether_test_is_required("is_support_ssd_power_ctl") == True:
            ret = self.misc.get_ssd_power_status()
            self.assertIn(ret, ["on","off"])
            ret = self.misc.set_ssd_power_status("test")
            self.assertEqual(ret, -1)
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_ssd_power_status("on")
            self.assertEqual(ret, 0)
            ret = self.misc.get_ssd_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_ssd_power_status("off")
            self.assertEqual(ret, 0)
            ret = self.misc.get_ssd_power_status()
            self.assertEqual(ret, "off")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_ssd_power_status("on")
            self.assertEqual(ret, 0)
            ret = self.misc.get_ssd_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_host_cpu_power("cycle")
            self.assertEqual(ret, 0)
            #wait cpu up
            unittest_config.wait_cpu_ready()
        else:
            pass

    def test_switch_chip_power_control(self):
        if unittest_config.determine_whether_test_is_required("is_support_mac_power_ctl") == True:
            ret = self.misc.get_switch_chip_power_status()
            self.assertIn(ret, ["on","off"])
            ret = self.misc.set_switch_chip_power_status("test")
            self.assertEqual(ret, -1)
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_chip_power_status("on")
            self.assertEqual(ret, 0)
            ret = self.misc.get_switch_chip_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_chip_power_status("off")
            self.assertEqual(ret, 0)
            ret = self.misc.get_switch_chip_power_status()
            self.assertEqual(ret, "off")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_chip_power_status("on")
            time.sleep(5)
            self.assertEqual(ret, 0)
            ret = self.misc.get_switch_chip_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(0)
                self.assertEqual(ret, 0)
            ret = self.misc.set_host_cpu_power("cycle")
            self.assertEqual(ret, 0)
            #wait cpu ready
            unittest_config.wait_cpu_ready()
        else:
            pass

    def test_switch_port_power_control(self):
        if unittest_config.determine_whether_test_is_required("is_support_port_power_ctl") == True:
            ret = self.misc.get_switch_port_power_status()
            self.assertIn(ret, ["on","off"])
            ret = self.misc.set_switch_port_power_status("test")
            self.assertEqual(ret, -1)
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_port_power_status("on")
            self.assertEqual(ret, 0)
            ret = self.misc.get_switch_port_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_port_power_status("off")
            self.assertEqual(ret, 0)
            ret = self.misc.get_switch_port_power_status()
            self.assertEqual(ret, "off")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(1)
                self.assertEqual(ret, 0)
            ret = self.misc.set_switch_port_power_status("on")
            self.assertEqual(ret, 0)
            time.sleep(5)
            ret = self.misc.get_switch_port_power_status()
            self.assertEqual(ret, "on")
            if unittest_config.determine_whether_test_is_required("is_support_force_power_ctl") == True:
                ret = self.misc.enable_host_cpu_power_force_control(0)
                self.assertEqual(ret, 0)
            ret = self.misc.set_host_cpu_power("cycle")
            self.assertEqual(ret, 0)
            #wait cpu up
            unittest_config.wait_cpu_ready()
        else:
            pass

    def tearDown(self):
        pass
