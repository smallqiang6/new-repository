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

RUIJIE_CARDID      = 0x000040c9
RUIJIE_PRODUCTNAME = "as24-128d-2"

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
#启机模块
STARTMODULE  = {
                "fancontrol":0,
                "avscontrol":0,
                "sfptempmodule":1,
                "sfptempmodule_interval":3,
                
                    }
                

## 驱动列表
## 
DRIVERLISTS = [
        "i2c_dev",
        "i2c_algo_bit",
        "i2c_gpio",
        "i2c_mux",
        "i2c_mux_pca9641",
        "i2c_mux_pca954x",  #  force_deselect_on_exit=1
        "fpga_i2c_ocores",
        "fpga_pcie_i2c",
        "rg_gpio_xeon",
        "at24",
        "ruijie_common",
        "rg_cpld",
        "rg_sff",
        #IPMIdriver
        "ipmi_msghandler",
        "ipmi_devintf",
        "ipmi_si",
]
FAN_PROTECT = {"list": [{"bus":8, "devno":0x0d, "addr":0x26}, {"bus":8, "devno":0x0d, "addr":0x36},
    {"bus":8, "devno":0x0d, "addr":0x46}, {"bus":8, "devno":0x0d, "addr":0x56},
    {"bus":8, "devno":0x0d, "addr":0x66}], "open":0x00, "close":0xff}

E2_DEV = {
    "E2_FAN":{"canreset":True,"list":[{"bus":90,"addr":0x50},{"bus":89,"addr":0x50},{"bus":88,"addr":0x50},{"bus":87,"addr":0x50},{"bus":86,"addr":0x50}],"restartserv":"", "chk_list": 1},
    "E2_CPU":{"canreset":True,"list":[{"bus":14,"addr":0x50}],"restartserv":"","protect":{"bus":14, "devno":0x0d, "addr":0x51, "open":0x00, "close":0xff},},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":2,"addr":0x57}],"restartserv":"",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"",},
    "E2_MAC":{"canreset":True,"list":[{"bus":22,"addr":0x51}],"restartserv":"","protect":{"bus":62, "devno":0x30, "addr":0xfc, "open":0x00, "close":0x01},},
    "E2_CLK":{"canreset":True,"list":[{"bus":102,"addr":0x50}],"restartserv":"","protect":{"bus":62, "devno":0x30, "addr":0xfc, "open":0x00, "close":0x10},},
    "E2_LC":{"canreset":True,"list":[{"bus":23,"addr":0x52}],"restartserv":"",},
    "E2_PCIE":{"canreset":True,"list":[{"bus":24,"addr":0x54}],"restartserv":"","protect":{"bus":66, "devno":0x31, "addr":0xfd, "open":0x00, "close":0xff},"opt": 1},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":92,"addr":0x56}],"restartserv":"","protect":{"bus":8, "devno":0x0d, "addr":0xf0, "open":0x00, "close":0xff}},
}

ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-14/14-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'mac': {'loc': '/sys/bus/i2c/devices/i2c-22/22-0051/eeprom', 'way': 'sysfs'},
              'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-92/92-0056/eeprom', 'way': 'sysfs'},
             }

DCDC_DEVICE = [
    {
        "name": "RTC_3.3_V",
        "Min": 2000,
        "Max": 3465,
        "format": "float(float(%s)/1000)",
        "Value": {
            "loc": "/sys/bus/i2c/devices/i2c-0/0-000d/hwmon/hwmon*/in1_input",
            "way": "sysfs"
        },
        "Unit": "V",
        "cpld": {
            "bus":0,
            "devno":0x0d,
            "addr":0xec
        }
    },
 ]

