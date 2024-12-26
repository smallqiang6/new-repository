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
    "switch" : {
        "way": "gpio",
        "on" : {
            "switch1" :{"way": "gpio", "pin" : 127, "dir": "out", "value": 1},
        },
        "off": {
            "switch1" : {"way": "gpio", "pin" : 127, "dir": "in", "value": 0},
        },
    },
    "slot": 0,
    "type": "spi"
},
'''
class flash(devicebase):

    def __init__(self, conf = None):
        if conf is not None:
            self.name = conf.get('name', None)
            self.switch = conf.get('switch', None)
            self.slot = conf.get('slot', None)
            self.device_config = conf.get("device_config", None)
            self.type = conf.get("type", None)

    def export_gpio(self, pin, direction, value):
        gpio = linuxgpio(pin)
        gpio.linuxgpio_export()
        gpio.linuxgpio_configure(direction, value)

    def unexport_gpio(self, pin, direction, value):
        gpio = linuxgpio(pin)
        gpio.linuxgpio_configure(direction, value)
        gpio.linuxgpio_unexport()

    def ext_firmware_operation(self, switch, operation):
        way = switch.get("way")
        on = switch.get("on")
        off = switch.get("off")
        if operation == Operation.ADD_FIRMWARE:
            for (key, value) in on.items():
                if way == "gpio":
                    self.export_gpio(value.get("pin"), value.get("dir"), value.get("value"))
                elif way == "i2c":
                    self.set_value(value, value.get("value"))
                    time.sleep(0.5)
            return True
        elif operation == Operation.REMOVE_FIRMWARE:
            for (key, value) in off.items():
                if way == "gpio":
                    self.unexport_gpio(value.get("pin"), value.get("dir"), value.get("value"))
                elif way == "i2c":
                    self.set_value(value, value.get("value"))
                    time.sleep(0.5)
            return True
        else:
            return False
        return False

    def spi_add_device(self, slot):
        ret, value = self.command("scan-asdsmc add " + str(slot))
        return ret

    def spi_remove_device(self, slot):
        ret, value = self.command("scan-asdsmc remove " + str(slot))
        return ret

    def i2c_add_device(self, device_config):
        device = device_config.get("device", None)
        bus = device_config.get("bus", None)
        addr = device_config.get("addr", None)
        ret, value = self.command("echo %s %d > /sys/bus/i2c/devices/i2c-%d/new_device" % (device, addr, bus))
        return ret

    def i2c_remove_device(self, device_config):
        bus = device_config.get("bus", None)
        addr = device_config.get("addr", None)
        ret, value = self.command("echo %d > /sys/bus/i2c/devices/i2c-%d/delete_device" % (addr, bus))
        return ret

    def add_ext_firmware(self):
        ret = -1

        if self.type == "spi":
            ret = self.spi_add_device(self.slot)
        elif self.type == "i2c":
            ret = self.i2c_add_device(self.device_config)
        return ret

    def remove_ext_firmware(self):
        ret = -1

        if self.type == "spi":
            ret = self.spi_remove_device(self.slot)
        elif self.type == "i2c":
            ret = self.i2c_remove_device(self.device_config)
        return ret

    def add_flash(self, ext_firmware):
        if self.ext_firmware_operation(self.switch, Operation.ADD_FIRMWARE):
            ret = self.add_ext_firmware()
            if ret == 0:
                return True
        return False
        
    def remove_flash(self, ext_firmware):
        self.command("sync")
        ret = self.remove_ext_firmware()
        if self.ext_firmware_operation(self.switch, Operation.REMOVE_FIRMWARE) and ret == 0:
            return True
        return False