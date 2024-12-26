#!/usr/bin/env python
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import subprocess
import os
import sys
import re

DATA_COLLECT_COMPLETE_MARK = "DONE"

# hex convert to binary
def hex_to_bin_bit(ret_out, name):
    try:
        bin_bit = ""
        if len(ret_out) == 2 or len(ret_out) == 4 or len(ret_out) == 8:
            for k in ret_out:
                ret = int(k, 16)
                ret_value = '{:08b}'.format(ret)
                bin_bit = bin_bit + ret_value[::-1]
        else:
            print("%s : no data(%s) need to convert to binary" % (name, ret_out))
            exit()
        return bin_bit
    except Exception as e:
        print("hex convert to binary failed : " + str(e))
        exit()

# MCE:
# read B1:D30:F2 offset: 0xEC, to verify Caterr err
def parse_mce_D1734_err_type(data):
    """
    bit31:CATERR
    bit30:IERR
    bit29:MCERR
    bit28:CATERR_INTERNAL
    bit27:IERR_INTERNAL
    bit26:MCERR_INTERNAL
    bit24:MSMI_MCP_SMBUS
    bit23:MSMI
    bit22:MSMI_IERR
    bit21:MSMI_MCERR
    bit20:MSMI_INTERNAL
    bit19:MSMI_IERR_INTERNAL
    bit18:MSMI_MCERR_INTERNAL
    """
    output = ""
    try:
        dict_err = {31 : "CATERR : ", 30 : "IERR : ", 29 : "MCERR : ",
                    28 : "CATERR_INTERNAL : ", 27 : "IERR_INTERNAL : ",
                    26 : "MCERR_INTERNAL : ", 24 : "MSMI_MCP_SMBUS : ",
                    23 : "MSMI : ", 22 : "MSMI_IERR : ", 21 : "MSMI_MCERR : ",
                    20 : "MSMI_INTERNAL : ", 19 : "MSMI_IERR_INTERNAL : ",
                    18 : "MSMI_MCERR_INTERNAL : "
                }
        key = "B31D30F2Addrec"
        if (key in data):
            value_str = data[key].split(" ")
            tmp_value = hex_to_bin_bit(value_str, key)
            for k in dict_err:
                if int(tmp_value[k], 2):
                    output = output + dict_err[k]
            if len(output) > 0:
                output = "%s: %s: " % (key, joint_addr(value_str)) + output
        return output
    except Exception as e:
        print("Resolve CPU type error failed : " + str(e))

