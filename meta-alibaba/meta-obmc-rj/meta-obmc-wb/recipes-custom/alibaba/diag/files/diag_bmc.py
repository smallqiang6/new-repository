#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import os
import sys
import signal
import time
import threading
import hashlib
import subprocess
import re
import datetime
import socket
import fcntl,struct
import json
import struct
from fru import E2Util,E2Exception
import base64
#import select
import os, errno
import math

import unicodedata
from collections import OrderedDict

from  plat_hal.interface import interface
from eepromutil.fru import *
from plat_hal.devicebase import devicebase
from plat_hal.chassisbase import chassisbase
import gettext

locale_path = '/usr/local/bin/i18n/locale'
LOCALE_DIR = '/var/log/locale'

def stop_ali_server():
    units = ["cpumon", "dcdcmon", "powermon", "fanctrl"]
    for unit in units:
        cmd = "systemctl stop %s;"%unit
        my_log(cmd)
        log_os_system(cmd, 0)

def start_ali_server():
    log_os_system("systemctl start cpumon;systemctl start dcdcmon;systemctl start powermon;systemctl start fanctrl;", 0)

def restart_ali_server():
    log_os_system("systemctl restart cpumon;systemctl restart dcdcmon;systemctl restart powermon;systemctl restart fanctrl;", 0)

def command(cmdstr):
        retcode, output = subprocess.getstatusoutput(cmdstr)
        return retcode, output

def wide_chars(s):
    if isinstance(s, str):
        s = s.encode('utf-8').decode('utf-8')
    return sum(unicodedata.east_asian_width(x) in ('F', 'W') for x in s)

def get_device_branch():
    Device = socket.gethostname()
    if Device == "bmc":
        ret_t, log = command(" cat /etc/device/productname") 
        if "can't open" in log:
            print("do not find config file")
        else:
            return log.lower()
    else:
         return Device
Device_branch = get_device_branch()
grtd_productfile = ("BMC_alibaba_"+Device_branch+ "_rj_r0_config").replace("-","_")

def get_conffit_branch():
    Device = socket.gethostname()
    if Device == "bmc":
        ret_t, log = command(" cat /etc/device/conffitname")
        if "can't open" in log:
            print("do not find config file")
        else:
            return log.lower()
    else:
         return Device
Conffit_branch = get_conffit_branch()
grtd_conffitfile = ("BMC_alibaba_" + Conffit_branch + "_rj_r0_config").replace("-","_")

common_productfile = "ruijiecommon"

configfile_pre   =  "/usr/local/bin/"
import sys
#sys.path.append(platformpath)
sys.path.append(configfile_pre)


############################################################################################
global  module_product
if os.path.exists(configfile_pre + grtd_conffitfile + ".py"):
    module_product  = __import__(grtd_conffitfile, globals(), locals(), [])
elif os.path.exists(configfile_pre + grtd_productfile + ".py"):
    module_product  = __import__(grtd_productfile, globals(), locals(), [])
elif os.path.exists(configfile_pre + common_productfile + ".py"):
    module_product  = __import__(common_productfile, globals(), locals(), [])
else:
    print("do not find config file")
    exit(-1)
menuList = module_product.menuList
DCDC_DEVICE = module_product.DCDC_DEVICE
PSU_INFO = module_product.PSU_INFO
I2C_SCAN_LIST =  module_product.I2C_SCAN_LIST
LED_INFO = module_product.LED_INFO
FAN_SPEED = module_product.FAN_SPEED
E2_DEV = module_product.E2_DEV
FAN_PROTECT = module_product.FAN_PROTECT
CPLD_TEST = module_product.CPLD_TEST
FPGA_TEST = module_product.FPGA_TEST
ALI_BMC = module_product.ALI_BMC
ALI_E2_DEV = module_product.ALI_E2_DEV
FAN_INFO = module_product.FAN_INFO
EMMC_REGISTER = module_product.EMMC_REGISTER if ( hasattr(module_product, 'EMMC_REGISTER') ) else None
EMMC_FIO = module_product.EMMC_FIO if ( hasattr(module_product, 'EMMC_FIO') ) else None
MAC_THRESHOLD = module_product.MAC_THRESHOLD if ( hasattr(module_product, 'MAC_THRESHOLD') ) else None
BUSBAR_INFO = module_product.BUSBAR_INFO if ( hasattr(module_product, 'BUSBAR_INFO') ) else None
SPI_TEST = module_product.SPI_TEST if ( hasattr(module_product, 'SPI_TEST') ) else None
CLOCK_TEST = module_product.CLOCK_TEST if ( hasattr(module_product, 'CLOCK_TEST') ) else None
NETCARD_INFO = module_product.NETCARD_INFO if ( hasattr(module_product, 'NETCARD_INFO') ) else None
POWER_FW_VER = module_product.POWER_FW_VER if ( hasattr(module_product, 'POWER_FW_VER') ) else None
LEAKAGE_INFO = module_product.LEAKAGE_INFO if ( hasattr(module_product, 'LEAKAGE_INFO') ) else None
ECC_ERR_INFO = module_product.ECC_ERR_INFO if ( hasattr(module_product, 'ECC_ERR_INFO') ) else None
MULTIPLE_POWER_EXCEPTIONS = module_product.MULTIPLE_POWER_EXCEPTIONS if ( hasattr(module_product, 'MULTIPLE_POWER_EXCEPTIONS') ) else None
EQUIPMENT_AB_MAP = module_product.EQUIPMENT_AB_MAP if ( hasattr(module_product, 'EQUIPMENT_AB_MAP') ) else {}
CONFIG_INFO_MAP = {"fan": FAN_INFO, "psu": PSU_INFO,"led": LED_INFO}
SET_AVS_TEST =  module_product.SET_AVS_TEST if (hasattr(module_product, 'SET_AVS_TEST') ) else None
MAC_VOUT_EXPONENT =  module_product.MAC_VOUT_EXPONENT if (hasattr(module_product, 'MAC_VOUT_EXPONENT') ) else None
MAC_VOUT_MAP =  module_product.MAC_VOUT_MAP if (hasattr(module_product, 'MAC_VOUT_MAP') ) else None

import argparse
import os
import subprocess
choices_g = [
             "bmc_i18n_init",
             "bmc_get_cpu_info",
             "bmc_get_ddr_info",
             "bmc_get_emmc_info",
             "bmc_test_emmc_stress",
             "bmc_test_emmc_stress_result",
             "bmc_test_emmc_stress_stop",
             "bmc_test_emmc_check_occupancy_rate",
             "test_bmc_emmc_register",
             "test_bmc_emmc_life",
             "test_bmc_emmc_rw_random",
             "test_bmc_emmc_rw_order",
             "bmc_test_memtester_ddr_stress",
             "bmc_test_ddr_stress",
             "bmc_test_ddr_stress_result",
             "bmc_test_ddr_stress_stop",
             "bmc_get_dcdc_info",
             "bmc_test_peci",
             "bmc_test_cpu_error",
             "bmc_test_SML0",
             "bmc_test_MDIO",
             "bmc_test_MDIO_stress",
             "bmc_test_MDIO_continuous_stress",
             "bmc_test_get_fan_present",
             "bmc_test_get_fan_speed",
             "bmc_test_set_fan_speed_high_without_reset",
             "bmc_test_set_fan_speed_reset",
             "bmc_test_set_fan_speed_high",
             "bmc_test_set_fan_speed_middle",
             "bmc_test_set_fan_speed_low",
             "bmc_test_get_psu_rfu_info",
             "bmc_test_get_psu_info",
             "bmc_test_get_psu_present",
             "bmc_test_i2c_scan",
             "bmc_test_i2c_opt_scan",
             "bmc_test_get_power_fw_version",
             "bmc_test_psu_multiple_power_exceptions",
             "bmc_test_i2c_stress",
             "bmc_test_i2c_continuous_stress",
             "bmc_test_i2c_opt_continuous_stress",
             "bmc_test_spi_continuous_stress",
             "bmc_set_led",
             "bmc_led_control",
             "bmc_test_cpu_gpio",
             "bmc_test_cpu_opt_gpio",
             "bmc_get_e2_show_list",
             "bmc_get_e2_set_list",
             "bmc_get_e2_bin",
             "bmc_write_e2_bin",
             "bmc_cpld_check",
             "bmc_cpld_opt_check",
             "bmc_fpga_check",
             "test_get_fan_info",
             "test_get_psu_fru_info",
             "test_get_psu_present_info",
             "test_get_psu_info",
             "test_get_temperature",
             "test_get_busbar_position",
             "test_get_dcdc_info",
             "test_get_bmc_bios_version",
             "bmc_test_add_bios_flash_slave",
             "test_direction_check",
             "test_get_fru_info",
             "bmc_test_rtc",
             "bmc_test_clock",
             "bmc_test_netcard_smbus",
             "bmc_test_netcard_diagnosis",
             "bmc_test_get_netcard_intrpt_signal",
             "bmc_test_clear_netcard_intrpt_signal",
             "bmc_test_get_fan_drop",
             "bmc_test_moc_svid",
             "bmc_test_get_psu_drop",
             "bmc_test_clear_fan_drop",
             "bmc_test_clear_psu_drop",
             "bmc_test_service_stop",
             "bmc_test_service_start",
             "bmc_test_leakage",
             "bmc_test_ecc_error",
             "bmc_test_avs_set_xdpe",
             ]

rj_diag_parser = argparse.ArgumentParser()
rj_diag_args = rj_diag_parser.parse_args([])

#import inspect
#import ctypes

#on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
#if on_appengine and os.name == 'nt':
#    os.name = None
#import msvcrt
log_debug_flag = 0
def log_debug(a):
   if log_debug_flag == 1:
       print(a)

def log_error(a):
   if log_debug_flag == 1:
       print(a)
#几个压力测试项 后台运行需要
#import multiprocessing

grtdlog_dir= "/var/grtd"
grtdlog_name = grtdlog_dir +"/grtdtest.log"
kjlogmaxshow = 10
if not os.path.exists(grtdlog_dir):
    os.makedirs(grtdlog_dir)

SYSLOG_IDENTIFIER = "FACTEST"


LOGERROR = False
DEBUG = False
KAOJILOGPATH = "/var/grtd/"
KAOJILOGFILE = KAOJILOGPATH + "kjlog.log"
KAOJISTATUS = 1
ISKAOJI = 0
# CONFIG_NAME = "apptest.xml"
RTC_WAIT_TIME                   = 3
RTC_THRESHOLD_LOWER             = 3
RTC_THRESHOLD_UPPER             = 4
SUCCESS_TIPS                    = "PASS"

RETURN_KEY1       = "code"
RETURN_KEY2       = "msg"
#后台执行项 返回暂时 采用执行函数的返回，不直接打印pass
KT_K_BG_SUCCESS = 1
KT_K_BG_FAILD = -1
#RETURN_KEY1 : -1 表示有一个失败项 0 表示没有失败项  1用来指示后台运行成功
ERROR_RETURN      = {RETURN_KEY1 : -1, RETURN_KEY2 : "init error"}
SUCCESS_RETURN    = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
#顺利执行返回

SUCCESS_RETURN_EXCECUTE_OFFLINE = {RETURN_KEY1 : KT_K_BG_SUCCESS, RETURN_KEY2 : ("Background execution started").encode('utf-8')}
SUCCESS_RETURN_EXCECUTE_OFFLINE_END = {RETURN_KEY1 : KT_K_BG_SUCCESS, RETURN_KEY2 : ("End test").encode('utf-8')}
ERROR_RETURN_DETAIL  = {RETURN_KEY1 : -1, RETURN_KEY2 : []}

kj_result =[]
MENUID     = "menuid"
MENUPARENT = "parentid"
MENUVALUE  =  "value"
CHILDID    = "childid"
MENUITEMNAME = "name"
MENUITEMDEAL = "deal"
GOBACK  = "goBack"
GOQUIT  = "quit"

listindex=['1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','g','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
formatStringLevel1 = "%s.%s"
SYSINFOTIPS_FORMAT = "%30s : %s"
nosetrtc = 1

def bmc_i18n_init(json_str = None):
    ret = {"status":"err", "ret_info":"none"}
    language = "zh_CN"

    if json_str is not None:
        try:
            if isinstance(json_str, str):
                req_json = eval(json_str)
            else:
                req_json = json_str
            language = req_json.get("locale")
        except Exception as e:
            ret = {"status":"err", "ret_info":"none"}
    if language == "en_US" or language == "en":
        language = "en_US"
    else:
        language = "zh_CN"
    with open(LOCALE_DIR, "w+") as locale:
        locale.write(language)
        log_debug("set locale language: %s" % language)
    ret["status"] = "ok"
    return ret

def bmc_set_i18n():
    language = "zh_CN"
    try:
        with open(LOCALE_DIR, "r") as locale_file:
            language = locale_file.read().strip()
            if language == "en_US" or language == "en":
                language = "en_US"
            else:
                language = "zh_CN"
    except FileNotFoundError:
        language = "zh_CN"
    if language == "en_US":
        trans = gettext.translation('diag_bmc', locale_path, languages=['en_US'])
    else:
        trans = gettext.translation('diag_bmc', locale_path, languages=['zh_CN'])
    trans.install()

#发给sonic时，必须保持一定的格式，不能随便print
#在本地显示时，直接打印出来不会显得太卡顿
g_info_tmp_for_sonic = ""
def print_choose(str_tmp):
    if isinstance(str_tmp, str):
        pass
    else:
        str_tmp = str_tmp.decode('utf-8')
    if rj_diag_args.operations != None:
        global g_info_tmp_for_sonic
        g_info_tmp_for_sonic += str_tmp+"\n"
    else:
        print(str_tmp)
def print_sonic(RET):
    if rj_diag_args.operations != None:
        global g_info_tmp_for_sonic
        if g_info_tmp_for_sonic != "":
           RET[RETURN_KEY2] = g_info_tmp_for_sonic.encode('utf-8')
        print(RET)
        g_info_tmp_for_sonic = ""
    else:
        pass
def init_env():
    global g_info_tmp_for_sonic
    g_info_tmp_for_sonic = ""

#def ApplicationInstance():
#    global pidfile
#    pidfile = open(os.path.realpath(__file__), "r")
#    try:
#        fcntl.flock(pidfile, fcntl.LOCK_EX | fcntl.LOCK_NB) #创建一个排他锁,并且所被锁住其他进程不会阻塞
#    except:
#        print "已有一个程序在运行...."
#        sys.exit(1)

def RJPRINT(x):
    if LOGERROR:
        print(x)
    else:
        print(x)

def rji2cget(bus, devno, address, word=None):
    if word != None:
        command_line = "i2cget -f -y %d 0x%02x 0x%02x %s" % (bus, devno, address, word)
    else:
        command_line = "i2cget -f -y %d 0x%02x 0x%02x " % (bus, devno, address)
    retrytime = 6
    ret_t = ""
    for i in range(retrytime):
        ret, ret_t = log_os_system(command_line,0)
        if ret == 0:
            return ret, ret_t
        time.sleep(0.1)
    return ret, ret_t


def rji2cset(bus, devno, address, byte):
    command_line = "i2cset -f -y %d 0x%02x 0x%02x 0x%02x" % (
        bus, devno, address, byte)
    retrytime = 6
    ret_t = ""
    for i in range(retrytime):
        ret, ret_t = log_os_system(command_line,0)
        if ret == 0:
            return ret, ret_t
        time.sleep(0.1)
    return ret, ret_t

def rji2cdetect(bus, first=0x03, last=0x77):
    command_line = "i2cdetect -y %d 0x%02x 0x%02x" % (bus, first, last)
    retrytime = 6
    ret_t = ""
    for i in range(retrytime):
        ret, ret_t = log_os_system(command_line,0)
        if ret == 0:
            return ret, ret_t
        time.sleep(0.1)
    return ret, ret_t

def set_fan_watchdog(action):
    ret = 0
    ret_t = ""
    capacity = FAN_SPEED.get("capacity", 1)
    if capacity == 0: #不支持风扇狗开启/关闭
        return ret, ret_t
    tmp_product_name = get_full_product_name()
    if "-L-" in tmp_product_name or "-LC-" in tmp_product_name or "-LD-" in tmp_product_name:
        # not required for liquid device
        return ret, ret_t
    bus = FAN_SPEED["bus"]
    addr = FAN_SPEED["addr"]
    reg = FAN_SPEED.get("watchdogreg", 0x51)
    if action == 0: #关狗
        byte_value = 0
    else: #开狗
        byte_value = FAN_SPEED.get("watchdongenalble", 1) #ats oob寄存器位定义不同
    ret, ret_t = rji2cset(bus, addr, reg, byte_value)
    return ret, ret_t

def set_gpio(gpio, byte, open=0):
    cmd = ""
    if open != 0:
        if byte != 0:
            byte = 1
        cmd = ("echo %d > /sys/class/gpio/export"
            "&& echo out > /sys/class/gpio/gpio%d/direction"
            "&& echo %d > /sys/class/gpio/gpio%d/value") % (gpio, gpio, byte, gpio)
    else: # close
        cmd = ("echo 0 > /sys/class/gpio/gpio%d/value"
            "&& echo %d > /sys/class/gpio/unexport") % (gpio, gpio)
    ret, log = log_os_system(cmd, 0)
    return ret

def rji2cget32(bus, devno, address):
    retstr = "32:"
    retcode = 0
    for index in range(0,32) :
        command_line = "i2cget -f -y %d 0x%02x %d b" % (
            bus, devno,address+index)
        retrytime = 6
        ret_t = ""
        ret = -1
        for i in range(retrytime):
            ret, ret_t = log_os_system(command_line,0)
            if ret == 0:
                retstr += " "+ret_t
                break
            time.sleep(0.1)
        if (ret != 0):
            retcode = -1
            break
    my_log ("rji2cget32 retstr:" + retstr)
    return retcode, retstr
    
def quit():
    sys.exit(0)

def test_tbd():
    print((_("Unavailable")).encode('utf-8'))
    RET = SUCCESS_RETURN
    if rj_diag_args.operations != None:
       print(RET)
    return RET

def test_sys_reload():
    log_os_system("sync", 0)
    log_os_system("reboot", 0)


#菜单打印 菜单项带前面数字提示符
def printList(_list, id):
    try:
        RJPRINT("****************************************")
        for index in range(len(_list)):
            print(formatStringLevel1 %( listindex[index] , _list[index]["name"]))
        if id != 0:
            RJPRINT(("q.Back").encode('utf-8'))
        else:
            RJPRINT(("q.Exit").encode('utf-8'))

        RJPRINT("****************************************")
    except Exception as e:
        log_error(e)
        sys.exit(-1)

def test_all():
    RET =SUCCESS_RETURN
    for item in alltest:
        print("")
        print("=" * 12 + item[MENUITEMNAME] + "=" *12)
        RET = eval(item[MENUITEMDEAL])()
    return RET

#菜单打印
#  printMenu
#  param: list_t  菜单项列表
#         id      菜单id
#  当前菜单处理，目前该实现应该是叶子菜单项
#
def printMenu(list_t, id):
    global nosetrtc
    while True:
        try:
            printList(list_t, id)
            test = ("Please select:").encode('utf-8')
            try:
               str = raw_input(test)
            except Exception as ex:
               continue
            #bmc 中暂时不支持
            #str= getch(test)

            log_debug(("Select: %s" % str).encode('utf-8'))
            str = str.lstrip().lower()
            if str == "q":
                break#eval("goBack")(id)
            if str not in listindex:
                log_debug(("%s not in the menu" % str).encode('utf-8'));
                RJPRINT("\n\n")
                continue;
            else:
                print("=======================> %s <======================="%list_t[listindex.index(str)][MENUITEMNAME])
                log_debug(("Selected test item: %s id:%d" % (list_t[listindex.index(str)][MENUITEMNAME], id)).encode('utf-8'))

                if list_t[listindex.index(str)].has_key(CHILDID):
                    childid = list_t[listindex.index(str)][CHILDID]
                    RET = eval(list_t[listindex.index(str)][MENUITEMDEAL])(childid)
                else:
                    RET = eval(list_t[listindex.index(str)][MENUITEMDEAL])()

                if RET == None:
                   RJPRINT("\n\n")
                   continue

                if RET[RETURN_KEY1] == 0:
                    RJPRINT(RET[RETURN_KEY2])
                    RJPRINT("Test Result: Pass")
                    log_debug(("Menu test results:" + SUCCESS_TIPS).encode('utf-8'))
                elif RET[RETURN_KEY1] == 1:
                    RJPRINT(RET[RETURN_KEY2])
                else:
                    RJPRINT("Test Result: Fail")
                    log_debug(("[%s]Test results:" % list_t[listindex.index(str)][MENUITEMNAME] + 'error').encode('utf-8'))
                    #log_debug(RET[RETURN_KEY2])
           # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                RJPRINT("\n\n")
        except IndexError as d:
            print(("\n\n Invalid input.\n\n").encode('utf-8'))
        except Exception as e:
            print(e)
            #log_debug(e)
            #RJPRINTERR("\n\n abnormal \n\n" )

def getMenuFromList(list, id):
    for key in list:
        if key[MENUID] == id:
            return key[MENUVALUE],True
    return 0, False

def getParentIdMenuFromList(list, id):
    for key in list:
        if key[MENUID] == id and key.has_key(MENUPARENT):
            return key[MENUPARENT],True
    return -1, False

def getDriverFromGlobal(name):
    for key in testdriver:
        if key["name"] == name:
            return key,True
    return "-1", False

def i2ccheckValue(ret1 , ret2, type):
    if type == 1 and ret1 == ret2:
        return True
    elif type == 2 and ret1 == "SUCCESS":
        return True
    else:
        return False


# 菜单： 单项测试
def test_signal(id):
    startMenu(id)

#不论大小比较字符串
def astrcmp(str1,str2):
    return str1.lower()==str2.lower()

#led check输入确认
def get_led_inputcheck(LED,STATE):
    err = 0;
    while True:
        print(("%s switch to %s [Yes/No]:"%(LED,STATE)).encode('utf-8')),
        str = raw_input("")
        if astrcmp(str, "y") or astrcmp(str, "ye") or astrcmp(str, "yes") or astrcmp(str, ""):
            return True
        elif astrcmp(str, "n") or astrcmp(str, "no"):
            return False


# 菜单：系统配置
def test_sysconfig(id):
    startMenu(id)

#设置debug等级
def test_setdebug():
    global DEBUG
    DEBUG = not DEBUG
    return SUCCESS_RETURN

#根据id获取菜单
def startMenu(id):
    list,code = getMenuFromList(menuList, id)
    if code == False:
        log_error(("Incorrect file structure").encode('utf-8'))
        sys.exit(1)
    log_debug(("Obtain corresponding menu list based on ID").encode('utf-8'))
    printMenu(list, id)

def keyboardTest():
    while True:
        log_debug("123")

def startThread():
    thread = threading.Thread(target=keyboardTest)
    thread.setDaemon(True)
    thread.start()

#开始
def start():
    startMenu(0)

#menu调用
def goBack(id):
    log_debug(str(id))
    parentid,code = getParentIdMenuFromList(menuList, id)
    if code == False:
        log_error(("No parent node").encode('utf-8'))
        sys.exit(1)
    list,code = getMenuFromList(menuList, parentid)
    if code == False:
        log_error(("Incorrect file structure").encode('utf-8'))
        sys.exit(1)
    startMenu(parentid)

#获取full_product_name
def get_full_product_name():
    full_product_path = "/etc/device/fullproductname"
    if not os.path.exists(full_product_path):
        return None
    cmd = "cat %s"%(full_product_path)
    ret,log=log_os_system(cmd,0)
    if ret !=0 or len(log) < 1:
        return None
    else:
        return log

# ====================================
# 执行shell命令
# ====================================
def get_sys_execute(str):
    #function 1
    result = os.popen(str)
    res = result.read()
    for line in res.splitlines():
        print(line)
    '''
    #function 2
    output = command(str)
    print  output


    #function 3
    p = subprocess.Popen('ps aux',shell=True,stdout=subprocess.PIPE)
    out,err = p.communicate()
    for line in out.splitlines():
       print line
    '''
#mylog
def my_log(txt):
    if DEBUG == True:
        print("[RUIJIE]:"),
        print(txt)
    return
# ====================================
# 执行shell命令
# ====================================
def log_os_system(cmd, show):
    my_log ('         Run :'+ cmd)
    status, output = command(cmd)
    my_log (" with result :" + str(status))
    my_log ("      output :" + output)
    if status:
        log_error('Failed :'+cmd)
        if show:
            print('Failed :'+ cmd)
    return  status, output
# ====================================
# 拷机初始化
# ====================================
def kj_init():
    global KAOJILOGFILE
    time1 = time.time();
    timeArraystart = time.localtime(time1)
    otherStyleTime = time.strftime("%m-%d_%H.%M", timeArraystart)
    KAOJILOGFILE = "/var/grtd/kjlog_%s.log" % otherStyleTime
    log_debug(("Burn-in log created:" + KAOJILOGFILE).encode('utf-8'))

    file = open(KAOJILOGFILE,'w')
    file.close()

# ====================================
# 拷机结果保存
# ====================================
def KJERSULT(log):
    global KAOJILOGFILE
    with open(KAOJILOGFILE, 'w') as f:
         print >> f, log
# ====================================
# 拷机错误数组中是否存在该测试项
# ====================================
def kj_isexit(name, result):
    for item in result:
        #log_debug(item)
        if name == item["name"]:
#            log_debug(name + " in result")
            return True
    return False

# ====================================
# 返回错误数组中存在的测试项信息
# ====================================
def kj_find_result(name , result):
    for item in result:
        if name == item["name"]:
#            log_debug(name + "exist")
            return item
    return None


# ====================================
# 拷机测试
# ====================================
def test_loop():
    global kj_result
    global KAOJISTATUS
    global ISKAOJI
    kj_result = []
    real_kj_result ={"starttime":"","endtime":"","result":[] ,"loop":0}
    KAOJISTATUS = 1
    kj_init()
    #创建拷机文件
    loop = 1
    isloopprint = True
    try:
        time1 = time.time();
        timeArraystart = time.localtime(time1)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArraystart)
        real_kj_result["starttime"] = otherStyleTime
        while True:
            ISKAOJI = 1
            for item in looptest:
                kj_itemresult = {"name":"test", "loop":[], "error":[]}
                print("\n\n",item[MENUITEMNAME])
                print("=" * 60)
                log_debug(" ")
                log_debug(("==========%s Start============" % item[MENUITEMNAME]).encode('utf-8'))
                RET = eval(item[MENUITEMDEAL])()
                #log_debug(RET)
                if RET[RETURN_KEY1] != 0:
                    if kj_isexit(item[MENUITEMNAME], kj_result):
                        it = kj_find_result(item[MENUITEMNAME], kj_result)
                        #log_debug(it)
                        it["loop"].append(loop)
                        it["error"].append(RET[RETURN_KEY2])
                    else:
                        kj_itemresult["name"] = item[MENUITEMNAME]
                        kj_itemresult["loop"].append(loop)
                        kj_itemresult["error"].append(RET[RETURN_KEY2])
                        #log_debug(kj_itemresult)
                        kj_result.append(kj_itemresult)
                log_debug(("==========%s End============" % item[MENUITEMNAME]).encode('utf-8'))
            time2 = time.time();
            timeArrayend = time.localtime(time2)
            otherStyleTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArrayend)
            real_kj_result["endtime"] = otherStyleTime1
            real_kj_result["result"] = kj_result
            real_kj_result["loop"] = loop
            #写文件
            KJERSULT(real_kj_result)
            loop += 1
            #isloopprint = True
            #time.sleep(5)
            if KAOJISTATUS == 0:
                break;
        ISKAOJI = 0
    except Exception as e:
        print(e)
        log_error(e)
    return {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}

