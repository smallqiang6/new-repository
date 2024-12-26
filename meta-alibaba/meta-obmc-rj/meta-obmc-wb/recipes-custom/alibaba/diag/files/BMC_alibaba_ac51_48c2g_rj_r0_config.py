#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
#from  ruijiecommon import *
from collections import OrderedDict

PCA9548START  = 0
PCA9548BUSEND = 0

RUIJIE_CARDID      = 0x00004075
RUIJIE_PRODUCTNAME = "ac51-48c2g"

MENU_ID_ROOT             = 0
MENU_ID_TEST_SINGLE      =11
MENU_ID_DDR_TEST         =12
MENU_ID_EMMC_TEST        =13
MENU_ID_BMC_DRIVER_TEST  =14
MENU_ID_PSU_TEST         =15
MENU_ID_FAN_TEST         =16
MENU_ID_STRESS_TEST      =18
MENU_ID_LED_TEST         =19
MENU_ID_FAN_SPEED_SET_TEST =20

FAN_PROTECT = { }

E2_DEV = {
    "E2_SYSFRU": {"canreset": True, "list": [ {"bus": 2, "addr": 0x57}], "restartserv": "",},
    "E2_EMMC_CARD": {"canreset": True, "list": [ {"bus": 2, "addr": 0x50}], "restartserv": "",},
    "E2_CPU": {"canreset": True, "list": [ {"bus": 1, "addr": 0x50}], "restartserv": "",},
}

ALI_E2_DEV = {
    'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
    'emmc_card': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0050/eeprom', 'way': 'sysfs'},
    'cpu': {'loc': '/sys/bus/i2c/devices/i2c-1/1-0050/eeprom', 'way': 'sysfs'},
}

DCDC_DEVICE = [
    {
        "name": "RTC_3.3_V",
        "Min": 2676,
        "Max": 3993,
        "format": "float(float(%s)/1000)",
        "Value": {
            "loc": "/sys/bus/platform/devices/ast_adc.0/in7_input",
            "way": "sysfs"
        },
        "Unit": "V",
        "Gpio": 149,
    }
]

CPLD_TEST = [
    {"name": "BASE板CPLD", "bus": 0, "addr": 0x0D, "test_reg": 0x0F},
    {"name": "PORT-CPLD", "bus": 5, "addr": 0x30, "test_reg": 0x0F},
    {"name": "CPU板CPLD", "bus": 1, "addr": 0x0D, "test_reg": 0x05},

]

FPGA_TEST = [
    {"name": "FPGA", "bus": 5, "addr": 0x36, "test_reg": 0x8},
]

ALI_BMC = {"FRU_NUM": 4, "NO_FRU_NUM": 3, "PCIE_CHK_STR": "40 65 06 05 00", "MDIO_8367": 1, "CPU_CHK_MOC":1.74, "IS_SUPPORT_MAC": 0}

#################x86_2v23_current#################生测菜单项 #################################
test_BMC_NOMAL_item0 = {"name": "CPU 信息显示", "deal": "bmc_get_cpu_info"}
test_BMC_NOMAL_item1 = {"name": "BMC DDR 信息显示", "deal": "bmc_get_ddr_info"}
test_BMC_NOMAL_item2 = {"name": "BMC eMMC 信息显示", "deal": "bmc_get_emmc_info"}
test_BMC_NOMAL_item3 = {"name": "BMC通过PECI访问CPU", "deal": "bmc_test_peci"}
test_BMC_NOMAL_item4 = {"name": "BMC访问CPU SML1(ME)", "deal": "bmc_test_SML0"}
test_BMC_NOMAL_item5 = {"name": "BMC I2C设备扫描", "deal": "bmc_test_i2c_scan"}
test_BMC_NOMAL_item7 = {"name": "系统/板级/风扇FRU EEPROM读取", "deal": "test_tbd"}#CPU ipmitool fru
test_BMC_NOMAL_item8 = {"name": "温感温度读取", "deal": "test_tbd"} # CPU platformutil.py sensor status
test_BMC_NOMAL_item9 = {"name": "DC/DC电压电流读取", "deal": "bmc_get_dcdc_info"}
test_BMC_NOMAL_item10 = {"name": "BMC GPIO测试", "deal": "bmc_test_cpu_gpio"}
test_BMC_NOMAL_item11 = {"name": "BMC CPLD测试", "deal": "bmc_cpld_check"}

