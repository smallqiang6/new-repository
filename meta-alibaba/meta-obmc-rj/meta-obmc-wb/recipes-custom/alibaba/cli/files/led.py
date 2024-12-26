#!/usr/bin/env python

# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from plat_utils.plat_common_util import *
from hal.hal_misc import HalMisc

def usage():
    print("usage:")
    print("    led.py get [location-led]")
    print("    led.py set location-led [on|off]")
    print("    led.py set system-fan-led [green|yellow|green-blink|yellow-blink|off]")
    exit()

if __name__ == "__main__":
    try:
        """
        led.py get/set system fan led and location led
        """
        platutil = PlatCommonUtil()
        hal_misc = HalMisc()
        args = platutil.Argparser(['option', 'nextpara', 'status'],
                              [str, str, str],
                              ['Action: get|set',
                               'Next led','location led status'],
                              [False, True, True])
        if args.option == "get":
            if args.nextpara == "location-led":
                print(repr(hal_misc.get_location_led()))
            else:
                print("error param")
                usage()
        elif args.option == "set":
            if args.nextpara == "location-led":
                if args.status == "on" or args.status == "off":
                    print(repr(hal_misc.set_location_led(args.status)))
            elif args.nextpara == "system-fan-led":
                if args.status == "green" or args.status == "off" or args.status == "yellow":
                    print(repr(hal_misc.set_system_fan_led(args.status)))
                elif args.status == "green-blink" or args.status == "yellow-blink":
                    param_tmp = args.status.split('-')[0]
                    print(repr(hal_misc.set_system_fan_led(param_tmp, True)))
                else:
                    print("error led status param")
                    usage()
            else:
                print("error next-led param")
                usage()
        else:
            print("error option")
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