def file_name(file_dir):
    L=[]
    for dirpath, dirnames, filenames in os.walk(file_dir):
        for file in filenames :
            if file.startswith("kjlog"):
                L.append(os.path.join(dirpath, file))
    datas =sorted(L,reverse=True)
    return datas


def readKjLog(filename):
    str1 =""
    with open(filename, 'r') as f:
         str1 = f.read()
    val_t = eval(str1)
    ret = val_t["result"]
    RJPRINT(("=====================================Burn-in results=========================================================").encode('utf-8'))
    RJPRINT(("Start time: %s \r\nEnd time: %s \r\nTotal rounds: [%d]"% (val_t["starttime"], val_t["endtime"], val_t["loop"])).encode('utf-8'))

    if len(ret) > 0:
        RJPRINT((">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Failed test items:").encode('utf-8'))
    else:
        RJPRINT(("No failed test items in this burn-in").encode('utf-8'))
    for item in ret:
        RJPRINT(("%s  [%s] "% ("Test item:", item["name"])).encode('utf-8'))
        loopstr = ""
        for loop in item["loop"]:
            loopstr += " %d " % loop
        RJPRINT(("Failed rounds: %s" % loopstr).encode('utf-8')),
        for loop in item["loop"]:
            print(("Error in round [%d]:" % loop).encode('utf-8'))
            index = item["loop"].index(loop)
            errmsg = item["error"][index]
            if isinstance(errmsg, list):
                for test in errmsg:
                    RJPRINT("   %s :  " % test["name"])
                    for case_ret  in test["errmsg"]:
                        RJPRINT("           {name}   {error}".format(**case_ret) )
            elif isinstance(errmsg, str):
                RJPRINT("{0}   {1}".format(item["name"] , errmsg))
            RJPRINT("\n")
    RJPRINT("\n\n\n\n")

# ====================================
# 拷机日志数组选择
# ====================================
def printKJList():
    readtips = True
    L = file_name(KAOJILOGPATH)
    if len(L) <= 0:
        RJPRINT(("\n\nno Burn-in log\n\n").encode('utf-8'));
        return
    while(readtips):
        index = 0
        for x in L:
            print("%d. %s"%(index, os.path.basename(x)))
            index += 1
            if (index >= kjlogmaxshow):
                break
        print(("q. %s"%("Back")).encode('utf-8'))
        test = ("Please select:").encode('utf-8')
        str= getch(test)
        print(" %s" % str)
        #log_debug("选择:%s" % str)
        str = str.lstrip().lower()
        if str == "q":
            readtips = False
        elif (int(str) >= 0 and  int(str) <= index):
            readKjLog(L[int(str)])
        else:
            log_debug(("Invalid input item").encode('utf-8'))

