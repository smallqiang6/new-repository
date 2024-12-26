#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

"""
class for Platfrom HAL for implement Firmware APIs.
"""
import subprocess
import syslog
import sys
import os
from product_hal.ruijieconfig import *
from .devicebase import devicebase

class misc(devicebase):

    def __init__(self):
        pass

    def get_bmc_boot_status(self):
        """
        Get BMC latest boot status

        @return "master"/"slave" for boot successfully from master/slave flash
                "N/A" for read failed
        """
        cmd = "bmc.sh view_flash bmc"
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return "N/A"
        if "master" in output :
            return "master"
        elif "slave" in output :
            return "slave"
        else:
            self.logger_debug(log_str)
            return "N/A"

    def set_host_cpu_power(self, power_command):
        """
        Control host cpu power

        @param power_command Control command of host CPU's power,
                             should be "cpu on"/"cpu off"/"cpu cycle"/"cpu reset"

        @return 0 for success, -1 for failure
        """
        if power_command != "on" and power_command != "off" and power_command != "cycle" and power_command != "reset" :
            self.logger_debug("error command %s"%(power_command))
            return -1
        cmd = "echo y | plat_power cpu %s"%(power_command)
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return -1
        else:
            return 0

    def get_host_cpu_power_status(self):
        """
        Get host cpu power status

        @return Power status of CPU(and affiliates), value should be
                "on"/"off", or "N/A" for failure
        """
        cmd = "plat_power cpu status"
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return "N/A"
        else:
            if "ON" in output :
                return "on"
            elif "OFF" in output :
                return "off"
            else:
                return "N/A"

    def set_location_led(self, command):
        """
        Set location LED admin status

        @param cmd Control command, "on"/"off"

        @return 0 for success, -1 for failure
        """
        if command != "on" and command != "off":
            self.logger_debug("error command %s"%(command))
            return -1
        cmd = "plat_led_location %s"%(command)
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return -1
        else:
            return 0

    def get_location_led(self):
        """
        Get location LED admin status

        @return status of location LED, "on"/"off" or "N/A" for failure
        """
        cmd = "plat_led_location status"
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return "N/A"
        else:
            if "OFF" in output :
                return "off"
            elif "ON" in output :
                return "on"
            else:
                return "N/A"

    def get_system_airflow(self):
        """
        Get system air flow.

        @return "F2B"/"B2F" on success, "N/A" for failure
        """
        ## 32/48/128 -F-RJ --- FTOB   -R-RJ --- BTOF
        ## 32 FAN5_airflow 
        ##systemctl list-unit-files |grep device-config.service
        ##device-config.service                  enabled

        sys_airflow_path = "/etc/device/fullproductname"
        if not os.path.exists(sys_airflow_path):
            self.logger_debug("no exist file: %s"%(sys_airflow_path))
            print("maybe something wrong with device-config.service or it did not end yet, please wait a moment and try again...")
            return "N/A"
        cmd = "cat %s"%(sys_airflow_path)
        output, ret = platcomutil.run_shell_cmd(cmd)
        log_str = cmd + " :result: " + output
        if ret != 0 :
            self.logger_debug(log_str)
            return "N/A"
        else:
            RUIJIE_PRODUCTNAME = module_product.RUIJIE_PRODUCTNAME
            if "-L-RJ" in output or "-LC-RJ" in output or "-LD-RJ" in output:
                return "LIQUID"
            elif "-F-RJ" in output :
                return "F2B"
            elif "-R-RJ" in output :
                return "B2F"
            #Compatible with 128 devices
            elif RUIJIE_PRODUCTNAME.lower() in output.lower() :
                return "F2B"
            else:
                self.logger_debug("system airflow: NA,productname: %s,output: %s"%(RUIJIE_PRODUCTNAME, output))
                return "N/A"
