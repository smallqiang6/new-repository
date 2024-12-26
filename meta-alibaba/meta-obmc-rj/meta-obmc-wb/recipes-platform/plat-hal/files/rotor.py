#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# rotor.py
# Python implementation of the Class rotor
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase
from .sensor import sensor

class rotor(devicebase):
    __rotor_Running   = None
    __rotor_HwAlarm_conf   = None
    __rotor_Speed     = None
    __rotor_run_conf  = None
    __Speedconfig = None
    __i2c_speed = None
    __SpeedMin         = None
    __SpeedMax         = None

    def __init__(self, conf = None):
        self.name = conf.get('name', None)
        self.rotor_HwAlarm_conf = conf.get('HwAlarm', None)
        self.rotor_run_conf = conf.get('Running', None)
        self.SpeedMin = conf.get('SpeedMin', None)
        self.SpeedMax = conf.get('SpeedMax', None)
        self.rotor_Speed = sensor(conf.get('Speed', None))
        self.Speedconfig = conf.get('Set_speed', None)

    def getRunning(self):
        if self.rotor_run_conf.get("fake", None) == 1:
            return True
        ret, val = self.get_value(self.rotor_run_conf)
        if val is None:
            return False
        mask = self.rotor_run_conf.get("mask")
        flag = val & mask
        if flag == mask:
            return True
        else:
            return False

    @property
    def SpeedMin(self):
        return self.__SpeedMin

    @SpeedMin.setter
    def SpeedMin(self, val):
        self.__SpeedMin = val

    @property
    def SpeedMax(self):
        return self.__SpeedMax

    @SpeedMax.setter
    def SpeedMax(self, val):
        self.__SpeedMax = val

    @property
    def i2c_speed(self):
        ret, val = self.get_value(self.Speedconfig)
        if ret == False:
            return None
        if val is not None:
            self.__i2c_speed = val
        return self.__i2c_speed

    def feed_watchdog(self):
        ret, val = self.get_value(self.Speedconfig)
        if ret == False:
            return False, None
        if val is not None:
            ret, val = self.set_value(self.Speedconfig, val)
            return ret, val
        return False, None

    @i2c_speed.setter
    def i2c_speed(self, val):
        self.__i2c_speed = val

    @property
    def Speedconfig(self):
        return self.__Speedconfig

    @Speedconfig.setter
    def Speedconfig(self, val):
        self.__Speedconfig = val

    @property
    def rotor_run_conf(self):
        return self.__rotor_run_conf

    @rotor_run_conf.setter
    def rotor_run_conf(self, val):
        self.__rotor_run_conf = val

    @property
    def rotor_Speed(self):
        return self.__rotor_Speed

    @rotor_Speed.setter
    def rotor_Speed(self, val):
        self.__rotor_Speed = val

    @property
    def rotor_HwAlarm(self):
        if self.rotor_Speed.Value < self.SpeedMin or self.rotor_Speed.Value > self.SpeedMax:
            return True
        if self.rotor_HwAlarm_conf.get("fake", None) == 1:
            return False
        ret, val = self.get_value(self.rotor_HwAlarm_conf)
        if ret is False:
            return False
        mask = self.rotor_HwAlarm_conf.get("mask")
        if val is None:
            return False
        flag = val & mask
        if flag == 0:
            return True
        else:
            return False
        return self.__rotor_HwAlarm

    @rotor_HwAlarm.setter
    def rotor_HwAlarm(self, val):
        self.__rotor_HwAlarm = val

    @property
    def rotor_HwAlarm_conf(self):
        return self.__rotor_HwAlarm_conf

    @rotor_HwAlarm_conf.setter
    def rotor_HwAlarm_conf(self, val):
        self.__rotor_HwAlarm_conf = val

    @property
    def rotor_Running(self):
        self.__rotor_Running = self.getRunning()
        return self.__rotor_Running

    @rotor_Running.setter
    def rotor_Running(self, val):
        self.__rotor_Running = val