# ==================================================
# 拷机结果删除
# ==================================================
def test_loop_delete():
    L = file_name(KAOJILOGPATH)
    if len(L) <=0:
        RJPRINT(("No burn-in record").encode('utf-8'))
        return {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    for file in L:
        os.remove(file)    #删除文件
    return {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}

# ====================================
# 拷机结果查看
# ====================================
def test_loop_read():
    printKJList();
    return {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}

# ====================================
# 设置日志等级
# ====================================
def test_log_setlevel(name):
    logger = logging.getLogger()    # initialize logging class
    logger.setLevel(levelNames[name])  # default log level

def test_log_critical():
    test_log_setlevel("CRITICAL")
def test_log_debug():
    test_log_setlevel("DEBUG")
def test_log_error():
    test_log_setlevel("ERROR")
def test_log_info():
    test_log_setlevel("INFO")
def test_log_notset():
    test_log_setlevel("NOTSET")
def test_log_warning():
    test_log_setlevel("WARNING")

#日志输出等级菜单
def test_loginfolevel():
    logger = logging.getLogger()    # initialize logging class
    print(("Current debug level: %s" % levelNames[logger.level]).encode('utf-8'))
    startMenu(3)

# ====================================
# 测试项:校验文件MD5
# ====================================
def checkFileMD5(filename):
     if not os.path.isfile(filename):
         return
     myhash = hashlib.md5()
     f = file(filename,'rb')
     while True:
         b = f.read(8096)
         if not b :
             break
         myhash.update(b)
     f.close()
     return myhash.hexdigest()



pidfile = 0
############################################################################################
##  文件锁
############################################################################################
def ApplicationInstance():
    global pidfile
    #pidfile = open(os.path.realpath(__file__), "r")
    pidfile = open("/tmp/single_bmc", "a")
    try:
        fcntl.flock(pidfile, fcntl.LOCK_EX | fcntl.LOCK_NB) #创建一个排他锁,并且所被锁住其他进程不会阻塞
    except:
        if rj_diag_args.operations != None:
            print({RETURN_KEY1 : -1,  RETURN_KEY2 : ("A program is already running....").encode('utf-8')})
        else:
            print(("启动失败，请确确认:\r\n\
                   1、是否已有另一个diag_bmc进程在本设备上运行？\r\n\
                   2、是否已有diag进程在sonic端运行？\r\n\
                   3、是否sonic端的diag进程被强行kill？如果是，请重新启动diag并正常退出。\r\n").encode('utf-8'))
        sys.exit(1)

def unlockInstance():
    global pidfile
    fcntl.flock(pidfile,fcntl.LOCK_UN)
def fac_init_setmac():
    if getsyseeprombyId(TLV_CODE_PRODUCT_NAME) == None or getsyseeprombyId(TLV_CODE_SERIAL_NUMBER) == None or\
       getsyseeprombyId(TLV_CODE_MAC_BASE) == None or getsyseeprombyId(TLV_CODE_DEVICE_VERSION) == None :
        log_debug(("Need to reset setmac").encode('utf-8'))
        return False
    return True

thread_test_ddr = None;
thread_test_emmc = None;
def background_test_stress(thread_hander, test_result_file, cmd):
    RET = {RETURN_KEY1 : KT_K_BG_SUCCESS, RETURN_KEY2 : ""}
    if "memtester" in cmd:
        tool = "memtester"
    else:
        tool = "stressapptest"
    ret, log = log_os_system("which %s" % tool, 0)

    if len(log):
        if thread_hander != None:#对于sonic 调用来说，这个条件永远不成立，所以判断逻辑放在sonic端
            RET[RETURN_KEY2] = (_("Already have background execution task, please check the test results or terminate the previous test task")).encode('utf-8')
        else:
            RET[RETURN_KEY2] = (_("Background execution started")).encode('utf-8')
            with open(test_result_file, "w+") as f:
                #thread_hander = subprocess.Popen("stressapptest -M 100 -s 10",shell=True,stdout=f)
                thread_hander = subprocess.Popen(cmd, shell=True, stdout=f)
    else:
        RET[RETURN_KEY2] = "no %s cmd" % tool
    if rj_diag_args.operations != None:
       print({"RET":RET,"pid":(thread_hander.pid)})
       RET = {"RET":RET,"pid":(thread_hander.pid)}
    return thread_hander,RET

def stop_makesure():
    while True:
        print((_("Forced termination will not allow viewing results, continue? [Yes/No]:")).encode('utf-8')),
        str = raw_input("")
        if astrcmp(str, "y") or astrcmp(str, "ye") or astrcmp(str, "yes") or astrcmp(str, ""):
            return True
        elif astrcmp(str, "n") or astrcmp(str, "no"):
            return False

def background_test_stress_stop(thread_hander, pid = -1):
    RET = {RETURN_KEY1 : KT_K_BG_SUCCESS, RETURN_KEY2 : ""}
    if rj_diag_args.operations == None: #本地运行
        if thread_hander == None:
            RET[RETURN_KEY2] = (_("Background test not started")).encode('utf-8')
            if rj_diag_args.operations != None:
               print_sonic(RET)
            return thread_hander,RET
        #if stop_makesure():强制执行，后续可能需要增加确认
            #该方法并不能杀死
        if not stop_makesure():
            return thread_hander,{RETURN_KEY1 : 1, RETURN_KEY2 : (_("Canceled")).encode('utf-8')}
        thread_hander.terminate()

        cmd = "kill -9 %d"%(thread_hander.pid + 1)
    else:#由sonic 下发
        cmd = "kill -9 %d"%(pid)
    #不管输出
    ret, log = log_os_system(cmd, 0)
    RET[RETURN_KEY2] = (_("This background test has been terminated")).encode('utf-8')
    thread_hander = None
    if rj_diag_args.operations != None:
       print_sonic(RET)
    return thread_hander, RET

def  background_test_stress_result(thread_hander, test_result_file, pid = -1):
    RET = {RETURN_KEY1 : 1, RETURN_KEY2 :""}

    if rj_diag_args.operations == None: #本地运行
        if thread_hander == None:
           print((_("Background test not started, no test results")).encode('utf-8'))
           print_sonic(RET)
           return thread_hander, RET
        pid = thread_hander.pid

    #判断测试进程是否已经结束，防止无谓等待
    cmd = r'ps | grep %d | grep -v grep | grep -v "\[" | grep -E "stressapptest|memtester"' % pid
    #print cmd

    ret, log = log_os_system(cmd, 0)
    if len(log):
        if rj_diag_args.operations != None: #本地运行
            RET[RETURN_KEY1] = -1
        try:
            if "memtester" in log:
                ddr_size = (log.split()[-2]).split("M")[0]
                # 测试耗时受到CPU使用情况影响，正常情况下约1s/M，
                take_time = "%.f" % (int(ddr_size) / 60)
            else:
                take_time = 1
        except:
            err_log = "error occurred while calculating take_time: ddr_size %s" % ddr_size
            log_os_system("logger -p debug %s" % err_log, 0)
            take_time = "unknown"
        RET[RETURN_KEY2] = (_("Test not finished, about %smins remaining, please check results later") % take_time).encode('utf-8')
        print_sonic(RET)
        return thread_hander, RET

    bufferSize = 5000
    input = ""
    resuult = ""

    try:
       file = os.open(test_result_file, os.O_RDONLY | os.O_NONBLOCK);
       input = os.read(file, bufferSize);
       resuult = input
       os.close(file)
    except OSError as err:
        if err.errno == 11:#为空，小概率到这里
            resuult = (_("No data")).encode('utf-8')
            os.close(file)
        else:
            raise err;

    RET[RETURN_KEY2] = resuult
    thread_hander = None;
    if rj_diag_args.operations != None:
       print_sonic(RET)
    return thread_hander, RET


ddr_test_result_file = "/var/log/ddr_test_result"
emmc_test_result_file = "/var/log/emmc_test_result"

def get_current_free_memory():
    free_cmd = "free |grep Mem |awk '{print $4}'"
    ret_status, log = log_os_system(free_cmd, 0)
    if ret_status != 0:
        return -1
    free_mem = int(int(log)/1000)
    return free_mem

def release_cached_memory():
    times = 0
    retry_times = 5
    wait_time = 3
    sync_cmd = "sync && sync"
    sync_ret, sync_log = log_os_system(sync_cmd, 0)
    if sync_ret != 0:
        return 0
    release_cmd = "echo 3 > /proc/sys/vm/drop_caches"
    while times < retry_times:
        release_ret, release_log = log_os_system(release_cmd, 0)
        if release_ret != 0:
            times = retry_times
            break
        time.sleep(wait_time)
        free_mem = get_current_free_memory()
        if free_mem == -1:
            times = retry_times
            break
        if free_mem > 50:
            break
        times = times + 1
    if times >= retry_times:
        return 0
    return free_mem

def get_free_memory(rule = "default"):
    free_mem = get_current_free_memory()
    if free_mem == -1:
        return 0
    if free_mem < 50:
        free_mem = release_cached_memory()
        if free_mem == 0:
            return 0
    if free_mem > 150 and rule != "max_size":
        return 100
    else:
        return free_mem -35

def bmc_test_memtester_ddr_stress():
    memtester_info = ALI_BMC.get("DDR_STRESS", None)
    return bmc_test_ddr_stress(memtester_info)

def bmc_test_ddr_stress(memtester_info = None):
    global thread_test_ddr
    size_rule = "default"
    ddr_stress = memtester_info
    if ddr_stress != None:
        memtester_preset = ddr_stress["memtester_preset"]
        cmd = memtester_preset + "exec memtester {}M 1"
        size_rule = "max_size"
    else:
        cmd = "stressapptest -M {} -s 60"
    free_mem = get_free_memory(size_rule)
    cmd = cmd.format(free_mem)
    global ddr_test_result_file
    test_result_file = ddr_test_result_file
    thread_test_ddr, ret =  background_test_stress(thread_test_ddr, test_result_file, cmd)
    return ret

def bmc_test_ddr_stress_stop( pid = -1 ):
    global thread_test_ddr
    test_result_file = ddr_test_result_file
    thread_test_ddr, ret = background_test_stress_stop(thread_test_ddr, int(pid))
    return ret

def bmc_test_ddr_stress_result( pid = -1 ):
    global thread_test_ddr
    global ddr_test_result_file
    test_result_file = ddr_test_result_file
    thread_test_ddr, ret = background_test_stress_result(thread_test_ddr, test_result_file, int(pid) )
    return ret

def bmc_test_emmc_stress():
    free_mem = get_free_memory()
    global thread_test_emmc
    test_result_file = emmc_test_result_file
    cmd = "stressapptest -f /var/log/data1 -f /var/log/data2 --filesize 20m --read-block-size 1024 -M %sM"%free_mem
    thread_test_emmc, ret =  background_test_stress(thread_test_emmc, test_result_file, cmd)
    return ret

def bmc_test_emmc_stress_stop( pid = -1 ):
    global thread_test_emmc
    test_result_file = emmc_test_result_file
    thread_test_emmc, ret = background_test_stress_stop(thread_test_emmc, int(pid))
    return ret
def bmc_test_emmc_stress_result( pid = -1 ):
    global thread_test_emmc
    test_result_file = emmc_test_result_file
    thread_test_emmc, ret = background_test_stress_result(thread_test_emmc, test_result_file, int(pid))
    return ret

def bmc_test_emmc_check_occupancy_rate():
    errtotal = 0
    sign = "%"
    RET = {RETURN_KEY1 : -1, RETURN_KEY2 : ""}
    cmd1 = "df |grep '/dev/mmcblk*' | awk 'NR==1{print}' | awk '{print $3}'"
    cmd2 = "df |grep '/dev/mmcblk*' | awk 'NR==1{print}' | awk '{print $2}'"
    cmd3 = "df |grep '/dev/mmcblk*' | awk 'NR==2{print}' | awk '{print $3}'"
    cmd4 = "df |grep '/dev/mmcblk*' | awk 'NR==2{print}' | awk '{print $2}'"
    cmd5 = "df |grep '/dev/mmcblk*' | grep '/var' | awk '{print $3}'"
    cmd6 = "df |grep '/dev/mmcblk*' | grep '/var' | awk '{print $2}'"

    ret1, emmc1_used = log_os_system(cmd1, 0)
    if ret1 != 0 or len(emmc1_used) <= 0:
        print_choose((_("Command execution error [%s]") % cmd1).encode('utf-8'))
        errtotal -= 1

    ret2, emmc1_total = log_os_system(cmd2, 0)
    if ret2 != 0 or len(emmc1_total) <= 0:
        print_choose((_("Command execution error [%s]") % cmd2).encode('utf-8'))
        errtotal -= 1

    ret3, emmc2_used = log_os_system(cmd3, 0)
    if ret3 != 0:
        print_choose((_("Command execution error [%s]") % cmd3).encode('utf-8'))
        errtotal -= 1

    ret4, emmc2_total = log_os_system(cmd4, 0)
    if ret4 != 0:
        print_choose((_("Command execution error [%s]") % cmd4).encode('utf-8'))
        errtotal -= 1

    ret5, var_log_used = log_os_system(cmd5, 0)
    if ret5 != 0 or len(var_log_used) <= 0:
        print_choose((_("Command execution error [%s]") % cmd5).encode('utf-8'))
        errtotal -= 1

    ret6, var_log_total = log_os_system(cmd6, 0)
    if ret6 != 0 or len(var_log_total) <= 0:
        print_choose((_("Command execution error [%s]") % cmd6).encode('utf-8'))
        errtotal -= 1

    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    else:
        if len(emmc2_used) <= 0:
            emmc_used_total = float(emmc1_used) / float(emmc1_total) * 100
        else:
            emmc_used_total = (float(emmc1_used) + float(emmc2_used)) / (float(emmc1_total) + float(emmc2_total)) * 100
        var_log_used_total = float(var_log_used) / float(var_log_total) * 100
        print_choose((_("emmc usage rate: %.1f%s")%(emmc_used_total, sign)).encode('utf-8'))
        print_choose((_("/var/log usage: %.1f%s")%(var_log_used_total, sign )).encode('utf-8'))
        if emmc_used_total > 40 or var_log_used_total > 40:
            print_choose((_("Items with over 40% usage")).encode('utf-8'))
            RET[RETURN_KEY1] = -1
        else:
            RET[RETURN_KEY1] = 0    
    print_sonic(RET)
    return RET

def print_register(value):
    index = 0
    lineStr = ""
    print_choose("       00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f")
    if "0x" in value:
        value = value.replace("0x","")
    for val in value:
        if index % 32 == 0:
            if len(lineStr) != 0:
                print_choose(lineStr)
            lineStr = "%04x: " % int(index/2)
        if index % 2 == 0 :
            lineStr += " "
        lineStr += val
        index += 1
    print_choose(lineStr + "\n")

def test_bmc_emmc_register():
    u'''eMMC寄存器值读取'''
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    totalerr = 0
    if EMMC_REGISTER == None:
        RET[RETURN_KEY1] = -1
        print_choose((_("get eMMC register configuration error")).encode('utf-8'))
        print_sonic(RET)
        return RET
    for item in EMMC_REGISTER:
        name = item.get('name')
        location = item.get('location')
        print_choose("%s : " % name)
        cmd = "cat %s" % location
        ret_cat, log_cat = log_os_system(cmd, 0)
        if ret_cat != 0 or len(log_cat) == 0:
            totalerr -= 1
            print_choose((_("Failed to read eMMC register value %s (%s): %s\n") % (name, cmd,log_cat)).encode('utf-8'))
        else:
            print_register(log_cat)
    if totalerr < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def test_bmc_emmc_life():
    u'''eMMC寿命检测'''
    RET = {RETURN_KEY1 : -1,  RETURN_KEY2 : ""}
    if EMMC_REGISTER == None:
        print_choose((_("get eMMC register configuration error")).encode('utf-8'))
        print_sonic(RET)
        return RET
    for item in EMMC_REGISTER:
        name = item.get('name')
        if name != "EXT_CSD":
            continue
        location = item.get('location')
        cmd = "cat %s" % location
        ret_cat, log_cat = log_os_system(cmd, 0)
        if ret_cat != 0 or len(log_cat) == 0:
            print_choose((_("get eMMC register configuration error") % (name, cmd, log_cat)).encode('utf-8'))
            print_sonic(RET)
            return RET
        else:
            val = log_cat
            val_268 = val[268*2 : 269*2]
            if len(val_268) != 2:
                print_choose((_("Failed to read EXT_CSD register byte 268: %s") % val_268).encode('utf-8'))
                print_sonic(RET)
                return RET
            print_choose("EXT_CSD byte 268 = 0x%s" % val_268)
            val_268_d = int(val_268, 16)
            if val_268_d == 0:
                print_choose((_("Warning: undefined lifetime value detected")).encode('utf-8'))
            elif val_268_d == 1:
                print_choose((_("eMMC lifetime normal")).encode('utf-8'))
                RET[RETURN_KEY1] = 0
            else:
                print_choose((_("Warning: eMMC lifetime used exceeds 10%")).encode('utf-8'))
            print_sonic(RET)
            return RET
    print_choose((_("eMMC register EXT_CSD configuration not found")).encode('utf-8'))
    print_sonic(RET)
    return RET

def test_bmc_emmc_rw_random():
    return test_bmc_emmc_rw("randrw")

def test_bmc_emmc_rw_order():
    return test_bmc_emmc_rw("ordrw")

def test_bmc_emmc_rw(param):
    u'''eMMC读写检测'''
    RET = {RETURN_KEY1 : -1,  RETURN_KEY2 : ""}
    emmc_fio_test_file = "/var/log/fio_test"
    if EMMC_FIO == None:
        print_choose((_("get eMMC register configuration error")).encode('utf-8'))
        print_sonic(RET)
        return RET
    emmc_fio_case = EMMC_FIO.get(param, None)
    if emmc_fio_case == None:
        print_choose((_("Cannot find specified eMMC FIO configuration")).encode('utf-8'))
        print_sonic(RET)
        return RET
    for item in emmc_fio_case:
        rw = item.get("rw", None)
        bs = item.get("bs", None)
        rwmixwrite = item.get("rwmixwrite", None)
        iodepth = item.get("iodepth", None)
        size = item.get("size", None)
        name = item.get("name", None)
        verify = item.get("verify", None)
        do_verify = item.get("do_verify", None)
        cmd_fio = "fio -rw=%s -bs=%s -rwmixwrite=%d -iodepth=%d -size=%s -verify=%s -do_verify=%d -verify_fatal=1 -verify_state_save=0 -name=%s -filename=%s" % \
            (rw, bs, rwmixwrite, iodepth, size, verify, do_verify, name, emmc_fio_test_file)
        ret_fio, log_fio = log_os_system(cmd_fio, 0)
        if ret_fio != 0 or len(log_fio) == 0:
            cmd_rm = "rm %s" % emmc_fio_test_file
            ret_rm, log_rm = log_os_system(cmd_rm, 0)
            print_choose((_("%s test failed (%s): %s") % (name, cmd_fio, log_fio)).encode('utf-8'))
            print_sonic(RET)
            return RET
        else:
            result = name + " :\n"
            index = log_fio.find("read", 0)
            if index != -1:
                result += "\tRead : "
                iops_index = log_fio.find("iops=", index)
                if iops_index == -1:
                    iops_index = log_fio.find("IOPS=", index)
                if iops_index != -1:
                    iops = log_fio[iops_index : log_fio.find(",", iops_index)]
                    result += iops + "\n"
            index = log_fio.find("write", 0)
            if index != -1:
                result += "\tWrite : "
                iops_index = log_fio.find("iops=", index)
                if iops_index == -1:
                    iops_index = log_fio.find("IOPS=", index)
                if iops_index != -1:
                    iops = log_fio[iops_index : log_fio.find(",", iops_index)]
                    result += iops + "\n"
            print_choose(result)
    cmd_rm = "rm %s" % emmc_fio_test_file
    ret_rm, log_rm = log_os_system(cmd_rm, 0)
    RET[RETURN_KEY1] = 0
    print_sonic(RET)
    return RET

def bmc_get_cpu_info():
    RET = {RETURN_KEY1 : -1, RETURN_KEY2 : ""}
    cmd = r"cat /proc/cpuinfo | grep 'Revision\|Serial' -v"

    ret, log1 = log_os_system(cmd, 0)
    if ret != 0 or len(log1) <= 0:
        RET[RETURN_KEY2] = (_("Command execution error [%s]") % cmd).encode('utf-8')
        RET[RETURN_KEY1] = -1
    else:
        RET[RETURN_KEY2] = log1
        RET[RETURN_KEY1] = 0
    if rj_diag_args.operations != None:
       print_sonic(RET)
    return RET

def bmc_get_ddr_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    cmd = "cat /proc/meminfo "

    ret, log1 = log_os_system(cmd, 0)
    if ret != 0 or len(log1) <= 0:
        RET[RETURN_KEY2] = (_("Command execution error [%s]") % cmd).encode('utf-8')
        RET[RETURN_KEY1] = -1
    else:
        RET[RETURN_KEY2] = log1
        RET[RETURN_KEY1] = 0
    if rj_diag_args.operations != None:
       print_sonic(RET)
    return RET
def bmc_get_emmc_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    cmd = "fdisk -l"
    cap_threshoud = {"high":9000,"low":7000}

    ret, log1 = log_os_system(cmd, 0)
    if ret != 0 or len(log1) <= 0:
        RET[RETURN_KEY2] = (_("Command execution error [%s]") % cmd).encode('utf-8')
        RET[RETURN_KEY1] = -1
    else:
        data = re.findall(r".*/dev/mmcblk0:\s+(\d+)\s+MB.*",log1)
        if len(data) != 1:
            RET[RETURN_KEY2] = (_("Failed to get capacity information")).encode('utf-8')
            RET[RETURN_KEY1] = -1
        else:
            cap = int(data[0])
            RET[RETURN_KEY2] = (_("EMMC capacity is %d MB")%(cap)).encode('utf-8')
            if cap in range(cap_threshoud["low"], cap_threshoud["high"]):
                RET[RETURN_KEY1] = 0
            else:
                RET[RETURN_KEY1] = -1

    if rj_diag_args.operations != None:
       print_sonic(RET)
    return RET

#暂时先写死 hwmon 的index
#def find_hwmon_index():
#    cmd = "ls /sys/class/hwmon/ -l"
#    dic_rt = {};
#    ret, log1 = log_os_system(cmd, 0)
#    print log1
#    if ret == 0 and len(log1):
#        log1 = log1.lstrip()
#        arr = log1.split("\n")
#        for arri in arr:
#           print arri
#           line_temp = re.search("(\d+)\-00(\d\w)/hwmon\/hwmon(\d+)",arri)
#           print "@@@"
#           if line_temp is None:
#              continue
#           bus = line_temp.group(1)
#           addr = line_temp.group(2)
#           index = int(line_temp.group(3))
#           dic_rt[index] = {"bus":bus,"addr":addr}
#        print dic_rt
#        return dic_rt
#    return None

def get_dcdc_1_info(dev):
    #先确认正确的地址
    cmd = "cat /sys/bus/i2c/devices/*/%s"%(dev["file"])

    ret, log = log_os_system(cmd, 0)
    if "can't open" in log:
        return -1;
    else:
        return int(log)

def bmc_get_dcdc_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    return RET

def bmc_test_cpu_error():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    ls_ret, ls_log = log_os_system("ls /var/log/mce 2>/dev/null", 0)
    if len(ls_log) == 0:
        print_choose("no exception occurred in CPU")
        print_sonic(RET)
        return RET

    # The existence of files indicates that the CPU has experienced an exception
    RET[RETURN_KEY1] = -1

    ret, log = log_os_system("which cpuparser", 0)
    if len(log):
        mce_cmd = "cpuparser mce"
        peci_cmd = "cpuparser peci"
    else:
        RET[RETURN_KEY2] = "no cpuparser cmd"
        print_sonic(RET)
        return RET
    try:
        print_choose("%s:" % mce_cmd)
        mce_ret, mce_log = log_os_system(mce_cmd, 0)
        print_choose(mce_log)
        print_choose("\n" + "%s:" % peci_cmd)
        peci_ret, peci_log = log_os_system(peci_cmd, 0)
        print_choose(peci_log)
    except:
        print_choose("exception occurred in the parsing process")
    print_sonic(RET)
    return RET

def bmc_test_peci():
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    cmd = "systemctl stop cpu-error-gpio;" #关闭打开/dev/aspeed-peci的服务
    log_os_system(cmd, 0)
    for i in range(5):
        ret, log = log_os_system("dfd_debug peci_pkgcfg_rd 0 0", 0)
        if ret or ALI_BMC["PCIE_CHK_STR"] not in log:
            RET[RETURN_KEY2] = (_("Failed to access CPU through PECI, %s")%log).encode('utf-8')
            RET[RETURN_KEY1] = -1
        else:
            RET[RETURN_KEY2] =  (_("Succeeded accessing CPU through PECI")).encode('utf-8')
            break
    cmd = "systemctl start cpu-error-gpio;" #重新打开/dev/aspeed-peci的服务
    log_os_system(cmd, 0)
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_test_SML0():
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    SML_INF = ALI_BMC.get("SML", None)
    errtotal = 0
    if SML_INF == None:
        SML_INF = [{"name": "SML1", "bus": 1, "addr": 0x16, "offset": 0x00}]
    for dev in SML_INF:
        sml = dev["name"]
        bus = dev["bus"]
        addr = dev["addr"]
        offset = dev["offset"]
        special = dev.get("special", None)
        if special != None:
            cmd = "i2cget -y -f %d %s" % (bus, addr)
            ret, log = log_os_system(cmd, 0)
        else:
            ret , log = rji2cget(bus,addr,offset)
        if "Error: Read failed" in log:
            RET[RETURN_KEY2] = print_choose((_("%s test failed") % sml).encode('utf-8'))
            errtotal -= 1
        else:
            RET[RETURN_KEY2] = print_choose((_("%s test passed, read register 0x%02x value %s")% (sml, offset, log)).encode('utf-8'))
    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_test_MDIO(test_times = 1):
    if ALI_BMC.get("MDIO_8367", 0) == 1:
        return bmc_test_MDIO_8367()
    else:
        return bmc_test_MDIO_vlanswitch(test_times)

def bmc_test_MDIO_8367():
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    errtotal = 0
    MDIO_dev_dict = {
        "PHY0":["0-10","15-31"],
        "PHY1":["0-10","15-31"],
        "PHY2":["0-10","15-31"],
        "PHY3":["0-10","15-31"],
        "PHY4":["0-10","15-31"],
    }

    for phy in range(0, len(MDIO_dev_dict)):
        phy_name = "PHY" + str(phy)
        check_log = ""
        dev_errtotal = 0
        for reg in MDIO_dev_dict[phy_name]:
            reg_num = reg.split('-')
            for i in range(int(reg_num[0]), int(reg_num[1])+1):
                cmd = "rtk_phy phy rd %d %d" % (phy, i)
                ret, log = log_os_system(cmd, 0) 
                if "0x" in log:
                    check_log = check_log + str(i) + ": PASS\n"
                else:
                    check_log = check_log + str(i) + ": FAILED\n"
                    dev_errtotal -= 1
        errtotal += dev_errtotal
        if dev_errtotal < 0:
            print_choose(phy_name + " : FAILED")
            print_choose(check_log) #打印详细的错误信息
        else:
            print_choose(phy_name + " : PASS")
    if errtotal < 0:
      RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def judge_fw_88e6321_exist():
    ret, log = log_os_system("cat /etc/sw_config.json 2>/dev/null | grep 88e6321 | wc -l", 0)
    if int(log) != 0:
        return True
    return False

def judge_fw_bcm53134_exist():
    ret, log = log_os_system("cat /etc/sw_config.json 2>/dev/null | grep bcm53134 | wc -l", 0)
    if int(log) != 0:
        return True
    return False

def get_ftgmac100_mii(dev_name, dev_list):
    reg_0_value_zero = "reg : 0x 0 value : 0x   0"
    reg_0_value_fullf = "reg : 0x 0 value : 0xffff"
    check_log = ""
    dev_errtotal = 0
    for i in dev_list:
        cmd = r"cat /sys/bus/mdio_bus/devices/ftgmac100_mii:%s/hw_test*"%i
        ret, log = log_os_system(cmd, 0)
        if "reg" in log and \
            reg_0_value_zero not in log and \
            reg_0_value_fullf not in log:
            check_log = check_log + i + ": PASS\n"
        else:
            check_log = check_log + i + ": FAILED\n"
            dev_errtotal -= 1
    if dev_errtotal < 0:
        print_choose(dev_name + " : FAILED")
        print_choose(check_log) #打印详细的错误信息
    else:
        print_choose(dev_name + " : PASS")
    return dev_errtotal

def get_smitool_switch(dev_name, phy_addr_list, test_times = 1):
    check_log = ""
    dev_errtotal = 0
    suffix= ""
    # 特殊的地址必须返回指定值，其他地址有返回值即可--返回log带“0x”
    check_dict = {
        "88e6321":{
            "01":{"2":"0x 362", "3":"0x5d12"},"03":{"2":"0x 141", "3":"0x c00"},
            "0c":{"2":"0x 141", "3":"0x c00"},"0d":{"2":"0x 141", "3":"0x c00"},
            "regaddr_range":32, "vlanswitch_type":"88e6321"},
        "MGMT-B50210S":{"11":{"2":"0x600d", "3":"0x8595"},"regaddr_range":16,"vlanswitch_type":"general"},
        "BCM53134":{"00":{"2":"0xae02", "3":"0x5350"},"01":{"2":"0xae02", "3":"0x5350"},"02":{"2":"0xae02", "3":"0x5350"},"03":{"2":"0xae02", "3":"0x5350"},"04":{},"regaddr_range":4,"vlanswitch_type":"general"},
    }
    dev_check_dict = check_dict[dev_name.strip()]
    regaddr_range = dev_check_dict["regaddr_range"]
    vlanswitch_type = dev_check_dict["vlanswitch_type"]
    for phy_addr in phy_addr_list:
        excepted_dict = dev_check_dict.get(phy_addr, None)
        phy_addr_str = str(int(phy_addr,16))
        if excepted_dict == None:
            check_log = check_log + phy_addr_str + " " + "non-existent" +": FAILED\n"
            dev_errtotal -= 1
            continue
        for reg_addr in range(0,regaddr_range):
            reg_addr_str = str(reg_addr)
            cmd = "smitool phy rd %s %s %s" % (vlanswitch_type, phy_addr_str, reg_addr_str)
            for count in range(1, test_times + 1):
                if test_times > 1:
                    # continuous stress test
                    suffix = "(%d/%d)" % (count, test_times)
                ret, log = log_os_system(cmd, 0)
                excepted_str = excepted_dict.get(reg_addr_str, "0x")
                if excepted_str in log:
                    if count == test_times:
                        check_log = check_log + phy_addr_str + " " + reg_addr_str + ": PASS%s\n" % suffix
                else:
                    check_log = check_log + phy_addr_str + " " + reg_addr_str + ": FAILED%s\n" % suffix
                    dev_errtotal -= 1
                    break
    if dev_errtotal < 0:
        print_choose(dev_name + " : FAILED")
        print_choose(check_log) #打印详细的错误信息
    else:
        print_choose(dev_name + " : PASS")
    return dev_errtotal

def get_mdiodev_switch(dev_name, phy_addr_list, test_times = 1):
    check_log = ""
    dev_errtotal = 0
    suffix= ""
    # 特殊的地址必须返回指定值，其他地址有返回值即可--返回log带“0x”
    check_dict = {
        "88e6321":{
            "01":{"2":"0x 362", "3":"0x5d12"},"03":{"2":"0x 141", "3":"0x c00"},
            "0c":{"2":"0x 141", "3":"0x c00"},"0d":{"2":"0x 141", "3":"0x c00"},
            "regaddr_range":32},
        "MGMT-B50210S":{"11":{"2":"0x600d", "3":"0x8595"},"regaddr_range":16},
        "BCM53134":{"00":{"2":"0xae02", "3":"0x5350"},"01":{"2":"0xae02", "3":"0x5350"},"02":{"2":"0xae02", "3":"0x5350"},"03":{"2":"0xae02", "3":"0x5350"},"04":{},"regaddr_range":4},
    }
    dev_check_dict = check_dict[dev_name.strip()]
    regaddr_range = dev_check_dict["regaddr_range"]
    for phy_addr in phy_addr_list:
        excepted_dict = dev_check_dict.get(phy_addr, None)
        phy_addr_str = str(int(phy_addr,16))
        if excepted_dict == None:
            check_log = check_log + phy_addr_str + " " + "non-existent" +": FAILED\n"
            dev_errtotal -= 1
            continue
        for reg_addr in range(0, regaddr_range):
            reg_addr_str = str(reg_addr)
            cmd = "dfd_debug mdiodev_rd 1 %s %s|grep 0x|awk '{print $4}'" % (phy_addr_str, reg_addr_str)
            for count in range(1, test_times + 1):
                if test_times > 1:
                    # continuous stress test
                    suffix = "(%d/%d)" % (count, test_times)
                ret, log = log_os_system(cmd, 0)
                if ret or "0xffff" in log or "0x   0" in log:
                    check_log =  check_log + phy_addr_str + " " + reg_addr_str + ": FAILED%s\n" % suffix
                    dev_errtotal -= 1
                    break
                else:
                    excepted_str = excepted_dict.get(reg_addr_str, "0")
                    if excepted_str in log:
                        if count == test_times:
                            check_log = check_log + phy_addr_str + " " + reg_addr_str + ": PASS%s\n" % suffix
                    else:
                        check_log = check_log + phy_addr_str + " " + reg_addr_str + ": FAILED%s\n" % suffix
                        dev_errtotal -= 1
                        break

    if dev_errtotal < 0:
        print_choose(dev_name + " : FAILED")
        print_choose(check_log) #打印详细的错误信息
    else:
        print_choose(dev_name + " : PASS")
    return dev_errtotal

def bmc_test_MDIO_vlanswitch(test_times):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    errtotal = 0
    MDIO_dev_dict = {
        # 5387 88e6321测试项
        "BMC-54616 ":["11"],
        # 5387 测试项
        "MGMT-54616":["18"],
        "5387      ":["00","01","02","03","04","05","06","07"],
        # 88e6321测试项
        "88e6321   ":["01","03","0c","0d"],
        # bcm53134测试项
        "MGMT-B50210S":["11"],
        "BCM53134    ":["00","01","02","03","04"],
    }
    exist_88e6321 = judge_fw_88e6321_exist()
    exist_bcm53134 = judge_fw_bcm53134_exist()
    for dev in MDIO_dev_dict.keys():
        if ("5387" in dev or "MGMT-54616" in dev) and (exist_88e6321 == True or exist_bcm53134 == True):
            # 要测试的dev为5387/MGMT-54616时，发现当前设备芯片为88e6321，则跳过测试
            continue
        elif "88e6321" in dev:
            if exist_88e6321 == True:
                errtotal += get_mdiodev_switch(dev, MDIO_dev_dict[dev])
            else:
                # 要测试的dev为88e6321时，发现当前设备芯片非88e6321，则跳过测试
                continue
        elif "MGMT-B50210S" in dev or "BCM53134" in dev:
            if exist_bcm53134 == True:
                errtotal += get_mdiodev_switch(dev, MDIO_dev_dict[dev], test_times)
            else:
                # 要测的dev为MGMT-B50210S/BCM53134时，当前设备vlanswitch非bcm53134则跳过测试
                continue
        elif "BMC-54616 " in dev and exist_bcm53134 == True:
            # 要测的dev为BMC-54616 时，当前设备为bcm53134则跳过测试
            continue
        else:
            errtotal += get_ftgmac100_mii(dev, MDIO_dev_dict[dev])
    if errtotal < 0:
      RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def bmc_test_MDIO_stress():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 :""}
    totalerr = 0
    test_times = 10
    for i in range(0, test_times):
       print_choose((_("\n\n Test count: %d/%d")%(i+1, test_times)).encode('utf-8'))
       RET1 = bmc_test_MDIO()
       totalerr += RET1[RETURN_KEY1]
    if totalerr < 0:
       RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def bmc_test_MDIO_continuous_stress():
    test_times = ALI_BMC.get("MIDO_REG_READ_TIMES", 1)
    return bmc_test_MDIO(test_times)

