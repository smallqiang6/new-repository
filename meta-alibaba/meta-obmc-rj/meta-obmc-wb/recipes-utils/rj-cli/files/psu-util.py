#!/usr/bin/env python
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import operator
import ctypes
import subprocess
import time

try:
    from plat_utils.plat_common_util import *
    from plat_hal.interface import interface
    from plat_hal.psu import psu
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

psu_info = [
    {
        "productPartModelName": "GW-CRPS2000DWA",
        "page": 15
    },
    {
        "productPartModelName": "DPST-2030AB D",
        "page": 15
    },
    {
        "productPartModelName": "AP-CA2000F12B1",
        "page": 15
    }
]

def usage():
    print("usage:")
    print("    psu-util.py psu[x] get_blackbox_info option")
    exit()

def command(cmdstr):
    retcode, output = subprocess.getstatusoutput(cmdstr)
    return retcode, output

def i2ctransfer_i2ctool(bus, addr, offset, read):
    command_line = "i2ctransfer -f -y %d w1@0x%02x 0x%02x r%d" % (bus, addr, offset, read)
    retrytime = 6
    ret_t = ""
    for i in range(retrytime):
        ret, ret_t = command(command_line)
        if ret == 0:
            return True, ret_t
        time.sleep(0.1)
    return False, ret_t

def psu_get_fw_ver(bus, addr):
    ret, pri_fw_ver = i2ctransfer_i2ctool(bus, addr, 0xd5, 8)
    ver = pri_fw_ver.split()
    for j in range(len(ver)):
        ver[j] = int(ver[j], 16)
        ver[j] = chr(ver[j])
    fw_ver_str = ''.join(ver)
    return fw_ver_str

def psu_get_mfr_pos(bus, addr, offset):
    ret, reg = i2ctransfer_i2ctool(bus, addr, offset, 4)
    pos = reg.split()
    mfr_pos = 0
    for i in range(len(pos)):
        pos[i] = int(pos[i], 16)
        mfr_pos |= pos[i] << (8 * i)
    return mfr_pos

def psu_change_blackbox_page(psu, page):
    bus = psu.pmbus.get('bus')
    addr = psu.pmbus.get("addr")
    psu.seti2c_byte_pec(bus, addr, 0xe4, page)

def linear11_to_double(data):
    sign_y = (data >> 10) & 0x1
    sign_n = (data >> 15) & 0x1

    y = -1 * ((~data & 0x3ff) + 1) if (sign_y == True) else data & 0x3ff
    n = -1 * ((~(data >> 11) & 0xf) + 1) if (sign_n == True) else (data >> 11) & 0xf
    x = float(y) * pow(2, n)

    return x

def linear16_to_double(data):
    y = data
    x = float(y) * pow(2, -9)

    return x

