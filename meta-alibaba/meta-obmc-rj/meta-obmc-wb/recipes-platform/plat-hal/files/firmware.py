
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
"""
class for Platfrom HAL for implement Firmware APIs.
"""
from product_hal.ruijieconfig import *
from .devicebase import devicebase
import shutil

PROGRAM_BIOS_PATH = "/usr/local/bin/program_bios.sh "
PROGRAM_BMC_PATH ="/usr/local/bin/program_bmc.sh "
PROGRAM_CPLD_PATH = "/usr/local/bin/program_cpld.sh "
REFRESH_CPLD_PATH = "/usr/local/bin/refresh_fw.sh "
UPGRADE_CPLD_PROGRAM_RESULT = "/tmp/upgrade_cpld_result"
UPGRADE_CPLD_REFRESH_RESULT = "/tmp/upgrade_cpld_fpga_bios_result"
AST_FUNC_SOURCE = "/usr/local/bin/ast-functions "
AST_FUNC_CALL = "ast_product_func_call "
SET_ME_STATUS = "/usr/local/bin/bios.sh me "

class firmware(devicebase):

    def __init__(self):
        pass

    def read_file(self, file_path):
        result, ret = platcomutil.run_shell_cmd("cat " + file_path)
        return result, ret

    def get_bios_capability(self):
        SYS_DEVICE_TREE = module_product.SYS_DEVICE_TREE
        capability = SYS_DEVICE_TREE.get("IS_SUPPORT_BIOS", None)
        if capability == 0:
            return 0
        elif capability != None:
            self.logger_debug("illegal capability: %s" %(capability))
        return 1

    def get_bus_addr_reg(self, spi_cs):
        SYS_DEVICE_TREE = module_product.SYS_DEVICE_TREE
        i2c_index = SYS_DEVICE_TREE[spi_cs]
        bus = i2c_index["bus"]
        addr = i2c_index["addr"]
        reg = i2c_index["reg"]
        return bus, addr, reg

    def get_bios_spi_cs_switch(self, spi_cs):
        # Determine BIOS cs switch, bit will always switch between 0 and 1
        bus, addr, reg = self.get_bus_addr_reg(spi_cs)
        i2c_cmd = "obmc_i2cget -f -y %d 0x%02x 0x%02x" %(bus, addr, reg)
        get_spi_sel, err = platcomutil.run_shell_cmd(i2c_cmd)
        if err:
            self.logger_debug("get bios %s failed" %(spi_cs))
            return -1
        return int(get_spi_sel.strip('\n'), 16)

    def set_bios_ce_switch(self, spi_cs, reg_value):
        bus, addr, reg = self.get_bus_addr_reg(spi_cs)
        i2c_cmd = "obmc_i2cset -f -y %d 0x%02x 0x%02x %s" %(bus, addr, reg, reg_value)
        set_spi_sel, err = platcomutil.run_shell_cmd(i2c_cmd)
        if err:
            self.logger_debug("set bios %s failed" %(spi_cs))
            return -1
        return 0

    def get_nextboot_reg(self):
        SYS_DEVICE_TREE = module_product.SYS_DEVICE_TREE
        return SYS_DEVICE_TREE.get("NEXT_BOOT", None)

    def get_bios_next_boot(self, purpose = "get_next_boot"):
        if self.get_bios_capability() == 0:
            self.logger_debug("cpu arch is arm, unsupport operation")
            return -1
        if self.get_nextboot_reg() != None and purpose == "get_next_boot":
            regname = "NEXT_BOOT"
        else:
            regname = "CS_SWITCH"
        bios_spi_cs = self.get_bios_spi_cs_switch("SPI_SEL")
        bios_cs_switch = self.get_bios_spi_cs_switch(regname)
        if bios_spi_cs == -1:
            self.logger_debug("get bios_spi_cs failed")
            return "N/A"
        if bios_cs_switch == -1:
            self.logger_debug("get bios_cs_switch failed")
            return "N/A"
        if bios_spi_cs & 0x02:
            if bios_cs_switch:
                return "master"
            else:
                return "slave"
        else:
            if bios_cs_switch:
                return "slave"
            else:
                return "master"

    def set_bios_next_boot(self, flash):
        if self.get_bios_capability() == 0:
            self.logger_debug("cpu arch is arm, unsupport operation")
            return -1
        if self.get_nextboot_reg() != None:
            nexboot_regname = "NEXT_BOOT"
        else:
            nexboot_regname = "CS_SWITCH"
        reg_value = "0x00"
        if flash != "master" and flash != "slave":
            self.logger_debug("set bios next boot parameter flash:%s error" %(flash))
            return -1
        bios_spi_cs = self.get_bios_spi_cs_switch("SPI_SEL")
        if bios_spi_cs == -1:
            return -1
        if bios_spi_cs & 0x02:
            if flash == "master":
                reg_value = "0x01"
        else:
            if flash == "slave":
                reg_value = "0x01"
        ret = self.set_bios_ce_switch(nexboot_regname, reg_value)
        return ret

    def set_me_status(self, status):
        if status != "recovery" and status != "reset":
            self.logger_debug("parameter status illegal, should be [recovery|reset]")
            return -1
        if self.get_bios_capability() == 0:
            self.logger_debug("cpu arch is arm, unsupport operation")
            return -1
        set_cmd = SET_ME_STATUS + status
        set_log, ret = platcomutil.run_shell_cmd(set_cmd)
        # ret: 0-success, including set me success and skip, 1-failed to write i2c, 2-check status failed
        if ret:
            self.logger_debug("Execute command(%s): failed" % set_cmd)
            return -1
        self.logger_debug("Execute command(%s): %s" % (set_cmd, set_log))
        return 0

    def judge_bios_bmc_being_upgrade(self, firmware, flash, image):
        # determine whether BMC/BIOS being upgraded
        cmd_log_flash, ret = platcomutil.run_shell_cmd("ps | grep -E \"flashcp|pflash\"")
        cmd_log_program, ret = platcomutil.run_shell_cmd("ps | grep program")
        if cmd_log_flash.find("mtd") != -1:
            self.logger_debug("%s does being upgraded %s" %(firmware, cmd_log_flash))
            return -1 
        if firmware == "bios":
            if self.get_bios_capability() == 0:
                self.logger_debug("cpu arch is arm, unsupport operation")
                return -1
            upgrade_cmd = PROGRAM_BIOS_PATH + flash + " " + image
            if cmd_log_program.find("program_bios.sh") != -1:
                self.logger_debug("BIOS does being upgraded" )
                return -1
        elif firmware == "bmc":
            upgrade_cmd = PROGRAM_BMC_PATH + flash + " " + image
            if cmd_log_program.find("program_bmc.sh") != -1:
                self.logger_debug("BMC does being upgraded" )
                return -1
        else:
            self.logger_debug("firmware(%s) does incorrect" %(firmware))
            return -1
        return upgrade_cmd

    def set_upgrade_info(self, firmware, flash, image):
        # determine whether the image file does empty
        if os.path.exists(image):
            if not os.path.getsize(image):
                self.logger_debug("image(%s) does empty" %(image))
                return -1
        else:
            self.logger_debug("image(%s) does not exists" %(image))
            return -1;
        # upgrade parameter judgment
        if flash != "master" and flash != "slave" and flash != "normal":
            self.logger_debug("flash(%s) does incorrect" %(flash))
            return -1

    def program_bmc_bios(self, firmware, flash, image):
        ret = self.set_upgrade_info(firmware, flash, image)
        if ret == -1:
            return -1
        #upgrade BMC/BIOS master slave or normal flash
        self.logger_debug("Begin: program %s %s, image(%s)" %(firmware, flash, image))
        upgrade_cmd = self.judge_bios_bmc_being_upgrade(firmware, flash, image)
        if upgrade_cmd == -1:
            return -1
        upgrade_log, ret = platcomutil.run_shell_cmd(upgrade_cmd)
        if ret:
            self.logger_debug("Execute command(%s) failed" %(upgrade_cmd))
            return -1
        upgrade_result = upgrade_log.strip('\n')
        self.logger_debug("upgrade program %s %s, image(%s) %s" %(firmware, flash, image, upgrade_result))
        if upgrade_result == "success":
            return 0
        return -1

    def split_cpld_name(self, names, files):
        #split cpld name
        cpld_names=""
        cpld_files = ""
        #adjust cpld order
        cpld_adjust="MAC_MISC_CPLD".lower()
        if cpld_adjust in names:
            cpld_index = names.index(cpld_adjust)
            names.insert(0, names.pop(cpld_index))
            files.insert(0, files.pop(cpld_index))

        fullproductname_path = "/etc/device/fullproductname"
        check_cpu_board_cpld_cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " get_current_cpu_board_cpld_type"
        get_fullproductname_cmd = "cat %s" % fullproductname_path
        # ret 0: CPU_BOARD_CPLD; else: CPU_BOARD_CPLD2
        check_log, ret = platcomutil.run_shell_cmd(check_cpu_board_cpld_cmd)
        fullproductname, cat_ret = platcomutil.run_shell_cmd(get_fullproductname_cmd)
        for i in range(len(files)):
            if names[i] == "CPU_BOARD_CPLD" and ret != 0:
                self.logger_debug("%s does not match CPU_BOARD_CPLD2, and ignore it" %(names[i]))
                continue
            if names[i] == "CPU_BOARD_CPLD2" and ret == 0:
                self.logger_debug("%s does not match CPU_BOARD_CPLD, and ignore it" %(names[i]))
                continue
            if names[i] == "CPU_BOARD_CPLD-FAN" and \
                ("-L-RJ" in fullproductname or "-LC-RJ" in fullproductname or "-LD-RJ" in fullproductname):
                self.logger_debug("No %s in liquid device, and ignore it" %(names[i]))
                continue
            if len(cpld_files) == 0:
                cpld_names = names[i]
                cpld_files = files[i]
            else:
                cpld_names = cpld_names + ":" + names[i]
                cpld_files = cpld_files + ":" + files[i]
        return cpld_names.upper(), cpld_files

    def program_cpld(self, names, files):
        """
        Program CPLD

        @param names List of CPLD/FPGA names
        @param files List of refresh files for CPLD/FPGA

        @return 0 on success, -1 for failure
        """
        if len(names) != len(files):
            self.logger_debug("names and files does not match")
            return -1;
        # Determine whether CPLD program has being upgraded
        cmd_log_firmware, ret = platcomutil.run_shell_cmd("ps | grep firmware_upgrade_ispvme")
        cmd_log_refresh, ret = platcomutil.run_shell_cmd("ps | grep program_cpld")
        if cmd_log_refresh.find("program_cpld.sh") != -1 or cmd_log_firmware.find("cpld") != -1:
            self.logger_debug("CPLD program does being upgraded")
            return -1
        # Upgrade CPLD program
        cpld_names, cpld_files = self.split_cpld_name(names, files)
        upgrade_cmd = PROGRAM_CPLD_PATH + cpld_names + " " +cpld_files
        cmd_log, ret = platcomutil.run_shell_cmd(upgrade_cmd)
        if ret:
            self.logger_debug("upgrade CPLD program failed" )
            return -1
        # Judge upgrade CPLD program result
        if os.path.exists(UPGRADE_CPLD_PROGRAM_RESULT):
            cmd_result_log, err = self.read_file(UPGRADE_CPLD_PROGRAM_RESULT)
            if err:
                self.logger_debug("read upgrade cpld result file %s failed" %(UPGRADE_CPLD_PROGRAM_RESULT))
                return -1
            if cmd_result_log.strip('\n') == "DONE":
                self.logger_debug("upgrade CPLD program result=%s" %(cmd_result_log))
                return 0
            else:
                self.logger_debug("upgrade CPLD program failed, result=%s" %(cmd_result_log) )
                return -1
        self.logger_debug("upgrade cpld result file %s does not exist" %(UPGRADE_CPLD_PROGRAM_RESULT))
        return -1

    def refresh_firmware(self, names, files):
        # Determine whether CPLD\BIOS\FPGA refresh has being upgraded
        cmd_log_firmware, ret = platcomutil.run_shell_cmd("ps | grep firmware_upgrade_ispvme")
        cmd_log_refresh, ret = platcomutil.run_shell_cmd("ps | grep refresh_fw")
        if cmd_log_refresh.find("refresh_fw.sh") != -1:
            self.logger_debug(r"CPLD\BIOS\FPGA refresh does being upgraded")
            return -1
        if len(names) != len(files):
            self.logger_debug("names and files does not match")
            return -1;
        for i in range(len(names)):
            if names[i].lower() == "fpga":
                fpga_index = names.index("fpga")
                files[fpga_index] = "/tmp/fpga_transfr_bmc"
            if names[i].lower() == "bios":
                if self.get_bios_capability() == 0:
                    self.logger_debug("cpu arch is arm, unsupport operation")
                    return -1
                bios_index = names.index("bios")
                files[bios_index] = "/tmp/bios_transfr_bmc"
        cpld_names, cpld_files = self.split_cpld_name(names, files)
        # Upgrade CPLD\BIOS\FPGA refresh
        upgrade_cmd = REFRESH_CPLD_PATH + cpld_names + " " +cpld_files
        self.logger_debug("run refresh cmd (%s)"%upgrade_cmd )
        cmd_log, ret = platcomutil.run_shell_cmd(upgrade_cmd)
        if ret:
            self.logger_debug(r"upgrade CPLD\BIOS\FPGA refresh failed (%s)"%upgrade_cmd )
            return -1
        # Judge upgrade CPLD\BIOS\FPGA result
        if os.path.exists(UPGRADE_CPLD_REFRESH_RESULT ):
            cmd_result_log, err = self.read_file(UPGRADE_CPLD_REFRESH_RESULT )
            if err:
               self.logger_debug("read upgrade cpld result file %s failed" %(UPGRADE_CPLD_REFRESH_RESULT ))
               return -1
            if cmd_result_log.strip('\n') == "DONE":
                self.logger_debug(r"upgrade CPLD\BIOS\FPGA result=%s" %(cmd_result_log))
                return 0
            else:
                self.logger_debug(r"upgrade CPLD\BIOS\FPGA result=%s" %(cmd_result_log))
                return -1
        self.logger_debug("upgrade cpld result file %s does not exist" %(UPGRADE_CPLD_REFRESH_RESULT ))
        return -1

    def judge_fw_channel_exist(self, type, show_mtd = False):
        """
        judge other fw channel is exist
        when upgrade fpga/mac/5387/bios
        @param type: fpga/mac/5387/bios
        show_mtd: is need to show mtd or not
        @return True for exist, False for not exist.
        """
        param = type
        if show_mtd == True:
            param = type + " show_mtd"
        fw_cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " judge_fw_channel_exist " + param
        cmd_log, ret = platcomutil.run_shell_cmd(fw_cmd)
        #0: fw channel not exist !0: exist
        if ret != 0:
            self.logger_debug("judge fw channel,  result: %s" % cmd_log)
            return True
        return False

    def touch_fw_lock_file(self):
        """
        touch fw upgrade lock file
        @return 0 for succ, -1 for failed.
        """
        lock_cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " fw_upgrade_lock"
        cmd_log, ret = platcomutil.run_shell_cmd(lock_cmd)
        if ret:
            self.logger_debug("touch fw upgrade lock file failed, result: %s" % cmd_log)
            return -1
        return 0

    def remove_fw_lock_file(self):
        """
        remove fw upgrade lock file
        @return 0 for succ, -1 for failed.
        """
        lock_cmd = AST_FUNC_SOURCE + AST_FUNC_CALL + " fw_upgrade_unlock"
        cmd_log, ret = platcomutil.run_shell_cmd(lock_cmd)
        if ret:
            self.logger_debug("remove fw upgrade lock file failed, result: %s" % cmd_log)
            return -1
        return 0

    def add_lock(self):
        """
        touch fw upgrade lock file, judge fw channel is exist or not
        @return 0 for succ, -1 for failed.
        """
        if self.touch_fw_lock_file() != 0:
            self.logger_debug("touch fw upgrade lock file failed")
            return -1
        if self.judge_fw_channel_exist("all") == True:
            self.logger_debug("fw channel exist")
            self.remove_fw_lock_file()
            return -1
        return 0

    def remove_lock(self):
        """
        remove fw upgrade lock file, judge fw channel is exist or not
        """
        if self.remove_fw_lock_file() != 0:
            self.logger_debug("touch fw upgrade lock file failed")
