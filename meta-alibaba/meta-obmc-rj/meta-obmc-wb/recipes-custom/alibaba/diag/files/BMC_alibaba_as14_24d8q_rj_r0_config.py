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

RUIJIE_CARDID      = 0x00004086
RUIJIE_PRODUCTNAME = "as14-24d8q"

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
    {"bus":8, "devno":0x0d, "addr":0x66}, {"bus":8, "devno":0x0d, "addr":0x76}], "open":0x00, "close":0xff}

E2_DEV = {
    "E2_FAN":{"canreset":True,"list":[{"bus":54,"addr":0x50},{"bus":55,"addr":0x50},{"bus":56,"addr":0x50},{"bus":57,"addr":0x50},{"bus":58,"addr":0x50},{"bus":59,"addr":0x50}],"restartserv":"","extra":"-F-",},
    "E2_PSU":{"canreset":True,"list":[{"bus":46,"addr":0x50},{"bus":47,"addr":0x50}],"restartserv":"","extra":"-LD-",},
    "E2_PSU":{"canreset":True,"list":[{"bus":46,"addr":0x50},{"bus":47,"addr":0x50}],"restartserv":"","extra":"-F-",},
    "E2_CPU":{"canreset":True,"list":[{"bus":1,"addr":0x50}],"restartserv":"","protect":{"bus":1, "devno":0x0d, "addr":0x51, "open":0x00, "close":0xff},},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":2,"addr":0x57}],"restartserv":"",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"",},
    "E2_MAC":{"canreset":True,"list":[{"bus":14,"addr":0x51}],"restartserv":"",},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":8,"addr":0x56}],"restartserv":"","protect":{"bus":8, "devno":0x0d, "addr":0xf0, "open":0x00, "close":0xff},"extra":"-F-",},
    "E2_IBVB_CARD": {"canreset": True, "list": [ {"bus": 51, "addr": 0x57}], "restartserv": "", "extra":"-LC-",}, 
}

ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-1/1-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'mac': {'loc': '/sys/bus/i2c/devices/i2c-14/14-0051/eeprom', 'way': 'sysfs'},
              'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-8/8-0056/eeprom', 'way': 'sysfs', "extra":"-F-"},
              'ibvb_card': {'loc': '/sys/bus/i2c/devices/i2c-51/51-0057/eeprom', 'way': 'sysfs', 'extra':'-LC-'},
             }

DCDC_DEVICE = [ ]

CPLD_TEST = [
    {"name":"BASE CPLD", "bus": 0, "addr": 0x0D ,"test_reg": 0xaa},
    {"name":"CPU CPLD", "bus": 1, "addr": 0x0D, "test_reg": 0x05},
    {"name":"FAN CPLD", "bus": 8, "addr": 0x0D, "test_reg": 0xf1, "extra": "-F-"},
    {"name":"MAC CPLD1", "bus": 16,"addr": 0x30, "test_reg": 0x0f},
    {"name":"MAC CPLD2", "bus": 17,"addr": 0x31, "test_reg": 0x0f},
]

FPGA_TEST = [
    {"name":"FPGA"  ,"bus":	5 ,"addr":0x70,"test_reg":0x8},
]

ALI_BMC = {"FRU_NUM":18, "NO_FRU_NUM":5, "LC_FRU_NUM":19, "LC_NO_FRU_NUM":6, "PCIE_CHK_STR":"40 c1 06 06 00", "MAC_CORE_V": "MAC_CORE_V",
            "SML":[{"name": "SMB_PECI_WRITE", "bus": 22, "addr": 0x4c, "offset": 0x00},
                    {"name": "SMB_PECI_READ", "bus": 22, "addr": 0x4b, "offset": 0x40},
                    {"name": "SML0", "bus": 23, "addr": 0x16, "offset": 0x00},
                    {"name": "SML1", "bus": 24, "addr": 0x48, "offset": 0x00},
            ],
            "CPU_PLATFORM": "ICELAKE",
            "CPU_CHK_LIST": ["OCM_VNN_PCH_V", "OCM_VNN_NAC_V"],
}

MAC_THRESHOLD = {"Min": -0.005, "Max": 0.005}

