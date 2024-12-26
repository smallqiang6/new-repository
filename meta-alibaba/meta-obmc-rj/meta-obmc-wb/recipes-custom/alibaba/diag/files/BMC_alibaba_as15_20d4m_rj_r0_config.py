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

RUIJIE_CARDID      = 0x0000405d
RUIJIE_PRODUCTNAME = "as15-20d4m"

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
FAN_PROTECT = {"bus":16, "devno":0x3d, "addr":0x30, "open":0x00, "close":0xff}

E2_DEV = {
    "E2_FAN":{"canreset":True,"list":[{"bus":26,"addr":0x50},{"bus":27,"addr":0x50},{"bus":28,"addr":0x50},{"bus":29,"addr":0x50},{"bus":30,"addr":0x50},{"bus":31,"addr":0x50}],"restartserv":"",},
    "E2_PSU":{"canreset":True,"list":[{"bus":37,"addr":0x50},{"bus":38,"addr":0x50}],"restartserv":"",},
    "E2_CPU":{"canreset":True,"list":[{"bus":6,"addr":0x50}],"restartserv":"",},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":18,"addr":0x57}],"restartserv":"",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"",},
    "E2_MAC":{"canreset":True,"list":[{"bus":34,"addr":0x57}],"restartserv":"",},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":33,"addr":0x56}],"restartserv":"","protect":{"bus":16, "devno":0x3d, "addr":0x30, "open":0x00, "close":0xff},},
}

ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-6/6-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-18/18-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'mac': {'loc': '/sys/bus/i2c/devices/i2c-34/34-0057/eeprom', 'way': 'sysfs'},
              'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-33/33-0056/eeprom', 'way': 'sysfs'},
             }

DCDC_DEVICE = [ ]

CPLD_TEST = [
    {"name": "MAC板CPLDA"  ,"bus": 14 ,"addr": 0x1D,"test_reg": 0xaa},
    {"name": "MAC板CPLDB"  ,"bus": 14 ,"addr": 0x2D,"test_reg": 0xaa},
    {"name": "风扇板CPLD"  ,"bus": 16 ,"addr": 0x3D,"test_reg": 0xaa},
    {"name": "CPU扣板CPLD" ,"bus": 6 ,"addr": 0x0D,"test_reg": 0x05},
    {"name": "BASE板CPLD"  ,"bus": 6 ,"addr": 0x3D,"test_reg": 0x55},
]

FPGA_TEST = [
    {"name":"FPGA"  ,"bus":	1 ,"addr":0x70,"test_reg":0x8},
]

ALI_BMC = {"FRU_NUM":18,"NO_FRU_NUM":5, "PCIE_CHK_STR":"40 65 06 05 00","CPU_CHK_MOC":1.74, "MAC_CORE_V": "MAC_CORE_V",
            "SML":[{"name": "SML1", "bus": 6, "addr": 0x16, "offset": 0x00}],
        }

MAC_THRESHOLD = {"Min": -0.02, "Max": 0.02}

#################x86_2v23_current#################生测菜单项 #################################

test_BMC_NOMAL_item0 = {"name":"CPU 信息显示", "deal" :"bmc_get_cpu_info"}
test_BMC_NOMAL_item1 = { "name":"BMC DDR 信息显示","deal" :"bmc_get_ddr_info"}
test_BMC_NOMAL_item2 = { "name":"BMC eMMC 信息显示","deal" :"bmc_get_emmc_info"}
test_BMC_NOMAL_item3 = { "name":"BMC通过PECI访问CPU","deal" :"bmc_test_peci"}
test_BMC_NOMAL_item4 = { "name":"BMC访问CPU SML1(ME)","deal" :"bmc_test_SML0"}
test_BMC_NOMAL_item5 = { "name":"BMC I2C设备扫描","deal" :"bmc_test_i2c_scan"}
test_BMC_NOMAL_item7 = { "name":"系统/板级/风扇FRU EEPROM读取","deal" :"test_tbd"}#CPU ipmitool fru
test_BMC_NOMAL_item8 = { "name":"温感温度读取  ","deal" :"test_tbd"} # CPU platformutil.py sensor status
test_BMC_NOMAL_item9 = { "name":"DC/DC电压电流读取","deal" :"bmc_get_dcdc_info"}
test_BMC_NOMAL_item10 = { "name":"BMC GPIO测试","deal" :"bmc_test_cpu_gpio"}
test_BMC_NOMAL_item11 = { "name":"BMC CPLD测试","deal" :"bmc_cpld_check"}

