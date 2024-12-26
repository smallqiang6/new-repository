###############################################################################
#
# Hardware Abstraction Layer APIs -- FAN APIs.
#
# Copyright (C) Alibaba, INC.
#
###############################################################################


"""
class for HAL Fan APIs

API parameters convention:

@param fan_name: Name of the specific fan, format: "FAN%d" % (fan_index),
                 where fan_index is integer starting from 1
@param rotor_index: Index of the specific  fan's rotor, integer starting from 1
"""
from plat_hal.interface import interface

class HalFan(object):
    __int_case = None

    def __init__(self):
        self.int_case = interface()

    @property
    def int_case(self):
        return self.__int_case

    @int_case.setter
    def int_case(self, val):
        self.__int_case = val

    def get_fans(self):
        return self.int_case.get_fans()

    def get_total_number(self):
        """
        Get total fan number count

        @return total number of fan in the system, -1 for failure
        """
        return self.int_case.get_fan_total_number()

    def get_rotor_number(self, fan_name):
        """
        Get fan's rotor count for specific fan_name

        @return total rotor count of specific fan, -1 for failure
        """
        return self.int_case.get_fan_rotor_number(fan_name)

    def get_speed(self, fan_name, rotor_index):
        """
        Get current speed for specific fan and rotor

        @return speed of the specific fan and rotor, unit is RPM,
                -1 for failure
        """
        return self.int_case.get_fan_speed(fan_name, rotor_index)

    def set_speed(self, fan_name, rotor_index, speed):
        """
        Get current speed for specific fan and rotor

        @param speed of the specific fan and rotor, unit is RPM

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_fan_speed(fan_name, rotor_index, speed)

    def get_speed_pwm(self, fan_name, rotor_index):
        """
        Get current PWM duty cycle for specific fan's specific rotor

        @return PWM duty cycle, unit is 1%, -1 for failure
        """
        return self.int_case.get_fan_speed_pwm(fan_name, rotor_index)

    def set_speed_pwm(self, fan_name, rotor_index, pwm):
        """
        Set PWM for specific fan's specific rotor

        @param pwm duty cycle, unit is 1%, -1 for failure

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_fan_speed_pwm(fan_name, rotor_index, pwm)

    def get_watchdog_status(self):
        """
        Get Fan watchdog status.

        @return 'Normal'/'Abnormal'/'N/A' for status good/bad/read-failed.
        """
        return self.int_case.get_fan_watchdog_status()

    def enable_watchdog(self, enable=True, timeout_sec=10):
        """
        Enable Fan watchdog

        @return 0 for success, -1 for failure
        """
        return self.int_case.enable_fan_watchdog(enable, timeout_sec)

    def feed_watchdog(self, pwm):
        """
        Feed watchdog

        @param pwm duty cycle, unit is 1%, -1 for failure

        @return 0 for success, -1 for failure
        """
        return self.int_case.feed_fan_watchdog(pwm)

    def set_led(self, fan_name, color, blink=False):
        """
        Set fan LED

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        return self.int_case.set_fan_led(fan_name, color, blink)

    def get_presence(self, fan_name):
        """
        Get a specific fan's presence status

        @return True for present, False for not present or failure
        """
        return self.int_case.get_fan_presence(fan_name)

    def get_fru_info(self, fan_name):
        """
        Get specific fan's information

        @return dict for specific fan on success, None for failure
                Example return value(all keys are mandatory)
                {
                    # Properties
                    "Name": "FAN1",
                    "SN": "serial_number_example",  # 'N/A'
                    "PN": "part_number_exampple",   # 'N/A'
                    "Rotors": 2,                    # -1
                    "AirFlow": "F2B",               # 'N/A'
                    "SpeedMin": 2000,               # -1
                    "SpeedMax": 30000               # -1
                }
        """
        return self.int_case.get_fan_fru_info(fan_name)

    def get_status(self, fan_name):
        """
        Get status of specific fan

        @return dict for specific fan for success, None for failure
                Example return value(all keys are mandatory)
                {
                    "Rotor1": {
                        "Running": "no",        # 'N/A'
                        "HwAlarm": "yes",       # 'N/A'
                        "speed": 0              # -1
                    },
                    "Rotor2": {
                        "Running": "yes",
                        "HwAlarm": "no",
                        "Speed": 6800
                    }
                }
        """
        return self.int_case.get_fan_status(fan_name)

    def get_info_all(self):
        """
        Get all fans' info

        @return dict of all system fans' infor for success, None for failure
                Example return value(all keys are mandatory)
                {
                    "Number": 2,                 # -99999
                    "WatchdogStatus": "Normal",  # "Abnormal"/"N/A"
                    "FAN1": {
                        # Properties
                        "Name": FAN1,
                        "SN": "serial_number_example",  # 'N/A'
                        "PN": "part_number_exampple",   # 'N/A'
                        "Present": "yes",               # 'N/A'
                        "Rotors": 2,                    # -99999
                        "AirFlow": "F2B",               # 'N/A'

                        # Status, dynamic data
                        "Rotor1": {
                            "Running": "yes",           # 'N/A'
                            "HwAlarm": "no",            # 'N/A'
                            "Speed": 7000               # -99999
                            "SpeedMin": 2000,           # -99999
                            "SpeedMax": 30000,          # -99999
                        },
                        "Rotor2": {
                            "Running": "yes",
                            "HwAlarm": "no"
                            "Speed": 8000
                            "SpeedMin": 2000,
                            "SpeedMax": 30000,
                        }
                    },
                    "FAN2": {
                        # Properties
                        "Name": FAN2,
                        "SN": "serial_number_example",
                        "PN": "part_number_exampple",
                        "Present": "yes"
                        "Rotors": 2,
                        "AirFlow": "F2B",
                        "SpeedMin": 2000,
                        "SpeedMax": 30000,

                        # Status, dynamic data
                        "Rotor1": {
                            "Running": "no",
                            "HwAlarm": "yes",
                            "Speed": 0
                        },
                        "Rotor2": {
                            "Running": "yes",
                            "HwAlarm": "no",
                            "Speed": 6800
                        }
                    }
                }
        """
        return self.int_case.get_fan_info_all()
