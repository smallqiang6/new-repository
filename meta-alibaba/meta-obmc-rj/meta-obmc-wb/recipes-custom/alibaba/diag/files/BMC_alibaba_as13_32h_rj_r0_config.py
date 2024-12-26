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

RUIJIE_CARDID      = 0x00004051
RUIJIE_PRODUCTNAME = "as13-32h"

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
FAN_PROTECT = {"bus":8, "devno":0x0d, "addr":0x19, "open":0x00, "close":0xff}
E2_DEV = {
    "E2_FAN":{"canreset":True,"list":[{"bus":22,"addr":0x50},{"bus":23,"addr":0x50},{"bus":24,"addr":0x50},{"bus":25,"addr":0x50},{"bus":26,"addr":0x50}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-fan%d.service",},
    "E2_PSU":{"canreset":True,"list":[{"bus":14,"addr":0x50},{"bus":15,"addr":0x50}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-psu%d.service",},
    "E2_CPU":{"canreset":True,"list":[{"bus":1,"addr":0x50}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-cpu.service",},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":2,"addr":0x57}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-motherboard.service",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-bmc.service",},
    "E2_MAC":{"canreset":True,"list":[{"bus":2,"addr":0x51}],"restartserv":"systemctl restart obmc-read-eeprom@system-chassis-mac.service",},
}
ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-1/1-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'mac': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0051/eeprom', 'way': 'sysfs'},
             }

DCDC_DEVICE = [
    {"name":"ODM_Mac1v2_C","file":"curr10_input"},
    {"name":"ODM_Mac3v3Cpld_C","file":"curr11_input"},
    {"name":"ODM_Mac5v0_C","file":"curr12_input"},
    {"name":"ODM_Mac1v2_V","file":"in10_input"},
    {"name":"ODM_Mac3v3Cpld_V","file":"in11_input"},
    {"name":"ODM_Mac5v0_V","file":"in12_input"},
    {"name":"ODM_Mac3v3Qs1_C","file":"curr13_input"},
    {"name":"ODM_Mac3v3Qs2_C","file":"curr14_input"},
    {"name":"ODM_Mac3v3_C","file":"curr15_input"},
    {"name":"ODM_Mac3v3Qs1_V","file":"in13_input"},
    {"name":"ODM_Mac3v3Qs2_V","file":"in14_input"},
    {"name":"ODM_Mac3v3_V","file":"in15_input"},
    {"name":"ODM_Con1v2_C","file":"curr16_input"},
    {"name":"ODM_Con3v3_C","file":"curr17_input"},
    {"name":"ODM_Con3v3Ssd_C","file":"curr18_input"},
    {"name":"ODM_Con1v2_V","file":"in16_input"},
    {"name":"ODM_Con3v3_V","file":"in17_input"},
    {"name":"ODM_Con3v3Ssd_V","file":"in18_input"},
    {"name":"SYS_1V7_C","file":"curr19_input"},
    {"name":"SYS_3V3_C","file":"curr20_input"},
    {"name":"SYS_5V_C","file":"curr21_input"},
    {"name":"SYS_1V7_V","file":"in19_input"},
    {"name":"SYS_3V3_V","file":"in20_input"},
    {"name":"SYS_5V_V","file":"in21_input"},
    {"name":"CPU_CCORE","file":"curr22_input"},
    {"name":"CPU_1V05_C","file":"curr23_input"},
    {"name":"CPU_VCORE","file":"in22_input"},
    {"name":"CPU_1V05_V","file":"in23_input"},
    {"name":"SWITCH_CCORE","file":"curr24_input"},
    {"name":"SWITCH_CANALOG","file":"curr25_input"},
    {"name":"SWITCH_VCORE","file":"in24_input"},
    {"name":"SWITCH_VANALOG","file":"in25_input"},
    {"name":"SYS_1V2_C","file":"curr26_input"},
    {"name":"SYS_2V23_C","file":"curr27_input"},
    {"name":"SYS_1V2_V","file":"in26_input"},
    {"name":"SYS_2V23_V","file":"in27_input"},
    ]   

CPLD_TEST = [
    {"name":"CPU底板CPLD"  ,"bus":	0 ,"addr":0x0D,"test_reg":0xaa},
    #{"name":"CPU板CPLD"  ,"bus":	1 ,"addr":0x0D,"test_reg":0xaa},
    {"name":"风扇板CPLD"  ,"bus":	8 ,"addr":0x0D,"test_reg":0xaa},
]
FPGA_TEST = [
    {"name":"FPGA"  ,"bus":	5 ,"addr":0x70,"test_reg":0x8},
]

ALI_BMC = {"FRU_NUM":15,"NO_FRU_NUM":5, "PCIE_CHK_STR":"40 63 06 05 00"}

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
        "psustatus_reg":{
        "bus":0,
        "addr":0x0d,
        "device":{ 
        "PSU1":{"offset":0x51, "bitoffset":1},
        "PSU2":{"offset":0x51, "bitoffset":5},
        },
        },
}             

    
I2C_SCAN_LIST=[
    {"name":"CPU底板CPLD                 " ,"bus":0 ,"addr":0x0D},
    {"name":"CPU板CPLD                   " ,"bus":1 ,"addr":0x0D},
    {"name":"X86板E2                     " ,"bus":1 ,"addr":0x50},
    {"name":"SML1(ME)                    " ,"bus":1 ,"addr":0x16},
    {"name":"BMC板 E2PROM                " ,"bus":2 ,"addr":0x53},
    {"name":"CPU底板 E2PROM              " ,"bus":2 ,"addr":0x57},
    {"name":"MAC板 E2PROM                " ,"bus":2 ,"addr":0x51},
    {"name":"CPU底板 电压电流监控" ,"bus":4 ,"addr":0x42},
    {"name":"X86板 电压电流监控          " ,"bus":4 ,"addr":0x43},
    {"name":"X86电源芯片1                " ,"bus":4 ,"addr":0x60},
    {"name":"X86电源芯片2                " ,"bus":4 ,"addr":0x6C},
    {"name":"MAC板ISL68127               " ,"bus":4 ,"addr":0x64},
    {"name":"MAC板电压电流监控1          " ,"bus":4 ,"addr":0x40},
    {"name":"MAC板电压电流监控2          " ,"bus":4 ,"addr":0x41},
    #不存在{"name":"BMC访问FPGA通道" ,"bus":5 ,"addr":0x36},
    {"name":"PSU1 PMBUS                  " ,"bus": 14 ,"addr":0x58},
    {"name":"PSU1 FRU                    " ,"bus": 14 ,"addr":0x50},
    {"name":"PSU2 PMBUS                  " ,"bus": 15 ,"addr":0x58},
    {"name":"PSU2 FRU                    " ,"bus": 15 ,"addr":0x50},
    {"name":"CPU底板LM75                 " ,"bus":7 ,"addr":0x4C},
    {"name":"MAC板LM75，入风口           " ,"bus":7 ,"addr":0x48},
    {"name":"MAC板LM75，MAC前            " ,"bus":7 ,"addr":0x49},
    {"name":"MAC板LM75，MAC后            " ,"bus":7 ,"addr":0x4A},
#    {"name":"TD3 BSC2" ,"bus":7 ,"addr":0x44},
#    {"name":"TD3 MAX TEMP" ,"bus":7 ,"addr":0x45},
    {"name":"CPU底板CPLD FAN logic       " ,"bus":8 ,"addr":0x0D},
    {"name":"风扇模块E2PROM1             " ,"bus":22 ,"addr":0x50 ,"scan_shielde_capacity":1},
    {"name":"风扇模块E2PROM2             " ,"bus":23 ,"addr":0x50 ,"scan_shielde_capacity":1},
    {"name":"风扇模块E2PROM3             " ,"bus":24 ,"addr":0x50 ,"scan_shielde_capacity":1},
    {"name":"风扇模块E2PROM4             " ,"bus":25 ,"addr":0x50 ,"scan_shielde_capacity":1},
    {"name":"风扇模块E2PROM5             " ,"bus":26 ,"addr":0x50 ,"scan_shielde_capacity":1},
    {"name":"88e6321配置E2PROM           " ,"bus":4 ,"addr":0x50 ,"scan_shielde_capacity":6321},
]


LED_INFO ={
    "sysleds":{ 
        "attrs":OrderedDict([("light-off",0x10),("red-light-blinking",0x11),("red-light-on",0x12),("green-light-blinking",0x13),("green-light-on",0x14),("yellow-light-blinking",0x15),("yellow-light-on",0x16),("backing-off",0x10),]),
        "bus":0,
        "addr":0X0D,
        "name":"前面板灯sys、pwr、fan灯",
        "device":[
            {"reg":0x72},
            {"reg":0x73},
            {"reg":0x74},
        ]
    },
    "fanleds":{ 
        "attrs":OrderedDict([("light-off",0X0B),("red-light-blinking",0x0E),("red-light-on",0x0A),("green-light-blinking",0x0D),("green-light-on",0x09),("yellow-light-blinking",0x07),("yellow-light-on",0x03),("backing-off",0X0B)]),
        "bus":8,
        "addr":0X0D,
        "name":"风扇灯",
        "device":[
            {"reg":0x3b},
            {"reg":0x3c},
            {"reg":0x3d},
            {"reg":0x3e},
            {"reg":0x3f},

        ]
    },
    "location_led":{ 
        "attrs":OrderedDict([("bit-stream-on",0X98),("green-light-blinking",0x83),("green-light-on",0x84),("yellow-light-blinking",0x85),("yellow-light-on",0x86),("backing-bit-stream-on",0X98)]),
        "bus":5,
        "addr":0X70,
        "name":"location 灯",
        "device":[
            {"reg":0x10},
        ]
    }
}

FAN_SPEED = {
        "speedlevel":{"high":{"value":255,"low_threshhold":16000,"high_threshhold":40000},
                      "middle":{"value":150,"low_threshhold":8000,"high_threshhold":19000},
                      "low":{"value":102,"low_threshhold":5000,"high_threshhold":14000},
        },
        "bus":8,
        "addr":0X0D,
        "waittime":5,
        "device":[
            {"name":"风扇1","reg":0x14},
            {"name":"风扇2","reg":0x15},
            {"name":"风扇3","reg":0x16},
            {"name":"风扇4","reg":0x17},
            {"name":"风扇5","reg":0x18},
        ]
}
FAN_INFO = {
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