test_PSU_item1 = { "name":"PSU FRU信息读取  ","deal" :"bmc_test_get_psu_rfu_info"}
test_PSU_item2 = { "name":"PSU电压电流功耗读取","deal" :"bmc_test_get_psu_info"}
test_PSU_item3 = { "name":"PSU状态监测(在位信号,ACOK,PWROK)","deal" :"bmc_test_get_psu_present"}

test_FAN_item1 = { "name":"风扇状态监测(在位信号，风向)","deal" :"bmc_test_get_fan_present"}
test_FAN_item2 = { "name":"风扇转速设置","deal" :"test_signal", "childid":MENU_ID_FAN_SPEED_SET_TEST}
test_FAN_item3 = { "name":"风扇转速读取","deal" :"bmc_test_get_fan_speed"}
test_Firmware_TMP_item1 = { "name":"通过MDIO读取54616s和5387寄存器","deal" :"bmc_test_MDIO"}
test_OPT_MODULE_item1 = { "name":"光模块在位检测","deal" :"test_tbd"}
test_strss_item1 = { "name":"DDR压力测试","deal" :"test_signal", "childid": MENU_ID_DDR_TEST}
test_strss_item3 = { "name":"eMMC压力测试","deal" :"test_signal", "childid": MENU_ID_EMMC_TEST}
test_strss_item4 = { "name":"I2C压力测试","deal":"bmc_test_i2c_stress" }
test_strss_item5 = { "name":"MDIO压力测试","deal":"bmc_test_MDIO_stress" }

test_led_item1 = { "name":"系统LED测试(SYS,PWR,FAN)","deal" :"bmc_test_sysled" }
test_led_item2 = { "name":"风扇模块LED测试","deal" :"bmc_test_fanled"}
test_led_item3 = { "name":"Location LED测试","deal" :"bmc_test_locationled"}

menuList =[
        {
        "menuid":MENU_ID_ROOT, "value":[
            {"name":"单项测试", "deal" :"test_signal", "childid":MENU_ID_TEST_SINGLE},
            #{"name":"所有测试", "deal" :"test_all"},
            #{"name":"拷机测试", "deal" :"test_loop"},
            #{"name":"拷机结果查看", "deal" :"test_loop_read"},
            #{"name":"拷机结果删除", "deal" :"test_loop_delete"},
#           #{"name":"配置加载", "deal" :"test_config"},
            #test_sys_reload_item,
            #{"name":"系统配置", "deal" :"test_sysconfig","childid":MENU_ID_TEST_SYS_CONFIG},
        ]
        },

        {
            "menuid":MENU_ID_TEST_SINGLE       , "parentid":MENU_ID_ROOT, "value":[
            {"name":"BMC 接口驱动测试", "deal" :"test_signal", "childid": MENU_ID_BMC_DRIVER_TEST },
            {"name":"PSU测试", "deal" :"test_signal", "childid": MENU_ID_PSU_TEST},
            {"name":"风扇测试", "deal" :"test_signal", "childid":  MENU_ID_FAN_TEST },
            {"name":"压力测试", "deal" :"test_signal", "childid": MENU_ID_STRESS_TEST },
            {"name":"LED测试", "deal" :"test_signal", "childid": MENU_ID_LED_TEST },
        ]},
        {
            "menuid":MENU_ID_BMC_DRIVER_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
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
        ]},

        {
            "menuid":MENU_ID_PSU_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
               test_PSU_item1,
               test_PSU_item2,
               test_PSU_item3,
        ]},            

        {
            "menuid":MENU_ID_FAN_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
                test_FAN_item1,
                test_FAN_item2,
                test_FAN_item3,       
         ]},              
        {
            "menuid":MENU_ID_STRESS_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
            test_strss_item1,
            test_strss_item3,
            test_strss_item4,
            test_strss_item5,

        ]},

        {
            "menuid":MENU_ID_DDR_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
                {"name":"开始后台测试", "deal" :"bmc_test_ddr_stress",    },
                {"name":"终止后台测试", "deal" :"bmc_test_ddr_stress_stop",     },
                {"name":"查看测试结果", "deal" :"bmc_test_ddr_stress_result",   },

        ]},
                {
            "menuid":MENU_ID_EMMC_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[
                {"name":"开始后台测试", "deal" :"bmc_test_emmc_stress",    },
                {"name":"终止后台测试", "deal" :"bmc_test_emmc_stress_stop",     },
                {"name":"查看测试结果", "deal" :"bmc_test_emmc_stress_result",   },

        ]},
        
        {
            "menuid":MENU_ID_LED_TEST, "parentid":MENU_ID_TEST_SINGLE, "value":[

                test_led_item1,
                test_led_item2,
                test_led_item3,

        ]},
       {
            "menuid":MENU_ID_FAN_SPEED_SET_TEST, "parentid":MENU_ID_FAN_TEST, "value":[

                {"name":"设置风扇等级-高", "deal" :"bmc_test_set_fan_speed_high",    },
                {"name":"设置风扇等级-中", "deal" :"bmc_test_set_fan_speed_middle",     },
                {"name":"设置风扇等级-低", "deal" :"bmc_test_set_fan_speed_low",   },

        ]},