def bmc_test_get_fan_present():
    errtotal = 0
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    modelname="fan"
    num_of_offset = "single"
    present_config = "present"
    device_config = "device"
    s3ip = None
    # Initialize configuration information
    tmp_product_name = get_full_product_name()
    # Heat Sink-Cooled Equipment
    if "-H-" in tmp_product_name:
        present_config = "h_present"
        device_config = "h_device"

    present = CONFIG_INFO_MAP[modelname].get(present_config, None)
    single_catpath_flag = 0
    try:
        if present != None:
            num_of_offset = present.get("num_of_offset", "single")
            s3ip = present.get("s3ip", None)
        all_fan_dev = FAN_SPEED[device_config]
        for i in range(0,len(all_fan_dev)):
            if single_catpath_flag == 0:
                if present == None:
                    path = "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan_present"
                    single_catpath_flag = 1
                else:
                    if num_of_offset == "single":
                        path = present["path"]
                        single_catpath_flag = 1
                    else:
                        path = present["path"]["FAN%d" % (i + 1)]
                ret, log = log_os_system("cat %s" % path, 0)
                if ret or "can't open" in log:
                    print_choose((_("Failed to read presence information: %s") % log).encode('utf-8'))
                    errtotal -= 1
                    continue
                fan_present = int(log, 16)
            if s3ip:
                if fan_present == 1:
                    print_choose((_("Fan%d")%(i+1)).encode('utf-8') + (_(":present")).encode('utf-8'))
                else:
                    print_choose((_("Fan%d")%(i+1)).encode('utf-8') + (_(":not present")).encode('utf-8'))
                    errtotal -= 1
            else:
                offset = i
                if present != None:
                    offset = present["bitoffset"]["FAN%d" % (i + 1)]
                if (fan_present & (1 << offset)):
                    print_choose((_("Fan%d")%(i+1)).encode('utf-8') + (_(":not present")).encode('utf-8'))
                    errtotal -= 1
                else:
                    print_choose((_("Fan%d")%(i+1)).encode('utf-8') + (_(":present")).encode('utf-8'))
    except Exception as e:
        errtotal -= 1
        print_choose(e)

    if errtotal < 0:
      RET[RETURN_KEY1] = -1
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def restart_and_get_fanctrl_status():
    restart_ali_server()
    set_fan_watchdog(1)
    time.sleep(70) # Wait for the fanctrl to work steadily
    cmd = "systemctl status fanctrl | cat | grep Active"
    ret, log = log_os_system(cmd, 0)
    if "min " not in log:
        ret = -1
    return ret, log

def bmc_test_get_fan_speed(startreset = False):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    device_config = "device"
    tmp_product_name = get_full_product_name()
    if "-L-" in tmp_product_name or "-LC-" in tmp_product_name or "-LD-" in tmp_product_name:
        # not required for liquid device
        return RET
    if "-H-" in tmp_product_name:
        device_config = "h_device"

    if startreset:
        restart_ret, log = restart_and_get_fanctrl_status()
        if restart_ret != 0:
            RET[RETURN_KEY1] = -1
            print_choose((_("fanctrl service restart exception: %s") % log).encode('utf-8'))
    int_case = interface()
    errtotal = 0
    out_of_range = 0

    try:
        fan_info_all = int_case.get_fan_info_all()
        fans_num = fan_info_all["Number"]
        for fan in range(1, fans_num + 1):
            fan_name = "FAN" + str(fan)
            fan_info = {}
            fan_info = fan_info_all[fan_name]
            if len(fan_info) <= 0:
                errtotal -= 1
                print_choose((_("    %s: information getting failed") % fan_name).encode('utf-8'))
                continue
            if fan_info["Present"] != "yes":
                errtotal -= 1
                print_choose((_("    %s: not present") % fan_name).encode('utf-8'))
                continue
            rotors_num = fan_info["Rotors"]
            for rotor in range(1, rotors_num + 1):
                rotor_name = "Rotor" + str(rotor)
                rotor_info = {}
                rotor_info = fan_info[rotor_name]
                if len(rotor_info) <= 0:
                    errtotal -= 1
                    print_choose((_("    %s-motor%d: failed to get information")%(fan_name, rotor)).encode('utf-8'))
                    continue
                if (rotor_info["Speed"] < rotor_info["SpeedMin"] or rotor_info["Speed"] > rotor_info["SpeedMax"]):
                    print_choose((_("    %s-motor%d: %dRPM, not in normal threshold range %d, %d")%(fan_name, rotor, rotor_info["Speed"], rotor_info["SpeedMin"], rotor_info["SpeedMax"])).encode('utf-8'))
                    errtotal -= 1 
                    out_of_range -= 1
                else:
                    print_choose((_("    %s-motor%d: %dRPM")%(fan_name, rotor, rotor_info["Speed"])).encode('utf-8'))

        if out_of_range < 0:
            print_choose((_("Read fan registers")).encode('utf-8'))
            fan_bus = FAN_SPEED["bus"]
            fan_addr = FAN_SPEED["addr"]
            fan_wdreg = FAN_SPEED.get("watchdogreg", 0x51)
            ret_wd, log_wd = rji2cget(fan_bus, fan_addr, fan_wdreg)
            print_choose((_("    Fan watchdog status:%s")%(log_wd)).encode('utf-8'))
            fan_list = FAN_SPEED[device_config]
            for fan in fan_list:
                ret_ctrl, log_ctrl = rji2cget(fan_bus, fan_addr, fan["reg"])
                if ret_ctrl != 0:
                    print_choose(("    %s:%s"%(_(fan["name"]), log_ctrl)).encode('utf-8'))
                else:
                    print_choose(("    %s:%s"%(_(fan["name"]), int(log_ctrl, 16))).encode('utf-8'))

    except Exception as e:
        errtotal -= 1
        RET[RETURN_KEY2] = e

    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def bmc_test_set_fan_speed( level , finlreset = True):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    tmp_product_name = get_full_product_name()
    if "-L-" in tmp_product_name or "-LC-" in tmp_product_name or "-LD-" in tmp_product_name:
        # not required for liquid device
        return RET
    device_config = "device"
    speedlevel_config = "speedlevel"
    if "-H-" in tmp_product_name:
        device_config = "h_device"
        speedlevel_config = "h_speedlevel"

    int_case = interface()
    errtotal = 0
    out_of_range = 0
    print_choose((_("Set fan speed")).encode('utf-8'))
    no_fan_present = False
    fan_bus = FAN_SPEED["bus"]
    fan_addr = FAN_SPEED["addr"]
    fan_wdreg = FAN_SPEED.get("watchdogreg", 0x51)

    try:
        set_fan_watchdog(0) #关闭风扇狗
        stop_ali_server()

        fans = int_case.get_fans()
        i = 0
        no_fan_present = True
        for fan in fans:
            current_fan_presence = int_case.get_fan_presence(fan.name)
            fan_name = fan.name.replace("FAN",_("Fan"))
            if (current_fan_presence != True): 
                errtotal -= 1
                print_choose((_("    %s: not present")%fan_name).encode('utf-8'))
            else:
                no_fan_present = False
                fan_level = FAN_SPEED[speedlevel_config][level]
                fan_dev = FAN_SPEED[device_config][i]
                ret, log = rji2cset(fan_bus, fan_addr, fan_dev["reg"],fan_level["value"])

                if ret or "can't open" in log:
                   print_choose((_("    %s: failed to set speed level")%(fan_name)).encode('utf-8'))
                   errtotal -= 1
                else :
                    print_choose((_("    %s set speed level to %s")%((fan_name),fan_level["value"])).encode('utf-8'))
            i += 1

        if no_fan_present:
            pass
        else:
            time.sleep(FAN_SPEED["waittime"])#等待风扇到达设置速度
            print_choose((_("Read fan speed")).encode('utf-8'))

            for fan in fans:
                current_fan_presence = int_case.get_fan_presence(fan.name)
                fan_name = fan.name.replace("FAN",_("Fan"))
                if (current_fan_presence == True): 
                    rotors = fan.rotor_list
                    for rotor in rotors:
                        index  =  rotors.index(rotor)
                        current_fan_speed = int_case.get_fan_speed(fan.name, index + 1)
                        if (current_fan_speed == -1):
                            print_choose((_("    %s-motor%d: failed to read speed information")%(fan_name, index + 1)).encode('utf-8'))
                            errtotal -= 1
                            continue

                        if (current_fan_speed  < fan_level["low_threshhold"] or current_fan_speed > fan_level["high_threshhold"]):
                            print_choose((_("    %s-motor%d: %sRPM, not in normal threshold range %d, %d")%(fan_name, index + 1, current_fan_speed,fan_level["low_threshhold"],fan_level["high_threshhold"])).encode('utf-8'))
                            errtotal -= 1 
                            out_of_range -= 1
                        else:
                            print_choose((_("    %s-motor%d: %sRPM")%(fan_name, index + 1, current_fan_speed)).encode('utf-8'))
                else:
                    errtotal -= 1
                    print_choose((_("    %s: not present")%fan_name).encode('utf-8'))

        if out_of_range < 0:
            print_choose((_("Read fan registers")).encode('utf-8'))
            ret_wd, log_wd = rji2cget(fan_bus, fan_addr, fan_wdreg)
            print_choose((_("    Fan watchdog status:%s")%(log_wd)).encode('utf-8'))
            fan_list = FAN_SPEED[device_config]
            for fan in fan_list:
                ret_ctrl, log_ctrl = rji2cget(fan_bus, fan_addr, fan["reg"])
                if ret_ctrl != 0:
                    print_choose(("    %s:%s"%(_(fan["name"]), log_ctrl)).encode('utf-8'))
                else:
                    print_choose(("    %s:%s"%(_(fan["name"]), int(log_ctrl, 16))).encode('utf-8'))
    except Exception as e:
        errtotal -= 1
        RET[RETURN_KEY2] = e
    finally:
        if (finlreset == True):
            start_ali_server()
            set_fan_watchdog(1) #开启风扇狗
    if errtotal < 0:
      RET[RETURN_KEY1] = -1

    print_sonic(RET)
    return RET

def bmc_test_set_fan_speed_high_without_reset():
    return bmc_test_set_fan_speed("high", False)

def bmc_test_set_fan_speed_reset():
    return bmc_test_get_fan_speed(True)

def bmc_test_set_fan_speed_high():
    return bmc_test_set_fan_speed("high")

def bmc_test_set_fan_speed_middle():
    return bmc_test_set_fan_speed("middle")

def bmc_test_set_fan_speed_low():
    return bmc_test_set_fan_speed("low")

def bmc_test_get_psu_rfu_info():
   RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
   PSUs =  PSU_INFO[Device_branch]
   int_case = interface()
   errtotal = 0
   i = 0;

   for psu in PSUs:
        try:
            i += 1
            print_choose("\nPSU%d:"%(i))
            if int_case.get_psu_presence("PSU%d"%(i)) is not True:
                print_choose((_("not present ")).encode('utf-8'))
                errtotal -= 1
                continue

            filename = "/sys/bus/i2c/devices/%d-00%x/eeprom"%(psu["bus"],psu["e2addr"])
            ret = E2Util.decodeBinName(filename)
            head = ["key","value"]
            if ret!= None:
                for key,values in ret.productInfoArea.todict().items():
                    print_choose( "%-25s: %s "% (key,values) )
            else:
               print_choose((_("Failed to read e2 information")).encode('utf-8'))
               errtotal -= 1
        except E2Exception as e:
            errtotal -= 1
            print_choose(e.message)


   if errtotal < 0:
      RET[RETURN_KEY1] = -1;
   if rj_diag_args.operations != None:
        print_sonic(RET)
   return RET

def bmc_test_get_psu_info():
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    PSUs =  PSU_INFO[Device_branch]
    int_case = interface()
    errtotal = 0
    i = 0;
    dic_k = {"curr2_input":(_("Input current")).encode('utf-8'),
             "curr1_input":(_("Output current")).encode('utf-8'),
             "in2_input":(_("Input voltage")).encode('utf-8'),
             "in1_input":(_("Output voltage")).encode('utf-8'),
             "power1_input":(_("Output power")).encode('utf-8'),
             "power2_input":(_("Input power")).encode('utf-8'),
            }

    for psu in PSUs:
        try:
            i += 1
            print_choose("PSU%d"%(i) +":") 
            if int_case.get_psu_presence("PSU%d"%(i)) is not True:
                print_choose((_("not present ")).encode('utf-8'))
                errtotal -= 1
                continue

            for attr_key in psu["attrs"]:
                cmd = "cat /sys/bus/i2c/devices/%d-00%x/hwmon/hwmon*/%s"%(psu["bus"],psu["addr"],attr_key)
                ret, log = log_os_system(cmd, 0)
                if ret or "can't open" in log:
                    print_choose((_("Read information failed")).encode('utf-8'))
                    errtotal -= 1
                else:
                    print_choose("%-20s %-10s %-10s"%(dic_k[attr_key],log,psu["attrs"][attr_key]))
        except E2Exception as e:
            errtotal -= 1
            print_choose(e.message)

    if errtotal < 0:
        RET[RETURN_KEY1] = -1;
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_test_get_psu_present():
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    PSUs =  PSU_INFO[Device_branch]
    int_case = interface()
    errtotal = 0
    i = 0

    for psu in PSUs:
        try:
            i += 1
            if int_case.get_psu_presence("PSU%d"%(i)) is not True:
                print_choose(("PSU%d"%(i) +_(":not present")).encode('utf-8'))
                errtotal -= 1
            else:
                print_choose(("PSU%d"%(i) +_(":present")).encode('utf-8'))
        except E2Exception as e:
            errtotal -= 1
            print_choose(e.message)

    if errtotal < 0:
       RET[RETURN_KEY1] = -1;
    if rj_diag_args.operations != None:
         print_sonic(RET)
    return RET

def get_equipment_AB_type():
    '''
    return "A" or "B"
    default: "A"
    '''
    EQUIPMENT_AB_MAP
    ret, log = log_os_system("cat /etc/device/hw_ver 2>/dev/null", 0) 
    return EQUIPMENT_AB_MAP.get(log, "A")

def bmc_test_i2c_scan(test_times = 1, opt = False):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    PSUs =  PSU_INFO[Device_branch]
    errtotal = 0
    exist_88e6321 = 0 # 0 ：removed, 1 : added
    channel_88e6321 = 0 # 0 ：non-existent, 1 : existent
    opt_arg = opt
    tmp_product_name = get_full_product_name()
    equipment_type = get_equipment_AB_type()
    if tmp_product_name == None:
        RET[RETURN_KEY1] = -1
        print_choose("product_name get failed")
        print_sonic(RET)
        return RET
    if judge_fw_88e6321_exist() == True:
        exist_88e6321 = 1
        int_case = interface()
        if int_case.add_spi_flash("88e6321") == False:
            output = "add 88e6321 channel failed"
            log_os_system("logger -p debug %s" % output,0)
            print_choose(output)
        else:
            channel_88e6321 = 1
    for i2cdev in I2C_SCAN_LIST:
        STATE = "PASS"
        shielde_value = i2cdev.get("scan_shielde_capacity",None)
        if shielde_value != None:
            if ("-L-" in tmp_product_name or "-LC-" in tmp_product_name or \
                    "-LD-" in tmp_product_name or "-H-" in tmp_product_name) \
                    and (shielde_value == 1):
                # 非风冷设备需要屏蔽的扫描项
                continue
            if ("-LC-" not in tmp_product_name) and (shielde_value == 2):
                # 非LC设备需要屏蔽的扫描项
                continue
            if ("-LD-" not in tmp_product_name) and (shielde_value == 3):
                # 非LD设备需要屏蔽的扫描项
                continue
            if ("-H-" not in tmp_product_name) and (shielde_value == 5):
                # 非H设备需要屏蔽的扫描项
                continue
            if (exist_88e6321 == 0) and (shielde_value == 6321):
                # 非88e6321设备需要屏蔽的扫描项
                continue
            if (equipment_type != "A") and (shielde_value == 6):
                # 非A配套设备，需要屏蔽的扫描项
                continue
            if (equipment_type != "B") and (shielde_value == 7):
                # 非B配套设备，需要屏蔽的扫描项
                continue
            if opt_arg and shielde_value != 4:
                # 测试选配项，需要屏蔽非选配项
                continue
            if not opt_arg and shielde_value == 4:
                # 测试非选配项，需要屏蔽选配项
                continue
        if opt_arg and shielde_value is None:
            # 测试选配项，需要屏蔽非选配项
            continue
        special = i2cdev.get("special", None)
        if special != None:
            cmd = "i2cget -y -f %d %s" % (i2cdev["bus"], i2cdev["addr"])
            for count in range(1, test_times + 1):
                ret, log = log_os_system(cmd, 0)
                if ret !=0 or "error" in log.lower() or "failed" in log.lower():
                    STATE = "FAILED"
                    errtotal -= 1
                    break
        else:
            for count in range(1, test_times + 1):
                ret, log = rji2cget(i2cdev["bus"], i2cdev["addr"], i2cdev.get("reg", 0))
                if ret or "Error" in log:
                    STATE = "FAILED"
                    errtotal -= 1
                    break
        if test_times > 1:
            # continuous stress test
            STATE = "%s(%d/%d)" % (STATE, count, test_times)
        tplt = '    {0:<{len}}\t{1:<10}'
        formatstr = tplt.format(_(i2cdev['name']), STATE, len=36-len(_(i2cdev['name']).encode('GBK'))+len(_(i2cdev['name'])))
        print_choose(formatstr)
    if channel_88e6321 == 1:
        if int_case.remove_spi_flash_retry("88e6321") == False:
            output = "remove 88e6321 channel failed"
            log_os_system("logger -p debug %s" % output,0)
            print_choose(output)
            errtotal -= 1
    if errtotal < 0:
      RET[RETURN_KEY1] = -1;
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_test_i2c_stress():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 :""}
    totalerr = 0
    test_times = 10
    for i in range(0, test_times):
       print_choose((_("\n\n Test count: %d/%d")%(i+1, test_times)).encode('utf-8'))
       RET1 = bmc_test_i2c_scan()
       totalerr += RET1[RETURN_KEY1]
    if totalerr < 0:
       RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def bmc_test_i2c_opt_continuous_stress():
    return bmc_test_i2c_continuous_stress(True)

def bmc_test_i2c_opt_scan():
    return bmc_test_i2c_scan(1, True)

def bmc_test_i2c_continuous_stress(opt = False):
    tset_times = ALI_BMC.get("I2C_REG_READ_TIMES", 1)
    return bmc_test_i2c_scan(tset_times, opt)

def bmc_test_get_power_fw_version():
    RET = {RETURN_KEY1 : -1, RETURN_KEY2 :""}
    err_total = 0
    tplt = '\t{0:<{len}}\t{1}'
    if not POWER_FW_VER:
        RET[RETURN_KEY2] = "    The configuration of Power FW verion is empty"
        return RET

    # Prevent access conflicts
    stop_ali_server()

    equipment_type = get_equipment_AB_type()
    for item in POWER_FW_VER:
        item_name = _(item["name"])
        item_page = item.get("page")
        item_offset = item["offset"]
        extra = item.get("extra", None)
        if extra != None and extra != equipment_type:
            continue
        for scan in I2C_SCAN_LIST:
            tmp_log = ""
            scan_name = _(scan["name"])
            if item_name in scan_name:
                scan_bus = scan["bus"]
                scan_addr = scan["addr"]
                shielde_value = scan.get("scan_shielde_capacity",None)
                if extra is None and shielde_value != None:
                    if (equipment_type != "A") and (shielde_value == 6):
                        # 非A配套设备，需要屏蔽的扫描项
                        continue
                    if (equipment_type != "B") and (shielde_value == 7):
                        # 非B配套设备，需要屏蔽的扫描项
                        continue
                if item_page:
                    page = item_page["val"]
                    switch_ret, switch_log = rji2cset(scan_bus, scan_addr, item_page["offset"], page)
                    if switch_ret != 0:
                        err_total -= 1
                        tmp_log = "Failed to switch page(0x%02x): %s" % (page, switch_log)
                        formatstr = tplt.format(scan_name, tmp_log, len=36-len(scan_name.encode('GBK'))+len(scan_name))
                        print_choose(formatstr)
                        continue
                get_ret, get_log = rji2cget(scan_bus, scan_addr, item_offset)
                if get_ret != 0 or "0x" not in get_log:
                    err_total -= 1
                    tmp_log = "Failed to get version: %s" % get_log
                else:
                    tmp_log = get_log
                if item_page:
                    page = item_page["rval"]
                    switch_ret, switch_log = rji2cset(scan_bus, scan_addr, item_page["offset"], page)
                    if switch_ret != 0:
                        err_total -= 1
                        tmp_log = tmp_log + ". " + "Failed to switch page(0x%02x): %s" % (page, switch_log)
                formatstr = tplt.format(scan_name, tmp_log, len=36-len(scan_name.encode('GBK'))+len(scan_name))
                print_choose(formatstr)
    if len(g_info_tmp_for_sonic) == 0:
        print_choose("Error: Power FW is none")
        err_total -= 1
    RET[RETURN_KEY1] = err_total
    print_sonic(RET)
    start_ali_server()
    return RET

