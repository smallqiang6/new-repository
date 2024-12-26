#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# bios.py
# Python implementation of the Class fan
# Original author: rd@ruijie.com.cn
#
#######################################################
from product_hal.ruijieconfig import *
from .devicebase import devicebase
from plat_hal.firmware import *

class bios(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.init_firm = firmware()
            self.name = conf.get('name', None)
            self.version_file = conf.get('FwVersion', None)
            self.bios_flash = conf.get('BiosFlash', None)
            self.bios_boot_ok = conf.get('BiosBootReg', None)
            # Register for master or slave bios whether or not failed
            self.bios_fail = conf.get('BiosFailReg', None)

    def set_bios_dict_result(self, dict_bios_info, data, tag):
        data = data.strip('\n')
        result_flag = True
        if "master" in data :
            dict_bios_info["Flash"] = "master"
        elif "slave" in data :
            dict_bios_info["Flash"] = "slave"
        else:
            result_flag = False
            self.logger_debug("Unknown bios flash status result(%s)" % (data))
        if result_flag == True and tag == True:
            dict_bios_info["Result"] = "success"
        if result_flag == False and tag == False:
            dict_bios_info["Result"] = "NA"
        return dict_bios_info

    def get_bios_boot_status(self):
        dict_bios_info = { "Flash":"N/A",
                           "Result":"N/A",
                         }
        ret_boot, val_boot = self.get_value(self.bios_boot_ok)
        ret_bios, val_bios = self.get_value(self.bios_fail)
        if ret_boot == False or ret_bios == False:
            # Flash boot failed to switch another flash, CPU board will lose power
            # No register access for 5 seconds 
            self.logger_debug("Unknown bios flash boot result(%s), and bios failed result(%s)" % (val_boot, val_bios))
            return dict_bios_info
        # BIOS boot complete
        # int(val_boot, 16) & 0x01, BiosOk(1), BiosSetup(0)
        if val_boot & 0x01 == 1:
            ret, output = self.command(self.bios_flash)
            if ret == 0:
                dict_bios_info = self.set_bios_dict_result(dict_bios_info, output, True)
            else:
                self.logger_debug("Unknown bios view_flash result(%s)" % (output))
        else:
            # During BIOS boot
            # int(val_bios, 16) & 0x03,biosSetup(0),MasterFailed(1),MlaveFailed(2),BothFailed(3)
            output = val_bios & 0x03
            if  output == 0:
                data = self.init_firm.get_bios_next_boot()
                dict_bios_info = self.set_bios_dict_result(dict_bios_info, data, False)
            elif output == 1:
                dict_bios_info["Flash"] = "master"
                dict_bios_info["Result"] = "failed"
            elif output == 2:
                dict_bios_info["Flash"] = "slave"
                dict_bios_info["Result"] = "failed"
            else:
                dict_bios_info["Result"] = "failed"
                data = self.init_firm.get_bios_next_boot()
                dict_bios_info = self.set_bios_dict_result(dict_bios_info, data, False)
        return dict_bios_info

    def set_bios_version(self, flash, version):
        cmd = "/usr/local/bin/store_bios_version.sh " + flash + " " + version
        ret, output = self.command(cmd)
        if ret:
            self.logger_debug("set bios version failed")
            return -1
        return 0

    def get_bios_version(self):
        dict_version_info = { "MasterBiosVersion":"N/A",
                              "SlaveBiosVersion":"N/A",
                            }
        if not os.path.exists(self.version_file):
            self.logger_debug("%s does not exist: " %(self.version_file))
            return dict_version_info
        dict_ver = platcomutil.JSONparserFile(self.version_file)
        if dict_ver == None:
            self.logger_debug("get bios version failed")
            return dict_version_info
        else:
            for i in dict_ver:
                re_version = dict_ver[i].replace(r"\(","(")
                dict_ver[i] = re_version.replace(r"\)",")")
            if "master-bios-fw" in dict_ver:
                dict_version_info["MasterBiosVersion"] = dict_ver["master-bios-fw"]
            if "slave-bios-fw" in dict_ver :
                dict_version_info["SlaveBiosVersion"] = dict_ver["slave-bios-fw"]
        return dict_version_info
