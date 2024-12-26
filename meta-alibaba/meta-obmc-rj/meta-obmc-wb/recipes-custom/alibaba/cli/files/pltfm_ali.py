#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import inspect
import os
import sys
import json
import time
from  hal.hal_dcdc import HalDcdc
from  hal.hal_fan import HalFan
from  hal.hal_psu import HalPsu
from  hal.hal_sensor import HalSensor
from  hal.hal_temp import HalTemperature

class Basecommand():
    def __init__(self, doc = '', name = None):
        self.name  = name
        self.doc = doc

class Command(Basecommand):
    def __init__(self, name, f):
        self.name =name
        self.f = f
        self.paramcount =self.f.__code__.co_argcount

    def dofun(self, args):
        fn = self.f.__call__
        fn(*args)

class Group(Basecommand):
    def __init__(self, name, f):
        self.groups= []
        self.commands = []
        self.name =name
        self.f = f
        pass

    def add_groups(self, command):
        self.groups.append(command)
        pass

    def add_commands(self, commnad):
        x = Command(commnad.__name__, commnad)
        self.commands.append(x)

    def find_valuebyname(self, name):
        for item in self.groups:
            if name == item.name:
                return item
        for item in self.commands:
            if name == item.name:
                return item
        return None

    def deal(self, args):
        if len(args) <= 0:
            return self.print_help()
        funclevel = args[0]
        val = self.find_valuebyname(funclevel)
        if val is None:
            return self.print_help()
        if isinstance(val, Command):
            if len(args) < (val.paramcount + 1):
                return self.print_help()
            else:
                inputargs = args[1: (1 + val.paramcount)]
            return val.dofun(inputargs)
        if isinstance(val , Group):
            args = args[1:]
            return val.deal(args)
        else:
            self.print_help()

    def get_max(self, arr):
        lentmp = 0
        for ar in arr:
            lentmp = len(ar) if (len(ar) > lentmp) else lentmp
        return lentmp

    def print_help(self,*attrs):

        namesize = []
        for item in self.groups:
            namesize.append(item.name)
        for item in self.commands:
            namesize.append(item.name)
        maxvalue  = self.get_max(namesize)

        if len(self.groups) > 0:
            print("Groups:")
            for item in self.groups:
                print("   %-*s    %s" % (maxvalue, item.name, item.f.__doc__ or ''))
        if len(self.commands) > 0:
            print("Commands:")
            for item in self.commands:
                print("   %-*s   %s" % (maxvalue,item.name, item.f.__doc__ or ''))

class clival():
    @staticmethod
    def Fire(val = None):
        group = Group("top",'mainlevel')
        clival.iterGroup(val, group)
        # context = {}
        # caller = inspect.stack()[1]
        # caller_frame = caller[0]
        # caller_globals = caller_frame.f_globals
        # caller_locals = caller_frame.f_locals
        # context.update(caller_globals)
        # context.update(caller_locals)
        args = sys.argv[1:]
        group.deal(args)

    @staticmethod
    def iterGroup(val, group):
        for key, item in val.items():
            if item is None:  # first level
                if (inspect.isfunction(key)):
                    group.add_commands(key)
            else:
                group1 = Group(key.__name__, key)
                clival.iterGroup(item, group1)
                group.add_groups(group1)

def psu():
    r'''test psu '''
    pass

def fan():
    r'''test fan '''
    pass

def sensor():
    r'''test sensor '''
    pass

def dcdc():
    r'''test dcdc '''
    pass

def temp():
    r'''test temp '''
    pass

def get_total_number():
    r'''psu  get_total_number '''
    psu_case = HalPsu()
    print("=================get_total_number======================")
    print(psu_case.get_total_number())

def get_presence():
    r'''psu  get_presence '''
    psu_case = HalPsu()
    print("=================get_presence======================")
    psus = psu_case.get_psus()
    for psu in psus:
        print(psu.name, end=' ')
        print(psu_case.get_presence(psu.name))