test_PSU_item1 = {"name": "PSU FRU信息读取", "deal": "bmc_test_get_psu_rfu_info"}
test_PSU_item2 = {"name": "PSU电压电流功耗读取", "deal": "bmc_test_get_psu_info"}
test_PSU_item3 = {"name": "PSU状态监测(在位信号,ACOK,PWROK)", "deal": "bmc_test_get_psu_present"}

test_FAN_item1 = {"name": "风扇状态监测(在位信号，风向)", "deal": "bmc_test_get_fan_present"}
test_FAN_item2 = {"name": "风扇转速设置", "deal": "test_signal", "childid": MENU_ID_FAN_SPEED_SET_TEST}
test_FAN_item3 = {"name": "风扇转速读取", "deal": "bmc_test_get_fan_speed"}
test_Firmware_TMP_item1 = {"name": "通过MDIO读取54616s和5387寄存器", "deal": "bmc_test_MDIO"}
test_OPT_MODULE_item1 = {"name": "光模块在位检测", "deal": "test_tbd"}
test_strss_item1 = {"name": "DDR压力测试", "deal": "test_signal", "childid": MENU_ID_DDR_TEST}
test_strss_item3 = {"name": "eMMC压力测试", "deal": "test_signal", "childid": MENU_ID_EMMC_TEST}
test_strss_item4 = {"name": "I2C压力测试", "deal": "bmc_test_i2c_stress"}
test_strss_item5 = {"name": "MDIO压力测试", "deal": "bmc_test_MDIO_stress"}

test_led_item1 = {"name": "系统LED测试(SYS,PWR,FAN)", "deal": "bmc_test_sysled" }
test_led_item2 = {"name": "风扇模块LED测试", "deal": "bmc_test_fanled"}
test_led_item3 = {"name": "Location LED测试", "deal": "bmc_test_locationled"}

