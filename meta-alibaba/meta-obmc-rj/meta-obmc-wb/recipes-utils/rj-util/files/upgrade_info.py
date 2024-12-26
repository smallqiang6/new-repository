#!/usr/bin/env python
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import sys
import os
import json
import subprocess

value = os.path.isdir('/var/log/fw')
if value == False:
    os.mkdir('/var/log/fw')

last_upgrade_result = '/var/log/fw/upgrade_info.json' 
bmc_upgrade_info = [
{ 'FwType':'bmc', 'FwPath':'', 'FwExtra':'', 'Result':'NOT_PERFORMED' }
]
bios_upgrade_info = [
{ 'FwType':'bios', 'FwPath':'', 'FwExtra':'', 'Result':'NOT_PERFORMED' }
]
as13_32h_upgrade_info = [
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_all_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_1_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_2_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_3_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_4_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_1_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_2_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_3_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_4_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_1_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_2_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_3_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-32h_cpld_4_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_bin', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'bios', 'FwPath':'', 'FwExtra':'bios_transfr_bmc', 'Result':'NOT_PERFORMED'}
]

as13_48f8h_upgrade_info = [
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_all_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_1_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_2_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_3_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_4_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_1_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_2_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_3_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_4_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_1_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_2_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_3_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as13-48f8h_cpld_4_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_bin', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'bios', 'FwPath':'', 'FwExtra':'bios_transfr_bmc', 'Result':'NOT_PERFORMED'}
]
as23_128h_upgrade_info = [
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_all_main_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_all_sub_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_main_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_main_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_3_main_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_sub_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_sub_cpu', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_main_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_main_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_3_main_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_sub_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_sub_cpu_pwr', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_bin', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_transfr_main_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_transfr_main_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_3_transfr_main_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_1_transfr_sub_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'cpld', 'FwPath':'', 'FwExtra':'as23-128h_cpld_2_transfr_sub_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'fpga', 'FwPath':'', 'FwExtra':'fpga_transfr_bmc', 'Result':'NOT_PERFORMED'},
{ 'FwType':'bios', 'FwPath':'', 'FwExtra':'bios_transfr_bmc', 'Result':'NOT_PERFORMED'}
]

def create_default_upgrade_info(fwtype):
    result = []
    if fwtype == "bmc":
        result = bmc_upgrade_info
    elif fwtype == "bios":
        result = bios_upgrade_info
    elif fwtype == "cpld" or fwtype == "fpga":
        ret, log = subprocess.getstatusoutput(" cat /etc/device/productname")
        if "can't open" in log:
            exit(-1)
        if log == "AS23-128H":
            result = as23_128h_upgrade_info
        elif log == "AS13-48F8H":
            result = as13_48f8h_upgrade_info
        elif log == "AS13-32H":
            result = as13_32h_upgrade_info
        else:
            exit(-1)
    else:
        exit(-1)
    with open(last_upgrade_result, 'w') as f:
        f.write(json.dumps(result,indent=4))
        f.flush()
        os.fsync(f)

def clear_upgrade_info():
    result = []
    with open(last_upgrade_result, 'w') as f:
        f.write(json.dumps(result,indent=4))
        f.flush()
        os.fsync(f)

def set_cpld_upgrade_path(fwextra, fwpath):
    with open(last_upgrade_result, 'r') as f:
        load_dict = json.load(f)
        for each in load_dict:
            if each["FwExtra"] == fwextra:
                each["FwPath"] = fwpath
                break
    with open(last_upgrade_result, "w") as f:
        f.write(json.dumps(load_dict,indent=4))
        f.flush()
        os.fsync(f)

def set_cpld_upgrade_result(fwextra, result):
    with open(last_upgrade_result, 'r') as f:
        load_dict = json.load(f)
        for each in load_dict:
            if each["FwExtra"] == fwextra:
                each["Result"] = result
                break
    with open(last_upgrade_result, "w") as f:
        f.write(json.dumps(load_dict,indent=4))
        f.flush()
        os.fsync(f)

def set_bios_or_bmc_upgrade_path(fwtype, fwextra, path):
    with open(last_upgrade_result, 'r') as f:
        load_dict = json.load(f)
        if load_dict[0]["FwType"] == fwtype:
            load_dict[0]["FwExtra"] = fwextra
            load_dict[0]["FwPath"] = path
        else:
            exit(-1)
    with open(last_upgrade_result, "w") as f:
        f.write(json.dumps(load_dict,indent=4))
        f.flush()
        os.fsync(f)

def set_bios_or_bmc_upgrade_result(fwtype, fwextra, result):
    with open(last_upgrade_result, 'r') as f:
        load_dict = json.load(f)
        if load_dict[0]["FwType"] == fwtype:
            load_dict[0]["FwExtra"] = fwextra
            load_dict[0]["Result"] = result
        else:
            exit(-1)
    with open(last_upgrade_result, "w") as f:
        f.write(json.dumps(load_dict,indent=4))
        f.flush()
        os.fsync(f)

def main(argv):
    param_num = len(sys.argv)
    param_str = sys.argv

    # upgrade_info.py clear
    if param_num == 2 and param_str[1] == "clear":
        clear_upgrade_info()

    # upgrade_info.py set cpld/bios/bmc default
    elif param_num == 4 and param_str[1] == "set" and param_str[3] == "default":
        create_default_upgrade_info(param_str[2])

    # upgrade_info.py set cpld/bios/bmc extra -p path
    elif param_num == 6 and param_str[4] == "-p":
        try:
            if param_str[2] == "cpld" or param_str[2] == "fpga" or param_str[2] == "bios_refresh":
                set_cpld_upgrade_path(param_str[3], param_str[5])
            else:
                set_bios_or_bmc_upgrade_path(param_str[2], param_str[3], param_str[5])
        except:
            print (last_upgrade_result + " does empty")
            exit(-1)
        else:
            print ("set " + last_upgrade_result + " success")

    # upgrade_info.py set cpld/bios/bmc extra -r result
    elif param_num == 6 and param_str[4] == "-r":
        try:
            if param_str[2] == "cpld" or param_str[2] == "fpga" or param_str[2] == "bios_refresh":
                set_cpld_upgrade_result(param_str[3], param_str[5])
            else:
                set_bios_or_bmc_upgrade_result(param_str[2], param_str[3], param_str[5])
        except:
            print (last_upgrade_result + " does empty")
            exit(-1)
        else:
            print ("set " + last_upgrade_result + " success")
    else:
        print ("parameter error")
        exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])

