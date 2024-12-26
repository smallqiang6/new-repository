###############################################################################
#
# Hardware Abstraction Layer APIs -- Temperature APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################

"""
class for HAL sensor APIs.

@param sensor_dict: Dict of sensor value
                    Example:
                    {
                        "Value": 30.0,      # -99999.0
                        "Min": -10.0,       # -99999.0
                        "Max": 50.0,        # -99999.0
                        "Unit": "C"         # "N/A"
                    }
@param name Name of a specific sensor
"""
import json
import os

from plat_hal.interface import interface


HAL_PLATFORM_DIR = "/etc/openbmc/devices"
HAL_SENSOR_CONFIG_NAME = "sensors_config.json"


class HalSensor(object):
    __int_case = None

    def __init__(self):
        self.int_case = interface()
        try:
            plat_name = self.int_case.get_bmc_productname()
            if not plat_name or plat_name == "N/A":
                msg = "Failed to get platform name in HalSensor init"
                raise Exception(msg)

            self.config_file = "/".join([HAL_PLATFORM_DIR, plat_name, \
                                         HAL_SENSOR_CONFIG_NAME])
        except Exception as e:
            msg = "Get sensor file name got exception: %s" % str(e)
            raise Exception(msg)

        if self.load_config() != 0:
            msg = "Load config %s failed" % self.config_file
            raise Exception(msg)

    @property
    def int_case(self):
        return self.__int_case

    @int_case.setter
    def int_case(self, val):
        self.__int_case = val

    def load_config(self, config_file=None):
        """
        Load sensors configuration

        Configuration file is writen in JSON format. Mandatory keys:

        {
            "TEMPERATURE_SENSORS": {
                "Cpu": "sensor_name_for_cpu_temp",
                "Inlet": "sensor_name_for_inlet_temp",
                "Switch": "sensor_name_for_switch_temp"
            },
            "DCDC_SENSORS": {
                "DcdcInputVoltageName1": {
                    "Descr": "DCDC Input Voltage Name1 detailed description",
                    "Name": "sensor_name_for_dcdc_sensor_name1"
                },
                "DcdcInputCurrentName2": {
                    "Descr": "DCDC Input Current Name2 detailed description",
                    "Name": "sensor_name_for_dcdc_sensor_name2"
                },
                "DcdcOutputVoltageName3": {
                    "Descr": "DCDC Output Voltage Name3 detailed description",
                    "Name": "sensor_name_for_dcdc_sensor_name3"
                }
            }
        }

        @return 0 for success, -1 for failure
        """
        if config_file:
            self.config_file = config_file

        if not os.path.isfile(self.config_file):
            return -1

        with open(self.config_file) as fh:
            self.config = json.load(fh)

        return 0

    def get_sensor(self, name):
        """
        Get a specific sensor's info

        @return sensor_dict or None for failure
        """
        sensorlist = self.int_case.get_sensor_info()
        return sensorlist.get(name)

    def get_monitor_temp(self, name):
        sensorvalue = self.int_case.get_monitor_temp(name)
        return sensorvalue

    def get_sensor_info(self):
        """
        @return dict of sensors' information
                {
                    "SensorName1": {
                        "Value": 1.0,       # -99999.0
                        "Min": 0.0,         # -99999.0
                        "Max": 2.0,         # -99999.0
                        "Unit": "C"         # "N/A"
                    }
                }
        """
        return self.int_case.get_sensor_info()

    def get_evst_sensor(self, name):
        """
        Get all event status sensor info
        @return dict for all EVST sensor info or None for failure
        Example:
        {
            "PLL_LOCK_HISTORY_EVENT": {
                "Descr": "PLL lock history",
                "Value": 0,
                "Decoder": {
                    0: "Never",
                    1: "Unlocked",
                    2: "Locked",
                    3: "Unlocked and Locked"
                },
                "RW": "RO",
                "Expects": [1, 2, 3]
            }
        }
        """
        if hasattr(self.int_case, 'get_evst_info'):
            return self.int_case.get_evst_info(name)
        return None

    def reset_evst_sensor(self, name):
        """
        Reset the EVST sensor to default value
        @return 0 for success, -1 for failure
        """
        if hasattr(self.int_case, 'reset_evst_sensor'):
            return self.int_case.reset_evst_sensor(name)
        return -1
