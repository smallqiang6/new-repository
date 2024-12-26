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
from plat_hal.interface import interface
from hal.hal_misc import HalMisc
from hal.hal_firmware import HalFirmware
from hal.hal_bmc import HalBmc
from hal.hal_cpu import HalCPU

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

def misc():
    r'''test misc '''
    pass

def intf():
    r'''test intf '''
    pass

def firmware():
    r'''test firmware '''
    pass

def bmc():
    r'''test bmc'''
    pass

def cpu():
    r'''test cpu'''
    pass

int_case = interface()
misc_case = HalMisc()
firmware_case = HalFirmware()
bmc_case = HalBmc()
cpu_case = HalCPU()

#misc operation
def get_ssd_power_status():
    r'''ssd  get power status '''
    print("=================get ssd power status======================")
    print(misc_case.get_ssd_power_status())

def set_ssd_power_status(status):
    r'''ssd  set power status '''
    print("=================set ssd power status======================")
    print(misc_case.set_ssd_power_status(status))

def get_host_cpu_power_force_control_status():
    r'''power force control get status '''
    print("=================get power force control power status======================")
    print(misc_case.get_host_cpu_power_force_control_status())

def enable_host_cpu_power_force_control(enable):
    r'''power force control set status '''
    print("=================set power force control power status======================")
    print(misc_case.enable_host_cpu_power_force_control(enable))

def get_switch_chip_power_status():
    r'''mac  get power status '''
    print("=================get switch chip power status======================")
    print(misc_case.get_switch_chip_power_status())

def set_switch_chip_power_status(status):
    r'''mac  set power status '''
    print("=================set switch chip power status======================")
    print(misc_case.set_switch_chip_power_status(status))

def get_switch_port_power_status():
    r'''port  get power status '''
    print("=================get switch port power status======================")
    print(misc_case.get_switch_port_power_status())

def set_switch_port_power_status(status):
    r'''port  set power status '''
    print("=================set switch  port power status======================")
    print(misc_case.set_switch_port_power_status(status))

def get_host_cpu_power_status():
    r'''cpu  get power status '''
    print("=================get cpu power status======================")
    print(misc_case.get_host_cpu_power_status())

def set_host_cpu_power(status):
    r'''cpu  set cpu power '''
    print("=================set cpu power status======================")
    print(misc_case.set_host_cpu_power(status))

def set_system_fan_led(color, blink=False):
    r'''led  set system fan led
    @param color The color of system fan LED, "green"/"yellow"/"off"
    @param blink True for blinking, False for steady
    '''
    print("=================set system fan led======================")
    print(misc_case.set_system_fan_led(color, blink))

def set_system_led(color, blink=False):
    r'''led  set system led
    @param color The color of system fan LED, "green"/"yellow"/"off"
    @param blink True for blinking, False for steady
    '''
    print("=================set system led======================")
    print(misc_case.set_system_led(color, blink))

def system_power_led_available():
    r'''led  get system power led availability '''
    print("=================get system power led availability======================")
    print(misc_case.system_power_led_available())

def set_system_power_led(color, blink=False):
    r'''led  set system power led
    @param color The color of system fan LED, "green"/"yellow"/"off"
    @param blink True for blinking, False for steady
    '''
    print("=================set system power led======================")
    print(misc_case.set_system_power_led(color,blink))

def set_location_led(cmd):
    r'''led  set location led
    @param cmd Control command, "on"/"off"
    '''
    print("=================set location led======================")
    print(misc_case.set_location_led(cmd))

def get_location_led():
    r'''led  get location led '''
    print("=================get location led======================")
    print(misc_case.get_location_led())

def get_uboot_boot_status():
    r'''get uboot boot status'''
    print("=================get uboot boot status======================")
    print(misc_case.get_uboot_boot_status())

def get_system_airflow():
    r'''get system airflow'''
    print("=================get system airflow======================")
    print(misc_case.get_system_airflow())

def get_bmc_boot_status():
    r'''get bmc boot status'''
    print("=================get bmc boot status======================")
    print(misc_case.get_bmc_boot_status())

def execute_command(cmd):
    r'''execute hal test'''
    print("=================execute_command %s======================" % cmd)
    ret_exec, log_exec = misc_case.execute_command(cmd)
    if ret_exec:
        print("failed, %s" % log_exec)
    else:
        print("result: %s" % log_exec)

def get_cpld_version():
    r'''get cpld version'''
    print("=================get cpld version======================")
    print(misc_case.get_cpld_version())

#intf
def power_machine_cycle():
    r'''power machine cycle '''
    print(int_case.set_machine_power_cycle())

def set_uboot_version(flash, version):
    r'''set uboot version'''
    print("=================set uboot version======================")
    if (flash != "master") and  (flash != "slave"):
        print("flash must be master or slave. current %s" %flash)
    else:
        print(int_case.write_uboot_version(flash, version))

