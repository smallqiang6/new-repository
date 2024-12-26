#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import subprocess
import time
import glob
import re
import ast
import logging.handlers

MAILBOX_DIR = "/sys/bus/i2c/devices/"


class CodeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.value = None

    def get_value(self):
        return self.value

    def get_op_value(self, node):
        if isinstance(node, ast.Call):       # node is func call
            value = self.visit_Call(node)
        elif isinstance(node, ast.BinOp):    # node is BinOp
            value = self.visit_BinOp(node)
        elif isinstance(node, ast.UnaryOp):  # node is UnaryOp
            value = self.visit_UnaryOp(node)
        elif isinstance(node, ast.Num):      # node is Num Constant
            value = node.n
        elif isinstance(node, ast.Str):      # node is Str Constant
            value = node.s
        elif isinstance(node, ast.List):     # node is List Constant
            value = [element.value for element in node.elts]
        else:
            raise NotImplementedError("Unsupport operand type: %s" % type(node))
        return value

    def visit_UnaryOp(self, node):
        '''
        node.op: operand type, only support ast.UAdd/ast.USub
        node.operand: only support ast.Call/ast.Constant(ast.Num/ast.Str)/ast.BinOp/ast.UnaryOp
        '''

        operand_value = self.get_op_value(node.operand)
        if isinstance(node.op, ast.UAdd):
            self.value = operand_value
        elif isinstance(node.op, ast.USub):
            self.value = 0 - operand_value
        else:
            raise NotImplementedError("Unsupport arithmetic methods %s" % type(node.op))
        return self.value

    def visit_BinOp(self, node):
        '''
        node.left: left operand,  only support ast.Call/ast.Constant(ast.Num)/ast.BinOp
        node.op: operand type, only support ast.Add/ast.Sub/ast.Mult/ast.Div
        node.right: right operan, only support ast.Call/ast.Constant(ast.Num/ast.Str)/ast.BinOp
        '''
        left_value = self.get_op_value(node.left)
        right_value = self.get_op_value(node.right)

        if isinstance(node.op, ast.Add):
            self.value = left_value + right_value
        elif isinstance(node.op, ast.Sub):
            self.value = left_value - right_value
        elif isinstance(node.op, ast.Mult):
            self.value = left_value * right_value
        elif isinstance(node.op, ast.Div):
            self.value = left_value / right_value
        else:
            raise NotImplementedError("Unsupport arithmetic methods %s" % type(node.op))
        return self.value

    def visit_Call(self, node):
        '''
        node.func.id: func name, only support 'float', 'int', 'str'
        node.args: func args list,only support ast.Constant(ast.Num/ast.Str)/ast.BinOp/ast.Call
        str/float only support one parameter, eg: float(XXX), str(xxx)
        int support one or two parameters, eg: int(xxx) or int(xxx, 16)
        xxx can be ast.Call/ast.Constant(ast.Num/ast.Str)/ast.BinOp
        '''
        calc_tuple = ("float", "int", "str", "max", "min")

        if node.func.id not in calc_tuple:
            raise NotImplementedError("Unsupport function call type: %s" % node.func.id)

        args_val_list = []
        for item in node.args:
            ret = self.get_op_value(item)
            if isinstance(ret, list):
                args_val_list.extend(ret)
            else:
                args_val_list.append(ret)

        if node.func.id == "str":
            if len(args_val_list) != 1:
                raise TypeError("str() takes 1 positional argument but %s were given" % len(args_val_list))
            value = str(args_val_list[0])
            self.value = value
            return value

        if node.func.id == "float":
            if len(args_val_list) != 1:
                raise TypeError("float() takes 1 positional argument but %s were given" % len(args_val_list))
            value = float(args_val_list[0])
            self.value = value
            return value

        if node.func.id == "max":
            value = max(args_val_list)
            self.value = value
            return value

        if node.func.id == "min":
            value = min(args_val_list)
            self.value = value
            return value
        # int
        if len(args_val_list) == 1:
            value = int(args_val_list[0])
            self.value = value
            return value
        if len(args_val_list) == 2:
            value = int(args_val_list[0], args_val_list[1])
            self.value = value
            return value
        raise TypeError("int() takes 1 or 2 arguments (%s given)" % len(args_val_list))

def inttostr(vl, length):
    if not isinstance(vl, int):
        raise Exception(" type error")
    index = 0
    ret_t = ""
    while index < length:
        ret = 0xff & (vl >> index * 8)
        ret_t += chr(ret)
        index += 1
    return ret_t


