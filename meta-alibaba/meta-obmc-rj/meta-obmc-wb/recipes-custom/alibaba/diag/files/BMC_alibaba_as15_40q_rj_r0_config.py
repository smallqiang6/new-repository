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

RUIJIE_CARDID      = 0x000040e6
RUIJIE_PRODUCTNAME = "as15-40q"

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
    "E2_FAN":{"canreset":True,"list":[{"bus":72,"addr":0x50},{"bus":73,"addr":0x50},{"bus":74,"addr":0x50},{"bus":75,"addr":0x50},{"bus":76,"addr":0x50},{"bus":77,"addr":0x50}],"restartserv":"", "chk_list": 1},
    "E2_CPU":{"canreset":True,"list":[{"bus":16,"addr":0x50}],"restartserv":"","protect":{"bus":16, "devno":0x0d, "addr":0x51, "open":0x00, "close":0xff},},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":2,"addr":0x57}],"restartserv":"",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"", "protect": {"way":"gpio", "gpio_pin":874}},
    "E2_MAC":{"canreset":True,"list":[{"bus":2,"addr":0x51}],"restartserv":"","protect":{"bus":48, "devno":0x30, "addr":0xfc, "open":0x00, "close":0x01},},
    "E2_CLK":{"canreset":True,"list":[{"bus":81,"addr":0x50}],"restartserv":"","protect":{"bus":48, "devno":0x30, "addr":0xfc, "open":0x00, "close":0x10},},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":8,"addr":0x56}],"restartserv":"","protect":{"bus":8, "devno":0x0d, "addr":0xf0, "open":0x00, "close":0xff}},
}

ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-16/16-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'mac': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0051/eeprom', 'way': 'sysfs'},
              'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-8/8-0056/eeprom', 'way': 'sysfs'},
             }

DCDC_DEVICE = [ ]

CPLD_TEST = [
    {"name":"CPU CPLD", "bus": 16, "addr": 0x0D, "test_reg": 0x05, "slot": 0},
    {"name":"BASE CPLD", "bus": 0, "addr": 0x0D ,"test_reg": 0xf7, "slot": 1},
    {"name":"MAC CPLDA", "bus": 49,"addr": 0x31, "test_reg": 0x0f, "slot": 2},
    {"name":"MISC CPLD", "bus": 48, "addr": 0x30, "test_reg": 0x0f, "slot": 3},
    {"name":"FAN CPLD", "bus": 8, "addr": 0x0D, "test_reg": 0xf1, "slot": 4},
]

FPGA_TEST = [
    {"name":"FPGA", "bus": 5 ,"addr":0x32,"test_reg":0x74, "protect":{"bus": 5, "devno": 0x32, "addr": 0x70, "open": 0xbc, "close": 0x00}},
]