#           二级菜单项 
        #{
        #    "menuid":MENU_ID_CPU_TEST        , "parentid":MENU_ID_TEST_SINGLE, "value":[
        #        test_cpu_info_item  ,
        #        test_sata_info_item ,
        #        test_ddr_info_item ,
        #        test_peci_scan_item ,
        #        test_lpc_read_cplds_item ,
        #        test_front_panel_usb_item ,
        #        test_usb_between_cpu_bmc_item ,
        #        test_KR_packet_item ,
        #        test_i2c_scan_item ,
        #        test_cpu_gpio_item ,
        #        test_rtc_test_item ,
        # 
        #    ]},        
        #
#       #{
#       "menuid":4, "parentid":MENU_ID_TEST_SYS_CONFIG, "value":[
#           test_e2_setmac_item ,
#           test_bmc_setmac_item,
#           test_fru_cpueeprom_item ,
#           test_fru_bmceeprom_item ,
#           test_fru_maceeprom_item ,
#           test_fru_fanseeprom_item,
#       ]},
        
]

PSU_INFO ={"as13-32h":[
        {"bus":14,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":15,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "as13-48f8h":[
        {"bus":14,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":15,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "as23-128h":[
        {"bus":33,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":32,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":31,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":30,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},        
        ],
        "as14-128h":[
        {"bus":33,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":32,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":31,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":30,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},        
        ],
        "as14-40d":[
        {"bus":22,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":23,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "as15-20d4m":[
        {"bus":37,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":38,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "droprecord_reg":{
        # NA
        "bus":0,
        "addr":0x0d,
        "offset":0x54,
        "bitoffset":{ "PSU1":0, "PSU2":1},
        },
        "psustatus_reg":{
        "bus":14,
        "addr":0x1d,
        "device":{ 
        "PSU1":{"offset":0x34, "bitoffset":1},
        "PSU2":{"offset":0x34, "bitoffset":5},
        },
        },
}             
 
I2C_SCAN_LIST=[
    {"name":"MAC板CPLDA                         " ,"bus":14 ,"addr":0x1D},
    {"name":"MAC板CPLDB                         " ,"bus":14 ,"addr":0x2D},
    {"name":"FPGA内部I2C SLAVE#1                " ,"bus":0 ,"addr":0x70},
    {"name":"FPGA内部I2C SLAVE#2                " ,"bus":1 ,"addr":0x70},
    {"name":"BMC扣板E2PROM                      " ,"bus":2 ,"addr":0x53},
    {"name":"BMC板E2PROM#1                      " ,"bus":2 ,"addr":0x56},
    {"name":"BMC板E2PROM#2                      " ,"bus":2 ,"addr":0x57},
    {"name":"FPGA内部I2C SLAVE#3                " ,"bus":4 ,"addr":0x70},
    {"name":"FPGA内部I2C SLAVE#4                " ,"bus":5 ,"addr":0x70},
    {"name":"BASE板CPLD                         " ,"bus":6 ,"addr":0x3D},
    {"name":"CPU扣板E2PROM                      " ,"bus":6 ,"addr":0x50},
    {"name":"CPU芯片SML1                        " ,"bus":6 ,"addr":0x16},
    {"name":"CPU扣板CPLD                        " ,"bus":6 ,"addr":0x0D},
    {"name":"BASE板E2PROM                       " ,"bus":18 ,"addr":0x57},
    {"name":"BASE板UCD90160A                    " ,"bus":20 ,"addr":0x5B},
    {"name":"CPU扣板VR电源/VCCIN/P1V05          " ,"bus":21 ,"addr":0x67},
    {"name":"CPU扣板VR电源/P1V2_VDDQ/P2V5_VPP   " ,"bus":21 ,"addr":0x6C},
    {"name":"CPU扣板监控芯片INA3221             " ,"bus":21 ,"addr":0x43},
    {"name":"风扇板CPLD                         " ,"bus":16 ,"addr":0x3D},
    {"name":"风扇1_E2PROM                       " ,"bus":31 ,"addr":0x50},
    {"name":"风扇2_E2PROM                       " ,"bus":30 ,"addr":0x50},
    {"name":"风扇3_E2PROM                       " ,"bus":29 ,"addr":0x50},
    {"name":"风扇4_E2PROM                       " ,"bus":28 ,"addr":0x50},
    {"name":"风扇5_E2PROM                       " ,"bus":27 ,"addr":0x50},
    {"name":"风扇6_E2PROM                       " ,"bus":26 ,"addr":0x50},
    {"name":"风扇板LM75_1                       " ,"bus":32 ,"addr":0x48},
    {"name":"风扇板LM75_2                       " ,"bus":32 ,"addr":0x49},
    {"name":"风扇板E2PROM                       " ,"bus":33 ,"addr":0x56},
    {"name":"MAC板E2PROM                        " ,"bus":34 ,"addr":0x57},
    {"name":"TMP411A#1                          " ,"bus":35 ,"addr":0x4C},
    {"name":"TMP411A#2                          " ,"bus":36 ,"addr":0x4C},
    {"name":"LM75#1                             " ,"bus":35 ,"addr":0x4B},
    {"name":"LM75#2                             " ,"bus":36 ,"addr":0x4E},
    {"name":"LM75#3                             " ,"bus":36 ,"addr":0x4F},
    {"name":"PSU1_E2PROM                        " ,"bus":37 ,"addr":0x50},
    {"name":"PSU1_PMBUS                         " ,"bus":37 ,"addr":0x58},
    {"name":"PSU2_E2PROM                        " ,"bus":38 ,"addr":0x50},
    {"name":"PSU1_PMBUS                         " ,"bus":38 ,"addr":0x58},
    {"name":"英飞凌电源                         " ,"bus":39 ,"addr":0x4E},
    {"name":"英飞凌电源 PMBUS                   " ,"bus":39 ,"addr":0x40},
    {"name":"MAC芯片BSC2                        " ,"bus":40 ,"addr":0x44},
    {"name":"UCD90160A                          " ,"bus":41 ,"addr":0x5B},
]


LED_INFO ={
    "sysleds":{ 
        "attrs":OrderedDict([("light-off",0xff),("red-light-blinking",0xfd),("red-light-on",0xf5),("green-light-blinking",0xfe),("green-light-on",0xf6),("yellow-light-blinking",0xfb),("yellow-light-on",0xf3),("backing-off",0xff),]),
        "bus":14,
        "addr":0x2D,
        "name":"前面板灯sys、pwr、fan灯",
        "device":[
            {"reg":0x41, "bus": 12}, #sys
            {"reg":0x42}, #fan
            {"reg":0x43}, #pwr
        ]
    },
    "fanleds":{ 
        "attrs":OrderedDict([("light-off",0xff),("red-light-blinking",0xf9),("red-light-on",0xfa),("green-light-blinking",0xfb),("green-light-on",0xfc),("yellow-light-blinking",0xfd),("yellow-light-on",0xfe),("backing-off",0Xff)]),
        "bus":16,
        "addr":0x3D,
        "name":"风扇灯",
        "device":[
            {"reg":0x41},
            {"reg":0x40},
            {"reg":0x3f},
            {"reg":0x3e},
            {"reg":0x3d},
            {"reg":0x3c},
        ]
    },
    "location_led":{ 
        "attrs":OrderedDict([("bit-stream-on",0xff),("green-light-blinking",0xee),("green-light-on",0xe6),("yellow-light-blinking",0xeb),("yellow-light-on",0xe3),("backing-bit-stream-on",0xff)]),
        "bus":14,
        "addr":0x1d,
        "name":"location 灯",
        "device":[
            {"reg":0x3b}, #LED0~15
            {"reg": 0x3a, "bus": 14, "addr": 0x2d}, #LED16~33
        ]
    }
}

FAN_SPEED = {
        "speedlevel":{"high":{"value":255,"low_threshhold":16000,"high_threshhold":40000},
                      "middle":{"value":150,"low_threshhold":8000,"high_threshhold":19000},
                      "low":{"value":102,"low_threshhold":5000,"high_threshhold":14000},
        },
        "bus":16,
        "addr":0x3D,
        "watchdogreg": 0x33,
        "waittime":8,
        "device":[
            {"name":"风扇1","reg":0x65},
            {"name":"风扇2","reg":0x64},
            {"name":"风扇3","reg":0x63},
            {"name":"风扇4","reg":0x62},
            {"name":"风扇5","reg":0x61},
            {"name":"风扇6","reg":0x60},
        ]
}


FAN_INFO = {
        "droprecord_reg":{
        # NA
        "bus":16,
        "addr":0x3D,
        "offset":0x57,
        "bitoffset":{"FAN1":0, "FAN2":1, "FAN3":2, "FAN4":3, "FAN5":4, "FAN6":5},
        },
        "present":{
        "path": "/sys/bus/i2c/devices/16-003d/hwmon/hwmon*/fan_present",
        "bitoffset":{"FAN1":5, "FAN2":4, "FAN3":3, "FAN4":2, "FAN5":1, "FAN6":0},
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
