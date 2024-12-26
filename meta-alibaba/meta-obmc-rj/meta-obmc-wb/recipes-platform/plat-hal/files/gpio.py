# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import os
import sys

class linuxgpio():
    attributes = ('value', 'direction', 'active_low')

    def __init__(self, index):
        self.index = index
        self.sysfs = {}
        if self.export:
            for name in self.attributes:
                self.sysfs[name] = open(
                    os.path.join(self.path, name), 'w+b',
                    buffering=0)

    @property
    def path(self):
        return '/sys/class/gpio/gpio{:d}/'.format(self.index)

    @property
    def export(self):
        return os.path.exists(self.path)

    @export.setter
    def export(self, export):
        exported = self.export
        if export and not exported:
            with open("/sys/class/gpio/export",   'w') as h:
                h.write(str(self.index))
        elif not export and exported:
            with open("/sys/class/gpio/unexport", 'w') as h:
                h.write(str(self.index))
        if export and not len(self.sysfs):
            for name in self.attributes:
                self.sysfs[name] = open(
                    os.path.join(self.path, name), 'w+b',
                    buffering=0)
        elif not export:
            for h in self.sysfs.values():
                h.close()
            self.sysfs.clear()

    def _write(self, name, data):
        file = self.sysfs[name]
        file.seek(0)
        file.write(data)

    def _read(self, name):
        file = self.sysfs[name]
        file.seek(0)
        return file.read()

    @property
    def value(self):
        return int(self._read("value"))
    @value.setter
    def value(self, value):
        self._write("value", str(value).encode('ascii'))

    @property
    def direction(self):
        return self._read("direction").decode('ascii').strip()
    @direction.setter
    def direction(self, direction):
        self._write("direction", direction.encode('ascii'))

    @property
    def active_low(self):
        return int(self._read("active_low"))
    @active_low.setter
    def active_low(self, active_low):
        self._write("active_low", str(active_low).encode('ascii'))

    def linuxgpio_export(self):
        self.export = True

    def linuxgpio_unexport(self):
        self.export = False

    def linuxgpio_configure(self, dic, val):
        self.direction = dic
        self.value = val