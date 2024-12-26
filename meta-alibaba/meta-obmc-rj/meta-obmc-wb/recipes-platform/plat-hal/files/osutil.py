#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# osutil.py
# Python implementation of the Class osutil
# Original author: rd@ruijie.com.cn
#
#######################################################

import subprocess
import time
import glob
import chardet
from wbutil.smbus import SMBus
import time
from  functools import wraps


def retry(maxretry =6, delay = 0.01):
    '''
        maxretry:  max retry times
        delay   :  interval after last retry
    '''
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            time_retry = maxretry
            time_delay = delay
            result_msg = ""
            while time_retry:
                try:
                    val , result_msg = f(*args, **kwargs)
                    if val is False:
                        time_retry -=1
                        time.sleep(time_delay)
                        continue
                    else:
                        return val, result_msg
                except Exception as e:
                    time_retry -= 1
                    result_msg = str(e)
                    time.sleep(time_delay)
            return False, "max time retry last errmsg is {}".format(result_msg)
        return wrapper
    return decorator

class osutil(object):
    """
       osutil
    """

    @staticmethod
    @retry(maxretry = 6)
    def rji2cget_python(bus, addr, reg):
        with SMBus(bus) as y:
            val , ind  = y.read_byte_data(addr, reg, True)
        return val , ind


    @staticmethod
    @retry(maxretry = 6)
    def rji2cset_python(bus, addr, reg, value):
        with SMBus(bus) as y:
            val , ind  = y.write_byte_data(addr, reg, value, True)
        return val , ind

    @staticmethod
    @retry(maxretry = 6)
    def rji2cgetword_python(bus, addr, reg):
        with SMBus(bus) as y:
            val , ind  = y.read_word_data(addr, reg, True)
        return val , ind

    @staticmethod
    @retry(maxretry = 6)
    def rji2csetword_python(bus, addr, reg, value):
        with SMBus(bus) as y:
            val , ind  = y.write_word_data(addr, reg, value, True)
        return val , ind

    @staticmethod
    @retry(maxretry = 6)
    def rji2cgetblock_python(bus, addr, reg):
        with SMBus(bus) as y:
            val , ind = y.read_block_data(addr, reg, True)
        return val , ind

    @staticmethod
    @retry(maxretry = 6)
    def rji2csetwordpec_python(bus, addr, reg, value):
        with SMBus(bus) as y:
            val , ind  = y.write_word_data_pec(addr, reg, value, True)
        return val , ind

    @staticmethod
    @retry(maxretry = 6)
    def rji2cset_byte_pec_python(bus, addr, reg, value):
        with SMBus(bus) as y:
            val , ind  = y.write_byte_data_pec(addr, reg, value, True)
        return val , ind


    @staticmethod
    def command(cmdstr):
        retcode, output = subprocess.getstatusoutput(cmdstr)
        return retcode, output


    @staticmethod
    def geti2cword_i2ctool(bus, addr, offset):
        command_line = "i2cget -f -y %d 0x%02x 0x%02x  wp" % (bus, addr, offset)
        retrytime = 6
        ret_t = ""
        for i in range(retrytime):
            ret, ret_t = osutil.command(command_line)
            if ret == 0:
                return True, int(ret_t, 16)
            time.sleep(0.1)
        return False, ret_t


    @staticmethod
    def seti2cword_i2ctool(bus, addr, offset, val):
        command_line = "i2cset -f -y %d 0x%02x 0x%0x 0x%04x wp" % (bus, addr, offset, val)
        retrytime = 6
        ret_t = ""
        for i in range(retrytime):
            ret, ret_t = osutil.command(command_line)
            if ret == 0:
                return True, ret_t
            time.sleep(0.1)
        return False, ret_t

    @staticmethod
    def rji2cget_i2ctool(bus, devno, address):
        command_line = "i2cget -f -y %d 0x%02x 0x%02x " % (bus, devno, address)
        retrytime = 6
        ret_t = ""
        for i in range(retrytime):
            ret, ret_t = osutil.command(command_line)
            if ret == 0:
                return True, int(ret_t, 16)
            time.sleep(0.1)
        return False, ret_t

    @staticmethod
    def rji2cset_i2ctool(bus, devno, address, byte):
        command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%02x" % (
            bus, devno, address, byte)
        retrytime = 6
        ret_t = ""
        for i in range(retrytime):
            ret, ret_t = osutil.command(command_line)
            if ret == 0:
                return True, ret_t
        return False, ret_t

    @staticmethod
    def geti2cword(bus, addr, offset):
        return osutil.rji2cgetword_python(bus, addr, offset)
    @staticmethod
    def seti2cword(bus, addr, offset, val):
        return osutil.rji2csetword_python(bus, addr, offset, val)

    @staticmethod
    def seti2cwordpec(bus, addr, offset, val):
        return osutil.rji2csetwordpec_python(bus, addr, offset, val)

    @staticmethod
    def seti2c_byte_pec(bus, addr, offset, val):
        return osutil.rji2cset_byte_pec_python(bus, addr, offset, val)

    @staticmethod
    def rji2cget(bus, devno, address):
        return osutil.rji2cget_python(bus, devno, address)
    @staticmethod
    def rji2cset(bus, devno, address, byte):
        return osutil.rji2cset_python(bus, devno, address, byte)

    @staticmethod
    def byteTostr(val):
        strtmp = ''
        for i in range(len(val)):
            strtmp += chr(val[i])
        return strtmp

    @staticmethod
    def find_real_file_path(location):
        try:
            locations = glob.glob(location)
            if len(locations) > 0:
                return True, locations[0]
            else:
                return False, "not found"
        except Exception as e:
            return False, (str(e)+" location[%s] not found" % location)

    @staticmethod
    def read_real_sysfs(location):
        """
        Get sys value by full file path
        """
        try:
            with open(location, 'rb') as fd1:
                tmp = fd1.read()
            retval = osutil.byteTostr(tmp)
        except Exception as e:
            return False, (str(e)+" location[%s]" % location)
        return True, retval


    @staticmethod
    def write_real_sysfs(location, value):
        """
        Set sys value by full file path
        """
        try:
            with open(location, 'r+') as fd1:
                write_len = fd1.write(value)
        except Exception as e:
            return False, (str(e)+" location[%s]" % location)
        return True, write_len


    @staticmethod
    def readsysfs(location, size):
        """
        Get sys value by Flexible file path
          such as   /*/*/test
        """
        try:
            locaitons = glob.glob(location)
            with open(locaitons[0], 'rb') as fd1:
                if size is None:
                    tmp = fd1.read()
                else:
                    tmp = fd1.read(size)
            retval = osutil.byteTostr(tmp).strip()
        except Exception as e:
            return False, (str(e)+" location[%s]" % location)
        return True, retval

    @staticmethod
    def getdevmem(addr, digit, mask):
        command_line = "devmem 0x%02x %d" %(addr, digit)
        retrytime = 6
        ret_t = ""
        for i in range(retrytime):
            ret, ret_t = osutil.command(command_line)
            if ret == 0:
                if mask != None:
                    ret_t = str(int(ret_t, 16) & mask)
            return True, ret_t
        return False, ret_t

