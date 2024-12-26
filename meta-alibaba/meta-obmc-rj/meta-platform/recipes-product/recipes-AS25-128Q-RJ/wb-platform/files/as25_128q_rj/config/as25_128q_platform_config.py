#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from platform_common import *

STARTMODULE = {
    "dev_monitor": 1,
    "hal_fanctrl": 0,
    "avscontrol": 0,
    "gen_sw_config": 1,
}


GEN_SW_CONFIG_PARAM = {
    "name": "bcm53134",
}

INIT_PARAM_PRE = [
    # MAC_CORE
    {"loc": "/sys/bus/i2c/devices/38-0040/hwmon/hwmon*/avs0_vout_min", "value": 747100, "gettype": "sysfs"},
    {"loc": "/sys/bus/i2c/devices/38-0040/hwmon/hwmon*/avs0_vout_max", "value": 840100, "gettype": "sysfs"},
]

INIT_PARAM = [
    # set sysled green
    {"path": "/dev/cpld0", "offset": 0x50, "value": [0x04], "gettype": "devfile"},
]

##################### MAC Voltage adjust####################################
MAC_DEFAULT_PARAM = [
    {
        "name": "mac_core",              # AVS name
        "type": 0,                       # 1: used default value, if rov value not in range. 0: do nothing, if rov value not in range
        "rov_source": 0,                 # 0: get rov value from cpld, 1: get rov value from SDK
        "cpld_avs": {"path": "/dev/cpld3", "offset": 0x10, "read_len": 1, "gettype": "devfile"},
        "set_avs": {
            "loc": "/sys/bus/i2c/devices/38-0040/hwmon/hwmon*/avs0_vout",
            "gettype": "sysfs", "formula": "int((%f)*1000000)"
        },
        "mac_avs_param": {
            0x92: 0.7471,
            0x90: 0.7600,
            0x8e: 0.7710,
            0x8c: 0.7839,
            0x8a: 0.7961,
            0x88: 0.8071,
            0x86: 0.8181,
            0x84: 0.8291,
            0x82: 0.8401
        },
        "check_avs_ready": {
            "retry": 3,
            "sleep_time": 10,
            "avs_ready_check_list": [
                [
                    {
                        "gettype": "devfile", "mask": 0x10, "okval": 0x10,
                        "path": "/dev/cpld3", "offset": 0x52, "read_len": 1,
                    }
                ]
            ],
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
                {"id": "psu1pmbus", "name": "wb_fsp1200", "bus": 70, "loc": 0x58, "attr": "hwmon"},
            ],
        },
        {
            "name": "psu2",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/psu/psu2/present", "okval": 1},
            "device": [
                {"id": "psu2pmbus", "name": "wb_fsp1200", "bus": 71, "loc": 0x58, "attr": "hwmon"},
            ],
        },
        {
            "name": "psu3",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/psu/psu3/present", "okval": 1},
            "device": [
                {"id": "psu3pmbus", "name": "wb_fsp1200", "bus": 72, "loc": 0x58, "attr": "hwmon"},
            ],
        },
        {
            "name": "psu4",
            "present": {"gettype": "sysfs", "loc": "/sys/s3ip/psu/psu4/present", "okval": 1},
            "device": [
                {"id": "psu4pmbus", "name": "wb_fsp1200", "bus": 73, "loc": 0x58, "attr": "hwmon"},
            ],
        },
    ],
    "fans": [
        {
            "name": "fan1",
            "present": {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x27, "read_len": 1, "presentbit": 0, "okval": 0},
            "device": [
                {"id": "fan1frue2", "name": "24c64", "bus":90, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan2",
            "present": {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x37, "read_len": 1, "presentbit": 0, "okval": 0},
            "device": [
                {"id": "fan2frue2", "name": "24c64", "bus":89, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan3",
            "present": {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x47, "read_len": 1, "presentbit": 0, "okval": 0},
            "device": [
                {"id": "fan3frue2", "name": "24c64", "bus":88, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan4",
            "present": {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x57, "read_len": 1, "presentbit": 0, "okval": 0},
            "device": [
                {"id": "fan4frue2", "name": "24c64", "bus":87, "loc": 0x50, "attr": "eeprom"},
            ],
        },
        {
            "name": "fan5",
            "present": {"gettype": "devfile", "path": "/dev/cpld1", "offset": 0x67, "read_len": 1, "presentbit": 0, "okval": 0},
            "device": [
                {"id": "fan5frue2", "name": "24c64", "bus":86, "loc": 0x50, "attr": "eeprom"},
            ],
        },
    ],
    "others": [
        {
            "name": "eeprom",
            "device": [
                {"id": "eeprom_1", "name": "24c02", "bus": 14, "loc": 0x50, "attr": "eeprom"},
                {"id": "eeprom_2", "name": "24c02", "bus": 2, "loc": 0x53, "attr": "eeprom"},
                {"id": "eeprom_3", "name": "24c02", "bus": 2, "loc": 0x57, "attr": "eeprom"},
                {"id": "eeprom_4", "name": "24c02", "bus": 22, "loc": 0x51, "attr": "eeprom"},
                {"id": "eeprom_5", "name": "24c02", "bus": 23, "loc": 0x52, "attr": "eeprom"},
                {"id": "eeprom_6", "name": "24c02", "bus": 92, "loc": 0x56, "attr": "eeprom"},
            ],
        },
        {
            "name": "tmp275",
            "device": [
                {"id": "tmp275_1", "name": "wb_tmp275", "bus": 74, "loc": 0x48, "attr": "hwmon"},
                {"id": "tmp275_2", "name": "wb_tmp275", "bus": 78, "loc": 0x48, "attr": "hwmon"},
                {"id": "tmp275_3", "name": "wb_tmp275", "bus": 93, "loc": 0x49, "attr": "hwmon"},
                {"id": "tmp275_4", "name": "wb_tmp275", "bus": 93, "loc": 0x48, "attr": "hwmon"},
            ],
        },
        {
            "name": "ina3221",
            "device": [
                {"id": "ina3221_1", "name": "wb_ina3221", "bus": 30, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_2", "name": "wb_ina3221", "bus": 31, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_3", "name": "wb_ina3221", "bus": 32, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_4", "name": "wb_ina3221", "bus": 33, "loc": 0x41, "attr": "hwmon"},
                {"id": "ina3221_5", "name": "wb_ina3221", "bus": 46, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_6", "name": "wb_ina3221", "bus": 47, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_7", "name": "wb_ina3221", "bus": 54, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_8", "name": "wb_ina3221", "bus": 55, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_9", "name": "wb_ina3221", "bus": 56, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_10", "name": "wb_ina3221", "bus": 57, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_11", "name": "wb_ina3221", "bus": 58, "loc": 0x40, "attr": "hwmon"},
                {"id": "ina3221_12", "name": "wb_ina3221", "bus": 59, "loc": 0x40, "attr": "hwmon"},
            ],
        },
        {
            "name": "xdpe12284",
            "device": [
                {"id": "xdpe12284_1", "name": "wb_xdpe12284", "bus": 15, "loc": 0x5e, "attr": "hwmon"},
                {"id": "xdpe12284_2", "name": "wb_xdpe12284", "bus": 15, "loc": 0x68, "attr": "hwmon"},
                {"id": "xdpe12284_3", "name": "wb_xdpe12284", "bus": 15, "loc": 0x6e, "attr": "hwmon"},
                {"id": "xdpe12284_4", "name": "wb_xdpe12284", "bus": 15, "loc": 0x70, "attr": "hwmon"},
                {"id": "xdpe12284_5", "name": "wb_xdpe12284", "bus": 41, "loc": 0x58, "attr": "hwmon"},
                {"id": "xdpe12284_6", "name": "wb_xdpe12284", "bus": 42, "loc": 0x58, "attr": "hwmon"},
                {"id": "xdpe12284_7", "name": "wb_xdpe12284", "bus": 48, "loc": 0x58, "attr": "hwmon"},
            ],
        },
        {
            "name": "xdpe132g5c",
            "device": [
                {"id": "xdpe132g5c_1", "name": "wb_xdpe132g5c_pmbus", "bus": 38, "loc": 0x40, "attr": "hwmon"},
                {"id": "xdpe132g5c_2", "name": "wb_xdpe132g5c_pmbus", "bus": 39, "loc": 0x40, "attr": "hwmon"},
                {"id": "xdpe132g5c_3", "name": "wb_xdpe132g5c_pmbus", "bus": 40, "loc": 0x40, "attr": "hwmon"},
            ],
        },
        {
            "name": "ucd90160",
            "device": [
                {"id": "ucd90160_1", "name": "wb_ucd90160", "bus": 15, "loc": 0x5f, "attr": "hwmon"},
            ],
        },
    ],
}

UPGRADE_SUMMARY = {
    "devtype": 0x408f,

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
                "name": "LC CPLD",
                "is_support_warm_upg": 0,
            },
            "chain4": {
                "name": "MAC CPLDA",
                "is_support_warm_upg": 0,
            },
            "chain5": {
                "name": "MAC CPLDB",
                "is_support_warm_upg": 0,
            },
            "chain6": {
                "name": "FCB CPLD",
                "is_support_warm_upg": 0,
            },
            "chain7": {
                "name": "MISC CPLD",
                "is_support_warm_upg": 0,
            },
            "chain8": {
                "name": "PCIE CPLD",
                "is_support_warm_upg": 0,
            }
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
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf0, "value": [0x00]},
                    # openbmc FPGA upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf1, "value": [0x00], "delay":0.1},
                    {"cmd": "modprobe wb_spi_nor_device", "gettype": "cmd", "delay": 0.1},
                ],
                "finish_cmd": [
                    {"cmd": "rmmod wb_spi_nor_device", "gettype": "cmd"},
                    # close FPGA upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf1, "value": [0x01]},
                ],
            },
            "chain5": {
                "name": "MAC PCIe",
                "is_support_warm_upg": 0,
                "init_cmd": [
                    # make sure FPGA upgrade channel is close
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf1, "value": [0x01]},
                    # openbmc MAC PCIe upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf0, "value": [0x01], "delay":0.1},
                    {"cmd": "modprobe wb_spi_nor_device", "gettype": "cmd", "delay": 0.1},
                ],
                "finish_cmd": [
                    {"cmd": "rmmod wb_spi_nor_device", "gettype": "cmd"},
                    # close MAC PCIe upgrade channel
                    {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0xf0, "value": [0x00]},
                ],
            },
            "chain4": [
                {
                    "chip_select": "master",
                    "name": "Master BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3d]},
                        # check ME recovery mode
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x202, "retry": 10, "sleep_time": 1
                        },
                        # switch master BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd"},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x02], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3f], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3d]},
                        # check ME recovery mode
                        {
                            "operation": "check_value", "gettype": "peci_pcicfglocal_rd", "delay": 1,
                            "bus": 0, "dev": 0x18, "func": 0, "reg": 0x40, "rd_len": 2,
                            "mask": 0x20f, "okval": 0x202, "retry": 10, "sleep_time": 1
                        },
                        # switch slave BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd"},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x02], "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x01], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3f], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3d]},
                        # switch master BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd", "delay":5},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x02], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3f], "delay":0.1},
                    ],
                },
                {
                    "chip_select": "force_slave",
                    "traverse_skip": 1,
                    "name": "Force slave BIOS",
                    "is_support_warm_upg": 0,
                    "init_cmd": [
                        # set ME recovery mode through CPU CPLD
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3d]},
                        # switch slave BIOS flash to BMC
                        {"cmd": "echo 947 > /sys/class/gpio/export", "gettype": "cmd", "delay":5},
                        {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "gettype": "cmd", "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x02], "delay":0.1},
                        {"gettype": "devfile", "path": "/dev/cpld0", "offset": 0x19, "value": [0x01], "delay":0.1},
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
                        {"gettype": "devfile", "path": "/dev/cpld2", "offset": 0x74, "value": [0x3f], "delay":0.1},
                    ],
                },
            ],
        },

        "TEST": {
            "cpld": [
                {"chain": 1, "file": "/etc/.upgrade_test/as25_128q_rj/cpu_cpld_test_header.vme", "display_name": "CPU_CPLD"},
                {"chain": 2, "file": "/etc/.upgrade_test/as25_128q_rj/base_cpld_test_header.vme", "display_name": "BASE_CPLD"},
                {"chain": 3, "file": "/etc/.upgrade_test/as25_128q_rj/lc_cpld_test_header.vme", "display_name": "LC_CPLD"},
                {"chain": 4, "file": "/etc/.upgrade_test/as25_128q_rj/mac_cplda_test_header.vme", "display_name": "MAC_CPLDA"},
                {"chain": 5, "file": "/etc/.upgrade_test/as25_128q_rj/mac_cpldb_test_header.vme", "display_name": "MAC_CPLDB"},
                {"chain": 6, "file": "/etc/.upgrade_test/as25_128q_rj/fcb_cpld_test_header.vme", "display_name": "FCB_CPLD"},
                {"chain": 7, "file": "/etc/.upgrade_test/as25_128q_rj/misc_cpld_test_header.vme", "display_name": "MISC_CPLD"},
            ],
            "fpga": [
                {"chain": 2, "file": "/etc/.upgrade_test/as25_128q_rj/fpga_test_header.bin", "display_name": "FPGA"},
            ]
        },
    },
}

