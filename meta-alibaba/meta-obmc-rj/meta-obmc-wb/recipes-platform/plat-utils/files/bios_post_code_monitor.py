#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

import subprocess
import time
import os
from plat_hal.baseutil import baseutil

IDENTIFIER = "BIOS_PARSE: "
AST_FUNC_SOURCE = "/usr/local/bin/ast-functions"
AST_FUNC_CALL = "ast_product_func_call"
POST_MODE_FUNC = "get_post_mode"
POST_PARSE_MODE_CMD = f"{AST_FUNC_SOURCE} {AST_FUNC_CALL} {POST_MODE_FUNC}"
POST_DEV_PATH = "/dev/aspeed-lpc-snoop2"

# 0: 1 Byte mode/1: 2 Byte mode/2: 4 Byte mode/3: Full mode
POST_SGL_MODE = 0
POST_DBL_MODE = 1
POST_CACHE_MAX_LEN = 2048
POST_PARSE_MODE = POST_SGL_MODE
POST_80_FLAG = "f5"
POST_81_FLAG = "f6"
POST_NULL_CODE = '00'
POST_NULL_CODE_LIST = ['00', POST_80_FLAG, '00', POST_80_FLAG]

g_double_mode_skip_codelist = ["50"]
g_parsed_lib = {
    "undecode": {
        '72': "System sleep down",
        '00': "Pch Init PrePolicy – Start",
        '01': "Power on post code",
        '02': "Load Processor Microcode / PSF early init",
        '03': "Initial cache as memory",
        '04': "Enable cache as memory",
        '05': "Init MMCFG and BUS Number",
        '06': "CPU init done in SEC phase",
        '7f': "Pch Init PrePolicy – End",
        '84': "Call xHCI device to switch USB ports",
        'aa': "Interrupt controller mode – APIC",
        'e3': "Native Hot plug control granted",
    },
    "ami_standard": {
        '0c': "Reserved for future AMI SEC error codes",
        '0d': "Reserved for future AMI SEC error codes",
        '0e': "Microcode not found",
        '0f': "Microcode not found",
        '50': "Memory initialization error.Invalid memory type or incompatible memory speed",
        '51': "Memory initialization error.SPD reading has failed",
        '52': "Memory initialization error.Invalid memory size or memory modules do not match",
        '53': "Memory initialization error.No usable memory detected",
        '54': "Unspecified memory initialization error",
        '55': "Memory not installed",
        '56': "Invalid CPU type or Speed",
        '57': "CPU mismatch",
        '58': "CPU self test failed or possible CPU cache error",
        '59': "CPU micro-code is not found or micro-code update is failed",
        '5a': "Internal CPU error",
        '5b': "reset PPI is  not available 0x5C PEI phase BMC self-test failure",
        '5c': "Reserved for future AMI error code",
        '5d': "Reserved for future AMI error code",
        '5e': "Reserved for future AMI error code",
        '5f': "Reserved for future AMI error code",
        'e8': "S3 Resume Failed",
        'e9': "S3 Resume PPI not Found",
        'ea': "S3 Resume Boot Script Error",
        'eb': "S3 OS Wake Error",
        'ec': "Reserved for future AMI error codes",
        'ed': "Reserved for future AMI error codes",
        'ee': "Reserved for future AMI error codes",
        'ef': "Reserved for future AMI error codes",
        'f8': "Recovery PPI is not available",
        'f9': "Recovery capsule is not found",
        'fa': "Invalid recovery capsule",
        'fb': "Reserved for future AMI error codes",
        'fc': "Reserved for future AMI error codes",
        'fd': "Reserved for future AMI error codes",
        'fe': "Reserved for future AMI error codes",
        'ff': "Reserved for future AMI error codes",
        'd0': "CPU initialization error",
        'd1': "North Bridge initialization error",
        'd2': "South Bridge initialization error",
        'd3': "Some of the Architectural Protocols are not available",
        'd4': "PCI resource allocation error.Out of Resources",
        'd5': "No Space for Legacy Option ROM",
        'd6': "No Console Output Devices are found",
        'd7': "No Console Input Devices are found",
        'd8': "Invalid password",
        'd9': "Error loading Boot Option (LoadImage returned error)",
        'da': "Boot Option is failed (StartImage returned error)",
        'db': "Flash update is failed",
        'dc': "Reset protocol is not available",
        'dd': "DXE phase BMC self-test failure",
    },
    "intel_standard": {
        '0100': "Power on post code",
        '0200': "Load Processor Microcode",
        '0300': "Initial cache as memory",
        '0400': "Enable cache as memory",
        '0500': "Init MMCFG and BUS Number",
        '0600': "CPU init done in SEC phase",
        'a100': "KTI - Collecting Early System Information",
        'a901': "KTI - Allocate CPU resource",
        'aa01': "KTI - Programming Credits",
        'a904': "KTI - Program early IO SAD setting",
        'a902': "KTI - Setup all IO SAD and address map for all sockets",
        'a8ff': "KTI - Program Optimum Route Table Settings",
        'aa02': "KTI - Program Misc. KTI Parameters",
        'ae00': "KTI - Coherency Settings",
        'af00': "KTI is done",
        'cd00': "MRC - Initialize memory structure",
        'b000': "MRC - Detect DIMM Configuration",
        'b004': "MRC - Waiting for Mailbox ready",
        'c100': "MRC - Check POR Compatibility",
        'b100': "MRC - Initialize clocks for all Memory",
        'c200': "MRC - Unlock Memory",
        'c300': "MRC - Check Reset requirement",
        'c400': "MRC - Check and Configure XMP",
        'b104': "MRC - Set Vdd",
        'b400': "MRC - Check DIMM Ranks",
        'b801': "MRC - Initialize Throttling Early",
        'c500': "MRC - Initialize Memory",
        'b200': "MRC - Gather SPD Data",
        'c601': "MRC - Print socket DIMM Information",
        'c701': "MRC - Prepare NVDIMM for training",
        'b300': "MRC - Early Configuration",
        'b302': "MRC - Disable clock for all rank",
        'b601': "MRC - DDRIO early Initialization",
        'b602': "MRC - DDRIO late Initialization",
        'b779': "MRC - Rcomp state training",
        'b609': "MRC - Enable Clock for all rank",
        'b70a': "MRC - Perform crossover calibration",
        'b72c': "MRC - Set starting/initial values for clock and control signals",
        'b72d': "MRC - by pass starting/initial values for clock and control signals",
        'b604': "MRC - Reset All DDR channels",
        'b605': "MRC - JEDEC Init",
        'b60b': "MRC - Sense Amp Offset training",
        'b701': "MRC - Early Command and Clock training, Receive enable, Write Leveling",
        'b606': "MRC - Update TxVref cached values",
        'b7ff': "MRC - DDR training started",
        'b778': "MRC - Pre Training Initial",
        'b71a': "MRC - Early control / clock training",
        'b70c': "MRC - Early command/ clock training",
        'b73b': "MRC - RCD QxCA Training",
        'b700': "MRC - Receive Enable",
        'b703': "MRC - Rx DQ/DQs basic per bit",
        'b725': "MRC - DQ Swizzle Discovery",
        'b701': "MRC - Write leveling training",
        'b702': "MRC - Write leveling cleanup- Center Tx DQS/ CLK timing",
        'b704': "MRC - TX DQ/DQs basic per bit",
        'b73e': "MRC - x16 DQs Swizzle Discovery",
        'b740': "MRC - Post Package Repair flow",
        'b731': "MRC - Read early Vref centering",
        'b732': "MRC - Write early Vref centering",
        'b770': "MRC - Training Command Tx EQ",
        'b724': "MRC - Command Vref centering",
        'b705': "MRC - late Command/Clock training",
        'b726': "MRC - Early Read ID training",
        'b76a': "MRC - Optimizes MC ODT by margining Rx eye width and height",
        'b76c': "MRC - Optimizes DRAM derive strength by margining Rx eye width and high",
        'b768': "MRC - Optimizes MC RON by margining TX eye width and height",
        'b764': "MRC - Training DRAM Rx EQ",
        'b765': "MRC - Optimizes TxEQ by margining TX DQ eye width and height",
        'b766': "MRC - Optimizes Tx IMODE by margining Tx DQ eye width and height",
        'b767': "MRC - Optimizes RX CTLE settings by margining Rx Dqs eye width and height",
        'b76f': "MRC - Optimizes TX rise and fall slew rates by margining Tx DQ eye width and height",
        'b76e': "MRC - Optimizes TX TCO by margining Tx DQ eye width and height",
        'b70e': "MRC - Tx Per Bit Deskew Training",
        'b70d': "MRC - Rx Per Bit Deskew Training",
        'b709': "MRC - Write Vref Re-center",
        'b708': "MRC - Read Vref Re-center",
        'b707': "MRC - Re-center Tx DQ timing",
        'b706': "MRC - Re-center Rx DQ timing",
        'b77c': "MRC - verify if the bit swizzling used for Rx and Tx is correct",
        'b73c': "MRC - TX Phase-based Xtalk Cancellation (PXC) algorithm",
        'b771': "MRC - TX Data Dependent Jitter Cancellation (DDJC) algorithm",
        'b772': "MRC - Optimizes Rx DFE settings by margining Rx Dqs eye width and height",
        'b713': "MRC - Optimizes round trip latency",
        'b77a': "MRC - Display Training result",
        'b77b': "MRC - Post-Training Initialization",
        'b710': "MRC - Rank Margin Tool start",
        'be01': "MRC - BIOS SSA Initialization",
        'be02': "MRC - Initialize SSA API",
        'd200': "MRC - Start Memory health test",
        'd600': "MRC - provide offset training result",
        'c702': "MRC - Restore NVDIMM",
        'c703': "MRC - Core arm NVDIMMs",
        'b711': "MRC - DDR training End",
        'b802': "MRC - Initialize Throttling",
        'b900': "MRC - Advanced MemTest",
        'b901': "MRC - Advanced Memtest step1",
        'b902': "MRC - Advanced Memtest step2",
        'b903': "MRC - Advanced Memtest step3",
        'c900': "MRC - Setup SVL and Scrambling",
        'ba00': "MRC - MemInit",
        'b901': "MRC - Advanced Mem test- step1",
        'cb00': "MRC - Check RAS support",
        'bb00': "MRC - Initialize memory map",
        'ca00': "MRC - Initialize CMI Credit Programming",
        'ca01': "MRC - CMI done",
        'b712': "MRC - Switch Normal Mode",
        'd300': "MRC - Enable 2N mode",
        'cc00': "MRC - Initialize ADR",
        'bc00': "MRC - Set RAS configuration",
        'ce00': "MRC - Programming required late in the memory initialization process",
        'c602': "MRC - DIMM info after MRC",
        'bf00': "MRC - done",
        'af01': "Uncore Mesh mode complete",
        'e600': "IIO late initialize entry",
        'e701': "IIO PCIE PORT initialize",
        'e908': "Intel Virtualization Technology (Intel VT) for Directed I/O (Intel VT-d) Chipset Initialization for IIO",
        'eb08': "R-Link Enable",
        'ed00': "Hide device in IIO",
        'ee00': "IIO late initialize exit",
        'd000': "PPM Initialize",
        'ef00': "IIO On ready to boot",
        '5700': "EFI shell",
    },
    "intel_non_standard": {
        '0b48': "Pch On Policy Installed – Start",
        '0b49': "Pch Pcie Bifurcation Init",
        '0b4a': "Perform DCI configuration Start",
        '0b4d': "Perform DCI configuration End",
        '0b15': "Pch Smbus Init",
        '0b52': "HPET Init",
        '0b55': "Pch On Policy Installed – End",
        '0b00': "PCH Init – Start",
        '0e22': "ME-BIOS0b: MBP Exit - Success",
        '0b04': "XHCI Usb2 AFE Programming",
        '0b05': "XHCI Usb3 HSIO Tuning",
        '0b06': "Configure XHCI",
        '0b0a': "Configure R-Link (DMI Mode)",
        '0b0b': "Configure P2SB",
        '0b0c': "Configure IOAPIC",
        '0b0d': "Configure interrupts",
        '0b13': "Configure SCS devices",
        '0b15': "Configure SMBUS",
        '0b7f': "PCH Init - END",
        '0b40': "Pch On End Of Pei after memory PEI module – Start",
        '0b41': "Init Thermal Device",
        '0b42': "Init Memory Throttling",
        '0b47': "Pch On End Of Pei after memory PEI module – End",
    },
}