CPLD_TEST = [
    {"name":"CPU CPLD", "bus": 14, "addr": 0x0D, "test_reg": 0x05, "slot": 0},
    {"name":"BASE CPLD", "bus": 0, "addr": 0x0D ,"test_reg": 0xf7, "slot": 1},
    {"name":"FAN CPLD", "bus": 8, "addr": 0x0D, "test_reg": 0xf1, "slot": 2},
    {"name":"LC CPLD", "bus": 65, "addr": 0x31, "test_reg": 0x0f, "slot": 3},
    {"name":"MAC CPLD2", "bus": 64,"addr": 0x31, "test_reg": 0x0f, "slot": 5},
    {"name":"MAC CPLD1", "bus": 63,"addr": 0x31, "test_reg": 0x0f, "slot": 6},
    {"name":"MAC MISC CPLD", "bus": 62, "addr": 0x30, "test_reg": 0x0f, "slot": 7},
]

FPGA_TEST = [
    {"name":"FPGA", "bus": 5 ,"addr":0x32,"test_reg":0x74, "protect":{"bus": 5, "devno": 0x32, "addr": 0x70, "open": 0xbc, "close": 0x00}},
]

# add: 0不需要挂载， 1需要挂载；chip: 存在主备
SPI_TEST = [
    {"name": "bmc", "chip": "master", "cmd": "cat /sys/bus/spi/devices/spi0.0/jedec_id", "add": 0},
    {"name": "bmc", "chip": "slave", "cmd": "cat /sys/bus/spi/devices/spi0.1/jedec_id", "add": 0},
    {"name": "bios", "chip": "master", "cmd": "cat /sys/bus/spi/devices/spi1.0/jedec_id", "add": 1},
    {"name": "bios", "chip": "slave", "cmd": "cat sys/bus/spi/devices/spi1.0/jedec_id", "add": 1},
    {"name": "fpga", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "mac", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "bcm53134", "cmd": "dumplog=$(hexdump /sys/bus/spi/devices/spi2.0/eeprom -n1);val=$?;echo $dumplog | awk 'NR==1{print $2}';exit $val", "add": 1},
]

CLOCK_TEST = {
    "bus": 102,
    "addr": 0x09,
    "page": [
        {
            "name": "page0",
            "switch": {"offset": 0xfd, "val": 0x00, "rval": 0x00},
            "reg_list": [
                {"name": "VENDOR_ID", "offset": [{"order": 0, "offset": 0x00}, {"order": 1, "offset": 0x01}], "chk": 0x1033, "mask": 0xffff}
            ],
        },
        {
            "name": "page2",
            "switch":{"offset": 0xfd, "val": 0x02, "rval": 0x00},
            "reg_list": [
                {"name": "APLL_EVENT", "offset": [{"order": 0, "offset": 0x6e}], "chk": 0x00, "mask": 0x03},
                {"name": "APLL_LOL_EVENT", "offset": [{"order": 0, "offset": 0x6f}], "chk": 0x00, "mask": 0x0f},
                {"name": "APLL_STS", "offset": [{"order": 0, "offset": 0x71}], "chk": 0x01, "mask": 0x01},
            ],
        },
    ],
}

ALI_BMC = {
    "FRU_NUM": 16,
    "NO_FRU_NUM": 6,
    "PCIE_CHK_STR": "40 65 06 05 00",
    "MAC_CORE_V": "MAC_CORE_V",
    "SML": [
        {"name": "SML0", "bus": 14, "addr": 0x16, "offset": 0x00},
        {"name": "SML1", "bus": 14, "addr": 0x4b, "offset": 0x00, "special": 1},
    ],
    "CPU_CHK_MOC": 1.74,
    "CPU_CHK_LIST": ["CPU_VCCIN_V"],
    "MIDO_REG_READ_TIMES": 80,
    "I2C_REG_READ_TIMES": 10,
    "SPI_ID_READ_TIMES": 1000,
    "DDR_STRESS": {"memtester_preset":"export MEMTESTER_TEST_MASK=$((1<<17));export MEMTESTER_TEST_RJ_MASK=$((1<<9));"},
    "TEST_CPU_GPIO_BY_SLOT": True,
}

