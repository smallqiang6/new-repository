import unittest
import time
import os

from hal.hal_firmware import *
from hal.hal_misc import *
import unittest_config

file_list_32_rj = ["/tmp/as13-32h_cpld_1_cpu_pwr.vme",
                         "/tmp/as13-32h_cpld_2_cpu_pwr.vme",
                         "/tmp/as13-32h_cpld_3_cpu_pwr.vme",
                         "/tmp/as13-32h_cpld_4_cpu_pwr.vme"]
name_list_32_rj = ["CPU_BOARD_CPLD","CPU_MODULE_CPLD","MAC_BOARD_CPLD_1","MAC_BOARD_CPLD_2"]

file_list_48_rj = ["/tmp/as13-48f8h_cpld_1_cpu_pwr.vme",
                         "/tmp/as13-48f8h_cpld_2_cpu_pwr.vme",
                         "/tmp/as13-48f8h_cpld_3_cpu_pwr.vme",
                         "/tmp/as13-48f8h_cpld_4_cpu_pwr.vme"]
name_list_48_rj = ["CPU_BOARD_CPLD","CPU_MODULE_CPLD","MAC_BOARD_CPLD_1","MAC_BOARD_CPLD_2"]

file_list_ph_rj = ["/tmp/as23-128h_cpld_1_main_cpu_pwr.vme",
                         "/tmp/as23-128h_cpld_2_main_cpu_pwr.vme",
                         "/tmp/as23-128h_cpld_3_main_cpu_pwr.vme",
                         "/tmp/as23-128h_cpld_1_sub_cpu_pwr.vme",
                         "/tmp/as23-128h_cpld_2_sub_cpu_pwr.vme"]
name_list_ph_rj = ["CPU_BOARD_CPLD-FAN","CPU_BOARD_CPLD","CPU_MODULE_CPLD","LC_CPLD1","LC_CPLD2"]

file_list_14_40d_rj = ["/tmp/as14-40d_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as14-40d_cpld_1_1_cpu_pwr.vme",
                         "/tmp/as14-40d_cpld_2_2_cpu_pwr.vme",
                         "/tmp/as14-40d_cpld_3_3_cpu_pwr.vme",
                         "/tmp/as14-40d_cpld_4_3_cpu_pwr.vme"]
name_list_14_40d_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "MAC_BOARD_CPLD_1","MAC_BOARD_CPLD_2"]

file_list_14_128h_rj = ["/tmp/as14-128h_cpld_1_main_cpu_pwr.vme",
                         "/tmp/as14-128h_cpld_2_main_cpu_pwr.vme",
                         "/tmp/as14-128h_cpld_3_main_cpu_pwr.vme",
                         "/tmp/as14-128h_cpld_1_sub_cpu_pwr.vme",
                         "/tmp/as14-128h_cpld_2_sub_cpu_pwr.vme"]
name_list_14_128h_rj = ["CPU_BOARD_CPLD-FAN","CPU_BOARD_CPLD","CPU_MODULE_CPLD","LC_CPLD1","LC_CPLD2"]


file_list_32_cl = ["/tmp/image/fishbone32basecpld.vme",
                         "/tmp/image/fishbone32fancpld.vme",
                         "/tmp/image/fishbone32cpucpld.vme",
                         "/tmp/image/fishbone32sw1cpld.vme",
                         "/tmp/image/fishbone32sw2cpld.vme"]

file_list_48_cl = ["/tmp/image/fishbone48basecpld.vme",
                         "/tmp/image/fishbone48fancpld.vme",
                         "/tmp/image/fishbone48cpucpld.vme",
                         "/tmp/image/fishbone48sw1cpld.vme",
                         "/tmp/image/fishbone48sw2cpld.vme"]
name_list_fb_cl = ["BASE_CPLD","FAN_CPLD","CPU_CPLD","SW_CPLD1","SW_CPLD2"]

file_list_ph_cl = ["/tmp/image/phalanxbasecpld.vme",
                         "/tmp/image/phalanxfancpld.vme",
                         "/tmp/image/phalanxcpucpld.vme",
                         "/tmp/image/phalanxlc1cpld.vme",
                         "/tmp/image/phalanxlc2cpld.vme"]
name_list_ph_cl = ["BASE_CPLD","FAN_CPLD","CPU_CPLD","TOP_LC_CPLD","BOT_LC_CPLD"]