def logger_debug(msg):
    baseutil.logger_debug(IDENTIFIER + msg)

def get_bios_parese_mode(cmd):
    global POST_PARSE_MODE
    ret, mode_log = subprocess.getstatusoutput(cmd)
    if ret in range(0, 4):
        POST_PARSE_MODE = ret
    else:
        logger_debug("failed to get postcode mode(%d, %s)" % (ret, mode_log))
        # default: 1 byte mode
        POST_PARSE_MODE = POST_SGL_MODE

def is_list_consistency(list, value):
    for elt in list:
        if elt != value:
            return False
    return True

def record_bios_post_code(data_list, data_len = None):
    if data_len is None:
        data_len = len(data_list)
    if data_len == 0:
        return
    if is_list_consistency(data_list, POST_NULL_CODE):
        return
    ami_lib = g_parsed_lib["ami_standard"]
    output = "BIOS POST CODE:"
    idx = 0
    try:
        for count in range(0, data_len):
            if idx > data_len - 1:
                break
            if data_list[idx] == POST_NULL_CODE and  idx + 1 < data_len and data_list[idx + 1] == POST_NULL_CODE:
                idx += 1
                continue
            key = data_list[idx]
            idx += 1
            if key not in ami_lib:
                output = output + "%s:" % key
            else:
                output = output + "%s(%s):" % (key, ami_lib[key])
        logger_debug("output %s" %(output))

    except Exception as e:
        logger_debug(str(e) + "record bios post code failed")

