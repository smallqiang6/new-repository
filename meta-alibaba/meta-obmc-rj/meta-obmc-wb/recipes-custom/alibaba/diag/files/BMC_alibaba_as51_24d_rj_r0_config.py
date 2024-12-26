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

RUIJIE_CARDID      = 0x00004090
RUIJIE_PRODUCTNAME = "as51-24d"

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
    {"bus":8, "devno":0x0d, "addr":0x46}], "open":0x00, "close":0xff}

E2_DEV = {
    "E2_FAN":{"canreset":True,"list":[{"bus":102,"addr":0x50},{"bus":103,"addr":0x50},{"bus":104,"addr":0x50}],"restartserv":"",},
    "E2_CPU":{"canreset":True,"list":[{"bus":14,"addr":0x50}],"restartserv":"","protect":{"bus":14, "devno":0x0d, "addr":0x51, "open":0x00, "close":0xff},},
    "E2_PSU":{"canreset":True,"list":[{"bus":94,"addr":0x50},{"bus":95,"addr":0x50}],"restartserv":"","extra":"-F-",},
    "E2_SYSFRU":{"canreset":True,"list":[{"bus":2,"addr":0x57}],"restartserv":"",},
    "E2_BMC":{"canreset":True,"list":[{"bus":2,"addr":0x53}],"restartserv":"",},
    "E2_SWITCH":{"canreset":True,"list":[{"bus":2,"addr":0x51}],"restartserv":"",},
    "E2_FANBOARD":{"canreset":True,"list":[{"bus":8,"addr":0x56}],"restartserv":"","protect":{"bus":8, "devno":0x0d, "addr":0xf0, "open":0x00, "close":0xff}},
}

ALI_E2_DEV = {'cpu': {'loc': '/sys/bus/i2c/devices/i2c-14/14-0050/eeprom', 'way': 'sysfs'},
              'sysfru': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
              'bmc': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0053/eeprom', 'way': 'sysfs'},
              'switch': {'loc': '/sys/bus/i2c/devices/i2c-2/2-0051/eeprom', 'way': 'sysfs'},
              'fanboard': {'loc': '/sys/bus/i2c/devices/i2c-8/8-0056/eeprom', 'way': 'sysfs'},
             }

DCDC_DEVICE = [ ]

CPLD_TEST = [
    {"name":"BASE CPLD", "bus": 0, "addr": 0x0D ,"test_reg": 0xaa},
    {"name":"CPU CPLD", "bus": 14, "addr": 0x0D, "test_reg": 0x05},
    {"name":"FAN CPLD", "bus": 8, "addr": 0x0D, "test_reg": 0xf1},
    {"name":"MISC CPLD", "bus": 86, "addr": 0x30, "test_reg": 0x0f},
    {"name":"SWITCH CPLDA", "bus": 87,"addr": 0x30, "test_reg": 0x0f},
    {"name":"SWITCH CPLDB", "bus": 88,"addr": 0x30, "test_reg": 0x0f},
]

FPGA_TEST = [
    {"name":"FPGA", "bus": 5 ,"addr":0x70,"test_reg":0x74, "protect":{"bus": 5, "devno": 0x70, "addr": 0x70, "open": 0xbc, "close": 0x00}},
]

# add: 0不需要挂载， 1需要挂载；chip: 存在主备
SPI_TEST = [
    {"name": "bmc", "chip": "master", "cmd": "cat /sys/bus/spi/devices/spi0.0/jedec_id", "add": 0},
    {"name": "bmc", "chip": "slave", "cmd": "cat /sys/bus/spi/devices/spi0.1/jedec_id", "add": 0},
    {"name": "bios", "chip": "master", "cmd": "cat /sys/bus/spi/devices/spi1.0/jedec_id", "add": 1},
    {"name": "bios", "chip": "slave", "cmd": "cat /sys/bus/spi/devices/spi1.0/jedec_id", "add": 1},
    {"name": "fpga", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "atlas0", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "atlas1", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "rtl8372", "cmd": "cat /sys/bus/spi/devices/spi2.1/jedec_id", "add": 1},
    {"name": "bcm53134", "cmd": "dumplog=$(hexdump /sys/bus/spi/devices/spi2.0/eeprom -n1);val=$?;echo $dumplog | awk 'NR==1{print $2}';exit $val", "add": 1},
]

