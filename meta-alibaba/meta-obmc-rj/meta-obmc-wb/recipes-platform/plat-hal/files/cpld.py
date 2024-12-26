#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# cpld.py
# Python implementation of the Class fan
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase
from product_hal.ruijieconfig import *

class cpld(devicebase):
    __user_reg  = None

    def __init__(self, conf = None):
        if conf is not  None:
            self.name = conf.get('name', None)
            self.user_reg = conf.get('UserReg', None)
            self.console_reg = conf.get('ConsoleReg', None)
            self.console_reg_attrs = conf.get('ConsoleRegAttrs', None)
            self.version_file = conf.get('VersionFile', None)
            self.upgrade_result = conf.get('UpgradeResultFile', None)

    def get_user_reg(self):
        if (self.user_reg == None):
            return Flase
        ret, val = self.get_value(self.user_reg)
        return val

    def set_user_reg(self, value):
        if (self.user_reg == None):
            return Flase
        byte = value & 0xFF
        ret, val = self.set_value(self.user_reg, byte)
        return ret

    def set_console_owner(self, owner):
        ret = False
        if (self.console_reg == None):
            return False
        if (self.console_reg.get("cmd", None) == "shell"):
            cmd = "/usr/local/bin/ast-functions " + "ast_product_func_call " + "swithch_serial " + owner
            cmd_log, ret_value = platcomutil.run_shell_cmd(cmd)
            if ret_value != 0:
                output = "ERR: set console owner failed,result:%s" % cmd_log
                ret = False
            else:
                ret = True
                output = "set console owner succed"
            self.logger_debug(output)
        else:
            tmpattr = self.console_reg_attrs.get(owner, None)
            if tmpattr != None:
                ret, val = self.set_value(self.console_reg, tmpattr)
        return ret

    def get_version(self):
        ret, val = self.get_value(self.version_file)
        if (ret == False):
            val = "N/A"
            return val
        try:
            cpld_version = val.strip('\n')
        except Exception as e:
            cpld_version = "N/A"
        return cpld_version

    def get_last_upgrade_result(self):
        """
        Get last upgrade result for CPLD\\BIOS\\FPGA refresh
        @return Get last upgrade content dict or None for failure.
        """
        if not os.path.exists(self.upgrade_result):
            self.logger_debug("%s does not exist: " %(self.upgrade_result))
            return -1, None
        dict_ver = platcomutil.JSONparserFile(self.upgrade_result)
        if dict_ver == None:
            self.logger_debug("get last upgrade result failed")
            return -1, dict_ver
        return 0, dict_ver