def record_bios_post_code_double_mode(data_list, data_len = None):
    output = "BIOS POST CODE:"
    POST_80_FLAG = "f5"
    POST_81_FLAG = "f6"
    idx = 0
    skip_meaningless_data = 0
    if data_len is None:
        data_len = len(data_list)
    if data_len == 0:
        return
    try:
        # remove port 80 identification
        tmp_list = [elt for elt in data_list if elt != POST_80_FLAG]
        if is_list_consistency(tmp_list, POST_NULL_CODE):
            return
        logger_debug("Original Code: %s" % (' '.join(data_list)))
        for count in range(0, data_len):
            # end of traversal
            if idx > data_len - 1:
                break
            # search for POST_80_FLAG
            if data_list[idx] != POST_80_FLAG:
                idx = idx + 1
                continue
            output_key = " "
            # the data to be parsed is double byte
            if idx + 2 < data_len and data_list[idx + 2] == POST_81_FLAG:
                # Compatible with single byte mode, the AMI code has only one byte
                # According to the current parsing library, there is no ambiguous parsing
                # key format: majorcode + minorcode
                if data_list[idx + 1] == POST_NULL_CODE:
                    idx_key = data_list[idx - 1]
                    output_key = data_list[idx + 1] + data_list[idx - 1]
                else:
                    idx_key = data_list[idx + 1] + data_list[idx - 1]
                # the next POST_80_FLAG
                idx = idx + 4
            # the data to be parsed is single byte
            else:
                # The meaningless data, POST_NULL_CODE_LIST, does not need to be parsed and can be discarded
                # when bios bootes successfully，a large number of duplicate data, POST_NULL_CODE_LIST, may appear in front of the data_list.
                # The actual data has not seen the case of "00 POST_80_FLAG 00 POST_80_FLAG bc POST_81_FLAG", that is,
                # although the combination of the first four bytes is meaningless,
                # the combination of the last four bytes is meaningful, which is not considered here.
                # In the actual boot process, we haven't seen "00 POST_80_FLAG 00 POST_80_FLAG" in the middle, and we don't consider it here.
                if idx + 2 < data_len and (data_list[idx - 1 : idx + 3] == POST_NULL_CODE_LIST):
                    skip_meaningless_data = 1
                    idx = idx + 2
                    continue
                idx_key = data_list[idx - 1]
                # Prevent parsing meaningless end data, "00POST_80_FLAG"
                if skip_meaningless_data == 1 and idx_key == POST_NULL_CODE:
                    idx = idx + 2
                    continue
                idx = idx + 2
            skip_meaningless_data = 0
            if output_key == " ":
                output_key = idx_key

            # The corresponding descriptions of some codes in the parsing library are not accurate for the double byte mode,
            # and need to be skipped
            if idx_key in g_double_mode_skip_codelist:
                output = output + "%s:" % output_key
                continue

            parsed = 0
            for subdict_key in g_parsed_lib.keys():
                if idx_key not in g_parsed_lib[subdict_key]:
                    continue
                else:
                    output = output + "%s(%s):" % (output_key, g_parsed_lib[subdict_key][idx_key])
                    parsed = 1
                    break
            if parsed == 0:
                output = output + "%s:" % output_key
        logger_debug("output %s" %(output))
    except Exception as e:
        logger_debug(str(e) + "record bios post code failed")