def get_fru_info():
    r'''psu  get_fru_info '''
    psu_case = HalPsu()
    print("=================get_fru_info======================")
    psus = psu_case.get_psus()
    for psu in psus:
        print(psu.name, end=' ')
        print(json.dumps(psu_case.get_fru_info(psu.name), sort_keys=True, ensure_ascii = False, indent=4))

def get_status():
    r'''psu  get_status '''
    psu_case = HalPsu()
    print("=================get_status======================")
    psus = psu_case.get_psus()
    for psu in psus:
        print(psu.name, end=' ')
        print(json.dumps(psu_case.get_status(psu.name), sort_keys=True, ensure_ascii = False,indent=4))

def set_psu_fan_speed_pwm(realspeed):
    r'''set_psu_fan_speed_pwm'''
    psu_case = HalPsu()
    print("=================set_psu_fan_speed_pwm======================")
    psus = psu_case.get_psus()
    for psu in  psus:
        print(psu.name, end=' ')
        #total = psu_case.set_psu_fan_speed_pwm(psu.name, int(realspeed))
        print(psu_case.set_psu_fan_speed_pwm(psu.name, int(realspeed)))

def get_psu_fan_speed_pwm():
    r'''get_psu_fan_speed_pwm'''
    psu_case = HalPsu()
    print("=================get_psu_fan_speed_pwm======================")
    psus = psu_case.get_psus()
    for psu in  psus:
        print(psu.name, end=' ')
        print(json.dumps(psu_case.get_psu_fan_speed_pwm(psu.name), sort_keys=True))
    pass

def get_psu_power_status():
    r'''psu  get_psu_power_status '''
    psu_case = HalPsu()
    print("=================get_psu_power_status======================")
    psus = psu_case.get_psus()
    for psu in psus:
        print(psu.name, end=' ')
        print(json.dumps(psu_case.get_power_status(psu.name), sort_keys=True, ensure_ascii = False,indent=4))

def get_info_all():
    r'''psu  get_info_all '''
    psu_case = HalPsu()
    print("=================get_info_all======================")
    print(json.dumps(psu_case.get_info_all(), sort_keys=True, ensure_ascii = False,indent=4))

def fan_get_total_number():
    r'''fan_get_total_number'''
    fan_case = HalFan()
    print("=================get_info_all======================")
    print(json.dumps(fan_case.get_total_number(), sort_keys=True, ensure_ascii = False, indent=4))


def fan_get_rotor_number():
    r'''fan_get_rotor_number'''
    fan_case = HalFan()
    print("=================fan_get_rotor_number======================")
    fans = fan_case.get_fans()
    for fan in  fans:
        print(fan.name, end=' ')
        print(fan_case.get_rotor_number(fan.name))

def fan_get_speed1():
    r'''fan_get_speed'''
    fan_case = HalFan()
    print("=================fan_get_speed======================")
    fans = fan_case.get_fans()
    for fan in  fans:
        rotors = fan.rotor_list
        for rotor in rotors:
            print("%s %s"%(fan.name, rotor.name) , end ='  ' )
            print(fan_case.get_speed(fan.name, rotor.name))
    pass

def fan_get_speed():
    r'''fan_get_speed'''
    fan_case = HalFan()
    print("=================fan_get_speed======================")
    fans = fan_case.get_fans()
    for fan in  fans:
        rotor_len = fan_case.get_rotor_number(fan.name)
        for i in range(rotor_len):
            print("%s rotor%d"%(fan.name, i + 1) , end ='  ' )
            print(fan_case.get_speed(fan.name, i + 1))
    pass

def fan_set_speed(realspeed):
    r'''fan_set_speed'''
    fan_case = HalFan()
    speed = int(realspeed)
    xspeed = round(speed /255 * 100)
    print("=================fan_set_speed======================")
    fans = fan_case.get_fans()
    for fan in  fans:
        rotors = fan.rotor_list
        for rotor in rotors:
            index  =  rotors.index(rotor)
            print("%s %s" % (fan.name, rotor.name) , end ='  ' )
            print(fan_case.get_speed(fan.name, index + 1), end ='  ')
            print(fan_case.set_speed_pwm(fan.name, index + 1, xspeed))
            time.sleep(5)
            print("%s %s" % (fan.name, rotor.name) , end ='  ' )
            print(fan_case.get_speed(fan.name, index + 1))

