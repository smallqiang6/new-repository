###############################################################################
#
# Hardware Abstraction Layer APIs -- CPU APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################

"""
class for HAL CPU APIs
"""
from plat_hal.cpu import cpu
from plat_hal.interface import interface

class HalCPU(object):
    def __init__(self):
        self.cpu = cpu()
        self.int_case = interface()

    def get_state(self):
        """
        Get CPU current state.

        @return 'S0', ..., 'S5', or 'N/A' for failure
        """
        return self.int_case.get_cpu_status()

    def get_mca_error(self):
        """
        Get CPU MCA error count.

        @return List of MCERR and IERR counts, or None for failure
                Example:
                {
                    "MCErr": 0,         # -99999
                    "IErr": 0           # -99999
                }
        """
        return self.cpu.get_mca_error()

    def get_aer_error(self):
        """
        Get CPU AER error vector.

        @return List of AER error vector or None for failure
                Example:
                [ERR[0], ERR[1], ERR[2]]
        """
        return self.cpu.get_aer_error()

    def get_last_reset(self):
        """
        Get last CPU reset type, WARM/COLD.

        @return Last CPU reset type, "WARM"/"COLD", "N/A" for failure
        """
        return self.int_case.get_cpu_last_reset()