def read_postcode(device):
    lastest_cache = []
    lastest_len = 0

    try:
        fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as e:
        logger_debug("Failed to open device: %s" % str(e))
        return 0, lastest_cache

    try:
        while lastest_len < POST_CACHE_MAX_LEN:
            try:
                postcode = os.read(fd, 1)
                if not postcode:
                    break
                lastest_cache.append("%02x" % postcode[0])
                lastest_len += 1
            except BlockingIOError:
                break
    finally:
        os.close(fd)
    return lastest_len, lastest_cache

if __name__ == '__main__':
    logger_debug("start bios_post_code_monitor service")
    get_bios_parese_mode(POST_PARSE_MODE_CMD)
    logger_debug("bios post code parese mode: %d" % POST_PARSE_MODE)
    if not os.path.exists(POST_DEV_PATH):
        logger_debug("bios post code history file(%s) does not exist" % POST_DEV_PATH)
        exit(1)
    while True:
        data_list = []
        data_len = 0
        data_len, data_list = read_postcode(POST_DEV_PATH)
        if data_len == 0:
            time.sleep(2)
            continue
        if POST_PARSE_MODE == POST_DBL_MODE:
            record_bios_post_code_double_mode(data_list, data_len)
        else:
            record_bios_post_code(data_list, data_len)
        time.sleep(2)