MAC_THRESHOLD = {
    # The conversion value of the CPLD register value of MAC voltage
    # corresponds one-to-one with the range of voltage regulation difference
    "type": "non-fixed",
    #"map":{value1:[min1,max1],...,valuen:[minn,maxn]}
    "map":{0.900:[-0.002, 0.100], 0.878:[0, 0.112], 0.854:[0, 0.102], 0.830:[0, 0.102], 0.805:[0, 0.102]}
}

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
        {"bus": 31, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 33, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 30, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
        {"bus": 32, "addr": 0x58, "e2addr": 0x50, "attrs": {"curr1_input": "mA", "curr2_input": "mA", "in1_input": "mV", "in2_input": "mV", "power1_input": "mW", "power2_input": "mW"} },
    ],

    "as25-128q":[
        {"bus":70,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":71,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":72,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":73,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
    ],

    "as24-128d-2":[
        {"bus":70,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":71,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":72,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":73,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
    ],

    "droprecord_reg": {
        "bus": 0,
        "addr": 0x0d,
        "offset":0x49,
        "bitoffset": {"PSU1": 0, "PSU2": 1, "PSU3": 2, "PSU4": 3},
    },
    "psustatus_reg":{
        "bus":0,
        "addr":0x0d,
        "device":{ 
            "PSU1":{"offset":0x40, "bitoffset":0},
            "PSU2":{"offset":0x40, "bitoffset":1},
            "PSU3":{"offset":0x40, "bitoffset":2},
            "PSU4":{"offset":0x40, "bitoffset":3},
        },
    },
}

I2C_SCAN_LIST=[
    {"name":"BASE CPLD(0-000D)                          " ,"bus":0 ,"addr":0x0D},
    {"name":"BASE板CPLD升级通路(0-0040)                  " ,"bus":0 ,"addr":0x40},
    {"name":"CPU板CPLD(14-000d)                         " ,"bus":14 ,"addr":0x0d},
    ###{"name":"CPU板CPLD升级通道(14-0040)                 " ,"bus":14 ,"addr":0x40},
    {"name":"CPU板 E2PROM(14-0050)                      " ,"bus":14 ,"addr":0x50},
    {"name":"SML0(14-0016)                              " ,"bus":14 ,"addr":0x16},
    {"name":"SML1(14-004b)                              " ,"bus":14 ,"addr":0x4b, "special": 1},
    {"name":"CPU板 电压电流监控(INA3221)(15-0043)        " ,"bus":15 ,"addr":0x43},
    {"name":"CPU板 VCCIN/P1V05(15-0067)                 " ,"bus":15 ,"addr":0x67},
    {"name":"CPU板 VCCSCSUS/VCCD(15-006c)               " ,"bus":15 ,"addr":0x6c},
    {"name":"BMC板 EEPROM(2-0053)                       " ,"bus":2 ,"addr":0x53},
    {"name":"BASE板 EEPROM(2-0057)                      " ,"bus":2 ,"addr":0x57},
    {"name":"MAC板 EEPROM(22-0051)                      " ,"bus":22 ,"addr":0x51},
    {"name":"LC板 EEPROM(23-0052)                       " ,"bus":23 ,"addr":0x52},
    {"name":"BASE板 RTC通道(3-0051)                     " ,"bus":3 ,"addr":0x51},
    {"name":"BASE板 电压电流监控1(INA3221)(30-0041)     " ,"bus":30 ,"addr":0x41},
    {"name":"BASE板 电压电流监控2(INA3221)(31-0041)     " ,"bus":31 ,"addr":0x41},
    {"name":"BASE板 电压电流监控3(INA3221)(32-0041)     " ,"bus":32 ,"addr":0x41},
    {"name":"BASE板 电压电流监控4(INA3221)(33-0041)     " ,"bus":33 ,"addr":0x41},
    {"name":"XDPE132G5D(38-0010)                        " ,"bus":38 ,"addr":0x10},
    {"name":"XDPE12284C(39-0058)                        " ,"bus":39 ,"addr":0x58},
    {"name":"XDPE12284C(40-0058)                        " ,"bus":40 ,"addr":0x58},
    {"name":"XDPE12284C(41-0058)                        " ,"bus":41 ,"addr":0x58},
    {"name":"LC板 电压电流监控0（INA3221)(46-0040)      " ,"bus":46 ,"addr":0x40},
    {"name":"LC板 电压电流监控1（INA3221)(47-0040)      " ,"bus":47 ,"addr":0x40},
    {"name":"XDPE12284C(48-0058)                        " ,"bus":48 ,"addr":0x58},
    {"name":"MAC板 电压电流监控0（INA3221)(54-0040)     " ,"bus":54 ,"addr":0x40},
    {"name":"MAC板 电压电流监控1（INA3221)(55-0040)     " ,"bus":55 ,"addr":0x40},
    {"name":"MAC板 电压电流监控2（INA3221)(56-0040)     " ,"bus":56 ,"addr":0x40},
    {"name":"MAC板 电压电流监控3（INA3221)(57-0040)     " ,"bus":57 ,"addr":0x40},
    {"name":"BMC访问FPGA通道(5-0032)                    " ,"bus":5 ,"addr":0x32},
    {"name":"MAC板MISC CPLD(62-0030)                    " ,"bus":62 ,"addr":0x30},
    {"name":"MAC板CPLD升级通道(62-0040)                 " ,"bus":62 ,"addr":0x40},
    {"name":"MAC板CPLD1(63-0031)                        " ,"bus":63 ,"addr":0x31},
    {"name":"MAC板CPLD1升级通路(63-0040)                " ,"bus":63 ,"addr":0x40},
    {"name":"MAC板CPLD2(64-0031)                        " ,"bus":64 ,"addr":0x31},
    {"name":"MAC板CPLD2升级通路(64-0040)                " ,"bus":64 ,"addr":0x40},
    {"name":"LC板CPLD(65-0031)                          " ,"bus":65 ,"addr":0x31},
    {"name":"LC板CPLD升级通路(65-0040)                  " ,"bus":65 ,"addr":0x40},
    {"name":"PSU1_PMBUS(70-0058)                        " ,"bus":70 ,"addr":0x58},
    {"name":"PSU2_PMBUS(71-0058)                        " ,"bus":71 ,"addr":0x58},
    {"name":"PSU3_PMBUS(72-0058)                        " ,"bus":72 ,"addr":0x58},
    {"name":"PSU4_PMBUS(73-0058)                        " ,"bus":73 ,"addr":0x58},
    {"name":"TMP275(74-0048)                            " ,"bus":74 ,"addr":0x48},
    {"name":"TH4 BSC2通道(7-0044)                        " ,"bus":7 ,"addr":0x44},
    {"name":"LC板TMP275(78-0048)                        " ,"bus":78 ,"addr":0x48},
    {"name":"FCB板 CPLD(8-000d)                         " ,"bus":8 ,"addr":0x0d},
    # 1, 表示：风冷设备独有，非风冷设备需要屏蔽
    {"name":"风扇模组_1 E2PROM(90-0050)                 " ,"bus":90 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"风扇模组_2 E2PROM(89-0050)                 " ,"bus":89 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"风扇模组_3 E2PROM(88-0050)                 " ,"bus":88 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"风扇模组_4 E2PROM(87-0050)                 " ,"bus":87 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"风扇模组_5 E2PROM(86-0050)                 " ,"bus":86 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"FCB板 E2PROM(92-0056)                      " ,"bus":92 ,"addr":0x56},
    {"name":"FCB板 TMP275(93-0048)                      " ,"bus":93 ,"addr":0x48},
    {"name":"FCB板 TMP275(93-0049)                      " ,"bus":93 ,"addr":0x49},
    {"name":"MAC板 CLOCK(102-0009)                      " ,"bus":102 ,"addr":0x09},
    {"name":"MAC板 CLOCK E2PROM(102-0050)               " ,"bus":102 ,"addr":0x50},
]

POWER_FW_VER = [
    # {"name": xxx, "bus": xxx, "addr": xxx, "offset": xxx, "page": {"bus": xxx, "addr": xxx, "offset": xxx, "val": xxx}},
    # The default value is provided by I2C_SCAN_LIST. 
    # Paging switching information does not necessarily require.
    {"name": "XDPE12284C", "offset": 0x3f, "page": {"offset":0x00, "val": 0x22, "rval": 0x00}},
    {"name": "XDPE132G5D", "offset": 0x7a},
]

ECC_ERR_INFO = {
    "reg_info": {"addr": 0x1e6e0050, "way": "devmem", "digit":32},
    "check_list": [
        {"name": "ECC recoverable error counter", "offset": 16, "mask": 0xff, "chk": 0},
        {"name": "ECC un-recoverable error counter", "offset": 12, "mask": 0xf, "chk": 0},
    ]
}

LED_INFO ={
    "sysleds":{
        "attrs":OrderedDict([("light-off",0x10),("red-light-blinking",0x11),("red-light-on",0x12),("green-light-blinking",0x13),("green-light-on",0x14),("yellow-light-blinking",0x15),("yellow-light-on",0x16),("backing-off",0x10),]),
        "bus":0,
        "addr":0X0D,
        "name":"前面板灯sys、pwr、fan灯",
        "device":[
            {"reg":0x50},
            {"reg":0x51},
            {"reg":0x08, "bus":8, "addr":0X0D}, #风冷 sysfan灯 (Bit4 1：软件控制点灯)
        ]
    },
    "fanleds":{
        "attrs":OrderedDict([("light-off",0X0B),("red-light-blinking",0x0E),("red-light-on",0x0A),("green-light-blinking",0x0D),("green-light-on",0x09),("yellow-light-blinking",0x07),("yellow-light-on",0x03),("backing-off",0X0B)]),
        "bus":8,
        "addr":0X0D,
        "name":"风扇灯",
        "device":[
            {"reg":0x25},
            {"reg":0x35},
            {"reg":0x45},
            {"reg":0x55},
            {"reg":0x65},
        ]
    },
    "location_led":{
        "attrs":OrderedDict([("bit-stream-on",0X98),("green-light-blinking",0x83),("green-light-on",0x84),("yellow-light-blinking",0x85),("yellow-light-on",0x86),("backing-bit-stream-on",0X98)]),
        "bus":5,
        "addr":0x32,
        "name":"location 灯",
        "device":[
            {"reg":0x40},
            {"reg":0x44},
            {"reg":0x48},
            {"reg":0x4c},
        ]
    }
}

FAN_SPEED = {
    "speedlevel": {
        "high": {"value": 255, "low_threshhold": 12000, "high_threshhold": 20000},
        "middle": {"value": 150, "low_threshhold": 7000, "high_threshhold": 12000},
        "low": {"value": 102, "low_threshhold": 5000, "high_threshhold": 9000},
    },
    "bus": 8,
    "addr": 0X0D,
    "watchdogreg":0x0C,
    "waittime": 8,
    "device": [
        {"name":"风扇1", "reg":0x24},
        {"name":"风扇2", "reg":0x34},
        {"name":"风扇3", "reg":0x44},
        {"name":"风扇4", "reg":0x54},
        {"name":"风扇5", "reg":0x64},

    ],
}

FAN_INFO = {
        "droprecord_reg":{
            "bus":8,
            "addr":0x0D,
            "num_of_offset": "multiple",
            "offset":{"FAN1": 0x28, "FAN2": 0x38, "FAN3": 0x48, "FAN4": 0x58, "FAN5": 0x68},
            "bitoffset": {"FAN1": 0, "FAN2": 0, "FAN3": 0, "FAN4": 0, "FAN5": 0, "FAN6": 0},
        },
        "present":{
            "num_of_offset": "multiple",
            "path": {
                    "FAN1": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan1_present",
                    "FAN2": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan2_present",
                    "FAN3": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan3_present",
                    "FAN4": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan4_present",
                    "FAN5": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan5_present",
            },
            "bitoffset": {"FAN1": 0, "FAN2": 0, "FAN3": 0, "FAN4": 0, "FAN5": 0, "FAN6": 0},
        },
}


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