ALI_BMC = {"FRU_NUM": 12, "NO_FRU_NUM": 5, "PCIE_CHK_STR":"40 c1 06 06 00", "IS_SUPPORT_MAC": 0,
            "SML":[{"name": "SMB_PECI_WRITE", "bus": 16, "addr": 0x4c, "offset": 0x00},
                    {"name": "SMB_PECI_READ", "bus": 16, "addr": 0x4b, "offset": 0x40},
                    {"name": "SML0", "bus": 13, "addr": 0x16, "offset": 0x00},
                    {"name": "SML1", "bus": 17, "addr": 0x48, "offset": 0x00},
            ],
            "CPU_PLATFORM": "ICELAKE",
            "CPU_CHK_LIST": ["OCM_VNN_PCH_V", "OCM_VNN_NAC_V"],
            "MIDO_REG_READ_TIMES": 80, "I2C_REG_READ_TIMES": 10, "SPI_ID_READ_TIMES": 1000,
            "DDR_STRESS": {"memtester_preset":"export MEMTESTER_TEST_MASK=$((1<<17));export MEMTESTER_TEST_RJ_MASK=$((1<<9));"},
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
        "as51-24d":[
        {"bus":94,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        {"bus":95,"addr":0x58,"e2addr":0x50,"attrs":{"curr1_input":"mA","curr2_input":"mA","in1_input":"mV","in2_input":"mV","power1_input":"mW","power2_input":"mW"}},
        ],
        "droprecord_reg":{
        "bus":0,
        "addr":0x0d,
        "offset":0x57,
        "bitoffset":{ "PSU1":0, "PSU2":1},
        },
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
    {"name":"BASE板CPLD升级通路(0-0040)                 " ,"bus":0 ,"addr":0x40},
    {"name":"BASE CPLD(0-000D)                          " ,"bus":0 ,"addr":0x0D},
    {"name":"CPU板CPLD(14-000d)                         " ,"bus":14 ,"addr":0x0d},
    {"name":"CPU板CPLD升级通道(14-0040)                 " ,"bus":14 ,"addr":0x40},
    {"name":"CPU板 E2PROM(14-0050)                      " ,"bus":14 ,"addr":0x50},
    {"name":"CPU板 UCD90160(15-005f)                    " ,"bus":15 ,"addr":0x5f},
    {"name":"CPU板 VR电源1 XDPE12284C(15-005e)          " ,"bus":15 ,"addr":0x5e},
    {"name":"CPU板 VR电源2 XDPE12284C(15-0068)          " ,"bus":15 ,"addr":0x68},
    {"name":"CPU板 VR电源3 XDPE12284C(15-006e)          " ,"bus":15 ,"addr":0x6e},
    {"name":"CPU板 VR电源4 XDPE12284C(15-0070)          " ,"bus":15 ,"addr":0x70},
    # 预留，实际未挂载
    #{"name":"CPU板RC32504A(15-009a)                     " ,"bus":15 ,"addr":0x9a},
    {"name":"SMB_PECI_WRITE(16-004c)                    " ,"bus":16 ,"addr":0x4c},
    {"name":"SMB_PECI_READ(16-004b)                     " ,"bus":16 ,"addr":0x4b, "reg":0x40},
    {"name":"SML0(13-0016)                              " ,"bus":13 ,"addr":0x16},
    {"name":"SML1(17-0048)                              " ,"bus":17 ,"addr":0x48},
    {"name":"BMC板 EEPROM(2-0053)                       " ,"bus":2 ,"addr":0x53},
    {"name":"BASE板 EEPROM(2-0057)                      " ,"bus":2 ,"addr":0x57},
    {"name":"ISW Switch板EEPROM(2-0051)                 " ,"bus":2 ,"addr":0x51},
    {"name":"RTL8372(2-005c)                            " ,"bus":2 ,"addr":0x5c},
    # 22-57对应外部插槽，地址需根据实际插的设备定，先不测试
    # {"name":"PEX0 ASM0A I2C(22-0070)                    " ,"bus":22 ,"addr":0x70},
    # {"name":"PEX0 ASM0B I2C(23-0070)                    " ,"bus":23 ,"addr":0x70},
    # {"name":"PEX0 ASM1A I2C(24-0070)                    " ,"bus":24 ,"addr":0x70},
    # {"name":"PEX0 ASM1B I2C(25-0070)                    " ,"bus":25 ,"addr":0x70},
    # {"name":"PEX0 ASM2A I2C(26-0070)                    " ,"bus":26 ,"addr":0x70},
    # {"name":"PEX0 ASM2B I2C(27-0070)                    " ,"bus":27 ,"addr":0x70},
    # {"name":"PEX0 ASM3A I2C(28-0070)                    " ,"bus":28 ,"addr":0x70},
    # {"name":"PEX0 ASM3B I2C(29-0070)                    " ,"bus":29 ,"addr":0x70},
    # {"name":"PEX0 ASM4A I2C(30-0071)                    " ,"bus":30 ,"addr":0x71},
    # {"name":"PEX0 ASM4B I2C(31-0071)                    " ,"bus":31 ,"addr":0x71},
    # {"name":"PEX0 ASM5A I2C(32-0071)                    " ,"bus":32 ,"addr":0x71},
    # {"name":"PEX0 ASM5B I2C(33-0071)                    " ,"bus":33 ,"addr":0x71},
    # {"name":"PEX0 ASM6A I2C(34-0071)                    " ,"bus":34 ,"addr":0x71},
    # {"name":"PEX0 ASM6B I2C(35-0071)                    " ,"bus":35 ,"addr":0x71},
    # {"name":"PEX0 ASM7A I2C(36-0071)                    " ,"bus":36 ,"addr":0x71},
    # {"name":"PEX0 ASM7B I2C(37-0071)                    " ,"bus":37 ,"addr":0x71},
    # {"name":"PEX0 ASM8A I2C(38-0072)                    " ,"bus":38 ,"addr":0x72},
    # {"name":"PEX0 ASM8B I2C(39-0072)                    " ,"bus":39 ,"addr":0x72},
    # {"name":"PEX1 ASM0A I2C(40-0072)                    " ,"bus":40 ,"addr":0x72},
    # {"name":"PEX1 ASM0B I2C(41-0072)                    " ,"bus":41 ,"addr":0x72},
    # {"name":"PEX1 ASM1A I2C(42-0072)                    " ,"bus":42 ,"addr":0x72},
    # {"name":"PEX1 ASM1B I2C(43-0072)                    " ,"bus":43 ,"addr":0x72},
    # {"name":"PEX1 ASM2A I2C(44-0072)                    " ,"bus":44 ,"addr":0x72},
    # {"name":"PEX1 ASM2B I2C(45-0072)                    " ,"bus":45 ,"addr":0x72},
    # {"name":"PEX1 ASM3A I2C(46-0073)                    " ,"bus":46 ,"addr":0x73},
    # {"name":"PEX1 ASM3B I2C(47-0073)                    " ,"bus":47 ,"addr":0x73},
    # {"name":"PEX1 ASM4A I2C(48-0073)                    " ,"bus":48 ,"addr":0x73},
    # {"name":"PEX1 ASM4B I2C(49-0073)                    " ,"bus":49 ,"addr":0x73},
    # {"name":"PEX1 ASM5A I2C(50-0073)                    " ,"bus":50 ,"addr":0x73},
    # {"name":"PEX1 ASM5B I2C(51-0073)                    " ,"bus":51 ,"addr":0x73},
    # {"name":"PEX1 ASM6A I2C(52-0073)                    " ,"bus":52 ,"addr":0x73},
    # {"name":"PEX1 ASM6B I2C(53-0073)                    " ,"bus":53 ,"addr":0x73},
    # {"name":"PEX1 ASM7A I2C(54-0074)                    " ,"bus":54 ,"addr":0x74},
    # {"name":"PEX1 ASM7B I2C(55-0074)                    " ,"bus":55 ,"addr":0x74},
    # {"name":"PEX1 ASM8A I2C(56-0074)                    " ,"bus":56 ,"addr":0x74},
    # {"name":"PEX1 ASM8B I2C(57-0074)                    " ,"bus":57 ,"addr":0x74},
    {"name":"PCIE_SLOT1 I2C(62-0075)                    " ,"bus":62 ,"addr":0x75},
    {"name":"PCIE_SLOT2 I2C(63-0075)                    " ,"bus":63 ,"addr":0x75},
    {"name":"PCIE_SLOT3 I2C(64-0075)                    " ,"bus":64 ,"addr":0x75},
    {"name":"PCIE_SLOT4 I2C(65-0075)                    " ,"bus":65 ,"addr":0x75},
    {"name":"PCIE_SLOT5 I2C(66-0075)                    " ,"bus":66 ,"addr":0x75},
    {"name":"PCIE_SLOT6 I2C(67-0075)                    " ,"bus":67 ,"addr":0x75},
    {"name":"BASE板 RTC通道(3-0051)                     " ,"bus":3 ,"addr":0x51},
    {"name":"BASE板 电压电流监控1(INA3221)(70-0041)     " ,"bus":70 ,"addr":0x41},
    {"name":"BASE板 电压电流监控2(INA3221)(71-0041)     " ,"bus":71 ,"addr":0x41},
    {"name":"BASE板 电压电流监控3(INA3221)(72-0041)     " ,"bus":72 ,"addr":0x41},
    {"name":"BASE板 电压电流监控4(INA3221)(73-0041)     " ,"bus":73 ,"addr":0x41},
    {"name":"SWITCH板 电压电流监控0(INA3221)(78-0040)  " ,"bus":78 ,"addr":0x40},
    {"name":"SWITCH板 电压电流监控1(INA3221)(79-0040)  " ,"bus":79 ,"addr":0x40},
    {"name":"SWITCH板 电压电流监控2(INA3221)(80-0040)  " ,"bus":80 ,"addr":0x40},
    {"name":"XDPE12284C(84-0068)                        " ,"bus":84 ,"addr":0x68},
    {"name":"XDPE12284C(85-0068)                        " ,"bus":85 ,"addr":0x68},
    {"name":"BMC访问FPGA通道(5-0070)                    " ,"bus":5 ,"addr":0x70},
    {"name":"Switch板MISC CPLD(86-0030)                 " ,"bus":86 ,"addr":0x30},
    {"name":"Switch板CPLD1(87-0030)                     " ,"bus":87 ,"addr":0x30},
    {"name":"Switch板CPLD2(88-0030)                     " ,"bus":88 ,"addr":0x30},
    {"name":"PSU1 PMBUS(94-0058)                        " ,"bus":94 ,"addr":0x58},
    {"name":"PSU1 EEPROM(94-0050)                       " ,"bus":94 ,"addr":0x50},
    {"name":"PSU2 PMBUS(95-0058)                        " ,"bus":95 ,"addr":0x58},
    {"name":"PSU2 EEPROM(95-0050)                       " ,"bus":95 ,"addr":0x50},
    {"name":"TMP275(98-0048)                            " ,"bus":98 ,"addr":0x48},
    {"name":"Switch板TMP275 0(7-0048)                   " ,"bus":7 ,"addr":0x48},
    {"name":"Switch板TMP275 1(7-0049)                   " ,"bus":7 ,"addr":0x49},
    {"name":"Switch板TMP275 2(7-004b)                   " ,"bus":7 ,"addr":0x4b},
    {"name":"FCB板 CPLD(8-000d)                         " ,"bus":8 ,"addr":0x0d},
    {"name":"FCB板 EEPROM(8-0056)                       " ,"bus":8 ,"addr":0x56},
    {"name":"风扇模组_1 E2PROM(102-0050)                " ,"bus":102 ,"addr":0x50},
    {"name":"风扇模组_2 E2PROM(103-0050)                " ,"bus":103 ,"addr":0x50},
    {"name":"风扇模组_3 E2PROM(104-0050)                " ,"bus":104 ,"addr":0x50},
    {"name":"FCB板 TMP275(107-0049)                     " ,"bus":107 ,"addr":0x49},
    {"name":"FCB板 TMP275(108-0048)                     " ,"bus":108 ,"addr":0x48},
    # 预留，实际未挂载
    # {"name":"PEX0_I2C_S(110-0070)                       " ,"bus":110 ,"addr":0x70},
    # {"name":"PEX0_I2C_0(111-0070)                       " ,"bus":111 ,"addr":0x70},
    # {"name":"PEX1_I2C_S(112-0070)                       " ,"bus":112 ,"addr":0x70},
    # {"name":"PEX1_I2C_0(113-0070)                       " ,"bus":113 ,"addr":0x70},
    # {"name":"RC21012(118-0009)                          " ,"bus":118 ,"addr":0x09},
    # {"name":"RC19008(119-0067)                          " ,"bus":119 ,"addr":0x67},
    # {"name":"RC19008(120-0067)                          " ,"bus":120 ,"addr":0x67},
    # {"name":"RC19008(121-0067)                          " ,"bus":121 ,"addr":0x67},
    # {"name":"RC19008(122-0067)                          " ,"bus":122 ,"addr":0x67},
    # {"name":"RC19008(123-0067)                          " ,"bus":123 ,"addr":0x67},
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
            {"reg":0x08, "bus":8, "addr":0X0D}, #风冷 sysfan灯 (Bit4 1：软件控制点灯)
        ]
    },
    "fanleds":{
        "attrs":OrderedDict([("light-off",0X0b),("red-light-blinking",0x0e),("red-light-on",0x0a),("green-light-blinking",0x0d),("green-light-on",0x09),("yellow-light-blinking",0x07),("yellow-light-on",0x03),("backing-off",0X0b)]),
        "bus":8,
        "addr":0X0D,
        "name":"风扇灯",
        "device":[
            {"reg":0x25},
            {"reg":0x35},
            {"reg":0x45},
        ]
    },
}