PLATFORM_E2_CONF = {
    "fan": [
        {
            "name": "FAN1 EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/90-0050/eeprom",
            "e2_decode": [
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "FAN2 EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/89-0050/eeprom",
            "e2_decode": [
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "FAN3 EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/88-0050/eeprom",
            "e2_decode": [
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "FAN4 EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/87-0050/eeprom",
            "e2_decode": [
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "FAN5 EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/86-0050/eeprom",
            "e2_decode": [
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
    ],
    "syseeprom": [
        {
            "name": "syseeprom", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/2-0057/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "productInfoArea", "field": "productVersion", "decode_type": "func", "func_name": "fru_decode_hw"
                },
                {
                    "area": "productInfoArea", "field": "productextra2", "decode_type": "func", "func_name": "fru_decode_mac"
                },
                {
                    "area": "productInfoArea", "field": "productextra3", "decode_type": "func", "func_name": "fru_decode_mac_number"
                },
            ]
        },
    ],
    "others": [
        {
            "name": "CPU EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/14-0050/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "BMC EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/2-0053/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "MAC EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/22-0051/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "LC EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/23-0052/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
        {
            "name": "FCB EEPROM", "e2_type": "fru", "e2_path": "/sys/bus/i2c/devices/92-0056/eeprom",
            "e2_decode": [
                {
                    "area": "boardInfoArea", "field": "boardextra1", "decode_type": "func", "func_name": "fru_decode_hw"
                }
            ]
        },
    ]
}

MANUINFO_CONF = {
    "bios": {
        "key": "BIOS",
        "head": True,
        "next": "cpld"
    },
    "bios_version": {
        "parent": "bios",
        "key": "Version",
        "cmd": "ipmitool mc getsysinfo system_fw_version",
        "arrt_index": 1,
    },
    "bios_boot": {
        "parent": "bios",
        "key": "Boot From",
        "file": "/sys/s3ip/system/bios_view",
        "decode": {
            "0": "Master",
            "1": "Slave"
        },
        "arrt_index": 2,
    },

    "cpld": {
        "key": "CPLD",
        "next": "fpga"
    },

    "cpld1": {
        "key": "CPLD1",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld1_model": {
        "key": "Device Model",
        "parent": "cpld1",
        "file": "/sys/s3ip/cpld/cpld1/type",
        "arrt_index": 1,
    },
    "cpld1_vender": {
        "key": "Vendor",
        "parent": "cpld1",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld1_desc": {
        "key": "Description",
        "parent": "cpld1",
        "file": "/sys/s3ip/cpld/cpld1/alias",
        "arrt_index": 3,
    },
    "cpld1_version": {
        "key": "Firmware Version",
        "parent": "cpld1",
        "file": "/sys/s3ip/cpld/cpld1/firmware_version",
        "arrt_index": 4,
    },
    
    "cpld2": {
        "key": "CPLD2",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld2_model": {
        "key": "Device Model",
        "parent": "cpld2",
        "file": "/sys/s3ip/cpld/cpld2/type",
        "arrt_index": 1,
    },
    "cpld2_vender": {
        "key": "Vendor",
        "parent": "cpld2",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld2_desc": {
        "key": "Description",
        "parent": "cpld2",
        "file": "/sys/s3ip/cpld/cpld2/alias",
        "arrt_index": 3,
    },
    "cpld2_version": {
        "key": "Firmware Version",
        "parent": "cpld2",
        "file": "/sys/s3ip/cpld/cpld2/firmware_version",
        "arrt_index": 4,
    },

    "cpld3": {
        "key": "CPLD3",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld3_model": {
        "key": "Device Model",
        "parent": "cpld3",
        "file": "/sys/s3ip/cpld/cpld3/type",
        "arrt_index": 1,
    },
    "cpld3_vender": {
        "key": "Vendor",
        "parent": "cpld3",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld3_desc": {
        "key": "Description",
        "parent": "cpld3",
        "file": "/sys/s3ip/cpld/cpld3/alias",
        "arrt_index": 3,
    },
    "cpld3_version": {
        "key": "Firmware Version",
        "parent": "cpld3",
        "file": "/sys/s3ip/cpld/cpld3/firmware_version",
        "arrt_index": 4,
    },


    "cpld4": {
        "key": "CPLD4",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld4_model": {
        "key": "Device Model",
        "parent": "cpld4",
        "file": "/sys/s3ip/cpld/cpld4/type",
        "arrt_index": 1,
    },
    "cpld4_vender": {
        "key": "Vendor",
        "parent": "cpld4",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld4_desc": {
        "key": "Description",
        "parent": "cpld4",
        "file": "/sys/s3ip/cpld/cpld4/alias",
        "arrt_index": 3,
    },
    "cpld4_version": {
        "key": "Firmware Version",
        "parent": "cpld4",
        "file": "/sys/s3ip/cpld/cpld4/firmware_version",
        "arrt_index": 4,
    },

    "cpld5": {
        "key": "CPLD5",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld5_model": {
        "key": "Device Model",
        "parent": "cpld5",
        "file": "/sys/s3ip/cpld/cpld5/type",
        "arrt_index": 1,
    },
    "cpld5_vender": {
        "key": "Vendor",
        "parent": "cpld5",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld5_desc": {
        "key": "Description",
        "parent": "cpld5",
        "file": "/sys/s3ip/cpld/cpld5/alias",
        "arrt_index": 3,
    },
    "cpld5_version": {
        "key": "Firmware Version",
        "parent": "cpld5",
        "file": "/sys/s3ip/cpld/cpld5/firmware_version",
        "arrt_index": 4,
    },

    "cpld6": {
        "key": "CPLD6",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld6_model": {
        "key": "Device Model",
        "parent": "cpld6",
        "file": "/sys/s3ip/cpld/cpld6/type",
        "arrt_index": 1,
    },
    "cpld6_vender": {
        "key": "Vendor",
        "parent": "cpld6",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld6_desc": {
        "key": "Description",
        "parent": "cpld6",
        "file": "/sys/s3ip/cpld/cpld6/alias",
        "arrt_index": 3,
    },
    "cpld6_version": {
        "key": "Firmware Version",
        "parent": "cpld6",
        "file": "/sys/s3ip/cpld/cpld6/firmware_version",
        "arrt_index": 4,
    },

    "cpld7": {
        "key": "CPLD7",
        "parent": "cpld",
        "arrt_index": 1,
    },
    "cpld7_model": {
        "key": "Device Model",
        "parent": "cpld7",
        "file": "/sys/s3ip/cpld/cpld7/type",
        "arrt_index": 1,
    },
    "cpld7_vender": {
        "key": "Vendor",
        "parent": "cpld7",
        "config": "LATTICE",
        "arrt_index": 2,
    },
    "cpld7_desc": {
        "key": "Description",
        "parent": "cpld7",
        "file": "/sys/s3ip/cpld/cpld7/alias",
        "arrt_index": 3,
    },
    "cpld7_version": {
        "key": "Firmware Version",
        "parent": "cpld7",
        "file": "/sys/s3ip/cpld/cpld7/firmware_version",
        "arrt_index": 4,
    },

    "fpga": {
        "key": "FPGA",
        "next": "others"
    },

    "fpga1": {
        "key": "FPGA1",
        "parent": "fpga",
        "arrt_index": 1,
    },
    "fpga1_model": {
        "parent": "fpga1",
        "config": "XC7A50T-2FGG484I",
        "key": "Device Model",
        "arrt_index": 1,
    },
    "fpga1_vender": {
        "parent": "fpga1",
        "config": "XILINX",
        "key": "Vendor",
        "arrt_index": 2,
    },
    "fpga1_desc": {
        "key": "Description",
        "parent": "fpga1",
        "config": "FPGA",
        "arrt_index": 3,
    },
    "fpga1_fw_version": {
        "parent": "fpga1",
        "devfile": {
            "loc": "/dev/fpga0",
            "offset": 0,
            "len": 4,
            "bit_width": 4
        },
        "key": "Firmware Version",
        "arrt_index": 4,
    },
    "fpga1_date": {
        "parent": "fpga1",
        "devfile": {
            "loc": "/dev/fpga0",
            "offset": 4,
            "len": 4,
            "bit_width": 4
        },
        "key": "Build Date",
        "arrt_index": 5,
    },
    "fpga1_boot": {
        "parent": "fpga1",
        "key": "Boot From",
        "devfile": {
            "loc": "/dev/fpga0",
            "offset":0x00,
            "len":1,
            "bit_width":1
        },
        "decode": {
            "00": "Golden",
            "default": "Main"
        },
        "arrt_index": 6,
    },

    "others": {
        "key": "OTHERS",
    },
    "cpu_bmc_switch": {
        "parent": "others",
        "key": "CPU-BMC-SWITCH",
        "arrt_index": 1,
    },
    "cpu_bmc_switch_model": {
        "parent": "cpu_bmc_switch",
        "config": "BCM53134O",
        "key": "Device Model",
        "arrt_index": 1,
    },
    "cpu_bmc_switch_vendor": {
        "parent": "cpu_bmc_switch",
        "config": "Broadcom",
        "key": "Vendor",
        "arrt_index": 2,
    },
    "cpu_bmc_switch_hw_version": {
        "parent": "cpu_bmc_switch",
        "key": "Hardware Version",
        "func": {
            "funcname": "get_cpu_bmc_switch_version",
            "params": {
                "before": [
                    {"cmd": "echo 941 > /sys/class/gpio/export", "gettype": "cmd"},
                    {"cmd": "echo out> /sys/class/gpio/gpio941/direction", "gettype": "cmd", "delay":0.1},
                    {"gettype": "cmd", "cmd": "modprobe wb_spi_93xx46"},
                ],
                "get_version": "md5sum /sys/bus/spi/devices/spi0.0/eeprom | awk '{print $1}'",
                "after": [],
                "finally": [
                    {"cmd": "echo 1 > /sys/class/gpio/gpio941/value", "gettype": "cmd", "delay":0.1},
                    {"cmd": "echo in > /sys/class/gpio/gpio941/direction", "gettype": "cmd", "delay":0.1},
                    {"cmd": "echo 941 > /sys/class/gpio/unexport", "gettype": "cmd"},
                    {"gettype": "cmd", "cmd": "rmmod wb_spi_93xx46"},
                ],
            },
        },
        "arrt_index": 3,
    }
}