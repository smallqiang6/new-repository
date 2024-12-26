# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
from .baseutil import baseutil
from product_hal.ruijieconfig import *
from .devicebase import devicebase
from .gpio import linuxgpio
import time

class Operation:
    REMOVE_FIRMWARE = 0
    ADD_FIRMWARE = 1
'''
example:
{
    "name": @flash name,
    "switch": [
        {"way": "gpio", "pin" : 127, "dir": "out", "enable": 1 , "disable": 0}
    ],
    "flash_chip": [
        {"way": "i2c", "bus": 0, "addr": 0x0d, "offset": 0x24, "master" : 0x00, "slave": 0x01}
    ],
    "slot": 0,
    "type": "spi"
}
'''
class flash_v2(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.name = conf.get('name', None)
            self.switch = conf.get('switch', None)
            self.init_cmd = conf.get('init_cmd', None)
            self.finish_cmd = conf.get('finish_cmd', None)
            self.slot = conf.get('slot', None)
            self.device_config = conf.get("device_config", None)
            self.type = conf.get("type", None)
            self.chip_select = conf.get("chip_select", None)
            self.select_master_cmd = conf.get("select_master_cmd", None)
            self.select_slave_cmd = conf.get("select_slave_cmd", None)
            self.deselect_master_cmd = conf.get("deselect_master_cmd", None)
            self.deselect_slave_cmd = conf.get("deselect_slave_cmd", None)

    def export_gpio(self, pin, direction, value):
        gpio = linuxgpio(pin)
        gpio.linuxgpio_export()
        gpio.linuxgpio_configure(direction, value)
        return True

    def unexport_gpio(self, pin, direction, value):
        gpio = linuxgpio(pin)
        gpio.linuxgpio_configure(direction, value)
        gpio.linuxgpio_unexport()
        return True

    def external_firmware_get_value(self, value):
        way = value.get("way")
        if way == "gpio":
            gpio = linuxgpio(value.get("pin"))
            return gpio.value
        elif way == "i2c":
            ret, val = self.get_value(value)
            time.sleep(0.5)
            return val
        else:
            return -1
        return -1

    def external_firmware_set_value(self, value, action):
        way = value.get("way")
        if way == "gpio":
            ret = self.export_gpio(value.get("pin"), value.get("dir"), value.get(action))
        elif way == "i2c":
            ret, val = self.set_value(value, value.get(action))
            time.sleep(0.5)
        else:
            return False
        return ret

    def external_firmware_unset_value(self, value, action):
        way = value.get("way")
        if way == "gpio":
            ret = self.unexport_gpio(value.get("pin"), value.get("dir"), value.get(action))
        elif way == "i2c":
            ret, val = self.set_value(value, value.get(action))
            time.sleep(0.5)
        else:
            return False
        return ret

    def external_firmware_channel_enable(self):
        for value in self.switch:
            ret = self.external_firmware_set_value(value, "enable")
            if ret == False:
                return ret
        return ret

    def external_firmware_channel_disable(self):
        for value in self.switch:
            ret = self.external_firmware_unset_value(value, "disable")
            if ret == False:
                return ret
        return ret

    def external_firmware_set_chip(self, operation, chip_select=None):
        if self.chip_select != None and chip_select != None:
            sel_invert = 0
            spi_sel = self.chip_select.get("spi_sel", None)
            chip = self.chip_select.get("chip", None)
            if spi_sel != None:
                for value in spi_sel:
                    val = self.external_firmware_get_value(value)
                    if (val & value.get("mask")) != value.get("target"):
                        sel_invert = 1
                        break
            if sel_invert == 1:
                if chip_select == "master":
                    chip_select = "slave"
                elif chip_select == "slave":
                    chip_select = "master"

            for value in chip:
                if operation == Operation.ADD_FIRMWARE:
                    ret = self.external_firmware_set_value(value, chip_select)
                elif operation == Operation.REMOVE_FIRMWARE:
                    ret = self.external_firmware_unset_value(value, chip_select)
                else:
                    self.logger_debug("Unknow operation %d", operation)
                    return False
                if ret == False:
                    return ret
        return True

    def spi_flash_add_device(self):
        cmd = "scan-asdsmc add " + str(self.slot)
        ret, value = self.command(cmd)
        if ret != 0:
            self.logger_debug("%s failed %d %s" % (cmd, ret, value))
            return False
        return True

    def spi_flash_remove_device(self):
        cmd = "scan-asdsmc remove " + str(self.slot)
        ret, value = self.command(cmd)
        if ret != 0:
            self.logger_debug("%s failed %d %s" % (cmd, ret, value))
            return False
        return True

    def i2c_eeprom_add_device(self):
        device = self.device_config.get("device", None)
        bus = self.device_config.get("bus", None)
        addr = self.device_config.get("addr", None)
        ret, value = self.command("echo %s %d > /sys/bus/i2c/devices/i2c-%d/new_device" % (device, addr, bus))
        if ret != 0:
            self.logger_debug("Add I2C eeprom bus %d addr %d failed" % (bus, addr))
            return False
        return True

    def i2c_eeprom_remove_device(self):
        bus = self.device_config.get("bus", None)
        addr = self.device_config.get("addr", None)
        ret, value = self.command("echo %d > /sys/bus/i2c/devices/i2c-%d/delete_device" % (addr, bus))
        if ret != 0:
            self.logger_debug("Remove I2C eeprom bus %d addr %d failed" % (bus, addr))
            return False
        return True

    def external_firmware_add_device(self):
        if self.type == "spi":
            ret = self.spi_flash_add_device()
        elif self.type == "i2c":
            ret = self.i2c_eeprom_add_device()
        else:
            return False
        return ret

    def external_firmware_remove_device(self):
        if self.type == "spi":
            ret = self.spi_flash_remove_device()
        elif self.type == "i2c":
            ret = self.i2c_eeprom_remove_device()
        else:
            return False
        return ret

    def add_flash(self, flash_chip=None):
        if flash_chip is not None:
            if flash_chip == "master":
                chip_select_cmd = self.select_master_cmd
            elif flash_chip == "slave":
                chip_select_cmd = self.select_slave_cmd
            else:
                self.logger_debug("%s unsupport select flash_chip: %s" % (self.name, flash_chip))
                return False

            #must config
            if chip_select_cmd is None:
                self.logger_debug("%s %s chip_select_cmd is None" % (self.name, flash_chip))
                return False

            ret = self.deal_itmes(chip_select_cmd)
            if ret == False:
                self.logger_debug("%s exec %s chip_select_cmd is fail" % (self.name, flash_chip))
                return False

        ret = self.deal_itmes(self.init_cmd)
        if ret == False:
            self.logger_debug("%s run init_cmd failed" % self.name)
            return ret
        return True

    def remove_flash(self, flash_chip=None):
        if flash_chip is not None:
            if flash_chip == "master":
                chip_deselect_cmd = self.deselect_master_cmd
            elif flash_chip == "slave":
                chip_deselect_cmd = self.deselect_slave_cmd
            else:
                self.logger_debug("%s unsupport deselect flash_chip: %s" % (self.name, flash_chip))
                return False

            #if not config, exec common finish_cmd
            if chip_deselect_cmd is not None:
                ret = self.deal_itmes(chip_deselect_cmd)
                if ret == False:
                    self.logger_debug("%s exec %s chip_deselect_cmd is fail" % (self.name, flash_chip))
                    return False

        ret = self.deal_itmes(self.finish_cmd)
        if ret == False:
            self.logger_debug("%s run finish_cmd failed" % self.name)
            return ret
        return True
