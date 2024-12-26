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

RUIJIE_CARDID      = 0x00004064
RUIJIE_PRODUCTNAME = "as24-128d"

MENU_ID_ROOT             = 0
MENU_ID_TEST_SINGLE      = 11
MENU_ID_DDR_TEST         = 12
MENU_ID_EMMC_TEST        = 13
MENU_ID_BMC_DRIVER_TEST  = 14
MENU_ID_PSU_TEST         = 15
MENU_ID_FAN_TEST         = 16
MENU_ID_STRESS_TEST      = 18
MENU_ID_LED_TEST         = 19
MENU_ID_FAN_SPEED_SET_TEST = 20

FAN_PROTECT = {"bus": 8, "devno": 0x0d, "addr": 0x1A, "open": 0x00, "close": 0xff}
E2_DEV = {
    "E2_FAN": {"canreset": True, "list": [ {"bus": 50, "addr": 0x50}, {"bus": 49, "addr":0x50}, {"bus": 48, "addr": 0x50}, {"bus": 47, "addr": 0x50}, {"bus": 46, "addr": 0x50}], "restartserv": "",},
    "E2_PSU": {"canreset": True, "list": [ {"bus": 31, "addr": 0x50}, {"bus": 33, "addr": 0x50}, {"bus": 30, "addr": 0x50}, {"bus": 32, "addr": 0x50}], "restartserv": "",},
    "E2_CPU": {"canreset": True, "list": [ {"bus": 1, "addr": 0x50}], "restartserv": "",},
    "E2_SYSFRU": {"canreset": True, "list": [ {"bus": 2, "addr": 0x57}], "restartserv": "",},
    "E2_BMC": {"canreset": True, "list": [ {"bus": 2, "addr": 0x53}], "restartserv": "",},
    "E2_MAC": {"canreset": True, "list": [ {"bus": 2, "addr": 0x51}], "restartserv": "",},
    "E2_40CCQ": {"canreset": True, "list": [ {"bus": 2, "addr": 0x52}], "restartserv": "",},
    "E2_44CCQ": {"canreset": True, "list": [ {"bus": 2, "addr": 0x54}], "restartserv": "",},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":8,"addr":0x56}],"restartserv":"","protect":{"bus":8, "devno":0x0d, "addr":0x47, "open":0x00, "close":0xff},},
}

ALI_E2_DEV = {
    'cpu': {'loc': '/sys/bus/i2c/devices/i2c-1/1-0050/eeprom', 'way': 'sysfs'},
    'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
    'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
    'mac': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0051/eeprom', 'way': 'sysfs'},
    'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-8/8-0056/eeprom', 'way': 'sysfs'},
    '40ccq': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0052/eeprom', 'way': 'sysfs'},
    '44ccq': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0054/eeprom', 'way': 'sysfs'},
}