def strtoint(str_tmp):
    value = 0
    rest_v = str_tmp.replace("0X", "").replace("0x", "")
    str_len = len(rest_v)
    for index, val in enumerate(rest_v):
        value |= int(val, 16) << ((str_len - index - 1) * 4)
    return value


def inttobytes(val, length):
    if not isinstance(val, int):
        raise Exception("type error")
    data_array = bytearray()
    index = 0
    while index < length:
        ret = 0xff & (val >> index * 8)
        data_array.append(ret)
        index += 1
    return data_array


def byteTostr(val):
    strtmp = ''
    for value in val:
        strtmp += chr(value)
    return strtmp


def typeTostr(val):
    strtmp = ''
    if isinstance(val, bytes):
        strtmp = byteTostr(val)
    return strtmp


def exec_os_cmd(cmd):
    status, output = subprocess.getstatusoutput(cmd)
    return status, output


def exec_os_cmd_log(cmd):
    proc = subprocess.Popen((cmd), stdin=subprocess.PIPE, shell=True, stderr=sys.stderr, close_fds=True,
                            stdout=sys.stdout, universal_newlines=True, bufsize=1)

    stdout = proc.communicate()[0]
    stdout = typeTostr(stdout)
    return proc.returncode, stdout


# i2cget byte data with offset
def wbi2cget(bus, devno, address, word=None):
    if word is None:
        command_line = "i2cget -f -y %d 0x%02x 0x%02x " % (bus, devno, address)
    else:
        command_line = "i2cget -f -y %d 0x%02x 0x%02x %s" % (bus, devno, address, word)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cset byte data with offset
def wbi2cset(bus, devno, address, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%02x" % (
        bus, devno, address, byte)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cget word data with offset
def wbi2cgetWord(bus, devno, address):
    command_line = "i2cget -f -y %d 0x%02x 0x%02x w" % (bus, devno, address)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2sget word data with offset
def wbi2csetWord(bus, devno, address, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%x w" % (
        bus, devno, address, byte)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cget byte data without offset
def wbi2cgetByte(bus, devno):
    command_line = "i2cget -f -y %d 0x%02x" % (bus, devno)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cset byte data without offset
def wbi2csetByte(bus, devno, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x" % (
        bus, devno, byte)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cset byte data with offset and PEC
def wbi2cset_pec(bus, devno, address, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%02x bp" % (
        bus, devno, address, byte)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


# i2cset word data with offset and PEC
def wbi2cset_wordpec(bus, devno, address, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%02x wp" % (
        bus, devno, address, byte)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


def wbsysset(location, value):
    command_line = "echo 0x%02x > %s" % (value, location)
    ret, ret_t = exec_os_cmd(command_line)
    if ret == 0:
        return True, ret_t
    return False, ret_t


def dev_file_read(path, offset, read_len):
    val_list = []
    msg = ""
    ret = ""
    fd = -1

    if not os.path.exists(path):
        msg = path + " not found !"
        return False, msg

    try:
        fd = os.open(path, os.O_RDONLY)
        os.lseek(fd, offset, os.SEEK_SET)
        ret = os.read(fd, read_len)
        for item in ret:
            val_list.append(item)
    except Exception as e:
        msg = str(e)
        return False, msg
    finally:
        if fd > 0:
            os.close(fd)
    return True, val_list


def dev_file_write(path, offset, buf_list):
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


def write_sysfs(location, value):
    try:
        locations = glob.glob(location)
        if len(locations) == 0:
            return False, ("%s not found" % location)
        with open(locations[0], 'w') as fd1:
            fd1.write(value)
    except Exception as e:
        return False, (str(e) + " location[%s]" % location)
    return True, ("set location[%s] %s success !" % (location, value))


def read_sysfs(location):
    try:
        locations = glob.glob(location)
        with open(locations[0], 'rb') as fd1:
            retval = fd1.read()
        retval = typeTostr(retval)
        retval = retval.rstrip('\r\n')
        retval = retval.lstrip(" ")
    except Exception as e:
        return False, (str(e) + "location[%s]" % location)
    return True, retval

