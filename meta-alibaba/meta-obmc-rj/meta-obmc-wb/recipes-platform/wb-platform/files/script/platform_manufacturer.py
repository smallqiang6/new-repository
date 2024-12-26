#!/usr/bin/env python3

import re
import fcntl
import subprocess
import os
import time
import sys
import argparse
from platform_config import MANUINFO_CONF, MGMT_VERSION_PATH, BSP_COMMON_LOG_PATH
from platform_util import *
from time import monotonic as _time

INDENT = 4
args = None
CURRENT_FILE_NAME = os.path.basename(__file__)

def printerr(vchar):
    sys.stderr.write(vchar + '\n')


def exec_os_cmd(cmd, timeout = None):
    status, output = subprocess.getstatusoutput(cmd)
    return status, output


def checksignaldriver(name):
    modisexistcmd = "lsmod | grep -w %s | wc -l" % name
    ret, output = exec_os_cmd(modisexistcmd)
    if ret:
        return False
    if output.isdigit() and int(output) > 0:
        return True
    return False


def adddriver(name):
    cmd = "modprobe %s" % name
    if checksignaldriver(name) is not True:
        ret, log = exec_os_cmd(cmd)
        if ret != 0 or len(log) > 0:
            return False
        return True
    return True


def removedriver(name):
    cmd = "rmmod %s" % name
    if checksignaldriver(name):
        exec_os_cmd(cmd)


def deal_itmes(item_list):
    for item in item_list:
        ret, log = set_value(item)
        if not ret:
            print("deal items error:%s" % log)


def get_func_value(funcname, params):
    func = getattr(ExtraFunc, funcname)
    ret = func(params)
    return ret


def devfileread(path, offset, length, bit_width):
    ret = ""
    val_str = ''
    val_list = []
    fd = -1
    if not os.path.exists(path):
        return "%s not found !" % path
    if length % bit_width != 0:
        return "only support read by bit_width"
    if length < bit_width:
        return "len needs to greater than or equal to bit_width"

    try:
        fd = os.open(path, os.O_RDONLY)
        os.lseek(fd, offset, os.SEEK_SET)
        ret = os.read(fd, length)
        for item in ret:
            val_list.append(item)

        for i in range(0, length, bit_width):
            for j in range(0, bit_width):
                val_str += "%02x" % val_list[i + bit_width - j - 1]
    except Exception as e:
        return "%s-%s" % (path, str(e))
    finally:
        if fd > 0:
            os.close(fd)
    return val_str


def read_reg(loc, offset, size):
    with open(loc, 'rb') as file:
        file.seek(offset)
        return ' '.join(["%02x" % item for item in file.read(size)])


def std_match(stdout, pattern):
    if pattern is None:
        return stdout.strip()
    for line in stdout.splitlines():
        if re.match(pattern, line):
            return line.strip()
    raise EOFError("pattern: {} does not match anything in stdout {}".format(
        pattern, stdout))


def i2c_rd(bus, loc, offset):
    '''
    read i2c with i2cget command
    '''
    cmd = "i2cget -f -y {} {} {}".format(bus, loc, offset)
    retrytime = 6
    for i in range(retrytime):
        ret, stdout = subprocess.getstatusoutput(cmd)
        if ret == 0:
            return stdout
        time.sleep(0.1)
    raise RuntimeError("run cmd: {} error, status {}".format(cmd, ret))


def i2c_rd_bytes(bus, loc, offset, size):
    blist = []
    for i in range(size):
        ret = i2c_rd(bus, loc, offset + i)
        blist.append(ret)

    return blist


def get_pair_val(source, separator):
    try:
        value = source.split(separator, 1)[1]
    except (ValueError, IndexError):
        return "ERR separator: {} does not match in source: {}".format(separator, source)
    return value.strip()


def get_regular_val(source, pattern, group):
    try:
        value = re.findall(pattern, source)[group]
    except Exception:
        return "ERR pattern: {} does not match  in source: {} with group: {}".format(pattern, source, group)
    return value.strip()


def find_match(file2read, pattern):
    with open(file2read, 'r') as file:
        for line in file:
            if not re.match(pattern, line):
                continue
            return line.strip()
    return "ERR pattern %s not match in %s" % (pattern, file2read)


def readaline(file2read):
    with open(file2read, 'r') as file:
        return file.readline()


def sort_key(e):
    return e.arrt_index


class ExtraFunc(object):
    @staticmethod
    def get_cpu_bmc_switch_version(params):
        version = ""
        try:
            before_deal_list = params.get("before", [])
            deal_itmes(before_deal_list)

            ret, version = exec_os_cmd(params["get_version"])
            if ret != 0:
                version = "ERR " + version

            if args.update:
                dir_path = os.path.dirname(MGMT_VERSION_PATH)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                if not os.path.exists(MGMT_VERSION_PATH):
                    with open(MGMT_VERSION_PATH, 'w') as file:
                        file.write('')

                ret, log = write_sysfs(MGMT_VERSION_PATH, ("%s\n" % version))
                if ret is False:
                    log = "%s: writer mgmt version to path fail, version:%s, patch:%s, reason:%s" % (CURRENT_FILE_NAME, version, MGMT_VERSION_PATH, log)
                    log_to_file(log, BSP_COMMON_LOG_PATH)
            after_deal_list = params.get("after", [])
            deal_itmes(after_deal_list)

        except Exception as e:
            version = "ERR %s" % (str(e))
        finally:
            finally_deal_list = params.get("finally", [])
            deal_itmes(finally_deal_list)
        return version