file_list_24_128d_rj = ["/tmp/as24-128d_cpld_0_0_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_1_1_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_2_2_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_3_3_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_4_3_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_5_4_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_6_4_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_7_5_cpu_pwr.vme",
                        "/tmp/as24-128d_cpld_8_5_cpu_pwr.vme"]

name_list_24_128d_rj = [ "CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "MAC_BOARD_CPLD_1",
                         "MAC_BOARD_CPLD_2", "40CCQ_CPLD_1", "40CCQ_CPLD_2", "44CCQ_CPLD_1", "44CCQ_CPLD_2"]

file_list_14_40d_cl = ["/tmp/image/shamubasecpld.vme",
                         "/tmp/image/shamufancpld.vme",
                        "/tmp/image/shamucpucpld.vme",
                         "/tmp/image/shamuswcpld.vme"]
name_list_14_40d_cl = ["BASE_CPLD","FAN_CPLD","CPU_CPLD","SW_CPLD1"]

file_list_14_128h_cl = ["/tmp/image/jawsbasecpld.vme",
                         "/tmp/image/jawsfancpld.vme",
                         "/tmp/image/jawscpucpld.vme",
                         "/tmp/image/jawslc1cpld.vme",
                         "/tmp/image/jawslc2cpld.vme",
                         "/tmp/image/jawsswcpld.vme"]
name_list_14_128h_cl = ["BASE_CPLD","FAN_CPLD","CPU_CPLD","TOP_LC_CPLD","BOT_LC_CPLD","SW_CPLD1"]

file_list_24_128d_cl = ["/tmp/image/migaloobasecpld.vme",
                         "/tmp/image/migaloofancpld.vme",
                         "/tmp/image/migaloocpucpld.vme",
                         "/tmp/image/migaloolc1cpld.vme",
                         "/tmp/image/migaloolc2cpld.vme",
                         "/tmp/image/migalooswcpld.vme"]
name_list_24_128d_cl = ["BASE_CPLD","FAN_CPLD","CPU_CPLD","TOP_LC_CPLD","BOT_LC_CPLD","SW_CPLD1"]

file_list_61_48x4t_rj = ["/tmp/as61-48x4t_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as61-48x4t_cpld_1_0_cpu_pwr.vme",
                         "/tmp/as61-48x4t_cpld_2_0_cpu_pwr.vme"]
name_list_61_48x4t_rj = ["CTRL_MODULE_CPLD","PORT_BOARD_CPLD_1","PORT_BOARD_CPLD_2"]

file_list_61_48e4t_rj = ["/tmp/as61-48e4t_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as61-48e4t_cpld_1_0_cpu_pwr.vme"]
name_list_61_48e4t_rj = ["CTRL_MODULE_CPLD","PORT_BOARD_CPLD"]

file_list_51_48c2g_rj = ["/tmp/ac51-48c2g_cpld_0_0_cpu_pwr.vme",
                         "/tmp/ac51-48c2g_cpld_1_1_cpu_pwr.vme",
                         "/tmp/ac51-48c2g_cpld2_1_1_cpu_pwr.vme",
                         "/tmp/ac51-48c2g_cpld_2_1_cpu_pwr.vme"]
name_list_51_48c2g_rj = ["CPU_MODULE_CPLD","CPU_BOARD_CPLD","CPU_BOARD_CPLD2","PORT_BOARD_CPLD"]

file_list_14_24d8q_rj = ["/tmp/as14-24d8q_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as14-24d8q_cpld_1_1_cpu_pwr.vme",
                         "/tmp/as14-24d8q_cpld_2_2_cpu_pwr.vme",
                         "/tmp/as14-24d8q_cpld_3_3_cpu_pwr.vme",
                         "/tmp/as14-24d8q_cpld_4_3_cpu_pwr.vme"]
name_list_14_24d8q_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "MAC_BOARD_CPLD_1","MAC_BOARD_CPLD_2"]

file_list_25_128q_rj = ["/tmp/as25-128q_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_1_1_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_2_2_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as25-128q_cpld_7_7_cpu_pwr.vme"]
name_list_25_128q_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "LC_BOARD_CPLD", "MAC_BOARD_CPLD_2", "MAC_BOARD_CPLD_1", "MAC_MISC_CPLD"]

