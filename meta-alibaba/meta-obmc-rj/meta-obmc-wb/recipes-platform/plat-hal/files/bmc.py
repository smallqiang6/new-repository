#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

"""
class for Platfrom HAL for implement Hal_bmc APIs.
"""
import subprocess
import os
import sys
import re
import time
from product_hal.ruijieconfig import *
from .devicebase import devicebase
import collections
from eepromutil.fru import *

RESET_NUM_PATH = "/tmp/reset_count"
AST_FUNC_SOURCE = "/usr/local/bin/ast-functions"
REPLACE_RESET_NUM = "replace_reset_num"

class bmc(devicebase):

    def __init__(self, conf = None):
        self.diag_lock_file = "/tmp/diaglockfile"
        if conf is not None:
            self.name = conf.get('name', None)
            self.product_name_path = conf.get('ProductName', None)
            self.product_fullname_path = conf.get('ProductFullName', None)
            self.switch_bmc_flag = conf.get('SwitchBmcFlag', None)
            self.bmc_watchdog = conf.get('watchdog', None)
            self.version_file = conf.get('FwVersion', None)
            self.current_flash_flag = conf.get('CurrentFlashFlag', None)
            self.sys_led_reg = conf.get('SysLedReg', None)
            self.pwr_led_reg = conf.get('PwrLedReg', None)
            self.sys_led_attrs = conf.get('SysLedAttrs', None)
            self.pwr_led_attrs = conf.get('PwrLedAttrs', None)
            self.sys_fan_led_reg = conf.get('SysFanLedReg', None)
            self.sys_fan_led_attrs = conf.get('SysFanLedAttrs', None)
            self.bmc_reset_cnt_reg = conf.get('BmcResetCntReg', None)
            self.sys_eeprom_path = conf.get('SysEeprom', None)
            self.reset_dev_list = conf.get('ResetDevList', None)

    def __diag_lock_file(self):
        if (os.path.exists(self.diag_lock_file) == True):
            self.logger_debug("bmc diag lock, but /tmp/diaglockfile has exist")
            return -1
        else:
            fp = open(self.diag_lock_file,'w')
            fp.close()
            return 0

    def __diag_unlock_file(self):
        if (os.path.exists(self.diag_lock_file) == False):
            self.logger_debug("/tmp/diaglockfile has not exist")
        else:
            os.remove(self.diag_lock_file)
        return 0

    def __import_fru_eeprom_config(self):
        output = None
        if self.sys_eeprom_path == None:
            self.logger_debug("Get sys eeprom path failed")
            return output
        eeprom_tmp = self.get_eeprom_info(self.sys_eeprom_path)
        if eeprom_tmp == None:
            self.logger_debug("Get sys eeprom info failed")
            return output
        fru_dev = ipmifru()
        fru_dev.decodeBin(eeprom_tmp)
        if fru_dev.productInfoArea != None:
            dict_tmp = fru_dev.productInfoArea.todict()
            if dict_tmp != None:
                output = dict_tmp
        return output

    def get_info(self):
        """
        Get BMC info

        @return dict of BMC info or None for failure
                    "Version": "1.1.1", # "N/A"
                    "Flash": "master",  # "N/A"
                    "Next": "master"    # "N/A"
        """
        dict_bmc_info = {"Version":"N/A",
                         "Flash":"N/A",
                         "Next":"N/A",
                        }
        ret, current_flash_flag = self.get_value(self.current_flash_flag)
        if ret == False:
            self.logger_debug("get bmc current flash failed")
        else:
            flash_version = self.get_version_all()
            if int(current_flash_flag) == 0 :
                dict_bmc_info["Flash"] = "master"
                dict_bmc_info["Version"] = flash_version["MasterVersion"]
            else:
                dict_bmc_info["Flash"] = "slave"
                dict_bmc_info["Version"] = flash_version["SlaveVersion"]
        dict_bmc_info["Next"] = self.get_next_boot()
        return dict_bmc_info

    def get_version_all(self):
        """
        @return dict of BMCs
                {
                    "MasterVersion": "1.1.1",   # "N/A"
                    "SlaveVersion": "1.1.1"     # "N/A"
                }
        """
        """
        master-bmc-fw : v2.2-1183-gb88065bc2-dirty
        slave-bmc-fw :
        slave-bios-fw :5.11(3BARB0015)
        master-bios-fw :5.11(3BARB0016)
        """
        dict_version = {
                        "MasterVersion": "N/A",
                        "SlaveVersion": "N/A",
                       }
        if not os.path.exists(self.version_file):
            self.logger_debug("%s does not exist" %(self.version_file))
            return dict_version
        dict_ver = platcomutil.JSONparserFile(self.version_file)
        if dict_ver == None:
            self.logger_debug("get bmc version failed")
            return dict_version
        else:
            if "master-bmc-fw" in dict_ver:
                dict_version["MasterVersion"] = dict_ver["master-bmc-fw"]
            if "slave-bmc-fw" in dict_ver :
                dict_version["SlaveVersion"] = dict_ver["slave-bmc-fw"]
        return dict_version

    def get_status(self):
        """
        Get BMC system status

        @return dict of system status or None for failure
                # "N/A" for invalid outputs
                {
                    "CPU": {
                        "StateOutputs": "output of command 'top -bn 1'"
                        "Usage": "10.0"
                    },
                    "MEMORY": {
                        "StateOutputs": "output of command 'free -m'"
                        "Usage": "15.0"   # caculate: "free -t | grep \"buffers/cache\" | awk '{ printf \"mem usage  : %.1f%%\\n\",$3/($3+$4) * 100}'"
                    },
                    "DISK": {
                        "StateOutputs": "output of command 'df -h'"
                        "Usage": "12.5"
                    }
                }
        """
        dict_sys_status ={
                          "CPU": {
                                  "StateOutputs": "N/A",
                                   "Usage": "N/A",
                                 },
                         "MEMORY": {
                                    "StateOutputs": "N/A",
                                    "Usage": "N/A",
                                   },
                         "DISK": {
                                   "StateOutputs": "N/A",
                                   "Usage": "N/A",
                                 },
                          }
        try:
            cmd = "top -bn 1"
            output,ret = platcomutil.run_shell_cmd(cmd)
            if ret != 0:
                self.logger_debug("%s bmc cpu result error:%s"%(cmd,output))
            else:
                dict_sys_status["CPU"]["StateOutputs"] = output
                value , times = re.subn(r"[\S\s]*nic\s+(\d+)%\sidle[\S\s]*",r"\g<1>", output)
                if times != 1:
                    self.logger_debug("%s bmc cpu result error:%s"%(value,output))
                else:
                    usage = 100 - int(value)
                    dict_sys_status["CPU"]["Usage"] = "%s"%(str(usage))

            cmd = "free -tm"
            output,ret = platcomutil.run_shell_cmd(cmd)
            if ret != 0:
                self.logger_debug("%s bmc memory result error:%s"%(cmd,output))
            else:
                dict_sys_status["MEMORY"]["StateOutputs"] = output
                cmd = "free -tm | grep \"buffers/cache\" | awk '{ printf \"%.1f\",$3/($3+$4) * 100}'"
                output,ret = platcomutil.run_shell_cmd(cmd)
                self.logger_debug("%s bmc memory result:%s"%(cmd,output))
                if ret != 0:
                    self.logger_debug("%s bmc memory result error:%s"%(cmd,output))
                else:
                    dict_sys_status["MEMORY"]["Usage"] = output

            cmd = "df -h"
            output,ret = platcomutil.run_shell_cmd(cmd)
            if ret != 0:
                self.logger_debug("%s bmc disk result error:%s"%(cmd,output))
            else:
                dict_sys_status["DISK"]["StateOutputs"] = output
                cmd = "df | grep mmc | awk '{print $2\"\t\"$3}'"
                output,ret = platcomutil.run_shell_cmd(cmd)
                result_str = output.split()
                result_len = len(result_str)
                if result_len == 0 or result_len % 2 != 0:
                    self.logger_debug("%s bmc cpu result error:%s"%(cmd,output))
                else:
                    result_int = list(map(int, result_str))
                    size = 0
                    used = 0
                    for part in range(int(result_len/2)):
                        size = size + result_int[2*part]
                        used = used + result_int[2*part + 1]
                    dict_sys_status["DISK"]["Usage"] = "%s"%(str("%.1f" % (used/size * 100)))
        except:
            self.logger_debug("error occurred while getting bmc status")

        return dict_sys_status

    def get_next_boot(self):
        """
        Get next booting flash of BMC

        @return 'master'/'slave' on success, "N/A" for failure
        """
        ret_boot = "N/A"
        cmd = "switch_bmc.sh get-next-boot"
        ret, output = self.command(cmd)
        if ret != 0 or (output.strip('\n') != "master" and output.strip('\n') != "slave"):
            self.logger_debug("get bmc next boot failed: %s" % output)
        else:
            ret_boot = output.strip('\n')
        return ret_boot

    def set_next_boot(self, nextbootflash):
        """
        Set flash from which next BMC boot

        @param flash Booting flash of BMC, "master" or "slave"

        @return 0 on success, -1 for failure
        """
        ret_boot = -1
        cmd = "switch_bmc.sh " + nextbootflash
        ret, output = self.command(cmd)
        if ret:
            self.logger_debug("set bmc %s flash next boot failed: %s" %(nextbootflash, output))
        else:
            ret_boot = 0
        return ret_boot

    def reboot(self):
        """
        Reboot running BMC
        """
        ret_reboot = -1
        if self.switch_bmc_flag is None:
            self.logger_debug("get bmc next boot failed")
            return ret_reboot
        if os.path.exists(self.switch_bmc_flag):
            ret, output = self.command(self.bmc_watchdog)
            if ret:
                self.logger_debug("%s bmc result error:%s"%(self.bmc_watchdog,output))
            else:
                ret_reboot = 0
        else:
            ret, output = self.command("reboot")
            if ret:
                self.logger_debug("reboot bmc failed")
            else:
                ret_reboot = 0
        return ret_reboot

    def call_diagcmd(self, cmdstr):
        ret = 0
        output = ""
        if (cmdstr == "bmc_set_lock"):
            tmpret = self.__diag_lock_file()
            if (tmpret == 0) :
                output = "True"
            else:
                output = "False"
        elif (cmdstr == "bmc_set_unlock"):
            tmpret = self.__diag_unlock_file()
            if (tmpret == 0) :
                output = "True"
            else:
                output = "False"
        else:
            # the former function subprocess.getstatusoutput() which running by self.command("diag_bmc -o %s"%cmdstr),
            # would waiting for sub-fork returned;os.popen do not.
            ret_fd = os.popen("diag_bmc -o %s"%cmdstr)
            if ret_fd != None:
                ret = 0
                output = ret_fd.readlines()
            else:
                ret = -1
                output = "error"
        return ret, output

    def run_script(self, script_path):
        return_code = os.system(f'python {script_path} start')
        return_code = return_code >> 8
        return return_code

    def get_mac_rov(self):
        ret = self.run_script('/usr/local/bin/avscontrol.py')
        if ret == 0:
            return 0, ret
        else:
            return 0, "-1"

    def get_productname(self):
        retval = "N/A"
        ret, output = self.command("cat %s"%self.product_fullname_path)
        if (ret == 0):
            # To distinguish the manufacturer did not find RJ, forced add RJ
            if (re.match(".*-RJ$", output) == None):
                output = output +"-RJ"
            retval = output
        return retval

    def set_system_led(self, color, blink):
        """
        Set system LED color, system LED indicates status of the whole system
        The 40D device does not support setting red light, set the red light to go out

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        sys_led_status = ["green", "yellow", "red", "off"]
        if color not in sys_led_status:
            self.logger_debug("input system LED color(%s) illegal, should be red|green|yellow|off" %(color))
            return -1
        if blink:
            led_attr = "blink"
        else:
            led_attr = "steady"
        ret, val = self.set_value(self.sys_led_reg, self.sys_led_attrs[color][led_attr])
        if ret == False:
            self.logger_debug("set system LED color(%s) failed" %(color))
            return -1
        return 0

    def get_system_power_led_available(self):
        """
        Get system power LED availability

        @return True if available, False otherwise.
        """
        ret, val = self.get_value(self.pwr_led_reg)
        if ret == False:
            self.logger_debug("get system power LED result: disabled")
            return False
        return True

    def set_system_power_led(self, color, blink):
        """
        Set system power LED color, power LED indicates PSU, DC/DC status
        The 40D device does not support setting red light, set the red light to go out

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        pwr_led_status = ["green", "yellow", "red", "off"]
        if color not in pwr_led_status:
            self.logger_debug("input power LED color(%s) illegal, should be red|green|yellow|off" %(color))
            return -1
        if blink:
            led_attr = "blink"
        else:
            led_attr = "steady"
        ret, val = self.set_value(self.pwr_led_reg, self.pwr_led_attrs[color][led_attr])
        if ret == False:
            self.logger_debug("set power LED color(%s) failed" %(color))
            return -1
        return 0

    def set_system_fan_led(self, color, blink=False):
        """
        Set system fan LED color
        The 40D device does not support setting red light, set the red light to go out??

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        sys_fan_led_status = ["green", "yellow", "off"]
        if color not in sys_fan_led_status:
            self.logger_debug("input sys fan LED color(%s) illegal, should be green|yellow|off" %(color))
            return -1
        if blink:
            led_attr = "blink"
        else:
            led_attr = "steady"
        ret, val = self.set_value(self.sys_fan_led_reg, self.sys_fan_led_attrs[color][led_attr])
        if ret == False:
            self.logger_debug("set sys fan LED color(%s) failed" %(color))
            return -1
        return 0

    def get_bmc_reset_num_reg(self):
        """
        get bmc reset num from register, register is cleared after it has been read
        distinguish by "read_clean" = 1, default 0
        1.only one read_clean register
        2.diff regs for reset/cycle, distinguish by "diff_reg" = 1, default 0
        3.reset/cycle use the same regs
        @return bmc reset number from the register
        """
        count = 0
        output = "N/A"
        try:
            if os.path.exists(RESET_NUM_PATH):
                if not os.path.getsize(RESET_NUM_PATH):
                    output = "ERR: The file is empty "
                    self.logger_debug("%s" % output)
                else:
                    count, ret = platcomutil.run_shell_cmd("cat" + ' ' + RESET_NUM_PATH + ' ' + "|grep bmc_reset_num|awk '{print $3}'")
                    if ret != 0:
                        output = "ERR: fail to get count from file result=%s" % count
                        self.logger_debug("End get count from file = %s" % output)
                        count = 0
                    try:
                        count = int(count)
                    except Exception as e:
                        count = 0
            power_cycle_reg = self.bmc_reset_cnt_reg.get('cycle', None)
            power_reset_reg = self.bmc_reset_cnt_reg.get('reset', None)
            if power_cycle_reg == None and power_reset_reg == None:
                ret, reset_num = self.get_value(self.bmc_reset_cnt_reg)
                if ret == False:
                    output = "ERR: i2c read bmc_reset_cnt_reg, result:%s" % reset_num
                    self.logger_debug("End read bmc reset num result=%s" % output)
                reset_num = int(reset_num)
                count = count + reset_num
            else:
                if self.bmc_reset_cnt_reg.get('diff_reg', 0) == 1:
                    ret, cycle_num = self.get_value(power_cycle_reg)
                    if ret == False:
                        output = "ERR: i2c read bmc cycle_reg, result:%s" % cycle_num
                        self.logger_debug("End read bmc cycle_reg num result=%s" % output)
                    cycle_num = int(cycle_num)
                    count = count + cycle_num
                    ret, reset_num = self.get_value(power_reset_reg)
                    if ret == False:
                        output = "ERR: i2c read bmc reset_reg, result:%s" % reset_num
                        self.logger_debug("End read bmc reset_reg num result=%s" % output)
                    reset_num = int(reset_num)
                    count = count + reset_num
                else:
                    ret, val = self.get_value(power_cycle_reg)
                    if ret == False:
                        output = "ERR: i2c read bmc reset reg failed, result:%s" % val
                        self.logger_debug("End: read bmc reset reset num result=%s" % output)
                    temporary = int(val)
                    cycle_num = self.get_reg_data(temporary, power_cycle_reg.get('mask'), power_cycle_reg.get('shift'), 'right')
                    count = count + int(cycle_num)
                    reset_num = self.get_reg_data(temporary, power_reset_reg.get('mask'), power_reset_reg.get('shift'), 'right')
                    count = count + int(reset_num)
            cmd = AST_FUNC_SOURCE + ' ' + REPLACE_RESET_NUM + ' ' + RESET_NUM_PATH + ' ' + "bmc_reset_num" + ' ' + str(count)
            cmd_log, ret = platcomutil.run_shell_cmd(cmd)
            if ret != 0:
                output = "ERR: fail to write reset_num file,result: %s,log= %s" %(ret, cmd_log)
                self.logger_debug("End to write reset_num file,result=%s" % output)
        except Exception as e:
            self.logger_debug("Error returned: " + str(e))
            count = -1
        return count

    def get_bmc_reset_num(self):
        """
        get bmc reset num.
        @return bmc reset num on success, -1 for failure
        """
        rest_num = 0
        return_value = -1
        if self.bmc_reset_cnt_reg == None:
            output = "ERR: no support get bmc reset num"
            self.logger_debug("End get bmc reset num result=%s" % output)
            return return_value
        if self.bmc_reset_cnt_reg.get('read_clean', 0) == 1:
            rest_num = self.get_bmc_reset_num_reg()
            return rest_num
        power_cycle_reg = self.bmc_reset_cnt_reg.get('cycle', None)
        power_reset_reg = self.bmc_reset_cnt_reg.get('reset', None)
        if power_cycle_reg == None and power_reset_reg == None:
            ret, reset_num = self.get_value(self.bmc_reset_cnt_reg)
            if ret == False:
                output = "ERR: i2c read bmc_reset_cnt_reg failed result:%s" % reset_num
                self.logger_debug("End get bmc reset num result=%s" % output)
            else:
                return_value = reset_num
            return return_value
        else:
            if power_cycle_reg != None:
                ret, power_cycle_time = self.get_value(power_cycle_reg)
                if ret == False:
                    output = "ERR: i2c read power_cycle_reg failed result: %s" % power_cycle_time
                    self.logger_debug("End get bmc reset num result=%s" % output)
                    return return_value
                else:
                    rest_num = rest_num + power_cycle_time
            if power_reset_reg != None:
                ret, power_reset_time = self.get_value(power_reset_reg)
                if ret == False:
                    output = "ERR: i2c read power_reset_reg failed result: %s, power_cycle_time: %s" %(power_reset_time, power_cycle_time)
                    self.logger_debug("End get bmc reset num result=%s" % output)
                    return return_value
                else:
                    rest_num = rest_num + power_reset_time
            return rest_num

    def get_sys_eeprom(self):
        """
        Get SYSEEPROM
        @return SYSEEPROM content dict or None for failure.

        """
        dict_sys = collections.OrderedDict()
        dict_sys["Product Serial"] = "N/A"
        dict_sys["Product Name"] = "N/A"
        dict_sys["Product Part Number"] = "N/A"
        dict_sys["Product Manufacturer"] = "N/A"
        dict_tmp = self.__import_fru_eeprom_config()
        if dict_tmp == None:
            self.logger_debug("Get sys eeprom failed")
            return dict_tmp
        try:
            dict_sys["Product Serial"] = dict_tmp.get("productSerialNumber")
            dict_sys["Product Name"] = dict_tmp.get("productName")
            dict_sys["Product Part Number"] = dict_tmp.get("productPartModelName")
            dict_sys["Product Manufacturer"] = dict_tmp.get("productManufacturer")
        except Exception as e:
            self.logger_debug("Get product eeprom info failed:%s" % str(e))
        return dict_sys