menuList = [
    {
        "menuid": MENU_ID_ROOT, "value": [
            {"name": "单项测试", "deal": "test_signal", "childid": MENU_ID_TEST_SINGLE},
            #{"name" :"所有测试", "deal": "test_all"},
            #{"name" :"拷机测试", "deal": "test_loop"},
            #{"name" :"拷机结果查看", "deal": "test_loop_read"},
            #{"name" :"拷机结果删除", "deal": "test_loop_delete"},
            #{"name" :"配置加载", "deal": "test_config"},
            #test_sys_reload_item,
            #{"name": "系统配置", "deal": "test_sysconfig", "childid": MENU_ID_TEST_SYS_CONFIG},
        ]
    },

    {
        "menuid": MENU_ID_TEST_SINGLE, "parentid": MENU_ID_ROOT, "value": [
            {"name": "BMC 接口驱动测试", "deal": "test_signal", "childid": MENU_ID_BMC_DRIVER_TEST},
            {"name": "PSU测试", "deal": "test_signal", "childid": MENU_ID_PSU_TEST},
            {"name": "风扇测试", "deal": "test_signal", "childid": MENU_ID_FAN_TEST},
            {"name": "压力测试", "deal": "test_signal", "childid": MENU_ID_STRESS_TEST},
            {"name": "LED测试", "deal": "test_signal", "childid": MENU_ID_LED_TEST},
        ]
    },

    {
        "menuid": MENU_ID_BMC_DRIVER_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            test_BMC_NOMAL_item0,
            test_BMC_NOMAL_item1,
            test_BMC_NOMAL_item2,
            test_BMC_NOMAL_item3,
            test_BMC_NOMAL_item4,
            test_BMC_NOMAL_item5,
            test_BMC_NOMAL_item7,
            test_BMC_NOMAL_item8,
            test_BMC_NOMAL_item9,
            test_BMC_NOMAL_item10,
            test_BMC_NOMAL_item11,
            test_Firmware_TMP_item1,
        ]
    },

    {
        "menuid": MENU_ID_PSU_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            test_PSU_item1,
            test_PSU_item2,
            test_PSU_item3,
        ]
    },

    {
        "menuid": MENU_ID_FAN_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            test_FAN_item1,
            test_FAN_item2,
            test_FAN_item3,
        ]
    },

    {
        "menuid": MENU_ID_STRESS_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            test_strss_item1,
            test_strss_item3,
            test_strss_item4,
            test_strss_item5,
        ]
    },

    {
        "menuid": MENU_ID_DDR_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            {"name": "开始后台测试", "deal": "bmc_test_ddr_stress",},
            {"name": "终止后台测试", "deal": "bmc_test_ddr_stress_stop",},
            {"name": "查看测试结果", "deal": "bmc_test_ddr_stress_result",},
        ]
    },

    {
        "menuid": MENU_ID_EMMC_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
                {"name": "开始后台测试", "deal": "bmc_test_emmc_stress",},
                {"name": "终止后台测试", "deal": "bmc_test_emmc_stress_stop",},
                {"name": "查看测试结果", "deal": "bmc_test_emmc_stress_result",},
        ]
    },

    {
        "menuid": MENU_ID_LED_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
            test_led_item1,
            test_led_item2,
            test_led_item3,
        ]
    },

    {
        "menuid": MENU_ID_FAN_SPEED_SET_TEST, "parentid": MENU_ID_FAN_TEST, "value": [
            {"name": "设置风扇等级-高", "deal": "bmc_test_set_fan_speed_high",},
            {"name": "设置风扇等级-中", "deal": "bmc_test_set_fan_speed_middle",},
            {"name": "设置风扇等级-低", "deal": "bmc_test_set_fan_speed_low",},
        ]
    },

    #二级菜单项
    #{
    #    "menuid":MENU_ID_CPU_TEST, "parentid": MENU_ID_TEST_SINGLE, "value": [
    #         test_cpu_info_item,
    #         test_sata_info_item,
    #         test_ddr_info_item,
    #         test_peci_scan_item,
    #         test_lpc_read_cplds_item,
    #         test_front_panel_usb_item,
    #         test_usb_between_cpu_bmc_item,
    #         test_KR_packet_item,
    #         test_i2c_scan_item,
    #         test_cpu_gpio_item,
    #         test_rtc_test_item,
    #    ]
    #},

    #{
    #    "menuid": 4, "parentid": MENU_ID_TEST_SYS_CONFIG, "value": [
    #        test_e2_setmac_item,
    #        test_bmc_setmac_item,
    #        test_fru_cpueeprom_item,
    #        test_fru_bmceeprom_item,
    #        test_fru_maceeprom_item,
    #        test_fru_fanseeprom_item,
    #    ]
    #},

]