file_list_24_128d_2_rj = ["/tmp/as24-128d-2_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_1_1_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_2_2_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_all_port_cpu_pwr.vme",
                         "/tmp/as24-128d-2_cpld_7_7_cpu_pwr.vme"]
name_list_24_128d_2_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "LC_BOARD_CPLD", "MAC_BOARD_CPLD_2", "MAC_BOARD_CPLD_1", "MAC_MISC_CPLD"]


file_list_51_24d_rj = ["/tmp/as51-24d-a1_cpld_0_0_cpu_pwr.vme",
                         "/tmp/as51-24d-a1_cpld_1_1_cpu_pwr.vme",
                         "/tmp/as51-24d-a1_cpld_2_2_cpu_pwr.vme",
                         "/tmp/as51-24d-a1_cpld_3_3_cpu_pwr.vme",
                         "/tmp/as51-24d-a1_cpld_4_4_cpu_pwr.vme",
                         "/tmp/as51-24d-a1_cpld_5_5_cpu_pwr.vme"]
name_list_51_24d_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "CPU_BOARD_CPLD-FAN", "SWITCH_MISC_CPLD", "SWITCH_CPLD_A", "SWITCH_CPLD_B"]

file_list_15_40q_rj = ["/tmp/as15-40q_cpld_1_1_cpu_pwr_header.vme",
                         "/tmp/as15-40q_cpld_2_2_cpu_pwr_header.vme",
                         "/tmp/as15-40q_cpld_3_3_cpu_pwr_header.vme",
                         "/tmp/as15-40q_cpld_4_4_cpu_pwr_header.vme",
                         "/tmp/as15-40q_cpld_5_5_cpu_pwr_header.vme"]
name_list_15_40q_rj = ["CPU_MODULE_CPLD", "CPU_BOARD_CPLD", "MAC_BOARD_CPLD_1", "CPU_BOARD_CPLD-FAN", "MAC_MISC_CPLD"]



