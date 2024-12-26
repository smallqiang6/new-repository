#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# devicebase.py
# Python implementation of the Class devicebase
# Original author: rd@ruijie.com.cn
#
#######################################################
from .osutil import osutil
from .baseutil import baseutil
import subprocess
import time
import os

class devicebase():
    _name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    def dumpValueByI2c(self, bus, loc):
        str = ""
        for i in range(256):
            ret,val = self.get_i2c(bus, loc, i)
            str += chr(val)
        return str

    def get_eeprom_info(self, conf):
        if conf.get('way') == 'sysfs':
            ret, eeprom = self.get_value(conf)
            if ret is False:
                return None
        else:
            eeprom = self.dumpValueByI2c(conf.get('bus'), conf.get('addr'))
        return eeprom

    def exec_os_cmd(self, cmd):
        status, output = subprocess.getstatusoutput(cmd)
        return status, output

    def get_value(self, config):
        '''
            get value by config way
            way  i2c/sysfs/lpc
        '''
        if config is None:
            return False, None
        way = config.get("way")
        size = config.get("size")
        if way == 'sysfs':
            return self.get_sysfs(config.get("loc"), size)
        elif way == "i2c":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.get_i2c(bus, addr, offset)
        elif way == "i2cword":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.get_i2cword(bus, addr, offset)
        elif way == "devmem":
            addr = config.get("addr")
            digit = config.get("digit")
            mask = config.get("mask", None)
            return self.get_devmem(addr, digit, mask)
        elif way == "i2cbit":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            bit = config.get("bit", 0)
            return self.get_i2cbit(bus, addr, offset, bit)
        elif way == "i2cbitblock":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            mask = config.get("mask", None)
            shift = config.get("shift", 0)
            direction = config.get("direction", "right")
            return self.get_data_shift(bus, addr, offset, mask, shift, direction)
        else:
            raise Exception("cannot found way deal")

    def get_sysfs(self, loc, size):
        return self.getsysfs(loc, size)

    def getsysfs(self, loc, size):
        ret,val = osutil.readsysfs(loc, size)
        return ret , val

    def find_real_file_path(self, loc):
        return osutil.find_real_file_path(loc)

    def read_real_sysfs(self, loc):
        return osutil.read_real_sysfs(loc)
    
    def write_real_sysfs(self, loc, value):
        return osutil.write_real_sysfs(loc, value)

    def get_devmem(self, addr, digit, mask):
        return osutil.getdevmem(addr, digit, mask)

    def get_i2cword(self, bus, addr, offset):
        return self.geti2cword(bus, addr, offset)

    def geti2cword(self,bus,addr, offset):
        ret,val = osutil.geti2cword(bus, addr, offset)
        return ret, val

    def get_i2c(self, bus, addr, offset):
        return self.geti2c(bus, addr, offset)

    def geti2c(self, bus, addr, offset):
        ret,val = osutil.rji2cget(bus, addr, offset)
        return ret , val

    def get_i2cbit(self, bus, addr, offset, bit):
        ret,val = self.get_i2c(bus, addr, offset)
        if ret == False:
            bit_val = val
        else:
            bit_val = ((val & (1<<bit)) >> bit)
        return ret, bit_val

    def get_data_shift(self, bus, addr, offset, mask, shift, direction):
        ret,val = self.get_i2c(bus, addr, offset)
        if ret == False:
            return ret, val
        else:
            data = self.get_reg_data(val, mask, shift, direction)
        return ret, data

    def get_reg_data(self, val, mask, shift, direction):
        data = val
        if mask == None:
            if direction == "right":
                data = val >> shift
            else:
                data = val << shift
        else:
            if direction == "right":
                data = ((val & mask) >> shift)
            else:
                data = ((val & mask) << shift)
        return data

    def get_i2cblock(self, bus, addr, offset):
        ret, val = osutil.rji2cgetblock_python(bus, addr, offset)
        return ret, val

    def dev_file_write(self, path, offset, buf_list):
        msg = ""
        fd = -1

        if not os.path.exists(path):
            msg = path + " not found !"
            return False, msg

        if isinstance(buf_list, list):
            if len(buf_list) == 0:
                msg = "buf_list:%s is NONE !" % buf_list
                return False, msg
        elif isinstance(buf_list, int):
            buf_list = [buf_list]
        else:
            msg = "buf_list:%s is not list type or not int type !" % buf_list
            return False, msg

        try:
            fd = os.open(path, os.O_WRONLY)
            os.lseek(fd, offset, os.SEEK_SET)
            ret = os.write(fd, bytes(buf_list))
        except Exception as e:
            msg = str(e)
            return False, msg
        finally:
            if fd > 0:
                os.close(fd)

        return True, ret

    def set_value(self, config, val):
        '''
            get value by config way
            way  i2c/sysfs/lpc
        '''
        delay_time = config.get("delay", None)
        if delay_time is not None:
            time.sleep(delay_time)

        way = config.get("way")
        if way == 'sysfs':
            pass
        elif way == "devfile":
            path = config.get("path")
            offset = config.get("offset")
            buf_list = val
            ret, log = self.dev_file_write(path, offset, buf_list)
            if ret is True:
                return True, ("devfile write path:%s, offset:0x%x, buf_list:%s success." % (path, offset, buf_list))
            return False, ("devfile read  path:%s, offset:0x%x, buf_list:%s failed.log:%s" %
                           (path, offset, buf_list, log))
        elif way == 'cmd':
            cmd = config.get("cmd")
            ret, log = self.exec_os_cmd(cmd)
            if ret:
                return False, ("cmd write exec %s failed, log: %s" % (cmd, log))
            return True, ("cmd write exec %s success" % cmd)

        elif way == "i2c":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.set_i2c(bus, addr, offset, val)
        elif way == "i2cpec":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.seti2c_byte_pec(bus, addr, offset, val)
        elif way =='i2cword':
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.set_i2cword(bus, addr, offset, val)
        elif way == "i2cwordpec":
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            return self.set_i2cwordpec(bus, addr, offset, val)
        elif way =='i2cbit':
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            bit = config.get("bit", 0)
            return self.set_i2cbit(bus, addr, offset, bit, val)
        elif way == "i2cbitblock": #set mask bit full 1 or full 0
            bus = config.get("bus")
            addr = config.get("addr")
            offset = config.get("offset")
            mask = config.get("mask", None)
            return self.set_data_shift(bus, addr, offset, mask, val)

    def set_i2cword(self, bus, addr, offset, val):
        return self.seti2cword(bus, addr, offset, val)

    def seti2cword(self, bus, addr, offset, val):
        return osutil.seti2cword(bus, addr, offset, val)

    def set_i2cwordpec(self, bus, addr, offset, val):
        return osutil.seti2cwordpec(bus, addr, offset, val)

    def seti2c_byte_pec(self, bus, addr, offset, val):
        return osutil.seti2c_byte_pec(bus, addr, offset, val)

    def set_i2c(self, bus, addr, offset, val):
        return self.seti2c(bus, addr, offset, val)

    def seti2c(self, bus, addr, offset, val):
        ret, val = osutil.rji2cset(bus, addr, offset, val)
        return ret, val

    def set_i2cbit(self, bus, addr, offset, bit, val):
        returnmsg = ""
        ret = False
        if val != 1 and val != 0:
            returnmsg = "ERR: illegal parameter %d" % val
            return ret, returnmsg
        ret, read_val = self.get_i2c(bus, addr, offset)
        if ret == False:
            returnmsg = read_val
            self.logger_debug("end set_i2cbit, get i2c bus:%d addr:0x%x offset:0x%x failed" %(bus, addr, offset))
        else:
            if val == 1:
                set_value = (read_val | (1<<bit))
            else:
                set_value = (read_val & ~(1<<bit))
            ret,returnmsg = self.set_i2c(bus, addr, offset, set_value)
        return ret, returnmsg

    def set_data_shift(self, bus, addr, offset, mask, val):
        returnmsg = ""
        ret = False
        if val != 1 and val != 0:
            returnmsg = "ERR: illegal parameter %d" % val
            return ret, returnmsg
        ret, read_val = self.get_i2c(bus, addr, offset)
        if ret == False:
            returnmsg = read_val
            self.logger_debug("end set_data_shift, get i2c bus:%d addr:0x%x offset:0x%x failed" %(bus, addr, offset))
        else:
            if mask == None:
                ret = True
                returnmsg = "mask is None, unneed to set"
            else:
                if val == 1:
                    set_value = read_val | mask
                else:
                    set_value = read_val & ~mask
                ret,returnmsg = self.set_i2c(bus, addr, offset, set_value)
        return ret, returnmsg

    def logger_debug(self, msg):
        baseutil.logger_debug(msg)

    def command(self, cmd):
        ret, output = osutil.command(cmd)
        return ret, output

    def deal_itmes(self, item_list):
        for item in item_list:
            val = item.get("value", None)
            ret, log = self.set_value(item, val)
            if not ret:
                self.logger_debug("deal items: %s fail, reason:%s" % (item, log))
                return False
        return True
