#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_misc import HalMisc
from plat_hal.interface import interface
from plat_hal.chassisbase import chassisbase

def usage():
    print("usage:")
    print("    power.py cpu [on|off|cycle|reset|status]")
    print("    power.py port [on|off|status]")
    print("    power.py mac [on|off|status]")
    print("    power.py ssd [on|off|status]")
    print("    power.py [netcard1|netcard2] [on|off|status]")
    print("    power.py bmc-emmc cycle")
    print("    power.py cpu-emmc cycle")
    print("    power.py machine cycle")
    exit()

if __name__ == "__main__":
    """
    power.py control the status of cpu
    """
    try:
        platutil = PlatCommonUtil()
        hal_misc = HalMisc()
        plat_interface = interface()
        chas = chassisbase()
        cpu = chas.get_cpu_byname("cpu")
        fpga_fw = chas.get_fpga_fw_byname("fpga_fw")
        args = platutil.Argparser(['option', 'type'],
                              [str, str],
                              ['option:cpu|port|mac|ssd|machine|bmc-emmc|cpu-emmc|netcard1|netcard2',
                               'type:on|off|cycle|reset|status'],
                              [True, True])
        if fpga_fw.get_operate_capacity("getforcecontrolpowerstatus") == 1:
            getforcecontrolpowerstatus = 1
        else:
            getforcecontrolpowerstatus = 0
        if args.option == "cpu":
            if args.type == "on" or args.type == "off" or args.type == "cycle" or args.type == "reset":
                str_input = input("power %s cpu [y/n]:"%(args.type))
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    print(repr(hal_misc.set_host_cpu_power(args.type)))
            elif args.type == "status":
                print(repr(hal_misc.get_host_cpu_power_status()))
            else:
                print("error option")
                usage()
        elif args.option == "port":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("getportpowerstatus") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "on" or args.type == "off":
                str_input = input("power %s port [y/n]:"%(args.type))
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(1) != 0:
                            print("enable host cpu power force control failed")
                            exit()
                    print(repr(plat_interface.set_port_power(args.type)))
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(0) != 0:
                            print("diasble host cpu power force control failed")
                            exit()
            elif args.type == "status":
                print(repr(plat_interface.get_port_power_status()))
            else:
                print("error option")
                usage()
        elif args.option == "mac":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("gettd4powerstatus") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "on" or args.type == "off":
                str_input = input("power %s mac [y/n]:"%(args.type))
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(1) != 0:
                            print("enable host cpu power force control failed")
                            exit()
                    print(repr(plat_interface.set_td4_power(args.type)))
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(0) != 0:
                            print("diasble host cpu power force control failed")
                            exit()
            elif args.type == "status":
                print(repr(plat_interface.get_td4_power_status()))
            else:
                print("error option")
                usage()
        elif args.option == "ssd":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("getssdpowerstatus") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "on" or args.type == "off":
                str_input = input("power %s ssd [y/n]:"%(args.type))
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(1) != 0:
                            print("enable host cpu power force control failed")
                            exit()
                    print(repr(plat_interface.set_ssd_power(args.type)))
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(0) != 0:
                            print("diasble host cpu power force control failed")
                            exit()
            elif args.type == "status":
                print(repr(plat_interface.get_ssd_power_status()))
            else:
                print("error option")
                usage()
        elif args.option == "bmc-emmc":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("powerbmcemmc") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "cycle":
                str_input = input("power bmc-emmc cycle [y/n]:")
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    plat_interface.set_bmcemmc_power_cycle()
                    print("power cycle bmc emmc done")
            else:
                print("error option")
                usage()
        elif args.option == "cpu-emmc":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("powercpuemmc") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "cycle":
                str_input = input("power bmc-cpu cycle [y/n]:")
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    plat_interface.set_cpuemmc_power_cycle()
                    print("power cycle cpu emmc done")
            else:
                print("error option")
                usage()
        elif args.option == "machine":
            if args.type == "cycle":
                if cpu != None:
                    if cpu.machine_reset_reg == None :
                        print("This operation is not supported!")
                        exit()
                str_input = input("power machine cycle  [y/n]:")
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    print(repr(plat_interface.set_machine_power_cycle()))
            else:
                print("error option")
                usage()
        elif args.option == "netcard1" or args.option == "netcard2":
            if fpga_fw != None:
                if fpga_fw.get_operate_capacity("getnetcardpowerstatus") == 0:
                    print("This operation is not supported!")
                    exit()
            if args.type == "on" or args.type == "off":
                str_input = input("power %s %s [y/n]:"%(args.type, args.option))
                if str_input.lower() == "y" or str_input.lower() == "yes" :
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(1) != 0:
                            print("enable host cpu power force control failed")
                            exit()
                    print(repr(plat_interface.set_netcard_power(args.option, args.type)))
                    if getforcecontrolpowerstatus == 1:
                        if plat_interface.enable_host_cpu_power_force_control(0) != 0:
                            print("diasble host cpu power force control failed")
                            exit()
            elif args.type == "status":
                print(repr(plat_interface.get_netcard_power_status(args.option)))
            else:
                print("error option")
                usage()
        else:
            print("error option")
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