DCDC_DEVICE = [
    {"name": "BASE_CPLD3.3_V", "file": "in1_input"},
    {"name": "B5387_V1.2_V", "file": "in2_input"},
    {"name": "BASE_SSD3.3_V", "file": "in3_input"},
    {"name": "BASE_CPLD3.3_C", "file": "curr1_input"},
    {"name": "B5387_V1.2_C", "file": "curr2_input"},
    {"name": "BASE_SSD3.3_C", "file": "curr3_input"},
    {"name": "FPGA_V1.8_V", "file": "in1_input"},
    {"name": "B5387_V2.5_V", "file": "in2_input"},
    {"name": "FPGV_V1.0_V", "file": "in3_input"},
    {"name": "FPGA_V1.8_C", "file": "curr1_input"},
    {"name": "B5387_V2.5_C", "file": "curr2_input"},
    {"name": "FPGV_V1.0_C", "file": "curr3_input"},
    {"name": "FPGA_V3.3_C", "file": "curr1_input"},
    {"name": "I210_V3.3_C", "file": "curr2_input"},
    {"name": "FPGA_V1.2_C", "file": "curr3_input"},
    {"name": "FPGA_V3.3_V", "file": "in1_input"},
    {"name": "I210_V3.3_V", "file": "in2_input"},
    {"name": "FPGA_V1.2_V", "file": "in3_input"},
    {"name": "RTC_V3.3_V", "file": "in3_input"},
    #{"name": "MAC_CORE_V", "file": ""},
    #{"name": "MAC_ANALOG_V", "file": ""},
    #{"name": "MAC_CORE_C", "file": ""},
    #{"name": "MAC_ANALOG_C", "file": ""},
    {"name": "SWITCH_QSFP0_V3.3_V", "file": "in1_input"},
    {"name": "SWITCH_QSFP1_V3.3_V", "file": "in2_input"},
    {"name": "SWITCH_V5.0_V", "file": "in3_input"},
    {"name": "SWITCH_QSFP0_V3.3_C", "file": "curr1_input"},
    {"name": "SWITCH_QSFP1_V3.3_C", "file": "curr2_input"},
    {"name": "SWITCH_V5.0_C", "file": "curr3_input"},
    {"name": "SWITCH_QSFP3_V3.3_V", "file": "in1_input"},
    {"name": "SWITCH_QSFP2_V3.3_V", "file": "in2_input"},
    {"name": "MAC_AVDD1.2_V", "file": "in3_input"},
    {"name": "SWITCH_QSFP3_V3.3_C", "file": "curr1_input"},
    {"name": "SWITCH_QSFP2_V3.3_C", "file": "curr2_input"},
    {"name": "MAC_AVDD1.2_C", "file": "curr3_input"},
    {"name": "SWITCH_V3.3_V", "file": "in1_input"},
    {"name": "MAC_DVDD1.8_V", "file": "in2_input"},
    {"name": "SWITCH_CPLD3.3_V", "file": "in3_input"},
    {"name": "SWITCH_V3.3_C", "file": "curr1_input"},
    {"name": "MAC_V1.8_C", "file": "curr2_input"},
    {"name": "SWITCH_CPLD3.3_C", "file": "curr3_input"},
    {"name": "MAC_AVDD1.8_V", "file": "in1_input"},
    {"name": "MAC_DVDD1.2_V", "file": "in2_input"},
    {"name": "SWITCH_CLK3.3_V", "file": "in3_input"},
    {"name": "MAC_AVDD1.8_C", "file": "curr1_input"},
    {"name": "MAC_DVDD1.2_C", "file": "curr2_input"},
    {"name": "SWITCH_CLK3.3_C", "file": "curr3_input"},
    {"name": "44CCQ_QSFP0_V3.3_V", "file": "in1_input"},
    {"name": "44CCQ_QSFP1_V3.3_V", "file": "in2_input"},
    {"name": "44CCQ_V3.3_V", "file": "in3_input"},
    {"name": "44CCQ_QSFP0_V3.3_C", "file": "curr1_input"},
    {"name": "44CCQ_QSFP1_V3.3_C", "file": "curr2_input"},
    {"name": "44CCQ_V3.3_C", "file": "curr3_input"},
    {"name": "44CCQ_QSFP3_V3.3_V", "file": "in1_input"},
    {"name": "44CCQ_CPLD_V3.3_V", "file": "in2_input"},
    {"name": "44CCQ_QSFP2_V3.3_V", "file": "in3_input"},
    {"name": "44CCQ_QSFP3_V3.3_C", "file": "curr1_input"},
    {"name": "44CCQ_CPLD_V3.3_C", "file": "curr2_input"},
    {"name": "44CCQ_QSFP2_V3.3_C", "file": "curr3_input"},
    {"name": "40CCQ_CPLD_V3.3_V", "file": "in1_input"},
    {"name": "40CCQ_QSFP2_V3.3_V", "file": "in2_input"},
    {"name": "40CCQ_QSFP1_V3.3_V", "file": "in3_input"},
    {"name": "40CCQ_CPLD_V3.3_C", "file": "curr1_input"},
    {"name": "40CCQ_QSFP2_V3.3_C", "file": "curr2_input"},
    {"name": "40CCQ_QSFP1_V3.3_C", "file": "curr3_input"},
    {"name": "40CCQ_V3.3_V", "file": "in1_input"},
    {"name": "40CCQ_QSFP0_V3.3_V", "file": "in2_input"},
    {"name": "40CCQ_V5.0_V", "file": "in3_input"},
    {"name": "40CCQ_V3.3_C", "file": "curr1_input"},
    {"name": "40CCQ_QSFP0_V3.3_C", "file": "curr2_input"},
    {"name": "40CCQ_V5.0_C", "file": "curr3_input"},
    {"name": "40CCQ_QSFP3_V3.3_V", "file": "in1_input"},
    {"name": "40CCQ_PHY_V1.2_V", "file": "in2_input"},
    {"name": "40CCQ_QSFP3_V3.3_C", "file": "curr1_input"},
    {"name": "40CCQ_PHY_V1.2_C", "file": "curr2_input"},
    {"name": "P5V_AUX_C", "file": "curr1_input"},
    {"name": "P3V3_STBY_C", "file": "curr2_input"},
    {"name": "P1V7_VCCSCFUSESUS_C", "file": "curr3_input"},
    {"name": "P5V_AUX_V", "file": "in1_input"},
    {"name": "P3V3_STBY_V", "file": "in2_input"},
    {"name": "P1V7_VCCSCFUSESUS_V", "file": "in3_input"},
    {"name": "P1V05_C", "file": "curr1_input"},
    {"name": "VCCIN_C", "file": "curr2_input"},
    {"name": "P1V05_V", "file": "in1_input"},
    {"name": "VCCIN_V", "file": "in2_input"},
    {"name": "VCCD_C", "file": "curr1_input"},
    {"name": "VCCSCSUS_C", "file": "curr2_input"},
    {"name": "VCCD_V", "file": "in1_input"},
    {"name": "VCCSCSUS_V", "file": "in2_input"},
    {"name": "TEST1V24_V", "file": "in5_input"},
    {"name": "P2V5_VPP_V", "file": "in6_input"},
    {"name": "P0V6_VTT_V", "file": "in7_input"},
    {"name": "P1V3_VCCKRHV_V"," file": "in8_input"},
    {"name": "P1V5_VRM_V", "file": "in9_input"},
    {"name": "SWITCH_TMP411_TEMP", "file": "temp2_input"},
    {"name": "SWITCH_HOTSPOT_TEMP", "file": "temp2_input"},
    {"name": "INLET_T_TEMP", "file": "temp1_input"},
    {"name": "INLET_B_TEMP", "file": "temp1_input"},
    {"name": "OUTLET_2_TEMP", "file": "temp1_input"},
    {"name": "OUTLET_1_TEMP", "file": "temp1_input"},
    {"name": "SWITCH_TEMP", "file": "temp99_input"},
    {"name": "PSU_TEMP", "file": "temp1_input"},
    {"name": "PSU_FAN", "file": "fan5_input"},
    {"name": "PSU_Input_C1", "file": "curr2_input"},
    {"name": "PSU_Input_C2", "file": "curr2_input"},
    {"name": "PSU_Input_V1", "file": "in2_input"},
    {"name": "PSU_Input_V2", "file": "in2_input"},
    {"name": "PSU_Input_P", "file": "power2_input"},
    {"name": "PSU_Output_C", "file": "curr1_input"},
    {"name": "PSU_Output_V", "file": "in1_input"},
    {"name": "PSU_Output_P", "file": "power1_input"},
    {"name": "FAN1_1", "file": "fan11_input"},
    {"name": "FAN1_2", "file": "fan12_input"},
    {"name": "FAN2_1", "file": "fan21_input"},
    {"name": "FAN2_2", "file": "fan22_input"},
    {"name": "FAN3_1", "file": "fan31_input"},
    {"name": "FAN3_2", "file": "fan32_input"},
    {"name": "FAN4_1", "file": "fan41_input"},
    {"name": "FAN4_2", "file": "fan42_input"},
    {"name": "FAN5_1", "file": "fan51_input"},
    {"name": "FAN5_2", "file": "fan52_input"},
]

