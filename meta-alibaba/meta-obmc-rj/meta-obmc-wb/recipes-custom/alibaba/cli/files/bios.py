#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_firmware import HalFirmware
from hal.hal_misc import HalMisc

def usage():
    print("usage:")
    print("    bios.py get {next-boot|boot-status}")
    print("    bios.py set {next-boot {master|slave}}")
    exit()

if __name__ == "__main__":
    """
    Commamd line interface with an input of a json file.
    """
    platutil = PlatCommonUtil()
    hal_firmware = HalFirmware()
    hal_misc = HalMisc()
    try:
        """
        bios.py get {next-boot|boot-status}
        bios.py set {next-boot {master|slave}}
        """
        args = platutil.Argparser(['option', 'nextpara', 'status'],
                              [str, str, str],
                              ['Action : get|set',
                               'next-boot','boot-status : master|slave'],
                              [False, True, True])
        if args.option == "get":
            if args.nextpara == "boot-status":
                print(repr(hal_misc.get_bios_boot_status()))
            elif args.nextpara == "next-boot":
                print(repr(hal_firmware.get_bios_next_boot()))
            else:
                usage()
        elif args.option == "set":
            if args.nextpara == "next-boot":
                if args.status == "master" or args.status == "slave":
                    print(repr(hal_firmware.set_bios_next_boot(args.status)))
            else:
                usage()
        else:
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