def bmc_test_power_sysfs_info(dev_dict, sysfs_dev_common, path_common):
    err_count = 0
    output_tlpt = '    {0:<25}: {1:<}'

    print_choose("  sysfs:")
    sysfs_list = dev_dict.get("sysfs", sysfs_dev_common.get(dev_dict["name"], []))
    if len(sysfs_list) == 0:
        print_choose("    empty, please check!")
        return 1

    for sysfs_dict in sysfs_list:
        name = sysfs_dict["name"]
        path_tplt = sysfs_dict.get("path", path_common.get(name, None))
        if path_tplt is None:
            err_count += 1
            print_choose(output_tlpt.format(name, "%s" % "sysfs is empty"))
            continue
        path = path_tplt.format("%d" % dev_dict["bus"], "%02x" % dev_dict["addr"])
        ret, log = log_os_system("cat %s" % path, 0)
        if ret != 0 or len(log) <= 0:
            err_count += 1
            reason = "failed to cat '%s'(log-%s)" % (path, log)
            print_choose(output_tlpt.format(name, "%s" % reason))
            continue
        print_choose(output_tlpt.format(name, log))
    return err_count

def bmc_test_power_i2c_info(dev_dict, i2c_dev_common, reg_common, i2c_page_common):
    err_count = 0
    output_tlpt = '    {0:<25}: {1:<}'

    i2c_dict = dev_dict.get("i2c", {})
    page_list = i2c_dict.get("page_list", i2c_page_common["page_list"])
    reg_list = i2c_dict.get("reg_list", i2c_dev_common.get(dev_dict["name"], []))
    print_choose("  i2c:")
    if len(reg_list) == 0 or len(page_list) == 0:
        print_choose("    empty, please check!")
        return 1

    bus = dev_dict["bus"]
    addr = dev_dict["addr"]
    for page in page_list:
        page_name = page["name"]
        page_offset = page["offset"]
        page_val = page["val"]
        page_rval = page.get("rval", None)

        print_choose("    %s:" % (page_name))
        switch_ret, switch_log = rji2cset(bus, addr, page_offset, page_val)
        if switch_ret != 0:
            err_count += 1
            print_choose("      switch page failed(%s): %s" % \
                ("%d %02x %02x %02x"% (bus, addr, page_offset, page_val), switch_log))
            continue

        #for page read powr info
        for reg_dict in reg_list:
            reg_name = reg_dict["name"]
            reg_info  = reg_dict.get("reg", None)
            if reg_info is None:
                reg_info = reg_common.get(reg_name, None)
                if reg_info is None:
                    err_count += 1
                    print_choose(output_tlpt.format(reg_name, "empty, please check!"))
                    continue
            reg_offset = reg_info["offset"]
            mode = reg_info["data_change_mode"]
            if mode == "READ_16_bit":
                read_ret, read_log = rji2cget(bus, addr, reg_offset, "w")
            else:
                read_ret, read_log = rji2cget(bus, addr, reg_offset)
            if read_ret or "0x" not in read_log:
                reason = "failed to get %d 0x%02x 0x%02x(log-%s)" % \
                    (bus, addr, reg_offset, read_log)
                print_choose(output_tlpt.format(reg_name, reason))
                err_count += 1
                continue

            reg_val = int(read_log, 16)
            if mode == "JUDGE_SOME_bit":
                mask = reg_dict.get("mask", None)
                check = reg_dict.get("check", None)
                if mask is None or check is None:
                    err_count += 1
                    reason = "mask(%s) check(%s)" % (mask, check)
                    print_choose(output_tlpt.format(reg_name, reason))
                    continue
                if (mask & reg_val) == check:
                    print_choose(output_tlpt.format(reg_name, "%d" % reg_val))
                else:
                    need_val = reg_val & (~mask)
                    err_count += 1
                    reason = "failed to check %d 0x%02x 0x%02x(read: 0x%02x, need: 0x%02x)" % \
                        (bus, addr, reg_offset, reg_val, need_val)
                    print_choose(output_tlpt.format(reg_name, reason))
            elif mode == "READ_16_bit":
                print_choose(output_tlpt.format(reg_name, "0x%04x" % reg_val))
            else:
                print_choose(output_tlpt.format(reg_name, "0x%02x" % reg_val))
        if page_rval is not None:
            rswitch_ret, rswitch_log = rji2cset(bus, addr, page_offset, page_rval)
            if rswitch_ret != 0:
                err_count += 1
                print_choose("      recover initial page failed(%s): %s" % \
                    ("%d %02x %02x %02x"% (bus, addr, page_offset, page_val), switch_log))
    return err_count

def bmc_test_psu_multiple_power_exceptions():
    RET = {RETURN_KEY1: 0, RETURN_KEY2: ""}
    total_err = 0

    if MULTIPLE_POWER_EXCEPTIONS is None:
        RET[RETURN_KEY2] = _("Error retrieving MULTIPLE_POWER_EXCEPTIONS configuration")
        RET[RETURN_KEY1] = -1
        print_sonic(RET)
        return RET
    i2c_reg_common = MULTIPLE_POWER_EXCEPTIONS["i2c_common"]["reg_common"]
    i2c_dev_common = MULTIPLE_POWER_EXCEPTIONS["i2c_common"]["dev_common"]
    i2c_page_common = MULTIPLE_POWER_EXCEPTIONS["i2c_common"]["page_common"]
    sys_path_common = MULTIPLE_POWER_EXCEPTIONS["sysfs_common"]["path_common"]
    sys_dev_common = MULTIPLE_POWER_EXCEPTIONS["sysfs_common"]["dev_common"]
    dev_list = MULTIPLE_POWER_EXCEPTIONS["dev_list"]
    equipment_type = get_equipment_AB_type()

    stop_ali_server()
    for test_item in dev_list:
        # 匹配设备类型
        extra = test_item.get("extra", None)
        if extra != None and extra != equipment_type:
            continue

        print_choose("%s(%d-00%02x):" % (test_item["name"], test_item["bus"], test_item["addr"]))
        # sysfs信息获取
        total_err -= bmc_test_power_sysfs_info(test_item, sys_dev_common, sys_path_common)

        # i2c信息获取
        total_err -= bmc_test_power_i2c_info(test_item, i2c_dev_common, i2c_reg_common, i2c_page_common)
        print_choose("")

    if total_err < 0:
        RET[RETURN_KEY1] = -1

    print_sonic(RET)
    start_ali_server()
    return RET

def bmc_test_spi_continuous_stress():
    test_times = ALI_BMC.get("SPI_ID_READ_TIMES", 1)
    return bmc_test_spi_scan(test_times)

def bmc_test_spi_scan(test_times = 1):
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    int_case = interface()
    chas_case = chassisbase()
    firmware = chas_case.get_firmware_byname("firmware")
    fpga_fw = chas_case.get_fpga_fw_byname("fpga_fw")
    if firmware == None:
        print_choose("name firmware not find")
        print_sonic(RET)
        return RET
    if SPI_TEST is None:
        print_choose("No SPI test required")
        print_sonic(RET)
        return RET
    # 关闭ali服务，防止占用过高的CPU，影响测试耗时
    stop_ali_server()

    for flash in SPI_TEST:
        flash_name = flash["name"]
        flash_chip = flash.get("chip", "")
        flash_add = flash["add"]
        test_cmd = flash["cmd"]
        flash_orgn = " "
        print_choose("%s%s:" % (flash_name, flash_chip))

        # spi flash 挂载
        if firmware.add_lock() == -1:
            print_choose("add fw lock failed")
            RET[RETURN_KEY1] = -1
            print_sonic(RET)
        if flash_add == 1:
            if flash_name == "bios":
                flash_orgn = firmware.get_bios_next_boot("get_orig_cs")
                if flash_orgn != "master" and flash_orgn != "slave":
                    print_choose("\tfailed to get current bios cs: %s" % flash_orgn)
                    RET[RETURN_KEY1] = -1
                    continue
                if firmware.set_me_status("recovery"):
                    print_choose("\tfailed to set me recovery")
                    RET[RETURN_KEY1] = -1
                    continue
                # ASW之前的设备，挂载接口不支持片选
                bioscsfirst = fpga_fw.get_operate_capacity("bioscsfirst")
                if bioscsfirst == 0 and firmware.set_bios_next_boot(flash_chip):
                    # 对于ASW之前的设备是额外的动作，没必要。这里只是为了逻辑的连续
                    firmware.set_me_status("reset")
                    print_choose("\tfailed to set current bios cs: %s" % flash_chip)
                    RET[RETURN_KEY1] = -1
                    continue
                add_spi_ret = int_case.add_spi_flash(flash_name, flash_chip)
            else:
                add_spi_ret = int_case.add_spi_flash(flash_name)
            if add_spi_ret == False:
                if flash_name == "bios":
                    firmware.set_me_status("reset")
                print_choose("\tfailed to add %s%s to bmc" %(flash_name, flash_chip))
                RET[RETURN_KEY1] = -1
                continue

        # spi flash val 获取与校验
        for count in range(1, test_times + 1):
            ret, log = log_os_system(test_cmd, 0)
            if ret != 0 or len(log) == 0 or log == "0x000000" or log == "0xffffff":
                test_result = "\tfailed test %s(%s): %s" % (flash_name, test_cmd, log)
                RET[RETURN_KEY1] = -1
                break
            if count == 1:
                orgn_val = log
            if count > 1 and log != orgn_val:
                test_result = "\tflash val has changed: %s not %s" % (log, orgn_val)
                RET[RETURN_KEY1] = -1
                break
            if count == test_times:
                test_result = "\tPASS"
        if test_times > 1:
            test_result = test_result + ("(%s/%s)" % (count, test_times))
        print_choose(test_result)

        # spi flash卸载，环境恢复
        if flash_add == 1:
            if flash_orgn != " ":
                remove_spi_ret = int_case.remove_spi_flash_retry(flash_name, flash_orgn)
            else:
                remove_spi_ret = int_case.remove_spi_flash_retry(flash_name)
            if remove_spi_ret == False:
                print_choose("\tfailed to remove %s%s" % (flash_name, flash_orgn))
                RET[RETURN_KEY1] = -1
            if flash_name == "bios":
                if bioscsfirst == 0 and firmware.set_bios_next_boot(flash_orgn):
                    print_choose("\tfailed to set current bios cs: %s" % flash_chip)
                    RET[RETURN_KEY1] = -1
                if firmware.set_me_status("reset"):
                    print_choose("\tfailed to reset me")
                    RET[RETURN_KEY1] = -1
        firmware.remove_lock()
    start_ali_server()
    print_sonic(RET)
    return RET

def led_test(LED_TYPE):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    LED_2_TEST = LED_INFO.get(LED_TYPE, None)
    if LED_2_TEST is None:
        print_choose("Unsupport %s" % LED_TYPE)
        print_sonic(RET)
        return RET
    errtotal = 0
    for attr_key in LED_2_TEST["attrs"]:
        RET = bmc_set_led(LED_TYPE, attr_key)
        if RET[RETURN_KEY1] == -1:
            errtotal = -1
            break
        else:
            if get_led_inputcheck(LED_2_TEST["name"],attr_key):
                print("yes")
            else:
                print("no")
                errtotal -= 1
    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_led_control(ctrl):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    errtotal = 0
    if "start" in ctrl:
        start_ali_server()
        set_fan_watchdog(1) #开启风扇狗
    else:
        set_fan_watchdog(0) #关闭风扇狗
        stop_ali_server()
    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_set_led(LED_TYPE, led_state):
    RET = {RETURN_KEY1 : 0,  RETURN_KEY2 : ""}
    LED_2_TEST = LED_INFO.get(LED_TYPE, None)
    if LED_2_TEST is None:
        print_choose("Unsupport %s" % LED_TYPE)
        print_sonic(RET)
        return RET
    errtotal = 0
    tmp_product_name = get_full_product_name()
    for led in LED_2_TEST["device"]:
        extra = led.get('extra', None)
        if extra != None:
            if extra not in tmp_product_name:
                continue
        if LED_2_TEST.get("way", "i2c") == "sysfs":
            loc = led.get("loc", None)
            if loc is None:
                print_choose((_("Set   FAILED")).encode('utf-8'))
                errtotal -= 1
                continue
            state = LED_2_TEST["attrs"][led_state]
            cmd = f"echo {state} > {loc}"
            ret, log = log_os_system(cmd, 0)
            if ret or "can't open" in log:
                print_choose((_("Set   FAILED")).encode('utf-8'))
                errtotal -= 1
        else:
            bus = led.get('bus', None)
            if bus == None :
                bus = LED_2_TEST["bus"]
            addr = led.get('addr', None)
            if addr == None :
                addr = LED_2_TEST["addr"]
            ret, log = rji2cset(bus,addr,led["reg"],LED_2_TEST["attrs"][led_state])
            if ret or "can't open" in log:
                print_choose((_("Set   FAILED")).encode('utf-8'))
                errtotal -= 1
    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    if rj_diag_args.operations != None:
        print_sonic(RET)
    return RET

def bmc_test_cpu_opt_gpio():
    opt_type = 1
    return bmc_test_cpu_gpio(opt_type)

# def bmc_test_cpu_gpio(opt = 0):
#     RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
#     cmd = ""
#     err_total = 0
#     ret, log = log_os_system("which firmware_upgrade_ispvme", 0)
#     if len(log):
#         cmd = "firmware_upgrade_ispvme cpld test"
#     else:
#         RET[RETURN_KEY1] = -1
#         RET[RETURN_KEY2] = "no firmware_upgrade_ispvme cmd"
#         print_sonic(RET)
#         return RET
#     if ALI_BMC.get("TEST_CPU_GPIO_BY_SLOT", False):
#         for cpld in CPLD_TEST:
#             if cpld.get("opt", 0) != opt:
#                 continue
#             slot = cpld.get("slot", None)
#             cpld_name = cpld["name"]
#             if slot == None:
#                 print_choose("%s:" % cpld_name)
#                 print_choose("failed to get slot" + "\n")
#                 err_total -= 1
#                 continue
#             testslot_cmd = cmd + " " + str(slot)
#             ret, log = log_os_system(testslot_cmd, 0)
#             if "PASS" not in log:
#                 print_choose("%s:" % cpld_name)
#                 print_choose(log + "\n")
#                 err_total -= 1
#     else:
#         ret, log = log_os_system(cmd, 0)
#         if "PASS" not in log:
#             print_choose(log)
#             err_total -= 1
#     if err_total < 0:
#         RET[RETURN_KEY1] = -1
#     print_sonic(RET)
#     return RET

def bmc_test_cpu_gpio():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    cmd = ""
    err_total = 0
    path = "/usr/local/bin/upgrade.py"
    if os.path.exists(path):
        cmd = "upgrade.py test cpld 0"
    else:
        RET[RETURN_KEY1] = -1
        RET[RETURN_KEY2] = "no upgrade.py cmd"
        print_sonic(RET)
        return RET

    ret, log = log_os_system(cmd, 0)
    if "FAILED REASON" in log or "test failed" in log:
        print_choose(log + "\n")
        err_total -= 1
    if err_total < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def bmc_test_sysled():
   return led_test("sysleds")
def bmc_test_fanled():
   return led_test("fanleds")
def bmc_test_locationled():
   return led_test("location_led")

def get_legal_e2_dev_num(e2type, product_name):
    chk_list = E2_DEV[e2type].get("chk_list", 0)
    if chk_list == 1:
        num = 0
        for e2_dev in E2_DEV[e2type]["list"]:
            extra = e2_dev.get("extra", None)
            if extra != None and extra not in product_name:
                continue
            num+=1
    else:
        num = len(E2_DEV[e2type]["list"])
    return num

def bmc_get_e2_show_list():
    e2_dict = {}
    tmp_product_name = get_full_product_name()
    for e2 in E2_DEV.keys():
        extra = E2_DEV[e2].get("extra", None)
        if extra != None:
            if extra not in tmp_product_name:
                continue
        e2_dict[e2] = get_legal_e2_dev_num(e2, tmp_product_name)
    print(e2_dict)
    return e2_dict

def bmc_get_e2_set_list():
    e2_dict = {}
    tmp_product_name = get_full_product_name()
    for e2 in E2_DEV.keys():
        extra = E2_DEV[e2].get("extra", None)
        if extra != None:
            if extra not in tmp_product_name:
                continue
        if E2_DEV[e2]["canreset"]:
            e2_dict[e2] = get_legal_e2_dev_num(e2, tmp_product_name)
    print(e2_dict)
    return e2_dict

def e2_para_check(json_str):

    ret = {"status":"err","ret_info":"none"}
    try:
        if isinstance(json_str,str):
            req_json = eval(json_str)
        else:
            req_json = json_str
    except Exception as e:
        ret["ret_info"] = "invalid json %s"%(json_str)
        return ret

    e2type = req_json.get("e2type")
    index = req_json.get("index")
    if e2type == None or index == None:
        ret["ret_info"] = "invalid json"
        return ret
    if e2type not in E2_DEV:
        ret["ret_info"] = "invalid e2 type "+e2type
        return ret
    tmp_product_name = get_full_product_name()
    e2_dev_num = get_legal_e2_dev_num(e2type, tmp_product_name)
    if index > ( e2_dev_num - 1 ):
        ret["ret_info"] = "invalid e2 index"
        return ret
    ret["status"] = "ok"
    return ret

def update_e2type_index(e2type, index):
    need_update = E2_DEV[e2type].get("chk_list", 0)
    if not need_update:
        return index
    tmp_product_name = get_full_product_name()
    current_index = 0
    legal_index = 0
    for e2_dev in E2_DEV[e2type]["list"]:
        extra = e2_dev.get("extra", None)
        if extra != None and extra not in tmp_product_name:
            current_index+=1
            continue
        if legal_index == index:
            log_os_system("logger -p debug 'update index(%d) to %d'" % (index, current_index), 0)
            return current_index
        current_index+=1
        legal_index+=1
    return index

def bmc_write_e2_bin(json_str):
    json_str_list = eval(json_str)

    json_str = json_str_list[0]
    ret = e2_para_check(json_str)
    if ret["status"] == "err":
        print(ret)
        return ret

    req_json = json_str
    e2type = req_json.get("e2type")
    index = req_json.get("index")
    index_current = index
    bin_base64 = req_json.get("bin")
    bin = base64.b64decode(bin_base64)
    if not E2_DEV[e2type]["canreset"]:
        ret["ret_info"] = "%s can not be set"%(e2type)
        ret["status"] = "err"
        print(ret)
        return ret

    if bin == None or len(bin) != 256:
        ret["ret_info"] = "invalid bin"
        ret["status"] = "err"
        print(ret)
        return ret

    index = update_e2type_index(e2type, index)
    
    bus = E2_DEV[e2type]["list"][index]["bus"]
    addr = E2_DEV[e2type]["list"][index]["addr"]
    filename = "/sys/bus/i2c/devices/%d-00%02x/eeprom"%(bus,addr)

    if os.path.exists(filename) == False:
        ret["status"] = "err"
        ret["ret_info"] = "{}:not exists".format(filename)
        return ret

    #bin_for_write ,times = re.subn("(\x00)+$","\x00",bin)
    bin_for_write = bin

    e2_protect = E2_DEV[e2type].get("protect", None)
    if e2_protect != None:
        if e2_protect.get("way") == "gpio":
            set_gpio(e2_protect["gpio_pin"], 0, 1)
        else:
            log_os_system("logger -p debug '%s protect open'" % e2type, 0)
            ret1,log = rji2cset(e2_protect["bus"], e2_protect["devno"],
                        e2_protect["addr"], e2_protect["open"])
            if ret1 or "Error" in log:
                ret["ret_info"] = "open %s protect failed :%s"%(e2type, log)
                ret["status"] = "err"
                print(ret)
                return ret

    if("E2_FAN" == e2type):
        fan_protect_list = FAN_PROTECT.get("list", None)
        if fan_protect_list != None:
            FAN_PROTECT_ADDR = fan_protect_list[index]
        else:
            FAN_PROTECT_ADDR = FAN_PROTECT
        log_os_system("logger -p debug 'E2_FAN protect open'",0)
        ret1,log = rji2cset(FAN_PROTECT_ADDR["bus"], FAN_PROTECT_ADDR["devno"],
                    FAN_PROTECT_ADDR["addr"], FAN_PROTECT["open"])
        if ret1 or "Error" in log:
            ret["ret_info"] = "open fan e2 protect failed :%s"%(log)
            ret["status"] = "err"
            print(ret)
            return ret

    with open(filename, "wb") as fp:
        fp.write(bin_for_write)

    if e2_protect != None:
        if e2_protect.get("way") == "gpio":
            set_gpio(e2_protect["gpio_pin"], 0)
        else:
            log_os_system("logger -p debug '%s protect close'" % e2type, 0)
            ret1,log = rji2cset(e2_protect["bus"], e2_protect["devno"],
                        e2_protect["addr"], e2_protect["close"])
            if ret1 or "Error" in log:
                ret["ret_info"] = "close %s protect failed :%s"%(e2type, log)
                ret["status"] = "err"
                print(ret)
                return ret

    if("E2_FAN" == e2type):
        log_os_system("logger -p debug 'E2_FAN protect close'",0)
        ret1,log = rji2cset(FAN_PROTECT_ADDR["bus"], FAN_PROTECT_ADDR["devno"],
                    FAN_PROTECT_ADDR["addr"], FAN_PROTECT["close"])
        if ret1 or "Error" in log:
            ret["ret_info"] = "close fan e2 protect failed :%s"%(log)
            ret["status"] = "err"
            print(ret)
            return ret

    ret["status"] = "ok"
    print(ret)
    return ret

def bmc_get_e2_bin(json_str):
    ret = e2_para_check(json_str)
    if ret["status"] == "err":
        print(ret)
        return ret

    req_json = eval(json_str)
    e2type = req_json.get("e2type")
    index = req_json.get("index")

    index = update_e2type_index(e2type, index)

    bus = E2_DEV[e2type]["list"][index]["bus"]
    addr = E2_DEV[e2type]["list"][index]["addr"]
    filename = "/sys/bus/i2c/devices/%d-00%02x/eeprom"%(bus,addr)
    retval = None
    try:
        #print(filename)
        if os.path.exists(filename) == False:
            ret["status"] = "err"
            ret["ret_info"] = "{}:not exists".format(filename)
            return ret
        list_reg = []
        retval = []
        with open(filename, 'rb') as fd:
            retval = fd.read()
        retvalstr = ""
        if(len(retval) >= 256):
            for k in range(256):
                retvalstr += "{:#x} ".format(retval[k])
        list_reg = retvalstr.strip().split(" ")
        ret["status"] = "ok"
        ret["ret_info"] = list_reg
        #print(ret)
        return ret
    except Exception as e:
        print(e)
        ret["status"] = "err"
        ret["ret_info"] = "get e2 failed "
        print(ret)
        return ret
 