PSU_INFO = {
    "as13-32h": [
        {"bus": 14, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 15, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as13-48f8h": [
        {"bus": 14, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 15, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as23-128h": [
        {"bus": 33, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 32, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 31, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 30, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as14-128h": [
        {"bus": 33, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 32, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 31, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 30, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as14-40d": [
        {"bus": 22, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 23, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as24-128d": [
        {"bus": 30, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 31, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 32, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 33, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "ac51-48c2g": [ ],

    "droprecord_reg": {
        "bus": 0,
        "addr": 0x0d,
        "offset": 0x57,
        "bitoffset": {"PSU1": 0, "PSU2": 1, "PSU3": 2, "PSU4": 3},
    },
    "psustatus_reg":{
        "bus":0,
        "addr":0x0d,
        "device":{ 
            "PSU1":{"offset":0x40, "bitoffset":0},
            "PSU2":{"offset":0x40, "bitoffset":1},
        },
    },
}

I2C_SCAN_LIST=[
    {"name":"BASE板CPLD                  " ,"bus":0 ,"addr":0x0D},
    {"name":"CPU板CPLD                   " ,"bus":1 ,"addr":0x0D},
    {"name":"X86板E2                     " ,"bus":1 ,"addr":0x50},
    {"name":"SML1(ME)                    " ,"bus":1 ,"addr":0x16},
    {"name":"EMMC CARD                   " ,"bus":2 ,"addr":0x50},
    {"name":"Sys FRU EEPROM              " ,"bus":2 ,"addr":0x57},
    {"name":"RTC模块                     " ,"bus":3 ,"addr":0x51},
    {"name":"INA3221 Base板电压电流监控1 " ,"bus":4 ,"addr":0x40},
    {"name":"INA3221 Base板电压电流监控2 " ,"bus":4 ,"addr":0x41},
    {"name":"PORT CPLD                   " ,"bus":5 ,"addr":0x30},
    {"name":"TPM275：INLET               " ,"bus":7 ,"addr":0x48},
    {"name":"TPM275：OUTLET              " ,"bus":7 ,"addr":0x49},
    #{"name":"RTL8367S E2升级，AT24C64D   " ,"bus":13 ,"addr":0x50},
    ]

LED_INFO = {
    "sysleds": {
        "attrs": OrderedDict( [("light-off", 0x10), ("red-light-blinking", 0x10), ("red-light-on", 0x10), ("green-light-blinking", 0x15), ("green-light-on", 0x11), ("yellow-light-blinking", 0x16), ("yellow-light-on", 0x12), ("backing-off" ,0x10),] ),
        "bus": 0,
        "addr": 0X0D,
        "name": "前面板灯sys、pwr、fan灯",
        "device": [
            {"reg": 0x50},#sys灯 (Bit4 1：软件控制点灯)
            {"reg": 0x51},#pwr灯 (Bit4 1：软件控制点灯)
            {"reg": 0x52},
        ]
    },

    "location_led": {
        "attrs": OrderedDict( [("bit-stream-on", 0x00), ("green-light-blinking", 0x15), ("green-light-on", 0x11), ("yellow-light-blinking", 0x16), ("yellow-light-on", 0x12), ("backing-bit-stream-on" ,0x00),] ),
        "bus": 5,
        "addr": 0x30,
        "name": "location 灯",
        "device": [
            {"reg": 0x2f},
        ]
    }
}

FAN_SPEED = {
    "speedlevel": {
        "high": {"value": 255, "low_threshhold": 12000, "high_threshhold": 20000},
        "middle": {"value": 150, "low_threshhold": 7000, "high_threshhold": 12000},
        "low": {"value": 102, "low_threshhold": 5000, "high_threshhold": 9000},
    },
    "bus": 0,
    "addr": 0X0D,
    "watchdogreg": 0x9f,
    "watchdongenalble": 0x15,
    "waittime": 8,
    "device": [
        {"name": "风扇1", "reg": 0x90},
        {"name": "风扇2", "reg": 0x91},
    ]
}

FAN_INFO = { }

EMMC_REGISTER = [
    {"name" : "OCR", "location": r"/sys/bus/mmc/devices/mmc0\:0001/ocr"},
    {"name" : "CID", "location": r"/sys/bus/mmc/devices/mmc0\:0001/cid"},
    {"name" : "CSD", "location": r"/sys/bus/mmc/devices/mmc0\:0001/csd"},
    {"name" : "EXT_CSD", "location" : r"/sys/kernel/debug/mmc0/mmc0\:0001/ext_csd"},
]

EMMC_FIO = {
    "randrw" : [
        {"name": "randrw_4k", "rw": "randrw", "bs": "4k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
        {"name": "randrw_8k", "rw": "randrw", "bs": "8k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
        {"name": "randrw_16k", "rw": "randrw", "bs": "16k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
    ],
    "ordrw" : [
        {"name": "ordrw_4k", "rw": "rw", "bs": "4k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
        {"name": "ordrw_8k", "rw": "rw", "bs": "8k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
        {"name": "ordrw_16k", "rw": "rw", "bs": "16k", "rwmixwrite": 50, "iodepth": 32, "size": "10M", "verify" : "md5", "do_verify": 1},
    ]
}