NETCARD_INFO = {
    "slotreg": {
        "bus": 0, "addr": 0x0d,
        "signal": {"mask": 0x30, "intrptless": 0x30, "clear": 0x30},
        "present": {},
        # "slotn" : {"bus": xx, "addr": xx, "offset": xx, "present": {xx}, "signal": {xx},},
        "slot1": { "offset": 0x30, "present": {"mask": 0x0f, "absent": 0x0f}},
        "slot2": { "offset": 0x31, "present": {"mask": 0x01, "absent": 0x01}},
    },
    "smbus_info": {
        # bus
        "slot1": 62, "slot2": 63,
        # checklist
        "DPU": [{"addr": 0x4a, "offset": 0x00}, {"addr": 0x53}],
        "IPU": [{"addr": 0x32}, {"addr": 0x53}, {"addr": 0x61}],
        # check reg
        "diagnosis": {
            "DPU": {"addr": 0x4a,
                "reg_info": [
                    {"name": "SOC Temperature", "offset": 0x16, "way": "threshold", "threshold": {"max": 95}},
                    {"name": "Board Temperature", "offset": 0x18, "way": "threshold", "threshold": {"max": 70}},
                    {"name": "SOC Warning Temperature", "offset": 0x1b, "way": "show"},
                    {"name": "SOC Critical Temperature", "offset": 0x1c, "way": "show"},
                    {"name": "SOC Fatal Temperature", "offset": 0x1d, "way": "show"},
                    {"name": "QSFP P1/P2 Present", "offset": 0x40, "way": "val", "val": 0x03},
                    {"name": "Power Cycle Reason", "offset": 0x50, "way": "val", "val": 0x00},
                    {"name": "Core PLL Lost Lock Count", "offset": 0x2b, "way": "show"},
                    {"name": "CPU PLL Lost Lock Count", "offset": 0x2c, "way": "show"},
                    {"name": "Flash PLL Lost Lock Count", "offset": 0x2d, "way": "val", "val": 0x00},
                    {"name": "PCIe PLL Lost Lock Count", "offset": 0x2e, "way": "show"},
                    {"name": "Power Fail Status0", "offset": 0x30, "way": "val", "val": 0x00},
                    {"name": "Power Fail Status1", "offset": 0x31, "way": "val", "val": 0x00},
                    {"name": "Power Fail Status2", "offset": 0x32, "way": "val", "val": 0x00}
                ]
            }
        }
    },
    "product": {
        # "fullproductname": [{"pos": "slotn", "cardtype": "DPU/IPU", "slotreg": {xxxx}, "smbus_info": {xxxx}}, ...],
        "AS14-24D8Q-B1-F-RJ": [{"pos": "slot1", "cardtype": "DPU"}],
        "AS14-24D8Q-B3-F-RJ": [{"pos": "slot1", "cardtype": "DPU"}, {"pos": "slot2", "cardtype": "DPU"},],
        "AS14-24D8Q-B2-F-RJ": [{"pos": "slot1", "cardtype": "IPU"}],
        "AS14-24D8Q-B4-F-RJ": [{"pos": "slot1", "cardtype": "IPU"}, {"pos": "slot2", "cardtype": "IPU"},],
        "AS14-24D8Q-A1-F-RJ": [{"pos": "slot1", "cardtype": "DPU"}],
        "AS14-24D8Q-A3-F-RJ": [{"pos": "slot1", "cardtype": "DPU"}, {"pos": "slot2", "cardtype": "DPU"},],
    },
}

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
        "as14-24d8q":[
        {"bus":46,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":47,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "droprecord_reg":{
        "bus":0,
        "addr":0x0d,
        "offset":0x54,
        "bitoffset":{ "PSU1":0, "PSU2":1},
        },
        "psustatus_reg":{
        "bus":0,
        "addr":0x0d,
        "device":{ 
        "PSU1":{"offset":0x51, "bitoffset":1},
        "PSU2":{"offset":0x51, "bitoffset":5},
        },
        "lcd_device":{
        "PSU1":{"offset":0x50, "bitoffset":4},
        "PSU2":{"offset":0x50, "bitoffset":6},
        },
        },
}             