FAN_SPEED = {
        "speedlevel":{"high":{"value":255,"low_threshhold":12000,"high_threshhold":20000},
                      "middle":{"value":150,"low_threshhold":7000,"high_threshhold":12000},
                      "low":{"value":102,"low_threshhold":5000,"high_threshhold":9000},
        },
        "bus":8,
        "addr":0X0D,
        "watchdogreg":0x0C,
        "waittime":8,
        "device":[
            {"name":"风扇1","reg":0x24},
            {"name":"风扇2","reg":0x34},
            {"name":"风扇3","reg":0x44},
        ]
}

FAN_INFO = {
        "droprecord_reg":{
        "bus":8,
        "addr":0x0D,
        "num_of_offset": "multiple",
        "offset":{"FAN1": 0x28, "FAN2": 0x38, "FAN3": 0x48},
        "bitoffset": {"FAN1": 0, "FAN2": 0, "FAN3": 0},
        },
        "present":{
        "num_of_offset": "multiple",
        "path": {
                "FAN1": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan1_present",
                "FAN2": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan2_present",
                "FAN3": "/sys/bus/i2c/devices/8-000d/hwmon/hwmon*/fan3_present",
        },
        "bitoffset": {"FAN1": 0, "FAN2": 0, "FAN3": 0},
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
