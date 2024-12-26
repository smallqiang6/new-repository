#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

import subprocess
import os
import sys
import re
from product_hal.ruijieconfig import *
from .devicebase import devicebase

EXIT_SUCCESS = 0
EXIT_FAILED = -1
AST_FUNC_SOURCE = "/usr/local/bin/ast-functions "
AST_FUNC_CALL = "ast_product_func_call "

class fpga_fw(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.name = conf.get('name', None)
            self.fw_5387_eeprom_path = conf.get('Fw5387EepromPath', None)
            self.fw_bcm53134_eeprom_path = conf.get('Fwbcm53134EepromPath', None)
            self.fw_88e6321_eeprom_path = conf.get('Fw88e6321EepromPath', None)
            self.upgrade_fpga_path = conf.get('UpgradeFpgaPath', None)
            self.Capacity = conf.get('Capacity', None)
            self.upgrade_mac_path = conf.get('UpgradeMacPath', None)
            self.upgrade_8367_path = conf.get('Upgrade8367Path', None)

    def upgrade_fw_fpga(self, bin):
        """
        upgrade fw fpga
        @param bin for fpga

        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        output = None
        ret = EXIT_FAILED
        # check fpga bin
        if os.path.exists(bin):
            if not os.path.getsize(bin):
                output = "ERR: %s does empty" % bin
        else:
            output = "ERR: %s does not exist" % bin
        if output != None:
            self.logger_debug(output)
            return ret, output
        # upgrade fpga bin
        self.logger_debug("Begin upgrade fpga...")
        upgrade_cmd = self.upgrade_fpga_path +" upgrade_fpga " +bin
        ret_status, output = self.command(upgrade_cmd)
        if ret_status:
            output = "ERR:upgrade fpga failed, ret_status:%d" % ret_status
            self.logger_debug(output)
        else:
            output = "OK:ok"
            ret = EXIT_SUCCESS
        self.logger_debug("End upgrade fpga, result=%s" % output)
        return ret, output

    def get_fpga_md5sum(self):
        output = None
        ret = EXIT_FAILED
        fpgamd5_cmd = self.upgrade_fpga_path +" get_md5sum"
        ret_status, output = self.command(fpgamd5_cmd)
        if ret_status:
            output = "ERR:get fpga md5 failed, ret_status:%d" % ret_status
            self.logger_debug(output)
        else:
            ret = EXIT_SUCCESS
        return ret, output

    def upgrade_fw_vlanswitch(self, fw_type, bin):
        """
        upgrade fw 5387/88e6321/bcm53134
        @param bin for 5387/88e6321/bcm53134
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = EXIT_FAILED
        output =None
        if fw_type == "88e6321":
            fw_eeprom_path = self.fw_88e6321_eeprom_path
        elif fw_type == "bcm53134":
            fw_eeprom_path = self.fw_bcm53134_eeprom_path
        else:
            fw_eeprom_path = self.fw_5387_eeprom_path
        # check 5387/88e6321/bcm53134 bin
        if os.path.exists(fw_eeprom_path):
            if os.path.exists(bin):
                if not os.path.getsize(bin):
                    output = "ERR: %s does empty" % bin
            else:
                output = "ERR: %s does not exist" % bin
        else:
            output = "ERR: %s does not exist" % fw_eeprom_path
        if output != None:
            self.logger_debug(output)
            return ret, output
        # upgrade fw 5387 bin
        self.logger_debug("Begin upgrade %s ..." % fw_type)
        cmd = "cat " + bin + ">" + fw_eeprom_path
        ret_status, output = self.command(cmd)
        if ret_status:
            output = "ERR: upgrade %s %s failed" % (fw_type, bin)
            self.logger_debug(output)
        else:
            output = "OK:ok"
            ret = EXIT_SUCCESS
        self.logger_debug("End upgrade %s, result=%s" % (fw_type,output))
        return ret, output

    def get_fw_vlanswitch_version(self, fw_type):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = EXIT_FAILED
        if fw_type == "88e6321":
            fw_eeprom_path = self.fw_88e6321_eeprom_path
        elif fw_type == "bcm53134":
            fw_eeprom_path = self.fw_bcm53134_eeprom_path
        else:
            fw_eeprom_path = self.fw_5387_eeprom_path
        if os.path.exists(fw_eeprom_path):
            cmd = "md5sum " + fw_eeprom_path
            ret_status, output = self.command(cmd)
            if ret_status:
                output = "ERR:get %s version failed, result:%s" % (fw_type, output)
                self.logger_debug(output)
            else:
                output = output.split(" ")[0]
                ret = EXIT_SUCCESS
        else:
            output = "%s path(%s) does not exist" % (fw_type, fw_eeprom_path)
            self.logger_debug(output)
        return ret, output

    def upgrade_fw_switch(self, fw_type, bin):
        """
        upgrade fw mac/atlas/rtl8372
        @param bin for mac/atlas/rtl8372

        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        output = None
        ret = EXIT_FAILED
        # check bin
        if os.path.exists(bin):
            if not os.path.getsize(bin):
                output = "ERR: %s does empty" % bin
        else:
            output = "ERR: %s does not exist" % bin
        if output != None:
            self.logger_debug(output)
            return ret, output
        # upgrade bin
        self.logger_debug("Begin upgrade %s..." % fw_type)
        upgrade_cmd = self.upgrade_mac_path + (" upgrade_%s " % fw_type) +bin
        ret_status, output = self.command(upgrade_cmd)
        if ret_status:
            output = "ERR: upgrade %s failed, ret_status:%d" % (fw_type, ret_status)
            self.logger_debug(output)
        else:
            output = "OK:ok"
            ret = EXIT_SUCCESS
        self.logger_debug("End upgrade %s, result=%s" % (fw_type, output))
        return ret, output

    def get_switch_md5sum(self, fw_type):
        output = None
        ret = EXIT_FAILED
        if self.upgrade_mac_path == None:
            output = "upgrade_mac_path is None"
            self.logger_debug(output)
            return ret, output
        macmd5_cmd = self.upgrade_mac_path + (" get_%s_md5sum" % fw_type)
        ret_status, output = self.command(macmd5_cmd)
        if ret_status:
            output = "ERR:get %s md5 failed, ret_status:%d" % (fw_type, ret_status)
            self.logger_debug(output)
        else:
            ret = EXIT_SUCCESS
        return ret, output

    def upgrade_fw_8367(self, bin):
        """
        upgrade fw 8367
        @param bin for 8367

        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = EXIT_FAILED
        output =None
        if self.Capacity.get("upgrade8367", 0) == 0:
            output = "ERR: not support upgrade 8367"
            return ret, output
        # upgrade 8367 bin
        self.logger_debug("Begin upgrade 8367...")
        upgrade_cmd = self.upgrade_8367_path +" upgrade_8367 " +bin
        ret_status, output = self.command(upgrade_cmd)
        if ret_status:
            output = "ERR:upgrade 8367 failed, ret_status:%d" % ret_status
            self.logger_debug(output)
        else:
            output = "OK:ok"
            ret = EXIT_SUCCESS
        self.logger_debug("End upgrade 8367, result=%s" % output)
        return ret, output

    def get_fw_8367_version(self):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = EXIT_FAILED
        if self.Capacity.get("get8367version", 0) == 0:
            output = "ERR: not support get 8367 version"
            return ret, output
        self.logger_debug("Begin get 8367 version...")
        md5_cmd = self.upgrade_8367_path + " get_md5sum"
        ret_status, output = self.command(md5_cmd)
        if ret_status:
            output = "ERR:get 8367 md5 failed, ret_status:%d" % ret_status
            self.logger_debug(output)
        else:
            ret = EXIT_SUCCESS
        return ret, output

    def get_operate_capacity(self, operation):
        operation_name = "%s" %operation
        if self.Capacity == None:
            output = "Capacity is None"
            self.logger_debug(output)
            return 0
        if self.Capacity.get(operation_name, 0) == 0:
            output = "ERR: not support operation %s" %operation_name
            self.logger_debug(output)
            return 0
        return 1

    def get_port_power_status(self):
        """
        @return port power status, on/off for success, N/A for failure
        """
        current_status = "N/A"
        if self.Capacity.get("getportpowerstatus", 0) == 0:
            output = "ERR: not support get port power status"
            self.logger_debug("End get port power status,result=%s" % output)
            return current_status
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " port_status"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        #0: off 1: on 2:unknown
        if ret == 0:
            current_status = "off"
        elif ret == 1:
            current_status = "on"
        else:
            output = "ERR: I2C read port power status failed,restult: %s %s" % (ret, cmd_log)
            self.logger_debug(output)
        return current_status

    def set_port_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure
        """
        return_value = EXIT_FAILED
        if self.Capacity.get("getportpowerstatus", 0) == 0:
            output = "ERR: not support set port power status"
            self.logger_debug("End set port power status,result=%s" % output)
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_off_port"
        if status == "on":
             cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_on_port"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret != 0:
            output = "ERR: I2C set port power status failed,result: %s %s" %(ret, cmd_log)
        else:
            return_value = EXIT_SUCCESS
            output = "set port power status succeed"
        self.logger_debug("End set port power status,result=%s" % output)
        return return_value

    def get_td4_power_status(self):
        """
        @return td4 power status, on/off for success, N/A for failure
        """
        current_status = "N/A"
        if self.Capacity.get("gettd4powerstatus", 0) == 0:
            output = "ERR: not support get TD4 power status"
            self.logger_debug("End get TD4 power status,result=%s" % output)
            return current_status
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " mac_status"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        #0: off 1: on 2:unknown
        if ret == 0:
            current_status = "off"
        elif ret == 1:
            current_status = "on"
        else:
            output = "ERR: I2C read TD4 power status failed,restult: %s %s" % (ret, cmd_log)
            self.logger_debug(output)
        return current_status

    def set_td4_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure
        """
        return_value = EXIT_SUCCESS
        if self.Capacity.get("gettd4powerstatus", 0) == 0:
            output = "ERR: not support set TD4 power status"
            self.logger_debug("End set TD4 power status,result=%s" % output)
            return_value = EXIT_FAILED
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_on_mac"
        if status == "off":
            if self.Capacity.get("powerportwithtd4", 0) == 1:
                if self.set_port_power("off"):
                    self.logger_debug("ERR, set TD4 power status: failed to set port off")
                    return_value = EXIT_FAILED
                if self.enable_host_cpu_power_force_control(1) != 0:
                    return_value = EXIT_FAILED
                    return return_value
            cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_off_mac"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret != 0:
            self.logger_debug("ERR: I2C set TD4 power status failed,result: %s %s" %(ret, cmd_log))
            return_value = EXIT_FAILED
        if status == "on":
            if self.Capacity.get("powerportwithtd4") == 1:
                if self.enable_host_cpu_power_force_control(1) != 0:
                    return_value = EXIT_FAILED
                    return return_value
                if self.set_port_power("on"):
                    self.logger_debug("ERR, set TD4 power status: failed to set port on")
                    return_value = EXIT_FAILED
        if return_value == EXIT_SUCCESS:
            self.logger_debug("End set TD4 power status, succeed")
        else:
            self.logger_debug("End set TD4 power status, failed")
        return return_value

    def get_ssd_power_status(self):
        """
        @return ssd power status, on/off for success, N/A for failure
        """
        current_status = "N/A"
        if self.Capacity.get("getssdpowerstatus", 0) == 0:
            output = "ERR: not support get ssd power status"
            self.logger_debug("End get ssd power status,result=%s" % output)
            return current_status
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " ssd_status"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        #0: off 1: on 2:unknown
        if ret == 0:
            current_status = "off"
        elif ret == 1:
            current_status = "on"
        else:
            output = "ERR: I2C read ssd power status failed,restult: %s %s" % (ret, cmd_log)
            self.logger_debug(outputg)
        return current_status

    def set_ssd_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure
        """
        return_value = EXIT_FAILED
        if self.Capacity.get("getssdpowerstatus", 0) == 0:
            output = "ERR: not support set ssd power status"
            self.logger_debug("End set ssd power status,result=%s" % output)
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_off_ssd"
        if status == "on":
             cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_on_ssd"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret != 0:
            output = "ERR: I2C set ssd power status failed,result: %s %s" %(ret, cmd_log)
        else:
            return_value = EXIT_SUCCESS
            output = "set ssd power status succeed"
        self.logger_debug("End set ssd power status,result=%s" % output)
        return return_value

    def set_bmcemmc_power_cycle(self):
        """
        power cycle bmc emmc
        @default return 0 for operation done
        """
        return_value = EXIT_SUCCESS
        if self.Capacity.get("powerbmcemmc", 0) == 0:
            output = "ERR: not support bmc emmc power status"
            self.logger_debug("End set bmc emmc power status,result=%s" % output)
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_cycle_bmcemmc"
        platcomutil.run_shell_cmd(cmd)
        self.logger_debug("Power cycle bmc emmc done")
        return return_value

    def set_cpuemmc_power_cycle(self):
        """
        power cycle cpu emmc
        @default return 0 for operation done
        """
        return_value = EXIT_SUCCESS
        if self.Capacity.get("powercpuemmc", 0) == 0:
            output = "ERR: not support cpu emmc power status"
            self.logger_debug("End set cpu emmc power status,result=%s" % output)
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_cycle_cpuemmc"
        platcomutil.run_shell_cmd(cmd)
        self.logger_debug("Power cycle cpu emmc done")
        return return_value

    def get_netcard_power_status(self, netcard):
        """
        @return netcard power status, on/off for success, N/A for failure
        """
        current_status = "N/A"
        if self.Capacity.get("getnetcardpowerstatus", 0) == 0:
            output = "ERR: not support get netcard power status"
            self.logger_debug("End get %s power status,result=%s" % (netcard, output))
            return current_status
        netcardid = netcard.split("netcard")[-1]
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " netcard_status %s" % netcardid
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        #0: off 1: on 2:unknown
        if ret == 0:
            current_status = "off"
        elif ret == 1:
            current_status = "on"
        else:
            output = "ERR: I2C read %s power status failed,restult: %s %s" % (netcard, ret, cmd_log)
            self.logger_debug(output)
        return current_status

    def set_netcard_power(self,netcard, status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure
        """
        return_value = EXIT_SUCCESS
        if self.Capacity.get("getnetcardpowerstatus", 0) == 0:
            output = "ERR: not support set netcard power status"
            self.logger_debug("End set %s power status,result=%s" % (netcard, output))
            return_value = EXIT_FAILED
            return return_value
        netcardid = netcard.split("netcard")[-1]
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_off_netcard %s" % netcardid
        if status == "on":
            cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_on_netcard %s" % netcardid
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret != 0:
            output = "ERR: I2C set %s power status failed,result: %s %s" %(netcard, ret, cmd_log)
        else:
            return_value = EXIT_SUCCESS
            output = "set %s power status succeed" % netcard
        self.logger_debug("End set netcard power status,result=%s" % output)
        return return_value

    def get_host_cpu_power_force_control_status(self):
        """
        @return host cpu power force control, 1 for enable, 0 for disable, -1 for failure
        """
        current_status = -1
        if self.Capacity.get("getforcecontrolpowerstatus", 0) == 0:
            output = "ERR: not support get force control power status"
            self.logger_debug("End get force control power status,result=%s" % output)
            return current_status
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " get_host_cpu_power_force_control_status"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        #0: off 1: on 2:unknown
        if ret == 0:
            current_status = 0
        elif ret == 1:
            current_status = 1
        else:
            output = "ERR: I2C read force control status failed,restult: %s %s" % (ret, cmd_log)
            self.logger_debug(output)
        return current_status

    def enable_host_cpu_power_force_control(self,enable):
        """
        @status 1 power on, 0 power off.
        @return 0 for success, -1 for failure
        """
        return_value = EXIT_FAILED
        if self.Capacity.get("getforcecontrolpowerstatus", 0) == 0:
            output = "ERR: not support set force control power"
            self.logger_debug("End set force control status,result=%s" % output)
            return return_value
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " disable_host_cpu_power_force_control"
        if enable == 1:
             cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " enable_host_cpu_power_force_control"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret != 0:
            output = "ERR: I2C set force control status failed,result: %s %s" %(ret, cmd_log)
        else:
            return_value = EXIT_SUCCESS
            output = "set force control status succeed"
        self.logger_debug("End set force control status,result=%s" % output)
        return return_value