def fan_get_speed_pwm():
    r'''fan_get_speed_pwm'''
    fan_case = HalFan()
    print("=================fan_get_speed_pwm======================")
    fans = fan_case.get_fans()
    for fan in  fans:
        rotor_len = fan_case.get_rotor_number(fan.name)
        for i in range(rotor_len):
            print("%s rotor%d" % (fan.name, i + 1), end='  ' )
            print (fan_case.get_speed_pwm(fan.name, i + 1))

def fan_set_speed_pwm(pwm):
    r'''fan_set_speed_pwm'''
    fan_case = HalFan()
    print("=================fan_set_speed_pwm======================")
    fans = fan_case.get_fans()
    for fan in fans:
        rotor_len = fan_case.get_rotor_number(fan.name)
        for i in range(rotor_len):
            print("%s rotor%d" % (fan.name, i + 1), end='  ')
            val = fan_case.set_speed_pwm(fan.name, i + 1, pwm)
            print (val)

def fan_get_watchdog_status():
    r'''fan_get_watchdog_status'''
    fan_case = HalFan()
    print("=================fan_get_watchdog_status======================")
    print(fan_case.get_watchdog_status())
    pass

def fan_enable_watchdog():
    r'''fan_enable_watchdog'''
    fan_case = HalFan()
    print("=================fan_enable_watchdog======================")
    print('enable',fan_case.enable_watchdog())

def fan_disable_watchdog():
    r'''fan_disable_watchdog'''
    fan_case = HalFan()
    print("=================fan_disable_watchdog======================")
    print('disable', fan_case.enable_watchdog(enable = False))



def fan_feed_watchdog():
    r'''fan_feed_watchdog'''
    fan_case = HalFan()
    print("=================fan_feed_watchdog======================")
    fan_get_speed()
    print (fan_case.feed_watchdog(None))
    time.sleep(2)
    fan_get_speed()

def fan_set_led(color):
    r'''fan_set_led'''
    fan_case = HalFan()
    print("=================fan_set_led======================")
    fans = fan_case.get_fans()
    for fan in fans:
        print("%s" % fan.name)
        for i in range(2):
            if i == 0:
                flag = True
            elif i == 1:
                flag = False
            print(color, fan_case.set_led(fan.name, color, flag))

def fan_get_presence():
    r'''fan_get_presence'''
    fan_case = HalFan()
    print("=================fan_get_presence======================")
    fans = fan_case.get_fans()
    for fan in fans:
        print("%s" % fan.name)
        print(fan_case.get_presence(fan.name))

def fan_get_fru_info():
    r'''fan_get_fru_info'''
    fan_case = HalFan()
    print("=================fan_get_fru_info======================")
    fans = fan_case.get_fans()
    for fan in fans:
        print("%s" % fan.name)
        print(json.dumps(fan_case.get_fru_info(fan.name), sort_keys=True, ensure_ascii=False, indent=4))

def fan_get_status():
    r'''fan_get_status'''
    fan_case = HalFan()
    print("=================fan_get_status======================")
    fans = fan_case.get_fans()
    for fan in fans:
        print("%s" % fan.name)
        print(json.dumps(fan_case.get_status(fan.name), sort_keys=True, ensure_ascii=False, indent=4))

def fan_get_info_all():
    r'''fan_get_info_all'''
    fan_case = HalFan()
    print("=================fan_get_info_all======================")
    print(json.dumps(fan_case.get_info_all(), sort_keys=True, ensure_ascii=False, indent=4))
    pass

def get_sensor_info():
    r'''get_sensor_info'''
    sensor_case = HalSensor()
    print("=================get_sensor_info======================")
    print(json.dumps(sensor_case.get_sensor_info(), sort_keys=True, ensure_ascii = False, indent=4))