def print_psu_blackbox(psu, total_page):
    psu_bus = psu.pmbus.get('bus')
    psu_addr = psu.pmbus.get("addr")

    pri_fw_ver = psu_get_fw_ver(psu_bus, psu_addr)

    for i in range(total_page):
        psu_change_blackbox_page(psu, i)

        ret, status_word = psu.get_i2cword(psu_bus, psu_addr, 0x79)
        ret, status_vout = psu.get_i2c(psu_bus, psu_addr, 0x7a)
        ret, status_iout = psu.get_i2c(psu_bus, psu_addr, 0x7b)
        ret, status_input = psu.get_i2c(psu_bus, psu_addr, 0x7c)
        ret, status_temp = psu.get_i2c(psu_bus, psu_addr, 0x7d)
        ret, status_cml = psu.get_i2c(psu_bus, psu_addr, 0x7e)
        ret, status_mfr_spec = psu.get_i2c(psu_bus, psu_addr, 0x80)
        ret, status_fan = psu.get_i2c(psu_bus, psu_addr, 0x81)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x88)
        read_vin = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x89)
        read_iin = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8a)
        read_vacp = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8b)
        read_vout = linear16_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8c)
        read_iout = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8d)
        read_temp_1 = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8e)
        read_temp_2 = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x8f)
        read_temp_3 = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x90)
        read_fan_speed_1 = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x96)
        read_pout = linear11_to_double(reg)
        ret, reg = psu.get_i2cword(psu_bus, psu_addr, 0x97)
        read_pin = linear11_to_double(reg)
        mfr_pos_total = psu_get_mfr_pos(psu_bus, psu_addr, 0xe5)
        mfr_pos_last = psu_get_mfr_pos(psu_bus, psu_addr, 0xe6)

        print("Blackbox Information         : %s (Bus:%d Addr:%x)" %(psu.name, psu_bus, psu_addr))
        print("--------------------         : -------------------")
        print("PAGE                         : 0x%02X             " %(i))
        print("PRI_FW_VER            (0xD5) : %s" %(pri_fw_ver))
        print("STATUS_WORD           (0x79) : 0x%04x" %(status_word))
        print("STATUS_VOUT           (0x7A) : 0x%02x" %(status_vout))
        print("STATUS_IOUT           (0x7B) : 0x%02x" %(status_iout))
        print("STATUS_INPUT          (0x7C) : 0x%02x" %(status_input))
        print("STATUS_TEMP           (0x7D) : 0x%02x" %(status_temp))
        print("STATUS_CML            (0x7E) : 0x%02x" %(status_cml))
        print("STATUS_MFR_SPEC       (0x80) : 0x%04x" %(status_mfr_spec))
        print("STATUS_FAN            (0x81) : 0x%02x" %(status_fan))
        print("READ_VIN              (0x88) : %.2f V" %(read_vin))
        print("READ_IIN              (0x89) : %.2f A" %(read_iin))
        print("READ_VCAP             (0x8A) : %.2f V" %(read_vacp))
        print("READ_VOUT             (0x8B) : %.2f V" %(read_vout))
        print("READ_IOUT             (0x8C) : %.2f A" %(read_iout))
        print("READ_TEMPERATURE_1    (0x8D) : %.2f C" %(read_temp_1))
        print("READ_TEMPERATURE_2    (0x8E) : %.2f C" %(read_temp_2))
        print("READ_TEMPERATURE_3    (0x8F) : %.2f C" %(read_temp_3))
        print("READ_FAN SPEED_1      (0x90) : %.2f RPM" %(read_fan_speed_1))
        print("READ_POUT             (0x96) : %.2f W" %(read_pout))
        print("READ_PIN              (0x97) : %.2f W" %(read_pin))
        print("MFR_POS_TOTAL         (0xE5) : 0x%08X Sec" %(mfr_pos_total))
        print("MFR_POS_LAST          (0xE6) : 0x%08X Sec" %(mfr_pos_last))
        print()
    psu_change_blackbox_page(psu, 0xff)

if __name__ == "__main__":
    platutil = PlatCommonUtil()
    int_case = interface()
    psu_total_number = int_case.get_psu_total_number()
    try:
        args = platutil.Argparser(['psu_num', 'type', 'option'],
                              [int, str, str],
                              ['Number : psu_num',
                               'Type : blackbox_info',
                               'Options : print|clear'],
                              [False, False, False])
        if args.psu_num > 0 and args.psu_num <= psu_total_number:
            psu = int_case.chas.psu_list[args.psu_num - 1]
            psu.get_fru_info()

            if psu.present == False:
                print("PSU%d is not present!\n", args.psu_num);
                exit()
            for i in range(len((psu_info))):
                psu_pn = psu_info[i].get("productPartModelName", "")
                if psu_pn == psu.productPartModelName:
                    total_page = psu_info[i].get("page", "")
                    break
            if args.option == "print":
                print_psu_blackbox(psu, total_page)
            elif args.option == "clear":
                print("clear blackbox info")
                psu.seti2cword(psu.pmbus.get('bus'), psu.pmbus.get('addr'), 0xe7, 0x00)
            else:
                print("option error")
        else:
            print("psu number error, total number %d" %(psu_total_number))
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
