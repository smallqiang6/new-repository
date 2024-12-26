###############################################################################
#
# Hardware Abstraction Layer APIs -- MISC APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################

"""
class for HAL Misc APIs.
"""
import subprocess
import os
import sys
import re

from plat_utils.plat_common_util import *
from plat_hal.misc import misc
from plat_hal.interface import interface
from plat_hal.rj_rawcmd import RjRawCmd

class HalMisc(object):
    __int_case = None

    def __init__(self):
        self.misc = misc()
        self.int_case = interface()
        self.cmd = RjRawCmd()

    @property
    def int_case(self):
        return self.__int_case

    @int_case.setter
    def int_case(self, val):
        self.__int_case = val

    def get_bios_boot_status(self):
        """
        Get lastest BIOS boot status, include boot_flash and result

        @return Dict of BIOS boot status or None for failure
                Example:
                {
                    "Flash": "master",      # "slave" or 'N/A'
                    "Result": "success"     # "failed" or 'N/A'
                }
        """
        return self.int_case.get_bios_status()

    def get_uboot_boot_status(self):
        """
        Get lastest U-Boot boot status, include boot_flash and result 
        @return Dict of U-Boot boot status or None for failure
            Example:
            {
                "Flash": "master",      # "slave" or 'N/A'
                "Result": "success"     # "failed" or 'N/A'
            }
        """
        return self.int_case.get_uboot_status()

    def get_bmc_boot_status(self):
        """
        Get BMC latest boot status

        @return "master"/"slave" for boot successfully from master/slave flash
                "N/A" for read failed
        """
        return self.misc.get_bmc_boot_status()

    def set_system_fan_led(self, color, blink=False):
        """
        Set system fan LED color

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_misc_system_fan_led(color, blink)

    def set_system_led(self, color, blink=False):
        """
        Set system LED color, system LED indicates status of the whole system

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_misc_system_led(color, blink)

    def system_power_led_available(self):
        """
        Get system power LED availability

        @return True if available, False otherwise.
        """
        return self.int_case.get_misc_system_power_led_available()

    def set_system_power_led(self, color, blink=False):
        """
        Set system power LED color, power LED indicates PSU, DC/DC status

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_misc_system_power_led(color, blink)

    def set_host_cpu_power(self, power_command):
        """
        Control host cpu power

        @param power_command Control command of host CPU's power,
                             should be "on"/"off"/"cycle"/"reset"

        @return 0 for success, -1 for failure
        """
        return self.misc.set_host_cpu_power(power_command)

    def get_host_cpu_power_status(self):
        """
        Get host cpu power status

        @return Power status of CPU(and affiliates), value should be
                "on"/"off", or "N/A" for failure
        """
        return self.misc.get_host_cpu_power_status()

    def set_location_led(self, cmd):
        """
        Set location LED admin status

        @param cmd Control command, "on"/"off"

        @return 0 for success, -1 for failure
        """
        return self.misc.set_location_led(cmd)

    def get_location_led(self):
        """
        Get location LED admin status

        @return status of location LED, "on"/"off" or "N/A" for failure
        """
        return self.misc.get_location_led()

    def get_system_airflow(self):
        """
        Get system air flow.

        @return "F2B"/"B2F" on success, "N/A" for failure
        """
        return self.misc.get_system_airflow()

    def get_cpld_user_reg(self):
        """
        Get user register value, 1 byte value

        @return unsigned value, 1 byte, None for failure
        """
        return self.int_case.get_cpld_user_reg()

    def set_cpld_user_reg(self, value):
        """
        Set user register value, 1 byte

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_cpld_user_reg(value)

    def set_console_owner(self, owner):
        """
        Set console I/O owner

        @param owner I/O owner of the console, either "cpu" or "bmc"

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_cpld_console_owner(owner)

    def get_cpld_version(self):
        """
        Get version of CPLDs' that can be read from BMC

        @return dict of CPLDs' version or None for failure.
                example outputs:
                {
                    "BASE_CPLD": "0.1",     # or "N/A" for read failure
                    "FAN_CPLD": "0.2"
                }
        """
        return self.int_case.get_cpld_all_version()

    def get_platform_name(self):
        """
        Get platform name

        @return platform name string, e.g. AS13-32H-F-$(VENDOR_NAME)
        """
        return self.int_case.get_bmc_productname()

    def get_sys_eeprom(self):
        """
        Get SYSEEPROM
        @return SYSEEPROM content dict or None for failure.
                example outputs:
                {
                    "Product Name": "AS23-128H",
                    "Product Manufacturer": "Manufacturer Name",
                    "Product Serial": "ABC0123456789",
                    "Product Part Number": "P10-F0001-01"
                    # Optional keys
                }
        @note value string should be "N/A" on read failure.
        """
        return self.int_case.get_bmc_sys_eeprom()

    def execute_command(self, cmd_str):
        """
        Excute user specified command string.

        @param cmd_str command string from user

        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        str = "rj_rawcmd_cli"
        if str in cmd_str:
            return self.cmd.param_manage(cmd_str)
        return self.int_case.bmc_execute_command(cmd_str)

    def enable_host_cpu_power_force_control(self, enable):
        """
        Force control host cpu power
        @param enable: enable/disable force control host cpu power,
                       enable: 1; disable: 0
        @return 0 for success, -1 for failure

        """
        return self.int_case.enable_host_cpu_power_force_control(enable)

    def get_host_cpu_power_force_control_status(self):
        """
        Get force control host cpu power status
        @return 1 for enable, 0 for disable, -1 for failure
        """
        return self.int_case.get_host_cpu_power_force_control_status()

    def set_switch_port_power_status(self, status):
        """
        Control switch port power
        @param status: Control switch port power,
                        should be "on"/"off"
        @return 0 for success, -1 for failure
        """
        if self.int_case.enable_host_cpu_power_force_control(1) == 0:
            return self.int_case.set_port_power(status)
        else:
            return -1

    def get_switch_port_power_status(self):
        """
        Get switch port power status
        @return switch port power status, value should be
                        "on"/"off", or "N/A" for failure
        """
        return self.int_case.get_port_power_status()

    def set_switch_chip_power_status(self, status):
        """
        Control switch chip power
        @param status: Control switch chip power,
                            should be "on"/"off"
        @return 0 for success, -1 for failure
        """
        if self.int_case.enable_host_cpu_power_force_control(1) == 0:
            return self.int_case.set_td4_power(status)
        else:
            return -1

    def get_switch_chip_power_status(self):
        """
        Get switch chip status
        @return switch chip power status, value should be
                            "on"/"off", or "N/A" for failure
        """
        return self.int_case.get_td4_power_status()

    def set_ssd_power_status(self, status):
        """
        Control SSD power
        @param status: Control SSD power,
                        should be "on"/"off"
        @return 0 for success, -1 for failure
        """
        if self.int_case.enable_host_cpu_power_force_control(1) == 0:
            return self.int_case.set_ssd_power(status)
        else:
            return -1

    def get_ssd_power_status(self):
        """
        Get SSD status
        @return SSD power status, value should be
                        "on"/"off", or "N/A" for failure
        """
        return self.int_case.get_ssd_power_status()