class CallbackSet:
    def cpld_format(self, blist):
        if isinstance(blist, str):
            blist = blist.split()
        elif not isinstance(blist, list) or len(blist) != 4:
            raise ValueError("cpld format: wrong parameter: {}".format(blist))

        return "{}{}{}{}".format(*blist).replace("0x", "")


class VersionHunter:
    call = CallbackSet()

    def __init__(self, entires):
        self.head = None
        self.next = None
        self.key = None
        self.cmd = None
        self.file = None
        self.reg = None
        self.i2c = None
        self.extra = None
        self.pattern = None
        self.separator = None
        self.parent = None
        self.ignore = False
        self.children = []
        self.level = 0
        self.callback = None
        self.delspace = None
        self.arrt_index = None
        self.config = None
        self.precheck = None
        self.func = None
        self.regular = None
        self.group = 0
        self.pci = None
        self.devfile = None
        self.decode = None
        self.timeout = 10
        self.__dict__.update(entires)


    def get_version(self):
        ret = "NA"
        try:
            if self.cmd is not None:
                ret, output = exec_os_cmd(self.cmd, self.timeout)
                if ret or len(output) == 0:
                    raise RuntimeError("run cmd: {} error, status: {}, msg: {}".format(self.cmd, ret, output))
                ret = std_match(output, self.pattern)
            elif self.file is not None:
                ret = self.read_file()
            elif self.reg is not None:
                ret = read_reg(self.reg.get("loc"), self.reg.get("offset"),
                               self.reg.get("size"))
            elif self.i2c:
                ret = i2c_rd_bytes(self.i2c.get("bus"), self.i2c.get("loc"),
                                   self.i2c.get("offset"),
                                   self.i2c.get("size"))
            elif self.config:
                ret = self.config
            elif self.func:
                ret = get_func_value(self.func.get("funcname"),
                                     self.func.get("params"))
            elif self.devfile:
                ret = devfileread(self.devfile.get("loc"), self.devfile.get("offset"),
                                  self.devfile.get("len"), self.devfile.get("bit_width"))

        except Exception as e:
            # printerr(e.message)
            return "ERR %s" % str(e)
        return self.exe_callback(ret)

    def exe_callback(self, data):
        try:
            if self.callback:
                method = getattr(self.call, self.callback)
                return method(data)
        except Exception:
            return "ERR run callback method: {} error, data: {}".format(self.callback, data)
        return data

    def read_file(self):
        if self.pattern is not None:
            return find_match(self.file, self.pattern)
        return readaline(self.file)

    def hunt(self):
        if self.ignore:
            return
        indent = self.level * INDENT * " "

        if self.precheck:
            try:
                ret = get_func_value(self.precheck.get("funcname"), self.precheck.get("params"))
                if ret is not True:
                    return
            except Exception as e:
                err_msg = "ERR %s" % str(e)
                format_str = "{}{:<{}}{}".format(indent, self.key + ':',
                                                 (30 - len(indent)), err_msg)
                print(format_str)
                return
        # has children
        if self.children:
            self.children.sort(key=sort_key)
            format_str = "{}{}:".format(indent, self.key)
            print(format_str)
            for child in self.children:
                if not isinstance(child, VersionHunter):
                    continue
                child.level = self.level + 1
                child.hunt()
        else:
            version = self.get_version() or ""
            if not version.startswith("ERR"):
                version = version.replace("\x00", "").strip()
                if self.separator is not None:
                    version = get_pair_val(version, self.separator)
                if self.delspace is not None:
                    version = version.replace(" ", "")
                if self.regular is not None:
                    version = get_regular_val(version, self.regular, self.group)
                if self.decode is not None:
                    tmp_version = self.decode.get(version)
                    if tmp_version is None:
                        if self.decode.get("default") is not None:
                            version = self.decode.get("default")
                        else:
                            version = "ERR decode %s failed" % version
                    else:
                        version = tmp_version
            format_str = "{}{:<{}}{}".format(indent, self.key + ':',
                                             (30 - len(indent)), version)
            print(format_str)

        if self.next:
            print("")
            self.next.hunt()


pidfile = 0


def ApplicationInstance():
    global pidfile
    pidfile = open(os.path.realpath(__file__), "r")
    try:
        fcntl.flock(pidfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except Exception:
        return False


def run():
    if os.geteuid() != 0:
        print("Root privileges are required for this operation")
        sys.exit(1)

    start_time = int(_time())
    while True:
        ret = ApplicationInstance()
        if ret is True:
            break
        if int(_time()) - start_time > 10:
            printerr("manufacturer is running.")
            sys.exit(1)
        time.sleep(0.5)

    objmap = {}

    try:
        target = {}
        target.update(MANUINFO_CONF)
        for objname, value in target.items():
            objmap[objname] = VersionHunter(value)
    except Exception as e:
        printerr(str(e))
        sys.exit(1)

    head = None
    for objname, obj in objmap.items():
        if head is None and obj.head:
            head = obj
        if obj.parent:
            objmap.get(obj.parent).children.append(obj)
        if obj.next:
            obj.next = objmap.get(obj.next)

    head.hunt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print firmware version.')
    parser.add_argument('-u','--update', action='store_true', help='update firmware version.')

    args = parser.parse_args()
    run()