def get_uboot_version():
    r'''get uboot version'''
    print("=================get uboot version======================")
    print(int_case.get_uboot_status())
    print(int_case.get_uboot_version())

def get_bmc_reset_num():
    r'''get bmc reset num'''
    print("=================get bmc reset num======================")
    print(int_case.get_bmc_reset_num())

def get_bios_version():
    r'''get bios version'''
    print("=================get bios version======================")
    print(int_case.get_bios_status())
    print(int_case.get_bios_version())

def set_bios_version(flash, version):
    r'''set bios version'''
    print("=================set bios version======================")
    if (flash != "master") and  (flash != "slave"):
        print("flash must be master or slave. current %s" %flash)
    else:
        print(int_case.write_bios_version(flash, version))

#firmware
def get_uboot_next_boot():
    r'''get uboot next boot '''
    print("=================get uboot next boot======================")
    print(firmware_case.get_uboot_next_boot())

def set_uboot_next_boot(flash):
    r'''set uboot next boot'''
    print("=================set uboot next boot======================")
    if (firmware_case.set_uboot_next_boot(flash) == 0):
        print("set uboot next boot: %s success" %flash)
    else:
        print("set uboot next boot: %s failed" %flash)

def get_bios_next_boot():
    r'''get bios next boot '''
    print("=================get bios next boot======================")
    print(firmware_case.get_bios_next_boot())

def set_bios_next_boot(flash):
    r'''set bios next boot'''
    print("=================set bios next boot======================")
    if (firmware_case.set_bios_next_boot(flash) == 0):
        print("set bios next boot: %s success" %flash)
    else:
        print("set bios next boot: %s failed" %flash)

#bmc
def get_info():
    r'''get bmc info'''
    print("=================get bmc info======================")
    print(bmc_case.get_info())

def get_version():
    r'''get bmc version'''
    print("=================get bmc version======================")
    print(bmc_case.get_version_all())

def get_next_boot():
    r'''get bmc next boot'''
    print("=================get bmc next boot======================")
    print(bmc_case.get_next_boot())

def get_status():
    r'''get bmc status'''
    print("=================get bmc status======================")
    dict_info = bmc_case.get_status()
    if dict_info == None :
        print("failed to get bmc status")
        exit()
    dict_info_keys = list(dict_info.keys())
    dict_info_keys.sort()
    for item in dict_info_keys:
        print(item)
        dict_info_sub = dict_info[item]
        dict_info_sub_keys = list(dict_info_sub.keys())
        dict_info_sub_keys.sort()
        for it in dict_info_sub_keys:
            print("%s :"%(it))
            print("%s"%(dict_info_sub[it]))
        print("\n")

def set_next_boot(flash):
    r'''set bmc next boot'''
    print("=================set bmc next boot======================")
    if (bmc_case.set_next_boot(flash) == 0):
        print("set bmc next boot: %s success" %flash)
    else:
        print("set bmc next boot: %s failed" %flash)

def reboot():
    r'''reboot bmc'''
    print("=================reboot bmc======================")
    str_input = input("Are you sure reboot bmc ? [y/n]:")
    if str_input.lower() == "y" or str_input.lower() == "yes" :
        print(bmc_case.reboot())

def get_last_reset():
    r'''get cpu last reset type'''
    print("=================get cpu last reset type======================")
    print(cpu_case.get_last_reset())

if __name__ == '__main__':
    clival.Fire(
        {
            misc: {
                    get_ssd_power_status         : None,
                    set_ssd_power_status         : None,
                    get_switch_chip_power_status : None,
                    set_switch_chip_power_status : None,
                    get_switch_port_power_status : None,
                    set_switch_port_power_status : None,
                    get_host_cpu_power_status    : None,
                    set_host_cpu_power           : None,
                    get_host_cpu_power_force_control_status : None,
                    enable_host_cpu_power_force_control     : None,
                    set_system_fan_led           : None,
                    set_system_led               : None,
                    system_power_led_available   : None,
                    set_system_power_led         : None,
                    set_location_led             : None,
                    get_location_led             : None,
                    get_uboot_boot_status        : None,
                    get_system_airflow           : None,
                    get_bmc_boot_status          : None,
                    execute_command              : None,
                    get_cpld_version             : None
                 },
            intf: {
                    power_machine_cycle  : None,
                    set_uboot_version    : None,
                    get_uboot_version    : None,
                    get_bmc_reset_num    : None,
                    get_bios_version     : None,
                    set_bios_version     : None
                },
            firmware: {
                    get_uboot_next_boot  : None,
                    set_uboot_next_boot  : None,
                    get_bios_next_boot   : None,
                    set_bios_next_boot   : None
                },
            bmc: {
                    get_info             : None,
                    get_version          : None,
                    get_next_boot        : None,
                    get_status           : None,
                    set_next_boot        : None,
                    reboot               : None
            },
            cpu: {
                    get_last_reset       : None
            }
        }

    )