def setup_logger(log_file, max_bytes=1024*1024*5, backup_count=3):
    dir_path = os.path.dirname(log_file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # creat logger
    logger = logging.getLogger(log_file)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # creat RotatingFileHandler set log file size and backupCount
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        handler.setLevel(logging.DEBUG)

        # creat formatter and addd to handler
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s[%(funcName)s][%(lineno)s]: %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

def log_to_file(content, log_file_path, max_size=5*1024*1024):
    try:
        logger = setup_logger(log_file_path, max_size)
        logger.info(content)

    except Exception as e:
        return False, (str(e) + "log_file_path[%s]" % log_file_path)
    return True, "log_to_file success"

def get_pmc_register(reg_name):
    retval = 'ERR'
    mb_reg_file = MAILBOX_DIR + reg_name
    filepath = glob.glob(mb_reg_file)
    if len(filepath) == 0:
        return "%s %s  notfound" % (retval, mb_reg_file)
    mb_reg_file = filepath[0]
    if not os.path.isfile(mb_reg_file):
        return "%s %s  notfound" % (retval, mb_reg_file)
    try:
        with open(mb_reg_file, 'r') as fd:
            retval = fd.read()
    except Exception as error:
        retval = retval + str(error)
    retval = retval.rstrip('\r\n')
    retval = retval.lstrip(" ")
    return retval


def get_sysfs_value(location):
    pos_t = str(location)
    name = get_pmc_register(pos_t)
    return name


def write_sysfs_value(reg_name, value):
    fileLoc = MAILBOX_DIR + reg_name
    try:
        if not os.path.isfile(fileLoc):
            print(fileLoc, 'not found !')
            return False
        with open(fileLoc, 'w') as fd:
            fd.write(value)
    except Exception:
        print("Unable to open " + fileLoc + "file !")
        return False
    return True


def wb_peci_pcicfglocal_rd(bus, device, func, reg, rd_len):
    valid_rd_len = (1, 2, 4)
    if rd_len not in valid_rd_len:
        return False, "Invalid read length: %d" % rd_len

    command_line = "dfd_debug peci_pcicfglocal_rd 0x%02x 0x%02x 0x%02x 0x%04x %d" % (bus, device, func, reg, rd_len)
    status, val_t = exec_os_cmd(command_line)
    if status != 0:
        return False, val_t

    val_list = []
    lines = val_t.strip("").split("\n")
    for line in lines:
        if line.startswith("0x"):
            val_list_tmp = re.sub(r'\s+', ' ', line.strip()).split(" ")
            val_list.extend(val_list_tmp[1:])

    if len(val_list) == 0:
        return False, "peci_pcicfglocal_rd fail, msg: %s " % val_t

    value = 0
    for index, val in enumerate(val_list):
        value |= (int(val, 16) << (8 * index))
    return True, value


def get_value_once(config):
    try:
        delay_time = config.get("delay", None)
        if delay_time is not None:
            time.sleep(delay_time)

        way = config.get("gettype")
        int_decode = config.get("int_decode", 16)
        if way == 'sysfs':
            loc = config.get("loc")
            ret, val = read_sysfs(loc)
            if ret is True:
                return True, int(val, int_decode)
            return False, ("sysfs read %s failed. log:%s" % (loc, val))
        if way == "i2c":
            bus = config.get("bus")
            addr = config.get("loc")
            offset = config.get("offset", 0)
            ret, val = wbi2cget(bus, addr, offset)
            if ret is True:
                return True, int(val, int_decode)
            return False, ("i2c read failed. bus:%d , addr:0x%x, offset:0x%x" % (bus, addr, offset))
        if way == "i2cword":
            bus = config.get("bus")
            addr = config.get("loc")
            offset = config.get("offset")
            ret, val = wbi2cgetWord(bus, addr, offset)
            if ret is True:
                return True, int(val, int_decode)
            return False, ("i2cword read failed. bus:%d, addr:0x%x, offset:0x%x" % (bus, addr, offset))
        if way == "i2cbyte":
            bus = config.get("bus")
            addr = config.get("loc")
            ret, val = wbi2cgetByte(bus, addr)
            if ret is True:
                return True, int(val, int_decode)
            return False, ("i2cbyte read failed. bus:%d, addr:0x%x" % (bus, addr))
        if way == "devfile":
            path = config.get("path")
            offset = config.get("offset")
            read_len = config.get("read_len")
            ret, val_list = dev_file_read(path, offset, read_len)
            if ret is True:
                if read_len == 1:
                    val = val_list[0]
                    return True, val
                return True, val_list
            return False, ("devfile read failed. path:%s, offset:0x%x, read_len:%d" % (path, offset, read_len))
        if way == 'cmd':
            cmd = config.get("cmd")
            ret, val = exec_os_cmd(cmd)
            if ret:
                return False, ("cmd read exec %s failed, log: %s" % (cmd, val))
            return True, int(val, int_decode)
        if way == 'file_exist':
            judge_file = config.get('judge_file', None)
            if os.path.exists(judge_file):
                return True, True
            return True, False
        if way == 'peci_pcicfglocal_rd':
            bus = config.get("bus")
            dev = config.get("dev")
            func = config.get("func")
            reg = config.get("reg")
            rd_len = config.get("rd_len")
            ret, val = wb_peci_pcicfglocal_rd(bus, dev, func, reg, rd_len)
            return ret, val
        return False, "not support read type"
    except Exception as e:
        return False, ("get_value_once exception:%s happen" % str(e))


def set_value_once(config):
    try:
        delay_time = config.get("delay", None)
        if delay_time is not None:
            time.sleep(delay_time)

        way = config.get("gettype")
        if way == 'sysfs':
            loc = config.get("loc")
            value = config.get("value")
            mask = config.get("mask", 0xff)
            mask_tuple = (0xff, 0)
            if mask not in mask_tuple:
                ret, read_value = read_sysfs(loc)
                if ret is True:
                    read_value = int(read_value, base=16)
                    value = (read_value & mask) | value
                else:
                    return False, ("sysfs read %s failed. log:%s" % (loc, read_value))
            ret, log = write_sysfs(loc, "0x%02x" % value)
            if ret is not True:
                return False, ("sysfs %s write 0x%x failed" % (loc, value))
            return True, ("sysfs write 0x%x success" % value)
        if way == "i2c":
            bus = config.get("bus")
            addr = config.get("loc")
            offset = config.get("offset")
            value = config.get("value")
            mask = config.get("mask", 0xff)
            mask_tuple = (0xff, 0)
            if mask not in mask_tuple:
                ret, read_value = wbi2cget(bus, addr, offset)
                if ret is True:
                    read_value = int(read_value, base=16)
                    value = (read_value & mask) | value
                else:
                    return False, ("i2c read failed. bus:%d , addr:0x%x, offset:0x%x" % (bus, addr, offset))
            ret, log = wbi2cset(bus, addr, offset, value)
            if ret is not True:
                return False, ("i2c write bus:%d, addr:0x%x, offset:0x%x, value:0x%x failed" %
                               (bus, addr, offset, value))
            return True, ("i2c write bus:%d, addr:0x%x, offset:0x%x, value:0x%x success" %
                          (bus, addr, offset, value))
        if way == 'i2cword':
            bus = config.get("bus")
            addr = config.get("loc")
            offset = config.get("offset")
            value = config.get("value")
            mask = config.get("mask", 0xff)
            mask_tuple = (0xff, 0)
            if mask not in mask_tuple:
                ret, read_value = wbi2cgetWord(bus, addr, offset)
                if ret is True:
                    read_value = int(read_value, base=16)
                    value = (read_value & mask) | value
                else:
                    return False, ("i2c read word failed. bus:%d , addr:0x%x, offset:0x%x" % (bus, addr, offset))
            ret, log = wbi2csetWord(bus, addr, offset, value)
            if ret is not True:
                return False, ("i2cword write bus:%d, addr:0x%x, offset:0x%x, value:0x%x failed" %
                               (bus, addr, offset, value))
            return True, ("i2cword write bus:%d, addr:0x%x, offset:0x%x, value:0x%x success" %
                          (bus, addr, offset, value))
        if way == 'i2cbyte':
            bus = config.get("bus")
            addr = config.get("loc")
            value = config.get("value")
            mask = config.get("mask", 0xff)
            mask_tuple = (0xff, 0)
            if mask not in mask_tuple:
                ret, read_value = wbi2cgetByte(bus, addr)
                if ret is True:
                    read_value = int(read_value, base=16)
                    value = (read_value & mask) | value
                else:
                    return False, ("i2c read byte failed. bus:%d, addr:0x%x" % (bus, addr))
            ret, log = wbi2csetByte(bus, addr, value)
            if ret is not True:
                return False, ("i2cbyte write bus:%d, addr:0x%x, value:0x%x failed" %
                               (bus, addr, value))
            return True, ("i2cbyte write bus:%d, addr:0x%x, value:0x%x success" %
                          (bus, addr, value))
        if way == "devfile":
            path = config.get("path")
            offset = config.get("offset")
            buf_list = config.get("value")
            ret, log = dev_file_write(path, offset, buf_list)
            if ret is True:
                return True, ("devfile write path:%s, offset:0x%x, buf_list:%s success." % (path, offset, buf_list))
            return False, ("devfile read  path:%s, offset:0x%x, buf_list:%s failed.log:%s" %
                           (path, offset, buf_list, log))
        if way == 'cmd':
            cmd = config.get("cmd")
            ret, log = exec_os_cmd(cmd)
            if ret:
                return False, ("cmd write exec %s failed, log: %s" % (cmd, log))
            return True, ("cmd write exec %s success" % cmd)
        if way == 'bit_wr':
            mask = config.get("mask")
            bit_val = config.get("value")
            val_config = config.get("val_config")
            ret, rd_value = get_value_once(val_config)
            if ret is False:
                return False, ("bit_wr read failed, log: %s" % rd_value)
            wr_val = (rd_value & mask) | bit_val
            val_config["value"] = wr_val
            ret, log = set_value_once(val_config)
            if ret is False:
                return False, ("bit_wr failed, log: %s" % log)
            return True, ("bit_wr success, log: %s" % log)
        if way == 'creat_file':
            file_name = config.get("file")
            ret, log = exec_os_cmd("touch %s" % file_name)
            if ret:
                return False, ("creat file %s failed, log: %s" % (file_name, log))
            exec_os_cmd("sync")
            return True, ("creat file %s success" % file_name)
        if way == 'remove_file':
            file_name = config.get("file")
            ret, log = exec_os_cmd("rm -rf %s" % file_name)
            if ret:
                return False, ("remove file %s failed, log: %s" % (file_name, log))
            exec_os_cmd("sync")
            return True, ("remove file %s success" % file_name)
        if way == "log_to_file":
            log_file_path = config.get("log_file_path")
            log_config = config.get("log_config")
            file_max_size = config.get("file_max_size", 5*1024*1024)
            if log_file_path is None or log_config is None:
                return False, ("log_to_file config err, please check, config: %s", config)
            ret, log_value = get_value_once(log_config)
            if ret is False:
                return False, ("log_to_file read failed, log: %s" % log_value)

            return log_to_file(log_value, log_file_path, file_max_size)
        return False, ("%s not support write type" % way)
    except Exception as e:
        return False, ("set_value_once exception:%s happen" % str(e))


def get_value(config):
    retrytime = 6
    for i in range(retrytime):
        ret, val = get_value_once(config)
        if ret is True:
            return True, val
        time.sleep(0.1)
    return False, val


def set_value(config):
    if config.get("pre_check") is not None:
        ret, rd_value = get_value(config["pre_check"])
        if ret is False:
            log = "do pre check get_value failed, msg: %s" % rd_value
            return False, log
        mask = config["pre_check"].get("mask")
        if mask is not None:
            value = rd_value & mask
        else:
            value = rd_value
        okval = config["pre_check"].get("okval")
        if value != okval:
            log = ("pre_check not ok, rd_value: %s, mask: %s, okval: %s, don't need to set_value" %
                (rd_value, mask, okval))
            return True, log

    retrytime = 6
    ignore_result_flag = config.get("ignore_result", 0)
    for i in range(retrytime):
        ret, log = set_value_once(config)
        if ret is True:
            return True, log
        if ignore_result_flag == 1:
            return True, log
        time.sleep(0.1)
    return False, log


def check_value(config):
    # check value
    retrytime = config.get("retry", 1)
    for i in range(retrytime):
        ret, rd_value = get_value(config)
        if ret is False:
            log = "get_value failed, msg: %s" % rd_value
            return False, log

        mask = config.get("mask")
        if mask is not None:
            value = rd_value & mask
        else:
            value = rd_value
        okval = config.get("okval")
        if value == okval:
            log = ("check ok, rd_value: %s, mask: %s, okval: %s, retry: %s" %
                (rd_value, mask, okval, i))
            return True, log
        # check failed, sleep to retry.
        sleep_time = config.get("sleep_time")
        if sleep_time is not None:
            time.sleep(sleep_time)
    log = ("check failed, rd_value: %s, mask: %s, okval: %s, retry: %s" %
            (rd_value, mask, okval, retrytime))
    return False, log


def get_format_value(format_str):
    ast_obj = ast.parse(format_str, mode='eval')
    visitor = CodeVisitor()
    visitor.visit(ast_obj)
    ret = visitor.get_value()
    return ret

