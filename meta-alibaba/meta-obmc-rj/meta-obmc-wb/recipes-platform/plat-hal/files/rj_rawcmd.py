#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

from plat_hal.interface import *
from product_hal.ruijieconfig import *
from plat_hal.devicebase import devicebase
import syslog
import json
import re
import os
import traceback

diag_bmc_path   =  "/usr/local/bin/"
sys.path.append(diag_bmc_path)
global diag_bmc
if os.path.exists(diag_bmc_path + "diag_bmc.py"):
    diag_bmc  = __import__("diag_bmc", globals(), locals(), [])

MAX_FEEDED_WDT_TIME = 65535
WAT_INFO_FILE = "/tmp/watchdog_info"
EXIT_SUCCESS = 0
EXIT_FAILED = -1

class RjRawCmd(devicebase):

    def __init__(self):
        self.int_case = interface()

    def get_wdt_info(self):
        ret = EXIT_FAILED
        if os.path.exists(WAT_INFO_FILE):
            if not os.path.getsize(WAT_INFO_FILE):
                result = "ERR:unknown host watchdog info"
                return ret, result
        wat_info = platcomutil.JSONparserFile(WAT_INFO_FILE)
        if wat_info == None:
            result = "ERR:get host watchdog info failed"
        else:
            result = wat_info
            ret = EXIT_SUCCESS
        return ret, result

    def wdt_action(self, value):
        result = None
        ret = EXIT_FAILED
        if value.isdigit() == False:
            result = "ERR:parameter non-numeric"
        elif int(value) < 0 or int(value) > MAX_FEEDED_WDT_TIME:
            result = "ERR:parameter illegal, range(0-65535)"
        if result != None:
            return ret, result
        ret = self.int_case.monitor_cpu_host_watchdog(value)
        if ret:
            result = "ERR:set watchdog failed"
        else:
            ret = EXIT_SUCCESS
            result = "OK:ok"
        return ret, result

    def get_bios_version(self):
        ret = EXIT_FAILED
        result = None
        info = {
            "CurrentFlashState": "N/A",
            "MasterBiosVersion": "N/A",
            "SlaveBiosVersion": "N/A",
        }
        output = self.int_case.get_bios_status()
        if output == None or output == -1 or output["Flash"] == "N/A":
            result = "ERR:get bios current flash failed"
        if result != None:
            return ret, result
        info["CurrentFlashState"] = output["Flash"]

        output = self.int_case.get_bios_version()
        if output == None or output == -1:
            result = "ERR:get bios version failed"
        elif output["MasterBiosVersion"] == "N/A":
            result = "ERR:get MasterBiosVersion failed"
        elif output["SlaveBiosVersion"] == "N/A":
            result = "ERR:get SlaveBiosVersion failed"
        if result != None:
            return ret, result
        else:
            info["MasterBiosVersion"] = output["MasterBiosVersion"]
            info["SlaveBiosVersion"] = output["SlaveBiosVersion"]
        result = info
        ret = EXIT_SUCCESS
        return ret, result

    def set_bios_version(self, flash, version):
        ret = EXIT_FAILED
        if version == None:
            result = "ERR:parameter biosVersion does NULL"
            return ret, result
        ret = self.int_case.write_bios_version(flash, version)
        if ret:
            result = "ERR:set bios version failed"
        else:
            result = "OK:ok"
            ret = EXIT_SUCCESS
        return ret, result

    def get_mac_rov(self):
        ret, output = self.int_case.get_bmc_mac_rov()
        if ret == -1:
            self.logger_debug("get mac rov failed, result:%s" % (output))
        return ret, output

    def producttest_action(self, data):
        ret = EXIT_FAILED
        if data == None:
            result = "ERR:parameter does None"
            return ret, result

        self.logger_debug("call bmc data:%s" % (data))
        if data == "bmc_set_lock" or data == "bmc_set_unlock":
            ret, output = self.int_case.call_bmc_diagcmd(data)
        else:
            try:
                cmdstr = "-o %s"%data
                output = [diag_bmc.CMD_dispatch(cmdstr)]
                if output != None:
                    ret = 0
            except Exception:
                ret = -1
                output = "call diag_bmc.CMD_dispatch failed"
                stack_log = traceback.format_exc()
                self.logger_debug(stack_log)
        self.logger_debug("call bmc diag cmd, result:%s" % (output))
        return ret, output

    def get_bmc_reset_num(self):
        return 0, self.int_case.get_bmc_reset_num()

    def get_cpu_reset_num(self):
        return 0, self.int_case.get_cpu_reset_num()

    def get_td4_power_status(self):
        return 0, self.int_case.get_td4_power_status()

    def set_td4_power(self,status):
        ret = EXIT_FAILED
        if status == None:
            output = "ERR:parameter td4 power status does NULL"
            self.logger_debug("set td4 power status failed, result:%s" % (output))
            return 0, ret
        return 0, self.int_case.set_td4_power(status)

    def get_port_power_status(self):
        return 0, self.int_case.get_port_power_status()

    def set_port_power(self,status):
        ret = EXIT_FAILED
        if status == None:
            output = "ERR:parameter port power status does NULL"
            self.logger_debug("set power status failed, result:%s" % (output))
            return 0, ret
        return 0, self.int_case.set_port_power(status)

    def set_machine_power_cycle(self):
        return 0, self.int_case.set_machine_power_cycle()

    def get_uboot_version(self):
        ret = EXIT_FAILED
        result = None
        info = {
            "CurrentFlashState": "N/A",
            "MasterUbootVersion": "N/A",
            "SlaveUbootVersion": "N/A",
        }
        output = self.int_case.get_uboot_status()
        if output == None or output == -1 or output["Flash"] == "N/A":
            result = "ERR:get uboot current flash failed"
        if result != None:
            return ret, result
        info["CurrentFlashState"] = output["Flash"]

        output = self.int_case.get_uboot_version()
        if output == None or output == -1:
            result = "ERR:get uboot version failed"
        elif output["MasterUbootVersion"] == "N/A":
            result = "ERR:get MasterUbootVersion failed"
        elif output["SlaveUbootVersion"] == "N/A":
            result = "ERR:get SlaveUbootVersion failed"
        if result != None:
            return ret, result
        else:
            info["MasterUbootVersion"] = output["MasterUbootVersion"]
            info["SlaveUbootVersion"] = output["SlaveUbootVersion"]
        result = info
        ret = EXIT_SUCCESS
        return ret, result

    def set_uboot_version(self, flash, version):
        ret = EXIT_FAILED
        if version == None:
            result = "ERR:parameter UbootVersion does NULL"
            return ret, result
        ret = self.int_case.write_uboot_version(flash, version)
        if ret:
            result = "ERR:set uboot version failed"
        else:
            result = "OK:ok"
            ret = EXIT_SUCCESS
        return ret, result

    def param_manage(self, cmd):
        # eg. cmd = "/usr/local/bin/rj_rawcmd_cli get watchdog"
        # cmd_list[0] = /usr/local/bin/rj_rawcmd_cli"
        # distinguish whether upper call cli, which no real effect
        # cmd contains multiple spaces does not supported
        output = None
        ret = EXIT_FAILED
        cmd_list = cmd.split(" ")
        if len(cmd_list) < 3:
            output = "ERR: parameter does wrong cmd=%s" % cmd
            self.logger_debug(output)
            return ret, output
        rj_option = cmd_list[1]
        rj_object = cmd_list[2]
        if len(cmd_list) > 3:
            rj_value = " ".join(cmd_list[3:])

        if rj_option == "get":
            if rj_object == "watchdog":
                ret, output = self.get_wdt_info()
            elif rj_object == "bios_version":
                ret, output = self.get_bios_version()
            elif rj_object == "mac_rov":
                ret, output = self.get_mac_rov()
                self.int_case.reset_bmc_devices()
            elif rj_object == "5387_version":
                ret, output = self.int_case.get_fw_5387_version()
            elif rj_object == "fpga_md5sum":
                ret, output = self.int_case.get_fpga_md5sum()
            elif rj_object == "bmc_reset_num":
                ret, output = self.get_bmc_reset_num()
            elif rj_object == "cpu_reset_num":
                ret, output = self.get_cpu_reset_num()
            elif rj_object == "td4_power_status":
                ret, output = self.get_td4_power_status()
            elif rj_object == "port_power_status":
                ret, output = self.get_port_power_status()
            elif rj_object == "last_upgrade_result":
                ret, output = self.int_case.get_cpld_last_upgrade_result()
            elif rj_object == "mac_md5sum":
                ret, output = self.int_case.get_mac_md5sum()
            elif rj_object == "atlas0_md5sum":
                ret, output = self.int_case.get_atlas0_md5sum()
            elif rj_object == "atlas1_md5sum":
                ret, output = self.int_case.get_atlas1_md5sum()
            elif rj_object == "8367_version":
                ret, output = self.int_case.get_fw_8367_version()
            elif rj_object == "uboot_version":
                ret, output = self.get_uboot_version()
            elif rj_object == "88e6321_version":
                ret, output = self.int_case.get_fw_88e6321_version()
            elif rj_object == "bcm53134_version":
                ret, output = self.int_case.get_fw_bcm53134_version()
            elif rj_object == "rtl8372_md5sum":
                ret, output = self.int_case.get_rtl8372_md5sum()
            elif rj_object == "device_cfg":
                ret, output = self.int_case.get_device_cfg()
            else:
                output = "ERR:get-object parameter illegal, cmd=%s" % cmd
                self.logger_debug(output)
        elif rj_option == "set":
            if rj_object == "watchdog":
                ret, output = self.wdt_action(rj_value)
            elif rj_object == "m_bios_version":
                ret, output = self.set_bios_version("master", rj_value)
            elif rj_object == "s_bios_version":
                ret, output = self.set_bios_version("slave", rj_value)
            elif rj_object == "td4_power" :
                ret, output = self.set_td4_power(rj_value)
            elif rj_object == "port_power":
                ret, output = self.set_port_power(rj_value)
            elif rj_object == "machine_power_cycle":
                ret, output = self.set_machine_power_cycle()
            elif rj_object == "m_uboot_version":
                ret, output = self.set_uboot_version("master", rj_value)
            elif rj_object == "s_uboot_version":
                ret, output = self.set_uboot_version("slave", rj_value)
            else:
                output = "ERR:set-object parameter illegal, cmd=%s" % cmd
                self.logger_debug(output)
        elif rj_option == "diag":
            if rj_object == "cmd":
                ret, output = self.producttest_action(rj_value)
        elif rj_option == "upgrade_5387":
            ret, output = self.int_case.upgrade_5387_fw(rj_object)
        elif rj_option == "upgrade_fpga":
            ret, output = self.int_case.upgrade_fpga_fw(rj_object)
        elif rj_option == "upgrade_8367":
            ret, output = self.int_case.upgrade_8367_fw(rj_object)
        elif rj_option == "upgrade_88e6321":
            ret, output = self.int_case.upgrade_88e6321_fw(rj_object)
        elif rj_option == "upgrade_bcm53134":
            ret, output = self.int_case.upgrade_bcm53134_fw(rj_object)
        elif rj_option == "upgrade_rtl8372":
            ret, output = self.int_case.upgrade_rtl8372_fw(rj_object)
        elif rj_option == "upgrade_mac":
            ret, output = self.int_case.upgrade_mac_fw(rj_object)
        elif rj_option == "upgrade_atlas0":
            ret, output = self.int_case.upgrade_atlas0_fw(rj_object)
        elif rj_option == "upgrade_atlas1":
            ret, output = self.int_case.upgrade_atlas1_fw(rj_object)
        else:
            output = "ERR:option parameter illegal, cmd=%s" % cmd
            self.logger_debug(output)
        return ret, output
