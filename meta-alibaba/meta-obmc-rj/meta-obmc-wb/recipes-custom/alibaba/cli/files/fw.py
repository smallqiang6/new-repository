#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_firmware import HalFirmware

def usage():
    print("usage:")
    print("    fw.py program {bmc|bios} filename {master|slave}")
    print("    fw.py program ['name1', 'name2',...] ['file1', '[file2]',...]")
    print("    fw.py refresh ['name1', 'name2',...] ['file1', '[file2]',...]")
    exit()

if __name__ == "__main__":
    """
    Commamd line interface with an input of a json file.
    """
    platutil = PlatCommonUtil()
    hal_firmware = HalFirmware()
    try:
        """
        fw.py program {bmc|cpld|bios} filename
        fw.py refresh "['name1', 'name2',...]" "['file1', '[file2]',...]"
        """
        args = platutil.Argparser(['option', 'name', 'filename', 'flash'],
                              [str, str, str, str],
                              ['Action : program|refresh ',
                               'type : bmc|cpld|bios',
                               'filename: image-bin',
                               'flash : master|slave',],
                              [False, False, False, True])
        if args.option == "program":
            if args.name == "bmc":
                print(hal_firmware.program_bmc(args.flash, args.filename))
            elif args.name == "bios":
                print(hal_firmware.program_bios(args.flash, args.filename))
            elif len(eval(args.name)) == len(eval(args.filename)):
                print(hal_firmware.program_cpld(eval(args.name), eval(args.filename)))
            else:
                usage()
        elif args.option == "refresh":
            if len(eval(args.name)) != len(eval(args.filename)):
                usage()
            for i in range(len(args.name)):
                if args.name[i].lower() == "fpga":
                    fpga_index = args.name.index("fpga")
                    if args.filename[fpga_index] != "none":
                        usage()
                if args.name[i].lower() == "bios":
                    bios_index = args.name.index("bios")
                    if args.filename[bios_index] != "none":
                        usage()
            print(hal_firmware.refresh_firmware(eval(args.name), eval(args.filename)))
        else:
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
