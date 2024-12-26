###############################################################################
#
# Hardware Abstraction Layer APIs -- FAN APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################

"""
class for HAL PSU APIs

API parameters convention:

@param psu_name Name of a PSU, format: "PSU%d" % psu_index, where psu_index is
                integer starting from 1
"""
from  plat_hal.interface import interface

class HalPsu(object):
    __int_case = None

    def __init__(self):
        self.int_case = interface()

    @property
    def int_case(self):
        return self.__int_case

    @int_case.setter
    def int_case(self, val):
        self.__int_case = val

    def get_psus(self):
        return self.int_case.get_psus()

    def get_total_number(self):
        """
        Get system's total number of PSU

        @return Total number of PSU, -1 for failure
        """
        return self.int_case.get_psu_total_number()

    def get_presence(self, psu_name):
        """
        Get a specific PSU's presence status

        @return True if present, False for NOT present or failure
        """
        return self.int_case.get_psu_presence(psu_name)

    def get_fru_info(self, psu_name):
        """
        Get FRU info of a specific PSU

        @return dict of the specific PSU's info, None for failure
                Example return value(all keys are mandatory)
                {
                    "Name": "PSU1",
                    "SN": "serial_number_example",    # 'N/A'
                    "PN": "part_number_example",      # 'N/A'
                    "AirFlow": "B2F"                  # 'N/A'
                }
        """
        return self.int_case.get_psu_fru_info(psu_name)

    def get_status(self, psu_name):
        """
        Get status of a specific PSU

        @return dict of the specific PSU's status, None for failure
                Example return value(all keys are mandatory)
                {
                    "Name": "PSU1",
                    "InputType": "DC",    # "AC" or 'N/A'
                    "InputStatus": True,  # H/W status bit
                    "OutputStatus": True  # H/W status bit
                    "FanSpeed": {
                        "Value": 4000,    # -99999
                        "Min": 2000,      # -99999
                        "Max": 10000      # -99999
                    },
                    "Temperature": {
                        "Value": 40.0,    # -99999.0
                        "Min": -30.0,     # -99999.0
                        "Max": 50.0       # -99999.0
                    }
                }
        """
        return self.int_case.get_psu_status(psu_name)

    def get_power_status(self, psu_name):
        """
        Get power status of a specific PSU

        @return dict of the specific PSU's power status, None for failure
                Example return value
                {
                    "Name": "PSU1",
                    "Inputs": {
                        "Status": True, # H/W status bit
                        "Type": "DC",   # or "AC" or "N/A"
                        "Voltage": {
                            "Value": 220,       # -1
                            "LowAlarm": 200,    # -1
                            "HighAlarm": 240,   # -1
                            "Unit": "V"
                        },
                        "Current": {
                            "Value": 6.0,       # -99999.0
                            "LowAlarm": 0.2,    # -99999.0
                            "HighAlarm": 7.0,   # -99999.0
                            "Unit": "A"
                        },
                        "Power": {
                            "Value": 1000,      # -99999
                            "LowAlarm": -1,     # -99999
                            "HighAlarm": 1400,  # -99999
                            "Unit": "W"
                       }
                    },
                    "Outputs": {
                        "Status": True,
                        "Voltage": {
                            "Value": 220,
                            "LowAlarm": 200,
                            "HighAlarm": 240,
                            "Unit": "V"
                        },
                        "Current": {
                            "Value": 6.0,
                            "LowAlarm": 0.2,
                            "HighAlarm": 7.0,
                            "Unit": "A"
                        },
                        "Power": {
                            "Value": 1000,
                            "LowAlarm": -1,  # Don't care
                            "HighAlarm": 1400,
                            "Unit": "W"
                        }
                    }
                }
        """
        return self.int_case.get_psu_power_status(psu_name)

    def set_psu_fan_speed_pwm(self, psu_name, pwm):
        """
        Set a specific PSU's fan's speed

        @param pwm duty cycle, unit is 1%

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_psu_fan_speed_pwm(psu_name, pwm)

    def get_psu_fan_speed_pwm(self, psu_name):
        """
        Get a specific PSU's fan's speed

        @return pwm duty cycle, unit is 1%, -1 for failure
        """
        return self.int_case.get_psu_fan_speed_pwm(psu_name)

    def get_info_all(self):
        """
        Get all system PSU's info

        @return dict of all PSUs or None for failure
                {
                    "Number": 2,
                    "PSU1": {
                        "SN": "serial_number_example",  # 'N/A'
                        "PN": "part_number_example",    # 'N/A'
                        "AirFlow": "F2B",               # 'N/A'
                        "Present": "yes"                # "no"

                        "FanSpeed": {
                            "Value": 4000,
                            "Min": 2000,
                            "Max": 30000
                        },
                        "Temperature": {
                            "Value": 35.0,
                            "Min": -20.0,
                            "Max": 45.0
                        },
                        "Inputs": {
                            "Status": True, # H/W status bit
                            "Type": "DC",   # or "AC"
                            "Voltage": {
                                "Value": 220,
                                "LowAlarm": 200,
                                "HighAlarm": 240,
                                "Unit": "V"
                            },
                            "Current": {
                                "Value": 6.0,
                                "LowAlarm": 0.2,
                                "HighAlarm": 7.0,
                                "Unit": "A"
                            },
                            "Power": {
                                "Value": 1000,
                                "LowAlarm": -1,
                                "HighAlarm": 1400,
                                "Unit": "W"
                           }
                        },
                        "Outputs": {
                            "Status": True,
                            "Voltage": {
                                "Value": 220,
                                "LowAlarm": 200,
                                "HighAlarm": 240,
                                "Unit": "V"
                            },
                            "Current": {
                                "Value": 6.0,
                                "LowAlarm": 0.2,
                                "HighAlarm": 7.0,
                                "Unit": "A"
                            },
                            "Power": {
                                "Value": 1000,
                                "LowAlarm": -1,  # Don't care
                                "HighAlarm": 1400,
                                "Unit": "W"
                            }
                        }
                    }
                }
        """
        return self.int_case.get_psu_info_all()