def get_dcdc_sensors():
    r'''get_dcdc_sensors'''
    sensor1 = HalSensor()
    dcdc_case = HalDcdc(sensor1)
    print("=================get_dcdc_sensors======================")
    print(json.dumps(dcdc_case.get_dcdc_sensors(), sort_keys=True, ensure_ascii=False, indent=4))

def get_dcdc_sensor_value(name):
    r'''get_dcdc_sensor_value'''
    sensor1 = HalSensor()
    dcdc_case = HalDcdc(sensor1)
    print("=================get_dcdc_sensor_value======================")
    print(json.dumps(dcdc_case.get_dcdc_sensor_value(name), sort_keys=True, ensure_ascii=False, indent=4))

def get_dcdc_sensor_descr(name):
    r'''get_dcdc_sensor_descr'''
    sensor1 = HalSensor()
    dcdc_case = HalDcdc(sensor1)
    print("=================get_dcdc_sensor_descr======================")
    print(dcdc_case.get_dcdc_sensor_descr(name))

def get_dcdc_all_info():
    r'''get_dcdc_all_info'''
    sensor1 = HalSensor()
    dcdc_case = HalDcdc(sensor1)
    print("=================get_dcdc_all_info======================")
    print(json.dumps(dcdc_case.get_dcdc_all_info(), sort_keys=True, ensure_ascii=False, indent=4))

def get_cpu_temp():
    r'''get_cpu_temp'''
    sensor1 = HalSensor()
    temp_case = HalTemperature(sensor1)
    print("=================get_cpu_temp======================")
    print(json.dumps(temp_case.get_cpu_temp(), sort_keys=True, ensure_ascii=False, indent=4))

def get_inlet_temp():
    r'''get_inlet_temp'''
    sensor1 = HalSensor()
    temp_case = HalTemperature(sensor1)
    print("=================get_inlet_temp======================")
    print(json.dumps(temp_case.get_inlet_temp(), sort_keys=True, ensure_ascii=False, indent=4))

def get_switch_temp():
    r'''get_switch_temp'''
    sensor1 = HalSensor()
    temp_case = HalTemperature(sensor1)
    print("=================get_switch_temp======================")
    print(json.dumps(temp_case.get_switch_temp(), sort_keys=True, ensure_ascii=False, indent=4))

def get_nic_temp():
    r'''get_nic_temp'''
    sensor1 = HalSensor()
    temp_case = HalTemperature(sensor1)
    print("=================get_nic_temp======================")
    print(json.dumps(temp_case.get_nic_temp(), sort_keys=True, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    clival.Fire(
        {
            psu:{
                    get_total_number       : None,
                    get_presence           : None,
                    get_fru_info           : None,
                    set_psu_fan_speed_pwm  : None,
                    get_psu_fan_speed_pwm  : None,
                    get_status             : None,
                    get_psu_power_status   : None,
                    get_info_all           : None
                 },
            fan:{
                    fan_get_total_number    : None,
                    fan_get_rotor_number    : None,
                    fan_get_speed           : None,
                    fan_set_speed           : None,
                    fan_get_speed_pwm       : None,
                    fan_set_speed_pwm       : None,
                    fan_get_watchdog_status : None,
                    fan_enable_watchdog     : None,
                    fan_disable_watchdog    : None,
                    fan_feed_watchdog       : None,
                    fan_set_led             : None,
                    fan_get_presence        : None,
                    fan_get_fru_info        : None,
                    fan_get_status          : None,
                    fan_get_info_all        : None
                 },
            sensor:{
                    get_sensor_info         : None
                 },
            dcdc:{
                    get_dcdc_sensors        : None,
                    get_dcdc_sensor_value   : None,
                    get_dcdc_sensor_descr   : None,
                    get_dcdc_all_info       : None,
            },
            temp:{
                    get_cpu_temp            : None,
                    get_inlet_temp          : None,
                    get_switch_temp         : None,
                    get_nic_temp         : None
            }
        }

    )
