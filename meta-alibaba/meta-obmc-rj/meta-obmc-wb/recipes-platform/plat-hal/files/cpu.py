###############################################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# Hardware Abstraction Layer APIs -- CPU APIs.
#
# Copyright (C) Ruijie, INC.
#
###############################################################################
from .devicebase import devicebase
from product_hal.ruijieconfig import *
import os

CPU_LAST_RESET_FILE_PATH = "/var/log/fw/cpu_last_reset_status"
CPU_IERR_PATH = "/var/log/fw/cpu_ierr"
CPU_MCE_PATH  = "/var/log/fw/cpu_mcerr"
CPU_AER0_PATH = "/var/log/fw/cpu_aer_err0"
CPU_AER1_PATH = "/var/log/fw/cpu_aer_err1"
CPU_AER2_PATH = "/var/log/fw/cpu_aer_err2"
RESET_NUM_PATH = "/tmp/reset_count"
AST_FUNC_SOURCE = "/usr/local/bin/ast-functions "
AST_FUNC_CALL = "ast_product_func_call "
REPLACE_RESET_NUM = "replace_reset_num"

class cpu(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.name = conf.get('name', None)
            self.cpu_status = conf.get('CpuStatus', None)
            self.cpu_status_attrs = conf.get('CpuStatusAttrs', None)
            self.cpu_status_on = self.cpu_status_attrs.get("on")
            self.cpu_status_off = self.cpu_status_attrs.get("off")
            self.cpu_reset_cnt_reg = conf.get('CpuResetCntReg', None)
            self.cpu_reset_type_reg = conf.get('CpuResetTypeReg', None)
            self.cpu_reset_type_attrs = conf.get('CpuResetTypeAttrs', None)
            self.machine_reset_reg = conf.get('MachineResetReg', None)

    def read_file(self, file_path):
        result, ret = platcomutil.run_shell_cmd("cat " + file_path)
        return result, ret

    def get_state(self):
        """
        Get CPU current status.

        @return 'S0', ..., 'S5', or 'N/A' for failure
        """
        # Read CPU state
        output = "N/A"
        ret, cpu_status = self.get_value(self.cpu_status)
        if ret == False:
            self.logger_debug("get cpu status failed")
        elif cpu_status == self.cpu_status_on:
            output = "S0"
        elif cpu_status == self.cpu_status_off:
            output = "S5"
        else:
            self.logger_debug("current CPU status is UNKNOWN, cpu_status=%d" %(cpu_status))
        return output

    def get_mca_ierr_error_count(self, file_path, mca_type, cpu_mce_ierr):
        if os.path.exists(file_path):
            cpu_mce, err = self.read_file(file_path)
            if err:
                self.logger_debug("Read CPU %s file %s failed" %(mca_type, file_path))
            else:
                try:
                    cpu_mce_ierr[mca_type] = int(cpu_mce.strip('\n'))
                except:
                    self.logger_debug("CPU %s file %s is in use: '%s'" % (mca_type, file_path, cpu_mce))
        else:
            cpu_mce_ierr[mca_type] = 0
        return cpu_mce_ierr

    def get_mca_error(self):
        """
        Get CPU MCA error count.
        @return List of MCERR and IERR counts, or None for failure
                Example:
                {
                    "MCErr": 0,         # -99999
                    "IErr": 0           # -99999
                }
        """
        #Get CPU MCA error count
        cpu_mce_ierr = {"MCErr": -99999, "IErr": -99999}
        cpu_mce_ierr = self.get_mca_ierr_error_count(CPU_IERR_PATH, "IErr", cpu_mce_ierr)
        #Get CPU IErr error count
        cpu_mce_ierr = self.get_mca_ierr_error_count(CPU_MCE_PATH, "MCErr", cpu_mce_ierr)
        return cpu_mce_ierr

    def get_aer_error_count(self, cpu_aer, file_path, index):
        if os.path.exists(file_path):
            cpu_aer_err, err = self.read_file(file_path)
            if err:
                self.logger_debug("Read CPU aer err%s file %s failed" %(index, file_path))
            else:
                try:
                    cpu_aer[index] = int(cpu_aer_err.strip('\n'))
                except:
                    self.logger_debug("CPU aer err%s file %s is in use: '%s'" % (index, file_path, cpu_aer_err))
        else:
            cpu_aer[index] = 0
        return cpu_aer

    def get_aer_error(self):
        """
        Get CPU AER error vector.

        @return List of AER error vector or None for failure
                Example:
                [ERR[0], ERR[1], ERR[2]]
        """
        cpu_aer = [-1, -1, -1]
        #Get CPU AER0 error count
        cpu_aer = self.get_aer_error_count(cpu_aer, CPU_AER0_PATH, 0)
        #Get CPU AER1 error count
        cpu_aer = self.get_aer_error_count(cpu_aer, CPU_AER1_PATH, 1)
        #Get CPU AER2 error count
        cpu_aer = self.get_aer_error_count(cpu_aer, CPU_AER2_PATH, 2)
        return cpu_aer

    def get_last_reset(self):
        """
        Get last CPU reset type, WARM/COLD.

        @return Last CPU reset type, "WARM"/"COLD", "N/A" for failure
        """
        if self.cpu_reset_type_reg != None:
            return self.get_last_reset_by_reg()
        if os.path.exists(CPU_LAST_RESET_FILE_PATH):
            last_reset_cpu_status, err = self.read_file(CPU_LAST_RESET_FILE_PATH)
            reset_cpu_status = last_reset_cpu_status.strip('\n')
            if err:
                self.logger_debug("Read last CPU reset type file %s failed" %(CPU_LAST_RESET_FILE_PATH))
                return "N/A"
            if reset_cpu_status == "COLD":
                return "COLD"
            if reset_cpu_status == "WARM":
                return "WARM"
            self.logger_debug("Last CPU reset type is UNKNOWN" )
            return "N/A"
        else:
            return "COLD"

    def set_cpu_host_watchdog(self, value):
        cmd = 'echo ' + value + ' >/tmp/watchdog'
        ret, output = self.command(cmd)
        if ret:
            self.logger_debug("set host cpu watchdog(%s) failed" %(value))
            return -1
        return 0

    def get_cpu_reset_num_reg(self):
        """
        get cpu reset num from register, register is cleared after it has been read
        distinguish by "read_clean" = 1, default 0
        1.only one read_clean register
        2.diff regs for reset/cycle, distinguish by "diff_reg" = 1, default 0
        3.reset/cycle use the same regs
        @return cpu reset number from the register
        """
        count = 0
        output = "N/A"
        try:
            if os.path.exists(RESET_NUM_PATH):
                if not os.path.getsize(RESET_NUM_PATH):
                    output = "ERR: The file is empty "
                    self.logger_debug("%s" % output)
                else:
                    count, ret = platcomutil.run_shell_cmd("cat" + ' ' + RESET_NUM_PATH + ' ' + "|grep cpu_reset_num|awk '{print $3}'")
                    if ret != 0:
                        output = "ERR: fail to get count from file result=%s" % count
                        self.logger_debug("End get count from file = %s" % output)
                        count = 0
                    try:
                        count = int(count)
                    except Exception as e:
                        count = 0
            power_cycle_reg = self.cpu_reset_cnt_reg.get('cycle', None)
            power_reset_reg = self.cpu_reset_cnt_reg.get('reset', None)
            if power_cycle_reg == None and power_reset_reg == None:
                ret, reset_num = self.get_value(self.cpu_reset_cnt_reg)
                if ret == False:
                    output = "ERR: i2c read cpu_reset_cnt_reg, result:%s" % reset_num
                    self.logger_debug("End read cpu reset num result=%s" % output)
                reset_num = int(reset_num)
                count = count + reset_num
            else:
                if self.cpu_reset_cnt_reg.get('diff_reg', 0) == 1:
                    ret, cycle_num = self.get_value(power_cycle_reg)
                    if ret == False:
                        output = "ERR: i2c read cpu cycle_reg, result:%s" % cycle_num
                        self.logger_debug("End read cpu cycle_reg num result=%s" % output)
                    cycle_num = int(cycle_num)
                    count = count + cycle_num
                    ret, reset_num = self.get_value(power_reset_reg)
                    if ret == False:
                        output = "ERR: i2c read cpu reset_reg, result:%s" % reset_num
                        self.logger_debug("End read cpu reset_reg num result=%s" % output)
                    reset_num = int(reset_num)
                    count = count + reset_num
                else:
                    ret, val = self.get_value(power_cycle_reg)
                    if ret == False:
                        output = "ERR: i2c read cpu reset reg failed, result:%s" % val
                        self.logger_debug("End: read cpu reset reset num result=%s" % output)
                    temporary = int(val)
                    cycle_num = self.get_reg_data(temporary, power_cycle_reg.get('mask'), power_cycle_reg.get('shift'), 'right')
                    count = count + int(cycle_num)
                    reset_num = self.get_reg_data(temporary, power_reset_reg.get('mask'), power_reset_reg.get('shift'), 'right')
                    count = count + int(reset_num)
            cmd = AST_FUNC_SOURCE + ' ' + REPLACE_RESET_NUM + ' ' + RESET_NUM_PATH + ' ' + "cpu_reset_num" + ' ' + str(count)
            cmd_log, ret = platcomutil.run_shell_cmd(cmd)
            if ret != 0:
                output = "ERR: fail to write reset_num file,result: %s,log= %s" %(ret, cmd_log)
                self.logger_debug("End to write reset_num file,result=%s" % output)
        except Exception as e:
            self.logger_debug("Error returned: " + str(e))
            count = -1
        return count

    def get_cpu_reset_num(self):
        """
        get cpu reset num.
        @return cpu reset number, -1 for failure
        """
        rest_num = 0
        return_value = -1
        if self.cpu_reset_cnt_reg == None:
            output = "ERR: no support get cpu reset num"
            self.logger_debug("End get cpu reset num result=%s" % output)
            return return_value
        if self.cpu_reset_cnt_reg.get('read_clean', 0) == 1:
            rest_num = self.get_cpu_reset_num_reg()
            return rest_num
        power_cycle_reg = self.cpu_reset_cnt_reg.get('cycle', None)
        power_reset_reg = self.cpu_reset_cnt_reg.get('reset', None)
        if power_cycle_reg == None and power_reset_reg == None:
            ret, reset_num = self.get_value(self.cpu_reset_cnt_reg)
            if ret == False:
                output = "ERR: i2c read cpu_reset_cnt_reg,result:%s" % reset_num
                self.logger_debug("End get cpu reset num result=%s" % output)
            else:
                return_value = reset_num
            return return_value
        else:
            if power_cycle_reg != None:
                ret, power_cycle_time = self.get_value(power_cycle_reg)
                if ret == False:
                    output = "ERR: i2c read power_cycle_reg failed result: %s" % power_cycle_time
                    self.logger_debug("End get cpu reset num result=%s" % output)
                    return return_value
                else:
                    rest_num = rest_num + power_cycle_time
            if power_reset_reg != None:
                ret, power_reset_time = self.get_value(power_reset_reg)
                if ret == False:
                    output = "ERR: i2c read power_reset_reg failed result: %s, power_cycle_time: %s" %(power_reset_time, power_cycle_time)
                    self.logger_debug("End get cpu reset num result=%s" % output)
                    return return_value
                else:
                    rest_num = rest_num + power_reset_time
            return rest_num

    def get_last_reset_by_reg(self):
        """
        Get last CPU reset type, WARM/COLD.
        @return Last CPU reset type, "WARM"/"COLD", "N/A" for failure
        """
        output = "N/A"
        if self.cpu_reset_type_reg == None:
            msg = "ERR: no support get cpu reset type"
            self.logger_debug("End get cpu reset type result=%s" % msg)
            return output
        cpu_warm_reset = self.cpu_reset_type_attrs.get("warm")
        cpu_cold_reset = self.cpu_reset_type_attrs.get("cold")
        reset_type_mask = self.cpu_reset_type_reg.get("mask")
        ret, reset_type = self.get_value(self.cpu_reset_type_reg)
        if ret == False:
            msg = "ERR: i2c read cpu_reset_type_reg failed,result:%s" % reset_type
            self.logger_debug("End get cpu reset type result=%s" % msg)
        else:
            type = (reset_type & reset_type_mask)
            if type == cpu_cold_reset:
                output = "COLD"
            elif type == cpu_warm_reset:
                output = "WARM"
            else:
                self.logger_debug("End get cpu reset type result=0x%x" % type)
        return output

    def set_machine_power_cycle(self):
        """
        @return 0 for success, -1 for failure
        """
        return_value = -1
        set_value = 0xff
        if self.machine_reset_reg == None:
            output = "ERR: not support set machine power status"
            self.logger_debug("End set machine power status,result=%s" % output)
            return return_value
        self.logger_debug("set machine power cycle")
        os.system("sync")
        if (self.machine_reset_reg.get("cmd", None) == "shell"):
            cyc_cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " power_cycle_machine "
            cmd_log, ret = platcomutil.run_shell_cmd(cyc_cmd)
            if ret != 0:
                output = "machine power cycle failed,  result: %s" % cmd_log
            else:
                return_value = 0
                output = "set machine power cycle success"
            self.logger_debug("End set machine power status,result=%s" % output)
            return return_value
        ret, value = self.set_value(self.machine_reset_reg, set_value)
        if ret == False:
            output = "ERR: I2C set machine power status failed,result %s" % value
        else:
            return_value = 0
            output = "set machine power cycle success"
        self.logger_debug("End set machine power status,result=%s" % output)
        return return_value