CPLD_TEST = [
    {"name": "CPU底板CPLD", "bus": 0, "addr": 0x0D, "test_reg": 0xaa},
    {"name": "风扇板CPLD", "bus": 8, "addr": 0x0D, "test_reg": 0xaa},
]

FPGA_TEST = [
    {"name": "FPGA", "bus": 5, "addr": 0x70, "test_reg": 0x8},
]

ALI_BMC = {"FRU_NUM": 18, "NO_FRU_NUM": 5, "PCIE_CHK_STR": "40 65 06 05 00", "CPU_CHK_MOC": 1.74, "MAC_CORE_V": "MAC_CORE_V"}

MAC_THRESHOLD = {"Min": -0.01, "Max": 0.01}

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
            "PSU1":{"offset":0x51, "bitoffset":1},
            "PSU2":{"offset":0x51, "bitoffset":5},
            "PSU3":{"offset":0x52, "bitoffset":1},
            "PSU4":{"offset":0x52, "bitoffset":5},
        },
    },
}

I2C_SCAN_LIST = [
    {"name": "BASE板CPLD1                  ", "bus": 0, "addr": 0x0D},
    {"name": "CPU板CPLD                    ", "bus": 1, "addr": 0x0D},
    {"name": "X86板E2                      ", "bus": 1, "addr": 0x50},
    {"name": "SML1(ME)                     ", "bus": 1, "addr": 0x16},
    {"name": "MAC板 E2PROM                 ", "bus": 2, "addr": 0x51},
    {"name": "40CCQ线卡 E2PROM             ", "bus": 2, "addr": 0x52},
    {"name": "BMC板 E2PROM                 ", "bus": 2, "addr": 0x53},
    {"name": "44CCQ线卡 E2PROM             ", "bus": 2, "addr": 0x54},
    {"name": "BASE板 E2PROM                ", "bus": 2, "addr": 0x57},
    {"name": "X86板 电源芯片1               ", "bus": 4, "addr": 0x67},
    {"name": "X86板 电源芯片2               ", "bus": 4, "addr": 0x6C},
    {"name": "X86板 电压电流监控            ", "bus": 4, "addr": 0x43},
    {"name": "BASE板 电压电流监控1         ", "bus": 54, "addr": 0x41},
    {"name": "BASE板 电压电流监控2         ", "bus": 55, "addr": 0x41},
    {"name": "BASE板 电压电流监控3         ", "bus": 56, "addr": 0x41},
    {"name": "40CCQ线卡 电压电流监控1      ", "bus": 22, "addr": 0x40},
    {"name": "40CCQ线卡 电压电流监控2      ", "bus": 23, "addr": 0x40},
    {"name": "40CCQ线卡 电压电流监控3      ", "bus": 24, "addr": 0x40},
    {"name": "MAC板CORE XDPE132G5C        ", "bus": 14, "addr": 0x10},
    {"name": "MAC板ANLOG XDPE132G5C       ", "bus": 15, "addr": 0x10},
    {"name": "MAC板 电压电流监控1          ", "bus": 16, "addr": 0x40},
    {"name": "MAC板 电压电流监控2          ", "bus": 17, "addr": 0x40},
    {"name": "MAC板 电压电流监控3          ", "bus": 18, "addr": 0x40},
    {"name": "MAC板 电压电流监控4          ", "bus": 19, "addr": 0x40},
    {"name": "44CCQ线卡 电压电流监控1      ", "bus": 20, "addr": 0x40},
    {"name": "44CCQ线卡 电压电流监控2      ", "bus": 21, "addr": 0x40},
    {"name": "BMC访问FPGA通道              ", "bus": 5, "addr": 0x70},
    {"name": "BASE板RTC通道                ", "bus": 6, "addr": 0x51},
    {"name": "PSU1 PMBUS                  ", "bus": 31, "addr": 0x58},
    {"name": "PSU2 PMBUS                  ", "bus": 33, "addr": 0x58},
    {"name": "PSU3 PMBUS                  ", "bus": 30, "addr": 0x58},
    {"name": "PSU4 PMBUS                  ", "bus": 32, "addr": 0x58},
    {"name": "PDB板 TMP275                ", "bus": 34, "addr": 0x48},
    {"name": "TH4 BSC2通道                 ", "bus": 7, "addr": 0x44},
    {"name": "线卡40CCQ TMP275            ", "bus": 38, "addr": 0x48},
    {"name": "TMP411 TH3节温#1            ", "bus": 39, "addr": 0x4C},
    {"name": "TMP411 TH3节温#2            ", "bus": 40, "addr": 0x4C},
    {"name": "FCB板 CPLD                   ", "bus": 8, "addr": 0x0D},
    {"name": "FCB板 EE2PROM                ", "bus": 8, "addr": 0x56},
    {"name": "风扇模块E2PROM1              ", "bus": 50, "addr": 0x50},
    {"name": "风扇模块E2PROM2              ", "bus": 49, "addr": 0x50},
    {"name": "风扇模块E2PROM3              ", "bus": 48, "addr": 0x50},
    {"name": "风扇模块E2PROM4              ", "bus": 47, "addr": 0x50},
    {"name": "风扇模块E2PROM5              ", "bus": 46, "addr": 0x50},
    {"name": "88e6321配置E2PROM            ", "bus": 61, "addr": 0x50,"scan_shielde_capacity":6321},
]

