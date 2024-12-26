#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# chassisbase.py
# Python implementation of the Class chassisbase
# Original author: rd@ruijie.com.cn
#
#######################################################
from .dcdc import dcdc
from .psu import psu
from .led import led
from .temp import temp
from .fan import fan
from .card import card
from .sensor import sensor
from .cpld import cpld
from .bios import bios
from .bmc import bmc
from .cpu import cpu
from .baseutil import baseutil
from .fpga_fw import fpga_fw
from .flash import flash
from .flash_v2 import flash_v2
from .firmware import firmware
from .uboot import uboot
from .devmon import devmon

class chassisbase:
    __device_cfg = None
    __psu_list  = []
    __led_list  = []
    __temp_list = []
    __fan_list  = []
    __card_list = []
    __sensor_list = []
    __dcdc_list = []
    __cpld_list = []
    __bios_list = []
    __bmc_list  = []
    __cpu = None
    __fpga_fw = None
    __firmware = None
    __uboot = None

    def __init__(self, conftype = 0, conf = None):
        # type: (object, object, object) -> object
        """
        init chassisbase as order

        type  = 0  use default conf, maybe auto find by platform
        type  = 1  use given conf,  conf is not None

        BITMAP
              bit 16
                      bit 0    PSU
                      bit 1    LED
                      bit 2    TEMP
                      bit 3    fan
                      bit 4    card
                      bit 5    sensor
        """
        __confTemp = None

        if conftype == 0:
            # user
            __confTemp = baseutil.get_config()
        elif conftype == 1:
            __confTemp = conf
        self.device_cfg = __confTemp

        #psu
        psutemp = []
        psuconfig = __confTemp.get('psus')
        for i in range(len((psuconfig))):
            psu1  = psu(psuconfig[i])
            psutemp.append(psu1)
        self.psu_list = psutemp

        #led
        ledtemp = []
        ledconfig = __confTemp.get('leds')
        for i in range(len((ledconfig))):
            led1  = led(ledconfig[i])
            ledtemp.append(led1)
        self.led_list = ledtemp
        #temp
        temptemp = []
        tempconfig = __confTemp.get('temps')
        for i in range(len((tempconfig))):
            temp1  = temp(tempconfig[i])
            temptemp.append(temp1)
        self.temp_list = temptemp
        #fan
        fantemp = []
        fanconfig = __confTemp.get('fans')
        for i in range(len((fanconfig))):
            fan1  = fan(fanconfig[i])
            fantemp.append(fan1)
        self.fan_list = fantemp
        #card
        cardtemp = []
        cardconfig = __confTemp.get('cards')
        for i in range(len((cardconfig))):
            card1  = card(cardconfig[i])
            cardtemp.append(card1)
        self.card_list = cardtemp

        #dcdc
        dcdctemp = []
        dcdcconfig = __confTemp.get('dcdc')
        for i in dcdcconfig:
            dcdc1 = sensor(i)
            dcdctemp.append(dcdc1)
        self.dcdc_list = dcdctemp

        #cpld
        cpldtemp = []
        cpldconfig = __confTemp.get('cplds')
        for i in range(len((cpldconfig))):
            cpld1 = cpld(cpldconfig[i])
            cpldtemp.append(cpld1)
        self.cpld_list = cpldtemp

        #bios
        biostemp = []
        biosconfig = __confTemp.get('bioss')
        for i in range(len((biosconfig))):
            bios1 = bios(biosconfig[i])
            biostemp.append(bios1)
        self.bios_list = biostemp

        #bmc
        bmctemp = []
        bmcconfig = __confTemp.get('bmcs')
        for i in range(len((bmcconfig))):
            bmc1 = bmc(bmcconfig[i])
            bmctemp.append(bmc1)
        self.bmc_list = bmctemp

        #cpu
        cpuconfig = __confTemp.get('cpu')
        self.cpu = cpu(cpuconfig[0])

        #fpga_fw
        fpga_fwconfig = __confTemp.get('fpga_fw', None)
        if fpga_fwconfig != None:
            self.fpga_fw = fpga_fw(fpga_fwconfig[0])
        else:
            self.fpga_fw = None

        #spi_flashs
        flashtmp = []
        flashconfig = __confTemp.get('ext_firmwares', None)
        external_firmwares = __confTemp.get('ext_firmwares_v2', None)
        if flashconfig is not None:
            for i in range(len((flashconfig))):
                flash1  = flash(flashconfig[i])
                flashtmp.append(flash1)
        elif external_firmwares is not None:
            for i in range(len((external_firmwares))):
                flash1  = flash_v2(external_firmwares[i])
                flashtmp.append(flash1)
        self.flash_list = flashtmp

        #firmware
        self.firmware = firmware()

        #uboot
        ubootconfig = __confTemp.get('uboots', None)
        if ubootconfig != None:
            self.uboot = uboot(ubootconfig[0])
        else:
            self.uboot = None

        #devmon
        devmontemp = []
        devmonconfig = __confTemp.get('devmon', None)
        if devmonconfig is not None:
            for i in devmonconfig:
                tmp = devmon(i)
                devmontemp.append(tmp)
        self.devmon_list = devmontemp

    #device_cfg
    @property
    def device_cfg(self):
        return self.__device_cfg

    @device_cfg.setter
    def device_cfg(self, val):
        self.__device_cfg = val

    #dcdc
    @property
    def dcdc_list(self):
        return self.__dcdc_list

    @dcdc_list.setter
    def dcdc_list(self, val):
        self.__dcdc_list = val

    #sensor
    @property
    def sensor_list(self):
        return self.__sensor_list

    @sensor_list.setter
    def sensor_list(self, val):
        self.__sensor_list = val

    def get_sensor_byname(self, name):
        tmp = self.sensor_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #psu
    @property
    def psu_list(self):
        return self.__psu_list


    @psu_list.setter
    def psu_list(self, val):
        self.__psu_list  = val

    def get_psu_byname(self, name):
        tmp = self.psu_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #fan
    @property
    def fan_list(self):
        return self.__fan_list

    @fan_list.setter
    def fan_list(self, val):
        self.__fan_list = val

    def get_fan_byname(self, name):
        tmp = self.fan_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None


    #led
    @property
    def led_list(self):
        return self.__led_list

    @led_list.setter
    def led_list(self, val):
        self.__led_list = val

    def get_ledlist_config(self):
        pass

    def get_led_byname(self, name):
        tmp = self.led_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #temp
    @property
    def temp_list(self):
        return self.__temp_list

    @temp_list.setter
    def temp_list(self, val):
        self.__temp_list = val

    def get_temp_byname(self, name):
        tmp = self.temp_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #cpld
    @property
    def cpld_list(self):
        return self.__cpld_list

    @cpld_list.setter
    def cpld_list(self, val):
        self.__cpld_list = val

    def get_cpld_byname(self, name):
        tmp = self.cpld_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #bios
    @property
    def bios_list(self):
        return self.__bios_list

    @bios_list.setter
    def bios_list(self, val):
        self.__bios_list = val

    def get_bios_byname(self, name):
        tmp = self.bios_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #bmc
    @property
    def bmc_list(self):
        return self.__bmc_list

    @bmc_list.setter
    def bmc_list(self, val):
        self.__bmc_list = val

    def get_bmc_byname(self, name):
        tmp = self.bmc_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #cpu
    @property
    def cpu(self):
        return self.__cpu

    @cpu.setter
    def cpu(self, val):
        self.__cpu = val

    def get_cpu_byname(self, name):
        return self.cpu

    #fpga_fw
    @property
    def fpga_fw(self):
        return self.__fpga_fw

    @fpga_fw.setter
    def fpga_fw(self, val):
        self.__fpga_fw = val

    def get_fpga_fw_byname(self, name):
        return self.fpga_fw

    #spi_flashs
    @property
    def flash_list(self):
        return self.__flash_list

    @flash_list.setter
    def flash_list(self, val):
        self.__flash_list = val

    def get_flash_byname(self, name):
        tmp = self.flash_list
        for i in range(len(tmp)):
            if name == tmp[i].name:
                return tmp[i]
        return None

    #firmware
    @property
    def firmware_fw(self):
        return self.__firmware

    @firmware_fw.setter
    def firmware_fw(self, val):
        self.__firmware = val

    def get_firmware_byname(self, name):
        return self.firmware

    #uboot
    @property
    def uboot(self):
        return self.__uboot

    @uboot.setter
    def uboot(self, val):
        self.__uboot = val

    def get_uboot_byname(self, name):
        return self.uboot