def bmc_cpld_opt_check():
    return bmc_cpld_check(True)

def bmc_cpld_check(opt = False):
    tmp_product_name = get_full_product_name()
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    opt_arg = opt
    for cpld in CPLD_TEST:
        extra = cpld.get("extra", None)
        opt_conf = cpld.get("opt", 0)
        if extra != None and extra not in tmp_product_name:
            continue
        if opt_arg and opt_conf != 1:
            # 测试选配项，需要屏蔽非选配项
            continue
        if not opt_arg and opt_conf == 1:
            # 测试非选配项，需要屏蔽选配项
            continue
        print_choose((_("%s read/write test:")% cpld["name"]).encode('utf-8'))
        for wr_byte in [0x5a,0xa5]:
            ret, log = rji2cset(cpld["bus"],cpld["addr"], cpld["test_reg"],wr_byte)
            if ret or "can't open" in log:
               RET[RETURN_KEY1] = -1
               print_choose(log)
            else:
               ret, log = rji2cget(cpld["bus"],cpld["addr"], cpld["test_reg"])
               str_get=log.replace('0x','')
               if "%x"%wr_byte not in log.lower():
                   RET[RETURN_KEY1] = -1
                   msg = (_("    Write %x, read %s")%(wr_byte, str_get)).encode('utf-8')
                   print_choose(msg)
                   print_choose("    FAILED")
               else:
                   msg = (_("    Write %x, read %s")%(wr_byte, str_get)).encode('utf-8')
                   print_choose(msg)
                   print_choose("    PASS")
        print_choose("\r\n")

    print_sonic(RET)
    return RET

def bmc_fpga_check():
    totalerr = 0
    result = ""
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    for fpga in FPGA_TEST:
        fpga_protect = fpga.get("protect", None)
        if fpga_protect != None:
            log_os_system("logger -p debug '%s protect open'" % fpga["name"], 0)
            ret1,log = rji2cset(fpga_protect["bus"], fpga_protect["devno"],
                        fpga_protect["addr"], fpga_protect["open"])
            if ret1 or "Error" in log:
                print_choose("open %s protect failed: %s" % (fpga["name"], log))
                RET[RETURN_KEY1] = -1
                continue
        print_choose((_("%s read/write test:")%fpga["name"]).encode('utf-8'))
        for wr_byte in [0x5a,0xa5]:
            ret, log = rji2cset(fpga["bus"],fpga["addr"], fpga["test_reg"],wr_byte)
            if ret or "can't open" in log:
               RET[RETURN_KEY1] = -1
               print_choose(log)
            else:
               ret, log = rji2cget(fpga["bus"],fpga["addr"], fpga["test_reg"])
               str_get=log.replace('0x','')
               if "%x"%wr_byte not in log.lower():
                   RET[RETURN_KEY1] = -1
                   msg = (_("    Write %x, read %s")%(wr_byte, str_get)).encode('utf-8')
                   print_choose(msg)
                   print_choose("    FAILED")
               else:
                   msg = (_("    Write %x, read %s")%(wr_byte, str_get)).encode('utf-8')
                   print_choose(msg)
                   print_choose("    PASS")
        if fpga_protect != None:
            log_os_system("logger -p debug '%s protect close'" % fpga["name"], 0)
            ret1,log = rji2cset(fpga_protect["bus"], fpga_protect["devno"],
                        fpga_protect["addr"], fpga_protect["close"])
            if ret1 or "Error" in log:
                print_choose("close %s protect failed: %s" % (fpga["name"], log))
                RET[RETURN_KEY1] = -1

    print_sonic(RET)
    return RET

def test_get_fan_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    int_case = interface()
    dict_tmp = int_case.get_fan_info_all()
    if dict_tmp == None:
        print_choose("get_fan_info_all None")
        RET[RETURN_KEY1] = -1
    else:
        print_choose(json.dumps(dict_tmp, ensure_ascii=False, indent=4))
    print_sonic(RET)
    return RET

def test_get_psu_fru_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    int_case = interface()
    list_psus = int_case.get_psus()
    for i in range(len(list_psus)):
        psu_case = list_psus[i]
        if psu_case.present != True:
            print_choose((_("\n%s: not present ")% (psu_case.name)).encode('utf-8'))
            RET[RETURN_KEY1] = -1
            continue

        psu_case.get_fru_info()
        print_choose("\n%s"%(psu_case.name))
        if (psu_case.productManufacturer is not None):
            productManufacturer = psu_case.productManufacturer
        else:
            productManufacturer = "N/A"
            RET[RETURN_KEY1] = -1
        if (psu_case.productPartModelName is not None):
            productPartModelName = psu_case.productPartModelName
        else:
            productPartModelName = "N/A"
            RET[RETURN_KEY1] = -1
        if (psu_case.productSerialNumber is not None):
            productSerialNumber = psu_case.productSerialNumber
        else:
            productSerialNumber = "N/A"
            RET[RETURN_KEY1] = -1
        if (psu_case.productVersion is not None):
            productVersion = psu_case.productVersion
        else:
            productVersion = "N/A"
            RET[RETURN_KEY1] = -1
        print_choose( "%-25s: %s "% ("productManufacturer", productManufacturer))
        print_choose( "%-25s: %s "% ("productPartModelName", productPartModelName))
        print_choose( "%-25s: %s "% ("productSerialNumber", productSerialNumber))
        try:
            print_choose( "%-25s: %d "% ("productVersion",int(productVersion,16)))
        except Exception:
            print_choose( "%-25s: %s "% ("productVersion",productVersion if productVersion != None else ""))

    #print_choose(json.dumps(dict_tmp, ensure_ascii=False, indent=4))
    print_sonic(RET)
    return RET

def parse_print_fru(dict_tmp, typestr=""):
    if (typestr == "product"):
        fru_compatible = OrderedDict(
                    [
                    ("ProductAssetTag"          ,""   ),
                    ("getMfgRealDate"          ,"1"   ),
                    ("boardextral"           ,"64"  ),
                    ("customField"           ,"64"  ),
                    ("fruFileId"         ,"25"  ),
                    ("boardManufacturer"     ,""    ),
                    ("boardPartModelName"             ,""    ),
                    ("boardProductVersion"         ,""    ),
                    ("boardPartNumber"    ,""    ),
                    ("Present"          ,""    ),
                    ("boardProductName"     ,""    ),
                    ("boardSerialNumber"         ,""    ),
                    ])
    else:
        fru_compatible = OrderedDict(
                    [
                    ("ProductAssetTag"          ,""   ),
                    ("getMfgRealDate"          ,"1"   ),
                    ("boardextral"           ,"64"  ),
                    ("fruFileId"         ,"25"  ),
                    ("boardManufacturer"     ,""    ),
                    ("boardPartModelName"             ,""    ),
                    ("boardPartNumber"    ,""    ),
                    ("Present"          ,""    ),
                    ("boardProductName"     ,""    ),
                    ("boardSerialNumber"         ,""    ),
                    ])
    fru_compatible["ProductAssetTag"] = dict_tmp.get("productAssetTag")
    fru_compatible["getMfgRealDate"] = dict_tmp.get("productextra1")
    if (typestr == "product"):
        tmp = dict_tmp.get("productextra2") if dict_tmp.get("productextra2") != None else ""
        tmpstr = ""
        for it in range(len(tmp)):
             tmpstr = tmpstr+"%02x"%(ord(tmp[it]))
        fru_compatible["boardextral"] =  tmpstr
        key_version = "boardProductVersion"
    else:
        key_version = "boardextral"
    try:
        fru_compatible[key_version] = int(dict_tmp.get("productVersion"),16)
    except Exception:
        fru_compatible[key_version] = dict_tmp.get("productVersion") if dict_tmp.get("productVersion") != None else ""
    if (typestr == "product"):
        tmp = dict_tmp.get("productextra3") if dict_tmp.get("productextra3") != None else ""
        tmpstr = ""
        for it in range(len(tmp)):
             tmpstr = tmpstr+"%x"%(ord(tmp[it]))
        fru_compatible["customField"] = tmpstr
    fru_compatible["fruFileId"] = dict_tmp.get("productfruFileId")
    fru_compatible["boardManufacturer"] = dict_tmp.get("productManufacturer")
    fru_compatible["boardPartModelName"] =  dict_tmp.get("productPartModelName")
    fru_compatible["boardPartNumber"] = ""
    fru_compatible["Present"] = "0" #Present??
    fru_compatible["boardProductName"] = dict_tmp.get("productName")
    fru_compatible["boardSerialNumber"] = dict_tmp.get("productSerialNumber")

    for valuskey in fru_compatible.keys():
        print_choose( "%-25s: %s "% (valuskey,fru_compatible[valuskey]) )

def parse_print_boardfru(dict_tmp):
    boardfru_compatible = OrderedDict(
                    [
                    ("getMfgRealDate"          ,"1"   ),
                    ("boardextral"           ,"64"  ),
                    ("fruFileId"         ,"25"  ),
                    ("boardManufacturer"     ,""    ),
                    ("boardPartModelName"             ,""    ),
                    ("boardPartNumber"    ,""    ),
                    ("Present"          ,""    ),
                    ("boardProductName"     ,""    ),
                    ("boardSerialNumber"         ,""    ),
                    ])
    boardfru_compatible["getMfgRealDate"] = dict_tmp.get("boardmfg_date")
    try:
        boardfru_compatible["boardextral"] = int(dict_tmp.get("boardextra1"),16)
    except Exception:
        boardfru_compatible["boardextral"] = dict_tmp.get("boardextra1") if dict_tmp.get("boardextra1") != None else ""
    boardfru_compatible["fruFileId"] = dict_tmp.get("boardfruFileId")
    boardfru_compatible["boardManufacturer"] = dict_tmp.get("boardManufacturer")
    boardfru_compatible["boardPartModelName"] = ""
    boardfru_compatible["boardPartNumber"] = dict_tmp.get("boardPartNumber")
    boardfru_compatible["Present"] = "0" #Present
    boardfru_compatible["boardProductName"] = dict_tmp.get("boardProductName")
    boardfru_compatible["boardSerialNumber"] = dict_tmp.get("boardSerialNumber")

    for valuskey in boardfru_compatible.keys():
        print_choose( "%-25s: %s "% (valuskey,boardfru_compatible[valuskey]) )

def print_eeprom_boardfru(dict_value, display_product, display_board, typestr=""):
    ret_num = 0
    try:
        dev_case = devicebase()
        eeprom_tmp = dev_case.get_eeprom_info(dict_value)
        if eeprom_tmp is None:
            print_choose("    value is none")
        fru_dev = ipmifru()
        fru_dev.decodeBin(eeprom_tmp)
        if display_product == True and fru_dev.productInfoArea is not None:
            dict_tmp = fru_dev.productInfoArea.todict()
            if dict_tmp != None:
                parse_print_fru(dict_tmp, typestr)
                ret_num = ret_num + 1
        if display_board == True and fru_dev.boardInfoArea is not None:
            dict_tmp = fru_dev.boardInfoArea.todict()
            if dict_tmp != None:
                parse_print_boardfru(dict_tmp)
                ret_num = ret_num + 1
    except Exception as e:
        print_choose("fail to get fru")
    return ret_num