# MCE: parse MSCOD bit 16-31 D1734
def parse_core_mc_mscod_D1734(ret_value, mc, dict):
    output = ""
    try:
        mc_list = ["MC0", "MC1", "MC2", "MC3", "MC6", "MC13", "CHA0"]
        if mc in mc_list:
            tmp_value = int(ret_value[16:32][::-1], 2)
            tmp_ret = dict[mc]["MSCOD"].get(tmp_value)
            if tmp_ret != None:
                output = output + "MSCOD : " + tmp_ret + " : "
        if mc == "MC4":
            tmp_value = int(ret_value[24:32][::-1], 2)
            tmp_put = dict[mc]["MSEC_FW"].get(tmp_value)
            if tmp_put != None:
                output = output + "MSEC_FW : " + tmp_put + " : "
            tmp_value = int(ret_value[20:24][::-1], 2)
            if tmp_value:
                tmp_ret = dict[mc]["MSEC_HW"].get(tmp_value)
                if tmp_ret != None:
                    output = output + "MSEC_HW : " + tmp_ret + " : "
            tmp_value = int(ret_value[16:20][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MSEC_UC"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MSEC_UC : " + tmp_result + " : "
        if mc == "MC12":
            tmp_value = int(ret_value[26][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MSCODRESETPREPFAIL"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MSCODRESETPREPFAIL : " + tmp_result + " : "
            tmp_value = int(ret_value[24:26][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MSCODDDRTYPE"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MSCODDDRTYPE : " + tmp_result + " : "
            tmp_value = int(ret_value[16:24][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MSCOD"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MSCOD : " + tmp_result + " : "
        return output
    except Exception as e:
        output = output + "Resolve MSCOD failed: %s" % str(e)
        print(output)

# MCE: parse MCACOD bit 0-15 for D1734
def parse_core_mc_mcacod_D1734(ret_value, mc, dict):
    output = ""
    try:
        mc_list = ["MC1", "MC2", "MC4", "MC6"]
        mc_list2= ["MC12", "MC13"] #两个bank mcacod定义相同
        if mc in mc_list:
            tmp_value = int(ret_value[0:16][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MCACOD"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MCACOD : " + tmp_result + " : "
        elif mc in mc_list2:
            tmp_value = int(ret_value[0:16][::-1], 2)
            if tmp_value:
                tmp_ret = dict[mc]["MCACOD"].get(tmp_value)
                if tmp_ret != None:
                    output = output + "MCACOD : " + tmp_ret + " : "
            tmp_value = int(ret_value[7:16][::-1], 2)
            if tmp_value:
                tmp_ret = dict[mc]["MCACOD-1"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[4:7][::-1], 2)
            if tmp_value:
                tmp_ret = dict[mc]["MCACOD-2"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[0:4][::-1], 2)
            if tmp_value:
                tmp_ret = dict[mc]["MCACOD-3"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
        if mc == "MC0":
            tmp_value = int(ret_value[0:11][::-1], 2)
            if tmp_value:
                tmp_result = dict[mc]["MCACOD"].get(tmp_value)
                if tmp_result != None:
                    output = output + "MCACOD : " + tmp_result + " : "
        elif mc == "MC3":
            tmp_value = int(ret_value[0:16][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCACOD-4"].get(tmp_value)
                if tmp_ret != None:
                    output = output + "MCACOD : " + tmp_ret + " : "
            tmp_value = int(ret_value[8], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCACOD"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[4:8][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCACOD-1"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[2:4][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCACOD-2"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[0:2][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCACOD-3"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
        elif mc == "CHA0":
            tmp_value = int(ret_value[0:16][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCCOD-4"].get(tmp_value)
                if tmp_ret != None:
                    output = output + "MCCOD : " + tmp_ret + " : "
            tmp_value = int(ret_value[12], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCCOD"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[4:8][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCCOD-1"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[2:4][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCCOD-2"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
            tmp_value = int(ret_value[0:2][::-1], 2)
            if tmp_value:
                tmp_ret =dict[mc]["MCCOD-3"].get(tmp_value)
                if tmp_ret != None:
                    output = output + tmp_ret + " : "
        else:
            output = output + "%s Unknown : " % mc
        return output
    except Exception as e:
        output = output + "Resolve mcacod failed: %s" % str(e)
        print(output)

#MCE : joint misc| addr bit 0-64
def joint_addr(ret_out):
    output = "0x"
    for k in ret_out[::-1]:
        output = output + "%02x" % (int(k, 16))
    return output

def parse_mce_misc_mc0_addr_D1734(data, name, mc_name):
    # ADDRESS_MODE : bit(8:6)
    # IFU_ADDR_LSB : bit(5:0)
    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        dict = {"000": "Segment Offset", "001": "Linear Addree", "010": "Physical Address",
                "011": "Memory Address", "111": "Generic"}
        ret = ret_value[6:9][::-1]
        if ret in dict:
            output = "ADDRESS_MODE(8:6) : " + dict[ret] + " : "
        if int(ret_value[0:6][::-1], 2):
            output = output + "IFU_ADDR_LSB(5:0) : " + ret_value[0:6][::-1]
        return output
    except Exception as e:
        print("Parse mce misc %s returned: %s" % mc_name, str(e))

def parse_mce_misc_channel_0_5_addr_D1734(data, name):
    """
    bit[63:62] : "ENH_MCA_AVAIL1"
    bit[56:61] : "TORFSM"
    bit[55:45] : "ORIGREQ"
    bit[43:39] : "TORID"
    bit[38:28] : "OPCODE"
    bit[27] : "RETRY"
    bit[26] : "INCLUSIVE"
    bit[25] : "MONITORHIT"
    bit[24] : "RSPCNFLT_P"
    bit[23] : "CACHEABLE"
    bit[22:19] : "CACHESTATE"
    bit[18:14] : "WAY"
    bit[13] : "ALLOWSNOOPP"
    bit[12] : "GOP"
    bit[11] : "VICP"
    bit[10:9] : "ENH_MCA_AVAIL0"
    bit[8:6] : "ADDRMODE"
    bit[5:0] : ADDRLSB
    """

    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        if int(ret_value[62:64][::-1], 2):
            output = "ENH_MCA_AVAIL1(62:63) : " + ret_value[62:64][::-1] + " : "
        if int(ret_value[56:62][::-1], 2):
            output = output + "TORFSM(56:61) : " + ret_value[56:62][::-1] + " : "
        if int(ret_value[45:56][::-1], 2):
            output = output + "ORIGREQ(45:55) : " + ret_value[45:56][::-1] + " : "
        if int(ret_value[39:44][::-1], 2):
            output = output + "TORID(39:43) : " + ret_value[39:44][::-1] + " : "
        if int(ret_value[28:39][::-1], 2):
            output = output + "OPCODE(28:38) : " + ret_value[28:39][::-1] + " : "
        if int(ret_value[27], 2):
            output = output + "RETRY(27) : " + ret_value[27] + " : "
        if int(ret_value[26], 2):
            output = output + "INCLUSIVE(26) : " + ret_value[26] + " : "
        if int(ret_value[25], 2):
            output = output + "MONITORHIT(25) : " + ret_value[25] + " : "
        if int(ret_value[24], 2):
            output = output + "RSPCNFLT_P(24) : " + ret_value[24] + " : "
        if int(ret_value[23], 2):
            output = output + "CACHEABLE(23) : " + ret_value[23] + " : "
        if int(ret_value[19:23][::-1], 2):
            output = output + "CACHESTATE(19:22) : " + ret_value[19:23][::-1] + " : "
        if int(ret_value[14:19][::-1], 2):
            output = output + "WAY(14:18) : " + ret_value[14:19][::-1] + " : "
        if int(ret_value[13][::-1], 2):
            output = output + "ALLOWSNOOPP(13) : " + ret_value[13][::-1] + " : "
        if int(ret_value[12][::-1], 2):
            output = output + "GOP(12) : " + ret_value[12][::-1] + " : "
        if int(ret_value[11][::-1], 2):
            output = output + "GOP(11) : " + ret_value[11][::-1] + " : "
        if int(ret_value[9:11][::-1], 2):
            output = output + "ENH_MCA_AVAIL0(9:10) : " + ret_value[9:11][::-1] + " : "
        output = output + parse_mce_misc_mc0_addr_D1734(data, name, "CHA0-5")
        return output
    except Exception as e:
        print("Parse mce misc CHA0-5 Exception returned: %s" % str(e))

def parse_mce_misc_mc13_14_addr_D1734(data, name):
    """
    bit[63:9] : "EXTRA_ERR_INFO"
    bit[8:6] : "ADDRMODE"
    bit[5:0] : "ADDRLSB"
    """

    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        extra_err = int(ret_value[9:64][::-1], 2)
        if extra_err:
            output = output + "EXTRA_ERR_INFO(9:63) : " + hex(extra_err) + " : "
        output = output + parse_mce_misc_mc0_addr_D1734(data, name, "mc13-14")
        return output
    except Exception as e:
        print("Parse mce misc mc13-14 Exception returned: %s" % str(e))
        
def parse_mce_misc_mc12_addr_D1734(data, name):
    """
    bit[63] : "MIRRORFAILOVER"
    bit[62] : "MIRRORCORRERR"
    bit[60:61] : "DATAERRORCHUNK"
    bit[59] : "MCCMDMIRRFO"
    bit[58] : "MCCMDMIRRSEC"
    bit[57] : "MCCMDMIRRREGION"
    bit[51:50] : "MCCMDCHNL"
    bit[49:46] : "MCCMDMEMREGION"
    bit[45:40] : "MCCMDOPCODE"
    bit[39] : "MCCMDVLD"
    bit[38] : "SMIAD"
    bit[37:35] : "SMIMSGCLASS"
    bit[34:31] : "SMIOPCODE"
    bit[29:21] : "TRKID"
    bit[20:11] : "ERRORTYPE"
    bit[8:6] : "ADDRMODE"
    bit[5:0] : "ADDRLSB"
    """
    dict_eq = {"000000": "MEMRD", "000001": "MEMSPECRD", "000010": "MEMRDDATA", "000100": "MEMRDXTOS",
                "000101": "MEMRDXTOI", "000110": "MEMRDXTOA", "001000": "MEMINV", "001001": "MEMINVXTOI",
                "001010": "MEMINVXTOA", "001100": "MEMINVITOX", "010000": "MEMWR", "010011": "MEMWRNI",
                "010100": "MEMWRPTL",  "010101": "PATROL", "011011": "MEMWRFLUSH", "101000": "FMFILLRD",
                "101110" : "DEALLOCSBRD", "101111" : "DEALLOCSBPF", "110000": "DIRUPD", "110001": "NMFILLWR",
                "110011" : "FMWR4NM", "110111": "FMWRPTL4NM", "111000": "FMEVICTWR", "111110": "DEALLOCSBWR",
                "111111" : "DEALLOCSBALL"
        }

    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        if int(ret_value[63], 2):
            output = "MIRRORFAILOVER(63) : " + ret_value[63] + " : "
        if int(ret_value[62], 2):
            output = output + "MIRRORCORRERR(62) : " + ret_value[63] + " : "
        if int(ret_value[60:62][::-1], 2):
            output = output + "DATAERRORCHUNK(60:61) : " + ret_value[60:62][::-1] + " : "
        if int(ret_value[59], 2):
            output = output + "MCCMDMIRRFO(59) : " + ret_value[59] + " : "
        if int(ret_value[58], 2):
            output = output + "MCCMDMIRRSEC(58) : " + ret_value[58] + " : "
        if int(ret_value[57], 2):
            output = output + "MCCMDMIRRREGION(57) : " + ret_value[57] + " : "
        if int(ret_value[50:52][::-1], 2):
            output = output + "MCCMDCHNL(50:51) : " + ret_value[50:52][::-1] + " : "
        if int(ret_value[46:50][::-1], 2):
            output = output + "MCCMDMEMREGION(46:49) : " + ret_value[46:50][::-1] + " : "
        ret = ret_value[40:46][::-1]
        if ret in dict_eq:
            output = output + "MCCMDOPCODE(40:45) : " + dict_eq[ret] + " : "
        else:
            output = output + "MCCMDOPCODE(40:45) : " + ret_value[40:46][::-1] + " : "
        if int(ret_value[39], 2):
            output = output + "MCCMDVLD(39) : " + ret_value[39] + " : "
        if int(ret_value[38], 2):
            output = output + "SMIAD(38) : " + ret_value[38] + " : "
        if int(ret_value[35:38][::-1], 2):
            output = output + "SMIMSGCLASS(35:37) : " + ret_value[35:38][::-1] + " : "
        if int(ret_value[31:35][::-1], 2):
            output = output + "SMIOPCODE(31:34) : " + ret_value[31:35][::-1] + " : "
        if int(ret_value[21:30][::-1], 2):
            output = output + "TRKID(21:29) : " + ret_value[21:30][::-1] + " : "
        if int(ret_value[11:21][::-1], 2):
            output = output + "ERRORTYPE(11:21) : " + ret_value[11:21][::-1] + " : "
        output = output + parse_mce_misc_mc0_addr_D1734(data, name, "mc12")
        return output
    except Exception as e:
        print("Parse mce misc mc12 Exception returned: %s" % str(e))

def parse_mce_misc_mc9_10_addr_D1734(data, name):
    """"
    bit63 : MC logs-second correctable error
    bit62 : MC logs-first correctable error
    bit[55:51] : MC logs the second error failing rank
    bit[50:46] : MC logs the first error failing rank
    bit[45:30] : MC logs the second error bit mask here
    bit[29:14]: MC logs the first error bit mask here
    bit[13:9]: MCWrDataPar error or MCWrBEPar error
    bit[8:6]: ADDR_MODE- 000: Segment Offset
                         001: Linear Address
                         010: Physical (system) Address
                         011: Memory Address
                         111: Generic
    bit[5:0] : REC_ERR_LSB
    """
    dict_addr_mode = {"000" : "Segment Offset : ", "001": "Linear Address : ",
                      "010" : "Physical (system) Address : ", "011": "Memory Address : ",
                      "111" : "Generic : "}
    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        if int(ret_value[63], 2):
            output = "EXTRA_ERR_INFO(63:9) : " + "MC logs-second correctable error : "
            if int(ret_value[51:56][::-1], 2):
                output = output + "MC logs the second error failing rank : " + \
                    ret_value[51:56][::-1] + " : "
            if int(ret_value[30:46][::-1], 2):
                output = output + "MC logs the second error bit mask here : " + \
                    ret_value[30:46][::-1] + " : "
        if int(ret_value[62], 2):
            output = "EXTRA_ERR_INFO : " + "MC logs-first correctable error : "
            if int(ret_value[51:56][::-1], 2):
                output = output + "MC logs the first error failing rank : " + \
                    ret_value[51:56][::-1] + " : "
            if int(ret_value[14:30][::-1], 2):
                output = output + "MC logs the first error bit mask here : " + \
                    ret_value[14:30][::-1] + " : "
        if int(ret_value[9:14][::-1], 2):
            output = output + "MCWrDataPar error or MCWrBEPar error : " + \
                ret_value[9:14][::-1] + ":"
        ret = ret_value[6:9][::-1]
        if ret in dict_addr_mode:
            output = output + "ADDR_MODE(6:8): " + dict_addr_mode[ret]
        if int(ret_value[0:6][::-1], 2):
            output = output + "REC_ERR_LSB(0:5) : " + ret_value[0:6][::-1] + " : "
        return output
    except Exception as e:
        print("Parse mce misc mc9-10 Exception returned: %s" % str(e))

def parse_mce_misc_mc6_addr_D1734(data, name):
    """
    bit 31: 24 - BUS_LOG
    bit 23: 19 - DEVICE_LOG
    bit 18: 16 - FUNCTION_LOG
    bit 15: 13 - SEGMENT_LOG
    """
    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        ret = int(ret_value[24:32][::-1], 2)
        if ret:
            output = "BUS_LOG(24:31) : " + str(ret) + " : "
        ret = int(ret_value[19:24][::-1], 2)
        if ret:
            output = output + "DEVICE_LOG(19:24) : " + str(ret) + " : "
        ret = int(ret_value[16:19][::-1], 2)
        if ret:
            output = output + "FUNCTION_LOG(16:18) : " + str(ret) + " : "
        ret = int(ret_value[13:16][::-1], 2)
        if ret:
            output = output + "SEGMENT_LOG(13:15) : " + str(ret) + " : "
        return output
    except Exception as e:
        print("Parse mce misc mc6 Exception returned: %s" % str(e))

def parse_mce_misc_mc4_addr_D1734(data, name):
    """
    bit 35: 16 - ERROR_ADDRESS
    """
    output = ""
    try:
        ret_value = hex_to_bin_bit(data, name)
        ret = int(ret_value[16:36][::-1], 2)
        if ret:
            output = "ERROR_ADDRESS(35:16) : " + str(ret) + " : "
        return output
    except Exception as e:
        print("Parse mce misc mc4 Exception returned: %s" % str(e))

def parse_mce_misc_addr_D1734(data, name):
    global g_mce_type
    # MC2 - Reserved, does not need to parse
    core_mc0 = ["CORE0MC0MISCTHREAD0", "CORE1MC0MISCTHREAD0", "CORE2MC0MISCTHREAD0", "CORE3MC0MISCTHREAD0", "CORE4MC0MISCTHREAD0", "CORE5MC0MISCTHREAD0", "CORE6MC0MISCTHREAD0", "CORE7MC0MISCTHREAD0"]
    core_mc1 = ["CORE0MC1MISCTHREAD0", "CORE1MC1MISCTHREAD0", "CORE2MC1MISCTHREAD0", "CORE3MC1MISCTHREAD0", "CORE4MC1MISCTHREAD0", "CORE5MC1MISCTHREAD0", "CORE6MC1MISCTHREAD0", "CORE7MC1MISCTHREAD0"]
    core_mc3 = ["CORE0MC3MISCTHREAD0", "CORE1MC3MISCTHREAD0", "CORE2MC3MISCTHREAD0", "CORE3MC3MISCTHREAD0", "CORE4MC3MISCTHREAD0", "CORE5MC3MISCTHREAD0", "CORE7MC3MISCTHREAD0", "CORE7MC3MISCTHREAD0"]
    core_mc4 = ["CORE0MC4MISCTHREAD0"]
    core_mc6 = ["CORE0MC6MISCTHREAD0"]
    core_mc7 = ["CORE0MC7MISCTHREAD0"]
    core_mc9_10 = ["CORE0MC9MISCTHREAD0", "CORE0MC10MISCTHREAD0"]
    core_mc12_16 = ["CORE0MC12MISCTHREAD0", "CORE0MC16MISCTHREAD0"]
    core_mc13_14_15 = ["CORE0MC13MISCTHREAD0", "CORE0MC14MISCTHREAD0", "CORE0MC15MISCTHREAD0"]
    core_mc17_18_19 = ["CORE0MC17MISCTHREAD0", "CORE0MC18MISCTHREAD0", "CORE0MC19MISCTHREAD0"]
    channel_0_5 = ["CHA0MC_MISC", "CHA1MC_MISC", "CHA2MC_MISC", "CHA3MC_MISC", "CHA4MC_MISC", "CHA5MC_MISC"]
    output = ""
    try:
        if name in core_mc0:
            output = parse_mce_misc_mc0_addr_D1734(data, name, "mc0")
        elif name in core_mc1:
            output = parse_mce_misc_mc0_addr_D1734(data, name, "mc1")
        elif name in core_mc3:
            output = parse_mce_misc_mc0_addr_D1734(data, name, "mc3")
        elif name in core_mc4:
            output = parse_mce_misc_mc4_addr_D1734(data, name)
        elif name in core_mc6:
            output = parse_mce_misc_mc6_addr_D1734(data, name)
        elif name in core_mc9_10:
            output = parse_mce_misc_mc9_10_addr_D1734(data, name)
        elif name in core_mc12_16:
            output = parse_mce_misc_mc12_addr_D1734(data, name)
        elif name in core_mc13_14_15:
            output = parse_mce_misc_mc13_14_addr_D1734(data, name)
        elif name in channel_0_5:
            output = parse_mce_misc_channel_0_5_addr_D1734(data, name)
        else:
            output = "%s Unknown : " % name
        return output
    except Exception as e:
        print("Parse mce misc addr Exception returned: %s" % str(e))

#Step-1 : name = val, to judge bit63, if be 0 invalid does not parse, if be 1 valid
#Step-2 : parse lsb bite 0-31
#Step-3 : name = ADDRV bit 58
#Step-4 : name = MISCV bit 59
#Step-5 : parse ctl2
def parse_bank_log_D1734(data, ret_out, sublist, name):
    output = ""
    ret = 0
    try:
        ret_value = hex_to_bin_bit(ret_out, name)
        if int(ret_value[63], 2) == 0:
            ret = 1
            return ret, output

        output = parse_mce_bank_lsb_D1734(ret_value, name) + "\n"
        for subname in sublist:
            if (subname not in data) or (len(data[subname].split(" ")) == 0):
                output = output + subname + ": does not exist, or no data\n"
                continue
            ret_out = data[subname].split(" ")
            if "ADDR" in subname and int(ret_value[58], 2):
                output = output + "%s : %s\n" % (subname, joint_addr(ret_out))
            elif "MISC" in subname and int(ret_value[59], 2):
                output = output + "%s : %s : %s\n" % \
                    (subname, joint_addr(ret_out), parse_mce_misc_addr_D1734(ret_out, subname))
            elif "CTL2" in subname:
                output = output + "%s : %s : %s\n" % \
                    (subname, joint_addr(ret_out), parse_mce_mc_ctl2_D1734(data, subname))
            else:
                output = output + "%s : %s : %s\n" % \
                    (subname, joint_addr(ret_out), "unknown and unparsed")
        return ret, output
    except Exception as e:
        print("Parse bank log Exception returned: %s" % str(e))

# MCE: parse mce msb bit 38-63
def parse_mce_bank_msb_D1734(data, list_mc):
    """
    bit63: Indicates (when set) that the information within the IA32_MC0_STATUS register is valid
    if invalid does not to parse
    bit62: "OVER"
    bit61: "UC"
    bit60: "EN"
    bit59: "MISCV"
    bit58: "ADDRV"
    bit57: "PCC"
    bit56: "S"
    bit55: "AR"
    bit54-53: "CorrErrorStatusInd" 00:No Tracking, 01:Green, 10: Yellow, 11: Reserved
    bit53-38: CORR_ERR_COUNT Correctable error count.This is not supported for the PCU-----CORE0MC4
    
    """
    output = ""
    output_tmp = ""
    bank_name = {
                    "CORE0MC0STATUSTHREAD0"  : ["CORE0MC0ADDRTHREAD0", "CORE0MC0MISCTHREAD0", "CORE0MC0CTL2THREAD0"],
                    "CORE0MC1STATUSTHREAD0"  : ["CORE0MC1ADDRTHREAD0", "CORE0MC1MISCTHREAD0", "CORE0MC1CTL2THREAD0"],
                    "CORE0MC2STATUSTHREAD0"  : ["CORE0MC2ADDRTHREAD0", "CORE0MC2MISCTHREAD0", "CORE0MC2CTL2THREAD0"],
                    "CORE0MC3STATUSTHREAD0"  : ["CORE0MC3ADDRTHREAD0", "CORE0MC3MISCTHREAD0", "CORE0MC3CTL2THREAD0"],
                    "CORE1MC0STATUSTHREAD0"  : ["CORE1MC0ADDRTHREAD0", "CORE1MC0MISCTHREAD0", "CORE1MC0CTL2THREAD0"],
                    "CORE1MC1STATUSTHREAD0"  : ["CORE1MC1ADDRTHREAD0", "CORE1MC1MISCTHREAD0", "CORE1MC1CTL2THREAD0"],
                    "CORE1MC2STATUSTHREAD0"  : ["CORE1MC2ADDRTHREAD0", "CORE1MC2MISCTHREAD0", "CORE1MC2CTL2THREAD0"],
                    "CORE1MC3STATUSTHREAD0"  : ["CORE1MC3ADDRTHREAD0", "CORE1MC3MISCTHREAD0", "CORE1MC3CTL2THREAD0"],
                    "CORE2MC0STATUSTHREAD0"  : ["CORE2MC0ADDRTHREAD0", "CORE2MC0MISCTHREAD0", "CORE2MC0CTL2THREAD0"],
                    "CORE2MC1STATUSTHREAD0"  : ["CORE2MC1ADDRTHREAD0", "CORE2MC1MISCTHREAD0", "CORE2MC1CTL2THREAD0"],
                    "CORE2MC2STATUSTHREAD0"  : ["CORE2MC2ADDRTHREAD0", "CORE2MC2MISCTHREAD0", "CORE2MC2CTL2THREAD0"],
                    "CORE2MC3STATUSTHREAD0"  : ["CORE2MC3ADDRTHREAD0", "CORE2MC3MISCTHREAD0", "CORE2MC3CTL2THREAD0"],
                    "CORE3MC0STATUSTHREAD0"  : ["CORE3MC0ADDRTHREAD0", "CORE3MC0MISCTHREAD0", "CORE3MC0CTL2THREAD0"],
                    "CORE3MC1STATUSTHREAD0"  : ["CORE3MC1ADDRTHREAD0", "CORE3MC1MISCTHREAD0", "CORE3MC1CTL2THREAD0"],
                    "CORE3MC2STATUSTHREAD0"  : ["CORE3MC2ADDRTHREAD0", "CORE3MC2MISCTHREAD0", "CORE3MC2CTL2THREAD0"],
                    "CORE3MC3STATUSTHREAD0"  : ["CORE3MC3ADDRTHREAD0", "CORE3MC3MISCTHREAD0", "CORE3MC3CTL2THREAD0"],
                    "CORE4MC0STATUSTHREAD0"  : ["CORE4MC0ADDRTHREAD0", "CORE4MC0MISCTHREAD0", "CORE4MC0CTL2THREAD0"],
                    "CORE4MC1STATUSTHREAD0"  : ["CORE4MC1ADDRTHREAD0", "CORE4MC1MISCTHREAD0", "CORE4MC1CTL2THREAD0"],
                    "CORE4MC2STATUSTHREAD0"  : ["CORE4MC2ADDRTHREAD0", "CORE4MC2MISCTHREAD0", "CORE4MC2CTL2THREAD0"],
                    "CORE4MC3STATUSTHREAD0"  : ["CORE4MC3ADDRTHREAD0", "CORE4MC3MISCTHREAD0", "CORE4MC3CTL2THREAD0"],
                    "CORE5MC0STATUSTHREAD0"  : ["CORE5MC0ADDRTHREAD0", "CORE5MC0MISCTHREAD0", "CORE5MC0CTL2THREAD0"],
                    "CORE5MC1STATUSTHREAD0"  : ["CORE5MC1ADDRTHREAD0", "CORE5MC1MISCTHREAD0", "CORE5MC1CTL2THREAD0"],
                    "CORE5MC2STATUSTHREAD0"  : ["CORE5MC2ADDRTHREAD0", "CORE5MC2MISCTHREAD0", "CORE5MC2CTL2THREAD0"],
                    "CORE5MC3STATUSTHREAD0"  : ["CORE5MC3ADDRTHREAD0", "CORE5MC3MISCTHREAD0", "CORE5MC3CTL2THREAD0"],
                    "CORE6MC0STATUSTHREAD0"  : ["CORE6MC0ADDRTHREAD0", "CORE6MC0MISCTHREAD0", "CORE6MC0CTL2THREAD0"],
                    "CORE6MC1STATUSTHREAD0"  : ["CORE6MC1ADDRTHREAD0", "CORE6MC1MISCTHREAD0", "CORE6MC1CTL2THREAD0"],
                    "CORE6MC2STATUSTHREAD0"  : ["CORE6MC2ADDRTHREAD0", "CORE6MC2MISCTHREAD0", "CORE6MC2CTL2THREAD0"],
                    "CORE6MC3STATUSTHREAD0"  : ["CORE6MC3ADDRTHREAD0", "CORE6MC3MISCTHREAD0", "CORE6MC3CTL2THREAD0"],
                    "CORE7MC0STATUSTHREAD0"  : ["CORE7MC0ADDRTHREAD0", "CORE7MC0MISCTHREAD0", "CORE7MC0CTL2THREAD0"],
                    "CORE7MC1STATUSTHREAD0"  : ["CORE7MC1ADDRTHREAD0", "CORE7MC1MISCTHREAD0", "CORE7MC1CTL2THREAD0"],
                    "CORE7MC2STATUSTHREAD0"  : ["CORE7MC2ADDRTHREAD0", "CORE7MC2MISCTHREAD0", "CORE7MC2CTL2THREAD0"],
                    "CORE7MC3STATUSTHREAD0"  : ["CORE7MC3ADDRTHREAD0", "CORE7MC3MISCTHREAD0", "CORE7MC3CTL2THREAD0"],
                    "CORE0MC4STATUSTHREAD0"  : ["CORE0MC4ADDRTHREAD0", "CORE0MC4MISCTHREAD0", "CORE0MC4CTL2THREAD0"],
                    "CORE0MC6STATUSTHREAD0"  : ["CORE0MC6ADDRTHREAD0", "CORE0MC6MISCTHREAD0", "CORE0MC6CTL2THREAD0"],
                    "CHA0MC_STATUS"  : ["CHA0MC_ADDR", "CHA0MC_MISC"],
                    "CHA1MC_STATUS"  : ["CHA1MC_ADDR", "CHA1MC_MISC"],
                    "CHA2MC_STATUS"  : ["CHA2MC_ADDR", "CHA2MC_MISC"],
                    "CHA3MC_STATUS"  : ["CHA3MC_ADDR", "CHA3MC_MISC"],
                    "CHA4MC_STATUS"  : ["CHA4MC_ADDR", "CHA4MC_MISC"],
                    "CHA5MC_STATUS"  : ["CHA5MC_ADDR", "CHA5MC_MISC"],
                    "CHA6MC_STATUS"  : ["CHA6MC_ADDR", "CHA6MC_MISC"],
                    "CHA7MC_STATUS"  : ["CHA7MC_ADDR", "CHA7MC_MISC"],
                    "CORE0MC11STATUSTHREAD0" : ["CORE0MC11ADDRTHREAD0", "CORE0MC11MISCTHREAD0", "CORE0MC11CTL2THREAD0"],
                    "CORE0MC12STATUSTHREAD0" : ["CORE0MC12ADDRTHREAD0", "CORE0MC12MISCTHREAD0", "CORE0MC12CTL2THREAD0"],
                    "CORE0MC13STATUSTHREAD0" : ["CORE0MC13ADDRTHREAD0", "CORE0MC13MISCTHREAD0", "CORE0MC13CTL2THREAD0"],
                    "CORE0MC14STATUSTHREAD0" : ["CORE0MC14ADDRTHREAD0", "CORE0MC14MISCTHREAD0", "CORE0MC14CTL2THREAD0"],
                    "CORE0MC15STATUSTHREAD0" : ["CORE0MC15ADDRTHREAD0", "CORE0MC15MISCTHREAD0", "CORE0MC15CTL2THREAD0"],
                    "CORE0MC16STATUSTHREAD0" : ["CORE0MC16ADDRTHREAD0", "CORE0MC16MISCTHREAD0", "CORE0MC16CTL2THREAD0"],
                }
    try:
        for name in list_mc:
            if (name in data) and (len(data[name].split(" ")) > 0):
                ret_out = data[name].split(" ")
                ret, output_tmp = parse_bank_log_D1734(data, ret_out, bank_name[name], name)
                if ret == 1:
                    continue
                if (output_tmp != None) and (len(output_tmp) > 0):
                    output = name + ": " + joint_addr(ret_out) + ": " + output_tmp
                    print(output)
            else:
                output = "%s does not exist" % name
                print(output)
    except Exception as e:
        print("Parse bank msb Exception returned: %s" % str(e))

#MCE: parse mce lsb bit 0-31
def parse_mce_bank_lsb_D1734(ret_value, name):
    """
    1.Each core of the CPU will have its own MC[0:3]
    2.Other MCS["MC4", "MC6", "MC9", "MC10", "MC11", "MC12", "MC13", "MC14"] are Shared
    MC0: bit31:16 - MSCOD bit 10:0 - MCACOD
    MC1: bit37:16 - MSCOD(只需要解析bit31:16) bit 15:0 - MCACOD 
    MC2: bit31:16 - MSCOD bit 15:0 - MCACOD
    MC3: bit31:16 - MSCOD bit 15:0 - MCACOD
    MC4: bit31:24 - MSEC_FW bit23:20 - MSEC_HW bit 19:16 - MSEC_UC bit 15:0 - MCACOD
    MC6: bit31:16 - MSCOD bit 15:0 - MCACOD
    MC9|MC10|MC11: bit31:16 - MSCOD bit15:0 - MCCOD CHA0-5
    MC12: bit26:MSCODFAILOVERWHILERESETPREP bit25:24: MSCODDDRTYPE 23:16 MSCOD bit15:0 - MCACOD
    MC13|MC14|MC15: bit31:16 - MSCOD bit15:0 - MCACOD
    """

    dict_mc_info = {"MC0": {"MSCOD": {0: "Internal Parity Error", 1: "Internal Parity Errors", 2: "Internal Parity Error", 3: "Internal Parity Error",
                                    4: "ICache Data Parity Error", 5: "ICache Tag Parity Error",
                                    6: "ITLB Parity Error", 7: "Internal Parity Error", 8: "Internal Parity Error",
                                    9: "Internal Error", 10: "Internal Error", 11: "Internal Error",
                                12: "Internal Parity Error", 13: "Internal Parity Error", 14: "Internal Error",
                                15: "Internal Error(AEDC)"},
                            "MCACOD": {5: "Internal Parity Error", 0x10: "TLB Errors:I.L0",
                                    0x150: "Cache Errors:IRD.I.L0", 0x406: "Internal Firmware Error", 
                                    0x40a: "AEDC Error"},
                        },
                    "MC1": {"MSCOD": {0: "Non-APIC Error Code", 0x10: "WBINVD Hitting Tag/Data Parity Error, ORxlat/ms \
                                        Load Hitting Poisoned Data (coming from MLC)", 0x11: "Internal Error",
                                        0x20: "APIC Error"},
                            "MCACOD": {0x0114: "Cache Errors: RD.D.L0", 0x0124: "Cache Errors: WR.D.L0",
                                    0x0134: "Cache Errors: DRD.D.L0", 0x0164: "Cache Errors: PREF.D.L0", 
                                    0x0174: "Cache Errors: EVICT.D.L0", 0x0184: "Cache Errors: SNOOP.D.L0",
                                    0x0401: "WB Access to APIC Memory", 0x0404: " Tag/Data Parity Error on APIC load /store"},
                        },
                    "MC2": {"MSCOD": {0: "Tag Parity Error", 1: "Data Parity Error",
                                        2: "Tag Parity Error", 3: "Data Parity Error"},
                            "MCACOD": {5: "Internal Parity Error", 0x0014: "TLB Errors:D.L0",
                                    0x0019: "TLB Errors:G.L1", 0x0406: "Internal Firmware Error"},
                        },
                    "MC3": {"MSCOD": {0x00C0: "Internal Error", 0x0080: " MLC Watchdog timer (3-strike) Error",
                                        0x0040: "IDI or SQ Parity Error", 0x0030: "Poisoned Data detected",
                                        0x0020: "Data Read Uncorrected error/prefetch Error", 
                                        0x0010: "Data Read Corrected error / prefetch Error",
                                        0x0008: "MESI State Uncorrected Error", 0x0004: "MESI State Corrected Error",
                                        0x0002: "Tag Uncorrected Error", 0x0001: "Tag Corrected Error"},
                            "MCACOD": {1: "Cache Hierarchy Error"},##bit[8]
                            "MCACOD-1": {0: "Generic Error", 1: "Generic Read", 2: "Generic Write",
                                            3: "Data Read", 4: "Data Write", 5: "Instruction Fetch",
                                            6: "Prefetch", 7: "Eviction", 8: "Snoop",
                                        }, ##bit[7-4]
                            "MCACOD-2" : {0: "Instruction", 1: "Data", 2: "Generic TT", 3: "Reserved TT"}, ##bit[3-2]
                            "MCACOD-3" : {0: "Level 0", 1: "Level 1", 2: "Level 2", 3: "Generic LL"}, ##bit[1-0]
                            "MCACOD-4" : {0x400: "Watchdog Timer (3-strike timeout) Error", 0x165: "Data Prefetch Errors",
                                        0x135: "Data Read Errors", 0x109: "Tag / MESI State Error"} ##bit[15-0]
                        },
                    "MC4": {"MSEC_FW": {0x0d: "MCA_LLC_BIST_ACTIVE_TIMEOUT", 0x0e: "MCA_DMI_TRAINING_TIMEOUT",
                                0x0f: "MCA_DMI_STRAP_SET_ARRIVAL_TIMEOUT;", 0x10: "MCA_DMI_CPU_RESET_ACK_TIMEOUT",
                                0x11: "MCA_MORE_THAN_ONE_LT_AGENT", 0x14: "MCA_INCOMPATIBLE_PCH_TYPE",
                                0x1e: "MCA_BIOS_RST_CPL_INVALID_SEQ", 0x1f: "MCA_BIOS_INVALID_PKG_STATE_CONFIG",
                                0x2d: "MCA_PCU_PMAX_CALIB_ERROR", 0x2e: "MCA_TSC100_SYNC_TIMEOUT",
                                0x3a: "MCA_GPSB_TIMEOUT", 0x3b: "MCA_PMSB_TIMEOUT", 0x3e: "MCA_IOSFSB_PMREQ_CMP_TIMEOUT",
                                0x40: "MCA_SVID_VCCIN_VR_ICC_MAX_FAILURE", 0x42: "MCA_SVID_VCCIN_VR_VOUT_FAILURE",
                                0x43: "MCA_SVID_CPU_VR_CAPABILITY_ERROR", 0x44: "MCA_SVID_CRITICAL_VR_FAILED",
                                0x45: "MCA_SVID_SA_ITD_ERROR", 0x46: "MCA_SVID_READ_REG_FAILED",
                                0x47: "MCA_SVID_WRITE_REG_FAILED", 0x4a: "MCA_SVID_PKGC_REQUEST_FAILED",
                                0x4b: "MCA_SVID_IMON_REQUEST_FAILED", 0x4c: "MCA_SVID_ALERT_REQUEST_FAILED",
                                0x4d: "MCA_SVID_MCP_VR_RAMP_ERROR", 0x56: "MCA_FIVR_PD_HARDERR",
                                0x58: "MCA_WATCHDOG_TIMEOUT_PKGC_SLAVE", 0x59:"MCA_WATCHDOG_TIMEOUT_PKGC_MASTER",
                                0x5a: "MCA_WATCHDOG_TIMEOUT_PKGS_MASTER", 0x5b: "MCA_WATCHDOG_TIMEOUT_MSG_CH_FSM",
                                0x5c: "MCA_WATCHDOG_TIMEOUT_BULK_CR_FSM", 0x5d: "MCA_WATCHDOG_TIMEOUT_IOSFSB_FSM",
                                0x60: "MCA_PKGS_SAFE_WP_TIMEOUT", 0x61: "MCA_PKGS_CPD_UNCPD_TIMEOUT",
                                0x62: "MCA_PKGS_INVALID_REQ_PCH", 0x63: "MCA_PKGS_INVALID_REQ_INTERNAL",
                                0x64: "MCA_PKGS_INVALID_RSP_INTERNAL", 0x65: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x66: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x67: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x68: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x69: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x6a: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x6b: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x6c: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x6d: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x6e: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x6f: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x70: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x71: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x72: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x73: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x74: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x75: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x76: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x77: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x78: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x79: "MCA_PKGS_RESET_PREP_TIMEOUT",
                                0x7a: "MCA_PKGS_RESET_PREP_TIMEOUT", 0x7b: "MCA_PKGS_SMBUS_VPP_PAUSE_TIMEOUT",
                                0x7c: "MCA_PKGS_SMBUS_MCP_PAUSE_TIMEOUT", 0x7d: "MCA_PKGS_SMBUS_SPD_PAUSE_TIMEOUT SMBUS",
                                0x80: "MCA_PKGC_DISP_BUSY_TIMEOUT", 0x81: "MCA_PKGC_INVALID_RSP_PCH PkgC",
                                0x83: "MCA_PKGC_WATCHDOG_HANG_CBZ_DOWN", 0x84: "MCA_PKGC_WATCHDOG_HANG_CBZ_UP",
                                0x87: "MCA_PKGC_WATCHDOG_HANG_C2_BLKMASTER", 0x88: "MCA_PKGC_WATCHDOG_HANG_C2_PSLIMIT",
                                0x89: "MCA_PKGC_WATCHDOG_HANG_SETDISP", 0x8b: "MCA_PKGC_ALLOW_L1_ERROR",
                                0x90: "MCA_RECOVERABLE_DIE_THERMAL_TOO_HOT", 0xa0: "MCA_ADR_SIGNAL_TIMEOUT",
                                0xa1: "MCA_BCLK_FREQ_OC_ABOVE_THRESHOLD", 0xb0: "MCA_DISPATCHER_RUN_BUSY_TIMEOUT"
                                },
                            "MSEC_HW": {4: "Clock/power IP response timeout", 5: "SMBus controller raised SMI",
                                        9: "PM controller received invalid transaction"
                                        },
                            "MSEC_UC": {1: "Instruction address out of valid space", 2: "Double bit RAM error on Instruction Fetch",
                                        3: "Invalid OpCode seen", 4: "Stack Underflow", 5: "Stack Overflow",
                                        6: "Data address out of valid space", 7: "Double bit RAM error on Data Fetch"
                                        },
                            "MCACOD": {0x402: "PCU Error", 0x40b: "internal firmware errors",
                                        0x40c: "shutdown error"}
                        },
                    "MC6": {"MSCOD": {0x8000: "Poison", 0x8001: "Unsupported Opcode", 0x8002: "Misaligned CFG Rd (SMM)",
                                0x8003: "Misaligned CFG Wr (SMM)", 0x8004: "Misaligned CFG Rd (Non-SMM)",
                                0x8005: "Misaligned CFG Wr (Non-SMM)", 0x8006: "Misaligned MMIO Rd (SMM)",
                                0x8007: "Misaligned MMIO Wr (SMM)", 0x8008: "Misaligned MMIO Rd (Non-SMM)",
                                0x8009: "Misaligned MMIO Wr (Non-SMM)", 0x800a: "SMI Timeout", 0x800b: "Lock Master Timeout",
                                0x800e: "Semaphore Error", 0x800f: "AK Egress Write Valid Entry",
                                0x8010: "BL Egress Write Valid Entry", 0x8011: "AD Egress Write Valid Entry",
                                0x8012: "AK Egress Overflow", 0x8013: "BL Egress Overflow", 0x8014: "AD Egress Overflow",
                                0x8015: "CHA to Ubox Overflow (NCB)", 0x8016: "CHA to Ubox Overflow (NCS)",
                                0x8017: "UPI to Ubox Overflow (NCB)", 0x8018: "UPI to Ubox Overflow (NCS)",
                                0x8019: "Ingress Parity Error", 0x801a: "MS2IOSF to Ubox Overflow (NCB)",
                                0x801b: "MS2IOSF to Ubox Overflow (NCS)"
                            },
                            "MCACOD":{0x407: "General UBox error", 0x406: "internal firmware error",
                                0xe0b: "Generic I/O erro"
                            }
                        },
                    
                    "CHA0": {"MSCOD": {1: "Uncorrectable Data Error", 2: "Uncorrectable Tag Error",
                                3: "SAD_ERR_WB_TO_MMIO", 4: "SAD_ERR_IA_ACCESS_TO_GSM", 5: "SAD_ERR_CORRUPTING_OTHER",
                                6: "SAD_ERR_NON_CORRUPTING_OTHER", 7: "Correctable Data Error", 8: "MEM_POISON_DATA_ERROR",
                                9: "SAD_ERR_CRABABORT", 0xa: "Parity Data Error", 0xb: "CORE_WB_MISS_LCC",
                                0xc: "TOR Time Out", 0xd: "Internal Error", 0xe: "Internal Error", 0xf: "Internal Error",
                                0x11: "LLC_TAG_CORR_ERR", 0x12: "LLC_STATE_CORR_ERR", 0x13: "LLC_STATE_UNCORR_ERR",
                                0x16: "MULT_TOR_ENTRY_MATCH", 0x17: "MULT_LCC_WAY_TAG_MATCH", 0x18: "BL_REG_RTID_TABLE_MISS",
                                0x19: "AK_REG_RTID_TABLE_MISS", 0x1c: "IDI_JITTER_ERROR", 0x1d: "Internal Error",
                                0x1e: "Internal Error",  0x1f: "Internal Error", 0x21: " UNCORRECTABLE_SF_TAG_ERROR",
                                0x22: "SnoopFilter_TAG_CORR_ERR", 0x23: "SnoopFilter_STATE_CORR_ERR", 0x24: "SnoopFilter_STATE_UNCORR_ERR",
                                0x27: "SAD_ERR_LTMEMLOCK", 0x28: "LLC_TWOLM_CORR_ERR", 0x29: "LLC_TWOLM_UNCORR_ERR",
                                0x2a: "ISMQ_UNEXPECTED_RSP", 0x2b: "TWOLM_MULT_HIT", 0x2c: "HA_UNEXPECTED_RSP",
                                0x2d: "SAD_ERR_RRQWBQ_TO_NONHOM", 0x2e: "SAD_ERR_IIOTONONHOM", 0x2f: "Internal Error",
                                0x31: "SF_TWOLM_CORR_ERR", 0x32: "SF_TWOLM_UNCORR_ERR", 0x33: "AK_BL_UQID_PTY_ERROR",
                                0x34: "WXSNP_WITH_SNPCOUNT_ZERO", 0x35: "MEM_PUSH_WR_NS_S", 0x36: "SAD_ERR_UNSECURE_UPI_ACCESS",
                                0x37: "CLFLUSH_MMIO_HIT_M"
                            },
                            "MCCOD": {1: "Corrected Data Error"},##bit[12]
                            "MCCOD-1": {0: "Generic Error", 1: "Generic Read", 2: "Generic Write",
                                            3: "Data Read", 4: "Data Write", 5: "Instruction Fetch",
                                            6: "Prefetch", 7: "Eviction", 8: "Snoop",
                                        }, ##bit[7-4]
                            "MCCOD-2" : {0: "Instruction", 1: "Data", 2: "Generic TT", 3: "Reserved TT"}, ##bit[3-2]
                            "MCCOD-3" : {0: "Level 0", 1: "Level 1", 2: "Level 2", 3: "Generic LL"}, ##bit[1-0]
                            "MCCOD-4" : {0x136: "Error during data read", 0x17a: "Error during Explicit Write Back", 
                                        0x152: "Error during instruction read"},  ##bit[15-0]
                        
                        },
                    "MC12": {"MSCODRESETPREPFAIL":{0: "No FailoverWhileResetPrep error logged",
                                    1: "Error logged is a FailoverWhileResetPrep error"
                            },
                            "MSCODDDRTYPE":{0: "Not logged whether error to DDR4 or DDRT",
                                    1: "Error specifically on DDR4", 2: "Error specifically on DDRT",
                                    3: "Error for this transaction was detected on both DDR4 and DDRT"
                            },
                            "MSCOD": {0: "No error (default)", 1: "Read ECC error", 2: "Bucket1 error",
                                    3: "RdTrkr Parity error", 4: "Secure mismatch", 5: "prefetch channel mismatch",
                                    6: "failover while reset prep", 7: "read completion parity error",
                                    8: "response parity error", 9: "timeout error", 0xa: "CMI reserved credit pool error",
                                    0xb: "CMI total credit count error", 0xc: "CMI credit oversubscription error"
                            },
                            "MCACOD": {0x400: "Time-out", 0x405: "Parity error on internal Mesh2mem structures"}, #bit[15-0]
                            "MCACOD-1": {1: "Last level memory controller error. Follow below encodings",
                                        4: "Near-Memory Cache controller error. Follow below encodings"}, #bit[15-7]
                            "MCACOD-2": {0: "Generic undefined request", 1: "Memory Read Error", 2: "Memory Write Error",
                                        3: "Address/Command Error", 4: "Memory Scrubbing Error"}, #bit[6-4]
                            "MCACOD-3": {0xf: "Channel not specified"} #bit[3-0]
                        },
                    "MC13": {"MSCOD": {0: "UnCorrectable Spare Error", 1: "Internal Error - End-End Address Parity Error",
                                    2: "Internal Error - Write Data Parity Error", 3: "Internal Error - End-End Uncorr/Corr Wr Data ECC Error",
                                    4: "Internal Error - Write Byte Enable Parity Error", 7: "Internal Error  - Transaction ID Parity Error",
                                    8: "Corr Patrol Scrub Error", 0x10: "UnCorr Patrol Scrub Error", 0x20: "Corr Spare Error",
                                    0x80: "Transient or Correctable Error for Demand or Underfill Reads",
                                    0xa0: "Uncorrectable Error for Demand or Underfill Reads", 0x100: "WDB Read Parity Error",
                                    0x108: "DDR/DDRT Link Fail", 0x111: "Internal Error - PCLS Address CSR Parity Error",
                                    0x112: "Internal Firmware Error - PCLS Illegal ADDDC Configuration Error", 0x200: "DDR4 CA Parity",
                                    0x400: "Internal Parity Error - RPQ Scheduler Address Parity", 0x8000: "Internal FW Error - 2LM unrecognized request type",
                                    0x801: "Internal Error - 2LM read response to an invalid scoreboard entry", 0x802: "Internal Error - 2LM unexpected read response",
                                    0x803: "Internal Error - 2LM DDR4 completion to an invalid scoreboard entry", 0x804: "Internal Error - 2LM DDRt completion to an invalid scoreboard entry",
                                    0x805: "Internal Error - 2LM completion FIFO overflow", 0x806: "DDRT Link Parity Error",
                                    0x807: "Internal Error - DDRT RID Uncorrectable error", 0x809: "Internal Error - DDRT RID FIFO overflow",
                                    0x80a: "Internal FW Error - DDRT Error on FNV Write credits", 0x80b: "Internal Error - DDRT Error on FNV Read credits",
                                    0x80c: "Internal Error - DDRT Scheduler error", 0x80d: "DDRT FNV Error (CAParity or WrECC Error)",
                                    0x80e: "DDRT FNV Thermal Error", 0x80f: "Internal Error - DDRT Unexpected Data Packet During CMI Idle",
                                    0x810: "Internal Parity Error - DDRT RPQ Request Parity Error", 0x811: "Internal Parity Error - DDRT WPQ Request Parity Error",
                                    0x812: "Internal Error - 2LM NmFillWr CAM Multiple Hit Error", 0x813: "Internal Error - CMI Credit Oversubscription Error",
                                    0x814: "Internal Error - CMI Total Credit Count Error", 0x815: "Internal Error - CMI Reserved Credit Pool Error",
                                    0x816: "DDRT Link ECC Error", 0x817: "Internal Error - WDB FIFO Overflow or Underflow Errors", 0x818: "Internal Error - CMI Request FIFO Overflow Error",
                                    0x819: "Internal Error - CMI Request FIFO Underflow Error", 0x81a: "Internal Error - CMI Response FIFO Overflow Error",
                                    0x81b: "Internal Error - CMI Response FIFO Underflow Error", 0x81c: "Internal Error - CMI Miscellaneous Credit Errors",
                                    0x81d: "Internal Error - CMI MC Arbiter Errors", 0x81e: "Internal Error - DDRT Write Completion FIFO Overflow Error",
                                    0x81f: "Internal Error - DDRT Write Completion FIFO Underflow Error", 0x820: "Internal Error - CMI Read Completion FIFO Overflow Error",
                                    0x821: "Internal Error - CMI Read Completion FIFO Underflow Error", 0x822: "Internal Parity Error - TME Key RF Parity Error",
                                    0x823: "Internal Error - TME Miscellaneous CMI Errors", 0x824: "Internal Error - TME CMI Overflow Error",
                                    0x825: "Internal Error - TME CMI Underflow Error", 0x826: "SGX TEM Secure Bit Mismatch Detected on Demand Read",
                                    0x827: "Internal Error - TME Detected Underfill Read Completion Data Parity Error", 0x828: "Internal Error - 2LM Scoreboard Overflow Error",
                                    0x1008: "Corr Patrol Scrub Error (Mirror Secondary)" 
                                },
                            "MCACOD" :{0x405: "Parity error on structures"}, #bit[15-0]
                            "MCACOD-1": {1: "Memory Controller Errors in 1LM mode", 5: " Memory Controller Errors in 2LM mode"}, #bit[15-7]
                            "MCACOD-2": {0: "Generic undefined request", 1: "Memory Read Error", 2: "Memory Write Erro",
                                        3: "Address/Command Error", 4: "Memory Scrubbing Error"}, #bit[6-4]
                            "MCACOD-3": {0xf: "Channel not specified"}, #bit[3-0]
                        }
                }
    mc_core = { "CORE0MC0STATUSTHREAD0" : "MC0", "CORE0MC1STATUSTHREAD0" : "MC1", "CORE0MC2STATUSTHREAD0" : "MC2",
                "CORE0MC3STATUSTHREAD0" : "MC3", "CORE1MC0STATUSTHREAD0" : "MC0", "CORE1MC1STATUSTHREAD0" : "MC1",
                "CORE1MC2STATUSTHREAD0" : "MC2", "CORE1MC3STATUSTHREAD0" : "MC3", "CORE2MC0STATUSTHREAD0" : "MC0",
                "CORE2MC1STATUSTHREAD0" : "MC1", "CORE2MC2STATUSTHREAD0" : "MC2", "CORE2MC3STATUSTHREAD0" : "MC3",
                "CORE3MC0STATUSTHREAD0" : "MC0", "CORE3MC1STATUSTHREAD0" : "MC1", "CORE3MC2STATUSTHREAD0" : "MC2",
                "CORE3MC3STATUSTHREAD0" : "MC3", "CORE4MC0STATUSTHREAD0" : "MC0", "CORE4MC1STATUSTHREAD0" : "MC1",
                "CORE4MC2STATUSTHREAD0" : "MC2", "CORE4MC3STATUSTHREAD0" : "MC3", "CORE5MC0STATUSTHREAD0" : "MC0",
                "CORE5MC1STATUSTHREAD0" : "MC1", "CORE5MC2STATUSTHREAD0" : "MC2", "CORE5MC3STATUSTHREAD0" : "MC3",
                "CORE6MC0STATUSTHREAD0" : "MC0", "CORE6MC1STATUSTHREAD0" : "MC1", "CORE6MC2STATUSTHREAD0" : "MC2",
                "CORE6MC3STATUSTHREAD0" : "MC3", "CORE7MC0STATUSTHREAD0" : "MC0", "CORE7MC1STATUSTHREAD0" : "MC1",
                "CORE7MC2STATUSTHREAD0" : "MC2", "CORE7MC3STATUSTHREAD0" : "MC3", "CHA0MC_STATUS" : "CHA0",
                "CHA1MC_STATUS" : "CHA0", "CHA2MC_STATUS" : "CHA0", "CHA3MC_STATUS" : "CHA0", "CHA4MC_STATUS" : "CHA0", 
                "CHA5MC_STATUS" : "CHA0", "CHA6MC_STATUS" : "CHA0", "CHA7MC_STATUS" : "CHA0", "CORE0MC4STATUSTHREAD0" : "MC4",
                "CORE0MC6STATUSTHREAD0" : "MC6", "CORE0MC12STATUSTHREAD0" : "MC12", "CORE0MC13STATUSTHREAD0" : "MC13",
                "CORE0MC14STATUSTHREAD0" : "MC13", "CORE0MC15STATUSTHREAD0": "MC13","CORE0MC16STATUSTHREAD0" : "MC12"
            }
    output = ""
    try:
        output = parse_core_mc_mscod_D1734(ret_value, mc_core[name], dict_mc_info)
        output = output + parse_core_mc_mcacod_D1734(ret_value, mc_core[name], dict_mc_info)
        return output
    except Exception as e:
        return output + "Resolve CATERR failed: %s" % str(e)

def parse_mce_ierr_err_D1734(data, name, err_type):
    output = ""
    try :
        if (name not in data) and (len(data[name].split(" ")) == 0):
            output = "%s does not exist, or no data" % name
            print(output)
            return
        value_str = data[name].split(" ")
        tmp_value = hex_to_bin_bit(value_str, name)
        if int(tmp_value[8], 2):
            src_id = tmp_value[0:8][::-1]
            output = "%s: %s: FIRST%sSRCID: %s" % \
                (name, joint_addr(value_str), err_type, src_id)
            print(output)
    except Exception as e:
        print(output + "Resolve mce-ierr err type  failed: %s" % str(e))

#MCE: parse mce ierr form a4(ierr) a8(mce)
def parse_mce_ierr_D1734(data):
    """
    1.CPU D1734 has eight cores(core[0:7])
    2.FirstIerrSrcId or FirstMCerrSrcId bite[0:7] to judge core type
    bit 8: FirstIerrSrcValid - a4
    bit 8: FirstMCerrSrcValid -a8
    """
    # parse "a4" ---ierr
    # parse "a8" ---mce
    output = ""
    dict_mce_ierr = {"B30D0F0Addra4" : "IERR", "B30D0F0Addra8" : "MCERR"}
    try:
        for name in dict_mce_ierr:
            parse_mce_ierr_err_D1734(data, name, dict_mce_ierr[name])
    except Exception as e:
        output = output + "Resolve IERR or MCE failed: %s" % str(e)
        print(output)

def parse_mce_core_status_D1734(data):
    core_status_list = [
        "CORE0MC0STATUSTHREAD0", "CORE0MC1STATUSTHREAD0", "CORE0MC2STATUSTHREAD0", "CORE0MC3STATUSTHREAD0",
        "CORE1MC0STATUSTHREAD0", "CORE1MC1STATUSTHREAD0", "CORE1MC2STATUSTHREAD0", "CORE1MC3STATUSTHREAD0",
        "CORE2MC0STATUSTHREAD0", "CORE2MC1STATUSTHREAD0", "CORE2MC2STATUSTHREAD0", "CORE2MC3STATUSTHREAD0",
        "CORE3MC0STATUSTHREAD0", "CORE3MC1STATUSTHREAD0", "CORE3MC2STATUSTHREAD0", "CORE3MC3STATUSTHREAD0",
        "CORE4MC0STATUSTHREAD0", "CORE4MC1STATUSTHREAD0", "CORE4MC2STATUSTHREAD0", "CORE4MC3STATUSTHREAD0",
        "CORE5MC0STATUSTHREAD0", "CORE5MC1STATUSTHREAD0", "CORE5MC2STATUSTHREAD0", "CORE5MC3STATUSTHREAD0",
        "CORE6MC0STATUSTHREAD0", "CORE6MC1STATUSTHREAD0", "CORE6MC2STATUSTHREAD0", "CORE6MC3STATUSTHREAD0",
        "CORE7MC0STATUSTHREAD0", "CORE7MC1STATUSTHREAD0", "CORE7MC2STATUSTHREAD0", "CORE7MC3STATUSTHREAD0",
        "CORE0MC4STATUSTHREAD0", "CORE0MC6STATUSTHREAD0",
        "CHA0MC_STATUS", "CHA1MC_STATUS", "CHA2MC_STATUS", "CHA3MC_STATUS", "CHA4MC_STATUS", "CHA5MC_STATUS",
        "CORE0MC12STATUSTHREAD0", "CORE0MC13STATUSTHREAD0", "CORE0MC14STATUSTHREAD0"
    ]
    parse_mce_bank_msb_D1734(data, core_status_list)

#MCE: parse mce mc ctl2 reg
def parse_mce_mc_ctl2_D1734(data, thread_keyname):
    BANK0_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK0_CTL2_REG_INFO = {0: "BANK0_CTL2 bits[0:14] Corrected error count threshold : ",
                                30: "BANK0_CTL2 bit[30] Corrected error interupt enable/disable : ",
                                32: "BANK0_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                                34: "BANK0_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK1_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK1_CTL2_REG_INFO = {0: "BANK1_CTL2 bits[0:14] Correctable error threshold : ",
                            30: "BANK1_CTL2 bit[30] Corrected error threshold enable/disable : ",
                            32: "BANK1_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK1_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK2_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK2_CTL2_REG_INFO = {0: "BANK2_CTL2 bits[0:14] Correctable error count threshold : ",
                            30: "BANK2_CTL2 bit[30] CMCI Enable : ",
                            32: "BANK2_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK2_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK3_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK3_CTL2_REG_INFO = {0: "BANK3_CTL2 bits[0:14] Correctable error threshold : ",
                            30: "BANK3_CTL2 bit[30] Corrected error threshold enable/disable : ",
                            32: "BANK3_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK3_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK4_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK4_CTL2_REG_INFO = {0: "BANK4_CTL2 bits[0:14] THRESHOLD :",
                            30: "BANK4_CTL2 bit[30] ENABLE :",
                            32: "BANK4_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK4_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK6_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK6_CTL2_REG_INFO = {0: "BANK6_CTL2 bits[0:14] Corrected error count threshold :",
                            30: "BANK6_CTL2 bit[30] CMCI_EN :",
                            32: "BANK6_CTL2 bit[32] Map Correctable Machine Check Interrupts to Correctable SM Interrupts : ",
                            34: "BANK6_CTL2 bit[34] Map Machine Check Errors to Machine check SM Interrupts : "
    }

    BANK9_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK9_CTL2_REG_INFO = {0: "BANK9_CTL2 bits[0:14] Corrected error counter threshold :",
                            30: "BANK9_CTL2 bit[30] Enable corrected error interrupts :",
                            32: "BANK9_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK9_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK10_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK10_CTL2_REG_INFO = {0: "BANK10_CTL2 bits[0:14] Corrected error counter threshold :",
                            30: "BANK10_CTL2 bit[30] Enable corrected error interrupts :",
                            32: "BANK10_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK10_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK11_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK11_CTL2_REG_INFO = {0: "BANK11_CTL2 bits[0:14] Corrected error counter threshold :",
                            30: "BANK11_CTL2 bit[30] Enable corrected error interrupts :",
                            32: "BANK11_CTL2 bit[32] Controls CMCI Remapping(0 CMCI/1 CSMI) : ",
                            34: "BANK11_CTL2 bit[34] Controls MCE Remapping(0 MCE/1 MSMI) : "
    }

    BANK12_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK12_CTL2_REG_INFO = {0: "BANK12_CTL2 bits[0:14] Correctable Error Threshold (CorrErrThrhd) : ",
                            30: "BANK12_CTL2 bit[30] Corrected Error Interrupt Enable (CmciEn) : ",
                            32: "BANK12_CTL2 bit[32] Map Correctable Machine Check Interrupt to Correctable SM Interrupt(MapCmciToCsmi) : ",
                            34: "BANK12_CTL2 bit[34] Map Machine Check Errors to Machine Check SM Interrupt (MapCmciToCsmi) : "
    }

    BANK13_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK13_CTL2_REG_INFO = {0: "BANK13_CTL2 bits[0:14] Corrected error count threshold : ",
                            30: "BANK13_CTL2 bit[30] CMCI_EN : ",
                            32: "BANK13_CTL2 bit[32] Map Correctable Machine Check Interrupts to Correctable SM Interrupts : ",
                            34: "BANK13_CTL2 bit[34] Map Machine Check Errors to Machine check SM Interrupts : "
    }

    BANK14_CTL2_BIT = {0: 14, 30: 30, 32: 32, 34: 34}
    BANK14_CTL2_REG_INFO = {0: "BANK14_CTL2 bits[0:14] Corrected error count threshold : ",
                            30: "BANK14_CTL2 bit[30] CMCI_EN : ",
                            32: "BANK14_CTL2 bit[32] Map Correctable Machine Check Interrupts to Correctable SM Interrupts : ",
                            34: "BANK14_CTL2 bit[34] Map Machine Check Errors to Machine check SM Interrupts : "
    }
    #1-8
    output = ""
    try:
        match = re.search(r'MC(\d+)CTL2', thread_keyname)
        if match:
            reg_name = "BANK%s_CTL2" % match.group(1)
        else:
            output = "invaild %s : " % thread_keyname
            return output
        dict_bit = reg_name + "_BIT"
        dict_reg_info = reg_name + "_REG_INFO"
        reg_vlaue = hex_to_bin_bit(data[thread_keyname].split(" "), thread_keyname)
        for beg_bit in locals()[dict_bit]:
            ret, ret_out = get_reg_bit_value(reg_vlaue, beg_bit, locals()[dict_bit][beg_bit], locals()[dict_reg_info])
            if ret:
                output = output + ret_out
        return output
    except Exception as e:
        output = output + "parse %s failed(%s) : " % str(thread_keyname, e)
        return output

# MCE: parse mce msr reg
def parse_mce_msr_D1734(data):
    list_msr_name = {"CORE_SMI_ERR_SRC", "UNCORE_SMI_ERR_SRC", "SMM_PROT_MODE_BASE", "SMM_FEATURE_CONTROL"}
    CORE_SMI_ERR_SRC_CORE_THREAD_INFO = {"core_num": 8, "thread_num": 1}
    CORE_SMI_ERR_SRC_BIT = {2: 2, 3: 3}
    CORE_SMI_ERR_SRC_REG_INFO = {2: "CORE_SMI_ERR bit[2]  DTLB : ", 3: "CORE_SMI_ERR bit[3]  MLC : "}

    UNCORE_SMI_ERR_SRC_CORE_THREAD_INFO = {"core_num": 8, "thread_num": 1}
    UNCORE_SMI_ERR_SRC_BIT = {4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13,
                                14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22,
                                23: 23, 24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    UNCORE_SMI_ERR_SRC_REG_INFO = { }
    for reg_bit in range(4, 31):
        value = "UNCORE_SMI_ERR_SRC bit[%d]  MCA_BANK_ID_%d : " %(reg_bit, reg_bit)
        UNCORE_SMI_ERR_SRC_REG_INFO[reg_bit] = value

    SMM_PROT_MODE_BASE_CORE_THREAD_INFO = {"core_num": 8, "thread_num": 2}
    SMM_PROT_MODE_BASE_BIT = {0: 0, 12: 31}
    SMM_PROT_MODE_BASE_REG_INFO = {0: "SMM_PROT_MODE_BASE bit[0] Protected Mode SMM Enable : ",
                                    12: "SMM_PROT_MODE_BASE bits[12:31] The physical address of the SMMSEG Table : "
    }

    SMM_FEATURE_CONTROL_CORE_THREAD_INFO = {"core_num": 1, "thread_num": 1}
    SMM_FEATURE_CONTROL_BIT = {0: 0, 1: 1, 2: 2}
    SMM_FEATURE_CONTROL_REG_INFO = {0: "SMM_FEATURE_CONTROL bit[0] LOCK(Lock = 1, CPU will drop writes to the register, \
                                    Lock = 0, CPU will allow update to b[2:0]) : ", 
                                    1: "SMM_FEATURE_CONTROL bit[1] SMM_CPU_SAVE_EN( If 0, SMI/RSM will save/restore state in SMRAM; \
                                    If 1, SMI/RSM will save/restore state from SRAM) : ", 2: "SMM_FEATURE_CONTROL bit[2](If 1, generate \
                                    unrecoverable MCHK on code fetch outside SMRRs; If 0, do not report any errors for code fetch outside SMRRs) : "
    }

    output = ""
    output_tmp = ""
    try:
        for key in list_msr_name:
            dict_bit = key + "_BIT"
            dict_reg_info = key + "_REG_INFO"
            dict_core_thread_info = key + "_CORE_THREAD_INFO"
            for core_index in range(0, locals()[dict_core_thread_info]["core_num"]):
                for thread_index in range(0, locals()[dict_core_thread_info]["thread_num"]):
                    print_flag = 0
                    reg_key_name = "CORE%d_%sTHREAD%d" %(core_index, key, thread_index)
                    if reg_key_name in data:
                        output_tmp = "%s : " % reg_key_name
                        reg_vlaue = hex_to_bin_bit(data[reg_key_name].split(" "), reg_key_name)
                        for beg_bit in locals()[dict_bit]:
                            ret, ret_out = get_reg_bit_value(reg_vlaue, beg_bit, locals()[dict_bit][beg_bit], locals()[dict_reg_info])
                            output_tmp = output_tmp + ret_out
                            if ret:
                                print_flag = 1
                        if print_flag:
                            output = output + output_tmp + "\n"
        print(output)
    except Exception as e:
        output = output + "parse mce msr failed : %s" % str(e)
        print(output)

# MCE: parse mce arr err type
def parse_mce_aer_D1734(value):
    #D1734也使用该方式解析
    output = parse_mce_D1734_err_type(value)
    if output == None or len(output) == 0:
        print("No abnormality")
        return
    else:
        print(output)
        parse_mce_ierr_D1734(value)
        parse_mce_core_status_D1734(value)
        #parse_mce_msr_D1734(value)

def get_reg_bit_value(reg_value, beg_bit, end_bit, reg_info, dev_bit_value = None):
    try:
        output = ""
        print_flag = 0
        if beg_bit == end_bit:
            return_value = int(reg_value[beg_bit], 2)
            #bit值不为0，则记录
            if dev_bit_value != None and return_value:
                dev_bit_value[beg_bit] = 1
        elif beg_bit < end_bit:
            return_value = int(reg_value[beg_bit:end_bit+1][::-1], 2)
        else:
            beg_bit = 0
        if return_value and beg_bit in reg_info:
            print_flag = 1
            output = reg_info[beg_bit] + "%s, " % return_value
    except Exception as e:
        print("Error get_reg_bit_value: " + str(e))
    return print_flag, output

def parse_peci_err_dev_func_info_D1734(data, bdf_info):
    dict_addr_reg = { "Addr6": "DEV_PCISTS" , "Addr4a": "DEV_DEVSTS", "Addr104": "DEV_ERRUNCSTS", "Addr110": "DEV_ERRCORSTS", "Addr130": "DEV_ROOTERRSTS",
                    "Addr19c": "DEV_RPPIOSTS", "Addr1b0": "DEV_RPPIOHDRLOG1", "Addr1b4": "DEV_RPPIOHDRLOG2", "Addr1b8": "DEV_RPPIOHDRLOG3",
                    "Addr1bc": "DEV_RPPIOHDRLOG4", "Addr208": "DEV_LANEERRSTS", "Addr620": "IBSTERRCRCSTS0", "Addr624": "IBSTERRRCRVSTS0",
                    "Addr628": "IBSTERRCRCSTS1", "Addr62c": "IBSTERRRCRVSTS1", "Addr630": "IBSTERRCRCSTS2", "Addr634": "IBSTERRRCRVSTS2",
                    "Addr638": "IBSTERRCRCSTS3", "Addr63c": "IBSTERRRCRVSTS3", "Addr764": "CORERRCNT", "Addrb58": "LEKBERR",
                    "Addrb6c": "LEKBLNERRCNT0", "Addrb70": "LEKBLNERRCNT1", "Addrb74": "LEKBLNERRCNT2"
    }
    #begin_bit: end_bit
    DEV_PCISTS_BIT = {3: 3, 4: 4, 5: 5, 7: 7, 8: 8, 9: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    #begin_bit: reg_bit_info
    DEV_PCISTS_REG_INFO = {3: "PCISTS bit[3] INTX_STATUS : ", 4 : "PCISTS bit[4] CAPABILITIES_LIST : ",
                        5: "PCISTS bit[3] X66MHZ_CAPABLE : ", 7: "PCISTS bit[4] FAST_BACK_TO_BACK : ",
                        8: "PCISTS bit[8] MASTER_DATA_PARITY_ERROR : ", 9: "PCISTS bits[9:10] DEVSEL_TIMING : ",
                        11: "PCISTS bit[11] DEVSEL_TIMING : ", 12: "PCISTS bit[12] RECEIVED_TARGET_ABORT",
                        13: "PCISTS bit[13] RECEIVED_MASTER_ABORT", 14: "PCISTS bit[14] SIGNALED_SYSTEM_ERROR", 
                        15: "PCISTS bit[15] DETECTED_PARITY_ERROR"
    }

    DEV_DEVSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    DEV_DEVSTS_REG_INFO = {0: "DEVSTS bit[0] Correctable Error Detected (CED) : ", 1: "DEVSTS bit[1] Non-Fatal Error Detected (NFED)",
                        2: "DEVSTS bit[2] Fatal Error Detected (FED) : ", 3: "DEVSTS bit[3] Unsupported Request Detected (URD)",
                        4: "DEVSTS bit[4] Auxiliary Power Detected (APD) : ", 5: "DEVSTS bit[5] Transactions Pending (TP) : "
    }

    DEV_ERRUNCSTS_BIT = {4: 4, 5: 5, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18,
                        19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26}
    DEV_ERRUNCSTS_REG_INFO = {4: "ERRUNC bit[4] Data Link Protocol Error Status (DLPE) : ",
                        5: "ERRUNC bit[5] Surprise Down Error Status (SLDE) : ",
                        12: "ERRUNC bit[12] Poisoned TLP Received Status (PTLPE) : ",
                        13: "ERRUNC bit[13] Flow Control Protocol Error Status (FCE) : ",
                        14: "ERRUNC bit[14] Completion Timeout Status (CTE) : ",
                        15: "ERRUNC bit[15] Completer Abort Status (CAE) : ",
                        16: "ERRUNC bit[16] Unexpected Completion Status (UCE) : ",
                        17: "ERRUNC bit[17] Receiver Overflow Status (ROE) : ",
                        18: "ERRUNC bit[18] Malformed TLP Status (MTLPE) : ",
                        19: "ERRUNC bit[19] ECRC Error Status (ECRCE) : ",
                        20: "ERRUNC bit[20] Unsupported Request Error Status (URE) : ",
                        21: "ERRUNC bit[21] ACS Violation Status (ACSE) : ",
                        22: "ERRUNC bit[22] Uncorrectable Internal Error Status (UIE) : ",
                        23: "ERRUNC bit[23] MC Blocked TLP Status (MCE) : ",
                        24: "ERRUNC bit[24] Atomic Egress Blocked Status (AEBE) : ",
                        25: "ERRUNC bit[25] TLP Prefix Blocked Error Status (TPBE) : ",
                        26: "ERRUNC bit[26] Poisoned TLP Egress Blocked Status (PTLPEB) : "
    }

    DEV_ERRCORSTS_BIT = {0: 0, 6: 6, 7: 7, 8: 8, 12: 12, 13: 13, 14: 14, 15: 15}
    DEV_ERRCORSTS_REG_INFO = {0: "ERRCORSTS bit[0] Receiver Error (RE) : ", 6: "ERRCORSTS bit[6]: Bad TLP Error (BTLPE) : ",
                            7: "ERRCORSTS bit[7] Bad DLLP Error (BDLLPE) : ", 8: "ERRCORSTS bit[8] Replay Number Rollover Error (RNRE) : ",
                            12: "ERRCORSTS bit[12] Replay Timer Timeout Error (RTTE) : ",
                            13: "ERRCORSTS bit[13] Advisory Non-Fatal Error (ANFE) : ",
                            14: "ERRCORSTS bit[14] Correctable Internal Error (CIE) : ",
                            15: "ERRCORSTS bit[15] Header Log Overflow Error (HLOE) : "
    }

    DEV_ROOTERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 27: 31}
    DEV_ROOTERRSTS_REG_INFO = {0: "ROOTERRSTS bit[0] Correctable Error Received (CER) : ",
                            1: "ROOTERRSTS bit[1] Multiple Error Correctable Error Received (MCER) : ",
                            2: "ROOTERRSTS bit[2] Error Fatal/Non-Fatal Received (EFR) : ",
                            3: "ROOTERRSTS bit[3] Multiple Error Fatal/Non-Fatal Received (MEFR) : ",
                            4: "ROOTERRSTS bit[4] First Uncorrectable Fatal (FUF) : ",
                            5: "ROOTERRSTS bit[5] Non-Fatal Error message Received (NFEMR) : ",
                            6: "ROOTERRSTS bit[6] Fatal Error Message Received (FEMR) : ",
                            27: "ROOTERRSTS bits[27:31] Advanced Error Interrupt Message Number (AEMN) : "
    }

    DEV_RPPIOSTS_BIT = {0: 0, 1: 1, 2: 2, 8: 8, 9: 9, 10: 10, 16: 16, 17: 17, 18: 18}
    DEV_RPPIOSTS_REG_INFO = {0: "RPPIOSTS bit[0] Cfg UR Cpl (CFGURC) : ", 1: "RPPIOSTS bit[1] Cfg CA Cpl (CFGCAC) : ",
                            2: "RPPIOSTS bit[2] Cfg CTO (CFGCTO) : ", 8: "RPPIOSTS bit[8] I/O UR Cpl (IOURC) : ",
                            9: "RPPIOSTS bit[9] I/O CA Cpl (IOCAC) : ", 10: "RPPIOSTS bit[10] I/O CTO (IOCTO) : ",
                            16: "RPPIOSTS bit[16] Mem UR Cpl (MEMURC) : ", 17: "RPPIOSTS bit[17] Mem CA Cpl (MEMCAC) : ",
                            18: "RPPIOSTS bit[18] Mem CTO (MEMCTO) : "
    }

    DEV_RPPIOHDRLOG1_BIT = {0: 31}
    DEV_RPPIOHDRLOG1_REG_INFO = {0: "RPPIOHDRLOG1 Header Byte (HB) : "}
    DEV_RPPIOHDRLOG2_BIT = {0: 31}
    DEV_RPPIOHDRLOG2_REG_INFO = {0: "RPPIOHDRLOG2 Header Byte (HB) : "}
    DEV_RPPIOHDRLOG3_BIT = {0: 31}
    DEV_RPPIOHDRLOG3_REG_INFO = {0: "RPPIOHDRLOG3 Header Byte (HB) : "}
    DEV_RPPIOHDRLOG4_BIT = {0: 31}
    DEV_RPPIOHDRLOG4_REG_INFO = {0: "RPPIOHDRLOG4 Header Byte (HB) : "}

    DEV_LANEERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
                        8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    DEV_LANEERRSTS_REG_INFO = {0: "LANEERRSTS bit[0] Lane 0 Error (L0ERR) : ", 1: "LANEERRSTS bit[1] Lane 1 Error (L1ERR) : ",
                            2: "LANEERRSTS bit[2] Lane 2 Error (L2ERR) : ", 3: "LANEERRSTS bit[3] Lane 3 Error (L3ERR) : ",
                            4: "LANEERRSTS bit[4] Lane 4 Error (L4ERR) : ", 5: "LANEERRSTS bit[5] Lane 5 Error (L5ERR) : ",
                            6: "LANEERRSTS bit[6] Lane 6 Error (L6ERR) : ", 7: "LANEERRSTS bit[7] Lane 7 Error (L7ERR) : ",
                            8: "LANEERRSTS bit[8] Lane 8 Error (L8ERR) : ", 9: "LANEERRSTS bit[9] Lane 9 Error (L9ERR) : ",
                            10: "LANEERRSTS bit[10] Lane 10 Error (L10ERR) : ", 11: "LANEERRSTS bit[11] Lane 11 Error (L11ERR) : ",
                            12: "LANEERRSTS bit[12] Lane 12 Error (L12ERR) : ", 13: "LANEERRSTS bit[13] Lane 13 Error (L13ERR) : ",
                            14: "LANEERRSTS bit[14] Lane 14 Error (L14ERR) : ", 15: "LANEERRSTS bit[15] Lane 15 Error (L15ERR) : ",
    }

    IBSTERRCRCSTS0_BIT = {0: 14, 15: 15}
    IBSTERRCRCSTS0_REG_INFO = {0: "IBSTERRCRCSTS0 bits[0:14] CRC Error Counter (CRCECC2ERRCNT) : ",
                                15: "IBSTERRCRCSTS0 bit[15] CRC Error Overflow (CRCECC2OVRFLOW) : "
    }
    IBSTERRCRCSTS1_BIT = {0: 14, 15: 15}
    IBSTERRCRCSTS1_REG_INFO = {0: "IBSTERRCRCSTS1 bits[0:14] CRC Error Counter (CRCECC2ERRCNT) : ",
                                15: "IBSTERRCRCSTS1 bit[15] CRC Error Overflow (CRCECC2OVRFLOW) : "
    }
    IBSTERRCRCSTS2_BIT = {0: 14, 15: 15}
    IBSTERRCRCSTS2_REG_INFO = {0: "IBSTERRCRCSTS2 bits[0:14] CRC Error Counter (CRCECC2ERRCNT) : ",
                                15: "IBSTERRCRCSTS2 bit[15] CRC Error Overflow (CRCECC2OVRFLOW) : "
    }
    IBSTERRCRCSTS3_BIT = {0: 14, 15: 15}
    IBSTERRCRCSTS3_REG_INFO = {0: "IBSTERRCRCSTS3 bits[0:14] CRC Error Counter (CRCECC2ERRCNT) : ",
                                15: "IBSTERRCRCSTS3 bit[15] CRC Error Overflow (CRCECC2OVRFLOW) : "
    }

    IBSTERRRCRVSTS0_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    IBSTERRRCRVSTS0_REG_INFO = {0: "IBSTERRRCRVSTS0 bits[0:14] Receiver Error Counter (RXERRCNT) : ",
                                15: "IBSTERRRCRVSTS0 bit[15] Receiver Error Overflow (RXERRCNTOVRFLOW) : ",
                                16: "IBSTERRRCRVSTS0 bits[16:30] Recovery Counter (RECOVCNT) : ",
                                31: "IBSTERRRCRVSTS0 bit[31] Recovery Overflow (LINKRECOVOVERFLOW) : "
    }
    IBSTERRRCRVSTS1_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    IBSTERRRCRVSTS1_REG_INFO = {0: "IBSTERRRCRVSTS1 bits[0:14] Receiver Error Counter (RXERRCNT) : ",
                                15: "IBSTERRRCRVSTS1 bit[15] Receiver Error Overflow (RXERRCNTOVRFLOW) : ",
                                16: "IBSTERRRCRVSTS1 bits[16:30] Recovery Counter (RECOVCNT) : ",
                                31: "IBSTERRRCRVSTS1 bit[31] Recovery Overflow (LINKRECOVOVERFLOW) : "
    }
    IBSTERRRCRVSTS2_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    IBSTERRRCRVSTS2_REG_INFO = {0: "IBSTERRRCRVSTS2 bits[0:14] Receiver Error Counter (RXERRCNT) : ",
                                15: "IBSTERRRCRVSTS2 bit[15] Receiver Error Overflow (RXERRCNTOVRFLOW) : ",
                                16: "IBSTERRRCRVSTS2 bits[16:30] Recovery Counter (RECOVCNT) : ",
                                31: "IBSTERRRCRVSTS2 bit[31] Recovery Overflow (LINKRECOVOVERFLOW) : "
    }
    IBSTERRRCRVSTS3_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    IBSTERRRCRVSTS3_REG_INFO = {0: "IBSTERRRCRVSTS3 bits[0:14] Receiver Error Counter (RXERRCNT) : ",
                                15: "IBSTERRRCRVSTS3 bit[15] Receiver Error Overflow (RXERRCNTOVRFLOW) : ",
                                16: "IBSTERRRCRVSTS3 bits[16:30] Recovery Counter (RECOVCNT) : ",
                                31: "IBSTERRRCRVSTS3 bit[31] Recovery Overflow (LINKRECOVOVERFLOW) : "
    }

    CORERRCNT_BIT = {0: 31}
    CORERRCNT_REG_INFO = {0: "CORERRCNT bits[0:31] Error Counter (ERRCNT) : "}

    LEKBERR_BIT = {0: 19, 20: 24, 25: 29, 31: 31}
    LEKBERR_REG_INFO = {0: "LEKBERR bits[0:19] Aggregate error for leaky bucket error handling (AGGRERR) : ",
                        20: "LEKBERR bits[20:24] Leaky Bucket Error Threshold (ERRTHRESH) : ",
                        25: "LEKBERR bits[25:29] Gen3 Leaky Bucket Error Threshold (G3ERRTHRESH) : ",
                        31: "LEKBERR bit[31] Leaky Bucket Equalization Request Enable (G3LBEEN) : "
    }

    LEKBLNERRCNT0_BIT = {0: 4, 5: 9, 10: 14, 15: 19, 20: 24, 25: 29}
    LEKBLNERRCNT0_REG_INFO = {0: "LEKBLNERRCNT0 bits[0:4] Lane 0 Error Count (ERRCNT0) : ",
                                5: "LEKBLNERRCNT0 bits[5:9] Lane 1 Error Count (ERRCNT1) : ",
                                10: "LEKBLNERRCNT0 bits[10:14] Lane 2 Error Count (ERRCNT2) : ",
                                15: "LEKBLNERRCNT0 bits[15:19] Lane 3 Error Count (ERRCNT3) : ",
                                20: "LEKBLNERRCNT0 bits[20:24] Lane 4 Error Count (ERRCNT4) : ",
                                25: "LEKBLNERRCNT0 bits[25:29] Lane 5 Error Count (ERRCNT5) : "
    }

    LEKBLNERRCNT1_BIT = {0: 4, 5: 9, 10: 14, 15: 19, 20: 24, 25: 29}
    LEKBLNERRCNT1_REG_INFO = {0: "LEKBLNERRCNT1 bits[0:4] Lane 6 Error Count (ERRCNT6) : ",
                                5: "LEKBLNERRCNT1 bits[5:9] Lane 7 Error Count (ERRCNT7) : ",
                                10: "LEKBLNERRCNT1 bits[10:14] Lane 8 Error Count (ERRCNT8) : ",
                                15: "LEKBLNERRCNT1 bits[15:19] Lane 9 Error Count (ERRCNT9) : ",
                                20: "LEKBLNERRCNT1 bits[20:24] Lane 10 Error Count (ERRCNT10) : ",
                                25: "LEKBLNERRCNT1 bits[25:29] Lane 11 Error Count (ERRCNT11) : "
    }

    LEKBLNERRCNT2_BIT = {0: 4, 5: 9, 10: 14, 15: 19}
    LEKBLNERRCNT2_REG_INFO = {0: "LEKBLNERRCNT2 bits[0:4] Lane 12 Error Count (ERRCNT12) : ",
                                5: "LEKBLNERRCNT2 bits[5:9] Lane 13 Error Count (ERRCNT13) : ",
                                10: "LEKBLNERRCNT2 bits[10:14] Lane 14 Error Count (ERRCNT14) : ",
                                15: "LEKBLNERRCNT2 bits[15:19] Lane 15 Error Count (ERRCNT15) : "
    }
    output = ""
    output_tmp = ""
    for addr in dict_addr_reg:
        print_flag = 0
        dict_bit = dict_addr_reg[addr] + "_BIT"
        dict_reg_info = dict_addr_reg[addr] + "_REG_INFO"
        addr_key_name = bdf_info + addr
        if addr_key_name in data:
            value_str = data[addr_key_name].split(" ")
            output_tmp = "%s : %s " % (addr_key_name, joint_addr(value_str))
            reg_vlaue = hex_to_bin_bit(value_str, addr_key_name)
            for beg_bit in locals()[dict_bit]:
                ret, ret_out = get_reg_bit_value(reg_vlaue, beg_bit, locals()[dict_bit][beg_bit], locals()[dict_reg_info])
                output_tmp = output_tmp + ret_out
                if ret:
                    print_flag = 1
            if print_flag:
                output = output + output_tmp
    return output

def parse_peci_err_dev_func_addr_D1734(data, name, devfunc_name):
    output = ""
    dict_rst = {"B30D0F3Addr200" : {"reg_name" : "B30D0F3Addr", "bus" : "B30"},
                "B0D0F4Addr200" : {"reg_name" : "B0D0F4Addr", "bus" : "B0"},
                "B1D0F4Addr200" : {"reg_name" : "B1D0F4Addr", "bus" : "B1"},
                "B2D0F4Addr200" : {"reg_name" : "B2D0F4Addr", "bus" : "B2"},
                "B3D0F4Addr200" : {"reg_name" : "B3D0F4Addr", "bus" : "B3"},
                "B4D0F4Addr200" : {"reg_name" : "B4D0F4Addr", "bus" : "B4"},
                "B5D0F4Addr200": {"reg_name" : "B5D0F4Addr", "bus" : "B5"},
    }
    
    dict_dev_func = {"DEVFUN0": 0x300, "DEVFUN1": 0x304, "DEVFUN2": 0x308,
                    "DEVFUN3": 0x30c, "DEVFUN4": 0x310, "DEVFUN5": 0x314,
                    "DEVFUN6": 0x318, "DEVFUN7": 0x31c, "DEVFUN8": 0x320,
                    "DEVFUN9": 0x324, "DEVFUN10": 0x328, "DEVFUN11": 0x32c,
                    "DEVFUN12": 0x330, "DEVFUN13": 0x334, "DEVFUN14": 0x338,
                    "DEVFUN15": 0x33c, "DEVFUN16": 0x340, "DEVFUN17": 0x344,
                    "DEVFUN18": 0x348, "DEVFUN19": 0x34c, "DEVFUN20": 0x350,
                    "DEVFUN21": 0x354, "DEVFUN22": 0x358, "DEVFUN23": 0x35c,
                    "DEVFUN21": 0x354, "DEVFUN22": 0x358, "DEVFUN23": 0x35c,
                    "DEVFUN24": 0x360, "DEVFUN25": 0x364, "DEVFUN26": 0x368,
                    "DEVFUN27": 0x36c, "DEVFUN28": 0x370, "DEVFUN29": 0x374,
                    "DEVFUN30": 0x378, "DEVFUN31": 0x37c,
    }
    try:
        if name in dict_rst and devfunc_name in dict_dev_func:
            devfunc_addr = dict_rst[name]["reg_name"] + "%x" % dict_dev_func[devfunc_name]
            if devfunc_addr in data:
                beg_addr = 0
                end_addr = beg_addr + 3
                reg_value = get_peci_reg_value(data, devfunc_addr, beg_addr, end_addr)
                value = int(reg_value[0], 16)
                #7:3 Satellite IEH Bit0 Device Number
                dev = (value >>3) & 0x1f;
                #2:0 Satellite IEH Bit0 Function Numbers
                func = value & 0x7;
                bdf_info = dict_rst[name]["bus"] + "D%dF%d : " %(dev, func)
                output = "%s : %s : %s" % (devfunc_addr, joint_addr(reg_value[0:1]), bdf_info)
                return output
    except Exception as e:
        output =  "Parse peci err type failed: %s" % str(e)
        print(output)
    return output

def parse_peci_4_D1734(data):
    output = ""
    output_tmp = ""
    list_bdf_info = ["B1D2F0", "B1D3F0", "B1D4F0", "B1D5F0", "B30D26F0", "B30D27F0"]
    try:
        for bdf_info in list_bdf_info:
            output_tmp = output_tmp + parse_peci_err_dev_func_info_D1734(data, bdf_info)
    except Exception as e:
        output_tmp =  output_tmp + "Parse peci 4.0 type failed: %s" % str(e)
        print(output_tmp)
    if len(output_tmp) > 0:
        output = "Pcie4.0 part : " + output_tmp + "\n"
    return output
 
# PECI:  parse specific types of errors
def parse_peci_err_type_D1734(data):
    """
    bit31-bi1 : Dev31 - Dev30 Error Status
    bit0 : IEH Local Error Status
    """

    list_key_name = {"B0D0F4Addr200", "B1D0F4Addr200", "B2D0F4Addr200", "B3D0F4Addr200", "B4D0F4Addr200", "B5D0F4Addr200", "B30D0F3Addr200"}
    dict_rst = {"GCOERRSTS" : "Global Corrected Error Status : ",
                "GCOFERRSTS" : "Global Corrected Error First Status : ",
                "GCONERRSTS" : "Global Corrected Next Error Status : ",
                "GNFERRSTS" : "Global Non-Fatal ERR Status : ",
                "GNFFERRSTS" : "Global Non-Fatal First ERR Status : ",
                "GNFNERRSTS" : "Global Non-Fatal Next ERR Status : ",
                "GFAERRSTS" : "Global Fatal ERR Status : ",
                "GFAFERRSTS " : "Global Fatal First ERR Status : ",
                "GFANERRSTS" : "Global Fatal Next ERR Status : ",
    }

    dict_reg_addr = {"GCOERRSTS" : 0x200,
                        "GCOFERRSTS" : 0x204,
                        "GCONERRSTS" : 0x208,
                        "GNFERRSTS" : 0x210,
                        "GNFFERRSTS" : 0x214,
                        "GNFNERRSTS" : 0x218,
                        "GFAERRSTS" : 0x220,
                        "GFAFERRSTS " : 0x224,
                        "GFANERRSTS" :  0x228
    }

    try:
        output = ""
        output_tmp = ""
        for key in list_key_name:
            if key in data:
                for reg_name in dict_reg_addr:
                    output_tmp = ""
                    beg_addr = dict_reg_addr[reg_name] - 0x200
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(data, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key + reg_name)
                    if int(ret_value[0], 2):
                        output_tmp = output_tmp + "IEH Local Error Status : "
                        output_tmp = output_tmp + parse_peci_err_dev_func_addr_D1734(data, key, "DEVFUN0")
                    for i in range(1,32):
                        if int(ret_value[i], 2):
                            output_tmp = output_tmp + "Dev%d Error Status : " % i
                            devfunc = "DEVFUN%d" %i
                            output_tmp = output_tmp + parse_peci_err_dev_func_addr_D1734(data, key, devfunc)
                    if len(output_tmp) > 0:
                        output = output + "%s%s(0x%x) : %s%s : " % \
                            (key, reg_name, dict_reg_addr[reg_name], dict_rst[reg_name], joint_addr(reg_value[0:4])) + \
                            output_tmp
        if len(output) > 0:
            output = "Cpu block global handler : " + output + "\n"
        return output
    except Exception as e:
        output = output + "Parse peci err type failed: %s" % str(e)
        print(output)

def parse_peci_vt_d_D1734(value):
    list_key_name = {"B0D0F0Addr190", "B1D0F0Addr190", "B2D0F0Addr190", "B3D0F0Addr190", 
                        "B4D0F0Addr190", "B5D0F0Addr190"}
    dist_reg_addr = {"VTCORERRSTS": 0x190, "VTCORFERR": 0x1a0, "VTCORNERR": 0x1a4,
                        "VTCORERRCNT": 0x1a8, "VTUNCERRSTS": 0x1ac,  "VTUNCFERR": 0x1b8,
                        "VTUNCNERR": 0x1bc }
    
    VTCORERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
                        9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
                        16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    VTCORERRSTS_REG_INFO = {0: "VTCORERRSTS bit[0]: Iommu Tag Iotlb Par Err (IOMMU_TAG_IOTLB_PAR_ERR) : ",
                            1: "VTCORERRSTS bit[1]: Iommu Tag Sl L2 Par Err (IOMMU_TAG_SL_L2_PAR_ERR) : ",
                            2: "VTCORERRSTS bit[2]: Iommu Tag Sl L3 Par Err (IOMMU_TAG_SL_L3_PAR_ERR) : ",
                            3: "VTCORERRSTS bit[3]: Iommu Tag Sl L4 Par Err (IOMMU_TAG_SL_L4_PAR_ERR) : ",
                            4: "VTCORERRSTS bit[4]: Iommu Tag Sl L5 Par Err (IOMMU_TAG_SL_L5_PAR_ERR) : ",
                            5: "VTCORERRSTS bit[5]: Iommu Tag Fl L2 Par Err (IOMMU_TAG_FL_L2_PAR_ERR) : ",
                            6: "VTCORERRSTS bit[6]: Iommu Tag Fl L3 Par Err (IOMMU_TAG_FL_L3_PAR_ERR) : ",
                            7: "VTCORERRSTS bit[7]: Iommu Tag Fl L4 Par Err (IOMMU_TAG_FL_L4_PAR_ERR) : ",
                            8: "VTCORERRSTS bit[8]: Iommu Tag Fl L5 Par Err (IOMMU_TAG_FL_L5_PAR_ERR) : ",
                            9: "VTCORERRSTS bit[9]: Iommu Tag Pasid Par Err (IOMMU_TAG_PASID_PAR_ERR) : ",
                            10: "VTCORERRSTS bit[10]: Iommu Tag Rcc Par Err (IOMMU_TAG_RCC_PAR_ERR) : ",
                            11: "VTCORERRSTS bit[11]: Iommu Tag Ice Par Err (IOMMU_TAG_ICE_PAR_ERR) : ",
                            12: "VTCORERRSTS bit[12]: Iommu Data Sl L2 Par Err (IOMMU_DATA_SL_L2_PAR_ERR) : ",
                            13: "VTCORERRSTS bit[13]: Iommu Data Sl L3 Par Err (IOMMU_DATA_SL_L3_PAR_ERR) : ",
                            14: "VTCORERRSTS bit[14]: Iommu Data Sl L4 Par Err (IOMMU_DATA_SL_L4_PAR_ERR) : ",
                            15: "VTCORERRSTS bit[15]: Iommu Data Sl L5 Par Err (IOMMU_DATA_SL_L5_PAR_ERR) : ",
                            16: "VTCORERRSTS bit[16]: Iommu Data Fl L2 Par Err (IOMMU_DATA_FL_L2_PAR_ERR) : ",
                            17: "VTCORERRSTS bit[17]: Iommu Data Fl L3 Par Err (IOMMU_DATA_FL_L3_PAR_ERR) : ",
                            18: "VTCORERRSTS bit[18]: Iommu Data Fl L4 Par Err (IOMMU_DATA_FL_L4_PAR_ERR) : ",
                            19: "VTCORERRSTS bit[19]: Iommu Data Fl L5 Par Err (IOMMU_DATA_FL_L5_PAR_ERR) : ",
                            20: "VTCORERRSTS bit[20]: Iommu Data Pasid Err (IOMMU_DATA_PASID_ERR) : ",
                            21: "VTCORERRSTS bit[21]: Iommu Data Rcc Par Err (IOMMU_DATA_RCC_PAR_ERR) : ",
                            22: "VTCORERRSTS bit[22]: Iommu Data Ice Par Err (IOMMU_DATA_ICE_PAR_ERR) : ",
                            23: "VTCORERRSTS bit[23]: Iommu Data Pwt Other Par Err (IOMMU_DATA_PWT_OTHER_PAR_ERR) : "
    }

    VTCORFERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
                        9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
                        16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    VTCORFERR_REG_INFO = {0: "VTCORFERR bit[0]: Iommu Tag Iotlb Par Err (IOMMU_TAG_IOTLB_PAR_ERR) : ",
                            1: "VTCORFERR bit[1]: Iommu Tag Sl L2 Par Err (IOMMU_TAG_SL_L2_PAR_ERR) : ",
                            2: "VTCORFERR bit[2]: Iommu Tag Sl L3 Par Err (IOMMU_TAG_SL_L3_PAR_ERR) : ",
                            3: "VTCORFERR bit[3]: Iommu Tag Sl L4 Par Err (IOMMU_TAG_SL_L4_PAR_ERR) : ",
                            4: "VTCORFERR bit[4]: Iommu Tag Sl L5 Par Err (IOMMU_TAG_SL_L5_PAR_ERR) : ",
                            5: "VTCORFERR bit[5]: Iommu Tag Fl L2 Par Err (IOMMU_TAG_FL_L2_PAR_ERR) : ",
                            6: "VTCORFERR bit[6]: Iommu Tag Fl L3 Par Err (IOMMU_TAG_FL_L3_PAR_ERR) : ",
                            7: "VTCORFERR bit[7]: Iommu Tag Fl L4 Par Err (IOMMU_TAG_FL_L4_PAR_ERR) : ",
                            8: "VTCORFERR bit[8]: Iommu Tag Fl L5 Par Err (IOMMU_TAG_FL_L5_PAR_ERR) : ",
                            9: "VTCORFERR bit[9]: Iommu Tag Pasid Par Err (IOMMU_TAG_PASID_PAR_ERR) : ",
                            10: "VTCORFERR bit[10]: Iommu Tag Rcc Par Err (IOMMU_TAG_RCC_PAR_ERR) : ",
                            11: "VTCORFERR bit[11]: Iommu Tag Ice Par Err (IOMMU_TAG_ICE_PAR_ERR) : ",
                            12: "VTCORFERR bit[12]: Iommu Data Sl L2 Par Err (IOMMU_DATA_SL_L2_PAR_ERR) : ",
                            13: "VTCORFERR bit[13]: Iommu Data Sl L3 Par Err (IOMMU_DATA_SL_L3_PAR_ERR) : ",
                            14: "VTCORFERR bit[14]: Iommu Data Sl L4 Par Err (IOMMU_DATA_SL_L4_PAR_ERR) : ",
                            15: "VTCORFERR bit[15]: Iommu Data Sl L5 Par Err (IOMMU_DATA_SL_L5_PAR_ERR) : ",
                            16: "VTCORFERR bit[16]: Iommu Data Fl L2 Par Err (IOMMU_DATA_FL_L2_PAR_ERR) : ",
                            17: "VTCORFERR bit[17]: Iommu Data Fl L3 Par Err (IOMMU_DATA_FL_L3_PAR_ERR) : ",
                            18: "VTCORFERR bit[18]: Iommu Data Fl L4 Par Err (IOMMU_DATA_FL_L4_PAR_ERR) : ",
                            19: "VTCORFERR bit[19]: Iommu Data Fl L5 Par Err (IOMMU_DATA_FL_L5_PAR_ERR) : ",
                            20: "VTCORFERR bit[20]: Iommu Data Pasid Err (IOMMU_DATA_PASID_ERR) : ",
                            21: "VTCORFERR bit[21]: Iommu Data Rcc Par Err (IOMMU_DATA_RCC_PAR_ERR) : ",
                            22: "VTCORFERR bit[22]: Iommu Data Ice Par Err (IOMMU_DATA_ICE_PAR_ERR) : ",
                            23: "VTCORFERR bit[23]: Iommu Data Pwt Other Par Err (IOMMU_DATA_PWT_OTHER_PAR_ERR) : "
    }

    VTCORNERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
                    9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
                    16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    VTCORNERR_REG_INFO = {0: "VTCORNERR bit[0]: Iommu Tag Iotlb Par Err (IOMMU_TAG_IOTLB_PAR_ERR) : ",
                            1: "VTCORNERR bit[1]: Iommu Tag Sl L2 Par Err (IOMMU_TAG_SL_L2_PAR_ERR) : ",
                            2: "VTCORNERR bit[2]: Iommu Tag Sl L3 Par Err (IOMMU_TAG_SL_L3_PAR_ERR) : ",
                            3: "VTCORNERR bit[3]: Iommu Tag Sl L4 Par Err (IOMMU_TAG_SL_L4_PAR_ERR) : ",
                            4: "VTCORNERR bit[4]: Iommu Tag Sl L5 Par Err (IOMMU_TAG_SL_L5_PAR_ERR) : ",
                            5: "VTCORNERR bit[5]: Iommu Tag Fl L2 Par Err (IOMMU_TAG_FL_L2_PAR_ERR) : ",
                            6: "VTCORNERR bit[6]: Iommu Tag Fl L3 Par Err (IOMMU_TAG_FL_L3_PAR_ERR) : ",
                            7: "VTCORNERR bit[7]: Iommu Tag Fl L4 Par Err (IOMMU_TAG_FL_L4_PAR_ERR) : ",
                            8: "VTCORNERR bit[8]: Iommu Tag Fl L5 Par Err (IOMMU_TAG_FL_L5_PAR_ERR) : ",
                            9: "VTCORNERR bit[9]: Iommu Tag Pasid Par Err (IOMMU_TAG_PASID_PAR_ERR) : ",
                            10: "VTCORNERR bit[10]: Iommu Tag Rcc Par Err (IOMMU_TAG_RCC_PAR_ERR) : ",
                            11: "VTCORNERR bit[11]: Iommu Tag Ice Par Err (IOMMU_TAG_ICE_PAR_ERR) : ",
                            12: "VTCORNERR bit[12]: Iommu Data Sl L2 Par Err (IOMMU_DATA_SL_L2_PAR_ERR) : ",
                            13: "VTCORNERR bit[13]: Iommu Data Sl L3 Par Err (IOMMU_DATA_SL_L3_PAR_ERR) : ",
                            14: "VTCORNERR bit[14]: Iommu Data Sl L4 Par Err (IOMMU_DATA_SL_L4_PAR_ERR) : ",
                            15: "VTCORNERR bit[15]: Iommu Data Sl L5 Par Err (IOMMU_DATA_SL_L5_PAR_ERR) : ",
                            16: "VTCORNERR bit[16]: Iommu Data Fl L2 Par Err (IOMMU_DATA_FL_L2_PAR_ERR) : ",
                            17: "VTCORNERR bit[17]: Iommu Data Fl L3 Par Err (IOMMU_DATA_FL_L3_PAR_ERR) : ",
                            18: "VTCORNERR bit[18]: Iommu Data Fl L4 Par Err (IOMMU_DATA_FL_L4_PAR_ERR) : ",
                            19: "VTCORNERR bit[19]: Iommu Data Fl L5 Par Err (IOMMU_DATA_FL_L5_PAR_ERR) : ",
                            20: "VTCORNERR bit[20]: Iommu Data Pasid Err (IOMMU_DATA_PASID_ERR) : ",
                            21: "VTCORNERR bit[21]: Iommu Data Rcc Par Err (IOMMU_DATA_RCC_PAR_ERR) : ",
                            22: "VTCORNERR bit[22]: Iommu Data Ice Par Err (IOMMU_DATA_ICE_PAR_ERR) : ",
                            23: "VTCORNERR bit[23]: Iommu Data Pwt Other Par Err (IOMMU_DATA_PWT_OTHER_PAR_ERR) : "
    }

    VTCORERRCNT_BIT = {0: 6, 7: 7}
    VTCORERRCNT_REG_INFO = {0: "VTCORERRCNT bits[0:6] ERRCNT : ", 7: "VTCORERRCNT bit[7] ERROVF : "}

    VTUNCERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
    VTUNCERRSTS_REG_INFO = {0: "VTUNCERRSTS bit[0] Iommu Data Iotlb Par Err (IOMMU_DATA_IOTLB_PAR_ERR) : ",
                            1: "VTUNCERRSTS bit[1] Pq Req Par Err (PQ_REQ_PAR_ERR) : ",
                            2: "VTUNCERRSTS bit[2] Pwt Req Par Err (PWT_REQ_PAR_ERR) : ",
                            3: "VTUNCERRSTS bit[3] Iommu Mem Resp Abort (IOMMU_MEM_RESP_ABORT) : ",
                            16: "VTUNCERRSTS bit[16] Pmr Check Abort (PMR_CHECK_ABORT) : ",
                            17: "VTUNCERRSTS bit[17] Hpa Overflow (HPA_OVERFLOW) : ",
                            18: "VTUNCERRSTS bit[18] Gpa Overflow (GPA_OVERFLOW) : ",
                            19: "VTUNCERRSTS bit[19] Illegal Msi (ILLEGAL_MSI) : ",
                            20: "VTUNCERRSTS bit[20] At Translated Illegal Device (AT_TRANSLATED_ILLEGAL_DEVICE) : "
    }

    VTUNCFERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
    VTUNCFERR_REG_INFO = {0: "VTUNCFERR bit[0] Iommu Data Iotlb Par Err (IOMMU_DATA_IOTLB_PAR_ERR) : ",
                            1: "VTUNCFERR bit[1] Pq Req Par Err (PQ_REQ_PAR_ERR) : ",
                            2: "VTUNCFERR bit[2] Pwt Req Par Err (PWT_REQ_PAR_ERR) : ",
                            3: "VTUNCFERR bit[3] Iommu Mem Resp Abort (IOMMU_MEM_RESP_ABORT) : ",
                            16: "VTUNCFERR bit[16] Pmr Check Abort (PMR_CHECK_ABORT) : ",
                            17: "VTUNCFERR bit[17] Hpa Overflow (HPA_OVERFLOW) : ",
                            18: "VTUNCFERR bit[18] Gpa Overflow (GPA_OVERFLOW) : ",
                            19: "VTUNCFERR bit[19] Illegal Msi (ILLEGAL_MSI) : ",
                            20: "VTUNCFERR bit[20] At Translated Illegal Device (AT_TRANSLATED_ILLEGAL_DEVICE) : "
    }

    VTUNCNERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
    VTUNCNERR_REG_INFO = {0: "VTUNCNERR bit[0] Iommu Data Iotlb Par Err (IOMMU_DATA_IOTLB_PAR_ERR) : ",
                            1: "VTUNCNERR bit[1] Pq Req Par Err (PQ_REQ_PAR_ERR) : ",
                            2: "VTUNCNERR bit[2] Pwt Req Par Err (PWT_REQ_PAR_ERR) : ",
                            3: "VTUNCNERR bit[3] Iommu Mem Resp Abort (IOMMU_MEM_RESP_ABORT) : ",
                            16: "VTUNCNERR bit[16] Pmr Check Abort (PMR_CHECK_ABORT) : ",
                            17: "VTUNCNERR bit[17] Hpa Overflow (HPA_OVERFLOW) : ",
                            18: "VTUNCNERR bit[18] Gpa Overflow (GPA_OVERFLOW) : ",
                            19: "VTUNCNERR bit[19] Illegal Msi (ILLEGAL_MSI) : ",
                            20: "VTUNCNERR bit[20] At Translated Illegal Device (AT_TRANSLATED_ILLEGAL_DEVICE) : "
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dist_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dist_reg_addr[reg] - 0x190
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dist_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                            output = output + output_tmp
    except Exception as e:
        output = output + "Parse Vt-d err failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Vt-d part : " + output + "\n"
    return output

def parse_peci_mesh_D1734(value):
    list_key_name = {"B0D0F1Addr260", "B1D0F1Addr260", "B2D0F1Addr260", "B3D0F1Addr260", 
                        "B4D0F1Addr260", "B5D0F1Addr260"}
    dist_reg_addr = {"R2PINGERRLOG0": 0x260, "R2EGRERRLOG": 0x264, "R2EGRPRQERRLOG0": 0x270,
                    "R2EGRPRQERRLOG1": 0x274}
    R2PINGERRLOG0_BIT = {0: 0, 1: 1, 2: 2, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 14: 14, 15: 15}
    R2PINGERRLOG0_REG_INFO = {0: "R2PINGERRLOG0 bit[0] AK0BGFCRDOVERFLOW : ", 1: "R2PINGERRLOG0 bit[1] AK1BGFCRDOVERFLOW : ",
                                2: "R2PINGERRLOG0 bit[2] BLBGFCRDOVERFLOW : ", 7: "R2PINGERRLOG0 bit[7]: IIOIDICRDOVERFLOW : ",
                                8: "R2PINGERRLOG0 bit[8] IIONCBCRDOVERFLOW : ", 9: "R2PINGERRLOG0 bit[9] IIONCSCRDOVERFLOW : ",
                                10: "R2PINGERRLOG0 bit[10] PARERRING0 : ", 11: "R2PINGERRLOG0 bit[11] PARERRING0INJDONE : ",
                                14: "R2PINGERRLOG0 bit[14] IVBGFCRDOVERFLOW : ", 15: "R2PINGERRLOG0 bit[15] IVSNPCRDOVERFLOW : "
    }

    R2EGRERRLOG_BIT = {18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24,
                        25: 25, 26: 26, 27: 27, 28: 28, 29: 29 }
    R2EGRERRLOG_REG_INFO = {18: "R2EGRERRLOG bit[18] Akegress0 Write To Valid Entry : ", 19: "R2EGRERRLOG bit[19]: Akegress1 Write To Valid Entry : ",
                            20: "R2EGRERRLOG bit[20] Blegress0 Write To Valid Entry : ", 21: "R2EGRERRLOG bit[21]: Blegress1 Write To Valid Entry : ",
                            22: "R2EGRERRLOG bit[22] Adegress0 Write To Valid Entry : ", 23: "R2EGRERRLOG bit[23]: Adegress1 Write To Valid Entry : ",
                            24: "R2EGRERRLOG bit[24] Akegress0 Overflow : ", 25: "R2EGRERRLOG bit[25] Akegress1 Overflow : ",
                            26: "R2EGRERRLOG bit[26] Blegress0 Overflow : ", 27: "R2EGRERRLOG bit[27] Blegress1 Overflow : ",
                            28: "R2EGRERRLOG bit[28] Adegress0 Overflow : ", 29: "R2EGRERRLOG bit[29] Adegress1 Overflow : "
    }

    R2EGRPRQERRLOG0_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    R2EGRPRQERRLOG0_REG_INFO = {0: "R2EGRPRQERRLOG0 bit[0] CBOPRQCRDOVERFLOW_31_00_00 : ", 1 : "R2EGRPRQERRLOG0 bit[1] CBOPRQCRDOVERFLOW_31_00_01 : ",
                                2: "R2EGRPRQERRLOG0 bit[2] CBOPRQCRDOVERFLOW_31_00_02 : ", 3 : "R2EGRPRQERRLOG0 bit[3] CBOPRQCRDOVERFLOW_31_00_03 : ",
                                4: "R2EGRPRQERRLOG0 bit[4] CBOPRQCRDOVERFLOW_31_00_04 : ", 5 : "R2EGRPRQERRLOG0 bit[5] CBOPRQCRDOVERFLOW_31_00_05 : ",
                                6: "R2EGRPRQERRLOG0 bit[6] CBOPRQCRDOVERFLOW_31_00_06 : ", 7 : "R2EGRPRQERRLOG0 bit[7] CBOPRQCRDOVERFLOW_31_00_07 : ",
                                8: "R2EGRPRQERRLOG0 bit[8] CBOPRQCRDOVERFLOW_31_00_08 : ", 9 : "R2EGRPRQERRLOG0 bit[9] CBOPRQCRDOVERFLOW_31_00_09 : ",
                                10: "R2EGRPRQERRLOG0 bit[10] CBOPRQCRDOVERFLOW_31_00_10 : ", 11 : "R2EGRPRQERRLOG0 bit[11] CBOPRQCRDOVERFLOW_31_00_11 : ",
                                12: "R2EGRPRQERRLOG0 bit[12] CBOPRQCRDOVERFLOW_31_00_12 : ", 13 : "R2EGRPRQERRLOG0 bit[13] CBOPRQCRDOVERFLOW_31_00_13 : ",
                                14: "R2EGRPRQERRLOG0 bit[14] CBOPRQCRDOVERFLOW_31_00_14 : ", 15 : "R2EGRPRQERRLOG0 bit[15] CBOPRQCRDOVERFLOW_31_00_15 : ",
                                16: "R2EGRPRQERRLOG0 bit[16] CBOPRQCRDOVERFLOW_31_00_16 : ", 17 : "R2EGRPRQERRLOG0 bit[17] CBOPRQCRDOVERFLOW_31_00_17 : ",
                                18: "R2EGRPRQERRLOG0 bit[18] CBOPRQCRDOVERFLOW_31_00_18 : ", 19 : "R2EGRPRQERRLOG0 bit[19] CBOPRQCRDOVERFLOW_31_00_19 : ",
                                20: "R2EGRPRQERRLOG0 bit[20] CBOPRQCRDOVERFLOW_31_00_20 : ", 21 : "R2EGRPRQERRLOG0 bit[21] CBOPRQCRDOVERFLOW_31_00_21 : ",
                                22: "R2EGRPRQERRLOG0 bit[22] CBOPRQCRDOVERFLOW_31_00_22 : ", 23 : "R2EGRPRQERRLOG0 bit[23] CBOPRQCRDOVERFLOW_31_00_23 : ",
                                24: "R2EGRPRQERRLOG0 bit[24] CBOPRQCRDOVERFLOW_31_00_24 : ", 25 : "R2EGRPRQERRLOG0 bit[25] CBOPRQCRDOVERFLOW_31_00_25 : ",
                                26: "R2EGRPRQERRLOG0 bit[26] CBOPRQCRDOVERFLOW_31_00_26 : ", 27 : "R2EGRPRQERRLOG0 bit[27] CBOPRQCRDOVERFLOW_31_00_27 : ",
                                28: "R2EGRPRQERRLOG0 bit[28] CBOPRQCRDOVERFLOW_31_00_28 : ", 29 : "R2EGRPRQERRLOG0 bit[29] CBOPRQCRDOVERFLOW_31_00_29 : ",
                                30: "R2EGRPRQERRLOG0 bit[30] CBOPRQCRDOVERFLOW_31_00_30 : ", 31 : "R2EGRPRQERRLOG0 bit[31] CBOPRQCRDOVERFLOW_31_00_31 : "
    }
    R2EGRPRQERRLOG1_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}

    R2EGRPRQERRLOG1_REG_INFO= {0: "R2EGRPRQERRLOG1 bit[0] CBOPRQCRDOVERFLOW_63_32_00 : ", 1 : "R2EGRPRQERRLOG1 bit[1] CBOPRQCRDOVERFLOW_63_32_01 : ",
                                2: "R2EGRPRQERRLOG1 bit[2] CBOPRQCRDOVERFLOW_63_32_02 : ", 3 : "R2EGRPRQERRLOG1 bit[3] CBOPRQCRDOVERFLOW_63_32_03 : ",
                                4: "R2EGRPRQERRLOG1 bit[4] CBOPRQCRDOVERFLOW_63_32_04 : ", 5 : "R2EGRPRQERRLOG1 bit[5] CBOPRQCRDOVERFLOW_63_32_05 : ",
                                6: "R2EGRPRQERRLOG1 bit[6] CBOPRQCRDOVERFLOW_63_32_06 : ", 7 : "R2EGRPRQERRLOG1 bit[7] CBOPRQCRDOVERFLOW_63_32_07 : ",
                                8: "R2EGRPRQERRLOG1 bit[8] CBOPRQCRDOVERFLOW_63_32_08 : ", 9 : "R2EGRPRQERRLOG1 bit[9] CBOPRQCRDOVERFLOW_63_32_09 : ",
                                10: "R2EGRPRQERRLOG1 bit[10] CBOPRQCRDOVERFLOW_63_32_10 : ", 11 : "R2EGRPRQERRLOG1 bit[11] CBOPRQCRDOVERFLOW_63_32_11 : ",
                                12: "R2EGRPRQERRLOG1 bit[12] CBOPRQCRDOVERFLOW_63_32_12 : ", 13 : "R2EGRPRQERRLOG1 bit[13] CBOPRQCRDOVERFLOW_63_32_13 : ",
                                14: "R2EGRPRQERRLOG1 bit[14] CBOPRQCRDOVERFLOW_63_32_14 : ", 15 : "R2EGRPRQERRLOG1 bit[15] CBOPRQCRDOVERFLOW_63_32_15 : ",
                                16: "R2EGRPRQERRLOG1 bit[16] CBOPRQCRDOVERFLOW_63_32_16 : ", 17 : "R2EGRPRQERRLOG1 bit[17] CBOPRQCRDOVERFLOW_63_32_17 : ",
                                18: "R2EGRPRQERRLOG1 bit[18] CBOPRQCRDOVERFLOW_63_32_18 : ", 19 : "R2EGRPRQERRLOG1 bit[19] CBOPRQCRDOVERFLOW_63_32_19 : ",
                                20: "R2EGRPRQERRLOG1 bit[20] CBOPRQCRDOVERFLOW_63_32_20 : ", 21 : "R2EGRPRQERRLOG1 bit[21] CBOPRQCRDOVERFLOW_63_32_21 : ",
                                22: "R2EGRPRQERRLOG1 bit[22] CBOPRQCRDOVERFLOW_63_32_22 : ", 23 : "R2EGRPRQERRLOG1 bit[23] CBOPRQCRDOVERFLOW_63_32_23 : ",
                                24: "R2EGRPRQERRLOG1 bit[24] CBOPRQCRDOVERFLOW_63_32_24 : ", 25 : "R2EGRPRQERRLOG1 bit[25] CBOPRQCRDOVERFLOW_63_32_25 : ",
                                26: "R2EGRPRQERRLOG1 bit[26] CBOPRQCRDOVERFLOW_63_32_26 : ", 27 : "R2EGRPRQERRLOG1 bit[27] CBOPRQCRDOVERFLOW_63_32_27 : ",
                                28: "R2EGRPRQERRLOG1 bit[28] CBOPRQCRDOVERFLOW_63_32_28 : ", 29 : "R2EGRPRQERRLOG1 bit[29] CBOPRQCRDOVERFLOW_63_32_29 : ",
                                30: "R2EGRPRQERRLOG1 bit[30] CBOPRQCRDOVERFLOW_63_32_30 : ", 31 : "R2EGRPRQERRLOG1 bit[31] CBOPRQCRDOVERFLOW_63_32_31 : "
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dist_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dist_reg_addr[reg] - 0x260
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dist_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse mesh failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output = "Mesh 2 pcie part : " + output + "\n"
    return output

def parse_peci_ras_D1734(value):
    list_key_name = {"B0D0F2Addrb0", "B1D0F2Addrb0", "B2D0F2Addrb0", "B3D0F2Addrb0", 
                        "B4D0F2Addrb0", "B5D0F2Addrb0", "B0D0F2Addr208", "B1D0F2Addr208", 
                        "B2D0F2Addr208", "B3D0F2Addr208", "B4D0F2Addr208", "B5D0F2Addr208",
                        "B0D0F2Addr2a0", "B1D0F2Addr2a0", "B2D0F2Addr2a0", "B3D0F2Addr2a0",
                        "B4D0F2Addr2a0", "B5D0F2Addr2a0"
    }

    dist_reg_addr = {"M2IOSFRASERR_1_0_2_CFG": 0xb0, "M2IOSFRASERRST_1_0_2_CFG": 0xb4, "IRPRINGERRST_1_5_2_CFG": 0x208, "IRPRINGFFERRST_1_5_2_CFG": 0x210,
                        "IRPRINGFNERRST_1_5_2_CFG": 0x214, "IRPRINGNFERRST_1_5_2_CFG": 0x218, "IRPRINGNNERRST_1_5_2_CFG": 0x21c, "IRPRINGERRCNT_1_5_2_CFG": 0x224,
                        "IRPRINGMISC_1_5_2_CFG": 0x228, "IRPERRST_1_5_2_CFG": 0x230, "IRPFFERRST_1_5_2_CFG": 0x238, "IRPFNERRST_1_5_2_CFG": 0x23c,
                        "IRPFFERRHD0_1_5_2_CFG": 0x240, "IRPFFERRHD1_1_5_2_CFG": 0x244, "IRPFFERRHD2_1_5_2_CFG": 0x248, "IRPFFERRHD3_1_5_2_CFG": 0x24c,
                        "IRPNFERRST_1_5_2_CFG": 0x250, "IRPNNERRST_1_5_2_CFG": 0x254, "IRPNFERRHD0_1_5_2_CFG": 0x258, "IRPNFERRHD1_1_5_2_CFG": 0x25c,
                        "IRPNFERRHD2_1_5_2_CFG": 0x260, "IRPNFERRHD3_1_5_2_CFG": 0x264, "IRPERRCNT_1_5_2_CFG": 0x26c, "ITCERRST_1_5_2_CFG": 0x270,
                        "TCERRCNT_1_5_2_CFG": 0x274, "ITCFFERRST_1_5_2_CFG": 0x2a0, "ITCFFERRHD0_1_5_2_CFG": 0x2a4, "ITCFFERRHD1_1_5_2_CFG": 0x2a8,
                        "ITCFFERRHD2_1_5_2_CFG": 0x2ac, "ITCFFERRHD3_1_5_2_CFG": 0x2b0, "ITCFNERRST_1_5_2_CFG": 0x2b4, "ITCNFERRST_1_5_2_CFG": 0x2b8,
                        "ITCNFERRHD0_1_5_2_CFG": 0x2bc, "ITCNFERRHD1_1_5_2_CFG": 0x2c0, "ITCNFERRHD2_1_5_2_CFG": 0x2c4, "ITCNFERRHD3_1_5_2_CFG": 0x2c8,
                        "ITCNNERRST_1_5_2_CFG": 0x2cc, "OTCFFERRST_1_5_2_CFG": 0x2d0, "OTCFFERRHD0_1_5_2_CFG": 0x2d4, "OTCFFERRHD1_1_5_2_CFG": 0x2d8,
                        "OTCFFERRHD2_1_5_2_CFG": 0x2dc, "OTCFFERRHD3_1_5_2_CFG": 0x2e0, "OTCFNERRST_1_5_2_CFG": 0x2e4, "OTCNFERRST_1_5_2_CFG": 0x2e8,
                        "OTCNFERRHD0_1_5_2_CFG": 0x2ec, "OTCNFERRHD1_1_5_2_CFG": 0x2f0, "OTCNFERRHD2_1_5_2_CFG": 0x2f4, "OTCNFERRHD3_1_5_2_CFG": 0x2f8,
                        "OTCNNERRST_1_5_2_CFG": 0x2fc, "TC_ERR_MISCLOG_1_5_2_CFG": 0x310, "IRPP0PLSR0_1_5_2_CFG": 0x370, "IRPP0PLSR1_1_5_2_CFG": 0x374,
                        "IRPP0PLSR2_1_5_2_CFG": 0x378, "OTCERRST_1_5_2_CFG": 0x380
    }

    M2IOSFRASERR_1_0_2_CFG_BIT = {0: 0, 1: 2, 3: 5, 6: 6, 7: 8, 9: 11}
    M2IOSFRASERR_1_0_2_CFG_REG_INFO = {0: "M2IOSFRASERR_1_0_2_CFG bit[0] RAS_STS_FIRST_ERR : ", 1: "M2IOSFRASERR_1_0_2_CFG bits[1:2] RAS_SEV_FIRST_ERR : ",
                                        3: "M2IOSFRASERR_1_0_2_CFG bits[3:5] RAS_FUNC_FIRST_ERR : ", 6: "M2IOSFRASERR_1_0_2_CFG bit[6] RAS_STS_NEXT_ERR : ",
                                        7: "M2IOSFRASERR_1_0_2_CFG bits[7:8] RAS_SEV_NEXT_ERR : ", 9: "M2IOSFRASERR_1_0_2_CFG bits[9:11] RAS_FUNC_NEXT_ERR : "
    }

    M2IOSFRASERRST_1_0_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12}
    M2IOSFRASERRST_1_0_2_CFG_REG_INFO = {0: "M2IOSFRASERRST_1_0_2_CFG bit[0] ITC_SEV0_ERR_ST : ", 1: "M2IOSFRASERRST_1_0_2_CFG bit[1] ITC_SEV1_ERR_ST : ",
                                            2: "M2IOSFRASERRST_1_0_2_CFG bit[2] ITC_SEV2_ERR_ST : ", 3: "M2IOSFRASERRST_1_0_2_CFG bit[3] OTC_SEV0_ERR_ST : ",
                                            4: "M2IOSFRASERRST_1_0_2_CFG bit[4] OTC_SEV1_ERR_ST : ", 5: "M2IOSFRASERRST_1_0_2_CFG bit[5] OTC_SEV2_ERR_ST : ",
                                            6: "M2IOSFRASERRST_1_0_2_CFG bit[6] IRP_SEV0_ERR_ST : ", 7: "M2IOSFRASERRST_1_0_2_CFG bit[7] IRP_SEV1_ERR_ST : ",
                                            8: "M2IOSFRASERRST_1_0_2_CFG bit[8] IRP_SEV2_ERR_ST : ", 9: "M2IOSFRASERRST_1_0_2_CFG bit[9] M2PCIE_SEV2_ERR_ST : ",
                                            10: "M2IOSFRASERRST_1_0_2_CFG bit[10] VT_SEV0_ERR_ST : ", 11: "M2IOSFRASERRST_1_0_2_CFG bit[11] VT_SEV1_ERR_ST : ",
                                            12: "M2IOSFRASERRST_1_0_2_CFG bit[12] VT_SEV2_ERR_ST : "
    }

    IRPRINGERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13}
    IRPRINGERRST_1_5_2_CFG_REG_INFO = {0: "IRPRINGERRST_1_5_2_CFG bit[0] BL_PARITY_ERROR : ", 1: "IRPRINGERRST_1_5_2_CFG bit[1] SNP_ADDR_PARITY_ERROR : ",
                                            2: "IRPRINGERRST_1_5_2_CFG bit[2] RXDATA1_PARITY_ERROR : ", 3: "IRPRINGERRST_1_5_2_CFG bit[3] RXDATA0_PARITY_ERROR : ",
                                            4: "IRPRINGERRST_1_5_2_CFG bit[4] BLQ_PARITY_ERROR : ", 5: "IRPRINGERRST_1_5_2_CFG bit[5] BL_ECC_CORRECTED_ERROR : ",
                                            6: "IRPRINGERRST_1_5_2_CFG bit[6] BL_ECC_UNCORRECTABLE_ERROR : ", 7: "IRPRINGERRST_1_5_2_CFG bit[7] BL_CQID_PARITY_ERROR : ",
                                            8: "IRPRINGERRST_1_5_2_CFG bit[8] AK0_CQID_PARITY_ERROR : ", 9: "IRPRINGERRST_1_5_2_CFG bit[9] AK1_CQID_PARITY_ERROR : ",
                                            10: "IRPRINGERRST_1_5_2_CFG bit[10] TXQ0_ADDR_PAR_ERROR : ", 11: "IRPRINGERRST_1_5_2_CFG bit[11] TXQ1_ADDR_PAR_ERROR : ",
                                            12: "IRPRINGERRST_1_5_2_CFG bit[12] SNPQ_RF_ADDR_PARITY_ERROR : ", 13: "IRPRINGERRST_1_5_2_CFG bit[13] UNEXPECTED_GO_ERR_RCVD : "
    }

    IRPRINGFFERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13}
    IRPRINGFFERRST_1_5_2_CFG_REG_INFO = {0: "IRPRINGFFERRST_1_5_2_CFG bit[0] BL_PARITY_ERROR : ", 1: "IRPRINGFFERRST_1_5_2_CFG bit[1] SNP_ADDR_PARITY_ERROR : ",
                                            2: "IRPRINGFFERRST_1_5_2_CFG bit[2] RXDATA1_PARITY_ERROR : ", 3: "IRPRINGFFERRST_1_5_2_CFG bit[3] RXDATA0_PARITY_ERROR : ",
                                            4: "IRPRINGFFERRST_1_5_2_CFG bit[4] BLQ_PARITY_ERROR : ", 5: "IRPRINGFFERRST_1_5_2_CFG bit[5] BL_ECC_CORRECTED_ERROR : ",
                                            6: "IRPRINGFFERRST_1_5_2_CFG bit[6] BL_ECC_UNCORRECTABLE_ERROR : ", 7: "IRPRINGFFERRST_1_5_2_CFG bit[7] BL_CQID_PARITY_ERROR : ",
                                            8: "IRPRINGFFERRST_1_5_2_CFG bit[8] AK0_CQID_PARITY_ERROR : ", 9: "IRPRINGFFERRST_1_5_2_CFG bit[9] AK1_CQID_PARITY_ERROR : ",
                                            10: "IRPRINGFFERRST_1_5_2_CFG bit[10] TXQ0_ADDR_PAR_ERROR : ", 11: "IRPRINGFFERRST_1_5_2_CFG bit[11] TXQ1_ADDR_PAR_ERROR : ",
                                            12: "IRPRINGFFERRST_1_5_2_CFG bit[12] SNPQ_RF_ADDR_PARITY_ERROR : ", 13: "IRPRINGFFERRST_1_5_2_CFG bit[13] UNEXPECTED_GO_ERR_RCVD : "
    }

    IRPRINGFNERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13}
    IRPRINGFNERRST_1_5_2_CFG_REG_INFO = {0: "IRPRINGFNERRST_1_5_2_CFG bit[0] BL_PARITY_ERROR : ", 1: "IRPRINGFNERRST_1_5_2_CFG bit[1] SNP_ADDR_PARITY_ERROR : ",
                                            2: "IRPRINGFNERRST_1_5_2_CFG bit[2] RXDATA1_PARITY_ERROR : ", 3: "IRPRINGFNERRST_1_5_2_CFG bit[3] RXDATA0_PARITY_ERROR : ",
                                            4: "IRPRINGFNERRST_1_5_2_CFG bit[4] BLQ_PARITY_ERROR : ", 5: "IRPRINGFNERRST_1_5_2_CFG bit[5] BL_ECC_CORRECTED_ERROR : ",
                                            6: "IRPRINGFNERRST_1_5_2_CFG bit[6] BL_ECC_UNCORRECTABLE_ERROR : ", 7: "IRPRINGFNERRST_1_5_2_CFG bit[7] BL_CQID_PARITY_ERROR : ",
                                            8: "IRPRINGFNERRST_1_5_2_CFG bit[8] AK0_CQID_PARITY_ERROR : ", 9: "IRPRINGFNERRST_1_5_2_CFG bit[9] AK1_CQID_PARITY_ERROR : ",
                                            10: "IRPRINGFNERRST_1_5_2_CFG bit[10] TXQ0_ADDR_PAR_ERROR : ", 11: "IRPRINGFNERRST_1_5_2_CFG bit[11] TXQ1_ADDR_PAR_ERROR : ",
                                            12: "IRPRINGFNERRST_1_5_2_CFG bit[12] SNPQ_RF_ADDR_PARITY_ERROR : ", 13: "IRPRINGFNERRST_1_5_2_CFG bit[13] UNEXPECTED_GO_ERR_RCVD : "
    }

    IRPRINGNFERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13}
    IRPRINGNFERRST_1_5_2_CFG_REG_INFO = {0: "IRPRINGNFERRST_1_5_2_CFG bit[0] BL_PARITY_ERROR : ", 1: "IRPRINGNFERRST_1_5_2_CFG bit[1] SNP_ADDR_PARITY_ERROR : ",
                                            2: "IRPRINGNFERRST_1_5_2_CFG bit[2] RXDATA1_PARITY_ERROR : ", 3: "IRPRINGNFERRST_1_5_2_CFG bit[3] RXDATA0_PARITY_ERROR : ",
                                            4: "IRPRINGNFERRST_1_5_2_CFG bit[4] BLQ_PARITY_ERROR : ", 5: "IRPRINGNFERRST_1_5_2_CFG bit[5] BL_ECC_CORRECTED_ERROR : ",
                                            6: "IRPRINGNFERRST_1_5_2_CFG bit[6] BL_ECC_UNCORRECTABLE_ERROR : ", 7: "IRPRINGNFERRST_1_5_2_CFG bit[7] BL_CQID_PARITY_ERROR : ",
                                            8: "IRPRINGNFERRST_1_5_2_CFG bit[8] AK0_CQID_PARITY_ERROR : ", 9: "IRPRINGNFERRST_1_5_2_CFG bit[9] AK1_CQID_PARITY_ERROR : ",
                                            10: "IRPRINGNFERRST_1_5_2_CFG bit[10] TXQ0_ADDR_PAR_ERROR : ", 11: "IRPRINGNFERRST_1_5_2_CFG bit[11] TXQ1_ADDR_PAR_ERROR : ",
                                            12: "IRPRINGNFERRST_1_5_2_CFG bit[12] SNPQ_RF_ADDR_PARITY_ERROR : ", 13: "IRPRINGNFERRST_1_5_2_CFG bit[13] UNEXPECTED_GO_ERR_RCVD : "
    }

    IRPRINGNNERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13}
    IRPRINGNNERRST_1_5_2_CFG_REG_INFO = {0: "IRPRINGNNERRST_1_5_2_CFG bit[0] BL_PARITY_ERROR : ", 1: "IRPRINGNNERRST_1_5_2_CFG bit[1] SNP_ADDR_PARITY_ERROR : ",
                                            2: "IRPRINGNNERRST_1_5_2_CFG bit[2] RXDATA1_PARITY_ERROR : ", 3: "IRPRINGNNERRST_1_5_2_CFG bit[3] RXDATA0_PARITY_ERROR : ",
                                            4: "IRPRINGNNERRST_1_5_2_CFG bit[4] BLQ_PARITY_ERROR : ", 5: "IRPRINGNNERRST_1_5_2_CFG bit[5] BL_ECC_CORRECTED_ERROR : ",
                                            6: "IRPRINGNNERRST_1_5_2_CFG bit[6] BL_ECC_UNCORRECTABLE_ERROR : ", 7: "IRPRINGNNERRST_1_5_2_CFG bit[7] BL_CQID_PARITY_ERROR : ",
                                            8: "IRPRINGNNERRST_1_5_2_CFG bit[8] AK0_CQID_PARITY_ERROR : ", 9: "IRPRINGNNERRST_1_5_2_CFG bit[9] AK1_CQID_PARITY_ERROR : ",
                                            10: "IRPRINGNNERRST_1_5_2_CFG bit[10] TXQ0_ADDR_PAR_ERROR : ", 11: "IRPRINGNNERRST_1_5_2_CFG bit[11] TXQ1_ADDR_PAR_ERROR : ",
                                            12: "IRPRINGNNERRST_1_5_2_CFG bit[12] SNPQ_RF_ADDR_PARITY_ERROR : ", 13: "IRPRINGNNERRST_1_5_2_CFG bit[13] UNEXPECTED_GO_ERR_RCVD : "
    }

    IRPRINGERRCNT_1_5_2_CFG_BIT = {0: 6, 7: 7}
    IRPRINGERRCNT_1_5_2_CFG_REG_INFO = {0: "IRPRINGERRCNT_1_5_2_CFG bits[0:6] ERRCNT : ", 7: "IRPRINGERRCNT_1_5_2_CFG bit[7] ERROVF : "}

    IRPRINGMISC_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    IRPRINGMISC_1_5_2_CFG_REG_INFO = {0: "IRPRINGMISC_1_5_2_CFG bit[0] BL_PARITY_BITS_0 : ", 1: "IRPRINGMISC_1_5_2_CFG bit[1] BL_PARITY_BITS_1 : ",
                                        2: "IRPRINGMISC_1_5_2_CFG bit[2] BL_PARITY_BITS_2 : ", 3: "IRPRINGMISC_1_5_2_CFG bit[3] BL_PARITY_BITS_3 : ",
                                        4: "IRPRINGMISC_1_5_2_CFG bit[4] BL_PARITY_BITS_4 : "
    }

    IRPERRST_1_5_2_CFG_BIT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10, 13: 13, 14: 14, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
    IRPERRST_1_5_2_CFG_REG_INFO = {1: "IRPERRST_1_5_2_CFG bit[1] WRCACHE_CORRECC_ERROR_CS0 : ", 2: "IRPERRST_1_5_2_CFG bit[2] WRCACHE_CORRECC_ERROR_CS1 : ",
                                    3: "IRPERRST_1_5_2_CFG bit[3] PROTOCOL_RCVD_POISON : ", 4: "IRPERRST_1_5_2_CFG bit[4] WRCACHE_UNCECC_ERROR_CS0 : ",
                                    5: "IRPERRST_1_5_2_CFG bit[5] WRCACHE_UNCECC_ERROR_CS1 : ", 6: "IRPERRST_1_5_2_CFG bit[6] CSR_ACC_32B_UNALIGNED : ",
                                    10: "IRPERRST_1_5_2_CFG bit[10] PROTOCOL_RCVD_UNEXPRSP : ", 13: "IRPERRST_1_5_2_CFG bit[13] PROTOCOL_QT_OVERFLOW_UNDERFLOW : ",
                                    14: "IRPERRST_1_5_2_CFG bit[14] PROTOCOL_PARITY_ERROR : ", 16: "IRPERRST_1_5_2_CFG bit[16] P2P_HDR_RF_ADDR_PAR_ERROR : ",
                                    17: "IRPERRST_1_5_2_CFG bit[17] FAF_RF_ADDR_PAR_ERROR : ", 18: "IRPERRST_1_5_2_CFG bit[18] ADDRCAM0_ADDR_PAR_ERROR : ",
                                    19: "IRPERRST_1_5_2_CFG bit[19] ADDRCAM1_ADDR_PAR_ERROR : ", 20: "IRPERRST_1_5_2_CFG bit[20] PF_TIMEOUT_ERR_CS0 : ",
                                    21: "IRPERRST_1_5_2_CFG bit[21] PF_TIMEOUT_ERR_CS1 : "
    }

    IRPFFERRST_1_5_2_CFG_BIT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10, 13: 13, 14: 14, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
    IRPFFERRST_1_5_2_CFG_REG_INFO = {1: "IRPFFERRST_1_5_2_CFG bit[1] WRCACHE_CORRECC_ERROR_CS0 : ", 2: "IRPFFERRST_1_5_2_CFG bit[2] WRCACHE_CORRECC_ERROR_CS1 : ",
                                        3: "IRPFFERRST_1_5_2_CFG bit[3] PROTOCOL_RCVD_POISON : ", 4: "IRPFFERRST_1_5_2_CFG bit[4] WRCACHE_UNCECC_ERROR_CS0 : ",
                                        5: "IRPFFERRST_1_5_2_CFG bit[5] WRCACHE_UNCECC_ERROR_CS1 : ", 6: "IRPFFERRST_1_5_2_CFG bit[6] CSR_ACC_32B_UNALIGNED : ",
                                        10: "IRPFFERRST_1_5_2_CFG bit[10] PROTOCOL_RCVD_UNEXPRSP : ", 13: "IRPFFERRST_1_5_2_CFG bit[13] PROTOCOL_QT_OVERFLOW_UNDERFLOW : ",
                                        14: "IRPFFERRST_1_5_2_CFG bit[14] PROTOCOL_PARITY_ERROR : ", 16: "IRPFFERRST_1_5_2_CFG bit[16] P2P_HDR_RF_ADDR_PAR_ERROR : ",
                                        17: "IRPFFERRST_1_5_2_CFG bit[17] FAF_RF_ADDR_PAR_ERROR : ", 18: "IRPFFERRST_1_5_2_CFG bit[18] ADDRCAM0_ADDR_PAR_ERROR : ",
                                        19: "IRPFFERRST_1_5_2_CFG bit[19] ADDRCAM1_ADDR_PAR_ERROR : ", 20: "IRPFFERRST_1_5_2_CFG bit[20] PF_TIMEOUT_ERR_CS0 : ",
                                        21: "IRPFFERRST_1_5_2_CFG bit[21] PF_TIMEOUT_ERR_CS1 : "
    }

    IRPFNERRST_1_5_2_CFG_BIT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10, 13: 13, 14: 14, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
    IRPFNERRST_1_5_2_CFG_REG_INFO = {1: "IRPFNERRST_1_5_2_CFG bit[1] WRCACHE_CORRECC_ERROR_CS0 : ", 2: "IRPFNERRST_1_5_2_CFG bit[2] WRCACHE_CORRECC_ERROR_CS1 : ",
                                        3: "IRPFNERRST_1_5_2_CFG bit[3] PROTOCOL_RCVD_POISON : ", 4: "IRPFNERRST_1_5_2_CFG bit[4] WRCACHE_UNCECC_ERROR_CS0 : ",
                                        5: "IRPFNERRST_1_5_2_CFG bit[5] WRCACHE_UNCECC_ERROR_CS1 : ", 6: "IRPFNERRST_1_5_2_CFG bit[6] CSR_ACC_32B_UNALIGNED : ",
                                        10: "IRPFNERRST_1_5_2_CFG bit[10] PROTOCOL_RCVD_UNEXPRSP : ", 13: "IRPFNERRST_1_5_2_CFG bit[13] PROTOCOL_QT_OVERFLOW_UNDERFLOW : ",
                                        14: "IRPFNERRST_1_5_2_CFG bit[14] PROTOCOL_PARITY_ERROR : ", 16: "IRPFNERRST_1_5_2_CFG bit[16] P2P_HDR_RF_ADDR_PAR_ERROR : ",
                                        17: "IRPFNERRST_1_5_2_CFG bit[17] FAF_RF_ADDR_PAR_ERROR : ", 18: "IRPFNERRST_1_5_2_CFG bit[18] ADDRCAM0_ADDR_PAR_ERROR : ",
                                        19: "IRPFNERRST_1_5_2_CFG bit[19] ADDRCAM1_ADDR_PAR_ERROR : ", 20: "IRPFNERRST_1_5_2_CFG bit[20] PF_TIMEOUT_ERR_CS0 : ",
                                        21: "IRPFNERRST_1_5_2_CFG bit[21] PF_TIMEOUT_ERR_CS1 : "
    }

    IRPFFERRHD0_1_5_2_CFG_BIT = {0: 31}
    IRPFFERRHD0_1_5_2_CFG_REG_INFO = {0: "IRPFFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    IRPFFERRHD1_1_5_2_CFG_BIT = {0: 31}
    IRPFFERRHD1_1_5_2_CFG_REG_INFO = {0: "IRPFFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    IRPFFERRHD2_1_5_2_CFG_BIT = {0: 31}
    IRPFFERRHD2_1_5_2_CFG_REG_INFO = {0: "IRPFFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    IRPFFERRHD3_1_5_2_CFG_BIT = {0: 31}
    IRPFFERRHD3_1_5_2_CFG_REG_INFO = {0: "IRPFFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    IRPNFERRST_1_5_2_CFG_BIT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10, 13: 13, 14: 14, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
    IRPNFERRST_1_5_2_CFG_REG_INFO = {1: "IRPNFERRST_1_5_2_CFG bit[1] WRCACHE_CORRECC_ERROR_CS0 : ", 2: "IRPNFERRST_1_5_2_CFG bit[2] WRCACHE_CORRECC_ERROR_CS1 : ",
                                        3: "IRPNFERRST_1_5_2_CFG bit[3] PROTOCOL_RCVD_POISON : ", 4: "IRPNFERRST_1_5_2_CFG bit[4] WRCACHE_UNCECC_ERROR_CS0 : ",
                                        5: "IRPNFERRST_1_5_2_CFG bit[5] WRCACHE_UNCECC_ERROR_CS1 : ", 6: "IRPNFERRST_1_5_2_CFG bit[6] CSR_ACC_32B_UNALIGNED : ",
                                        10: "IRPNFERRST_1_5_2_CFG bit[10] PROTOCOL_RCVD_UNEXPRSP : ", 13: "IRPNFERRST_1_5_2_CFG bit[13] PROTOCOL_QT_OVERFLOW_UNDERFLOW : ",
                                        14: "IRPNFERRST_1_5_2_CFG bit[14] PROTOCOL_PARITY_ERROR : ", 16: "IRPNFERRST_1_5_2_CFG bit[16] P2P_HDR_RF_ADDR_PAR_ERROR : ",
                                        17: "IRPNFERRST_1_5_2_CFG bit[17] FAF_RF_ADDR_PAR_ERROR : ", 18: "IRPNFERRST_1_5_2_CFG bit[18] ADDRCAM0_ADDR_PAR_ERROR : ",
                                        19: "IRPNFERRST_1_5_2_CFG bit[19] ADDRCAM1_ADDR_PAR_ERROR : ", 20: "IRPNFERRST_1_5_2_CFG bit[20] PF_TIMEOUT_ERR_CS0 : ",
                                        21: "IRPNFERRST_1_5_2_CFG bit[21] PF_TIMEOUT_ERR_CS1 : "
    }

    IRPNNERRST_1_5_2_CFG_BIT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10, 13: 13, 14: 14, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
    IRPNNERRST_1_5_2_CFG_REG_INFO = {1: "IRPNNERRST_1_5_2_CFG bit[1] WRCACHE_CORRECC_ERROR_CS0 : ", 2: "IRPNNERRST_1_5_2_CFG bit[2] WRCACHE_CORRECC_ERROR_CS1 : ",
                                        3: "IRPNNERRST_1_5_2_CFG bit[3] PROTOCOL_RCVD_POISON : ", 4: "IRPNNERRST_1_5_2_CFG bit[4] WRCACHE_UNCECC_ERROR_CS0 : ",
                                        5: "IRPNNERRST_1_5_2_CFG bit[5] WRCACHE_UNCECC_ERROR_CS1 : ", 6: "IRPNNERRST_1_5_2_CFG bit[6] CSR_ACC_32B_UNALIGNED : ",
                                        10: "IRPNNERRST_1_5_2_CFG bit[10] PROTOCOL_RCVD_UNEXPRSP : ", 13: "IRPNNERRST_1_5_2_CFG bit[13] PROTOCOL_QT_OVERFLOW_UNDERFLOW : ",
                                        14: "IRPNNERRST_1_5_2_CFG bit[14] PROTOCOL_PARITY_ERROR : ", 16: "IRPNNERRST_1_5_2_CFG bit[16] P2P_HDR_RF_ADDR_PAR_ERROR : ",
                                        17: "IRPNNERRST_1_5_2_CFG bit[17] FAF_RF_ADDR_PAR_ERROR : ", 18: "IRPNNERRST_1_5_2_CFG bit[18] ADDRCAM0_ADDR_PAR_ERROR : ",
                                        19: "IRPNNERRST_1_5_2_CFG bit[19] ADDRCAM1_ADDR_PAR_ERROR : ", 20: "IRPNNERRST_1_5_2_CFG bit[20] PF_TIMEOUT_ERR_CS0 : ",
                                        21: "IRPNNERRST_1_5_2_CFG bit[21] PF_TIMEOUT_ERR_CS1 : "
    }

    IRPNFERRHD0_1_5_2_CFG_BIT = {0: 31}
    IRPNFERRHD0_1_5_2_CFG_REG_INFO = {0: "IRPNFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    IRPNFERRHD1_1_5_2_CFG_BIT = {0: 31}
    IRPNFERRHD1_1_5_2_CFG_REG_INFO = {0: "IRPNFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    IRPNFERRHD2_1_5_2_CFG_BIT = {0: 31}
    IRPNFERRHD2_1_5_2_CFG_REG_INFO = {0: "IRPNFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    IRPNFERRHD3_1_5_2_CFG_BIT = {0: 31}
    IRPNFERRHD3_1_5_2_CFG_REG_INFO = {0: "IRPNFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    IRPERRCNT_1_5_2_CFG_BIT = {0: 6, 7: 7}
    IRPERRCNT_1_5_2_CFG_REG_INFO = {0: "IRPERRCNT_1_5_2_CFG bits[0:6] ERRCNT : ", 7: "IRPERRCNT_1_5_2_CFG bits[7] ERROVF : "}

    ITCERRST_1_5_2_CFG_BIT = {12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                                24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    ITCERRST_1_5_2_CFG_REG_INFO = {12: "ITCERRST_1_5_2_CFG bit[12] ITC_ENQ_DATA_OVERFLOW : ", 13: "ITCERRST_1_5_2_CFG bit[13] SW2IOSF_MPS_ERR : ",
                                    14: "ITCERRST_1_5_2_CFG bit[14] SW2IOSF_REQ_BUF_UF : ", 15: "ITCERRST_1_5_2_CFG bit[15] SW2IOSF_REQ_BUF_OV : ",
                                    16: "ITCERRST_1_5_2_CFG bit[16] ITC_IRP_CRED_UF : ", 17: "ITCERRST_1_5_2_CFG bit[17] ITC_IRP_CRED_OF : ",
                                    18: "ITCERRST_1_5_2_CFG bit[18] ITC_PAR_IOSF_DAT : ", 19: "ITCERRST_1_5_2_CFG bit[19] ITC_PAR_HDR_RF : ",
                                    20: "ITCERRST_1_5_2_CFG bit[20] ITC_VTMISC_HDR_RF : ", 21: "ITCERRST_1_5_2_CFG bit[21] ITC_PAR_ADDR_RF : ",
                                    22: "ITCERRST_1_5_2_CFG bit[22] ITC_ECC_COR_RF : ", 23: "ITCERRST_1_5_2_CFG bit[23] ITC_ECC_UNCOR_RF : ",
                                    24: "ITCERRST_1_5_2_CFG bit[24] ITC_CABORT : ", 25: "ITCERRST_1_5_2_CFG bit[25] ITC_MABORT : ",
                                    26: "ITCERRST_1_5_2_CFG bit[26] INB_UNSUCCESSFUL_CMPL : ", 27: "ITCERRST_1_5_2_CFG bit[27] ITC_ENQ_OVERFLOW : ",
                                    28: "ITCERRST_1_5_2_CFG bit[28] ITC_MISC_PRH_OVERFLOW : ", 29: "ITCERRST_1_5_2_CFG bit[29] ITC_HW_ASSERT : ",
                                    30: "ITCERRST_1_5_2_CFG bit[30] ITC_PAR_IOSF_CMD : ", 31: "ITCERRST_1_5_2_CFG bit[31] ITC_MSGD_ILLEGAL_SIZE : ",
    }

    TCERRCNT_1_5_2_CFG_BIT = {0: 6, 7: 7, 8: 14, 15: 15}
    TCERRCNT_1_5_2_CFG_REG_INFO = {0: "TCERRCNT_1_5_2_CFG bits[0:6] OTC_ERRCNT : ", 7: "TCERRCNT_1_5_2_CFG bits[7] OTC_ERROVF : ",
                                    8: "TCERRCNT_1_5_2_CFG bits[8:14] OTC_ERRCNT : ", 15: "TCERRCNT_1_5_2_CFG bit[15] ITC_ERROVF : "}

    ITCFFERRST_1_5_2_CFG_BIT = {0: 6}
    ITCFFERRST_1_5_2_CFG_REG_INFO = {0: "ITCFFERRST_1_5_2_CFG bits[0:6] TC_CORE_ERROR_STATUS_LOG : "}

    ITCFFERRHD0_1_5_2_CFG_BIT = {0: 31}
    ITCFFERRHD0_1_5_2_CFG_REG_INFO = {0: "ITCFFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    ITCFFERRHD1_1_5_2_CFG_BIT = {0: 31}
    ITCFFERRHD1_1_5_2_CFG_REG_INFO = {0: "ITCFFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    ITCFFERRHD2_1_5_2_CFG_BIT = {0: 31}
    ITCFFERRHD2_1_5_2_CFG_REG_INFO = {0: "ITCFFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    ITCFFERRHD3_1_5_2_CFG_BIT = {0: 31}
    ITCFFERRHD3_1_5_2_CFG_REG_INFO = {0: "ITCFFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    ITCFNERRST_1_5_2_CFG_BIT = {0: 6}
    ITCFNERRST_1_5_2_CFG_REG_INFO = {0: "ITCFNERRST_1_5_2_CFG bits[0:6] TC_CORE_ERROR_STATUS_LOG : "}

    ITCNFERRST_1_5_2_CFG_BIT = {0: 6}
    ITCNFERRST_1_5_2_CFG_REG_INFO = {0: "ITCNFERRST_1_5_2_CFG bits[0:6] TC_CORE_ERROR_STATUS_LOG : "}

    ITCNFERRHD0_1_5_2_CFG_BIT = {0: 31}
    ITCNFERRHD0_1_5_2_CFG_REG_INFO = {0: "ITCNFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    ITCNFERRHD1_1_5_2_CFG_BIT = {0: 31}
    ITCNFERRHD1_1_5_2_CFG_REG_INFO = {0: "ITCNFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    ITCNFERRHD2_1_5_2_CFG_BIT = {0: 31}
    ITCNFERRHD2_1_5_2_CFG_REG_INFO = {0: "ITCNFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    ITCNFERRHD3_1_5_2_CFG_BIT = {0: 31}
    ITCNFERRHD3_1_5_2_CFG_REG_INFO = {0: "ITCNFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    ITCNNERRST_1_5_2_CFG_BIT = {0: 6}
    ITCNNERRST_1_5_2_CFG_REG_INFO = {0: "ITCNNERRST_1_5_2_CFG bits[0:6] TC_CORE_ERROR_STATUS_LOG : "}

    OTCFFERRST_1_5_2_CFG_BIT = {0: 6}
    OTCFFERRST_1_5_2_CFG_REG_INFO = {0: "OTCFFERRST_1_5_2_CFG bits[0:6] OTC_ERROR_STATUS_LOG : "}

    OTCFFERRHD0_1_5_2_CFG_BIT = {0: 31}
    OTCFFERRHD0_1_5_2_CFG_REG_INFO = {0: "OTCFFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    OTCFFERRHD1_1_5_2_CFG_BIT = {0: 31}
    OTCFFERRHD1_1_5_2_CFG_REG_INFO = {0: "OTCFFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    OTCFFERRHD2_1_5_2_CFG_BIT = {0: 31}
    OTCFFERRHD2_1_5_2_CFG_REG_INFO = {0: "OTCFFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    OTCFFERRHD3_1_5_2_CFG_BIT = {0: 31}
    OTCFFERRHD3_1_5_2_CFG_REG_INFO = {0: "OTCFFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    OTCFNERRST_1_5_2_CFG_BIT = {0: 6}
    OTCFNERRST_1_5_2_CFG_REG_INFO = {0: "OTCFNERRST_1_5_2_CFG bits[0:6] OTC_ERROR_STATUS_LOG : "}

    OTCNFERRST_1_5_2_CFG_BIT = {0: 6}
    OTCNFERRST_1_5_2_CFG_REG_INFO = {0: "OTCNFERRST_1_5_2_CFG bits[0:6] OTC_ERROR_STATUS_LOG : "}

    OTCNFERRHD0_1_5_2_CFG_BIT = {0: 31}
    OTCNFERRHD0_1_5_2_CFG_REG_INFO = {0: "OTCNFERRHD0_1_5_2_CFG bits[0:31] HDR : "}

    OTCNFERRHD1_1_5_2_CFG_BIT = {0: 31}
    OTCNFERRHD1_1_5_2_CFG_REG_INFO = {0: "OTCNFERRHD1_1_5_2_CFG bits[0:31] HDR : "}

    OTCNFERRHD2_1_5_2_CFG_BIT = {0: 31}
    OTCNFERRHD2_1_5_2_CFG_REG_INFO = {0: "OTCNFERRHD2_1_5_2_CFG bits[0:31] HDR : "}

    OTCNFERRHD3_1_5_2_CFG_BIT = {0: 31}
    OTCNFERRHD3_1_5_2_CFG_REG_INFO = {0: "OTCNFERRHD3_1_5_2_CFG bits[0:31] HDR : "}

    OTCNNERRST_1_5_2_CFG_BIT = {0: 6}
    OTCNNERRST_1_5_2_CFG_REG_INFO = {0: "OTCNNERRST_1_5_2_CFG bits[0:6] OTC_ERROR_STATUS_LOG : "}

    TC_ERR_MISCLOG_1_5_2_CFG_BIT = {0: 10, 11: 31}
    TC_ERR_MISCLOG_1_5_2_CFG_REG_INFO = {0: "TC_ERR_MISCLOG_1_5_2_CFG bits[0:10] OTCFIFOERRIDX : ",
                                            11: "TC_ERR_MISCLOG_1_5_2_CFG bits[11:31] ITCFIFOERRIDX : " }

    IRPP0PLSR0_1_5_2_CFG_BIT = {0: 1, 2: 8, 9: 13, 14: 18, 28: 28, 29: 29, 30: 30, 31: 31}
    IRPP0PLSR0_1_5_2_CFG_REG_INFO = {0: "IRPP0PLSR0_1_5_2_CFG bits[0:1] POISON_LOG_TYPE : ", 2: "IRPP0PLSR0_1_5_2_CFG bits[2:8] POISON_LOG_RID : ",
                                        9: "IRPP0PLSR0_1_5_2_CFG bits[9:13] POISON_LOG_LEN : ", 14: "IRPP0PLSR0_1_5_2_CFG bits[14:18] POISON_LOG_TTYPE : ",
                                        28: "IRPP0PLSR0_1_5_2_CFG bit[28] DBG_MUX_EN : ", 29: "IRPP0PLSR0_1_5_2_CFG bit[29] (POISON_LOG_OVERFLOW : ",
                                        30: "IRPP0PLSR0_1_5_2_CFG bit[30]  POISON_LOG_VALID : ", 31: "IRPP0PLSR0_1_5_2_CFG bit[31] POISON_LOG_EN : "
    }

    IRPP0PLSR1_1_5_2_CFG_BIT = {0: 31}
    IRPP0PLSR1_1_5_2_CFG_REG_INFO = {0: "IRPP0PLSR1_1_5_2_CFG bits[0:31] POISON_LOG_ADDR_LO : "}

    IRPP0PLSR2_1_5_2_CFG_BIT = {0: 31}
    IRPP0PLSR2_1_5_2_CFG_REG_INFO = {0: " IRPP0PLSR2_1_5_2_CFG bits[0:31] POISON_LOG_ADDR_HI : "}

    OTCERRST_1_5_2_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
    OTCERRST_1_5_2_CFG_REG_INFO = {0: "OTCERRST_1_5_2_CFG bit[0] OTC_CRDT_UF : ", 1: "OTCERRST_1_5_2_CFG bit[1] OTC_CRDT_OF : ",
                                    2: "OTCERRST_1_5_2_CFG bit[2] OTC_PAR_HDR_RF : ", 3: "OTCERRST_1_5_2_CFG bit[3] OTC_PAR_ADDR_RF : ",
                                    4: "OTCERRST_1_5_2_CFG bit[4] OTC_ECC_UNCOR_RF : ", 5: "OTCERRST_1_5_2_CFG bit[5] OTC_CABORT : ",
                                    6: "OTCERRST_1_5_2_CFG bit[6] OTC_MABORT : ", 7: "OTCERRST_1_5_2_CFG bit[7] OTC_MTC_TGT_ERR : ",
                                    8: "OTCERRST_1_5_2_CFG bit[8] OTC_ECC_COR_RF : ", 9: "OTCERRST_1_5_2_CFG bit[9] OTC_MCTP_BCAST_TO_DMI : ",
                                    10: "OTCERRST_1_5_2_CFG bit[10] OTC_PAR_RTE : ", 11: "OTCERRST_1_5_2_CFG bit[11] OTC_IRP_DAT_PAR : ",
                                    12: "OTCERRST_1_5_2_CFG bit[12] OTC_IRP_ADDR_PAR : ", 13: "OTCERRST_1_5_2_CFG bit[13] OTC_HW_ASSERT : ",
                                    14: "OTCERRST_1_5_2_CFG bit[14] OTC_TXN_DUR_LOCK : ", 15: "OTCERRST_1_5_2_CFG bit[15] OTC_GPSB_PAR : ",
                                    16: "OTCERRST_1_5_2_CFG bit[16] OTC_SB_UF : ", 17: "OTCERRST_1_5_2_CFG bit[17] OTC_SB_OF : ",
                                    18: "OTCERRST_1_5_2_CFG bit[18] OTC_MISC_SNARF_FIFO_OF : ", 19: "OTCERRST_1_5_2_CFG bit[19] OTC_MISC_SNARF_FIFO_UF : ",
                                    20: "OTCERRST_1_5_2_CFG bit[20] OTC_MISC_OOBMSM_MULT_PEND : "
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dist_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = 0
                    if re.search("Addr2a0",key) :
                        if dist_reg_addr[reg] < 0x2a0 :
                            continue
                        beg_addr = dist_reg_addr[reg] - 0x2a0
                    elif re.search("Addr208",key) :
                        if dist_reg_addr[reg] < 0x208 : 
                            continue
                        beg_addr = dist_reg_addr[reg] - 0x208
                    elif re.search("Addrb0",key) :
                        if dist_reg_addr[reg] < 0xb0:
                            continue
                        beg_addr = dist_reg_addr[reg] - 0xb0
                    else:
                        continue
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dist_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse RAS failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Ras part : " + output + "\n"
    return output

def parse_peci_cbdma_D1734(value):
    list_key_name = {"B0D1F0Addr6", "B0D1F1Addr6", "B0D1F2Addr6", "B0D1F3Addr6", "B0D1F4Addr6", "B0D1F5Addr6", "B0D1F6Addr6", "B0D1F7Addr6",
                        "B0D1F0Addr4a", "B0D1F1Addr4a", "B0D1F2Addr4a", "B0D1F3Addr4a", "B0D1F4Addr4a", "B0D1F5Addr4a", "B0D1F6Addr4a", "B0D1F7Addr4a",
                        "B0D1F0Addr104", "B0D1F1Addr104", "B0D1F2Addr104", "B0D1F3Addr104", "B0D1F4Addr104", "B0D1F5Addr104," "B0D1F6Addr104", "B0D1F7Addr104"
    }
                        #16 bit
    dict_reg_addr = { "dict_reg_addr_1": {"CBDMA_PCISTS": 0x6, "CBDMA_DEVSTS": 0x4a, "CBDMA_CBPERRSTSLOG": 0x1b4},
                        #32 bit
                        "dict_reg_addr_2":{"CBDMA_ERRUNCSTS": 0x104, "CBDMA_ERRCORSTS": 0x110, "CBDMA_AERHDRLOG1": 0x11c, "CBDMA_AERHDRLOG2": 0x120,
                        "CBDMA_AERHDRLOG3": 0x124, "CBDMA_AERHDRLOG4": 0x128, "CBDMA_FERR_CHANERR": 0x180, "CBDMA_FERR_DMACOUNT": 0x184, "CBDMA_FERR_INTDMACOUNT": 0x186,
                        "CBDMA_NERR_CHANERR": 0x1a8},
                        #64 bit
                        "dict_reg_addr_3": {"CBDMA_FERR_CHANSTS": 0x188, "CBDMA_FERR_CADDR": 0x198, "CBDMA_FERR_NADDR": 0x1a0}
    }

    dict_reg_addr_offset_num = {"dict_reg_addr_1": 1, "dict_reg_addr_2": 3, "dict_reg_addr_3": 7}
    CBDMA_PCISTS_BIT = {3: 3, 4: 4, 5: 5, 7: 7, 8: 8, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    CBDMA_PCISTS_REG_INFO = {3: "PCISTS bit[3] INTS : ", 4: "PCISTS bit[4] CAPE : ", 5: "PCISTS bit[5] C66 : ",
                        7: "PCISTS bit[7] FBC : ", 8: "PCISTS bit[8] MDPE : ", 11: "PCISTS bit[11] STA : ",
                        12: "PCISTS bit[12] RTA : ", 13: "PCISTS bit[13] RMA : ", 14: "PCISTS bit[14] SSE : ",
                        15: "PCISTS bit[15] DPE : "
    }

    CBDMA_DEVSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    CBDMA_DEVSTS_REG_INFO = {0: "DEVSTS bit[0] CED : ", 1: "DEVSTS bit[1] NFED : ", 2: "DEVSTS bit[2] FED : ",
                        3: "DEVSTS bit[3] URD : ", 4: "DEVSTS bit[4] APD : ", 5: "DEVSTS bit[5] TP : "
    }

    CBDMA_ERRUNCSTS_BIT = {5: 5, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22}
    CBDMA_ERRUNCSTS_REG_INFO = {5: "ERRUNCSTS bit[5] SLDE : ", 12: "ERRUNCSTS bit[12] PTLPE : ", 13: "ERRUNCSTS bit[13] FCE : ",
                            14: "ERRUNCSTS bit[14] CTE : ", 15: "ERRUNCSTS bit[15] CAE : ", 16: "ERRUNCSTS bit[16] UCE : ",
                            17: "ERRUNCSTS bit[17] ROE : ", 18: "ERRUNCSTS bit[18] MTLPE : ", 19: "ERRUNCSTS bit[19] ECRCE : ",
                            20: "ERRUNCSTS bit[17] URE : ", 21: "ERRUNCSTS bit[21] ACSE : ", 22: "ERRUNCSTS bit[22] UIE : "
    }

    CBDMA_ERRCORSTS_BIT = {0: 0, 6: 6, 7: 7, 8: 8, 12: 12, 13: 13, 14: 14, 15: 15}
    CBDMA_ERRCORSTS_REG_INFO = {0: "ERRCORSTS bit[0] RE : ", 6: "ERRCORSTS bit[6] BTLPE : ", 7: "ERRCORSTS bit[7] BDLLPE : ",
                            8: "ERRCORSTS bit[8] RNRE : ", 12: "ERRCORSTS bit[12] RTTE : ", 13: "ERRCORSTS bit[13] ANFE : ",
                            14: "ERRCORSTS bit[14] CIE : ", 15: "ERRCORSTS bit[15] HLOE : "
    }

    CBDMA_AERHDRLOG1_BIT = {0: 31}
    CBDMA_AERHDRLOG1_REG_INFO = {0: "AERHDRLOG1 bits[0:31] TLPHDRLOG : "}

    CBDMA_AERHDRLOG2_BIT = {0: 31}
    CBDMA_AERHDRLOG2_REG_INFO = {0: "AERHDRLOG2 bits[0:31] TLPHDRLOG : "}

    CBDMA_AERHDRLOG3_BIT = {0: 31}
    CBDMA_AERHDRLOG3_REG_INFO = {0: "AERHDRLOG3 bits[0:31] TLPHDRLOG : "}

    CBDMA_AERHDRLOG4_BIT = {0: 31}
    CBDMA_AERHDRLOG4_REG_INFO = {0: "AERHDRLOG4 bits[0:31] TLPHDRLOG : "}

    CBDMA_FERR_CHANERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27}
    CBDMA_FERR_CHANERR_REG_INFO = {0: "FERR_CHANERR bit[0] XSADDERR_DMA0 : ", 1: "FERR_CHANERR bit[1] XDADDERR_DMA1 : ", 2: "FERR_CHANERR bit[2] NDARERR_DMA2 : ",
                                3: "FERR_CHANERR bit[3] DERR_DMA3 : ", 4: "FERR_CHANERR bit[4] CHADERR_DMA4 : ", 5: "FERR_CHANERR bit[5] CHANCMD_ERR_DMA5 : ",
                                6: "FERR_CHANERR bit[6] CUNCORERR_DMA6 : ", 7: "FERR_CHANERR bit[7] DUNCORERR_DMA7 : ", 8: "FERR_CHANERR bit[8] RDERR_DMA8 : ",
                                9: "FERR_CHANERR bit[9] WDERR_DMA9 : ", 10: "FERR_CHANERR bit[10] DCERR_DMA10 : ", 11: "FERR_CHANERR bit[11] DSXERR_DMA11 : ",
                                12: "FERR_CHANERR bit[12] CMPADDERR_DMA12 : ", 13: "FERR_CHANERR bit[13] INTCFGERR_DMA13 : ", 14: "FERR_CHANERR bit[14] SEDERR_DMA14 : ",
                                15: "FERR_CHANERR bit[15] UAERR_DMA15 : ", 16: "FERR_CHANERR bit[16] CXPERR_DMA16 : ", 17: "FERR_CHANERR bit[17] XQERR_DMA17 : ",
                                18: "FERR_CHANERR bit[18] DCNTERR_DMA18 : ", 19: "FERR_CHANERR bit[19] DIFFERR_DMA19 : ", 20: "FERR_CHANERR bit[20] GTVERR_DMA20 : ",
                                21: "FERR_CHANERR bit[21] ATVERR_DMA21 : ", 22: "FERR_CHANERR bit[22] RTVERR_DMA22 : ", 23: "FERR_CHANERR bit[23] BBERR_DMA23 : ",
                                24: "FERR_CHANERR bit[24] RDIFFERR_DMA24 : ", 25: "FERR_CHANERR bit[25] RGTVERR_DMA25 : ", 26: "FERR_CHANERR bit[26] RATVERR_DMA26 : ",
                                27: "FERR_CHANERR bit[27] RRTVERR_DMA27 : "
    }

    CBDMA_FERR_DMACOUNT_BIT = {0: 15}
    CBDMA_FERR_DMACOUNT_REG_INFO = {0: "FERR_DMACOUNT bits[0:15] NUMBEROFDESCRIPTORSTOPROCESS : "}

    CBDMA_FERR_INTDMACOUNT_BIT = {0: 15}
    CBDMA_FERR_INTDMACOUNT_REG_INFO = {0: "FERR_INTDMACOUNT bits[0:15] NUMBEROFDESCRIPTORSTOPROCESS : "}

    CBDMA_FERR_CHANSTS_BIT = {0: 2, 6: 63}
    CBDMA_FERR_CHANSTS_REG_INFO = {0: "FERR_CHANSTS bits[0:2] DMAXSTS : ", 6: "FERR_CHANSTS bits[6:63] CMPDA : "}

    CBDMA_FERR_CADDR_BIT = {0: 63}
    CBDMA_FERR_CADDR_REG_INFO = {0: "FERR_CADDR bits[0:63] CDADDR : "}

    CBDMA_FERR_NADDR_BIT = {0: 63}
    CBDMA_FERR_NADDR_REG_INFO = {0: "FERR_NADDR bits[0:63] NXT_ADDR : "}
    
    CBDMA_NERR_CHANERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27}
    CBDMA_NERR_CHANERR_REG_INFO = {0: " NERR_CHANERR bit[0] XSADDERR_DMA0 : ", 1: " NERR_CHANERR bit[1] XDADDERR_DMA1 : ", 2: " NERR_CHANERR bit[2] NDARERR_DMA2 : ",
                                3: " NERR_CHANERR bit[3] DERR_DMA3 : ", 4: " NERR_CHANERR bit[4] CHADERR_DMA4 : ", 5: " NERR_CHANERR bit[5] CHANCMD_ERR_DMA5 : ",
                                6: " NERR_CHANERR bit[6] CUNCORERR_DMA6 : ", 7: " NERR_CHANERR bit[7] DUNCORERR_DMA7 : ", 8: " NERR_CHANERR bit[8] RDERR_DMA8 : ",
                                9: " NERR_CHANERR bit[9] WDERR_DMA9 : ", 10: " NERR_CHANERR bit[10] DCERR_DMA10 : ", 11: " NERR_CHANERR bit[11] DSXERR_DMA11 : ",
                                12: " NERR_CHANERR bit[12] CMPADDERR_DMA12 : ", 13: " NERR_CHANERR bit[13] INTCFGERR_DMA13 : ", 14: " NERR_CHANERR bit[14] SEDERR_DMA14 : ",
                                15: " NERR_CHANERR bit[15] UAERR_DMA15 : ", 16: " NERR_CHANERR bit[16] CXPERR_DMA16 : ", 17: " NERR_CHANERR bit[17] XQERR_DMA17 : ",
                                18: " NERR_CHANERR bit[18] DCNTERR_DMA18 : ", 19: " NERR_CHANERR bit[19] DIFFERR_DMA19 : ", 20: " NERR_CHANERR bit[20] GTVERR_DMA20 : ",
                                21: " NERR_CHANERR bit[21] ATVERR_DMA21 : ", 22: " NERR_CHANERR bit[22] RTVERR_DMA22 : ", 23: " NERR_CHANERR bit[23] BBERR_DMA23 : ",
                                24: " NERR_CHANERR bit[24] RDIFFERR_DMA24 : ", 25: " NERR_CHANERR bit[25] RGTVERR_DMA25 : ", 26: " NERR_CHANERR bit[26] RATVERR_DMA26 : ",
                                27: " NERR_CHANERR bit[27] RRTVERR_DMA27 : "
    }

    CBDMA_CBPERRSTSLOG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    CBDMA_CBPERRSTSLOG_REG_INFO = {0: "CBPERRSTSLOG bit[0] CBPERRSTSLOG : ", 1: "CBPERRSTSLOG bit[1] PEDRIOSFSB : ", 2: "CBPERRSTSLOG bit[2] PERDIOSFCMD : ",
                                3: "CBPERRSTSLOG bit[3] PEDCBR : ", 4: "CBPERRSTSLOG bit[4] PEDWBR : ", 5: "CBPERRSTSLOG bit[5] PEDBR : ",
                                6: "CBPERRSTSLOG bit[6] PECSR : ", 7: "CBPERRSTSLOG bit[7] ERRINJSTS : "
    }
    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg_addr in dict_reg_addr:
                    for reg in dict_reg_addr[reg_addr]:
                        print_flag = 0
                        dict_bit = reg + "_BIT"
                        dict_reg_info = reg + "_REG_INFO"
                        beg_addr = 0
                        if re.search("Addr104",key) :
                            if dict_reg_addr[reg_addr][reg] < 0x104:
                                continue
                            beg_addr = dict_reg_addr[reg_addr][reg] - 0x104
                        elif re.search("Addr4a",key) :
                            if dict_reg_addr[reg_addr][reg] < 0x4a:
                                continue
                            beg_addr = dict_reg_addr[reg_addr][reg] - 0x4a
                        elif re.search("Addr6",key) :
                            if dict_reg_addr[reg_addr][reg] < 0x6:
                                continue
                            beg_addr = dict_reg_addr[reg_addr][reg] - 0x6
                        else:
                            continue
                        end_addr = beg_addr + dict_reg_addr_offset_num[reg_addr]
                        reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                        if dict_reg_addr_offset_num[reg_addr] == 1:
                            reg_value_tmp = reg_value[0:2]
                        elif dict_reg_addr_offset_num[reg_addr] == 3:
                            reg_value_tmp = reg_value[0:4]
                        else:
                            reg_value_tmp = reg_value[0:8]
                        ret_value = hex_to_bin_bit(reg_value_tmp, key)
                        output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg_addr][reg], joint_addr(reg_value_tmp))
                        for beg_bit in locals().get(dict_bit):
                            ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                            if ret_output not in output_tmp:
                                output_tmp = output_tmp + ret_output
                            if ret:
                                print_flag = 1
                        if print_flag :
                            output = output + output_tmp
    except Exception as e:
        output = output + "Parse CBDMA failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Cbdma part : " + output + "\n"
    return output

def parse_peci_msm_D1734(value):
    dict_key_name = {"B0D2F0Addr4" : "PCI_CFG_STATUS_COMMAND", "B0D2F0Addr1a8": "FABRIC_ERROR_STS"}

    PCI_CFG_STATUS_COMMAND_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
                                    19: 19, 20: 20, 21: 21, 23: 23, 24: 24, 25: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    PCI_CFG_STATUS_COMMAND_REG_INFO = {0: "PCI_CFG_STATUS_COMMAND bit[0] IO_SPACE_ENA : ", 1: "PCI_CFG_STATUS_COMMAND bit[1] MEMORY_SPACE_ENA : ",
                                        2: "PCI_CFG_STATUS_COMMAND bit[2] BUS_MASTER_ENA : ", 3: "PCI_CFG_STATUS_COMMAND bit[3] SPECIAL_CYCLE_ENA : ",
                                        4: "PCI_CFG_STATUS_COMMAND bit[4] MEM_WRT_INVAL : ", 5: "PCI_CFG_STATUS_COMMAND bit[5] VGA_PALETTE_SNOOP : ",
                                        6: "PCI_CFG_STATUS_COMMAND bit[6] PARITY_ERROR_RESP : ", 7: "PCI_CFG_STATUS_COMMAND bit[7] IDSEL_STEP : ",
                                        8: "PCI_CFG_STATUS_COMMAND bit[8] SERR_ENABLE : ", 9: "PCI_CFG_STATUS_COMMAND bit[9] FAST_B2B_TRANS_ENA : ",
                                        10: "PCI_CFG_STATUS_COMMAND bit[10] INTERRUPT_DISABLE : ", 19: "PCI_CFG_STATUS_COMMAND bit[19] INTERRUPT_STATUS : ",
                                        20: "PCI_CFG_STATUS_COMMAND bit[20] CAPABILITIES_LIST : ", 21: "PCI_CFG_STATUS_COMMAND bit[21] IS66MHZ_CAPABLE : ",
                                        23: "PCI_CFG_STATUS_COMMAND bit[23] FAST_B2B_TRANS_CAP : ", 24: "PCI_CFG_STATUS_COMMAND bit[24] MAS_DATA_PAR_ERR : ",
                                        25: "PCI_CFG_STATUS_COMMAND bits[25:26] DEVSEL_TIMING : ", 27: "PCI_CFG_STATUS_COMMAND bit[27] SIG_TARGET_ABORT : ",
                                        28: "PCI_CFG_STATUS_COMMAND bit[28] REC_TARGET_ABORT : ", 29: "PCI_CFG_STATUS_COMMAND bit[29] REC_MASTER_ABORT : ",
                                        30: "PCI_CFG_STATUS_COMMAND bit[30] SIG_SYSTEM_ERROR : ", 31: "PCI_CFG_STATUS_COMMAND bit[31] PARITY_ERROR : ",
    }

    FABRIC_ERROR_STS_BIT = {0: 0, 1: 1, 2: 2}
    FABRIC_ERROR_STS_REG_INFO = {0: "FABRIC_ERROR_STS bit[0] FABRIC_0_PARITY_ERR : ", 1: "FABRIC_ERROR_STS bit[1] FABRIC_1_PARITY_ERR : ",
                                    2: "FABRIC_ERROR_STS bit[2] INPKGC : "}

    output = ""
    try:
        for key in dict_key_name:
            print_flag = 0
            if key in value:
                dict_bit = dict_key_name[key] + "_BIT"
                dict_reg_info = dict_key_name[key] + "_REG_INFO"
                beg_addr = 0
                end_addr = 3
                reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                ret_value = hex_to_bin_bit(reg_value[0:4], key)
                output_tmp = "%s%s : %s : " % (key, dict_key_name[key], joint_addr(reg_value[0:4]))
                for beg_bit in locals().get(dict_bit):
                    ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                    if ret_output not in output_tmp:
                        output_tmp = output_tmp + ret_output
                    if ret:
                        print_flag = 1
                if print_flag :
                    output = output + output_tmp
    except Exception as e:
        output = output + "Parse MSM failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Msm part : " + output + "\n"
    return output

def parse_peci_pmon_msm_D1734(value):
    dict_key_name = {"B0D2F1Addr4": "PCI_CFG_STATUS_COMMAND_DISC"}
    PCI_CFG_STATUS_COMMAND_DISC_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
                                        19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    PCI_CFG_STATUS_COMMAND_DISC_REG_INFO = {0: "PCI_CFG_STATUS_COMMAND_DISC bit[0] IO_SPACE_ENA : ", 1: "PCI_CFG_STATUS_COMMAND_DISC bit[1] MEMORY_SPACE_ENA : ",
                                            2: "PCI_CFG_STATUS_COMMAND_DISC bit[2] BUS_MASTER_ENA : ", 3: "PCI_CFG_STATUS_COMMAND_DISC bit[3] SPECIAL_CYCLE_ENA: : ",
                                            4: "PCI_CFG_STATUS_COMMAND_DISC bit[4] VGA_PALETTE_SNOOP : ", 5: "PCI_CFG_STATUS_COMMAND_DISC bit[5] PARITY_ERROR_RESP: : ",
                                            6: "PCI_CFG_STATUS_COMMAND_DISC bit[6] PARITY_ERROR_RESP : ", 7: "PCI_CFG_STATUS_COMMAND_DISC bit[7] IDSEL_STEP: : ",
                                            8: "PCI_CFG_STATUS_COMMAND_DISC bit[8] SERR_ENABLE : ", 9: "PCI_CFG_STATUS_COMMAND_DISC bit[9] FAST_B2B_TRANS_ENA: : ",
                                            10: "PCI_CFG_STATUS_COMMAND_DISC bit[10] INTERRUPT_DISABLE : ", 19: "PCI_CFG_STATUS_COMMAND_DISC bit[19] INTERRUPT_STATUS : ",
                                            20: "PCI_CFG_STATUS_COMMAND_DISC bit[20] CAPABILITIES_LIST : ", 21: "PCI_CFG_STATUS_COMMAND_DISC bit[21] IS66MHZ_CAPABLE : ",
                                            23: "PCI_CFG_STATUS_COMMAND_DISC bit[23] FAST_B2B_TRANS_CAP : ", 24: "PCI_CFG_STATUS_COMMAND_DISC bit[24] MAS_DATA_PAR_ERR : ",
                                            25: "PCI_CFG_STATUS_COMMAND_DISC bits[25:26] DEVSEL_TIMING: ", 27: "PCI_CFG_STATUS_COMMAND_DISC bit[27] SIG_TARGET_ABORT : ",
                                            28: "PCI_CFG_STATUS_COMMAND_DISC bit[28] REC_TARGET_ABORT: ", 29: "PCI_CFG_STATUS_COMMAND_DISC bit[29] REC_MASTER_ABORT : ",
                                            30: "PCI_CFG_STATUS_COMMAND_DISC bit[30] SIG_SYSTEM_ERROR: ", 31: "PCI_CFG_STATUS_COMMAND_DISC bit[31] PARITY_ERROR : "
    }

    output = ""
    try:
        for key in dict_key_name:
            print_flag = 0
            if key in value:
                dict_bit = dict_key_name[key] + "_BIT"
                dict_reg_info = dict_key_name[key] + "_REG_INFO"
                beg_addr = 0
                end_addr = 3
                reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                ret_value = hex_to_bin_bit(reg_value[0:4], key)
                output_tmp = "%s%s : %s : " % (key, dict_key_name[key], joint_addr(reg_value[0:4]))
                for beg_bit in locals().get(dict_bit):
                    ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                    if ret_output not in output_tmp:
                        output_tmp = output_tmp + ret_output
                    if ret:
                        print_flag = 1
                if print_flag :
                    output = output + output_tmp
    except Exception as e:
        output = output + "Parse PMON MSM failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Pmon msm part : " + output + "\n"
    return output

def parse_peci_trace_hub_D1734(value):
    dict_key_name = {"B0D2F4Addr4": "HUB_CMD"}
    HUB_CMD_BIT = {0: 0, 1: 1, 2: 2, 6: 6, 8: 8, 10: 10, 19: 19, 20: 20, 24: 24, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    HUB_CMD_REG_INFO = {0: "CMD bit[0] IOSE: ", 1: "CMD bit[1] MEM: ", 2: "CMD bit[2] BME: ", 6: "CMD bit[6] PERE: ",
                    8: "CMD bit[8] SERREN: ", 10: "CMD bit[10] INTDIS: ", 19: "CMD bit[19] INSTAT: ", 20: "CMD bit[20] CLIST: ",
                    24: "CMD bit[24] MDPE: ", 27: "CMD bit[27] STA: ", 28: "CMD bit[28] RTA: ", 29: "CMD bit[29] RMA: ",
                    30: "CMD bit[30] SSE: ", 31: "CMD bit[31] DPE: "
    }

    output = ""
    try:
        for key in dict_key_name:
            print_flag = 0
            if key in value:
                dict_bit = dict_key_name[key] + "_BIT"
                dict_reg_info = dict_key_name[key] + "_REG_INFO"
                beg_addr = 0
                end_addr = 3
                reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                ret_value = hex_to_bin_bit(reg_value[0:4], key)
                output_tmp = "%s%s : %s : " % (key, dict_key_name[key], joint_addr(reg_value[0:4]))
                for beg_bit in locals().get(dict_bit):
                    ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                    if ret_output not in output_tmp:
                        output_tmp = output_tmp + ret_output
                    if ret:
                        print_flag = 1
                if print_flag :
                    output = output + output_tmp
    except Exception as e:
        output = output + "Parse Trace HUB failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Trace hub part : " + output + "\n"
    return output

def parse_peci_mem_D1734(value):
    list_key_name = { "B30D12F0Addr22c18", "B30D13F0Addr22c18"}
    dict_reg_addr = { "CORRERRCNT_0": 0x22c18, "CORRERRCNT_1": 0x22c1c, "CORRERRCNT_2": 0x22c20, "CORRERRCNT_3": 0x22c24,
                        "RETRY_RD_ERR_LOG_ADDRESS2": 0x22c28, "CORRERRORSTATUS": 0x22c50, "RETRY_RD_ERR_LOG_MISC": 0x22c54,
                        "RETRY_RD_ERR_LOG_ADDRESS1": 0x22c58, "RETRY_RD_ERR_LOG_PARITY": 0x22c5c, "RETRY_RD_ERR_LOG": 0x22c60
    }
    CORRERRCNT_0_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    CORRERRCNT_0_REG_INFO = {0: "CORRERRCNT_0 bits[0:14] COR_ERR_CNT_0 : ", 15: "CORRERRCNT_0 bit[15] OVERFLOW_0 : ",
                                16: "CORRERRCNT_0 bits[16:30] COR_ERR_CNT_1 : ", 31: "CORRERRCNT_0 bit[31] OVERFLOW_1 : "
    }

    CORRERRCNT_1_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    CORRERRCNT_1_REG_INFO = {0: "CORRERRCNT_1 bits[0:14] COR_ERR_CNT_2 : ", 15: "CORRERRCNT_1 bit[15] OVERFLOW_2 : ",
                                16: "CORRERRCNT_1 bits[16:30] COR_ERR_CNT_3 : ", 31: "CORRERRCNT_1 bit[31] OVERFLOW_3 : "
    }

    CORRERRCNT_2_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    CORRERRCNT_2_REG_INFO = {0: "CORRERRCNT_2 bits[0:14] COR_ERR_CNT_4 : ", 15: "CORRERRCNT_2 bit[15] OVERFLOW_4 : ",
                                16: "CORRERRCNT_2 bits[16:30] COR_ERR_CNT_5 : ", 31: "CORRERRCNT_2 bit[31] OVERFLOW_5 : "
    }

    CORRERRCNT_3_BIT = {0: 14, 15: 15, 16: 30, 31: 31}
    CORRERRCNT_3_REG_INFO = {0: "CORRERRCNT_3 bits[0:14] COR_ERR_CNT_6 : ", 15: "CORRERRCNT_3 bit[15] OVERFLOW_6 : ",
                                16: "CORRERRCNT_3 bits[16:30] COR_ERR_CNT_7 : ", 31: "CORRERRCNT_3 bit[31] OVERFLOW_7 : "
    }

    RETRY_RD_ERR_LOG_ADDRESS2_BIT = {0: 20, 21: 22, 23: 27, 28: 29}
    RETRY_RD_ERR_LOG_ADDRESS2_REG_INFO = {0: "RETRY_RD_ERR_LOG_ADDRESS2 bits[0:20] ROW : ", 21: "RETRY_RD_ERR_LOG_ADDRESS2 bits[21:22] ECC_BIST_ERRTYPE : ",
                                            23: "RETRY_RD_ERR_LOG_ADDRESS2 bits[23:27] ECC_BIST_CORR_ERR_DEVNUM : ", 28: "RETRY_RD_ERR_LOG_ADDRESS2 bits[28:29] CORR_FSM_ERRTYPE : ",
    }

    CORRERRORSTATUS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    CORRERRORSTATUS_REG_INFO = {0: "CORRERRORSTATUS bit[0] ERR_OVERFLOW_STAT Rank 0 : ", 1: "CORRERRORSTATUS bit[1] ERR_OVERFLOW_STAT Rank 1 : ",
                                2: "CORRERRORSTATUS bit[2] ERR_OVERFLOW_STAT Rank 2 : ", 3: "CORRERRORSTATUS bit[3] ERR_OVERFLOW_STAT Rank 3 : ",
                                4: "CORRERRORSTATUS bit[4] ERR_OVERFLOW_STAT Rank 4 : ", 5: "CORRERRORSTATUS bit[5] ERR_OVERFLOW_STAT Rank 5 : ",
                                6: "CORRERRORSTATUS bit[6] ERR_OVERFLOW_STAT Rank 6 : ", 7: "CORRERRORSTATUS bit[7] ERR_OVERFLOW_STAT Rank 7 : ",
    }

    RETRY_RD_ERR_LOG_MISC_BIT = {0: 11, 12: 23, 24: 29, 30: 31}
    RETRY_RD_ERR_LOG_MISC_REG_INFO = {0: "RETRY_RD_ERR_LOG_MISC bits[0:11] PLUS1_LOC_SYN : " , 12: "RETRY_RD_ERR_LOG_MISC bits[12:23] INTER_LOC_SYN : ",
                                        24: "RETRY_RD_ERR_LOG_MISC bits[24:29] DATA_FAILED_COL_NUM : " , 30: "META_FAILED_COL_NUM bits[30:31] META_FAILED_COL_NUM : "
    }

    RETRY_RD_ERR_LOG_ADDRESS1_BIT = {0: 5, 6: 8, 9: 12, 13: 18, 19: 28}
    RETRY_RD_ERR_LOG_ADDRESS1_REG_INFO = {0: "RETRY_RD_ERR_LOG_ADDRESS1 bits[0:5] FAILED_DEV : ", 6: "RETRY_RD_ERR_LOG_ADDRESS1 bits[6:8] CHIP_SELECT : ",
                                            9: "RETRY_RD_ERR_LOG_ADDRESS1 bits[9:12] CBIT : ", 13: "RETRY_RD_ERR_LOG_ADDRESS1 bits[13:18] BANK : ",
                                            19: "RETRY_RD_ERR_LOG_ADDRESS1 bits[19:28] COL : "
    }

    RETRY_RD_ERR_LOG_PARITY_BIT = {0: 31}
    RETRY_RD_ERR_LOG_PARITY_REG_INFO = {0: "RETRY_RD_ERR_LOG_PARITY bits[0:31] PAR_SYN : "}

    RETRY_RD_ERR_LOG_BIT = {0: 0, 1: 1, 2: 2, 3: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17,
                            18: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26, 27: 27}
    RETRY_RD_ERR_LOG_REG_INFO = {0: "RETRY_RD_ERR_LOG bit[0] V : ", 1: "RETRY_RD_ERR_LOG bit[1] UC : ", 2: "RETRY_RD_ERR_LOG bit[2] OVER : ",
                                    3: "RETRY_RD_ERR_LOG bits[3:6] MODE : ", 7: "RETRY_RD_ERR_LOG bit[7] CORR_ERR : ", 8: "RETRY_RD_ERR_LOG bit[8] CORR_NOERR : ",
                                    9: "RETRY_RD_ERR_LOG bit[9] CORR_CORRECTABLE : ", 10: "RETRY_RD_ERR_LOG bit[10] CORR_CORRECTABLE_PAR_DEV : ", 11: "RETRY_RD_ERR_LOG bit[11] ECC_ERR : ",
                                    12: "RETRY_RD_ERR_LOG bit[12] PATSPR : ", 13: "RETRY_RD_ERR_LOG bit[13] EN_PATSPR : ", 14: "RETRY_RD_ERR_LOG bit[14] NOOVER : ",
                                    15: "RETRY_RD_ERR_LOG bit[15] EN : ", 16: "RETRY_RD_ERR_LOG bit[16] COL_CORRECTION : ", 17: "RETRY_RD_ERR_LOG bit[17] SINGLE_BIT_ERROR : ",
                                    18: "RETRY_RD_ERR_LOG bits[18:20] TRANSFER_NUMBER : ", 21: "RETRY_RD_ERR_LOG bit[21] PERSISTENT_ERROR : ", 22: "RETRY_RD_ERR_LOG bit[22] SYSTEM_ADDR_VALID : ",
                                    23: "RETRY_RD_ERR_LOG bit[23] MIRROR : ", 24: "RETRY_RD_ERR_LOG bit[24] MIRROR_PRI : ", 25: "RETRY_RD_ERR_LOG bit[25] MIRROR_FAILOVER : ",
                                    26: "RETRY_RD_ERR_LOG bit[26] ECC_BIST_VALID : ", 27: "RETRY_RD_ERR_LOG bit[27] DDRT_MODEB_UC : "
    }
    output = ""
    try:
        for key in list_key_name:
            if key in value:
                output_tmp = "%s : " % key
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x22c18
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse mem failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Mem part : " + output + "\n"
    return output

def parse_peci_pch_ieh_D1734(value, ieh_reg_dict):
    dict_reg_addr = {"LERRUNCSTS": 0x280, "LFERRUNCSTS": 0x284, "LNERRUNCSTS": 0x288, "LERRCORSTS": 0x294,
                        "LFERRCORSTS": 0x298, "LNERRCORSTS": 0x29c, "LCORERRCNTSEL": 0x2a4, "LCORERRCNT": 0x2a8,
                        "LFERRHDRLOG1": 0x2ac, "LFERRHDRLOG2": 0x2b0, "LFERRHDRLOG3": 0x2b4, "LFERRHDRLOG4": 0x2b8}

    LERRUNCSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    LERRUNCSTS_REG_INFO = {0: "LERRUNCSTS bit[0] IEH_CFGREGP : ", 1: "LERRUNCSTS bit[1] IEH_MTLP : ", 2: "LERRUNCSTS bit[2] IEH_UR : ",
                            3: "LERRUNCSTS bit[3] P2SB_CMDP : ", 4: "LERRUNCSTS bit[4] P2SB_DATAP : ", 5: "LERRUNCSTS bit[5] P2SB_NDT : ",
                            6: "LERRUNCSTS bit[6] RLINK_ERROR : ", 7: "LERRUNCSTS bit[7] MCSMB_ERROR : ", 8: "LERRUNCSTS bit[8] PSF0_CMDP : ",
                            9: "LERRUNCSTS bit[9] PSF0_UC : ", 10: "LERRUNCSTS bit[10] PSF0_UR : ", 11: "LERRUNCSTS bit[11] PSF1_CMDP : ",
                            12: "LERRUNCSTS bit[12] PSF1_UC : ", 13: "LERRUNCSTS bit[13] PSF1_UR : ", 14: "LERRUNCSTS bit[14] PSF2_CMDP : ",
                            15: "LERRUNCSTS bit[15] PSF2_UC : ", 16: "LERRUNCSTS bit[16] PSF2_UR : ", 17: "LERRUNCSTS bit[17] PSFPCC_CMDP : ",
                            18: "LERRUNCSTS bit[18] PSFPCC_UC : ", 19: "LERRUNCSTS bit[19] PSFPCC_UR : ", 20: "LERRUNCSTS bit[20] PSFS_CMDP : ",
                            21: "LERRUNCSTS bit[21] PSFS_UC : ", 22: "LERRUNCSTS bit[22] PSFS_UR : ", 23: "LERRUNCSTS bit[23] PSFSATA_CMDP : ",
                            24: "LERRUNCSTS bit[24] PSFSATA_UC : ", 25: "LERRUNCSTS bit[25] PSFSATA_UR : ", 26: "LERRUNCSTS bit[26] PSFME_CMDP : ",
                            27: "LERRUNCSTS bit[27] PSFME_UC : ", 28: "LERRUNCSTS bit[28] PSFME_UR : ", 29: "LERRUNCSTS bit[29] PSFIE_CMDP : ",
                            30: "LERRUNCSTS bit[30] PSFIE_UC : ", 31: "LERRUNCSTS bit[31] PSFIE_UR : "
    }

    LFERRUNCSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    LFERRUNCSTS_REG_INFO = {0: "LFERRUNCSTS bit[0] IEH_CFGREGP_FERR : ", 1: "LFERRUNCSTS bit[1] IEH_MTLP_FERR : ", 2: "LFERRUNCSTS bit[2] IEH_UR_FERR : ",
                            3: "LFERRUNCSTS bit[3] P2SB_CMDP_FERR_FERR : ", 4: "LFERRUNCSTS bit[4] P2SB_DATAP_FERR : ", 5: "LFERRUNCSTS bit[5] P2SB_NDT_FERR : ",
                            6: "LFERRUNCSTS bit[6] RLINK_ERROR_FERR : ", 7: "LFERRUNCSTS bit[7] MCSMB_ERROR_FERR : ", 8: "LFERRUNCSTS bit[8] PSF0_CMDP_FERR : ",
                            9: "LFERRUNCSTS bit[9] PSF0_UC_FERR : ", 10: "LFERRUNCSTS bit[10] PSF0_UR_FERR : ", 11: "LFERRUNCSTS bit[11] PSF1_CMDP_FERR : ",
                            12: "LFERRUNCSTS bit[12] PSF1_UC_FERR : ", 13: "LFERRUNCSTS bit[13] PSF1_UR_FERR : ", 14: "LFERRUNCSTS bit[14] PSF2_CMDP_FERR : ",
                            15: "LFERRUNCSTS bit[15] PSF2_UC_FERR : ", 16: "LFERRUNCSTS bit[16] PSF2_UR_FERR : ", 17: "LFERRUNCSTS bit[17] PSFPCC_CMDP_FERR : ",
                            18: "LFERRUNCSTS bit[18] PSFPCC_UC_FERR : ", 19: "LFERRUNCSTS bit[19] PSFPCC_UR_FERR : ", 20: "LFERRUNCSTS bit[20] PSFS_CMDP_FERR : ",
                            21: "LFERRUNCSTS bit[21] PSFS_UC_FERR : ", 22: "LFERRUNCSTS bit[22] PSFS_UR_FERR : ", 23: "LFERRUNCSTS bit[23] PSFSATA_CMDP_FERR : ",
                            24: "LFERRUNCSTS bit[24] PSFSATA_UC_FERR : ", 25: "LFERRUNCSTS bit[25] PSFSATA_UR_FERR : ", 26: "LFERRUNCSTS bit[26] PSFME_CMDP_FERR : ",
                            27: "LFERRUNCSTS bit[27] PSFME_UC_FERR : ", 28: "LFERRUNCSTS bit[28] PSFME_UR_FERR : ", 29: "LFERRUNCSTS bit[29] PSFIE_CMDP_FERR : ",
                            30: "LFERRUNCSTS bit[30] PSFIE_UC_FERR : ", 31: "LFERRUNCSTS bit[31] PSFIE_UR_FERR : "
    }

    LNERRUNCSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23,
                            24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    LNERRUNCSTS_REG_INFO = {0: "LNERRUNCSTS bit[0] IEH_CFGREGP_NERR : ", 1: "LNERRUNCSTS bit[1] IEH_MTLP_NERR : ", 2: "LNERRUNCSTS bit[2] IEH_UR_NERR : ",
                            3: "LNERRUNCSTS bit[3] P2SB_CMDP_NERR_NERR : ", 4: "LNERRUNCSTS bit[4] P2SB_DATAP_NERR : ", 5: "LNERRUNCSTS bit[5] P2SB_NDT_NERR : ",
                            6: "LNERRUNCSTS bit[6] RLINK_ERROR_NERR : ", 7: "LNERRUNCSTS bit[7] MCSMB_ERROR_NERR : ", 8: "LNERRUNCSTS bit[8] PSF0_CMDP_NERR : ",
                            9: "LNERRUNCSTS bit[9] PSF0_UC_NERR : ", 10: "LNERRUNCSTS bit[10] PSF0_UR_NERR : ", 11: "LNERRUNCSTS bit[11] PSF1_CMDP_NERR : ",
                            12: "LNERRUNCSTS bit[12] PSF1_UC_NERR : ", 13: "LNERRUNCSTS bit[13] PSF1_UR_NERR : ", 14: "LNERRUNCSTS bit[14] PSF2_CMDP_NERR : ",
                            15: "LNERRUNCSTS bit[15] PSF2_UC_NERR : ", 16: "LNERRUNCSTS bit[16] PSF2_UR_NERR : ", 17: "LNERRUNCSTS bit[17] PSFPCC_CMDP_NERR : ",
                            18: "LNERRUNCSTS bit[18] PSFPCC_UC_NERR : ", 19: "LNERRUNCSTS bit[19] PSFPCC_UR_NERR : ", 20: "LNERRUNCSTS bit[20] PSFS_CMDP_NERR : ",
                            21: "LNERRUNCSTS bit[21] PSFS_UC_NERR : ", 22: "LNERRUNCSTS bit[22] PSFS_UR_NERR : ", 23: "LNERRUNCSTS bit[23] PSFSATA_CMDP_NERR : ",
                            24: "LNERRUNCSTS bit[24] PSFSATA_UC_NERR : ", 25: "LNERRUNCSTS bit[25] PSFSATA_UR_NERR : ", 26: "LNERRUNCSTS bit[26] PSFME_CMDP_NERR : ",
                            27: "LNERRUNCSTS bit[27] PSFME_UC_NERR : ", 28: "LNERRUNCSTS bit[28] PSFME_UR_NERR : ", 29: "LNERRUNCSTS bit[29] PSFIE_CMDP_NERR : ",
                            30: "LNERRUNCSTS bit[30] PSFIE_UC_NERR : ", 31: "LNERRUNCSTS bit[31] PSFIE_UR_NERR : "
    }

    LERRCORSTS_BIT = {6: 6, 9: 9, 10: 10, 12: 12, 13: 13, 15: 15, 16: 16, 18: 18, 19: 19, 21: 21, 22: 22,
                        24: 24, 25: 25, 27: 27, 28: 28, 30: 30, 31: 31}
    LERRCORSTS_REG_INFO = {6: "LERRCORSTS bit[6] RLINK_ERR : ", 9: "LERRCORSTS bit[9] PSF0_ANFUC : ", 10: "LERRCORSTS bit[10] PSF0_ANFUR : ",
                            12: "LERRCORSTS bit[12] PSF1_ANFUC : ", 13: "LERRCORSTS bit[13] PSF1_ANFUR : ", 15: "LERRCORSTS bit[15] PSF2_ANFUC : ",
                            16: "LERRCORSTS bit[16] PSF2_ANFUR : ", 18: "LERRCORSTS bit[18] PSFPCC_ANFUC : ", 19: "LERRCORSTS bit[19] PSFPCC_ANFUR : ",
                            21: "LERRCORSTS bit[21] PSFS_ANFUC : ", 22: "LERRCORSTS bit[22] PSFS_ANFUR : ", 24: "LERRCORSTS bit[24] PSFSATA_ANFUC : ",
                            25: "LERRCORSTS bit[25] PSFSATA_ANFUR : ", 27: "LERRCORSTS bit[27] PSFME_ANFUC : ", 28: "LERRCORSTS bit[28] PSFME_ANFUR : ",
                            30: "LERRCORSTS bit[30] PSFIE_ANFUC : ", 31: "LERRCORSTS bit[31] PSFIE_ANFUR : "
    }

    LFERRCORSTS_BIT =  {6: 6, 9: 9, 10: 10, 12: 12, 13: 13, 15: 15, 16: 16, 18: 18, 19: 19, 21: 21, 22: 22,
                        24: 24, 25: 25, 27: 27, 28: 28, 30: 30, 31: 31}
    LFERRCORSTS_REG_INFO = {6: "LFERRCORSTS bit[6] RLINK_FERR : ", 9: "LFERRCORSTS bit[9] PSF0_ANFUC : ", 10: "LFERRCORSTS bit[10] PSF0_ANFUR : ",
                        12: "LFERRCORSTS bit[12] PSF1_ANFUC : ", 13: "LFERRCORSTS bit[13] PSF1_ANFUR : ", 15: "LFERRCORSTS bit[15] PSF2_ANFUC : ",
                        16: "LFERRCORSTS bit[16] PSF2_ANFUR : ", 18: "LFERRCORSTS bit[18] PSFPCC_ANFUC : ", 19: "LFERRCORSTS bit[19] PSFPCC_ANFUR : ",
                        21: "LFERRCORSTS bit[21] PSFS_ANFUC : ", 22: "LFERRCORSTS bit[22] PSFS_ANFUR : ", 24: "LFERRCORSTS bit[24] PSFSATA_ANFUC : ",
                        25: "LFERRCORSTS bit[25] PSFSATA_ANFUR : ", 27: "LFERRCORSTS bit[27] PSFME_ANFUC : ", 28: "LFERRCORSTS bit[28] PSFME_ANFUR : ",
                        30: "LFERRCORSTS bit[30] PSFIE_ANFUC : ", 31: "LFERRCORSTS bit[31] PSFIE_ANFUR : "
    }

    LNERRCORSTS_BIT = {6: 6, 9: 9, 10: 10, 12: 12, 13: 13, 15: 15, 16: 16, 18: 18, 19: 19, 21: 21, 22: 22,
                        24: 24, 25: 25, 27: 27, 28: 28, 30: 30, 31: 31}
    LNERRCORSTS_REG_INFO = {6: "LNERRCORSTS bit[6] RLINK_NERR : ", 9: "LNERRCORSTS bit[9] PSF0_ANFUC : ", 10: "LNERRCORSTS bit[10] PSF0_ANFUR : ",
                        12: "LNERRCORSTS bit[12] PSF1_ANFUC : ", 13: "LNERRCORSTS bit[13] PSF1_ANFUR : ", 15: "LNERRCORSTS bit[15] PSF2_ANFUC : ",
                        16: "LNERRCORSTS bit[16] PSF2_ANFUR : ", 18: "LNERRCORSTS bit[18] PSFPCC_ANFUC : ", 19: "LNERRCORSTS bit[19] PSFPCC_ANFUR : ",
                        21: "LNERRCORSTS bit[21] PSFS_ANFUC : ", 22: "LNERRCORSTS bit[22] PSFS_ANFUR : ", 24: "LNERRCORSTS bit[24] PSFSATA_ANFUC : ",
                        25: "LNERRCORSTS bit[25] PSFSATA_ANFUR : ", 27: "LNERRCORSTS bit[27] PSFME_ANFUC : ", 28: "LNERRCORSTS bit[28] PSFME_ANFUR : ",
                        30: "LNERRCORSTS bit[30] PSFIE_ANFUC : ", 31: "LNERRCORSTS bit[31] PSFIE_ANFUR : "
    }

    LCORERRCNTSEL_BIT = {6: 6, 9: 9, 10: 10, 12: 12, 13: 13, 15: 15, 16: 16, 18: 18, 19: 19, 21: 21, 22: 22,
                        24: 24, 25: 25, 27: 27, 28: 28, 30: 30, 31: 31}
    LCORERRCNTSEL_REG_INFO = {6: "LCORERRCNTSEL bit[6] RLINK_COR_ERRCNTSEL : ", 9: "LCORERRCNTSEL bit[9] PSF0_ANFUC_ERRCNTSEL : ", 10: "LCORERRCNTSEL bit[10] PSF0_ANFUR_ERRCNTSEL : ",
                        12: "LCORERRCNTSEL bit[12] PSF1_ANFUC_ERRCNTSEL : ", 13: "LCORERRCNTSEL bit[13] PSF1_ANFUR_ERRCNTSEL : ", 15: "LCORERRCNTSEL bit[15] PSF2_ANFUC_ERRCNTSEL : ",
                        16: "LCORERRCNTSEL bit[16] PSF2_ANFUR_ERRCNTSEL : ", 18: "LCORERRCNTSEL bit[18] PSFPCC_ANFUC_ERRCNTSEL : ", 19: "LCORERRCNTSEL bit[19] PSFPCC_ANFUR_ERRCNTSEL : ",
                        21: "LCORERRCNTSEL bit[21] PSFS_ANFUC_ERRCNTSEL : ", 22: "LCORERRCNTSEL bit[22] PSFS_ANFUR_ERRCNTSEL : ", 24: "LCORERRCNTSEL bit[24] PSFSATA_ANFUC_ERRCNTSEL : ",
                        25: "LCORERRCNTSEL bit[25] PSFSATA_ANFUR_ERRCNTSEL : ", 27: "LCORERRCNTSEL bit[27] PSFME_ANFUC_ERRCNTSEL : ", 28: "LCORERRCNTSEL bit[28] PSFME_ANFUR_ERRCNTSEL : ",
                        30: "LCORERRCNTSEL bit[30] PSFIE_ANFUC_ERRCNTSEL : ", 31: "LCORERRCNTSEL bit[31] PSFIE_ANFUR_ERRCNTSEL : "
    }

    LCORERRCNT_BIT = {0: 6, 7: 7}
    LCORERRCNT_REG_INFO = {0: "LCORERRCNT bits[0:6] ERRCNT : ", 7: "LCORERRCNT bits[7] ERR_OVF : "}

    LFERRHDRLOG1_BIT = {0: 31}
    LFERRHDRLOG1_REG_INFO = {0: "LFERRHDRLOG1 bits[0:31] TLPHDRLOG : " }

    LFERRHDRLOG2_BIT = {0: 31}
    LFERRHDRLOG2_REG_INFO = {0: "LFERRHDRLOG2 bits[0:31] TLPHDRLOG : " }

    LFERRHDRLOG3_BIT = {0: 31}
    LFERRHDRLOG3_REG_INFO = {0: "LFERRHDRLOG3 bits[0:31] TLPHDRLOG : " }

    LFERRHDRLOG4_BIT = {0: 31}
    LFERRHDRLOG4_REG_INFO = {0: "LFERRHDRLOG4 bits[0:31] TLPHDRLOG : " }

    output = ""
    try:
        for key in ieh_reg_dict:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x280
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
        if len(output) > 0:
            output = "IEH part : " + output + "\n"
    except Exception as e:
        output = output + "Parse pch ieh failed: %s" % str(e)
        print(output)
    return output

def parse_peci_root_port_D1734(value, rp_num):
    dict_key_name = {"RP0": {"B0D9F0Addr4a", "B0D9F0Addr104", "B0D9F0Addr19c", "B0D9F0Addr208", 
                                "B0D9F0Addr99e", "B0D9F0Addracc", "B0D9F0Addrb58", "B0D9F0Addrb70", "B0D9F0Addrbec"},
                    "RP1": {"B0D10F0Addr4a", "B0D10F0Addr104", "B0D10F0Addr19c", "B0D10F0Addr208", 
                                "B0D10F0Addr99e", "B0D10F0Addracc", "B0D10F0Addrb58", "B0D10F0Addrb70", "B0D10F0Addrbec"},
                    "RP2": {"B0D11F0Addr4a", "B0D11F0Addr104", "B0D11F0Addr19c", "B0D11F0Addr208", 
                                "B0D11F0Addr99e", "B0D11F0Addracc", "B0D11F0Addrb58", "B0D11F0Addrb70", "B0D11F0Addrbec"},
                    "RP3": {"B0D12F0Addr4a", "B0D12F0Addr104", "B0D12F0Addr19c", "B0D12F0Addr208", 
                                "B0D12F0Addr99e", "B0D12F0Addracc", "B0D12F0Addrb58", "B0D12F0Addrb70", "B0D12F0Addrbec"},
                    "RP4": {"B0D16F0Addr4a", "B0D16F0Addr104", "B0D16F0Addr19c", "B0D16F0Addr208", 
                                "B0D16F0Addr99e", "B0D16F0Addracc", "B0D16F0Addrb58", "B0D16F0Addrb70", "B0D16F0Addrbec"},
                    "RP5": {"B0D17F0Addr4a", "B0D17F0Addr104", "B0D17F0Addr19c", "B0D17F0Addr208", 
                                "B0D17F0Addr99e", "B0D17F0Addracc", "B0D17F0Addrb58", "B0D17F0Addrb70", "B0D17F0Addrbec"},
                    "RP6": {"B0D18F0Addr4a", "B0D18F0Addr104", "B0D18F0Addr19c", "B0D18F0Addr208", 
                                "B0D18F0Addr99e", "B0D18F0Addracc", "B0D18F0Addrb58", "B0D18F0Addrb70", "B0D18F0Addrbec"},
                    "RP7": {"B0D19F0Addr4a", "B0D19F0Addr104", "B0D19F0Addr19c", "B0D19F0Addr208", 
                                "B0D19F0Addr99e", "B0D19F0Addracc", "B0D19F0Addrb58", "B0D19F0Addrb70", "B0D19F0Addrbec"},
                    "RP8": {"B0D20F0Addr4a", "B0D20F0Addr104", "B0D20F0Addr19c", "B0D20F0Addr208", 
                                "B0D20F0Addr99e", "B0D20F0Addracc", "B0D20F0Addrb58", "B0D20F0Addrb70", "B0D20F0Addrbec"},
                    "RP9": {"B0D21F0Addr4a", "B0D21F0Addr104", "B0D21F0Addr19c", "B0D21F0Addr208", 
                                "B0D21F0Addr99e", "B0D21F0Addracc", "B0D21F0Addrb58", "B0D21F0Addrb70", "B0D21F0Addrbec"},
                    "RP10": {"B0D22F0Addr4a", "B0D22F0Addr104", "B0D22F0Addr19c", "B0D22F0Addr208", 
                                "B0D22F0Addr99e", "B0D22F0Addracc", "B0D22F0Addrb58", "B0D22F0Addrb70", "B0D22F0Addrbec"},
                    "RP11": {"B0D23F0Addr4a", "B0D23F0Addr104", "B0D23F0Addr19c", "B0D23F0Addr208", 
                                "B0D23F0Addr99e", "B0D23F0Addracc", "B0D23F0Addrb58", "B0D23F0Addrb70", "B0D23F0Addrbec"}
    }
    #16 bit
    dict_reg_addr = { "dict_reg_addr_1": {"DEVSTS": 0x4a, "FRMERRSTS": 0x99e},
                        #32 bit
                        "dict_reg_addr_2":{"ROOT_ERRUNCSTS": 0x104, "ROOT_ERRCORSTS": 0x110, "ROOT_AERHDRLOG1": 0x11c, "ROOT_AERHDRLOG2": 0x120,
                        "ROOT_AERHDRLOG3": 0x124, "ROOT_AERHDRLOG4": 0x128, "ROOTERRSTS": 0x130, "ERRSRCID": 0x134,
                        "RPPIOSTS": 0x19c, "RPPIOHDRLOG1": 0x1b0, "RPPIOHDRLOG2": 0x1b4, "RPPIOHDRLOG3": 0x1b8,
                        "RPPIOHDRLOG4": 0x1bc, "LANEERRSTS": 0x208, "G3SOSERRSTS": 0xacc, "ROOT_LEKBERR": 0xb58,
                        "RCVRERR": 0xb70, "EBERR": 0xb74, "LTSSMERRSTS0": 0xb80, "LTSSMERRSTS1": 0xb84, "G3FRAMEERR": 0x8ec}
    }
    dict_reg_addr_offset_num = {"dict_reg_addr_1": 1, "dict_reg_addr_2": 3}
    DEVSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    DEVSTS_REG_INFO = {0: "DEVSTS bit[0] CED : ", 1: "DEVSTS bit[1] NFED : ", 2: "DEVSTS bit[2] FED : ",
                        3: "DEVSTS bit[3] URD : ", 4: "DEVSTS bit[4] APD : ", 5: "DEVSTS bit[5] TP : "}

    FRMERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
    FRMERRSTS_REG_INFO = {0: "FRMERRSTS bit[0] DW1_ERR : ", 1: "FRMERRSTS bit[1] PAD_ERR : ", 2: "FRMERRSTS bit[2] IDL_ERR : ",
                            3: "FRMERRSTS bit[3] GAP_STP_ERR : ", 4: "FRMERRSTS bit[4] GAP_SDP_ERR : ", 5: "FRMERRSTS bit[5] STP_FRQ_ERR : ",
                            6: "FRMERRSTS bit[6] SDP_FRQ_ERR : ", 7: "FRMERRSTS bit[7] ILL_STP_END_ERR : ", 8: "FRMERRSTS bit[8] DUMP_IN_TLP_ERR : ",
                            9: "FRMERRSTS bit[9] DUMP_IN_DLLP_ERR : "
    }

    ROOT_ERRUNCSTS_BIT = {4: 4, 5: 5, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
                        21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26}
    ROOT_ERRUNCSTS_REG_INFO = {4: "ERRUNCSTS bit[4] DLPE : ", 5: "ERRUNCSTS bit[5] SLDE : ", 12: "ERRUNCSTS bit[12] PTLPE : ",
                            13: "ERRUNCSTS bit[13] FCE : ", 14: "ERRUNCSTS bit[14] CTE : ", 15: "ERRUNCSTS bit[15] CAE : ",
                            16: "ERRUNCSTS bit[16] UCE : ", 17: "ERRUNCSTS bit[17] ROE : ", 18: "ERRUNCSTS bit[18] MTLPE : ",
                            19: "ERRUNCSTS bit[19] ECRCE : ", 20: "ERRUNCSTS bit[20] URE : ", 21: "ERRUNCSTS bit[21] ACSE : ",
                            22: "ERRUNCSTS bit[22] UIE : ", 23: "ERRUNCSTS bit[23] MCE : ", 24: "ERRUNCSTS bit[24] AEBE : ",
                            25: "ERRUNCSTS bit[25] TPBE : ", 26: "ERRUNCSTS bit[26] PTLPEB : "
    }

    ROOT_ERRCORSTS_BIT = {0: 0, 6: 6, 7: 7, 8: 8, 12: 12, 13: 13, 14: 14, 15: 15}
    ROOT_ERRCORSTS_REG_INFO = {0: "ERRCORSTS bit[0] RE : ", 6: "ERRCORSTS bit[6] BTLPE : ", 7: "ERRCORSTS bit[7] BDLLPE : ",
                            8: "ERRCORSTS bit[8] RNRE : ", 12: "ERRCORSTS bit[12] RTTE : ", 13: "ERRCORSTS bit[13] ANFE : ",
                            14: "ERRCORSTS bit[14] CIE : ", 15: "ERRCORSTS bit[15] HLOE : "
    }

    ROOT_AERHDRLOG1_BIT = {0: 31}
    ROOT_AERHDRLOG1_REG_INFO = {0: "AERHDRLOG1 bits[0:31] TLPHDRLOG : "}

    ROOT_AERHDRLOG2_BIT = {0: 31}
    ROOT_AERHDRLOG2_REG_INFO = {0: "AERHDRLOG2 bits[0:31] TLPHDRLOG : "}

    ROOT_AERHDRLOG3_BIT = {0: 31}
    ROOT_AERHDRLOG3_REG_INFO = {0: "AERHDRLOG3 bits[0:31] TLPHDRLOG : "}

    ROOT_AERHDRLOG4_BIT = {0: 31}
    ROOT_AERHDRLOG4_REG_INFO = {0: "AERHDRLOG4 bits[0:31] TLPHDRLOG : "}

    ROOTERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 27: 31}
    ROOTERRSTS_REG_INFO = {0: "ROOTERRSTS bit[0] CER : ", 1: "ROOTERRSTS bit[1] MCER : ", 2: "ROOTERRSTS bit[2] EFR : ",
                            3: "ROOTERRSTS bit[3] MEFR : ", 4: "ROOTERRSTS bit[4] FUF : ", 5: "ROOTERRSTS bit[5] NFEMR : ",
                            6: "ROOTERRSTS bit[6] FEMR : ", 27: "ROOTERRSTS bits[27:31] AEMN : "
    }

    ERRSRCID_BIT = {0: 15, 16: 31}
    ERRSRCID_REG_INFO = {0: "ERRSRCID bits[0:15] ECSID : ", 16: "ERRSRCID bits[16:31] EFSID : "}

    RPPIOSTS_BIT = {0: 0, 1: 1, 2: 2, 8: 8, 9: 9, 10: 10, 16: 16, 17: 17, 18: 18}
    RPPIOSTS_REG_INFO = {0: "RPPIOSTS bit[0] CFGURC : ", 1: "RPPIOSTS bit[1] CFGCAC : ", 2: "RPPIOSTS bit[2] CFGCTO : ",
                            8: "RPPIOSTS bit[8] IOURC : ", 9: "RPPIOSTS bit[9] IOCAC : ", 10: "RPPIOSTS bit[10] IOCTO : ",
                            16: "RPPIOSTS bit[16] MEMURC : ", 17: "RPPIOSTS bit[17] MEMCAC : ", 18: "RPPIOSTS bit[18] MEMCTO : "
    }

    RPPIOHDRLOG1_BIT = {0: 31}
    RPPIOHDRLOG1_REG_INFO = {0: "RPPIOHDRLOG1 bits[0:31] HB : "}

    RPPIOHDRLOG2_BIT = {0: 31}
    RPPIOHDRLOG2_REG_INFO = {0: "RPPIOHDRLOG2 bits[0:31] HB : "}

    RPPIOHDRLOG3_BIT = {0: 31}
    RPPIOHDRLOG3_REG_INFO = {0: "RPPIOHDRLOG3 bits[0:31] HB : "}

    RPPIOHDRLOG4_BIT = {0: 31}
    RPPIOHDRLOG4_REG_INFO = {0: "RPPIOHDRLOG4 bits[0:31] HB : "}

    LANEERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    LANEERRSTS_REG_INFO = {0: "LANEERRSTS bit[0] L0ERR : ", 1: "LANEERRSTS bit[1] L1ERR : ", 2: "LANEERRSTS bit[2] L2ERR : ",
                            3: "LANEERRSTS bit[3] L3ERR : ", 4: "LANEERRSTS bit[4] L4ERR : ", 5: "LANEERRSTS bit[5] L5ERR : ",
                            6: "LANEERRSTS bit[6] L6ERR : ", 7: "LANEERRSTS bit[7] L7ERR : "
    }

    G3SOSERRSTS_BIT = {0: 15, 16: 31}
    G3SOSERRSTS_REG_INFO = {0: "G3SOSERRSTS bits[0:15] PARERR : ", 16: "G3SOSERRSTS bits[16:31] LFSRERR : "}

    ROOT_LEKBERR_BIT = {0: 19, 20: 24, 25: 29, 31: 31}
    ROOT_LEKBERR_REG_INFO = {0: "LEKBERR bits[0:19] AGGRERR : ", 20: "LEKBERR bits[20:24] ERRTHRESH : ",
                        25: "LEKBERR bits[25:29] G3ERRTHRESH : ", 31: "LEKBERR bit[31] G3LBEEN : "
    }

    RCVRERR_BIT = {0: 7, 16: 23}
    RCVRERR_REG_INFO = {0: "RCVRERR bits[0:7] LANE : ", 16: "RCVRERR bits[16:23] MASK : "}

    EBERR_BIT = {0: 7, 16: 23}
    EBERR_REG_INFO = {0: "EBERR bits[0:7] EBEMPTYERR : ", 16: "EBERR bits[16:23] EBFULLERR : "}

    LTSSMERRSTS0_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                            13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22,
                            23: 23, 24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29}
    LTSSMERRSTS0_REG_INFO = {0: "LTSSMERRSTS0 bit[0] SPEEDCHANGEFAIL : ", 1: "LTSSMERRSTS0 bit[1] PARTIAL_RCVRDET : ",
                                2: "LTSSMERRSTS0 bit[2] POLACT_NOTS : ", 3: "LTSSMERRSTS0 bit[3] POLCFG_NOTS : ",
                                4: "LTSSMERRSTS0 bit[4] CFGLNKWDST_TO : ", 5: "LTSSMERRSTS0 bit[5] CFGLNKWDAC_TO : ",
                                6: "LTSSMERRSTS0 bit[6] CFGLNNUMWT_TO : ", 7: "LTSSMERRSTS0 bit[7] CFGLNNUMAC_TO : ",
                                8: "LTSSMERRSTS0 bit[8] CFGCMPLT_TO : ", 9: "LTSSMERRSTS0 bit[9] CFGIDLE_TO : ",
                                10: "LTSSMERRSTS0 bit[10] UPL12RCVEIOS_TO : ", 11: "LTSSMERRSTS0 bit[11] RECRCVRLCKDOWN_TO : ",
                                12: "LTSSMERRSTS0 bit[12] RECRCVRLCKBW_TO : ", 13: "LTSSMERRSTS0 bit[13] RECSPDIDLWTEI_TO : ",
                                14: "LTSSMERRSTS0 bit[14] RECSPDEXITEIEX_TO : ", 15: "LTSSMERRSTS0 bit[15] RECRCVRCFGDOWN_TO : ",
                                16: "LTSSMERRSTS0 bit[16] RECRCVRCFGSPDOWN_TO : ", 17: "LTSSMERRSTS0 bit[17] RECIDLEDOWN_TO : ",
                                18: "LTSSMERRSTS0 bit[18] DISWTEIOS_TO : ", 19: "LTSSMERRSTS0 bit[19] LBMSTENTRY_TO : ",
                                20: "LTSSMERRSTS0 bit[20] UNEXPECTEDEI : ", 21: "LTSSMERRSTS0 bit[21] RXL0SFTS_TO : ",
                                22: "LTSSMERRSTS0 bit[22] RECRCVRLCKNOTALLTS : ", 23: "LTSSMERRSTS0 bit[23] RECRCVRLCKWIDTH : ",
                                24: "LTSSMERRSTS0 bit[24] EQPH0_TO : ", 25: "LTSSMERRSTS0 bit[25] EQPH1_TO : ",
                                26: "LTSSMERRSTS0 bit[26] EQSEVASYNC_TO : ", 27: "LTSSMERRSTS0 bit[27] EQSEVA_TO : ",
                                28: "LTSSMERRSTS0 bit[28] EQMEVALCK_TO : ", 29: "LTSSMERRSTS0 bit[29] EQMEVAL_TO : "
    }

    LTSSMERRSTS1_BIT = {0: 2, 3: 3, 4: 6, 7: 7, 27: 31}
    LTSSMERRSTS1_REG_INFO = {0: "LTSSMERRSTS1 bits[0:2] G2FAILCTR : ", 3: "LTSSMERRSTS1 bit[3] G2FAILLIMERR : ",
                                4: "LTSSMERRSTS1 bits[4:6] G3FAILCTR : ", 7: "LTSSMERRSTS1 bit[7] G3FAILLIMERR : ",
                                27: "LTSSMERRSTS1 bits[27:31] LTERR0FERR : "
    }

    G3FRAMEERR_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 27: 30}
    G3FRAMEERR_REG_INFO = {0: "G3FRAMEERR bit[0] RDOK : ", 1: "G3FRAMEERR bit[1] SDP2 : ", 2: "G3FRAMEERR bit[2] STP2 : ",
                            3: "G3FRAMEERR bit[3] EDS : ", 4: "G3FRAMEERR bit[4] BK1FE : ", 5: "G3FRAMEERR bit[5] BKFE : ",
                            6: "G3FRAMEERR bit[6] SDSFE : ", 7: "G3FRAMEERR bit[7] ITKNTL : ", 8: "G3FRAMEERR bit[8] ITKNDL : ",
                            9: "G3FRAMEERR bit[9] ITKNLI : ", 10: "G3FRAMEERR bit[10] ITKNL0 : ", 11: "G3FRAMEERR bit[11] FCRC : ",
                            27: "G3FRAMEERR bits[27:30] G3FRAMEFERR : "
    }
    output = ""
    try:
        if rp_num in dict_key_name:
            for key in dict_key_name[rp_num]:
                print_flag = 0
                if key in value:
                    output_tmp = "%s : " % key
                    for reg_addr in dict_reg_addr:
                        for reg in dict_reg_addr[reg_addr]:
                            dict_bit = reg + "_BIT"
                            dict_reg_info = reg + "_REG_INFO"
                            beg_addr = 0
                            if re.search("Addrbec",key) :
                                if dict_reg_addr[reg_addr][reg] < 0xbec :
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0xbec
                            elif re.search("Addrb70",key) :
                                if dict_reg_addr[reg_addr][reg] < 0xb70: 
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0xb70
                            elif re.search("Addrb58",key) :
                                if dict_reg_addr[reg_addr][reg] < 0xb58:
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0xb58
                            elif re.search("Addracc",key) :
                                if dict_reg_addr[reg_addr][reg] < 0xacc:
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0xacc
                            elif re.search("Addr99e",key) :
                                if dict_reg_addr[reg_addr][reg] < 0x99e:
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0x99e
                            elif re.search("Addr208",key) :
                                if dict_reg_addr[reg_addr][reg] < 0x208:
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0x208
                            elif re.search("Addr19c",key) :
                                if dict_reg_addr[reg_addr][reg] < 0x19c :
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0x19c
                            elif re.search("Addr104",key) :
                                if dict_reg_addr[reg_addr][reg] < 0x104 :
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0x104
                            elif re.search("Addr4a",key) :
                                if dict_reg_addr[reg_addr][reg] < 0x4a:
                                    continue
                                beg_addr = dict_reg_addr[reg_addr][reg] - 0x4a
                            else:
                                continue
                            end_addr = beg_addr + dict_reg_addr_offset_num[reg_addr]
                            reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                            if dict_reg_addr_offset_num[reg_addr] == 1:
                                ret_value = hex_to_bin_bit(reg_value[0:2], key)
                            else:
                                ret_value = hex_to_bin_bit(reg_value[0:4], key)
                            for beg_bit in locals().get(dict_bit):
                                ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                                if ret_output not in output_tmp:
                                    output_tmp = output_tmp + ret_output
                                if ret:
                                    print_flag = 1
                            if print_flag :
                                output = output + output_tmp
                                output_tmp = ""
    except Exception as e:
        output = output + "Parse %s: %s" % (rp_num, str(e))
        print(output)
    return output

def parse_peci_pch_sata_D1734(value):
    list_key_name = {"B0D14F0Addr6"}
    dict_reg_addr = {"DVESTS": 0x6}

    DVESTS_BIT = {3: 3, 4: 4, 8: 8, 9: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    DVESTS_REG_INFO = {3: "DVESTS bit[3] IS : ", 4: "DVESTS bit[4] CL : ",
                        8: "DVESTS bit[8] DPD : ", 9: "DVESTS bits[9:10] DEVT : ",
                        11: "DVESTS bit[11] STA : ", 12: "DVESTS bit[12] RTA : ",
                        13: "DVESTS bit[13] RMA : ", 14: "DVESTS bit[14] SSE : ",
                        15: "DVESTS bit[15] DPE : "
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x6
                    end_addr = beg_addr + 1
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:2], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:2]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse sata failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Sata part : " + output + "\n"
    return output

def parse_peci_pch_usb_D1734(value):
    list_key_name = {"B0D30F0Addr6"}
    dict_reg_addr = {"DVESTS": 0x6}

    DVESTS_BIT = {3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    DVESTS_REG_INFO = {3: "DVESTS bit[3] IS : ", 4: "DVESTS bit[4] CL : ", 5: "DVESTS bit[5] MC : ",
                        6: "DVESTS bit[6] UDF : ", 7: "DVESTS bit[7] FBBC : ", 8: "DVESTS bit[8] MDPED : ",
                        9: "DVESTS bits[9:10] DEVT : ", 11: "DVESTS bit[11] STA : ", 12: "DVESTS bit[12] RTA : ",
                        13: "DVESTS bit[13] RMA : ", 14: "DVESTS bit[14] SSE : ", 15: "DVESTS bit[15] DPE : ",
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x6
                    end_addr = beg_addr + 1
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:2], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:2]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse usb failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Usb part : " + output + "\n"
    return output

def parse_peci_pch_lpc_D1734(value):
    list_key_name = {"B0D31F0Addr6"}
    dict_reg_addr = {"DVESTS": 0x6}

    DVESTS_BIT = {3: 3, 4: 4, 5: 5, 7: 7, 8: 8, 9: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    DVESTS_REG_INFO = {3: "DVESTS bit[3] INTRSTS : ", 4: "DVESTS bit[4] CLIST : ", 5: "DVESTS bit[5] C66 : ",
                        7: "DVESTS bit[7] FBC : ", 8: "DVESTS bit[8] DPD : ", 9: "DVESTS bits[9:10] DTS : ",
                        11: "DVESTS bit[11] STA : ", 12: "DVESTS bit[12] RTA : ", 13: "DVESTS bit[13] RMA : ",
                        14: "DVESTS bit[14] SSE : ", 15: "DVESTS bit[15] DPE : "
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x6
                    end_addr = beg_addr + 1
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:2], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:2]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse lpc failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Lpc part : " + output + "\n"
    return output

def parse_peci_pch_legacy_smbus_D1734(value):
    list_key_name = {"B0D31F4Addr6"}
    dict_reg_addr = {"DS": 0x6}

    DS_BIT = {3: 3, 4: 4, 5: 5, 6: 6 , 7: 7, 8: 8, 9: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    DS_REG_INFO = {3: "DS bit[3] INTS : ", 4: "DS bit[4] CLI : ", 5: "DS bit[5] C_66M : ",
                    6: "DS bit[6] UDF : ", 7: "DS bit[7] FBC : ", 8: "DS bit[8] DPED : ",
                    9: "DS bits[9:10] DEVT : ", 11: "DS bit[11] STA : ", 12: "DS bit[12] RTA : ",
                    13: "DS bit[13] RMA : ", 14: "DS bit[14] SSE : ", 15: "DS bit[15] DPE : ",
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x6
                    end_addr = beg_addr + 1
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:2], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:2]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse legacy smbus failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Legacy smbus part : " + output + "\n"
    return output

def parse_peci_pch_spi_D1734(value):
    list_key_name = {"B0D31F5Addr4", "B0D31F5Addrd0"}
    dict_reg_addr = {"BIOS_SPI_STS_CMD": 0x4, "BIOS_SPI_UR_STS_CTL": 0xd0}

    BIOS_SPI_STS_CMD_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 8: 8, 9: 9, 10: 10, 19: 19, 20: 20, 21: 21,
                            23: 23, 24: 24, 25: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    BIOS_SPI_STS_CMD_REG_INFO = {0: "BIOS_SPI_STS_CMD bit[0] IOSE : ", 1: "BIOS_SPI_STS_CMD bit[1] MSE : ",
                                    2: "BIOS_SPI_STS_CMD bit[2] BME : ", 3: "BIOS_SPI_STS_CMD bit[3] SPCYC : ",
                                    4: "BIOS_SPI_STS_CMD bit[4] MWRIEN : ", 5: "BIOS_SPI_STS_CMD bit[5] VGAPS : ",
                                    6: "BIOS_SPI_STS_CMD bit[6] PERRR : ", 8: "BIOS_SPI_STS_CMD bit[8] SERREN : ",
                                    9: "BIOS_SPI_STS_CMD bit[9] FBTBEN : ", 10: "BIOS_SPI_STS_CMD bit[10] INTD : ",
                                    19: "BIOS_SPI_STS_CMD bit[19] INTS : ", 20: "BIOS_SPI_STS_CMD bit[20] CAPL : ",
                                    21: "BIOS_SPI_STS_CMD bit[21] MCAP : ", 23: "BIOS_SPI_STS_CMD bit[23] FBTBC : ",
                                    24: "BIOS_SPI_STS_CMD bit[24] MDPE : ", 25: "BIOS_SPI_STS_CMD bits[25:26] DEVT : ",
                                    27: "BIOS_SPI_STS_CMD bit[27] STA : ", 28: "BIOS_SPI_STS_CMD bit[28] RTA : ",
                                    29: "BIOS_SPI_STS_CMD bit[29] RMA : ", 30: "BIOS_SPI_STS_CMD bit[30] SSE : ",
                                    31: "BIOS_SPI_STS_CMD bit[31] DPE : "
    }

    BIOS_SPI_UR_STS_CTL_BIT = {0: 0, 1: 1}
    BIOS_SPI_UR_STS_CTL_REG_INFO = {0: "BIOS_SPI_UR_STS_CTL bit[0] URRE : ", 1: "BIOS_SPI_UR_STS_CTL bit[0] URD : "}

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = 0
                    if re.search("Addrd0",key) :
                        if dict_reg_addr[reg] < 0xd0:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0xd0
                    elif re.search("Addr4",key) :
                        if dict_reg_addr[reg] < 0x4:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0x4
                    else:
                        continue
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse spi failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Spi part : " + output + "\n"
    return output

def parse_peci_pch_trace_hub_D1734(value):
    list_key_name = {"B0D31F7Addr4"}
    dict_reg_addr = {"CMD": 0x4}

    CMD_BIT = {0: 0, 1: 1, 2: 2, 6: 6, 8: 8, 10: 10, 19: 19, 20: 20, 24: 24, 27: 27,
                28: 28, 29: 29, 30: 30, 31: 31}

    CMD_REG_INFO = {0: "CMD bit[0] IOSE", 1: "CMD bit[1] MEM", 2: "CMD bit[2] BME",
                        6: "CMD bit[6] PERE", 8: "CMD bit[8] SERREN", 10: "CMD bit[10] INTDIS",
                        19: "CMD bit[19] INSTAT", 20: "CMD bit[20] CLIST", 24: "CMD bit[24] MDPE",
                        27: "CMD bit[27] STA", 28: "CMD bit[28] RTA", 29: "CMD bit[29] RMA",
                        30: "CMD bit[30] SSE", 31: "CMD bit[31] DPE"
    }

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x4
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse trace hub failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Pch trace hub part : " + output + "\n"
    return output

def parse_peci_pch_hsuart_D1734(value):
    list_key_name = {"B0D26F0Addr4", "B0D26F1Addr4", "B0D26F2Addr4"}
    dict_reg_addr = {"CMD_STAT_REG": 0x4}

    CMD_STAT_REG_BIT = {0: 0, 1: 1, 2: 2, 3: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 15, 16: 18, 19: 19,
                        20: 20, 21: 23, 24: 24, 25: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31}
    CMD_STAT_REG_REG_INFO = {0: "CMD_STAT_REG bit[0] COMMAND_IO_ACCESS_ENABLE : ", 1: "CMD_STAT_REG bit[1] COMMAND_MEM_ACCESS_ENABLE : ",
                                2: "CMD_STAT_REG bit[2] COMMAND_BUS_ACCESS_ENABLE : ", 3: "CMD_STAT_REG bits[3:5] COMMAND_RESERVED_3 : ",
                                6: "CMD_STAT_REG bit[6] COMMAND_PARITY_ERROR_RESPONSE_ENABLE : ", 7: "CMD_STAT_REG bit[7] COMMAND_RESERVED_7 : ",
                                8: "CMD_STAT_REG bit[8] COMMAND_SERR_ENABLE : ", 9: "CMD_STAT_REG bit[9] COMMAND_RESERVED_9 : ",
                                10: "CMD_STAT_REG bit[10] COMMAND_INTERRUPT_DISABLE : ", 11: "CMD_STAT_REG bits[11:15] COMMAND_RESERVED_11 : ",
                                16: "CMD_STAT_REG bits[16:18] STATUS_RESERVED_16 : ", 19: "CMD_STAT_REG bit[19] STATUS_INTERRUPT_STATUS : ",
                                20: "CMD_STAT_REG bit[20] STATUS_NEW_CAP : ", 21: "CMD_STAT_REG bits[21:23] STATUS_RESERVED_21 : ",
                                24: "CMD_STAT_REG bit[24] STATUS_MASTER_DATA_PARITY_ERROR : ", 25: "CMD_STAT_REG bits[25:26] STATUS_RESERVED_25 : ",
                                27: "CMD_STAT_REG bit[27] STATUS_SIGNALED_TARGET_ABORT : ", 28: "CMD_STAT_REG bit[28] STATUS_RECEIVED_TARGET_ABORT : ",
                                29: "CMD_STAT_REG bit[29] STATUS_RECEIVED_MASTER_ABORT : ", 30: "CMD_STAT_REG bit[30] STATUS_SIGNALED_SYSTEM_ERROR : ",
                                31: "CMD_STAT_REG bit[31] STATUS_DETECTED_PARITY_ERROR : "
    }

    output = ""
    try:
        for key in list_key_name:
            print_flag = 0
            if key in value:
                for reg in dict_reg_addr:
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x4
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse hsuart failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Hsuart part : " + output + "\n"
    return output

def parse_peci_pch_smbus_ctl_D1734(value):
    list_key_name = {"B0D15F0Addr4", "B0D15F0Addr4a"}
    dict_reg_addr = {"SMBUS_PCISTS": 0x6, "SMBUS_DEVSTS": 0x4a}

    SMBUS_PCISTS_BIT = {3: 3, 4: 4, 8: 8, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15}
    SMBUS_PCISTS_REG_INFO = {3: "PCISTS bit[3] INTS : ", 4: "PCISTS bit[4] CAPE : ", 8: "PCISTS bit[8] MDPD : ",
                        11: "PCISTS bit[11] STA : ", 12: "PCISTS bit[12] RTA : ", 13: "PCISTS bit[13] RMA : ",
                        14: "PCISTS bit[14] SSE : ", 15: "PCISTS bit[15] DPE : "
    }

    SMBUS_DEVSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 5: 5}
    SMBUS_DEVSTS_REG_INFO = {0: "DEVSTS bit[0] CED : ", 1: "DEVSTS bit[1] NFED : ", 2: "DEVSTS bit[2] FED : ",
                        3: "DEVSTS bit[3] URD : ", 5: "DEVSTS bit[5] TP : "}

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = 0
                    if re.search("Addr4a",key) :
                        if dict_reg_addr[reg] < 0x4a:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0x4a
                    elif re.search("Addr4",key) :
                        if dict_reg_addr[reg] < 0x6:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0x6
                    else:
                        continue
                    end_addr = beg_addr + 1
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:2], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:2]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
    except Exception as e:
        output = output + "Parse smbus ctl failed: %s" % str(e)
        print(output)
    if len(output) > 0:
        output  = "Smbus part : " + output + "\n"
    return output

def parse_peci_pch_dev_D1734(dict_dev_bit_value, value):
    dict_dev_bit_name= {0: "IEH", 1: "RP0", 2: "RP1", 3: "RP2", 4: "RP3", 5: "RP4", 6: "RP5", 7: "RP6", 8: "RP7", 9: "RP8",
                        10: "RP9", 11: "RP10", 12: "RP11", 13: "VRP", 14: "SATA0", 15: "SATA1", 16: "SATA2", 17: "USB",
                        18: "LPC", 19: "Legacy SMBUS", 20: "ESPI", 21: "Trace Hub", 22: "HSUART", 23: "SMBUS"
    }

    output = ""
    for bit in dict_dev_bit_value:
        if dict_dev_bit_value[bit] == 1:
            if bit == 0:
                output = output + parse_peci_pch_ieh_D1734(value, {"B0D29F0Addr280"})
            elif bit >= 14 and bit <= 16:
                output = output +parse_peci_pch_sata_D1734(value)
            elif bit == 17:
                output = output +parse_peci_pch_usb_D1734(value)
            elif bit == 18:
                output = output +parse_peci_pch_lpc_D1734(value)
            elif bit == 19:
                output = output +parse_peci_pch_legacy_smbus_D1734(value)
            elif bit == 20:
                output = output +parse_peci_pch_spi_D1734(value)
            elif bit == 21:
                output = output +parse_peci_pch_trace_hub_D1734(value)
            elif bit == 22:
                output = output +parse_peci_pch_hsuart_D1734(value)
            elif bit == 23:
                output = output +parse_peci_pch_smbus_ctl_D1734(value)
            else:
                output = output
    return output

def parse_peci_pch_err_D1734(value):
    list_key_name = {"B0D29F0Addr200"}
    dict_reg_addr = {"GCOERRSTS": 0x200, "GCOFERRSTS": 0x204, "GCONERRSTS": 0x208, "GNFERRSTS": 0x210,
                        "GNFFERRSTS": 0x214, "GNFNERRSTS": 0x218, "GFAERRSTS": 0x220, "GFAFERRSTS": 0x224,
                        "GFANERRSTS": 0x228}
    GCOERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GCOERRSTS_REG_INFO = {0: "GCOERRSTS bit[0] IEHLOCAL_CO_STS : ", 1: "GCOERRSTS bit[1] RP0_CO_STS : ", 2: "GCOERRSTS bit[2] RP1_CO_STS : ",
                            3: "GCOERRSTS bit[3] RP2_CO_STS : ", 4: "GCOERRSTS bit[4] RP3_CO_STS : ", 5: "GCOERRSTS bit[5] RP4_CO_STS : ",
                            6: "GCOERRSTS bit[6] RP5_CO_STS : ", 7: "GCOERRSTS bit[7] RP6_CO_STS : ", 8: "GCOERRSTS bit[8] RP7_CO_STS : ",
                            9: "GCOERRSTS bit[9] RP8_CO_STS : ", 10: "GCOERRSTS bit[10] RP9_CO_STS : ", 11: "GCOERRSTS bit[11] RP10_CO_STS : ",
                            12: "GCOERRSTS bit[12] RP11_CO_STS : ", 13: "GCOERRSTS bit[13] VRP_CO_STS : ", 14: "GCOERRSTS bit[14] SATA0_CO_STS : ",
                            15: "GCOERRSTS bit[15] SATA1_CO_STS : ", 16: "GCOERRSTS bit[16] SATA2_CO_STS : ", 17: "GCOERRSTS bit[17] USB_CO_STS : ",
                            18: "GCOERRSTS bit[18] LPC_CO_STS : ", 19: "GCOERRSTS bit[19] LSMBUS_CO_STS : ", 20: "GCOERRSTS bit[20] SPIESPI_CO_STS : ",
                            21: "GCOERRSTS bit[21] NPK_CO_STS : ", 22: "GCOERRSTS bit[22] HSUART_CO_STS : ", 23: "GCOERRSTS bit[23] GSMBUS_CO_STS : ",
    }

    GCOFERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GCOFERRSTS_REG_INFO = {0: "GCOFERRSTS bit[0] IEHLOCAL_CO_FERR : ", 1: "GCOFERRSTS bit[1] RP0_CO_FERR : ", 2: "GCOFERRSTS bit[2] RP1_CO_FERR : ",
                            3: "GCOFERRSTS bit[3] RP2_CO_FERR : ", 4: "GCOFERRSTS bit[4] RP3_CO_FERR : ", 5: "GCOFERRSTS bit[5] RP4_CO_FERR : ",
                            6: "GCOFERRSTS bit[6] RP5_CO_FERR : ", 7: "GCOFERRSTS bit[7] RP6_CO_FERR : ", 8: "GCOFERRSTS bit[8] RP7_CO_FERR : ",
                            9: "GCOFERRSTS bit[9] RP8_CO_FERR : ", 10: "GCOFERRSTS bit[10] RP9_CO_FERR : ", 11: "GCOFERRSTS bit[11] RP10_CO_FERR : ",
                            12: "GCOFERRSTS bit[12] RP11_CO_FERR : ", 13: "GCOFERRSTS bit[13] VRP_CO_FERR : ", 14: "GCOFERRSTS bit[14] SATA0_CO_FERR : ",
                            15: "GCOFERRSTS bit[15] SATA1_CO_FERR : ", 16: "GCOFERRSTS bit[16] SATA2_CO_FERR : ", 17: "GCOFERRSTS bit[17] USB_CO_FERR : ",
                            18: "GCOFERRSTS bit[18] LPC_CO_FERR : ", 19: "GCOFERRSTS bit[19] LSMBUS_CO_FERR : ", 20: "GCOFERRSTS bit[20] SPIESPI_CO_FERR : ",
                            21: "GCOFERRSTS bit[21] NPK_CO_FERR : ", 22: "GCOFERRSTS bit[22] HSUART_CO_FERR : ", 23: "GCOFERRSTS bit[23] GSMBUS_CO_FERR : ",
    }

    GCONERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GCONERRSTS_REG_INFO = {0: "GCONERRSTS bit[0] IEHLOCAL_CO_NERR : ", 1: "GCONERRSTS bit[1] RP0_CO_NERR : ", 2: "GCONERRSTS bit[2] RP1_CO_NERR : ",
                            3: "GCONERRSTS bit[3] RP2_CO_NERR : ", 4: "GCONERRSTS bit[4] RP3_CO_NERR : ", 5: "GCONERRSTS bit[5] RP4_CO_NERR : ",
                            6: "GCONERRSTS bit[6] RP5_CO_NERR : ", 7: "GCONERRSTS bit[7] RP6_CO_NERR : ", 8: "GCONERRSTS bit[8] RP7_CO_NERR : ",
                            9: "GCONERRSTS bit[9] RP8_CO_NERR : ", 10: "GCONERRSTS bit[10] RP9_CO_NERR : ", 11: "GCONERRSTS bit[11] RP10_CO_NERR : ",
                            12: "GCONERRSTS bit[12] RP11_CO_NERR : ", 13: "GCONERRSTS bit[13] VRP_CO_NERR : ", 14: "GCONERRSTS bit[14] SATA0_CO_NERR : ",
                            15: "GCONERRSTS bit[15] SATA1_CO_NERR : ", 16: "GCONERRSTS bit[16] SATA2_CO_NERR : ", 17: "GCONERRSTS bit[17] USB_CO_NERR : ",
                            18: "GCONERRSTS bit[18] LPC_CO_NERR : ", 19: "GCONERRSTS bit[19] LSMBUS_CO_NERR : ", 20: "GCONERRSTS bit[20] SPIESPI_CO_NERR : ",
                            21: "GCONERRSTS bit[21] NPK_CO_NERR : ", 22: "GCONERRSTS bit[22] HSUART_CO_NERR : ", 23: "GCONERRSTS bit[23] GSMBUS_CO_NERR : ",
    }

    GNFERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GNFERRSTS_REG_INFO = {0: "GNFERRSTS bit[0] IEHLOCAL_NF_STS : ", 1: "GNFERRSTS bit[1] RP0_NF_STS : ", 2: "GNFERRSTS bit[2] RP1_NF_STS : ",
                            3: "GNFERRSTS bit[3] RP2_NF_STS : ", 4: "GNFERRSTS bit[4] RP3_NF_STS : ", 5: "GNFERRSTS bit[5] RP4_NF_STS : ",
                            6: "GNFERRSTS bit[6] RP5_NF_STS : ", 7: "GNFERRSTS bit[7] RP6_NF_STS : ", 8: "GNFERRSTS bit[8] RP7_NF_STS : ",
                            9: "GNFERRSTS bit[9] RP8_NF_STS : ", 10: "GNFERRSTS bit[10] RP9_NF_STS : ", 11: "GNFERRSTS bit[11] RP10_NF_STS : ",
                            12: "GNFERRSTS bit[12] RP11_NF_STS : ", 13: "GNFERRSTS bit[13] VRP_NF_STS : ", 14: "GNFERRSTS bit[14] SATA0_NF_STS : ",
                            15: "GNFERRSTS bit[15] SATA1_NF_STS : ", 16: "GNFERRSTS bit[16] SATA2_NF_STS : ", 17: "GNFERRSTS bit[17] USB_NF_STS : ",
                            18: "GNFERRSTS bit[18] LPC_NF_STS : ", 19: "GNFERRSTS bit[19] LSMBUS_NF_STS : ", 20: "GNFERRSTS bit[20] SPIESPI_NF_STS : ",
                            21: "GNFERRSTS bit[21] NPK_NF_STS : ", 22: "GNFERRSTS bit[22] HSUART_NF_STS : ", 23: "GNFERRSTS bit[23] GSMBUS_NF_STS : ",
    }

    GNFFERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GNFFERRSTS_REG_INFO = {0: "GNFFERRSTS bit[0] IEHLOCAL_NF_FERR : ", 1: "GNFFERRSTS bit[1] RP0_NF_FERR : ", 2: "GNFFERRSTS bit[2] RP1_NF_FERR : ",
                            3: "GNFFERRSTS bit[3] RP2_NF_FERR : ", 4: "GNFFERRSTS bit[4] RP3_NF_FERR : ", 5: "GNFFERRSTS bit[5] RP4_NF_FERR : ",
                            6: "GNFFERRSTS bit[6] RP5_NF_FERR : ", 7: "GNFFERRSTS bit[7] RP6_NF_FERR : ", 8: "GNFFERRSTS bit[8] RP7_NF_FERR : ",
                            9: "GNFFERRSTS bit[9] RP8_NF_FERR : ", 10: "GNFFERRSTS bit[10] RP9_NF_FERR : ", 11: "GNFFERRSTS bit[11] RP10_NF_FERR : ",
                            12: "GNFFERRSTS bit[12] RP11_NF_FERR : ", 13: "GNFFERRSTS bit[13] VRP_NF_FERR : ", 14: "GNFFERRSTS bit[14] SATA0_NF_FERR : ",
                            15: "GNFFERRSTS bit[15] SATA1_NF_FERR : ", 16: "GNFFERRSTS bit[16] SATA2_NF_FERR : ", 17: "GNFFERRSTS bit[17] USB_NF_FERR : ",
                            18: "GNFFERRSTS bit[18] LPC_NF_FERR : ", 19: "GNFFERRSTS bit[19] LSMBUS_NF_FERR : ", 20: "GNFFERRSTS bit[20] SPIESPI_NF_FERR : ",
                            21: "GNFFERRSTS bit[21] NPK_NF_FERR : ", 22: "GNFFERRSTS bit[22] HSUART_NF_FERR : ", 23: "GNFFERRSTS bit[23] GSMBUS_NF_FERR : ",
    }

    GNFNERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GNFNERRSTS_REG_INFO = {0: "GNFNERRSTS bit[0] IEHLOCAL_NF_NERR : ", 1: "GNFNERRSTS bit[1] RP0_NF_NERR : ", 2: "GNFNERRSTS bit[2] RP1_NF_NERR : ",
                            3: "GNFNERRSTS bit[3] RP2_NF_NERR : ", 4: "GNFNERRSTS bit[4] RP3_NF_NERR : ", 5: "GNFNERRSTS bit[5] RP4_NF_NERR : ",
                            6: "GNFNERRSTS bit[6] RP5_NF_NERR : ", 7: "GNFNERRSTS bit[7] RP6_NF_NERR : ", 8: "GNFNERRSTS bit[8] RP7_NF_NERR : ",
                            9: "GNFNERRSTS bit[9] RP8_NF_NERR : ", 10: "GNFNERRSTS bit[10] RP9_NF_NERR : ", 11: "GNFNERRSTS bit[11] RP10_NF_NERR : ",
                            12: "GNFNERRSTS bit[12] RP11_NF_NERR : ", 13: "GNFNERRSTS bit[13] VRP_NF_NERR : ", 14: "GNFNERRSTS bit[14] SATA0_NF_NERR : ",
                            15: "GNFNERRSTS bit[15] SATA1_NF_NERR : ", 16: "GNFNERRSTS bit[16] SATA2_NF_NERR : ", 17: "GNFNERRSTS bit[17] USB_NF_NERR : ",
                            18: "GNFNERRSTS bit[18] LPC_NF_NERR : ", 19: "GNFNERRSTS bit[19] LSMBUS_NF_NERR : ", 20: "GNFNERRSTS bit[20] SPIESPI_NF_NERR : ",
                            21: "GNFNERRSTS bit[21] NPK_NF_NERR : ", 22: "GNFNERRSTS bit[22] HSUART_NF_NERR : ", 23: "GNFNERRSTS bit[23] GSMBUS_NF_NERR : ",
    }

    GFAERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GFAERRSTS_REG_INFO = {0: "GFAERRSTS bit[0] IEHLOCAL_FA_STS : ", 1: "GFAERRSTS bit[1] RP0_FA_STS : ", 2: "GFAERRSTS bit[2] RP1_FA_STS : ",
                            3: "GFAERRSTS bit[3] RP2_FA_STS : ", 4: "GFAERRSTS bit[4] RP3_FA_STS : ", 5: "GFAERRSTS bit[5] RP4_FA_STS : ",
                            6: "GFAERRSTS bit[6] RP5_FA_STS : ", 7: "GFAERRSTS bit[7] RP6_FA_STS : ", 8: "GFAERRSTS bit[8] RP7_FA_STS : ",
                            9: "GFAERRSTS bit[9] RP8_FA_STS : ", 10: "GFAERRSTS bit[10] RP9_FA_STS : ", 11: "GFAERRSTS bit[11] RP10_FA_STS : ",
                            12: "GFAERRSTS bit[12] RP11_FA_STS : ", 13: "GFAERRSTS bit[13] VRP_FA_STS : ", 14: "GFAERRSTS bit[14] SATA0_FA_STS : ",
                            15: "GFAERRSTS bit[15] SATA1_FA_STS : ", 16: "GFAERRSTS bit[16] SATA2_FA_STS : ", 17: "GFAERRSTS bit[17] USB_FA_STS : ",
                            18: "GFAERRSTS bit[18] LPC_FA_STS : ", 19: "GFAERRSTS bit[19] LSMBUS_FA_STS : ", 20: "GFAERRSTS bit[20] SPIESPI_FA_STS : ",
                            21: "GFAERRSTS bit[21] NPK_FA_STS : ", 22: "GFAERRSTS bit[22] HSUART_FA_STS : ", 23: "GFAERRSTS bit[23] GSMBUS_FA_STS : ",
    }

    GFAFERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GFAFERRSTS_REG_INFO = {0: "GFAFERRSTS bit[0] IEHLOCAL_FA_FERR : ", 1: "GFAFERRSTS bit[1] RP0_FA_FERR : ", 2: "GFAFERRSTS bit[2] RP1_FA_FERR : ",
                            3: "GFAFERRSTS bit[3] RP2_FA_FERR : ", 4: "GFAFERRSTS bit[4] RP3_FA_FERR : ", 5: "GFAFERRSTS bit[5] RP4_FA_FERR : ",
                            6: "GFAFERRSTS bit[6] RP5_FA_FERR : ", 7: "GFAFERRSTS bit[7] RP6_FA_FERR : ", 8: "GFAFERRSTS bit[8] RP7_FA_FERR : ",
                            9: "GFAFERRSTS bit[9] RP8_FA_FERR : ", 10: "GFAFERRSTS bit[10] RP9_FA_FERR : ", 11: "GFAFERRSTS bit[11] RP10_FA_FERR : ",
                            12: "GFAFERRSTS bit[12] RP11_FA_FERR : ", 13: "GFAFERRSTS bit[13] VRP_FA_FERR : ", 14: "GFAFERRSTS bit[14] SATA0_FA_FERR : ",
                            15: "GFAFERRSTS bit[15] SATA1_FA_FERR : ", 16: "GFAFERRSTS bit[16] SATA2_FA_FERR : ", 17: "GFAFERRSTS bit[17] USB_FA_FERR : ",
                            18: "GFAFERRSTS bit[18] LPC_FA_FERR : ", 19: "GFAFERRSTS bit[19] LSMBUS_FA_FERR : ", 20: "GFAFERRSTS bit[20] SPIESPI_FA_FERR : ",
                            21: "GFAFERRSTS bit[21] NPK_FA_FERR : ", 22: "GFAFERRSTS bit[22] HSUART_FA_FERR : ", 23: "GFAFERRSTS bit[23] GSMBUS_FA_FERR : ",
    }

    GFANERRSTS_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12,
                        13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23}
    GFANERRSTS_REG_INFO = {0: "GFANERRSTS bit[0] IEHLOCAL_FA_NERR : ", 1: "GFANERRSTS bit[1] RP0_FA_NERR : ", 2: "GFANERRSTS bit[2] RP1_FA_NERR : ",
                            3: "GFANERRSTS bit[3] RP2_FA_NERR : ", 4: "GFANERRSTS bit[4] RP3_FA_NERR : ", 5: "GFANERRSTS bit[5] RP4_FA_NERR : ",
                            6: "GFANERRSTS bit[6] RP5_FA_NERR : ", 7: "GFANERRSTS bit[7] RP6_FA_NERR : ", 8: "GFANERRSTS bit[8] RP7_FA_NERR : ",
                            9: "GFANERRSTS bit[9] RP8_FA_NERR : ", 10: "GFANERRSTS bit[10] RP9_FA_NERR : ", 11: "GFANERRSTS bit[11] RP10_FA_NERR : ",
                            12: "GFANERRSTS bit[12] RP11_FA_NERR : ", 13: "GFANERRSTS bit[13] VRP_FA_NERR : ", 14: "GFANERRSTS bit[14] SATA0_FA_NERR : ",
                            15: "GFANERRSTS bit[15] SATA1_FA_NERR : ", 16: "GFANERRSTS bit[16] SATA2_FA_NERR : ", 17: "GFANERRSTS bit[17] USB_FA_NERR : ",
                            18: "GFANERRSTS bit[18] LPC_FA_NERR : ", 19: "GFANERRSTS bit[19] LSMBUS_FA_NERR : ", 20: "GFANERRSTS bit[20] SPIESPI_FA_NERR : ",
                            21: "GFANERRSTS bit[21] NPK_FA_NERR : ", 22: "GFANERRSTS bit[22] HSUART_FA_NERR : ", 23: "GFANERRSTS bit[23] GSMBUS_FA_NERR : ",
    }
    #解析相应的接口标志
    dict_dev_bit_value = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0,
                        13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0}

    output = ""
    try:
        for key in list_key_name:
            if key in value:
                for reg in dict_reg_addr:
                    print_flag = 0
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = dict_reg_addr[reg] - 0x200
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    output_tmp = "%s%s(0x%x) : %s : " % (key, reg, dict_reg_addr[reg], joint_addr(reg_value[0:4]))
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info), dict_dev_bit_value)
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
        if len(output) > 0:
            output  = "Pch block global handler : " + output + "\n"
        output = output + parse_peci_pch_dev_D1734(dict_dev_bit_value, value)
    except Exception as e:
        output = output + "Parse smbus ctl failed: %s" % str(e)
        print(output)
    return output

def parse_peci_pcu_D1734(value):
    list_key_name = { "B31D30F4Addr84", "B31D30F4Addrf0", "B30D0F0Addrd8"}
    dict_reg_addr = { "VIRAL_CONTROL_CFG": 0x84, "EMCA_EN_CORE_IERR_TO_MSMI_CFG": 0xd8, "PCU_FIRST_IERR_TSC_LO_CFG": 0xf0, "PCU_FIRST_IERR_TSC_HI_CFG": 0xf4,
                    "PCU_FIRST_MCERR_TSC_LO_CFG": 0xf8, "PCU_FIRST_MCERR_TSC_HI_CFG": 0xfc
    }

    VIRAL_CONTROL_CFG_BIT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 8: 8, 9: 9, 10: 10}
    VIRAL_CONTROL_CFG_REG_INFO = {0: "VIRAL_CONTROL_CFG bits[0] VIRAL_RESET: ", 1: "VIRAL_CONTROL_CFG bits[1] VIRAL_FAST_PIN_DIS: ",
                                    2: "VIRAL_CONTROL_CFG bits[2] EMCA_MODE: ", 3: "VIRAL_CONTROL_CFG bits[3] VIRAL_LOG_DISABLE: ",
                                    4: "VIRAL_CONTROL_CFG bits[4] VIRAL_LOG: ", 8: "VIRAL_CONTROL_CFG bits[8] EN_PCU_HW_ERROR: ",
                                    9: "VIRAL_CONTROL_CFG bits[9] EN_PCU_UC_ERROR: ", 10: "VIRAL_CONTROL_CFG bits[10] EN_PCU_FW_ERROR: "
    }

    EMCA_EN_CORE_IERR_TO_MSMI_CFG_BIT = {0: 0}
    EMCA_EN_CORE_IERR_TO_MSMI_CFG_REG_INFO = {0: "EMCA_EN_CORE_IERR_TO_MSMI_CFG bit[0] ENCOREIERRTOMSMI : "}

    PCU_FIRST_IERR_TSC_LO_CFG_BIT = {0:31}
    PCU_FIRST_IERR_TSC_LO_CFG_REG_INFO = {0: "PCU_FIRST_IERR_TSC_LO_CFG bits[0:31] Low 4B of TSC snapshot taken on first internal IERR: "}

    PCU_FIRST_IERR_TSC_HI_CFG_BIT = {0:31}
    PCU_FIRST_IERR_TSC_HI_CFG_REG_INFO = {0: "PCU_FIRST_IERR_TSC_HI_CFG bits[0:31] High 4B of TSC snapshot taken on first internal IERR: "}

    PCU_FIRST_MCERR_TSC_LO_CFG_BIT = {0:31}
    PCU_FIRST_MCERR_TSC_LO_CFG_REG_INFO = {0: "PCU_FIRST_MCERR_TSC_LO_CFG bits[0:31] Low 4B of TSC snapshot taken on first internal MCERR: "}

    PCU_FIRST_MCERR_TSC_HI_CFG_BIT = {0:31}
    PCU_FIRST_MCERR_TSC_HI_CFG_REG_INFO = {0: "PCU_FIRST_MCERR_TSC_HI_CFG bits[0:31] High 4B of TSC snapshot taken on first internal MCERR: "}

    output = ""
    try:
        for key in list_key_name:
            print_flag = 0
            if key in value:
                output_tmp = "%s : " % key
                for reg in dict_reg_addr:
                    dict_bit = reg + "_BIT"
                    dict_reg_info = reg + "_REG_INFO"
                    beg_addr = 0
                    if re.search("Addrf0",key) :
                        if dict_reg_addr[reg] < 0xf0:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0xf0
                    elif re.search("Addrd8",key) :
                        if dict_reg_addr[reg] < 0xd8:
                            continue
                        beg_addr = dict_reg_addr[reg] - 0xd8
                    elif re.search("Addr84",key) :
                        if dict_reg_addr[reg] < 0x84 :
                            continue
                        beg_addr = dict_reg_addr[reg] - 0x84
                    else:
                        continue
                    end_addr = beg_addr + 3
                    reg_value = get_peci_reg_value(value, key, beg_addr, end_addr)
                    ret_value = hex_to_bin_bit(reg_value[0:4], key)
                    for beg_bit in locals().get(dict_bit):
                        ret, ret_output = get_reg_bit_value(ret_value, beg_bit, locals().get(dict_bit)[beg_bit], locals().get(dict_reg_info))
                        if ret_output not in output_tmp:
                            output_tmp = output_tmp + ret_output
                        if ret:
                            print_flag = 1
                    if print_flag :
                        output = output + output_tmp
                        output_tmp = ""
    except Exception as e:
        output = output + "Parse pcu failed: %s" % str(e)
        print(output)
    return output

# PECI: parse pec
# i err type--(correctable error, non-fatal error, fatal error)
def parse_peci_D1734(value):
    # value = 1, need to parse Memory Controller Error Status
    try:
        ret = 0
        output = ""
        #解析GCOERRSTS、DEVFUNC等具体出错信息
        output = parse_peci_err_type_D1734(value)
        #解析IEH local部分
        ieh_reg_dict = {"B0D0F4Addr280", "B1D0F4Addr280", "B2D0F4Addr280", "B30D0F3Addr280"}
        output = output + parse_peci_pch_ieh_D1734(value, ieh_reg_dict)
        #解析peci4.0
        output = output + parse_peci_4_D1734(value)
        #解析VT-d部分
        output = output + parse_peci_vt_d_D1734(value)
        #解析 Mesh 2 PCIe部分：
        output = output + parse_peci_mesh_D1734(value)
        #解析 RAS部分
        output = output + parse_peci_ras_D1734(value)
        #解析 CBDMA部分
        output = output + parse_peci_cbdma_D1734(value)
        #解析 MSM部分
        output = output + parse_peci_msm_D1734(value)
        #解析 PMON MSM部分
        output = output + parse_peci_pmon_msm_D1734(value)
        #解析 Trace Hub部分
        output = output + parse_peci_trace_hub_D1734(value)
        #解析 内存部分
        output = output + parse_peci_mem_D1734(value)
        #解析 PCH ERR
        output = output + parse_peci_pch_err_D1734(value)
        #解析B31.D30.F4 0x84，0XF0~0XFC（PCU相关）以及EMCA等具体出错信息，新增部分不解析
        #output = output + parse_peci_pcu_D1734(value)
        if (output != None) and len(output) > 0:
            ret = 1
            print(output)
        if ret == 0:
            print("No abnormality")
            return
    except Exception as e:
        output = "Parse peci err failed: %s" % str(e)
        print(output)

def get_peci_reg_value(data, name, beg_addr, end_addr):
    try:
        list_value = ["0"] * 32
        num = 0
        if (name in data) and (len(data[name]) >= (end_addr*3+2)):
            for index in range(beg_addr, end_addr + 1):
                list_value[num] = data[name][index*3:index*3+2]
                num = num + 1
        return list_value
    except Exception as e:
        output = "Parse reg value failed: %s" % str(e)
        print(output)