I2C_SCAN_LIST=[
    {"name":"BASE CPLD(0-000D)                      " ,"bus":0 ,"addr":0x0D},
    {"name":"BASE CPLD upgrade channel(0-0040)               " ,"bus":0 ,"addr":0x40},
    {"name":"CPU CPLD(1-000D)                       " ,"bus":1 ,"addr":0x0D},
    {"name":"CPU CPLD upgrade channel(1-0040)                " ,"bus":1 ,"addr":0x40},
    {"name":"CPU EEPROM(24c02)(1-0050)              " ,"bus":1 ,"addr":0x50},
    {"name":"BMC EEPROM(24c02)(2-0053)              " ,"bus":2 ,"addr":0x53},
    {"name":"BASE EEPROM(24c02)(2-0057)             " ,"bus":2 ,"addr":0x57},
    {"name":"PCA9548(2-0071)                        " ,"bus":2 ,"addr":0x71},
    {"name":"MAC EEPROM(24c02)(14-0051)              " ,"bus":14 ,"addr":0x51},
    {"name":"CLOCK EEPROM(15-0050)                   " ,"bus":15 ,"addr":0x50},
    {"name":"RC32012 Clock(15-0058)                    " ,"bus":15 ,"addr":0x58},
    {"name":"MAC CPLD1(16-0030)                      " ,"bus":16 ,"addr":0x30},
    {"name":"MAC CPLD2(17-0031)                      " ,"bus":17 ,"addr":0x31},
    {"name":"MAC CPLD1 upgrade channel(18-0040)               " ,"bus":18 ,"addr":0x40},
    {"name":"MAC CPLD2 upgrade channel(19-0040)               " ,"bus":19 ,"addr":0x40},
    {"name":"PCA9548(3-0070)                         " ,"bus":3 ,"addr":0x70},
    {"name":"SMB_PECI_WRITE(22-004C)                 " ,"bus":22 ,"addr":0x4c},
    {"name":"SMB_PECI_READ(22-004B)                  " ,"bus":22 ,"addr":0x4b, "reg":0x40},
    {"name":"SML0(23-0016)                           " ,"bus":23 ,"addr":0x16},
    {"name":"SML1(24-0048)                           " ,"bus":24 ,"addr":0x48},
    {"name":"PCA9548(4-0072)                         " ,"bus":4 ,"addr":0x72},
    {"name":"INA3221(30-0041)                        " ,"bus":30 ,"addr":0x41},
    {"name":"INA3221(31-0041)                        " ,"bus":31 ,"addr":0x41},
    {"name":"INA3221(32-0041)                        " ,"bus":32 ,"addr":0x41},
    {"name":"INA3221(33-0041)                        " ,"bus":33 ,"addr":0x41},
    {"name":"INA3221(34-0041)                        " ,"bus":34 ,"addr":0x41},
    {"name":"UCD90160(35-005F)                       " ,"bus":35 ,"addr":0x5F},
    {"name":"XDPE12284C(35-005E)                     " ,"bus":35 ,"addr":0x5E},
    {"name":"XDPE12284C(35-0068)                     " ,"bus":35 ,"addr":0x68},
    {"name":"XDPE12284C(35-006E)                     " ,"bus":35 ,"addr":0x6E},
    {"name":"XDPE12284C(35-0070)                     " ,"bus":35 ,"addr":0x70},
    # 硬件需求，不再测试
    #{"name":"RC32504A(35-0009)                       " ,"bus":35 ,"addr":0x09},
    {"name":"PCA9548(4-0071)                         " ,"bus":4 ,"addr":0x71},
    {"name":"INA3221(38-0040)                        " ,"bus":38 ,"addr":0x40},
    {"name":"INA3221(39-0040)                        " ,"bus":39 ,"addr":0x40},
    {"name":"INA3221(40-0040)                        " ,"bus":40 ,"addr":0x40},
    {"name":"INA3221(41-0040)                        " ,"bus":41 ,"addr":0x40},
    {"name":"INA3221(42-0040)                        " ,"bus":42 ,"addr":0x40},
    {"name":"XDPE132G5C(43-0040)                     " ,"bus":43 ,"addr":0x40},
    {"name":"BMC accesses FPGA channel(5-0070)                 " ,"bus":5 ,"addr":0x70},
    {"name":"RTC channel(6-0051)                         " ,"bus":6 ,"addr":0x51},
    {"name":"MAC board TMP275（top layer of the air inlet）(7-0048)      " ,"bus":7 ,"addr":0x48},
    {"name":"MAC board TMP275（Top layer of the hottest spot）(7-0049)      " ,"bus":7 ,"addr":0x49},
    {"name":"MAC board TMP275（Bottom layer of the air inlet）(7-004B)   " ,"bus":7 ,"addr":0x4B},
    {"name":"TD4 BSC2 channel(7-0044)                    " ,"bus":7 ,"addr":0x44},
    {"name":"TD4 TMP411 chip(7-004C)                  " ,"bus":7 ,"addr":0x4C},
    # 1，表示：风冷设备独有，非风冷设备需要屏蔽
    {"name":"PCA9548(6-0077)                         " ,"bus":6 ,"addr":0x77 ,"scan_shielde_capacity": 1},
    {"name":"PSU PMBUS(46-0058)                      " ,"bus":46 ,"addr":0x58 ,"scan_shielde_capacity": 1},
    #{"name":"PSU EEPROM(46-0050)                    " ,"bus":46 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"PSU PMBUS(47-0058)                      " ,"bus":47 ,"addr":0x58 ,"scan_shielde_capacity": 1},
    #{"name":"PSU EEPROM(47-0050)                    " ,"bus":47 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FCB CPLD(8-000D)                        " ,"bus":8 ,"addr":0x0D ,"scan_shielde_capacity": 1},
    {"name":"FCB CPLD upgrade channel(8-0040)                " ,"bus":8 ,"addr":0x40 ,"scan_shielde_capacity": 1},
    {"name":"FCB EEPROM(8-0056)                      " ,"bus":8 ,"addr":0x56 ,"scan_shielde_capacity": 1},
    {"name":"PCA9548(8-0075)                         " ,"bus":8 ,"addr":0x75 ,"scan_shielde_capacity": 1},
    {"name":"FAN1 EEPROM(54-0050)                    " ,"bus":54 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FAN2 EEPROM(55-0050)                    " ,"bus":55 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FAN3 EEPROM(56-0050)                    " ,"bus":56 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FAN4 EEPROM(57-0050)                    " ,"bus":57 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FAN5 EEPROM(58-0050)                    " ,"bus":58 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FAN6 EEPROM(59-0050)                    " ,"bus":59 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    {"name":"FCB board TMP275(60-0049)                   " ,"bus":60 ,"addr":0x49 ,"scan_shielde_capacity": 1},
    {"name":"FCB board TMP275(61-0048)                   " ,"bus":61 ,"addr":0x48 ,"scan_shielde_capacity": 1},
    {"name":"PCA9548(13-0070)                        " ,"bus":13 ,"addr":0x70 ,"scan_shielde_capacity": 1},
    #{"name":"网卡1 SMBUS(62-0050)                   " ,"bus":62 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    #{"name":"网卡2 SMBUS(63-0050)                   " ,"bus":63 ,"addr":0x50 ,"scan_shielde_capacity": 1},
    # 2, 表示：液冷集中供电LC设备独有，非LC设备需要屏蔽
    {"name":"PCA9548(6-0076)                         " ,"bus":6 ,"addr":0x76 ,"scan_shielde_capacity": 2},
    {"name":"PCA9554(46-0027)                        " ,"bus":46 ,"addr":0x27 ,"scan_shielde_capacity": 2},
    {"name":"LM5066(47-0015)                         " ,"bus":47 ,"addr":0x15 ,"reg":0x01,"scan_shielde_capacity": 2},
    {"name":"RAA228004(48-0060)                      " ,"bus":48 ,"addr":0x60 ,"scan_shielde_capacity": 2},
    {"name":"INA3221(49-0040)                        " ,"bus":49 ,"addr":0x40 ,"scan_shielde_capacity": 2},
    {"name":"TMP275(50-004F)                         " ,"bus":50 ,"addr":0x4F ,"scan_shielde_capacity": 2},
    {"name":"IBVB EEPROM(24c02)(51-0057)             " ,"bus":51 ,"addr":0x57 ,"scan_shielde_capacity": 2},
    {"name":"PCA9548(13-0070)                        " ,"bus":13 ,"addr":0x70 ,"scan_shielde_capacity": 2},
    #{"name":"网卡1 SMBUS(54-0050)                   " ,"bus":54 ,"addr":0x50 ,"scan_shielde_capacity": 2},
    #{"name":"网卡2 SMBUS(55-0050)                   " ,"bus":55 ,"addr":0x50 ,"scan_shielde_capacity": 2},
    # 3, 表示：液冷非集中供电LD设备独有，非LD设备需要屏蔽
    {"name":"PCA9548(6-0057)                         " ,"bus":6 ,"addr":0x75 ,"scan_shielde_capacity": 3},
    {"name":"PSU PMBUS(46-0058)                      " ,"bus":46 ,"addr":0x58 ,"scan_shielde_capacity": 3},
    #{"name":"PSU EEPROM(46-0050)                    " ,"bus":46 ,"addr":0x50 ,"scan_shielde_capacity": 3},
    {"name":"PSU PMBUS(47-0058)                      " ,"bus":47 ,"addr":0x58 ,"scan_shielde_capacity": 3},
    #{"name":"PSU EEPROM(47-0050)                    " ,"bus":47 ,"addr":0x50 ,"scan_shielde_capacity": 3},
    {"name":"PCA9548(13-0070)                        " ,"bus":13 ,"addr":0x70 ,"scan_shielde_capacity": 3},
    #{"name":"网卡1 SMBUS(54-0050)                   " ,"bus":54 ,"addr":0x50 ,"scan_shielde_capacity": 3},
    #{"name":"网卡2 SMBUS(55-0050)                   " ,"bus":55 ,"addr":0x50 ,"scan_shielde_capacity": 3},
]

LED_INFO ={
    "sysleds":{
        "attrs":OrderedDict([("light-off",0x10),("red-light-blinking",0x11),("red-light-on",0x12),("green-light-blinking",0x13),("green-light-on",0x14),("yellow-light-blinking",0x15),("yellow-light-on",0x16),("backing-off",0x10),]),
        "bus":0,
        "addr":0X0D,
        "name":"Front panel sys, pwr, fan LED",
        "device":[
            {"reg":0x72},
            {"reg":0x73},
            {"reg":0x08, "bus":8, "addr":0X0D, "extra": "-F-"}, #风冷 sysfan灯 (Bit4 1：软件控制点灯)
            {"reg":0x75, "bus":0, "addr":0X0D, "extra": "-LC-"}, #LC sysfan灯 (Bit4 1：软件控制点灯)
            {"reg":0x75, "bus":0, "addr":0X0D, "extra": "-LD-"}, #LD sysfan灯 (Bit4 1：软件控制点灯)
        ]
    },
    "fanleds":{
        "attrs":OrderedDict([("light-off",0X0B),("red-light-blinking",0x0E),("red-light-on",0x0A),("green-light-blinking",0x0D),("green-light-on",0x09),("yellow-light-blinking",0x07),("yellow-light-on",0x03),("backing-off",0X0B)]),
        "bus":8,
        "addr":0X0D,
        "name":"Fan LED",
        "device":[
            {"reg":0x25},
            {"reg":0x35},
            {"reg":0x45},
            {"reg":0x55},
            {"reg":0x65},
            {"reg":0x75},
        ]
    },
    "location_led":{
        "attrs":OrderedDict([("bit-stream-on",0X98),("green-light-blinking",0x83),("green-light-on",0x84),("yellow-light-blinking",0x85),("yellow-light-on",0x86),("backing-bit-stream-on",0X98)]),
        "bus":5,
        "addr":0X70,
        "name":"location LED",
        "device":[
            {"reg":0x10},
            {"reg":0x14},
            {"reg":0x18},
            {"reg":0x1c},
        ]
    }
}

FAN_SPEED = {
        "speedlevel":{"high":{"value":255,"low_threshhold":16000,"high_threshhold":40000},
                      "middle":{"value":150,"low_threshhold":10000,"high_threshhold":21000},
                      "low":{"value":102,"low_threshhold":500,"high_threshhold":14000},
        },
        "bus":8,
        "addr":0X0D,
        "watchdogreg":0x0C,
        "waittime":8,
        "device":[
            {"name":"Fan1","reg":0x24},
            {"name":"Fan2","reg":0x34},
            {"name":"Fan3","reg":0x44},
            {"name":"Fan4","reg":0x54},
            {"name":"Fan5","reg":0x64},
            {"name":"Fan6","reg":0x74},
        ]
}

FAN_INFO = {
        "droprecord_reg":{
        "bus":8,
        "addr":0x0D,
        "num_of_offset": "multiple",
        "offset":{"FAN1": 0x28, "FAN2": 0x38, "FAN3": 0x48, "FAN4": 0x58, "FAN5": 0x68, "FAN6": 0x78},
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
                "FAN6": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan6_present",
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

BUSBAR_INFO = {
    "extra": "-LC-",
    "info": [
        {"gpio": 480, "offset": 0},
        {"gpio": 481, "offset": 1},
        {"gpio": 482, "offset": 2},
        {"gpio": 484, "offset": 3},
        {"gpio": 485, "offset": 4},
        {"gpio": 486, "offset": 5},
    ],
}