#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from platform_common import *

STARTMODULE = {
    "dev_monitor": 1,
    "gen_sw_config": 1,
}

INIT_PARAM_PRE = [
    # MAC_CORE
    {"loc": "/sys/bus/i2c/devices/32-0060/hwmon/hwmon*/avs0_vout_min", "value": 650000, "gettype": "sysfs"},
    {"loc": "/sys/bus/i2c/devices/32-0060/hwmon/hwmon*/avs0_vout_max", "value": 806250, "gettype": "sysfs"},
]

INIT_PARAM = [
    # set sysled green
    {"gettype": "sysfs", "loc": "/sys/s3ip/sysled/sys_led_status", "value": 0x01},
]

##################### MAC Voltage adjust####################################
MAC_DEFAULT_PARAM = [
    {
        "name": "mac_core",              # AVS name
        "type": 0,                       # 1: used default value, if rov value not in range. 0: do nothing, if rov value not in range
        "rov_source": 0,                 # 0: get rov value from cpld, 1: get rov value from SDK
        "cpld_avs": {"path": "/dev/cpld3", "offset": 0x10, "read_len": 1, "gettype": "devfile"},
        "set_avs": {
            "loc": "/sys/bus/i2c/devices/32-0060/hwmon/hwmon*/avs0_vout",
            "gettype": "sysfs", "formula": "int((%f)*1000000)"
        },
        "mac_avs_param": {
            0x81: 0.80625,
            0x82: 0.80000,
            0x83: 0.79375,
            0x84: 0.78750,
            0x85: 0.78125,
            0x86: 0.77500,
            0x87: 0.76875,
            0x88: 0.76250,
            0x89: 0.75625,
            0x8A: 0.75000,
            0x8b: 0.74375,
            0x8c: 0.73750,
            0x8d: 0.73125,
            0x8e: 0.72500,
            0x8f: 0.71875,
            0x90: 0.7125,
            0x91: 0.70625,
            0x92: 0.7,
            0x93: 0.69375,
            0x94: 0.6875,
            0x95: 0.68125,
            0x96: 0.675,
            0x97: 0.66875,
            0x98: 0.6625,
            0x99: 0.65625,
            0x9a: 0.65,
        },
        "avs_ctrl_pre_sleep": 10,
    }
]