class TestHalFirmware(unittest.TestCase):
    def setUp(self):
        self.fw = HalFirmware()
        self.misc = HalMisc()
        self.cl_image_flag = True if unittest_config.PRODUCT_INFO["VENDER_INFO"] == "CL" else False

    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_program_bios(self):
        ret = self.fw.program_bios("master", "/tmp/testerr")
        self.assertEqual(ret, -1)
        ret = self.fw.program_bios("test", "/tmp/bios.bin")
        self.assertEqual(ret, -1)
        ret = self.fw.program_bios("master", "/tmp/bios.bin")
        self.assertEqual(ret, 0)
        ret = self.fw.program_bios("slave", "/tmp/bios.bin")
        self.assertEqual(ret, 0)

    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_get_bios_next_boot(self):
        ret = self.fw.get_bios_next_boot()
        self.assertIn(ret, ['master', 'slave'])


    @unittest.skipUnless(unittest_config.PRODUCT_INFO["ARCH_PLATFORM"] ==  "X86", "CPU PLATFROM is not X86, Skip this case!")
    def test_set_bios_next_boot(self):
        ret = self.fw.set_bios_next_boot("test")
        self.assertEqual(ret, -1)
        ret = self.fw.set_bios_next_boot("slave")
        self.assertEqual(ret, 0)
        ret = self.fw.get_bios_next_boot()
        self.assertEqual(ret, 'slave')
        ret = self.fw.set_bios_next_boot("master")
        self.assertEqual(ret, 0)
        ret = self.fw.get_bios_next_boot()
        self.assertEqual(ret, 'master')

    def test_program_bmc(self):
        ret = self.fw.program_bmc("master", "/tmp/testerr")
        self.assertEqual(ret, -1)
        ret = self.fw.program_bmc("test", "/tmp/image-bmc")
        self.assertEqual(ret, -1)
        ret = self.fw.program_bmc("slave", "/tmp/image-bmc")
        self.assertEqual(ret, 0)
        ret = self.fw.program_bmc("master", "/tmp/image-bmc")
        self.assertEqual(ret, 0)

    def test_program_cpld(self):
        output = self.misc.get_platform_name()
        self.assertIsNotNone(output, 'get platform name is None')
        if "32" in output:
            if self.cl_image_flag:
                file_list = file_list_32_cl
                name_list = name_list_fb_cl
            else:
                file_list = file_list_32_rj
                name_list = name_list_32_rj
        elif "AS13-48F8H" in output:
            if self.cl_image_flag:
                file_list = file_list_48_cl
                name_list = name_list_fb_cl
            else:
                file_list = file_list_48_rj
                name_list = name_list_48_rj
        elif "AS14-40D" in output:
            if self.cl_image_flag:
                file_list = file_list_14_40d_cl
                name_list = name_list_14_40d_cl
            else:
                file_list = file_list_14_40d_rj
                name_list = name_list_14_40d_rj
        elif "AS14-128H" in output:
            if self.cl_image_flag:
                file_list = file_list_14_128h_cl
                name_list = name_list_14_128h_cl
            else:
                file_list = file_list_14_128h_rj
                name_list = name_list_14_128h_rj
        elif "AS24-128D-2" in output:
            if self.cl_image_flag:
                file_list = file_list_24_128d_2_cl
                name_list = name_list_24_128d_2_cl
            else:
                file_list = file_list_24_128d_2_rj
                name_list = name_list_24_128d_2_rj
        elif "AS24-128D" in output:
            if self.cl_image_flag:
                file_list = file_list_24_128d_cl
                name_list = name_list_24_128d_cl
            else:
                file_list = file_list_24_128d_rj
                name_list = name_list_24_128d_rj
        elif "AS61-48X4T" in output:
            if self.cl_image_flag:
                file_list = file_list_61_48x4t_cl
                name_list = name_list_61_48x4t_cl
            else:
                file_list = file_list_61_48x4t_rj
                name_list = name_list_61_48x4t_rj
        elif "AS61-48E4T" in output:
            if self.cl_image_flag:
                file_list = file_list_61_48e4t_cl
                name_list = name_list_61_48e4t_cl
            else:
                file_list = file_list_61_48e4t_rj
                name_list = name_list_61_48e4t_rj
        elif "AC51-48C2G" in output:
            if self.cl_image_flag:
                file_list = file_list_51_48c2g_cl
                name_list = name_list_51_48c2g_cl
            else:
                file_list = file_list_51_48c2g_rj
                name_list = name_list_51_48c2g_rj
        elif "AS14-24D8Q" in output:
            if self.cl_image_flag:
                file_list = file_list_14_24d8q_cl
                name_list = name_list_14_24d8q_cl
            else:
                file_list = file_list_14_24d8q_rj
                name_list = name_list_14_24d8q_rj
        elif "AS25-128Q" in output:
            if self.cl_image_flag:
                file_list = file_list_25_128q_cl
                name_list = name_list_25_128q_cl
            else:
                file_list = file_list_25_128q_rj
                name_list = name_list_25_128q_rj
        elif "AS51-24D" in output:
            if self.cl_image_flag:
                file_list = file_list_51_24d_cl
                name_list = name_list_51_24d_cl
            else:
                file_list = file_list_51_24d_rj
                name_list = name_list_51_24d_rj
        elif "AS15-40Q" in output:
            if self.cl_image_flag:
                file_list = file_list_15_40q_cl
                name_list = name_list_15_40q_cl
            else:
                file_list = file_list_15_40q_rj
                name_list = name_list_15_40q_rj
        else:
            if self.cl_image_flag:
                file_list = file_list_ph_cl
                name_list = name_list_ph_cl
            else:
                file_list = file_list_ph_rj
                name_list = name_list_ph_rj
        if unittest_config.CPLD_NAME_LIST:
            name_list = unittest_config.CPLD_NAME_LIST
            file_list = unittest_config.CPLD_IMAGE_LIST
        ret = self.fw.program_cpld(name_list, file_list)
        self.assertEqual(ret, 0)
        ret = self.fw.program_cpld(["cpld"], ["/tmp/test"])
        self.assertEqual(ret, -1)

    def test_refresh_firmware(self):
        ret = self.fw.refresh_firmware("cpld", "/tmp/testerr")
        self.assertEqual(ret, -1)
        if unittest_config.determine_whether_test_is_required("is_support_bios") == True:
            ret = self.fw.refresh_firmware(["bios"], ["none", "none"])
            self.assertEqual(ret, -1)
            #refreshing bios by cold rebooting the cpu
            ret = self.misc.set_host_cpu_power("cycle")
            self.assertEqual(ret, 0)
            #wait cpu up -- after upgrading BIOS, this action takes longer
            unittest_config.wait_cpu_ready(120)
        else:
            pass

    def tearDown(self):
        pass