LED_INFO = {
    "sysleds": {
        "attrs": OrderedDict( [("light-off", 0x10), ("red-light-blinking", 0x11), ("red-light-on", 0x12), ("green-light-blinking", 0x13), ("green-light-on", 0x14), ("yellow-light-blinking", 0x15), ("yellow-light-on", 0x16), ("backing-off" ,0x10),] ),
        "bus": 0,
        "addr": 0X0D,
        "name": "前面板灯sys、pwr、fan灯",
        "device": [
            {"reg": 0x72},
            {"reg": 0x73},
            {"reg": 0x40, "bus": 8, "addr": 0X0D}, #sysfan灯 (Bit4 1：软件控制点灯)
        ]
    },

    "fanleds": {
        "attrs": OrderedDict( [("light-off", 0X0B), ("red-light-blinking", 0x0E), ("red-light-on", 0x0A), ("green-light-blinking", 0x0D), ("green-light-on", 0x09), ("yellow-light-blinking", 0x07), ("yellow-light-on", 0x03), ("backing-off", 0X0B),] ),
        "bus": 8,
        "addr": 0X0D,
        "name": "风扇灯",
        "device": [
            {"reg": 0x39},
            {"reg": 0x3a},
            {"reg": 0x3b},
            {"reg": 0x3c},
            {"reg": 0x3d},
        ]
    },

    "location_led": {
        "attrs": OrderedDict( [("bit-stream-on", 0X98), ("green-light-blinking", 0x83), ("green-light-on", 0x84), ("yellow-light-blinking", 0x85), ("yellow-light-on", 0x86), ("backing-bit-stream-on" ,0X98),] ),
        "bus": 5,
        "addr": 0X70,
        "name": "location 灯",
        "device": [
            {"reg": 0x10},
            {"reg": 0x14},
            {"reg": 0x18},
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
    "waittime": 8,
    "device": [
        {"name": "风扇1", "reg": 0x14},
        {"name": "风扇2", "reg": 0x15},
        {"name": "风扇3", "reg": 0x16},
        {"name": "风扇4", "reg": 0x17},
        {"name": "风扇5", "reg": 0x18},
    ],
}

FAN_INFO = {
    "droprecord_reg": {
        "bus": 8,
        "addr": 0x0D,
        "offset": 0x57,
        "bitoffset": {"FAN1": 0, "FAN2": 1, "FAN3": 2, "FAN4": 3, "FAN5": 4},
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
