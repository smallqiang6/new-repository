#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# uboot.py
# Python implementation of the Class uboot
# Original author: rd@ruijie.com.cn
#
#######################################################
from product_hal.ruijieconfig import *
from .devicebase import devicebase

AST_FUNC_SOURCE = "/usr/local/bin/ast-functions "
AST_FUNC_CALL = "ast_product_func_call "

class uboot(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.version_file = conf.get('FwVersion', None)
            self.uboot_flash = conf.get('UbootFlash', None)
            self.boot_ok = conf.get('UbootBootOkReg', None)
            self.boot_ok_typeattrs = conf.get('UbootBootOkTypeAttrs', None)

    def set_uboot_dict_result(self, dict_uboot_info, data, tag):
        data = data.strip('\n')
        result_flag = True
        if "master" in data :
            dict_uboot_info["Flash"] = "master"
        elif "slave" in data :
            dict_uboot_info["Flash"] = "slave"
        else:
            result_flag = False
            self.logger_debug("Unknown uboot flash status result(%s)" % (data))
        if result_flag == True and tag == True:
            dict_uboot_info["Result"] = "success"
        if result_flag == True and tag == False:
            dict_uboot_info["Result"] = "failed"
        if result_flag == False and tag == False:
            dict_uboot_info["Result"] = "N/A"
        return dict_uboot_info

    def get_uboot_boot_status(self):
        dict_uboot_info = { "Flash":"N/A",
                           "Result":"N/A",
                         }
        if self.boot_ok == None or self.boot_ok_typeattrs == None:
            self.logger_debug("Unknown conf boot_ok(%s) boot_ok_typeattrs(%s)" % (self.boot_ok, self.boot_ok_typeattrs))
            return dict_uboot_info
        ret_boot, val_boot = self.get_value(self.boot_ok)
        if ret_boot == False:
            # Flash boot failed, maybe in booting
            self.logger_debug("Unknown uboot flash boot result(%s)" % val_boot)
            return dict_uboot_info
        boot_ok = self.boot_ok_typeattrs.get("ok")
        boot_failed = self.boot_ok_typeattrs.get("failed")
        ret, output = self.command(self.uboot_flash)
        if ret == 0:
            # uboot boot complete
            if val_boot == boot_ok:
                dict_uboot_info = self.set_uboot_dict_result(dict_uboot_info, output, True)
            elif val_boot == boot_failed:
                dict_uboot_info = self.set_uboot_dict_result(dict_uboot_info, output, False)
            else:
                self.logger_debug("Unknown uboot boot status: %s, ok: %s,failed: %s)" % (val_boot, boot_ok, boot_failed))
                dict_uboot_info = self.set_uboot_dict_result(dict_uboot_info, output, False)
                dict_uboot_info["Result"] = "N/A"
        else:
            self.logger_debug("Unknown uboot view_flash result(%s)" % (output))
        return dict_uboot_info

    def set_uboot_version(self, flash, version):
        cmd = "/usr/local/bin/store_host_uboot_version.sh " + flash + " " + version
        ret, output = self.command(cmd)
        if ret:
            self.logger_debug("set uboot version failed")
            return -1
        return 0

    def get_uboot_version(self):
        dict_version_info = { "MasterUbootVersion":"N/A",
                              "SlaveUbootVersion":"N/A",
                            }
        if not os.path.exists(self.version_file):
            self.logger_debug("%s does not exist: " %(self.version_file))
            return dict_version_info
        dict_ver = platcomutil.JSONparserFile(self.version_file)
        if dict_ver == None:
            self.logger_debug("get uboot version failed")
            return dict_version_info
        else:
            if "master-uboot-fw" in dict_ver:
                dict_version_info["MasterUbootVersion"] = dict_ver["master-uboot-fw"]
            if "slave-uboot-fw" in dict_ver :
                dict_version_info["SlaveUbootVersion"] = dict_ver["slave-uboot-fw"]
        return dict_version_info

    def get_uboot_next_boot(self):
        current_flash = "N/A"
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " get_uboot_next_boot"
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret == 0:
            current_flash = "master"
        elif ret == 1:
            current_flash = "slave"
        else:
            self.logger_debug("Unknown uboot flash type %d %s" %(ret, cmd_log))
        return current_flash

    def set_uboot_next_boot(self, flash):
        cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " set_uboot_next_boot " + flash
        cmd_log, ret = platcomutil.run_shell_cmd(cmd)
        if ret:
            self.logger_debug("$set uboot next boot failed, cmd: %s, result: %s" %(cmd, cmd_log))
            return -1
        return 0
