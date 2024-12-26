#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# interface.py
# Python implementation of the Class interface
# Original author: rd@ruijie.com.cn
#
#######################################################
from .chassisbase import chassisbase
from .baseutil import baseutil
from .osutil import osutil
from .sensor import sensor
import sys
import time

def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton

@Singleton
class interface(object):
    __chas = None
    __error_ret = None
    val_list = {}

    def __init__(self):
        self.chas = chassisbase()
        self.__error_ret = -99999
        self.__na_ret = 'N/A'

    @property
    def na_ret(self):
        return self.__na_ret

    @na_ret.setter
    def na_ret(self, val):
        self.__na_ret = val

    @property
    def error_ret(self):
        return self.__error_ret

    @error_ret.setter
    def error_ret(self, val):
        self.__error_ret = val

    @property
    def chas(self):
        return self.__chas

    @chas.setter
    def chas(self, val):
        self.__chas = val

    def get_device_cfg(self):
        return True, self.chas.device_cfg

    # temp
    def get_temp_total_number(self):
        templist = self.chas.temp_list
        return len(templist)

    def get_temp_location(self, temp_name):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.get_location()

    def set_temp_location(self, temp_name, location):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.set_location(location)

    def set_temp_name(self, temp_name, name):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.set_name(name)

    def get_appoint_temp(self, temp_name):
        temp = self.chas.get_led_byname(temp_name)
        return temp.get_temp()

    def set_appoint_temp(self, temp_name, val):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.set_temp(val)

    def get_temp_mintemp(self, temp_name):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.get_mintemp()

    def set_temp_mintemp(self, temp_name, val):
        temp = self.chas.get_temp_byname(temp_name)
        return temp.set_mintemp(val)

    # led
    def get_led_total_number(self):
        ledlist = self.chas.led_list
        return len(ledlist)

    def get_led_color(self, led_name):
        led = self.chas.get_led_byname(led_name)
        return led.get_color()

    def set_led_color(self, led_name, color):
        led = self.chas.get_led_byname(led_name)
        return led.set_color(color)

    # psu
    def get_psu_total_number(self):
        psulist = self.chas.psu_list
        return len(psulist)

    def get_psus(self):
        psulist = self.chas.psu_list
        return psulist

    def get_psu_presence(self, psu_name):
        psu = self.chas.get_psu_byname(psu_name)
        return psu.present

    def get_psu_fru_info(self, psu_name):
        '''
                    {
                    "Name": "PSU1",
                    "SN": "serial_number_example",    # 'N/A'
                    "PN": "part_number_example",      # 'N/A'
                    "AirFlow": "B2F"                  # 'N/A'
                }
        '''
        psu = self.chas.get_psu_byname(psu_name)
        psu.get_fru_info()
        psu.get_AirFlow()

        dic = {}
        dic["Name"] = psu.name
        dic["SN"] = psu.productSerialNumber if (psu.productSerialNumber is not None) else self.na_ret
        dic["PN"] = psu.productPartModelName if (psu.productPartModelName is not None) else self.na_ret
        dic["AirFlow"] = psu.AirFlow if (psu.AirFlow is not None) else self.na_ret
        return dic

    def get_psu_status(self, psu_name):
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
        psu = self.chas.get_psu_byname(psu_name)
        return psu.psu_status_dict

    def get_psu_power_status(self, psu_name):
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
        psu = self.chas.get_psu_byname(psu_name)

        return psu.psu_power_status_dict

    def set_psu_fan_speed_pwm(self, psu_name, pwm):
        '''
            pmbus
            0x3a 看是否duty还是RPM
                if RPM:
                    改成 duty
                if duty:
                    0x3b    i2cset -f -y 0x0064  wp
        '''
        psu = self.chas.get_psu_byname(psu_name)
        return psu.set_fan_speed_pwm(pwm)

    def get_psu_fan_speed_pwm(self, psu_name):
        psu = self.chas.get_psu_byname(psu_name)
        return psu.get_fan_speed_pwm()

    def get_psu_info_all(self):
        """
                        {
                    "Number": 2,
                    "PSU1": {
                        "SN": "serial_number_example",  # 'N/A'
                        "PN": "part_number_example",    # 'N/A'
                        "AirFlow": "F2B",               # 'N/A'

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

        psus = self.get_psus()
        dict = {}
        dict['Number'] = len(psus)
        for psu in psus:
            dicttmp = self.get_psu_fru_info(psu.name)
            dicttmp.update(self.get_psu_status(psu.name))
            dicttmp.update(self.get_psu_power_status(psu.name))
            if self.get_psu_presence(psu.name) is True:
                dicttmp['Present'] = 'yes'
            else:
                dicttmp['Present'] = 'no'
            dict[psu.name] = dicttmp
        return dict

    def get_fans(self):
        fanlist = self.chas.fan_list
        return fanlist

    # fan
    def get_fan_total_number(self):
        fanlist = self.chas.fan_list
        if fanlist is None:
            return -1
        return len(fanlist)

    def get_fan_rotor_number(self, fan_name):
        fan = self.chas.get_fan_byname(fan_name)
        ret = fan.rotors
        if ret is None:
            return -1
        return ret

    def get_fan_speed(self, fan_name, rotor_index):
        fan = self.chas.get_fan_byname(fan_name)
        ret = fan.get_speed(rotor_index)
        if ret is None:
            return -1
        return ret

    def set_fan_speed(self, fan_name, rotor_index, speed):
        return -1

    def fan_speed_set_level(self, fan_name, rotor_index, level):
        fan = self.chas.get_fan_byname(fan_name)
        ret = fan.set_speed(rotor_index, level)
        if ret is True:
            return 0
        else:
            return -1

    def get_fan_speed_pwm(self, fan_name, rotor_index):
        fan = self.chas.get_fan_byname(fan_name)
        val = fan.get_speed_pwm(rotor_index)
        if val is None:
            return -1
        return val

    def set_fan_speed_pwm(self, fan_name, rotor_index, pwm):
        fan = self.chas.get_fan_byname(fan_name)
        if isinstance(pwm, str):
            rate = float(pwm.strip('%s'))
            speed = round(rate * 255 / 100)
        elif isinstance(pwm, int):
            speed = round(pwm * 255 / 100)
        elif isinstance(pwm, float):
            speed = round(pwm * 255 / 100)
        else:
            return -1
        ret = self.fan_speed_set_level(fan.name, rotor_index, speed)
        if ret == 0:
            return 0
        return -1

    def get_fan_watchdog_status(self):
        list_temp = self.chas.fan_list
        if list_temp:
            fan = list_temp[0]
            dic = fan.get_watchdog_status()
            if dic is None or dic["support"] == False:
                return "N/A"
            elif dic["open"] is False or dic["work_allow_set"] is True:
                return "Normal"
            elif dic["work_full"] is True:
                return "Abnormal"
            else:
                return "Abnormal"
        else:
            return "N/A"


    def enable_fan_watchdog(self, enable=True, timeout_sec=10):
        list_temp = self.chas.fan_list
        if list_temp:
            fan = list_temp[0]
            ret = fan.enable_watchdog(enable, timeout_sec)
            if ret is True:
                return 0
            else:
                return -1
        else:
            return -1

    def feed_fan_watchdog(self, pwm):
        list_temp = self.chas.fan_list
        if list_temp:
            fan_list = list_temp
            if fan_list is None:
                return -1
            for fan in fan_list:
                ret = fan.feed_watchdog(pwm)
                if ret is False:
                    return -1
            return 0
        else:
            return -1

    def set_fan_led(self, fan_name, color, blink = False):
        fan = self.chas.get_fan_byname(fan_name)
        ret = fan.set_led(color, blink)
        if ret is True:
            return 0
        else:
            return -1

    def get_fan_presence(self, fan_name):
        fan = self.chas.get_fan_byname(fan_name)
        return fan.get_presence()

    def get_fan_fru_info(self, fan_name):
        """
        Get specific fan's information
                    # Properties
                    "Name": "FAN1",
                    "SN": "serial_number_example",  # 'N/A'
                    "PN": "part_number_exampple",   # 'N/A'
                    "Rotors": 2,                    # -1
                    "AirFlow": "F2B",               # 'N/A'
                    "SpeedMin": 2000,               # -1
                    "SpeedMax": 30000               # -1
        """
        fan = self.chas.get_fan_byname(fan_name)
        fan.get_fru_info()
        fan.get_AirFlow()
        dic = {}
        dic["Name"] = fan.name
        dic["SN"] = fan.productSerialNumber
        if dic["SN"] is None:
            dic["SN"] = "N/A"
        dic["PN"] = fan.productPartModelName
        if dic["PN"] is None:
            dic["PN"] = "N/A"
        dic["Rotors"] = fan.rotors
        dic["AirFlow"] = fan.AirFlow
        if dic["AirFlow"] is None:
            dic["AirFlow"] = "N/A"
        dic["SpeedMin"] = fan.SpeedMin
        dic["SpeedMax"] = fan.SpeedMax
        return dic

    def get_product_fullname(self):
        return baseutil.get_product_fullname()

    def get_fan_status(self, fan_name):
        fan = self.chas.get_fan_byname(fan_name)
        if fan is None:
            return -1
        rotorlist = fan.rotor_list
        dir = {}
        for rotor in rotorlist:
            dir_val = {}
            if rotor.rotor_Running == True:
                dir_val['Running'] = 'yes'
            else:
                dir_val['Running'] = 'no'
            if rotor.rotor_HwAlarm == True:
                dir_val['HwAlarm'] = 'yes'
            else:
                dir_val['HwAlarm'] = 'no'
            dir_val['Speed'] = int(rotor.rotor_Speed.Value)
            dir[rotor.name] = dir_val
        return dir

    def get_fan_info_fru(self, fan_name):
        fan = self.chas.get_fan_byname(fan_name)
        fan.get_fru_info()
        fan.get_AirFlow()
        dic = {}
        dic["Name"] = fan.name
        dic["SN"] = fan.productSerialNumber
        if dic["SN"] is None:
            dic["SN"] = "N/A"
        dic["PN"] = fan.productPartModelName
        if dic["PN"] is None:
            dic["PN"] = "N/A"
        flag = self.get_fan_presence(fan_name)
        if flag is True:
            dic["Present"] = "yes"
        elif flag is False:
            dic["Present"] = "no"
        else:
            dic["Present"] = "N/A"
        dic["Rotors"] = fan.rotors
        dic["AirFlow"] = fan.AirFlow
        if dic["AirFlow"] is None:
            dic["AirFlow"] = "N/A"
        return dic

    def get_fan_info_rotor(self, fan_name):
        fan = self.chas.get_fan_byname(fan_name)
        if fan is None:
            return -1
        rotorlist = fan.rotor_list
        dir = {}
        for rotor in rotorlist:
            dir_val = {}
            if rotor.rotor_Running == True:
                dir_val['Running'] = 'yes'
            else:
                dir_val['Running'] = 'no'
            if rotor.rotor_HwAlarm == True:
                dir_val['HwAlarm'] = 'yes'
            else:
                dir_val['HwAlarm'] = 'no'
            speed_value = rotor.rotor_Speed.Value
            if speed_value is None:
                dir_val['Speed'] = self.error_ret
            else:
                dir_val['Speed'] = int(speed_value)
            if rotor.SpeedMin is None:
                dir_val['SpeedMin'] = self.error_ret
            else:
                dir_val['SpeedMin'] = rotor.SpeedMin
            if rotor.SpeedMax is None:
                dir_val['SpeedMax'] = self.error_ret
            else:
                dir_val['SpeedMax'] = rotor.SpeedMax

            dir[rotor.name] = dir_val
        return dir

    def get_fan_info_all(self):
        fanlist = self.chas.fan_list
        dic = {}
        dic['Number'] = len(fanlist)
        dic['WatchdogStatus'] = self.get_fan_watchdog_status()
        for fan in fanlist:
            dic[fan.name] = self.get_fan_info_fru(fan.name)
            dic[fan.name].update(self.get_fan_info_rotor(fan.name))
        return dic

    def chk_value_ready(self, prechk):
        if prechk is None or self.get_cpu_status() == prechk:
            return True
        return False

    def temp_test(self):
        templist = self.chas.temp_list
        dicret = {}

        for temp in templist:
            dic = {}
            tmp = temp.Value if self.chk_value_ready(temp.prechk) else None
            dic["Value"] = tmp if (tmp is not None) else self.error_ret
            dic["LowAlarm"] = temp.Min
            dic["HighAlarm"] = temp.Max
            dicret[temp.name] = dic
        return dicret

    # sensors
    def get_dcdc_all_info(self):
        dcdclist = self.chas.dcdc_list
        for dcdc in dcdclist:
            dicttmp = {}
            sensorname = "%s" % (dcdc.name)
            dicttmp['Min'] = dcdc.Min
            dicttmp['Max'] = dcdc.Max
            tmp = dcdc.Value
            if tmp is not None:
                dicttmp['Value'] = tmp
            else:
                dicttmp['Value'] = self.error_ret
            dicttmp['Unit'] = dcdc.Unit
            self.val_list[sensorname] = dicttmp
        return self.val_list
    def get_monitor_temp(self, name):
        templist = self.chas.temp_list
        temptmp = None
        for temp in templist:
            if temp.name == name:
                temptmp = temp

        dic = {}
        if temptmp is None:
            dic["Min"] = self.error_ret
            dic["Max"] = self.error_ret
            dic["Value"] = self.error_ret
            dic["Unit"] = self.error_ret
        else:
            dic["Min"] = temptmp.Min
            dic["Max"] = temptmp.Max
            tmp = temptmp.Value if self.chk_value_ready(temptmp.prechk) else None
            dic["Value"] = tmp if (tmp is not None) else self.error_ret
            dic["Unit"] = temptmp.Unit
        return dic

    def get_sensor_info(self):
        val_list = {}
        #temp
        templist = self.chas.temp_list
        for temp in templist:
            dic = {}
            dic["Min"] = temp.Min
            dic["Max"] = temp.Max
            tmp = temp.Value if self.chk_value_ready(temp.prechk) else None
            dic["Value"] = tmp if (tmp is not None) else self.error_ret
            dic["Unit"] = temp.Unit
            val_list[temp.name] = dic
        # fan
        fanlist = self.chas.fan_list
        for fan in fanlist:
            for rotor in fan.rotor_list:
                sensorname = "%s%s"%(fan.name, rotor.name)
                speed = {}
                speed['Min'] = rotor.rotor_Speed.Min
                speed['Max'] = rotor.rotor_Speed.Max
                speed['Value'] = rotor.rotor_Speed.Value if (rotor.rotor_Speed.Value is not None) else self.error_ret
                speed['Unit'] = rotor.rotor_Speed.Unit
                val_list[sensorname] = speed

        val_list.update(self.get_dcdc_all_info())

        # psu
        psulist = self.chas.psu_list
        for psu in psulist:
            val_list.update(psu.psu_sensor_info_dict)       

        return val_list

    #cpld
    def get_cpld_user_reg(self):
        cpld = self.chas.get_cpld_byname("BASE_CPLD")
        if cpld == None :
            return None
        else:
            return cpld.get_user_reg()

    def set_cpld_user_reg(self, value):
        if (isinstance (value, int) == False) :
            baseutil.logger_debug("value must int %s"%type(value))
            return -1
        if (int(value) < 0 or int(value) > 255) :
            baseutil.logger_debug("value must [0 - 255]")
            return -1
        cpld = self.chas.get_cpld_byname("BASE_CPLD")
        if cpld == None :
            baseutil.logger_debug("name BASE_CPLD not find")
            return -1
        if cpld.set_user_reg(value) == True:
            return 0
        else:
            return -1

    def set_cpld_console_owner(self, owner):
        """
        Set console I/O owner

        @param owner I/O owner of the console, either "cpu" or "bmc"

        @return 0 for success, -1 for failure
        """
        if (owner == None):
            baseutil.logger_debug("owner is None")
            return -1
        if (owner != "cpu" and owner != "bmc") :
            baseutil.logger_debug("owner is %s, must cpu or bmc"%owner)
            return -1
        cpld = self.chas.get_cpld_byname("BASE_CPLD")
        if cpld == None :
            baseutil.logger_debug("name BASE_CPLD not find")
            return -1
        if cpld.set_console_owner(owner) == True:
            return 0
        else:
            return -1

    def get_cpld_all_version(self):
        """
        Get version of all CPLDs' that can be read from BMC

        @return dict of CPLDs' version or None for failure.
                example outputs:
                {
                    "BASE_CPLD": "0.1",     # or "N/A" for read failure
                    "FAN_CPLD": "0.2"
                }
        """
        cpld_version = {}
        cpld_list = self.chas.cpld_list
        if cpld_list != None:
            count = 0
            for cpld in cpld_list:
                cpld_name = cpld.name
                count += 1
                if cpld_name is None:
                    cpld_name = "cpld%d" % count
                    baseutil.logger_debug("name of cpld is not configured, named: %s"%cpld_name)
                cpld_version[cpld_name] = cpld.get_version()
        if len(cpld_version) != 0:
            return cpld_version
        cpld_version = {
            "BASE_CPLD": "N/A",
            "FAN_CPLD": "N/A"
        }
        return cpld_version

    def get_bmc_productname(self):
        """
        Get product name

        @return product name string, e.g. AS13-32H-F-$(VENDOR_NAME), if error return "N/A"
        """
        bmc = self.chas.get_bmc_byname("master")
        if (bmc == None):
            baseutil.logger_debug("name bmc(master) not find")
            return "N/A"
        return bmc.get_productname()

    def call_bmc_diagcmd(self, cmdstr):
        """
        Call BMC diag comman func

        @return ret: 0 sucess , -1 fail
                outmsg: if success is out msg, or fail is err msg
        """
        if (cmdstr == None or cmdstr == ""):
            outmsg = "cmdstr is empty"
            baseutil.logger_debug(outmsg)
            return -1, outmsg
        bmc = self.chas.get_bmc_byname("master")
        if (bmc == None):
            outmsg = "name bmc(master) not find"
            baseutil.logger_debug(outmsg)
            return -1, outmsg
        baseutil.logger_debug("call cmdstr %s"%cmdstr)
        return bmc.call_diagcmd(cmdstr)

    def write_bios_version(self, flash, version):
        bios = self.chas.get_bios_byname("master")
        if bios == None :
            baseutil.logger_debug("name bios(master) not find")
            return -1
        baseutil.logger_debug("write bios version %s: %s" %(flash, version))
        return bios.set_bios_version(flash, version)

    def get_bios_version(self):
        bios = self.chas.get_bios_byname("master")
        if bios == None :
            baseutil.logger_debug("name bios(master) not find")
            return -1
        return bios.get_bios_version()

    def get_bios_status(self):
        bios = self.chas.get_bios_byname("master")
        if bios == None :
            baseutil.logger_debug("name bios(master) not find")
            return -1
        return bios.get_bios_boot_status()

    def monitor_cpu_host_watchdog(self, value):
        cpu = self.chas.get_cpu_byname("cpu")
        if cpu == None:
            baseutil.logger_debug("name cpu not find")
            return -1
        return cpu.set_cpu_host_watchdog(value)

    def get_bmc_mac_rov(self):
        """
        Get BMC mac rov

        @return ret: 0 sucess , -1 fail
                outmsg: if success is out msg, or fail is err msg
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            msg = "name master not find"
            baseutil.logger_debug(msg)
            return -1, msg
        return bmc.get_mac_rov()

    def reset_bmc_devices(self):
        """
        Reset devices
        @return ret: 0 sucess or sikp, -1 fail
                outmsg: if success is out msg, or fail is err msg
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            msg = "name master not find"
            baseutil.logger_debug(msg)
            return -1, msg
        dev_list = bmc.reset_dev_list
        if dev_list == None or len(dev_list) == 0:
            msg = "skip resetting devices"
            baseutil.logger_debug(msg)
            return 0, msg
        failed_list = []
        ret = 0
        for dev in dev_list:
            if self.reset_evst_sensor(dev) != 0:
                failed_list.append(dev)
                ret = -1
        msg = "failed to reset %d devices(%s)" % (len(failed_list), failed_list)
        baseutil.logger_debug(msg)
        return ret, msg

    def get_bmc_next_boot(self):
        """
        Get next booting flash of BMC

        @return 'master'/'slave' on success, "N/A" for failure
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return "N/A"
        return bmc.get_next_boot()

    def get_bmc_reset_num(self):
        """
        Get BMC reset num
        @return BMC reset num on success, -1 for failure
        """ 
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            msg = "name master not find"
            baseutil.logger_debug(msg)
            return -1
        return bmc.get_bmc_reset_num()

    def set_bmc_next_boot(self, flash):
        """
        Set flash from which next BMC boot

        @param flash Booting flash of BMC, "master" or "slave"

        @return 0 on success, -1 for failure
        """
        if flash == None or (flash != "master" and flash != "slave"):
            baseutil.logger_debug("parameter flash illegal, should be [master|slave]")
            return -1
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return -1
        return bmc.set_next_boot(flash)

    def reboot_bmc(self):
        """
        Reboot running BMC
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return -1
        return bmc.reboot()

    def get_bmc_info(self):
        """
        Get BMC info

        @return dict of BMC info or None for failure
                    "Version": "1.1.1", # "N/A"
                    "Flash": "master",  # "N/A"
                    "Next": "master"    # "N/A"
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return "N/A"
        return bmc.get_info()

    def get_bmc_version_all(self):
        """
        @return dict of BMCs
                {
                    "MasterVersion": "1.1.1",   # "N/A"
                    "SlaveVersion": "1.1.1"     # "N/A"
                }
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return "N/A"
        return bmc.get_version_all()

    def bmc_execute_command(self, cmd_str):
        ret, output = osutil.command(cmd_str)
        if ret:
            baseutil.logger_debug("execute %s command failed" %(cmd_str))
        return ret, output

    def get_cpu_status(self):
        """
        Get CPU current status.

        @return 'S0', ..., 'S5', or 'N/A' for failure
        """
        cpu = self.chas.get_cpu_byname("cpu")
        if cpu == None:
            baseutil.logger_debug("name cpu not find")
            return 'N/A'
        return cpu.get_state()

    def get_cpu_reset_num(self):
        """
        Get CPU reset num
        @return CPU reset num on success, -1 for failure
        """
        cpu = self.chas.get_cpu_byname("cpu")
        if cpu == None:
            msg = "name cpu not find"
            baseutil.logger_debug(msg)
            return -1
        return cpu.get_cpu_reset_num()

    def get_cpu_last_reset(self):
        """
        Get last CPU reset type, WARM/COLD.
        @return Last CPU reset type, WARM/COLD, N/A for failure
        """
        cpu = self.chas.get_cpu_byname("cpu")
        if cpu == None:
            msg = "name cpu not find"
            baseutil.logger_debug(msg)
            return "N/A"
        return cpu.get_last_reset()

    def set_machine_power_cycle(self):
        """
        Set machine power status.
        @return 0 on success, -1 for failure
        """
        cpu = self.chas.get_cpu_byname("cpu")
        if cpu == None:
            msg = "name cpu not find"
            baseutil.logger_debug(msg)
            return -1
        return cpu.set_machine_power_cycle()

    def set_misc_system_led(self, color, blink):
        """
        Set system LED color, system LED indicates status of the whole system

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return -1
        return bmc.set_system_led(color, blink)

    def get_misc_system_power_led_available(self):
        """
        Get system power LED availability

        @return True if available, False otherwise.
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return False
        return bmc.get_system_power_led_available()

    def set_misc_system_power_led(self, color, blink):
        """
        Set system power LED color, power LED indicates PSU, DC/DC status

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return -1
        return bmc.set_system_power_led(color, blink)

    def set_misc_system_fan_led(self, color, blink):
        """
        Set system fan LED color

        @param color The color of system fan LED, "green"/"yellow"/"off"
        @param blink True for blinking, False for steady

        @return 0 for success, -1 for failure
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return -1
        return bmc.set_system_fan_led(color, blink)

    def get_bmc_sys_eeprom(self):
        """
        Get SYSEEPROM
        @return SYSEEPROM content dict or None for failure.
        """
        bmc = self.chas.get_bmc_byname("master")
        if bmc == None:
            baseutil.logger_debug("name master not find")
            return None
        return bmc.get_sys_eeprom()

    def get_cpld_last_upgrade_result(self):
        """
        Get last upgrade result for CPLD\\BIOS\\FPGA refresh
        @return Get last upgrade content dict or None for failure.
        """
        cpld = self.chas.get_cpld_byname("BASE_CPLD")
        if cpld == None :
            baseutil.logger_debug("name BASE_CPLD not find")
            return -1, None
        return cpld.get_last_upgrade_result()

    def upgrade_8367_fw(self, bin):
        """
        upgrade fw 8367
        @param bin for 8367

        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return -1, output
        return fpga_fw.upgrade_fw_8367(bin)

    def get_fw_8367_version(self):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return -1, output
        return fpga_fw.get_fw_8367_version()

    def add_spi_flash(self, flash_name, flash_chip=None):
        """
        add extend spi-flash to device
        @return True for success, False for failure.
        """
        flash = self.chas.get_flash_byname(flash_name)
        if flash == None:
            return False
        return flash.add_flash(flash_chip)

    def remove_spi_flash(self, flash_name, flash_chip=None):
        """
        remove extend spi-flash to device
        @return True for success, False for failure.
        """
        flash = self.chas.get_flash_byname(flash_name)
        if flash == None:
            return False
        return flash.remove_flash(flash_chip)

    def remove_spi_flash_retry(self, flash_name, flash_chip = None, times = 3):
        """
        retry remove extend spi-flash to device
        @return True for success, False for failure.
        @time retry time
        """
        count = 0
        while True:
            if self.remove_spi_flash(flash_name, flash_chip) == True or count == times:
                break
            else:
                output = "remove device %s failed, retry %d time" %(flash_name, count)
                baseutil.logger_debug(output)
                count = count + 1
                time.sleep(10)
        if count == times:
            return False
        return True

    def upgrade_fpga_fw(self, bin):
        """
        upgrade fw fpga
        @param bin for fpga
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = -1
        is_need_exit = 0
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("upgradefpga") == 0:
            output = "ERR: not support upgrade fpga, and not support get md5sum"
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash("fpga") == False:
                output = "add fpga channel failed"
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.upgrade_fw_fpga(bin)
        except Exception as e:
            baseutil.logger_debug("upgrade_fpga_fw err: %s" %str(e))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry("fpga") == False:
                    baseutil.logger_debug("remove fpga channel failed")
                else:
                    baseutil.logger_debug("remove fpga channel success")
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def get_fpga_md5sum(self):
        """
        get fpga md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        ret = -1
        is_need_exit = 0
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("upgradefpga") == 0:
            output = "ERR: not support upgrade fpga, and not support get md5sum"
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash("fpga") == False:
                output = "add fpga channel failed"
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.get_fpga_md5sum()
        except Exception as e:
            baseutil.logger_debug("get_fpga_md5sum err: %s" %str(e))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry("fpga") == False:
                    baseutil.logger_debug("remove fpga channel failed")
                else:
                    baseutil.logger_debug("remove fpga channel success")
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def upgrade_5387_fw(self, bin):
        """
        upgrade fw 5387
        @param bin for 5387
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_vlanswitch_fw("5387", bin)

    def get_fw_5387_version(self):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.get_fw_vlanswitch_version("5387")

    def upgrade_88e6321_fw(self, bin):
        """
        upgrade fw 88e6321
        @param bin for 88e6321
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_vlanswitch_fw("88e6321", bin)

    def get_fw_88e6321_version(self):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.get_fw_vlanswitch_version("88e6321")

    def upgrade_bcm53134_fw(self, bin):
        """
        upgrade fw bcm53134
        @param bin for bcm53134
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_vlanswitch_fw("bcm53134", bin)

    def get_fw_bcm53134_version(self):
        """
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.get_fw_vlanswitch_version("bcm53134")

    def upgrade_rtl8372_fw(self, bin):
        """
        upgrade fw rtl8372
        @param bin for rtl8372
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_switch_fw("rtl8372", bin)

    def get_rtl8372_md5sum(self):
        """
        get rtl8372 md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        return self.get_switch_md5sum("rtl8372")

    def upgrade_vlanswitch_fw(self, fw_type, bin):
        """
        upgrade fw 88e6321/5387/bcm53134
        @param bin for 5387/88e6321/bcm53134
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = -1
        is_need_exit = 0
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("upgrade%s" % fw_type) == 0:
            output = "ERR: not support upgrade %s" % fw_type
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash(fw_type) == False:
                output = "add %s channel failed" % fw_type
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.upgrade_fw_vlanswitch(fw_type, bin)
        except Exception as e:
            baseutil.logger_debug("upgrade_%s_fw err: %s" %(fw_type, str(e)))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry(fw_type) == False:
                    baseutil.logger_debug("remove %s channel failed" % fw_type)
                else:
                    baseutil.logger_debug("remove %s channel success" % fw_type)
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def get_fw_vlanswitch_version(self, fw_type):
        """
        get fw 88e6321/5387/bcm53134 version
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = -1
        is_need_exit = 0
        output = ""
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("get%sversion" % fw_type) == 0:
            output = "ERR: not support get %s version" % fw_type
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash(fw_type) == False:
                output = "add %s channel failed" % fw_type
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.get_fw_vlanswitch_version(fw_type)
        except Exception as e:
            output = "get_%s_md5sum err: %s" % (fw_type,str(e))
            baseutil.logger_debug(output)
        except KeyboardInterrupt:
            output = "code exit because KeyboardInterrupt"
            baseutil.logger_debug(output)
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry(fw_type) == False:
                    baseutil.logger_debug("remove %s channel failed" % fw_type)
                else:
                    baseutil.logger_debug("remove %s channel success" % fw_type)
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def upgrade_mac_fw(self, bin):
        """
        upgrade fw mac
        @param bin for mac
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_switch_fw("mac", bin)

    def upgrade_atlas0_fw(self, bin):
        """
        upgrade fw atlas0
        @param bin for atlas0
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_switch_fw("atlas0", bin)

    def upgrade_atlas1_fw(self, bin):
        """
        upgrade fw atlas1
        @param bin for atlas1
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        return self.upgrade_switch_fw("atlas1", bin)

    def upgrade_switch_fw(self, fw_type, bin):
        """
        upgrade fw mac/atlas/rtl8372
        @param bin for mac/atlas/rtl8372
        @return (0, outputs) for success, (-1, outputs) for failure.
        """
        ret = -1
        is_need_exit = 0
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("upgrade%s" % fw_type) == 0:
            output = "ERR: not support upgrade %s" % fw_type
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash(fw_type) == False:
                output = "add %s channel failed" % fw_type
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.upgrade_fw_switch(fw_type, bin)
        except Exception as e:
            baseutil.logger_debug("upgrade_switch_fw err: %s" %str(e))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry(fw_type) == False:
                    baseutil.logger_debug("remove %s channel failed" % fw_type)
                else:
                    baseutil.logger_debug("remove %s channel success" % fw_type)
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def get_mac_md5sum(self):
        """
        get mac md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        return self.get_switch_md5sum("mac")

    def get_atlas0_md5sum(self):
        """
        get atlas0 md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        return self.get_switch_md5sum("atlas0")

    def get_atlas1_md5sum(self):
        """
        get atlas1 md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        return self.get_switch_md5sum("atlas1")

    def get_switch_md5sum(self, fw_type):
        """
        get mac/atlas/rtl8372 md5sum
        @return (0, md5sum) for success, (-1, msg) for failure.
        """
        ret = -1
        is_need_exit = 0
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return ret, output
        if fpga_fw.get_operate_capacity("upgrade%s" % fw_type) == 0:
            output = "ERR: not support upgrade %s, and not support get md5sum" % fw_type
            baseutil.logger_debug(output)
            return ret, output
        firmware = self.chas.get_firmware_byname("firmware")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret, output
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
            baseutil.logger_debug(output)
            return ret, output
        try:
            if self.add_spi_flash(fw_type) == False:
                output = "add mac channel failed"
                baseutil.logger_debug(output)
            else:
                ret, output = fpga_fw.get_switch_md5sum(fw_type)
        except Exception as e:
            baseutil.logger_debug("get_switch_md5sum err: %s" %str(e))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if self.remove_spi_flash_retry(fw_type) == False:
                    baseutil.logger_debug("remove %s channel failed" % fw_type)
                else:
                    baseutil.logger_debug("remove %s channel success" % fw_type)
                firmware.judge_fw_channel_exist("all", True)
            firmware.remove_lock()
        return ret, output

    def upgrade_bios_fw(self, flash, image):
        """
        Program BIOS flash with specific image
        @param flash 'master' or 'slave' BIOS flash
        @param image Absolute path of the BIOS image file
        @return 0 for success, -1 for failure
        """
        ret = -1
        is_need_exit = 0
        firmware = self.chas.get_firmware_byname("firmware")
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if firmware == None:
            output = "name firmware not find"
            baseutil.logger_debug(output)
            return ret
        bioscsfirst = fpga_fw.get_operate_capacity("bioscsfirst")
        if bioscsfirst == 1:
            # store original bios chip select
            orig_cs = firmware.get_bios_next_boot("get_orig_cs")
            if orig_cs != "master" and orig_cs != "slave":
                baseutil.logger_debug("get current bios cs failed: %s" % orig_cs)
                return ret
        if firmware.set_me_status("recovery"):
            return ret
        if firmware.add_lock() == -1:
            output = "add fw lock failed"
        try:
            if bioscsfirst == 1:
                add_spi_ret = self.add_spi_flash("bios", flash)
            else:
                add_spi_ret = self.add_spi_flash("bios")
            if add_spi_ret == False:
                output = "add bios channel failed"
                baseutil.logger_debug(output)
            else:
                ret = firmware.program_bmc_bios("bios", flash, image)
        except Exception as e:
            baseutil.logger_debug("upgrade_bios_fw err: %s" %str(e))
        except KeyboardInterrupt:
            baseutil.logger_debug("code exit because KeyboardInterrupt")
            is_need_exit = 1
        finally:
            if is_need_exit == 0:
                if bioscsfirst == 1:
                    remove_spi_ret = self.remove_spi_flash_retry("bios", orig_cs)
                else:
                    remove_spi_ret = self.remove_spi_flash_retry("bios")
                if remove_spi_ret == False:
                    baseutil.logger_debug("remove bios channel failed")
                else:
                    baseutil.logger_debug("remove bios channel success")
                firmware.judge_fw_channel_exist("all", True)
            firmware.set_me_status("reset")
            firmware.remove_lock()
        return ret

    def write_uboot_version(self, flash, version):
        """
        Write uboot version

        @return 0 on success, -1 for failure
        """
        uboot = self.chas.get_uboot_byname("master")
        if uboot == None :
            baseutil.logger_debug("name uboot(master) not find, not support")
            return -1
        return uboot.set_uboot_version(flash, version)

    def get_uboot_version(self):
        """
        Get uboot version

        @return
            { "MasterUbootVersion":"N/A",
              "SlaveUbootVersion":"N/A",
            }
        """
        uboot = self.chas.get_uboot_byname("master")
        if uboot == None :
            baseutil.logger_debug("name uboot(master) not find, not support")
            return None
        return uboot.get_uboot_version()

    def get_uboot_status(self):
        """
        Get lastest UBOOT boot status, include boot_flash and result

        @return Dict of UBOOT boot status or None for failure
                Example:
                {
                    "Flash": "master",      # "slave" or 'N/A'
                    "Result": "success"     # "failed" or 'N/A'
                }
        """
        uboot = self.chas.get_uboot_byname("master")
        if uboot == None :
            baseutil.logger_debug("name uboot(master) not find, not support")
            return None
        return uboot.get_uboot_boot_status()

    def get_uboot_next_boot(self):
        """
        Get next booting flash of UBOOT

        @return "master"/"slave" on success, "N/A" for failure
        """
        uboot = self.chas.get_uboot_byname("master")
        if uboot == None :
            baseutil.logger_debug("name uboot(master) not find, not support")
            return None
        return uboot.get_uboot_next_boot()

    def set_uboot_next_boot(self, flash):
        """
        Set flash from which next BIOS boot

        @param flash Booting flash of BIOS, "master" or "slave"

        @return 0 on success, -1 for failure
        """
        uboot = self.chas.get_uboot_byname("master")
        if uboot == None :
            baseutil.logger_debug("name uboot(master) not find, not support")
            return -1
        return uboot.set_uboot_next_boot(flash)

    def get_host_cpu_power_force_control_status(self):
        """
        @return host cpu power force control, 1 for enable, 0 for disable, -1 for failure
        """
        current_status = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return current_status
        return fpga_fw.get_host_cpu_power_force_control_status()

    def enable_host_cpu_power_force_control(self,enable):
        """
        @status 1 enable, 0 disable.
        @return 0 for success, -1 for failure.
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        try:
            if isinstance(enable,int):
                val = enable
            elif enable.isdigit() == True:
                val = int(enable.strip('\n'))
            else:
                val = enable
        except Exception as e:
            baseutil.logger_debug("str transform to int err: %s" %str(e))
            return return_val
        if val != 1 and val != 0: #on off
            output = "ERR: illegal parameter :%s  %s" % (val, enable)
            baseutil.logger_debug("End enable power force control,result=%s" % output)
            return return_val
        return fpga_fw.enable_host_cpu_power_force_control(val)

    def get_ssd_power_status(self):
        """
        @return ssd power status, on/off, N/A for failure
        """
        current_status = "N/A"
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return current_status
        return fpga_fw.get_ssd_power_status()

    def set_ssd_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure.
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        if status != "on" and status != "off": #on off
            output = "ERR: illegal parameter : %s" % status
            baseutil.logger_debug("End set ssd power status,result=%s" % output)
            return return_val
        return fpga_fw.set_ssd_power(status)

    def set_bmcemmc_power_cycle(self):
        """
        Power cycle bmc emmc.
        @return 0 on success, -1 for failure
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        return fpga_fw.set_bmcemmc_power_cycle()

    def set_cpuemmc_power_cycle(self):
        """
        Power cycle cpu emmc.
        @return 0 on success, -1 for failure
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        return fpga_fw.set_cpuemmc_power_cycle()

    def get_td4_power_status(self):
        """
        @return td4 power status, on/off, N/A for failure
        """
        current_status = "N/A"
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return current_status
        return fpga_fw.get_td4_power_status()

    def set_td4_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure.
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        if status != "on" and status != "off": #on off
            output = "ERR: illegal parameter : %s" % status
            baseutil.logger_debug("End set TD4 power status,result=%s" % output)
            return return_val
        return fpga_fw.set_td4_power(status)

    def get_port_power_status(self):
        """
        @return port power status, on/off, N/A for failure
        """
        current_status = "N/A"
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return current_status
        return fpga_fw.get_port_power_status()

    def set_port_power(self,status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure.
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        if fpga_fw.get_operate_capacity("gettd4powerstatus") == 1:
            mac_status = self.get_td4_power_status()
            if mac_status != "on":
                baseutil.logger_debug("mac status err,current status: %s" % mac_status)
                return return_val
        if status != "on" and status != "off": #on off
            output = "ERR: illegal parameter : %s" % status
            baseutil.logger_debug("End set TD4 power status,result=%s" % output)
            return return_val
        return fpga_fw.set_port_power(status)

    def get_netcard_power_status(self, netcard):
        """
        @return netcard power status, on/off, N/A for failure
        """
        current_status = "N/A"
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return current_status
        return fpga_fw.get_netcard_power_status(netcard)

    def set_netcard_power(self,netcard, status):
        """
        @status on power on, off power off.
        @return 0 for success, -1 for failure.
        """
        return_val = -1
        fpga_fw = self.chas.get_fpga_fw_byname("fpga_fw")
        if fpga_fw == None:
            output = "name fpga_fw not find"
            baseutil.logger_debug(output)
            return return_val
        if status != "on" and status != "off": #on off
            output = "ERR: illegal parameter : %s" % status
            baseutil.logger_debug("End set %s power status,result=%s" % (netcard, output))
            return return_val
        return fpga_fw.set_netcard_power(netcard, status)

    def get_evst_info(self, name):
        devlist = self.chas.devmon_list
        for dev in devlist:
            tmplist = {}
            if dev.Name == name:
                tmp = dev.Value if self.chk_value_ready(dev.prechk) else None
                tmplist['Value'] = tmp if tmp is not None else self.error_ret
                tmplist['Expects'] = dev.Expects
                tmplist['RW'] = dev.RW
                tmplist['Decoder'] = dev.Decoder
                tmplist['Descr'] = dev.Descr
                return tmplist
        return None

    def reset_evst_sensor(self, name):
        devlist = self.chas.devmon_list
        for dev in devlist:
            if dev.Name == name:
                if self.chk_value_ready(dev.prechk):
                    return dev.reset()
        return -1

    def get_evst_info_all(self):
        dict = {}
        devlist = self.chas.devmon_list
        dict['Number'] = len(devlist)
        for dev in devlist:
            dicttmp = self.get_evst_info(dev.Name)
            dict[dev.Name] = dicttmp
        return dict