# add: 0不需要挂载， 1需要挂载；chip: 存在主备
SPI_TEST = [
    {"name": "bmc", "chip": "master", "cmd": "cat /proc/mtd | grep flash0 | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 0},
    {"name": "bmc", "chip": "slave", "cmd": "cat /proc/mtd | grep flashro | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 0},
    {"name": "bios", "chip": "master", "cmd": "cat /proc/mtd | grep BIOS | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 1},
    {"name": "bios", "chip": "slave", "cmd": "cat /proc/mtd | grep BIOS | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 1},
    {"name": "fpga", "cmd": "cat /proc/mtd | grep spi0.1 | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 1},
    {"name": "mac", "cmd": "cat /proc/mtd | grep spi0.1 | awk '{print $1}' | tr -d \":\" | xargs -I {} sh -c 'cat /sys/kernel/debug/mtd/{}/jedec_id'", "add": 1},
    {"name": "bcm53134", "cmd": "dumplog=$(hexdump /sys/bus/spi/devices/spi0.0/eeprom -n1);val=$?;echo $dumplog | awk 'NR==1{print $2}';exit $val", "add": 1},
]

CLOCK_TEST = {
    "bus": 80,
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
    "FRU_NUM": 18, "NO_FRU_NUM": 6, "H_FRU_NUM": 12, "PCIE_CHK_STR":"c1 06 06 00", "MAC_CORE_V": "MAC_CORE_V",
    "SML":[
        {"name": "SMB_PECI_WRITE", "bus": 18, "addr": 0x4c, "offset": 0x00},
        {"name": "SMB_PECI_READ", "bus": 18, "addr": 0x4b, "offset": 0x40},
        {"name": "SML0", "bus": 13, "addr": 0x16, "offset": 0x00},
        {"name": "SML1", "bus": 19, "addr": 0x48, "offset": 0x00},
    ],
    "CPLD_AVS": {"bus": 48, "devno": 0x30, "addr": 0x10},
    "CPU_PLATFORM": "ICELAKE",
    "CPU_CHK_LIST": ["OCM_VNN_PCH_V", "OCM_VNN_NAC_V"],
    "MIDO_REG_READ_TIMES": 80, "I2C_REG_READ_TIMES": 10, "SPI_ID_READ_TIMES": 1000,
    "DDR_STRESS": {"memtester_preset":"export MEMTESTER_TEST_MASK=$((1<<17));export MEMTESTER_TEST_RJ_MASK=$((1<<9));"},
    "TEST_CPU_GPIO_BY_SLOT": True,
}

MAC_THRESHOLD = {
    # The conversion value of the CPLD register value of MAC voltage
    # corresponds one-to-one with the range of voltage regulation difference
    "type": "non-fixed",
    #"map":{value1:[min1,max1],...,valuen:[minn,maxn]}
    "map":{
        0.8062 :[0,0.005],
        0.8000 :[0,0.005],
        0.7937 :[0,0.005],
        0.7876 :[0,0.005],
        0.7813 :[0,0.005],
        0.7751 :[0,0.005],
        0.7688 :[0,0.005],
        0.7625 :[0,0.005],
        0.7563 :[0,0.005],
        0.75   :[0,0.005],
        0.7439 :[0,0.005],
        0.7375 :[0,0.005],
        0.7314 :[0,0.005],
        0.7251 :[0,0.005],
        0.71875:[0,0.005],
        0.7126 :[0,0.005],
        0.7063 :[0,0.005],
        0.7002 :[0,0.005],
        0.6938 :[0,0.005],
        0.6875 :[0,0.005],
        0.6814 :[0,0.005],
        0.67505:[0,0.005],
        0.6689 :[0,0.005],
        0.6826 :[0,0.005],
        0.65625:[0,0.005],
        0.6501 :[0,0.005],
    }
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
        "as25-128q":[
        {"bus":70,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":71,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":72,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":73,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "as15-40q":[
            {"bus":56,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
            {"bus":57,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "droprecord_reg":{
        "bus":0,
        "addr":0x0d,
        "offset":0x49,
        "bitoffset":{ "PSU1":0, "PSU2":1},
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
    {"name":"BASE CPLD(0-000D)                          " ,"bus":0 ,"addr":0x0D},
    {"name":"CPU board CPLD(16-000d)                         " ,"bus":16 ,"addr":0x0d},
    {"name":"CPU board CPLD upgrade channel(14-0040)                 " ,"bus":16 ,"addr":0x40},
    {"name":"CPU board E2PROM(16-0050)                      " ,"bus":16 ,"addr":0x50},
    {"name":"CPU board UCD90160(17-005f)                    " ,"bus":17 ,"addr":0x5f},
    {"name":"CPU board VR power 1 XDPE12284C(17-005e)          " ,"bus":17 ,"addr":0x5e},
    {"name":"CPU board VR power 2 XDPE12284C(17-0068)          " ,"bus":17 ,"addr":0x68},
    {"name":"CPU board VR power 3 XDPE12284C(17-006e)          " ,"bus":17 ,"addr":0x6e},
    {"name":"CPU board VR power 4 XDPE12284C(17-0070)          " ,"bus":17 ,"addr":0x70},
    # {"name":"CPU RC32504A(17-0009)                      " ,"bus":17 ,"addr":0x09},
    {"name":"SMB_PECI_WRITE(18-004C)                    " ,"bus":18 ,"addr":0x4c},
    {"name":"SMB_PECI_READ(18-004B)                     " ,"bus":18 ,"addr":0x4b, "reg":0x40},
    {"name":"SML0(13-0016)                              " ,"bus":13 ,"addr":0x16},
    {"name":"SML1(19-0048)                              " ,"bus":19 ,"addr":0x48},
    {"name":"BMC board EEPROM(2-0053)                       " ,"bus":2 ,"addr":0x53},
    {"name":"BASE board EEPROM(2-0057)                      " ,"bus":2 ,"addr":0x57},
    {"name":"MAC board EEPROM(2-0051)                      " ,"bus":2 ,"addr":0x51},
    {"name":"BASE board RTC channel(3-0051)                     " ,"bus":3 ,"addr":0x51},
    {"name":"BASE board voltage/current monitoring 1(INA3221)(30-0041)     " ,"bus":24, "addr":0x41},
    {"name":"BASE board voltage/current monitoring 2(INA3221)(31-0041)     " ,"bus":25, "addr":0x41},
    {"name":"BASE board voltage/current monitoring 3(INA3221)(32-0041)     " ,"bus":26, "addr":0x41},
    {"name":"BASE board voltage/current monitoring 4(INA3221)(33-0041)     " ,"bus":27, "addr":0x41},
    {"name":"XDPE132G5D(32-0060)                        " ,"bus":32 ,"addr":0x60},
    {"name":"XDPE12284C(33-0060)                        " ,"bus":33 ,"addr":0x60},
    {"name":"XDPE12284C(34-0060)                        " ,"bus":34 ,"addr":0x60},
    {"name":"XDPE12284C(35-0060)                        " ,"bus":35 ,"addr":0x60},
    {"name":"MAC board voltage/current monitoring 0(INA3221)(54-0040)     " ,"bus":40 ,"addr":0x40},
    {"name":"MAC board voltage/current monitoring 1(INA3221)(55-0040)     " ,"bus":41 ,"addr":0x40},
    {"name":"MAC board voltage/current monitoring 2(INA3221)(56-0040)     " ,"bus":42 ,"addr":0x40},
    {"name":"MAC board voltage/current monitoring 3(INA3221)(57-0040)     " ,"bus":43 ,"addr":0x40},
    {"name":"MAC board voltage/current monitoring 4(INA3221)(58-0040)     " ,"bus":44 ,"addr":0x40},
    {"name":"BMC accesses FPGA channel (5-0032)                    " ,"bus":5 ,"addr":0x32},
    {"name":"MAC board MISC CPLD(48-0030)                    " ,"bus":48 ,"addr":0x30},
    {"name":"MAC board CPLD upgrade channel(48-0040)                 " ,"bus":48 ,"addr":0x40},
    {"name":"MAC board CPLD1(49-0031)                        " ,"bus":49 ,"addr":0x31},
    {"name":"MAC board CPLD1 upgrade channel(49-0040)                " ,"bus":49 ,"addr":0x40},
    {"name":"PSU1 PMBUS(56-0058)                        " ,"bus":56 ,"addr":0x58},
    # {"name":"PSU1 FRU(56-0050)                        " ,"bus":56 ,"addr":50},
    {"name":"PSU2 PMBUS(57-0058)                        " ,"bus":57,"addr":0x58},
    # {"name":"PSU2 FRU(57-0050)                        " ,"bus":57,"addr":0x50},
    {"name":"TD5 BSC2 channel (7-0044)                       " ,"bus":7 ,"addr":0x44},
    {"name":"MAC TMP275 top layer air inlet(64-0048)                      " ,"bus":64 ,"addr":0x48},
    {"name":"MAC TMP275 hottest spot on board(65-0049)                    " ,"bus":65 ,"addr":0x49},
    {"name":"MAC TMP275 bottom layer air inlet(66-004b)                   " ,"bus":66 ,"addr":0x4b},
    # {"name":"MAC TMP411(67-004c)                      " ,"bus":67 ,"addr":0x4c},
    # {"name":"MAC TMP411(68-004c)                      " ,"bus":68 ,"addr":0x4c},
    {"name":"FCB board E2PROM(8-0056)                      " ,"bus":8 ,"addr":0x56},
    {"name":"FCB board CPLD(8-000d)                         " ,"bus":8 ,"addr":0x0d},
    # 1, 表示：风冷设备独有，非风冷设备需要屏蔽
    {"name":"Fan module_1 E2PROM(72-0050)                 " ,"bus":72 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"Fan module_2 E2PROM(73-0050)                 " ,"bus":73 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"Fan module_3 E2PROM(74-0050)                 " ,"bus":74 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"Fan module_4 E2PROM(75-0050)                 " ,"bus":75 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"Fan module_5 E2PROM(76-0050)                 " ,"bus":76 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"Fan module_5 E2PROM(77-0050)                 " ,"bus":77 ,"addr":0x50,"scan_shielde_capacity": 1},
    {"name":"FCB board TMP275(78-0049)                      " ,"bus":78 ,"addr":0x49},
    {"name":"FCB board TMP275(79-0048)                      " ,"bus":79 ,"addr":0x48},
    {"name":"MAC board CLOCK(80-0009)                      " ,"bus":80 ,"addr":0x09},
    {"name":"MAC board CLOCK E2PROM(81-0050)              " ,"bus":80 ,"addr":0x50},
]

EQUIPMENT_AB_MAP = {"v0": "A", "v1": "B"}

POWER_FW_VER = [
    # {"name": xxx, "bus": xxx, "addr": xxx, "offset": xxx, "page": {"bus": xxx, "addr": xxx, "offset": xxx, "val": xxx}},
    # The default value is provided by I2C_SCAN_LIST. 
    # Paging switching information does not necessarily require.
    {"name": "XDPE12284C", "offset": 0x3f, "page": {"offset":0x00, "val": 0x22, "rval": 0x00}},
    {"name": "XDPE132G5D", "offset": 0x7a, "extra": "A"},
    {"name": "RAA228248", "offset": 0xae, "extra": "B"},
    {"name": "ISL69260", "offset": 0xae, "extra": "B"},
]

MULTIPLE_POWER_EXCEPTIONS = {
    "i2c_common": {
        "reg_common": {
                "STATUS_WORD":          {"offset": 0x79,  "data_change_mode": "READ_16_bit"},
                "STATUS_VOUT":          {"offset": 0x7a,  "data_change_mode": "JUDGE_SOME_bit"},
                "STATUS_IOUT":          {"offset": 0x7b,  "data_change_mode": "JUDGE_SOME_bit"},
                "STATUS_INPUT":         {"offset": 0x7c,  "data_change_mode": "READ_8_bit"},
                "STATUS_TEMPERATURE":   {"offset": 0x7d,  "data_change_mode": "JUDGE_SOME_bit"},
                "STATUS_CML":           {"offset": 0x7e,  "data_change_mode": "READ_8_bit"},
                "STATUS_MFR_SPECIFIC":  {"offset": 0x80,  "data_change_mode": "JUDGE_SOME_bit"},
        },
        "dev_common": {
            #"DeviceName": [
            #     --缺省值从reg_common获取
            #       mask/check未配置，则无需校验；offset/data_change_mode缺省，并且reg_common无配置，则报错
            #    {"name": "xxx", "reg": {"offset": xxx, "data_change_mode": xxx}, "mask": xxx, "check": xxx},
            #    {"name": "yyy", "reg": {"offset": yyy, "data_change_mode": yyy}},
            #    {"name": "zzz"},
            #],
            "XDPE132G5D": [
                {"name": "STATUS_WORD"},
                {"name": "STATUS_VOUT",         "mask": 0x90, "check": 0x00},
                {"name": "STATUS_IOUT",         "mask": 0xa0, "check": 0x00},
                {"name": "STATUS_INPUT"},
                {"name": "STATUS_TEMPERATURE",  "mask": 0xc0, "check": 0x00},
                {"name": "STATUS_CML"},
                {"name": "STATUS_MFR_SPECIFIC", "mask": 0xc1, "check": 0x00},
            ],
            "XDPE12284C": [
                {"name": "STATUS_WORD"},
                {"name": "STATUS_VOUT",         "mask": 0x90, "check": 0x00},
                {"name": "STATUS_IOUT",         "mask": 0xa0, "check": 0x00},
                {"name": "STATUS_INPUT"},
                {"name": "STATUS_TEMPERATURE",  "mask": 0xc0, "check": 0x00},
                {"name": "STATUS_CML"},
                {"name": "STATUS_MFR_SPECIFIC", "mask": 0x02, "check": 0x00},
            ],
            "RAA228248": [
                {"name": "STATUS_WORD"},
                {"name": "STATUS_VOUT",         "mask": 0x90, "check": 0x00},
                {"name": "STATUS_IOUT",         "mask": 0xb8, "check": 0x00},
                {"name": "STATUS_INPUT"},
                {"name": "STATUS_TEMPERATURE",  "mask": 0x90, "check": 0x00},
                {"name": "STATUS_CML"},
                {"name": "STATUS_MFR_SPECIFIC", "reg": {"offset": 0x80,  "data_change_mode": "READ_8_bit"}},
            ],
            "ISL69260": [
                {"name": "STATUS_WORD"},
                {"name": "STATUS_VOUT",         "mask": 0x90,   "check": 0x00},
                {"name": "STATUS_IOUT",         "mask": 0xb8,   "check": 0x00},
                {"name": "STATUS_INPUT"},
                {"name": "STATUS_TEMPERATURE",  "mask": 0x90,   "check": 0x00},
                {"name": "STATUS_CML"},
                {"name": "STATUS_MFR_SPECIFIC", "reg": {"offset": 0x80,  "data_change_mode": "READ_8_bit"}},
            ],
        },
        "page_common": {
            "page_list": [
                {"name": "page0",   "offset": 0x00, "val": 0x00},
                {"name": "page1",   "offset": 0x00, "val": 0x01, "rval": 0x00}
            ],
        },
    },
    "sysfs_common": {
        "path_common": {
            "READ_IIN":           "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/curr1_input",
            "READ_PIN":           "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/power1_input",
            "READ_VIN":           "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/in1_input",
            "READ_TEMPERATURE_1": "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/temp1_input",
            "READ_POUT_P0":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/power2_input",
            "READ_POUT_P1":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/power3_input",
            "READ_IOUT_P0":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/curr2_input",
            "READ_IOUT_P1":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/curr3_input",
            "READ_VOUT_P0":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/in2_input",
            "READ_VOUT_P1":       "/sys/bus/i2c/devices/{}-00{}/hwmon/hwmon*/in3_input",
        },
        "dev_common": {
            #"DeviceName": [
            #     --缺省值从path_common获取，缺省并且path_common获取不到，则报错
            #    {"name": "xxx", "path": xxx, "unit": xxx},
            #    {"name": "yyy"},
            #],
            "XDPE132G5D": [
                {"name": "READ_IIN"}, {"name": "READ_PIN"}, {"name": "READ_VIN"}, {"name": "READ_TEMPERATURE_1"},
                {"name": "READ_POUT_P0"}, {"name": "READ_POUT_P1"}, {"name": "READ_IOUT_P0"},
                {"name": "READ_IOUT_P1"}, {"name": "READ_VOUT_P0"}, {"name": "READ_VOUT_P1"},
            ],
            "XDPE12284C": [
                {"name": "READ_IIN"}, {"name": "READ_PIN"}, {"name": "READ_VIN"}, {"name": "READ_TEMPERATURE_1"},
                {"name": "READ_POUT_P0"}, {"name": "READ_POUT_P1"}, {"name": "READ_IOUT_P0"},
                {"name": "READ_IOUT_P1"}, {"name": "READ_VOUT_P0"}, {"name": "READ_VOUT_P1"},
            ],
            "RAA228248": [
                {"name": "READ_IIN"}, {"name": "READ_PIN"}, {"name": "READ_VIN"}, {"name": "READ_TEMPERATURE_1"},
                {"name": "READ_POUT_P0"}, {"name": "READ_POUT_P1"}, {"name": "READ_IOUT_P0"},
                {"name": "READ_IOUT_P1"}, {"name": "READ_VOUT_P0"}, {"name": "READ_VOUT_P1"},
            ],
            "ISL69260": [
                {"name": "READ_IIN"}, {"name": "READ_PIN"}, {"name": "READ_VIN"}, {"name": "READ_TEMPERATURE_1"},
                {"name": "READ_POUT_P0"}, {"name": "READ_POUT_P1"}, {"name": "READ_IOUT_P0"},
                {"name": "READ_IOUT_P1"}, {"name": "READ_VOUT_P0"}, {"name": "READ_VOUT_P1"},
            ],
        }
    },
    "dev_list": [
        # {
        #   "name": "xxx", "bus": xxx, "addr": xxx, "extra": xxx,   --如果没有extra,则无条件检查
        #   "i2c": { -- 缺省则，下述list都将从common获取
        #       "page_list": [ --缺省则从common获取
        #           {"name": "xxx", "offset": xxx, "val": xxx, "rval": xxx},
        #           {"name": "yyy", "offset": yyy, "val": yyy}, --rval如果是默认分页0，则不用配置
        #       ],
        #       "reg_list": [
        #           --缺省则从common对应获取，一旦自定义，则不查询common
        #           --自定义：
        #               mask/check未配置，则无需校验
        #               offset/data_change_mode缺省，则报错
        #           {"name": "xxx", "reg": {"offset": xxx, "data_change_mode": xxx}, "mask": xxx, "check": xxx},
        #           {"name": "yyy", "reg": {"offset": yyy, "data_change_mode": yyy}},
        #       ],
        #   },
        #   "sysfs": [
        #       --缺省则直接从common获取，一旦自定义，则不查询common
        #       --自定义：
        #       {"name": "xxx", "path": "xxx", "unit": "xxx"},
        #       {"name": "yyy", "path": "yyy", "unit": "yyy"},
        #   ],
        # },
        {"name": "XDPE132G5D", "bus": 38, "addr": 0x40, "extra": "A", "i2c":
            {"page_list": [{"name": "page0", "offset": 0x00, "val": 0x00}]}
        },
        {"name": "XDPE132G5D", "bus": 39, "addr": 0x40, "extra": "A"},
        {"name": "XDPE132G5D", "bus": 40, "addr": 0x40, "extra": "A",},
        {"name": "XDPE12284C", "bus": 15, "addr": 0x5e, "i2c":
            {"page_list": [{"name": "page0", "offset": 0x00, "val": 0x00}]}
        },
        {"name": "XDPE12284C", "bus": 15, "addr": 0x68},
        {"name": "XDPE12284C", "bus": 15, "addr": 0x6e},
        {"name": "XDPE12284C", "bus": 15, "addr": 0x70},
        {"name": "XDPE12284C", "bus": 41, "addr": 0x58, "extra": "A"},
        {"name": "XDPE12284C", "bus": 42, "addr": 0x58, "extra": "A"},
        {"name": "XDPE12284C", "bus": 48, "addr": 0x58, "extra": "A"},
        {"name": "RAA228248",  "bus": 38, "addr": 0x60, "extra": "B", "i2c":
            {"page_list": [{"name": "page0", "offset": 0x00, "val": 0x00}]}
        },
        {"name": "RAA228248",  "bus": 39, "addr": 0x60, "extra": "B"},
        {"name": "RAA228248",  "bus": 40, "addr": 0x60, "extra": "B"},
        {"name": "ISL69260",   "bus": 41, "addr": 0x60, "extra": "B"},
        {"name": "ISL69260",   "bus": 42, "addr": 0x60, "extra": "B"},
        {"name": "ISL69260",   "bus": 48, "addr": 0x60, "extra": "B"},
    ],
}

ECC_ERR_INFO = {
    "reg_info": {"addr": 0x1e6e0050, "way": "devmem", "digit":32},
    "check_list": [
        {"name": "ECC recoverable error counter", "offset": 16, "mask": 0xff, "chk": 0},
        {"name": "ECC un-recoverable error counter", "offset": 12, "mask": 0xf, "chk": 0},
    ]
}

LED_INFO ={
    "sysleds":{
        "attrs":OrderedDict([("light-off", 0), ("green-light-blinking", 5),("green-light-on", 1),("yellow-light-blinking", 6),("backing-off", 0),]),
        "bus":0,
        "addr":0X0D,
        "way": "sysfs",
        "name":"Front panel sys, pwr, fan LED",
        "device":[
            {"loc":"/sys/s3ip/sysled/sys_led_status"},
            {"loc":"/sys/s3ip/sysled/psu_led_status"},
            {"loc":"/sys/s3ip/sysled/fan_led_status"}, #风冷 sysfan灯 (Bit4 1：软件控制点灯)
        ]
    },
    "fanleds":{
        "attrs":OrderedDict([("light-off", 0),("green-light-blinking", 5),("green-light-on", 1),("yellow-light-blinking", 6),("yellow-light-on", 2),("backing-off", 0)]),
        "bus":8,
        "addr":0X0D,
        "name":"Fan light",
        "way": "sysfs",
        "device":[
            # 液冷设备相对于风冷，少两个风扇（FAN1 FAN2）
            {"loc":"/sys/s3ip/fan/fan1/led_status"},
            {"loc":"/sys/s3ip/fan/fan2/led_status"},
            {"loc":"/sys/s3ip/fan/fan3/led_status"},
            {"loc":"/sys/s3ip/fan/fan4/led_status"},
            {"loc":"/sys/s3ip/fan/fan5/led_status"},
            {"loc":"/sys/s3ip/fan/fan6/led_status"},
        ]
    },
    "location_led":{
        "attrs":OrderedDict([("bit-stream-on",0X98),("green-light-blinking",0x83),("green-light-on",0x84),("yellow-light-blinking",0x85),("yellow-light-on",0x86),("backing-bit-stream-on",0X98)]),
        "bus":5,
        "addr":0x32,
        "name":"location LED",
        "device":[
            {"reg":0x40},
            {"reg":0x44},
            {"reg":0x48},
            {"reg":0x4c},
        ]
    }
}

FAN_SPEED = {
    "speedlevel":{
        "high":{
            "value":255,"low_threshhold":16000,"high_threshhold":40000},
        "middle":{
            "value":150,"low_threshhold":10000,"high_threshhold":21000},
        "low":{
            "value":102,"low_threshhold":500,"high_threshhold":14000},
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

    ],
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
        "s3ip": 1,
        "path": {
                "FAN1": "/sys/s3ip/fan/fan1/present",
                "FAN2": "/sys/s3ip/fan/fan2/present",
                "FAN3": "/sys/s3ip/fan/fan3/present",
                "FAN4": "/sys/s3ip/fan/fan4/present",
                "FAN5": "/sys/s3ip/fan/fan5/present",
                "FAN6": "/sys/s3ip/fan/fan6/present",
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

MAC_VOUT_EXPONENT = {
    "0x18": -8,
    "0x17": -9,
    "0x16": -10,
    "0x15": -11,
    "0x14": -12,
}

MAC_VOUT_MAP = {
    0x81: 0.8062,
    0x82: 0.8000,
    0x83: 0.7937,
    0x84: 0.7876,
    0x85: 0.7813,
    0x86: 0.7751,
    0x87: 0.7688,
    0x88: 0.7625,
    0x89: 0.7563,
    0x8A: 0.75,
    0x8b: 0.7439,
    0x8c: 0.7375,
    0x8d: 0.7314,
    0x8e: 0.7251,
    0x8f: 0.71875,
    0x90: 0.7126,
    0x91: 0.7063,
    0x92: 0.7002,
    0x93: 0.6938,
    0x94: 0.6875,
    0x95: 0.6814,
    0x96: 0.67505,
    0x97: 0.6689,
    0x98: 0.6826,
    0x99: 0.65625,
    0x9a: 0.6501,
}