def test_get_fru_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    fru_num = 0
    int_case = interface()
    tmp_product_name = get_full_product_name()

    list_fru = ALI_E2_DEV
    dict_value = list_fru.get("bmc", None)
    if (dict_value != None):
        print_choose("=======bmc FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("sysfru", None)
    if (dict_value != None):
        print_choose("=======board FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("cpu", None)
    if (dict_value != None):
        print_choose("=======cpu FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("emmc_card", None)
    if (dict_value != None):
        print_choose("=======emmc_card FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("ibvb_card", None)
    if (dict_value != None):
        extra = dict_value.get("extra", None)
        if extra == None or (extra != None and extra in tmp_product_name):
            print_choose("=======ibvb_card FRU==========")
            ret_num = print_eeprom_boardfru(dict_value, False, True)
            fru_num = fru_num +ret_num

    list_fans = int_case.get_fans()
    for it in range(len(list_fans)):
        fan_case = list_fans[it]
        try:
            if fan_case.e2loc is None or "fake" in fan_case.e2loc:
                continue
            eeprom_fan = fan_case.get_eeprom_info(fan_case.e2loc)
            if eeprom_fan is None:
                print_choose("=======%s FRU=========="%(fan_case.name.lower()))
                print_choose("fail to get this FRU!")
                print_choose("=======%sboard FRU=========="%(fan_case.name.lower()))
                print_choose("fail to get this board FRU!")
                continue
            fru_fan = ipmifru()
            fru_fan.decodeBin(eeprom_fan)
            if fru_fan.productInfoArea is not None:
                print_choose("=======%s FRU=========="%(fan_case.name.lower()))
                dict_tmp = fru_fan.productInfoArea.todict()
                if dict_tmp != None:
                    fru_num = fru_num + 1
                    parse_print_fru(dict_tmp, "fan")
            if fru_fan.boardInfoArea is not None:
                print_choose("=======%sboard FRU=========="%(fan_case.name.lower()))
                dict_tmp = fru_fan.boardInfoArea.todict()
                if dict_tmp != None:
                    fru_num = fru_num + 1
                    parse_print_boardfru(dict_tmp)
        except Exception as e:
            print_choose("=======%s FRU=========="%(fan_case.name.lower()))
            print_choose("fail to get fru")

    dict_value = list_fru.get("fanboard", None)
    if (dict_value != None):
        extra = dict_value.get("extra", None)
        if extra == None or (extra != None and extra in tmp_product_name):
            print_choose("=======fanboard FRU==========")
            ret_num = print_eeprom_boardfru(dict_value, False, True)
            fru_num = fru_num +ret_num

    for it in range(4):
        dict_value = list_fru.get("card%d"%(it+1), None)
        if (dict_value != None):
            print_choose("=======linecard%d FRU=========="%(it+1))
            ret_num = print_eeprom_boardfru(dict_value, False, True)
            fru_num = fru_num +ret_num

    dict_value = list_fru.get("mac", None)
    if (dict_value != None):
        print_choose("=======mac FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("switch", None)
    if (dict_value != None):
        print_choose("=======switch FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("40ccq", None)
    if (dict_value != None):
        print_choose("=======40ccq FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num
    
    dict_value = list_fru.get("44ccq", None)
    if (dict_value != None):
        print_choose("=======44ccq FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, False, True)
        fru_num = fru_num +ret_num

    dict_value = list_fru.get("sysfru", None)
    if (dict_value != None):
        print_choose("=======product FRU==========")
        ret_num = print_eeprom_boardfru(dict_value, True, False, "product")
        fru_num = fru_num +ret_num

    if tmp_product_name == None:
        RET[RETURN_KEY1] = -1
    else:
        if "-L-" in tmp_product_name or "-LD-" in tmp_product_name:
            if fru_num == ALI_BMC["FRU_NUM"] or fru_num == ALI_BMC["NO_FRU_NUM"]:
                RET[RETURN_KEY1] = 0
            else:
                RET[RETURN_KEY1] = -1
        elif "-LC-" in tmp_product_name:
            if fru_num != ALI_BMC["LC_FRU_NUM"] and fru_num != ALI_BMC["LC_NO_FRU_NUM"]:
                RET[RETURN_KEY1] = -1
        elif "-H-" in tmp_product_name:
            if fru_num != ALI_BMC["H_FRU_NUM"]:
                RET[RETURN_KEY1] = -1
        else:
            if fru_num != ALI_BMC["FRU_NUM"]:
                RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET    

def test_get_psu_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    psu_flag = 0
    int_case = interface()
    dict_psu_info = int_case.get_psu_info_all()
    if dict_psu_info != None:
        print_choose(json.dumps(dict_psu_info, ensure_ascii = False,indent=4))  #
    else:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def test_direction_check():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    air_flow_info = collections.OrderedDict()

    int_case = interface()
    dict_psu_info = int_case.get_psu_info_all()
    if dict_psu_info != None:
        #print_choose(json.dumps(dict_psu_info, ensure_ascii = False,indent=4))  #
        for i in range(dict_psu_info["Number"]):
            psu_num = "PSU%d"%(i+1)
            dict_tmp = {}
            if psu_num in dict_psu_info:
                dict_psu = dict_psu_info[psu_num]
                dict_tmp["PN"] = dict_psu["PN"]
                dict_tmp["AirFlow"] = dict_psu["AirFlow"]
                air_flow_info[dict_psu["Name"]] = dict_tmp
    else:
        RET[RETURN_KEY1] = -1
    
    dict_fan_info = int_case.get_fan_info_all()
    if dict_fan_info == None:
        print_choose("get_fan_info_all None")
        RET[RETURN_KEY1] = -1
    else:
        #print_choose(json.dumps(dict_fan_info, ensure_ascii=False, indent=4))
        for i in range(dict_fan_info["Number"]):
            fan_num = "FAN%d"%(i+1)
            dict_tmp = {}
            if fan_num in dict_fan_info:
                dict_fan = dict_fan_info[fan_num]
                dict_tmp["PN"] = dict_fan["PN"]
                dict_tmp["AirFlow"] = dict_fan["AirFlow"]
                air_flow_info[dict_fan["Name"]] = dict_tmp
    
    print_choose(json.dumps(air_flow_info, ensure_ascii=False, indent=4))
    print_sonic(RET)
    return RET


def test_get_psu_present_info():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    psu_flag = 0
    int_case = interface()
    list_psus = int_case.get_psus()
    modelname="psu"
    tmp_product_name = get_full_product_name()
    psustatus_reg = CONFIG_INFO_MAP[modelname].get("psustatus_reg", None)
    pwrn_output_status = ""
    if psustatus_reg != None:
        bus = psustatus_reg["bus"]
        addr = psustatus_reg["addr"]
        if "-LC-" in tmp_product_name or "-LD-" in tmp_product_name:
            device = psustatus_reg["lcd_device"] if psustatus_reg["lcd_device"] != None else psustatus_reg["device"]
        else:
            device = psustatus_reg["device"]
    for i in range(len(list_psus)):
        psu_case = list_psus[i]
        psu_name = psu_case.name
        
        if psu_case.present == True:
            present = _("present ")
        else:
            psu_flag = psu_flag + 1
            present = _("not present ")
            print_choose(("%-10s: %s "%(psu_name,present)).encode('utf-8'))
            continue
        if psu_case.OutputStatus == True:
            status = _("power on ")
        else:
            psu_flag = psu_flag + 1
            status = _("Not powered")
        if psustatus_reg != None:
            offset = device[psu_name]["offset"]
            bitoffset = device[psu_name]["bitoffset"]
            ret, log = rji2cget(bus, addr, offset)
            if ret != 0:
                psu_flag = psu_flag + 1
                pwrn_output_status = _("Fault-") + log
            else:
                pwrn_output_ok = (int(log, 16) >> bitoffset) & 1 
                if pwrn_output_ok == 1:
                    pwrn_output_status = _("Normal")
                else:
                    psu_flag = psu_flag + 1
                    pwrn_output_status = _("Fault")
        print_choose(("%-10s: %s "%(psu_name, (present+status+pwrn_output_status))).encode('utf-8'))
    if psu_flag > 0:
        RET[RETURN_KEY1] = -1       
    print_sonic(RET)
    return RET

def get_drop_status(RET, list_models, droprecord_reg, model_result):
    drop_flag = 0
    drop_state = 0
    single_i2cget_flag = 0
    result = ""
    ret_status = 0
    json_info = collections.OrderedDict()
    if droprecord_reg == None:
        RET[RETURN_KEY1] = -1
        json_info[model_result] = "can't find droprecord_reg object"
        print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
        print_sonic(RET)
        return RET
    bus = droprecord_reg["bus"]
    addr = droprecord_reg["addr"]
    offset = droprecord_reg["offset"]
    num_of_offset = droprecord_reg.get("num_of_offset", "single")
    for i in range(len(list_models)):
        model_case = list_models[i]
        model_name = model_case.name 
        if single_i2cget_flag == 0:
            if num_of_offset == "single":
                reg_offset = offset
                ret_status, result = rji2cget(bus, addr, reg_offset)
                single_i2cget_flag = 1
            else:
                reg_offset = offset.get(model_name, None)
                if reg_offset == None:
                    drop_flag = drop_flag + 1
                    json_info[model_name] = "can't get %s offset" % model_name
                    continue
                ret_status, result = rji2cget(bus, addr, reg_offset)
            if ret_status != 0:
                RET[RETURN_KEY1] = -1
                json_info[model_result] = "rji2cget %d 0x%02X 0x%02X failed:%s"% (bus, addr, reg_offset, result)
                print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
                if single_i2cget_flag == 1:
                    print_sonic(RET)
                    return RET
                else:
                    drop_flag = drop_flag + 1
                    continue
        bitoff = droprecord_reg["bitoffset"].get(model_name, None)
        if bitoff != None:
            drop_state = (int(result, 16) >> bitoff ) & 1
            drop = ""
            if drop_state == 1:
                drop = _("No disconnected record")
            else:
                drop = _("Disconnected before")
                drop_flag = drop_flag + 1
            json_info[model_name] = drop
        else:
            drop_flag = drop_flag + 1
            json_info[model_name] = "can't get %s bit_offset"%model_name
    if drop_flag > 0:
        RET[RETURN_KEY1] = -1
    print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
    print_sonic(RET)

def clear_drop_status(RET, droprecord_reg, model_result):
    result = ""
    ret_status = 0
    json_info = collections.OrderedDict()
    if droprecord_reg == None:
        RET[RETURN_KEY1] = -1
        json_info[model_result] = "can't find droprecord_reg object"
        print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
        print_sonic(RET)
        return RET
    bus = droprecord_reg["bus"]
    addr = droprecord_reg["addr"]
    offset = droprecord_reg["offset"]
    num_of_offset = droprecord_reg.get("num_of_offset", "single")
    if num_of_offset == "single":
        ret_status, result = rji2cset(bus, addr, offset, 0xff)
        if ret_status != 0:
            RET[RETURN_KEY1] = -1
            json_info[model_result] = "rji2cset %d 0x%02X 0x%02X 0xff failed:%s failed:%s"% (bus, addr, offset, result)
            print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
            print_sonic(RET)
            return RET
    else:
        totalerr = 0
        for unit in offset.keys():
            ret_status, result = rji2cset(bus, addr, offset[unit], 0xff)
            if ret_status != 0:
                json_info[model_result] = "rji2cset %d 0x%02X 0x%02X 0xff failed:%s failed:%s"% (bus, addr, offset[unit], result)
                print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
                totalerr -= 1
                continue
        if totalerr < 0:
            RET[RETURN_KEY1] = -1
            print_sonic(RET)
            return RET
    my_log("ret_status=%d, result=%s"%(ret_status, result))
    json_info[model_result] = result
    print_choose(json.dumps(json_info, ensure_ascii=False, indent=4))
    print_sonic(RET)

def get_fan_drop_status(RET):
    int_case = interface()
    list_models = int_case.get_fans()
    modelname="fan"
    droprecord_config = "droprecord_reg"
    tmp_product_name = get_full_product_name()
    if "-H-" in tmp_product_name:
        droprecord_config = "h_droprecord_reg"
    droprecord_reg = CONFIG_INFO_MAP[modelname].get(droprecord_config, None)
    get_drop_status(RET, list_models, droprecord_reg, ("%s_result"%modelname));

def get_psu_drop_status(RET):
    int_case = interface()
    list_models = int_case.get_psus()
    modelname="psu"
    droprecord_reg = CONFIG_INFO_MAP[modelname].get("droprecord_reg", None)
    get_drop_status(RET, list_models, droprecord_reg, ("%s_result"%modelname));

def clear_fan_drop_status(RET):
    int_case = interface()
    list_models = int_case.get_fans()
    modelname="fan"
    droprecord_reg = CONFIG_INFO_MAP[modelname].get("droprecord_reg", None)
    clear_drop_status(RET, droprecord_reg, ("%s_result"%modelname));

def clear_psu_drop_status(RET):
    int_case = interface()
    list_models = int_case.get_psus()
    modelname="psu"
    droprecord_reg = CONFIG_INFO_MAP[modelname].get("droprecord_reg", None)
    clear_drop_status(RET, droprecord_reg, ("%s_result"%modelname));

def bmc_test_get_fan_drop():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    get_fan_drop_status(RET)
    return RET
def bmc_test_get_psu_drop():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    get_psu_drop_status(RET)
    return RET

def bmc_test_clear_fan_drop():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    clear_fan_drop_status(RET)
    return RET
def bmc_test_clear_psu_drop():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    clear_psu_drop_status(RET)
    return RET
    

def test_get_temperature():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    psu_flag = 0
    int_case = interface()
    dict_sensor_info = int_case.get_sensor_info()
    if dict_sensor_info != None:
        print_choose(json.dumps(dict_sensor_info, ensure_ascii = False,indent=4))  #
    else:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def export_gpio(gpio, export):
    cmd = "echo %d > /sys/class/gpio/%s" %(gpio, export)
    ret, log = log_os_system(cmd, 0)
    return ret

def read_gpio_value(gpio):
    ret = -1
    value = 0
    if export_gpio(gpio, "export") != 0:
        return ret, value
    cmd = "cat /sys/class/gpio/gpio%d/value" % gpio
    read_ret, read_value = log_os_system(cmd, 0)
    if export_gpio(gpio, "unexport") != 0:
        return ret, read_value
    return read_ret, read_value

def test_get_busbar_position():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    position = 0
    try:
        tmp_product_name = get_full_product_name()
        if BUSBAR_INFO == None or BUSBAR_INFO.get("extra") not in tmp_product_name:
            return RET
        gpio_list = BUSBAR_INFO.get("info")
        for gpio_info in gpio_list:
            gpio = gpio_info.get("gpio")
            offset = gpio_info.get("offset")
            ret, value = read_gpio_value(gpio)
            if ret != 0:
                break
            position = position + (int(value) << offset)
        if ret != 0:
            RET[RETURN_KEY1] = -1
            RET[RETURN_KEY2] = "fail to read gpio %d\n" % gpio
            return RET
        RET[RETURN_KEY2] = "BUSBAR position: %d\n" % position
    except Exception as e:
        RET[RETURN_KEY1] = -1
        RET[RETURN_KEY2] = "failed to get BUSBAR position: %s\n" % e
    return RET

def cpld_switch_channel(cpld_channel=None, val=0x00):
    if cpld_channel is None:
        return True
    bus = cpld_channel["bus"]
    devno = cpld_channel["devno"]
    addr = cpld_channel["addr"]
    ret, log = rji2cset(bus, devno, addr, val)
    if ret != 0:
        log_debug("  failed to open channel %d: %s" % (val, log))
    return ret

def test_get_dcdc_info():
    totalerr = 0
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    dcdc_list = {}
    for dcdc in DCDC_DEVICE:
        dicttmp = {}
        sensorname = dcdc["name"]
        val_format = dcdc["format"]
        dicttmp["Min"] = eval(val_format % dcdc["Min"])
        dicttmp["Max"] = eval(val_format % dcdc["Max"])
        gpio = dcdc.get("Gpio",None)
        if gpio != None:
            set_gpio(gpio, 1, 1)#拉高gpio
        cpld_channel = dcdc.get("cpld", None)
        if cpld_channel != None:
            val = 0x01
            cpld_switch_channel(cpld_channel, val) #open channel, sleep 0.1s
            time.sleep(0.1)
        cmd = "cat %s"%(dcdc["Value"]["loc"])
        ret, log = log_os_system(cmd, 0)
        if ret !=0 or "can't open" in log:
            dicttmp["Value"] = -99999
            totalerr += 1
        else:
            dicttmp["Value"] = eval(val_format % log)
        dicttmp["Unit"] = dcdc["Unit"]
        dcdc_list[sensorname] = dicttmp
        if gpio != None:#关闭gpio
            set_gpio(gpio, 0)
        cpld_channel = dcdc.get("cpld", None)
        if cpld_channel != None:
            val = 0x00
            cpld_switch_channel(cpld_channel, val) #close channel
    if len(dcdc_list) != 0:
        print_choose(json.dumps(dcdc_list, ensure_ascii = False,indent=4))
    else:
        totalerr += 1
    if totalerr > 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def JSONparserFile(file, div=':'):
        """
        Get a json file and create a dictionary
        """
        data = {}
        with open(file) as data_file:
            for line in data_file.readlines():
                if div in line:
                    line_list = line.split(div, 1)
                    data[line_list[0].strip()] = line_list[1].strip() 
        return data


def test_get_bmc_bios_version():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    version_file = "/var/log/fw/fw_version"
    dict_version = {
                        "MasterBmcVersion": "N/A",
                        "SlaveBmcVersion": "N/A",
                        "MasterBiosVersion": "N/A",
                        "SlaveBiosVersion": "N/A",
                        "MasterUbootVersion": "N/A",
                        "SlaveUbootVersion": "N/A",
                   }
    if not os.path.exists(version_file):
        print_choose(("%s is not exists")%(version_file))
        RET[RETURN_KEY1] = -1
        print_sonic(RET)
        return RET
    dict_ver = JSONparserFile(version_file)
    if dict_ver == None:
        print_choose(("get version failed")%(version_file))
        RET[RETURN_KEY1] = -1
        print_sonic(RET)
        return RET
    else:
        for i in dict_ver:
            re_version = dict_ver[i].replace("(","(")
            dict_ver[i] = re_version.replace(")",")")
        if "master-bmc-fw" in dict_ver:
            dict_version["MasterBmcVersion"] = dict_ver["master-bmc-fw"]+"-"+dict_ver.get("master-bmc-buildid", "N/A")
        if "slave-bmc-fw" in dict_ver :
            dict_version["SlaveBmcVersion"] = dict_ver["slave-bmc-fw"]+"-"+dict_ver.get("slave-bmc-buildid", "N/A")
        if "master-bios-fw" in dict_ver:
            dict_version["MasterBiosVersion"] = dict_ver["master-bios-fw"]
        if "slave-bios-fw" in dict_ver :
            dict_version["SlaveBiosVersion"] = dict_ver["slave-bios-fw"]
        if "master-uboot-fw" in dict_ver:
            dict_version["MasterUbootVersion"] = dict_ver["master-uboot-fw"]
        if "slave-uboot-fw" in dict_ver :
            dict_version["SlaveUbootVersion"] = dict_ver["slave-uboot-fw"]
        print_choose(json.dumps(dict_version, ensure_ascii = False,indent=4))
        print_sonic(RET)
        return RET

def bmc_test_add_bios_flash_slave():
    RET = {RETURN_KEY1 : -1, RETURN_KEY2 : ""}
    int_case = interface()
    chas_case = chassisbase()
    is_need_exit = 0
    firmware = chas_case.get_firmware_byname("firmware")
    fpga_fw = chas_case.get_fpga_fw_byname("fpga_fw")
    if firmware == None:
        print_choose("name firmware not find")
        print_sonic(RET)
        return RET
    bioscsfirst = fpga_fw.get_operate_capacity("bioscsfirst")
    if bioscsfirst == 0:
        # only asw need
        print_choose("current device doesn't need this test, and skip!")
        RET[RETURN_KEY1] = 0
        print_sonic(RET)
        return RET
    # store original bios chip select
    orig_cs = firmware.get_bios_next_boot("get_orig_cs")
    if orig_cs != "master" and orig_cs != "slave":
        print_choose("get current bios cs failed: %s" % orig_cs)
        print_sonic(RET)
        return RET
    print_choose("current bios cs: %s" % orig_cs)
    # set me recovery
    if firmware.set_me_status("recovery"):
        print_choose("failed to set me recovery")
        print_sonic(RET)
        return RET
    firmware.add_lock()
    try:
        add_spi_ret = int_case.add_spi_flash("bios", "slave")
        if add_spi_ret == False:
            print_choose("add bios(slave) to bmc failed")
        else:
            print_choose("add bios(slave) to bmc success")
    except Exception as e:
        print_choose("add bios(slave) to bmc err: %s" % str(e))
    except KeyboardInterrupt:
        print_choose("code exit because KeyboardInterrupt")
        is_need_exit = 1
    finally:
        if is_need_exit == 0:
            remove_spi_ret = int_case.remove_spi_flash_retry("bios", orig_cs)
            if remove_spi_ret == False:
                print_choose("add bios(%s) to cpu filed" % orig_cs)
            else:
                print_choose("add bios(%s) to cpu success" % orig_cs)
                RET[RETURN_KEY1] = 0
            firmware.judge_fw_channel_exist("all", True)
        firmware.set_me_status("reset")
        firmware.remove_lock()
    print_sonic(RET)
    return RET

def bmc_test_rtc():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    hw_cmd = "busybox hwclock --utc"
    ret1, rtc1_str = log_os_system(hw_cmd, 0)
    if ret1 or "0.000000 seconds" not in rtc1_str:
        RET[RETURN_KEY1] = -1
        print_choose((_("Execute command %s failed: %s")%(hw_cmd, rtc1_str)).encode('utf-8'))
        return RET
    rtc1_timeArraystart=time.strptime(rtc1_str,"%a %b %d %H:%M:%S %Y  0.000000 seconds")
    time1=time.mktime(rtc1_timeArraystart)
    otherStyleTime1 = time.strftime("%Y-%m-%d %H:%M:%S", rtc1_timeArraystart)
    print_choose((_("Start time: %s") % otherStyleTime1).encode('utf-8'))
    my_log("start time:%s" % otherStyleTime1)
    my_log("start time_stamp:" + str(time1))
    time.sleep(RTC_WAIT_TIME)

    ret2, rtc2_str = log_os_system(hw_cmd, 0)
    if ret2 or "0.000000 seconds" not in rtc2_str:
        RET[RETURN_KEY1] = -1
        print_choose((_("Execute command %s failed: %s")%(hw_cmd, rtc2_str)).encode('utf-8'))
        return RET
    rtc2_timeArraystart=time.strptime(rtc2_str,"%a %b %d %H:%M:%S %Y  0.000000 seconds")
    time2=time.mktime(rtc2_timeArraystart)
    otherStyleTime2 = time.strftime("%Y-%m-%d %H:%M:%S", rtc2_timeArraystart)
    print_choose((_("End time: %s") % otherStyleTime2).encode('utf-8'))
    my_log("end time:%s" % otherStyleTime2)
    my_log("end time_stamp:" + str(time2))
    timeCompare =  time2 - time1
    my_log("time difference:" + str(timeCompare))
    if timeCompare < RTC_THRESHOLD_LOWER or timeCompare > RTC_THRESHOLD_UPPER:
        my_log("RTC test failed.")
        RET[RETURN_KEY1] = -1
        print_choose((_("Error: RTC test failed")).encode('utf-8'))
    else:
        my_log("RTC test success")
    print_sonic(RET)
    return RET

def bmc_test_clock():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    err_total = 0
    if CLOCK_TEST is None:
        print_choose("No clock test required")
        print_sonic(RET)
        return RET
    for page in CLOCK_TEST["page"]:
        page_name = page["name"]
        reg_list = page["reg_list"]
        switch_info = page["switch"]
        switch_bus, switch_addr = get_device_addr(switch_info, CLOCK_TEST)
        switch_offset = switch_info["offset"]
        switch_val = switch_info["val"]
        switch_rval = switch_info["rval"]
        print_choose("%s:" % page_name.upper())

        # switch to the specified page
        switch_ret, switch_log = rji2cset(switch_bus, switch_addr, switch_offset, switch_val)
        if switch_ret != 0:
            print_choose("  failed to switch to %s: %s" % (page_name, switch_log))
            err_total -= 1
            continue

        # check reg value
        err_total += chk_clock_reg_val(reg_list)

        # restore orgn page
        switch_ret, switch_log = rji2cset(switch_bus, switch_addr, switch_offset, switch_rval)
        if switch_ret != 0:
            print_choose("  failed to switch to orgn page(0x%x): %s" % (switch_rval, switch_log))
            err_total -= 1
        print_choose("\r")

    if err_total < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def chk_clock_reg_val(reg_list):
    errtotal = 0
    for reg in reg_list:
        reg_name = reg["name"]
        chk = reg["chk"]
        mask = reg["mask"]
        reg_val = 0
        reg_bus, reg_addr = get_device_addr(reg, CLOCK_TEST)
        offset_list = reg["offset"]
        for reg_offset in offset_list:
            byte_offset = reg_offset["offset"]
            byte_order = reg_offset["order"]
            get_ret, get_log = rji2cget(reg_bus, reg_addr, byte_offset)
            if get_ret != 0 or "0x" not in get_log:
                output_msg = "FAILED(i2cget: bus: %s, addr: 0x%x, offset: 0x%x, failed: %s)" %(reg_bus, reg_addr, reg_offset, get_log)
                errtotal -= 1
                break
            reg_val = reg_val + int(get_log, 16) * (256 ** byte_order)
        if get_ret == 0:
            real_val = reg_val & mask
            if real_val != chk:
                output_msg = "FAILED(check: %s not 0x%x)" % (hex(real_val), chk)
                errtotal -= 1
            else:
                output_msg = "PASS"
        tplt = '\t{0:<20} {1:<}'
        formatstr = tplt.format(reg_name, output_msg)
        print_choose(formatstr)
    return errtotal

def get_device_addr(custom, default):
    bus = custom.get("bus", None)
    if bus == None:
        bus = default["bus"]
    addr = custom.get("addr", None)
    if addr == None:
        addr = default["addr"]
    return bus, addr

def bmc_test_netcard_smbus():
    return bmc_test_netcard_info(check_netcart_smbus)

def bmc_test_netcard_diagnosis():
    return bmc_test_netcard_info(check_netcart_diagnosis)

def bmc_test_netcard_info(func):
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    product_name = get_full_product_name()
    check_ret, check_log = check_product_netcard_requirement(product_name)
    if check_ret:
        print_choose(check_log)
        print_sonic(RET)
        return RET
    err_total = 0
    product_info = NETCARD_INFO["product"][product_name]
    tplt = '{0:<10} {1:<10} {2:<}'
    for slot_info in product_info:
        position = slot_info["pos"]
        cardtype = slot_info["cardtype"]
        test_stat = ""
        slotreg = slot_info.get("slotreg", NETCARD_INFO["slotreg"])
        present_ret, present_stat = get_netcard_present(position, slotreg)
        if present_ret:
            print_choose(tplt.format(position.upper(), present_stat, test_stat))
            err_total -= 1
            continue
        smbus_info = slot_info.get("smbus_info", NETCARD_INFO["smbus_info"])
        try:
            test_ret = func(position, cardtype, smbus_info)
            if test_ret:
                err_total -= 1
        except:
            print_choose(tplt.format(position.upper(), "error: %s" % func.__name__, test_stat))
            err_total -= 1
    if err_total < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def check_netcart_diagnosis(slot, cardtype, smbus_info):
    tplt = '  {0:<30} {1:<10} {2:<}'
    present = "PRESENT"
    errtotal = 0
    print_choose("\n%s:" % (slot.upper()))
    slot_bus = smbus_info.get(slot, None)
    diagnosis_info = smbus_info["diagnosis"].get(cardtype, None)
    if diagnosis_info is None:
        msg = "No NETCARD diagnosis required on %s" % cardtype
        print_choose(tplt.format(slot.upper(), present, msg))
        return errtotal
    if slot_bus is None:
        stat = "NOT_OK"
        print_choose(tplt.format(slot.upper(), present, stat))
        print_choose("\tSmbus information of %s conf is missing" % slot)
        errtotal -= 1
        return errtotal
    addr = diagnosis_info["addr"]
    reg_info = diagnosis_info["reg_info"]
    for reg in reg_info:
        stat = "NOT_OK"
        name = reg["name"]
        offset = reg["offset"]
        way = reg["way"]
        get_ret, get_log = rji2cget(slot_bus, addr, offset)
        if get_ret != 0 or "0x" not in get_log:
            msg = "Failed to i2cget -f -y %s 0x%02x 0x%02x: %s" % (slot, slot_bus, addr, offset, get_log)
            print_choose(tplt.format(name, stat, msg))
            errtotal -= 1
            continue
        msg = "Val: " + get_log
        if way == "show":
            stat = "OK"
        elif way == "val":
            get_val = int(get_log, 16)
            check_val = reg["val"]
            if get_val == check_val:
                stat = "OK"
            else:
                errtotal -= 1
                msg = msg + ", not 0x%02x" % check_val
        elif way == "threshold":
            get_val = int(get_log, 16)
            threshold = reg["threshold"]
            max = threshold.get("max", None)
            min = threshold.get("min", None)
            if max != None and get_val >= max:
                msg = msg + ", not less then 0x%2x" % max
                errtotal -= 1
            elif min != None and get_val <= min:
                msg = msg + ", not more then 0x%2x" % min
                errtotal -= 1
            else:
                stat = "OK"
        else:
            msg = "unknown way"
            errtotal -= 1
        print_choose(tplt.format(name, stat, msg))
    return errtotal


def check_product_netcard_requirement(product_name):
    msg = ""
    if NETCARD_INFO is None:
        msg = "No NETCARD test required"
        return -1, msg
    product = NETCARD_INFO.get("product")
    if product.get(product_name) is None:
        msg = "No NETCARD test required on %s" % product_name
        return -1, msg
    return 0, msg

def get_netcard_present(slot, slotreg):
    ret = -1
    msg = ""
    slot_spec = slotreg.get(slot, None)
    if slot_spec is None:
        msg = "Reg information of %s conf is None" % slot
        return ret, msg
    present_info = slot_spec.get("present", slotreg["present"])
    if len(present_info) == 0:
        msg = "Present information of %s conf is None" % slot
        return ret, msg
    bus, addr = get_device_addr(slot_spec, slotreg)
    offset = slot_spec["offset"]
    get_ret, get_log = rji2cget(bus, addr, offset)
    if get_ret != 0 or "0x" not in get_log:
        msg = "Failed to get %s in-place information(bus: %s, addr: 0x%x, offset: 0x%x): %s" %(slot, bus, addr, offset, get_log)
        return ret, msg
    val = int(get_log, 16)
    mask = present_info["mask"]
    absent = present_info["absent"]
    if (val & mask) == absent:
        msg = "ABSENT"
        ret = 1
        return ret, msg
    msg = "PRESENT"
    ret = 0
    return ret, msg

def check_netcart_smbus(slot, cardtype, smbus_info):
    stat = "ABNORMAL"
    present = "PRESENT"
    errtotal = 0
    msg = ""
    tplt = '{0:<10} {1:<10} {2:<}'
    slot_bus = smbus_info.get(slot, None)
    check_list = smbus_info.get(cardtype, None)
    if slot_bus is None or check_list is None:
        msg = "\tSmbus information of %s conf is missing" % slot
        errtotal -= 1
    if errtotal == 0:
        detect_ret, detect_log = rji2cdetect(slot_bus)
        if detect_ret:
            errtotal -= 1
            msg = "\tFailed to detect %s smbus information(bus: %s): %s" % (slot, slot_bus, detect_log)
        else:
            for sub in check_list:
                addr = sub["addr"]
                addr_str = "%02x" % addr
                # Detect if a device exists on this address
                if addr_str in detect_log:
                    continue
                # The mounted device will not be detected.
                # If the test register is configured, further confirmation will be made.
                offset = sub.get("offset")
                if offset is None:
                    errtotal -= 1
                    msg = msg + "\t0x%02x is not in bus %s.\n" % (addr, slot_bus)
                    continue
                # Confirm if there is a device attached to this address
                sub_i2cdetect_ret, sub_i2cdetect_log = rji2cdetect(slot_bus, addr, addr)
                if sub_i2cdetect_ret != 0 or "UU" not in sub_i2cdetect_log:
                    errtotal -= 1
                    msg = msg + "\t0x%02x(UU) is not in bus %s, ret: %d, log:\n%s\n" % \
                        (addr, slot_bus, sub_i2cdetect_ret, sub_i2cdetect_log)
                    continue
                # Access specific device registers to confirm device existence
                sub_i2cget_ret, sub_i2cget_log = rji2cget(slot_bus, addr, offset)
                if sub_i2cget_ret != 0 or "0x" not in sub_i2cget_log:
                    errtotal -= 1
                    msg = msg + "\tFail to get %d 0x%02x 0x%02x, ret: %d, log: %s.\n" % \
                        (slot_bus, addr, offset, sub_i2cget_ret, sub_i2cget_log)
            if errtotal < 0:
                msg = msg + "bus %s infofomation:\n%s\n" % (slot_bus, detect_log)
            else:
                stat = "NORMAL"
    print_choose(tplt.format(slot.upper(), present, stat))
    if len(msg):
        print_choose(msg)
    return errtotal

def bmc_test_get_netcard_intrpt_signal():
    return bmc_test_netcard_intprt_signal("get")

def bmc_test_clear_netcard_intrpt_signal():
    return bmc_test_netcard_intprt_signal("clear")

def bmc_test_netcard_intprt_signal(action):
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    product_name = get_full_product_name()
    check_ret, check_log = check_product_netcard_requirement(product_name)
    if check_ret:
        print_choose(check_log)
        print_sonic(RET)
        return RET
    err_total = 0
    product_info = NETCARD_INFO["product"][product_name]
    tplt = '{0:<10} {1:<}'
    for slot_info in product_info:
        position = slot_info["pos"]
        action_stat = ""
        slotreg = slot_info.get("slotreg", NETCARD_INFO["slotreg"])
        if action == "get":
            action_ret, action_stat = check_netcart_intrpt_signal(position, slotreg)
        else:
            action_ret, action_stat = clear_netcart_intrpt_signal(position, slotreg)
        print_choose(tplt.format(position.upper(), action_stat))
        if action_ret:
            err_total -= 1
    if err_total < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def check_netcart_intrpt_signal(slot, slotreg):
    ret = -1
    msg = ""
    slot_spec = slotreg.get(slot, None)
    if slot_spec is None:
        msg = "Signal information of %s conf is None" % slot
        return ret, msg
    bus, addr = get_device_addr(slot_spec, slotreg)
    signal_info = slot_spec.get("signal", slotreg["signal"])
    offset = slot_spec["offset"]
    get_ret, get_log = rji2cget(bus, addr, offset)
    if get_ret != 0 or "0x" not in get_log:
        msg = "Failed to get %s signal information(bus: %s, addr: 0x%02x, offset: 0x%02x): %s" %(slot, bus, addr, offset, get_log)
        return ret, msg
    val = int(get_log, 16)
    mask = signal_info["mask"]
    intrptless = signal_info["intrptless"]
    if (val & mask) == intrptless:
        msg = "OK"
        ret = 0
        return ret, msg
    msg = "NOT_OK: %s" % get_log
    return ret, msg

def clear_netcart_intrpt_signal(slot, slotreg):
    ret = -1
    msg = ""
    slot_spec = slotreg.get(slot, None)
    if slot_spec is None:
        msg = "Signal information of %s conf is None" % slot
        return ret, msg
    bus, addr = get_device_addr(slot_spec, slotreg)
    signal_info = slot_spec.get("signal", slotreg["signal"])
    offset = slot_spec["offset"]
    clear = signal_info["clear"]
    ret, set_log = rji2cset(bus, addr, offset, clear)
    if ret != 0:
        msg = "NOT_OK: (bus: %s, addr: 0x%02x, offset: 0x%02x, clear: 0x%02x) %s" %(slot, bus, addr, offset, clear, set_log)
        return ret, msg
    msg = "OK"
    return ret, msg

def bmc_test_get_mac_threshold(ch_mac_v):
    threshold = {}
    if MAC_THRESHOLD.get("type", "fixed") == "non-fixed":
        # The conversion value of the CPLD register value of MAC voltage
        # corresponds one-to-one with the range of voltage regulation difference
        threshold_map = MAC_THRESHOLD["map"]
        if ch_mac_v in threshold_map.keys() and len(threshold_map[ch_mac_v]) == 2:
            threshold["Min"] = threshold_map[ch_mac_v][0]
            threshold["Max"] = threshold_map[ch_mac_v][1]
    else:
        # Unique difference range
        threshold = MAC_THRESHOLD
    return threshold

def bmc_test_moc_svid():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    int_case = interface()
    dict_sensor_info = int_case.get_sensor_info()
    check_mac_v = True
    ch_mac_v = 0
    min_threshold = 0
    max_threshold = 0

    if dict_sensor_info == None:
        print_choose("dict_sensor_info:error")
        print_sonic(RET)
        RET[RETURN_KEY1] = -1
        return RET
    #mac svid --IS_SUPPORT_MAC: special- 0 unsupport; default- 1 support
    if ALI_BMC.get("IS_SUPPORT_MAC", 1) == 1:
        CPLD_AVS = ALI_BMC.get("CPLD_AVS", None)
        if CPLD_AVS is not None:
            ret, ch_mac_v_str = rji2cget(CPLD_AVS["bus"], CPLD_AVS["devno"], CPLD_AVS["addr"])
            if ret != 0 or "0x" not in ch_mac_v_str:
                print_choose((_("MAC voltage CPLD register value converted value: %s")%ch_mac_v_str).encode('utf-8'))
                check_mac_v = False
                RET[RETURN_KEY1] = -1
            else:
                ch_mac_v = MAC_VOUT_MAP.get(int(ch_mac_v_str, 16), None)
                if ch_mac_v is None:
                    print_choose((_("MAC voltage CPLD register value converted value: %s")%ch_mac_v_str).encode('utf-8'))
                    check_mac_v = False
                    RET[RETURN_KEY1] = -1
                else:
                    print_choose((_("MAC voltage CPLD register value converted value: %.4fV")%ch_mac_v).encode('utf-8'))
        else:
            try:
                ret, ch_mac_v_str = int_case.get_mac_transform_rov()
                if ret == -1 or ch_mac_v_str == None:
                    print_choose((_("MAC voltage CPLD register value converted value: %s")%ch_mac_v_str).encode('utf-8'))
                    check_mac_v = False
                    RET[RETURN_KEY1] = -1
                else:
                    ch_mac_v = float(ch_mac_v_str)
                    print_choose((_("MAC voltage CPLD register value converted value: %.4fV")%ch_mac_v).encode('utf-8'))
            except Exception as e:
                print_choose((_("MAC voltage CPLD register value conversion failed: %s")% e).encode('utf-8'))
                check_mac_v = False
                RET[RETURN_KEY1] = -1
        MAC_CORE_V = ALI_BMC.get("MAC_CORE_V", None)
        real_mac_v = None
        if MAC_CORE_V != None:
            real_mac_v = dict_sensor_info.get(MAC_CORE_V, None)
        if real_mac_v == None:
            print_choose(_("MAC actual voltage value: None").encode('utf-8'))
            check_mac_v = False
            RET[RETURN_KEY1] = -1
        else:
            print_choose((_("MAC actual voltage value: %.4fV")%real_mac_v["Value"]).encode('utf-8'))
        if MAC_THRESHOLD != None:
            threshold = bmc_test_get_mac_threshold(ch_mac_v)
            min_threshold = threshold.get("Min", None)
            max_threshold = threshold.get("Max", None)
        if min_threshold == None or max_threshold == None:
            print_choose(_("MAC deviation Min: %s Max: %s")%(str(min_threshold).encode('utf-8'), str(max_threshold).encode('utf-8')))
            RET[RETURN_KEY1] = -1
        elif real_mac_v != None:
            deviation = ch_mac_v - real_mac_v["Value"]
            if check_mac_v and (deviation > max_threshold or deviation < min_threshold):
                print_choose(_("  FAILED: MAC deviation exceeds range: [%.4f, %.4f]") % (min_threshold, max_threshold))
                RET[RETURN_KEY1] = -1
    else:
        pass
    #cpu svid
    errtotal = 0
    cpu_chk_list = ALI_BMC.get("CPU_CHK_LIST", None)
    cpu_platform = ALI_BMC.get("CPU_PLATFORM", None)
    if cpu_chk_list == None:
        cpu_chk_list = ["VCCIN_V"]
    for sensor in cpu_chk_list:
        check_cpu_v = True
        real_cpu_v = dict_sensor_info.get(sensor, None)
        if real_cpu_v == None:
            tmp_log = (_("CPU %s actual voltage value: None") % sensor).encode('utf-8')
            check_cpu_v = False
            errtotal -= 1
        else:
            tmp_log = (_("CPU %s actual voltage value: %.4fV")%(sensor, real_cpu_v["Value"])).encode('utf-8')
            ch_cpu_min_v = real_cpu_v.get("Min", None)
            ch_cpu_max_v = real_cpu_v.get("Max", None)
        if cpu_platform == "ICELAKE":
            if real_cpu_v != None and ch_cpu_min_v != None and ch_cpu_max_v != None:
                print_choose((_("CPU %s regulator register value range: (%.4fV, %.4fV)") % (sensor, ch_cpu_min_v, ch_cpu_max_v) ).encode('utf-8'))
            else:
                print_choose(_("CPU %s regulator register value: None").encode('utf-8'))
                check_cpu_v = False
                errtotal -= 1
            print_choose(tmp_log)
            if check_cpu_v and (real_cpu_v["Value"] <= ch_cpu_min_v or real_cpu_v["Value"] >= ch_cpu_max_v):
                print_choose((_("  FAILED: CPU %s actual voltage value needs to be within regulator register value range") % sensor).encode('utf-8'))
                errtotal -= 1
        else:
            # default paltform: GRANGEVILLE
            ch_cpu_v = ALI_BMC.get("CPU_CHK_MOC", None)
            if ch_cpu_v == None:
                print_choose((_("CPU %s regulator register value: None") % sensor).encode('utf-8'))
                check_cpu_v = False
                errtotal -= 1
            else:
                print_choose((_("CPU %s regulator register value: %.4fV") % (sensor, ch_cpu_v)).encode('utf-8'))
            print_choose(tmp_log)
            if check_cpu_v and real_cpu_v["Value"] < ch_cpu_v:
                print_choose((_("  FAILED: CPU %s actual voltage value needs to be greater than or equal to regulator register value") % sensor).encode('utf-8'))
                errtotal -= 1
    if errtotal < 0:
        RET[RETURN_KEY1] = -1
    print_sonic(RET)
    return RET

def send_commands(commands):
    for command in commands:
        cmd = command.get("cmd")
        sleep_time = command.get("sleep", 0)
        ret, msg = log_os_system(cmd, 0)
        if sleep_time != 0:
            time.sleep(sleep_time)
        if ret != 0:
            log_debug("failed %s" % cmd)
            print("failed %s" % cmd)
            return False, cmd
        else:
            log_debug("succeed %s" % cmd)
    return True, "success"

def get_mac_vout_exponent_xdpe(cmd):
    u'''获取MAC电压精度'''

    ret, log = log_os_system(cmd, 0)
    if ret or len(log) == 0:
        print_choose(_("    [%s] Command execution error: %d") % (cmd, ret))
        return False, None
    vout_mode = log.strip()
    mac_vout_exponent = MAC_VOUT_EXPONENT
    if mac_vout_exponent is None:
        print_choose(_("    Error retrieving MAC_VOUT_EXPONENT configuration"))
        return False, None
    if vout_mode not in mac_vout_exponent.keys():
        print_choose(_("    VOUT_MODE register value abnormal: %s") % vout_mode)
        return False, None
    exponent = mac_vout_exponent[vout_mode]

    return True, exponent

def bmc_test_avs_set_xdpe(volattr = None, set_vol = None):
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    if SET_AVS_TEST is None:
        print_choose(_("Error retrieving SET_AVS_TEST configuration"))
        print_sonic(RET)
        RET[RETURN_KEY1] = -1
        return RET

    test_item = SET_AVS_TEST.get(volattr, None)
    if test_item is None:
        print_choose(_("Error retrieving test_item configuration"))
        print_sonic(RET)
        RET[RETURN_KEY1] = -1
        return RET
    test_name = test_item.get("test_name", None)
    print_choose("%s" % test_name)
    err = 1
    while True:
        #获取当前末端电压
        read_vout_cmd = test_item.get("read_vout", None)
        ret, log = log_os_system(read_vout_cmd, 0)
        if ret or len(log) == 0:
            print_choose(_("    Failed to retrieve current voltage: %d") % ret)
            break
        print_choose(_("    Before voltage regulation, current voltage is %.2f mV") % float(log))
        get_vol_cmd = test_item.get("get_vol", None)
        ret, log = log_os_system(get_vol_cmd, 0)
        if ret or len(log) == 0:
            print_choose(_("    Failed to retrieve current voltage regulation value: %d") % ret)
            break
        get_vol = int(log, 16)
        print_choose(_("    Before voltage regulation, current voltage regulation value is 0x%x") % get_vol)
        min_vol = test_item.get("min", None)
        max_vol = test_item.get("max", None)
        init_vol = test_item.get("init_vol", None)
        if min_vol is not None and max_vol is not None:
            if set_vol < min_vol or set_vol > max_vol:
                print_choose(
                    _("    Target voltage regulation value %.2f mV exceeds threshold [%.2f mV, %.2f mV], no regulation performed") %
                    (set_vol, min_vol, max_vol))
                break
        switch_page1_cmds = test_item.get("switch_page", None)
        if switch_page1_cmds is None:
            print_choose(_("    Error retrieving switch_page1 configuration"))
            break
        ret, val = send_commands(switch_page1_cmds)
        if not ret:
            print_choose(_("    switch_page failed: %s") % val)
            break
        get_vout_mode_cmd = test_item.get("get_vout_mode", None)
        if get_vout_mode_cmd is None:
            print_choose(_("    Error retrieving get_vout_mode configuration"))
            break
        ##如沟通，因电压接口读取的电压为去尾取整数，合法区间727.5-728之间的值写入后回读值为727MV，此部分区间值生测软件内部按照728mv写入
        if math.floor(set_vol) < min_vol:
            set_vol = math.ceil(set_vol)
        ret, vout_exponent = get_mac_vout_exponent_xdpe(get_vout_mode_cmd)
        if not ret or vout_exponent is None:
            break
        set_vol_hex = set_vol / pow(2, vout_exponent) / 1000
        # 调低压向上取整，调高压/常压向下取整
        if set_vol < init_vol:
            set_vol_hex = math.ceil(set_vol_hex)
        else:
            set_vol_hex = int(set_vol_hex)
        set_vol_cmd = test_item.get("set_vol", None)
        cmd = set_vol_cmd % set_vol_hex
        ret, log = log_os_system(cmd, 0)
        if ret:
            print_choose(_("    Failed to set target voltage regulation value 0x%x: %d") % (set_vol_hex, ret))
            break
        ret, log = log_os_system(get_vol_cmd, 0)
        if ret or len(log) == 0:
            print_choose(_("    Failed to retrieve current voltage value: %d") % ret)
            break
        get_vol = int(log, 16)
        print_choose(_("    After voltage regulation, current voltage regulation value is 0x%x") % get_vol)
        if get_vol != set_vol_hex:
            print_choose(_("    Current voltage regulation value 0x%x does not match the set target voltage regulation value 0x%x") % (get_vol, set_vol_hex))
            break
        #等待末端电压刷新
        time.sleep(1)
        read_vout_cmd = test_item.get("read_vout", None)
        ret, log = log_os_system(read_vout_cmd, 0)
        if ret or len(log) == 0:
            print_choose(_("    Failed to retrieve current voltage: %d") % ret)
            break
        vout = float(log)
        print_choose(_("    After voltage regulation, current voltage is %.2f mV") % vout)
        print_choose(_("    Voltage threshold [%.2f mV, %.2f mV]") % (min_vol, max_vol))
        if vout < min_vol or vout > max_vol:
            print_choose(_("    Current voltage exceeds threshold"))
            break
        print_choose(_("    Voltage regulation successful"))
        err = 0
        break
    recover_page_cmds = test_item.get("recover_page", None)
    if recover_page_cmds is None:
        print_choose(_("    Error retrieving recover_page configuration"))
    ret, val = send_commands(recover_page_cmds)
    if ret == False:
        print_choose(_("    recover_page failed: %s") % val)
    if err > 0:
        print_choose(_("    Voltage regulation failed, please execute to restore normal voltage"))
        RET[RETURN_KEY1] = -1
    print_sonic(RET)

    return RET

def bmc_test_service_stop():
    units = ["cpumon", "dcdcmon", "powermon", "fanctrl", "read-uboot-mac"]
    for unit in units:
        cmd = "systemctl stop %s;"%unit
        my_log(cmd)
        log_os_system(cmd, 0)

def bmc_test_service_start():
    units = ["cpumon", "dcdcmon", "powermon", "fanctrl", "read-uboot-mac"]
    for unit in units:
        cmd = "systemctl start %s;"%unit
        my_log(cmd)
        log_os_system(cmd, 0)

def bmc_test_leakage():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    if LEAKAGE_INFO is None:
        print_choose("No Leakage test required")
        print_sonic(RET)
        return RET
    tmp_product_name = get_full_product_name()
    extra = LEAKAGE_INFO.get("extra", None)
    if extra not in tmp_product_name:
        print_choose("No Leakage test required on %s" % tmp_product_name)
        print_sonic(RET)
        return RET
    bus = LEAKAGE_INFO["bus"]
    addr = LEAKAGE_INFO["addr"]
    reg = LEAKAGE_INFO["reg"]
    mask = LEAKAGE_INFO["mask"]
    val_map = LEAKAGE_INFO["val_map"]

    ret, log = rji2cget(bus, addr, reg)
    if ret != 0 or "0x" not in log:
        print_choose("Failed to get leakage information(bus: %s, addr: 0x%02x, reg: 0x%02x): %s" %(bus, addr, reg, log))
        RET[RETURN_KEY1] = -1
        print_sonic(RET)
        return RET

    reg_val = int(log, 16)
    val = reg_val & mask
    val_info = val_map.get(val, None)
    if val_info is None:
        msg = "Unknown error"
        RET[RETURN_KEY1] = -1
    else:
        msg = _(val_info["msg"])
        RET[RETURN_KEY1] = val_info["code"]
    output = '    {0:<15}\t{1:<}'.format("Val: %s" % log, "Status: %s" % msg)
    print_choose(output)
    print_sonic(RET)
    return RET

def bmc_test_ecc_error():
    RET = {RETURN_KEY1 : 0, RETURN_KEY2 : ""}
    if ECC_ERR_INFO is None:
        print_choose("No ECC test required")
        print_sonic(RET)
        return RET
    dev_case = devicebase()
    try:
        reg_info = ECC_ERR_INFO["reg_info"]
        ret, log = dev_case.get_value(reg_info)
        if not ret or "0x" not in log:
            raise Exception("fail to exec \"%s %s %s\", log: %s" % \
                (reg_info["way"], reg_info["addr"], reg_info["digit"], log))
        reg_val = int(log, 16)

        check_list = ECC_ERR_INFO["check_list"]
        if len(check_list) == 0:
            raise Exception("ECC check_list is empty")

        tplt = '    {0:<35} {1:<4}\t{2:<}'
        for it in check_list:
            name = it["name"]
            offset = it["offset"]
            mask = it["mask"]
            chk = it["chk"]
            status = "OK"
            val = (reg_val >> offset) & mask
            if val > chk:
                RET[RETURN_KEY1] = -1
                status = "NOT_OK, exceeded max value(%d)" % chk
            print_choose(tplt.format("%s:" % name, "%d" % val, "Status: %s" % status))
    except Exception as e:
        RET[RETURN_KEY1] = -1
        print_choose(str(e))
    
    print_sonic(RET)
    return RET

def CMD_dispatch():
    if rj_diag_args.operations == None:
        ApplicationInstance()
        start()
    elif rj_diag_args.json_str != None:
        eval(rj_diag_args.operations)(rj_diag_args.json_str)
    elif rj_diag_args.processid != None:
        eval(rj_diag_args.operations)(rj_diag_args.processid)
    elif rj_diag_args.ledattribute!= None and rj_diag_args.ledtype != None:
        eval(rj_diag_args.operations)(rj_diag_args.ledtype, rj_diag_args.ledattribute)
    elif rj_diag_args.action != None:
        eval(rj_diag_args.operations)(rj_diag_args.action)
    else:
        eval(rj_diag_args.operations)()

def CMD_dispatch(cmdstr):
    rj_diag_args.operations = "for none"
    split_json = cmdstr.split(" -json ")
    arg = split_json[0].split()
    if len(split_json) > 1:
        arg.append('-json')
        arg.append(split_json[1][1:-1])

    log_debug("CMD_dispatch(%s) argv = %s"%(cmdstr, str(arg)))
    bmc_set_i18n()
    par = argparse.ArgumentParser()
    global choices_g
    par.add_argument("-o","--operations",type=str,
    choices=choices_g,
    help=("For restful call").encode('utf-8'))
    par.add_argument("-pid","--processid",type=str,help = ("Process ID to kill").encode('utf-8'))
    par.add_argument("-led","--ledtype",type=str,help = ("Led type to set").encode('utf-8'))
    par.add_argument("-ledattr","--ledattribute",type=str,help = ("Led attribute to set").encode('utf-8'))
    par.add_argument("-action","--action",type=str,help = ("Action to perform").encode('utf-8'))
    par.add_argument("-json","--json_str",type=str,help = ("JSON parameters").encode('utf-8'))
    par.add_argument("-volattr", "--volattr", type = str, help = ("Voltage attribuite to set").encode('utf-8'))
    par.add_argument("-vol", "--vol", type = float, help = ("Voltage value").encode('utf-8'))
    args_in = par.parse_args(arg)
    init_env()
    if args_in.operations == None:
        ApplicationInstance()
        start()
    elif args_in.json_str != None:
        ret = eval(args_in.operations)(args_in.json_str)
    elif args_in.processid != None:
        ret= eval(args_in.operations)(args_in.processid)
    elif args_in.ledattribute != None and args_in.ledtype != None:
        ret = eval(args_in.operations)(args_in.ledtype, args_in.ledattribute)
    elif args_in.action != None:
        ret = eval(args_in.operations)(args_in.action)
    elif args_in.volattr != None and args_in.vol != None:
        ret = eval(args_in.operations)(args_in.volattr, args_in.vol)
    else:
        ret = eval(args_in.operations)()

    unlockInstance();
    return str(ret)


