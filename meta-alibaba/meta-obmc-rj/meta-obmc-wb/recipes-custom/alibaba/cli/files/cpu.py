#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_cpu import HalCPU
from plat_hal.interface import interface

def usage():
    print("usage:")
    print("    cpu.py get all")
    exit()

if __name__ == "__main__":
    """
    cpu.py get all CPU currentstate MCA error count AER error last CPU reset type
    """
    hal_cpu = HalCPU()
    platutil = PlatCommonUtil()
    plat_interface = interface()
    try:
        """
        CPU Info:
            Current state: S0
            Last reset type: WARM
            MCA error count: MCErr: 0,  IErr: 0
            AER error count: ERR[0]: 0, ERR[1]: 0, ERR[2]: 0
        """
        args = platutil.Argparser(['option', 'type'],
                              [str, str],
                              ['Action : get',
                               'type : all'],
                              [False, True])
        if args.option == "get":
            if args.type == "all":
                mca_err = hal_cpu.get_mca_error()
                aer_err = hal_cpu.get_aer_error()
                print("CPU Info: ")
                print("    Current state: %s" %(repr(hal_cpu.get_state())))
                print("    Last reset type: %s" %(repr(hal_cpu.get_last_reset())))
                print("    Cpu reset num: %s" %(repr(plat_interface.get_cpu_reset_num())))
                print("    MCA error count: MCErr: %d, IErr: %d" %(mca_err["MCErr"], mca_err["IErr"]))
                print("    AER error count: ERR[0]: %d, ERR[1]: %d, ERR[2]: %d" %(aer_err[0], aer_err[1], aer_err[2]))
            else:
                print("error option")
                usage()
        else:
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