DEV_MONITOR_PARAM = {
    "polling_time": 10,
    "psus": [
        {
            "name": "psu1",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/psu/psu1/present", "okval": 1},
            "device": [
                {"id": "psu1pmbus", "name": "wb_fsp1200", "bus": 56, "loc": 0x58, "attr": "hwmon"},
            ],
        },
        {
            "name": "psu2",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/psu/psu2/present", "okval": 1},
            "device": [
                {"id": "psu2pmbus", "name": "wb_fsp1200", "bus": 57, "loc": 0x58, "attr": "hwmon"},
            ],
        },
    ],
    "fans": [
        {
            "name": "fan1",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan1/present", "okval": 1},
            "device": [
                {"id": "fan1frue2", "name": "24c64", "bus":72, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan2",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan2/present", "okval": 1},
            "device": [
                {"id": "fan2frue2", "name": "24c64", "bus":73, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan3",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan3/present", "okval": 1},
            "device": [
                {"id": "fan3frue2", "name": "24c64", "bus":74, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan4",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan4/present", "okval": 1},
            "device": [
                {"id": "fan4frue2", "name": "24c64", "bus":75, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan5",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan5/present", "okval": 1},
            "device": [
                {"id": "fan5frue2", "name": "24c64", "bus":76, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan6",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/fan/fan6/present", "okval": 1},
            "device": [
                {"id": "fan6frue2", "name": "24c64", "bus":77, "loc": 0x50, "attr": "eeprom"},
            ],
        },
    ],
    "others": [
        {
            "name": "eeprom",
            "device": [
                {"id": "eeprom_1", "name": "24c02", "bus": 16, "loc": 0x50, "attr": "eeprom"},
                {"id": "eeprom_2", "name": "24c02", "bus": 2, "loc": 0x53, "attr": "eeprom"},
                {"id": "eeprom_3", "name": "24c02", "bus": 2, "loc": 0x57, "attr": "eeprom"},
                {"id": "eeprom_4", "name": "24c02", "bus": 2, "loc": 0x51, "attr": "eeprom"},
                {"id": "eeprom_5", "name": "24c128", "bus": 80, "loc": 0x50, "attr": "eeprom"},
                {"id": "eeprom_6", "name": "24c02", "bus": 8, "loc": 0x56, "attr": "eeprom"},
            ],
        },
        {
            "name": "tmp275",
            "device": [
                {"id": "tmp275_1", "name": "wb_tmp275", "bus": 64, "loc": 0x48, "attr": "hwmon"},
                {"id": "tmp275_2", "name": "wb_tmp275", "bus": 65, "loc": 0x48, "attr": "hwmon"},
                {"id": "tmp275_2", "name": "wb_tmp275", "bus": 66, "loc": 0x4b, "attr": "hwmon"},
                {"id": "tmp275_3", "name": "wb_tmp275", "bus": 78, "loc": 0x49, "attr": "hwmon"},
                {"id": "tmp275_4", "name": "wb_tmp275", "bus": 79, "loc": 0x48, "attr": "hwmon"},
            ],
        },
        {
            "name": "ina3221",
            "device": [
                {"id": "ina3221_1", "name": "wb_ina3221", "bus": 24, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_2", "name": "wb_ina3221", "bus": 25, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_3", "name": "wb_ina3221", "bus": 26, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_4", "name": "wb_ina3221", "bus": 27, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_5", "name": "wb_ina3221", "bus": 40, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_6", "name": "wb_ina3221", "bus": 41, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_7", "name": "wb_ina3221", "bus": 42, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_8", "name": "wb_ina3221", "bus": 43, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_9", "name": "wb_ina3221", "bus": 44, "loc": 0x40, "attr": "hwmon"},
            ],
        },
        {
            "name": "xdpe12284",
            "device": [
                {"id": "xdpe12284_1", "name": "wb_xdpe12284", "bus": 17, "loc": 0x5e, "attr": "hwmon"},
                {"id": "xdpe12284_2", "name": "wb_xdpe12284", "bus": 17, "loc": 0x68, "attr": "hwmon"},
                {"id": "xdpe12284_3", "name": "wb_xdpe12284", "bus": 17, "loc": 0x6e, "attr": "hwmon"},
                {"id": "xdpe12284_4", "name": "wb_xdpe12284", "bus": 17, "loc": 0x70, "attr": "hwmon"},
                {"id": "xdpe12284_5", "name": "wb_xdpe12284", "bus": 33, "loc": 0x60, "attr": "hwmon"},
                {"id": "xdpe12284_6", "name": "wb_xdpe12284", "bus": 34, "loc": 0x60, "attr": "hwmon"},
                {"id": "xdpe12284_7", "name": "wb_xdpe12284", "bus": 35, "loc": 0x60, "attr": "hwmon"},
            ],
        },
        {
            "name": "xdpe132g5c",
            "device": [
                {"id": "xdpe132g5c_1", "name": "wb_xdpe132g5c_pmbus", "bus": 32, "loc": 0x60, "attr": "hwmon"},
            ],
        },
        {
            "name": "ucd90160",
            "device": [
                {"id": "ucd90160_1", "name": "wb_ucd90160", "bus": 17, "loc": 0x5f, "attr": "hwmon"},
            ],
        },
    ],
}

UPGRADE_SUMMARY = {
    "devtype": 0x40e6,

    "slot0": {
        "subtype": 0,
        "VME": {
            "chain1": {
                "name": "CPU CPLD",
                "is_support_warm_upg": 0,
            },
            "chain2": {
                "name": "BASE CPLD",
                "is_support_warm_upg": 0,
            },
            "chain3": {
                "name": "MAC CPLDA",
                "is_support_warm_upg": 0,
            },
            "chain4": {
                "name": "FCB CPLD",
                "is_support_warm_upg": 0,
            },
            "chain5": {
                "name": "MISC CPLD",
                "is_support_warm_upg": 0,
            },
        },

        "SYSFS": {
            "chain1": {
                "name": "BCM53134",
                "is_support_warm_upg": 0,
                "init_cmd": [
                    {"cmd": "modprobe wb_spi_93xx46", "gettype": "cmd", "delay": 0.1},
                ],
                "finish_cmd": [
                    {"cmd": " rmmod wb_spi_93xx46", "gettype": "cmd", "delay": 0.1},
                ],
            },
        },

        "MTD": {
            "chain2": {
                "name": "FPGA",
                "is_support_warm_upg": 0,
                "init_cmd": [
                    # make sure MAC PCIe upgrade channel is close
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x00]},
                    # openbmc FPGA upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x00], "delay":0.1},
                    {"cmd": "modprobe wb_spi_nor_device", "gettype": "cmd", "delay": 0.1},
                ],
                "finish_cmd": [
                    {"cmd": "rmmod wb_spi_nor_device", "gettype": "cmd"},
                    # close FPGA upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x01]},
                ],
            },
            "chain5": {
                "name": "MAC PCIe",
                "is_support_warm_upg": 0,
                "init_cmd": [
                    # make sure FPGA upgrade channel is close
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x01]},
                    # openbmc MAC PCIe upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x01], "delay":0.1},
                    {"cmd": "modprobe wb_spi_nor_device", "gettype": "cmd", "delay": 0.1},
                ],
                "finish_cmd": [
                    {"cmd": "rmmod wb_spi_nor_device", "gettype": "cmd"},
                    # close MAC PCIe upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x00]},
                ],
            },
            "chain4": [
                {
                    "chip_select": "master",
                    "name": "Master BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3d]},
                        # check ME recovery mode
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x202, "retry": 10, "sleep_time": 1
                        },
                        # switch master BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd"},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x02], "delay":0.1},
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # bind scm
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind",
                            "gettype": "cmd", "delay":0.1
                        },
                    ],
                    "finish_cmd": [
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # switch BIOS flash to CPU
                        {
                            "cmd": "echo 0 > /sys/class/gpio/gpio947/value",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        {
                            "cmd": "echo 947 > /sys/class/gpio/unexport",
                            "gettype": "cmd", "delay":0.1,
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        # set ME to normal operation state through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3f], "delay":0.1},
                        # check ME normal operation state
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x205, "retry": 10, "sleep_time": 1
                        },
                    ],
                },
                {
                    "chip_select": "slave",
                    "name": "Slave BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3d]},
                        # check ME recovery mode
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x202, "retry": 10, "sleep_time": 1
                        },
                        # switch slave BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd"},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x02], "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x01], "delay":0.1},
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # bind scm
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind",
                            "gettype": "cmd", "delay":0.1
                        },
                    ],
                    "finish_cmd": [
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # switch BIOS flash to CPU
                        {
                            "cmd": "echo 0 > /sys/class/gpio/gpio947/value",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        {
                            "cmd": "echo 947 > /sys/class/gpio/unexport",
                            "gettype": "cmd", "delay":0.1,
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        # set ME to normal operation state through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3f], "delay":0.1},
                        # check ME normal operation state
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x205, "retry": 10, "sleep_time": 1
                        },
                    ],
                },
                {
                    "chip_select": "force_master",
                    "traverse_skip": 1,
                    "name": "Force master BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3d]},
                        # switch master BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd", "delay":5},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x02], "delay":0.1},
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # bind scm
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind",
                            "gettype": "cmd", "delay":0.1
                        },
                    ],
                    "finish_cmd": [
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # switch BIOS flash to CPU
                        {
                            "cmd": "echo 0 > /sys/class/gpio/gpio947/value",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        {
                            "cmd": "echo 947 > /sys/class/gpio/unexport",
                            "gettype": "cmd", "delay":0.1,
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        # set ME to normal operation state through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3f], "delay":0.1},
                    ],
                },
                {
                    "chip_select": "force_slave",
                    "traverse_skip": 1,
                    "name": "Force slave BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3d]},
                        # switch slave BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd", "delay":5},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x02], "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": [0x01], "delay":0.1},
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # bind scm
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind",
                            "gettype": "cmd", "delay":0.1
                        },
                    ],
                    "finish_cmd": [
                        # unbind scm if needed
                        {
                            "cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/bus/platform/drivers/aspeed-smc/1e630000.spi",
                                "okval": True
                            }
                        },
                        # switch BIOS flash to CPU
                        {
                            "cmd": "echo 0 > /sys/class/gpio/gpio947/value",
                            "gettype": "cmd",
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        {
                            "cmd": "echo 947 > /sys/class/gpio/unexport",
                            "gettype": "cmd", "delay":0.1,
                            "pre_check": {
                                "gettype": "file_exist",
                                "judge_file": "/sys/class/gpio/gpio947/value",
                                "okval": True
                            }
                        },
                        # set ME to normal operation state through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": [0x3f], "delay":0.1},
                    ],
                },
            ],
        },

        "TEST": {
            "cpld": [
                {"chain": 1, "file": "/etc/.upgrade_test/as15_40q_rj/cpu_cpld_test_header.vme", "display_name": "CPU_CPLD"},
                {"chain": 2, "file": "/etc/.upgrade_test/as15_40q_rj/base_cpld_test_header.vme", "display_name": "BASE_CPLD"},
                {"chain": 3, "file": "/etc/.upgrade_test/as15_40q_rj/mac_cplda_test_header.vme", "display_name": "MAC_CPLDA"},
                {"chain": 4, "file": "/etc/.upgrade_test/as15_40q_rj/fcb_cpld_test_header.vme", "display_name": "FCB_CPLD"},
                {"chain": 5, "file": "/etc/.upgrade_test/as15_40q_rj/misc_cpld_test_header.vme", "display_name": "MISC_CPLD"},
            ],
            "fpga": [
                {"chain": 2, "file": "/etc/.upgrade_test/as15_40q_rj/fpga_test_header.bin", "display_name": "FPGA"},
            ]
        },
    },
}

PLATFORM_E2_CONF = {
}

GEN_SW_CONFIG_PARAM = {
    "name": "bcm53134"
}
