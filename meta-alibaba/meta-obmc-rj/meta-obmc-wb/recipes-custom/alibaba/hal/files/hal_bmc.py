###############################################################################
#
# Hardware Abstraction Layer APIs -- BMC APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################

"""
class for HAL BMC APIs

"""
import subprocess
import os
import sys
import re

from plat_utils.plat_common_util import *
from plat_hal.bmc import bmc
from plat_hal.interface import interface

class HalBmc(object):
    def __init__(self):
        try:
            self.int_case = interface()
        except:
            pass
        bmc_default_conf =  {
            "FwVersion": "/var/log/fw/fw_version",
            "CurrentFlashFlag": {"addr": 0x1E620064,  "digit":32, "way":"devmem", "mask": 0x10},
        }
        self.bmc = bmc(bmc_default_conf)

    def get_info(self):
        """
        Get BMC info

        @return dict of BMC info or None for failure
                {
                    "Version": "1.1.1", # "N/A"
                    "Flash": "master",  # "N/A"
                    "Next": "master"    # "N/A"
                }
        """
        #When bmc starts, this function willed be called, which cannot be realized by int_case
        return self.bmc.get_info()

    def get_version_all(self):
        """
        @return dict of BMCs
                {
                    "MasterVersion": "1.1.1",   # "N/A"
                    "SlaveVersion": "1.1.1"     # "N/A"
                }
        """
        return self.int_case.get_bmc_version_all()

    def get_status(self):
        """
        Get BMC system status

        @return dict of system status or None for failure
                # "N/A" for invalid outpouts
                {
                    "CPU": {
                        "StateOutputs": "output of command 'top -bn 1'"
                        "Usage": "10.0"
                    },
                    "MEMORY": {
                        "StateOutputs": "output of command 'free -m'"
                        "Usage": "15.0"   # caculate: "free -t | grep \"buffers/cache\" | awk '{ printf \"mem usage  : %.1f%%\\n\",$3/($3+$4) * 100}'"
                    },
                    "DISK": {
                        "StateOutput": "output of command 'df -h'"
                        "Usage": "12.5"
                    }
                }
        """
        return self.bmc.get_status()

    def get_next_boot(self):
        """
        Get next booting flash of BMC

        @return 'master'/'slave' on success, "N/A" for failure
        """
        return self.int_case.get_bmc_next_boot()

    def set_next_boot(self, flash):
        """
        Set flash from which next BMC boot

        @param flash Booting flash of BMC, "master" or "slave"

        @return 0 on success, -1 for failure
        """
        return self.int_case.set_bmc_next_boot(flash)

    def reboot(self):
        """
        Reboot running BMC
        """
        return self.int_case.reboot_bmc()
