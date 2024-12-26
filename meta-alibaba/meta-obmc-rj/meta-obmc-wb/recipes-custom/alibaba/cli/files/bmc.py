#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_bmc import HalBmc
from hal.hal_misc import HalMisc
from plat_hal.interface import interface

def usage():
    print("usage:")
    print("    bmc.py get [info|status|next-boot|boot-status|version|system-airflow|reset-num]")
    print("    bmc.py set next-boot [master|slave]")
    print("    bmc.py reboot")
    exit()

if __name__ == "__main__":
    """
    bmc.py get or set bmc version or status or flash or reset-num
    """
    try:
        platutil = PlatCommonUtil()
        hal_bmc = HalBmc()
        hal_misc = HalMisc()
        plat_interface = interface()
        args = platutil.Argparser(['option', 'nextpara', 'flash'],
                              [str, str, str],
                              ['Action: get|set|reboot',
                               'Next paramter','master | slave'],
                              [False, True, True])
        if args.option == "get":
            if args.nextpara == "info":
                print(repr(hal_bmc.get_info()))
            elif args.nextpara == "version":
                print(repr(hal_bmc.get_version_all()))
            elif args.nextpara == "next-boot":
                print(repr(hal_bmc.get_next_boot()))
            elif args.nextpara == "system-airflow":
                print(repr(hal_misc.get_system_airflow()))
            elif args.nextpara == "status":
                #print(repr(hal_bmc.get_status()))
                dict_info = hal_bmc.get_status()
                if dict_info == None :
                    print("hal_bmc.get_status() error")
                    exit()
                dict_info_keys = list(dict_info.keys())
                dict_info_keys.sort()
                for item in dict_info_keys:
                    print(item)
                    dict_info_sub = dict_info[item]
                    dict_info_sub_keys = list(dict_info_sub.keys())
                    dict_info_sub_keys.sort()
                    for it in dict_info_sub_keys:
                        print("%s :"%(it))
                        print("%s"%(dict_info_sub[it]))
                    print("\n")
            elif args.nextpara == "boot-status":
                print(repr(hal_misc.get_bmc_boot_status()))
            elif args.nextpara == "reset-num":
                print(repr(plat_interface.get_bmc_reset_num()))
            else:
                print("error param")
                usage()
        elif args.option == "reboot":
            str_input = input("Are you sure reboot bmc ? [y/n]:")
            if str_input.lower() == "y" or str_input.lower() == "yes" :
                print(repr(hal_bmc.reboot()))
        elif args.option == "set":
            if args.nextpara == "next-boot":
                if args.flash == "master" or args.flash == "slave":
                    print(repr(hal_bmc.set_next_boot(args.flash)))
                else:
                    print("error flash param")
                    usage()
            else:
                print("error next param")
                usage()
        else:
            print("error option")
            usage()
            
    except Exception as e:
        print("Error returned: " + str(e))
