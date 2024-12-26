# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
psu_fan_airflow = {
    "F2B": ['DPS-800AB-48 A','CSU550AP-3-300','AS-40FAN-01-F-RJ','CSU550AP-3-500','DPS-550AB-39 A', 'DPS-1300AB-6 S','FSP1200-20ERM', 'CSU800AP-3-300', 'GW-CRPS800N2WA','DPS-1300AB-16A', 'GW-CRPS1300D2WA'],
    "B2F": ['CSU550AP-3-501','DPS-550AB-40 A']
}

fanairflow = {
    "F2B": ['AS-80FAN-01-F-RJ','AS-40FAN-01-F-RJ','AS-40FAN-02-F','AS-40FAN-03-F','AS-80FAN-02-F'],
    "B2F": ['AS-80FAN-01-R-RJ','AS-40FAN-01-R-RJ'],
}

psutypedecode = {
    0x00: 'N/A',
    0x01: 'AC',
    0x02: 'DC',
}

class Unit:
    Temperature = "C"
    Voltage = "V"
    Current = "A"
    Power =  "W"
    Speed = "RPM"

class threshold:
    PSU_TEMP_MIN = -10 * 1000
    PSU_TEMP_MAX =  60 * 1000

    PSU_FAN_SPEED_MIN = 2000
    PSU_FAN_SPEED_MAX = 40000

    PSU_OUTPUT_VOLTAGE_MIN = 11.8 * 1000
    PSU_OUTPUT_VOLTAGE_MAX = 13 * 1000

    PSU_AC_INPUT_VOLTAGE_MIN = 180 * 1000
    PSU_AC_INPUT_VOLTAGE_MAX = 264 * 1000

    PSU_DC_INPUT_VOLTAGE_MIN = 180 * 1000
    PSU_DC_INPUT_VOLTAGE_MAX = 320 * 1000

    ERR_VALUE =  -99999000

    PSU_OUTPUT_POWER_MIN  = 0 * 1000 * 1000
    PSU_OUTPUT_POWER_MAX  = 2000 * 1000 * 1000

    PSU_INPUT_POWER_MIN = 0 * 1000 * 1000
    PSU_INPUT_POWER_MAX = 1300 * 1000 * 1000

    PSU_OUTPUT_CURRENT_MIN = 2 * 1000
    PSU_OUTPUT_CURRENT_MAX = 107 * 1000

    PSU_AC_INPUT_CURRENT_MIN = 0 * 1000
    PSU_AC_INPUT_CURRENT_MAX = 8 * 1000

    PSU_DC_INPUT_CURRENT_MIN = 0 * 1000
    PSU_DC_INPUT_CURRENT_MAX = 8 * 1000

    FAN_SPEED_MAX = 40000
    FAN_SPEED_MIN = 2000

devices = {
    "psus": [
        {
            'e2loc': {'way': 'pmbus', 'size':0x100},
            "pmbusloc": {"bus": 56, "addr": 0x58,  "way":"i2c"},
            "present" : {'loc': '/sys/s3ip/psu/psu1/present', 'way': 'sysfs', 'okval': "1"},
            "name": "PSU1",
            "airflow" :psu_fan_airflow,
            "Temperature": {
                           "value": {"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/temp1_input","way":"sysfs"},
                           "Min": threshold.PSU_TEMP_MIN ,
                           "Max": threshold.PSU_TEMP_MAX,
                           "Unit": Unit.Temperature,
                           "format":"float(float(%s)/1000)"
                          },
            "FanSpeed" : {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/fan1_input","way":"sysfs"},
                         "Min": threshold.PSU_FAN_SPEED_MIN,
                         "Max": threshold.PSU_FAN_SPEED_MAX,
                         "Unit": Unit.Speed
                          },
            "InputsStatus":{"bus": 56, "addr": 0x58,  "offset":0x79, "way":"i2cword", "mask": 0x2000},
            "InputsType":{"bus": 56, "addr": 0x58,  "offset":0x80, "way":"i2c", 'psutypedecode':psutypedecode},
            "InputsVoltage": {
                        'AC': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.PSU_AC_INPUT_VOLTAGE_MIN ,
                                    "Max": threshold.PSU_AC_INPUT_VOLTAGE_MAX,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"

                                },
                              'DC': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.PSU_DC_INPUT_VOLTAGE_MIN ,
                                    "Max": threshold.PSU_DC_INPUT_VOLTAGE_MAX,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"
                              },
                              'other': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.ERR_VALUE,
                                    "Max": threshold.ERR_VALUE,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"
                              }
                        },
            "InputsCurrent":
                    {
                        'AC': {
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.PSU_AC_INPUT_CURRENT_MIN ,
                            "Max": threshold.PSU_AC_INPUT_CURRENT_MAX,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        },
                        'DC':{
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.PSU_DC_INPUT_CURRENT_MIN ,
                            "Max": threshold.PSU_DC_INPUT_CURRENT_MAX,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        },
                        'other':{
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.ERR_VALUE ,
                            "Max": threshold.ERR_VALUE,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        }
                    },

            "InputsPower":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/power1_input","way":"sysfs"},
                         "Min": threshold.PSU_INPUT_POWER_MIN ,
                         "Max": threshold.PSU_INPUT_POWER_MAX,
                         "Unit": Unit.Power,
                         "format":"float(float(%s)/1000000)"
                          },
            "OutputsStatus":{"bus": 56, "addr": 0x58,  "offset":0x79, "way":"i2cword", "mask": 0x8800},
            "OutputsVoltage":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/in2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_VOLTAGE_MIN,
                         "Max": threshold.PSU_OUTPUT_VOLTAGE_MAX,
                         "Unit": Unit.Voltage,
                         "format":"float(float(%s)/1000)"
                          },
            "OutputsCurrent":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/curr2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_CURRENT_MIN ,
                         "Max": threshold.PSU_OUTPUT_CURRENT_MAX ,
                         "Unit": Unit.Current,
                         "format":"float(float(%s)/1000)"
                          },
            "OutputsPower":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-56/56-0058/hwmon/hwmon*/power2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_POWER_MIN ,
                         "Max": threshold.PSU_OUTPUT_POWER_MAX ,
                         "Unit": Unit.Power,
                         "format":"float(float(%s)/1000000)"
                          },
        },
        {
            'e2loc': {'way': 'pmbus', 'size':0x100},
            "pmbusloc": {"bus": 57, "addr": 0x58 ,  "way":"i2c"},
            "present" : {'loc': '/sys/s3ip/psu/psu2/present', 'way': 'sysfs', 'okval': "1"},
            "name": "PSU2",
            "airflow" :psu_fan_airflow,
            "Temperature": {
                           "value": {"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/temp1_input","way":"sysfs"},
                           "Min": threshold.PSU_TEMP_MIN ,
                           "Max": threshold.PSU_TEMP_MAX,
                           "Unit": Unit.Temperature,
                           "format":"float(float(%s)/1000)"
                          },
            "FanSpeed" : {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/fan1_input","way":"sysfs"},
                         "Min": threshold.PSU_FAN_SPEED_MIN,
                         "Max": threshold.PSU_FAN_SPEED_MAX,
                         "Unit": Unit.Speed,
                          },
            "InputsStatus": {"bus": 57, "addr": 0x58,  "offset":0x79, "way":"i2cword", "mask": 0x2000},
            "InputsType": {"bus": 57, "addr": 0x58,  "offset":0x80, "way":"i2c", 'psutypedecode':psutypedecode},
            "InputsVoltage": {
                            'AC': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.PSU_AC_INPUT_VOLTAGE_MIN ,
                                    "Max": threshold.PSU_AC_INPUT_VOLTAGE_MAX,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"

                                },
                              'DC': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.PSU_DC_INPUT_VOLTAGE_MIN ,
                                    "Max": threshold.PSU_DC_INPUT_VOLTAGE_MAX,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"
                              },
                              'other': {
                                    "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/in1_input","way":"sysfs"},
                                    "Min": threshold.ERR_VALUE,
                                    "Max": threshold.ERR_VALUE,
                                    "Unit": Unit.Voltage,
                                    "format":"float(float(%s)/1000)"
                              }

                        },
            "InputsCurrent":
                    {
                        'AC':{
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.PSU_AC_INPUT_CURRENT_MIN ,
                            "Max": threshold.PSU_AC_INPUT_CURRENT_MAX,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        },
                        'DC':{
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.PSU_DC_INPUT_CURRENT_MIN ,
                            "Max": threshold.PSU_DC_INPUT_CURRENT_MAX,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        },
                        'other':{
                            "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/curr1_input","way":"sysfs"},
                            "Min": threshold.ERR_VALUE ,
                            "Max": threshold.ERR_VALUE,
                            "Unit": Unit.Current,
                            "format":"float(float(%s)/1000)"
                        }
                    },
            "InputsPower":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/power1_input","way":"sysfs"},
                         "Min": threshold.PSU_INPUT_POWER_MIN ,
                         "Max": threshold.PSU_INPUT_POWER_MAX,
                         "Unit": Unit.Power,
                         "format":"float(float(%s)/1000000)"
                          },
            "OutputsStatus": {"bus": 57, "addr": 0x58,  "offset":0x79, "way":"i2cword", "mask": 0x8800},
            "OutputsVoltage":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/in2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_VOLTAGE_MIN,
                         "Max": threshold.PSU_OUTPUT_VOLTAGE_MAX,
                         "Unit": Unit.Voltage,
                         "format":"float(float(%s)/1000)"
                          },
            "OutputsCurrent":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/curr2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_CURRENT_MIN ,
                         "Max": threshold.PSU_OUTPUT_CURRENT_MAX ,
                         "Unit": Unit.Current,
                         "format":"float(float(%s)/1000)"
                          },
            "OutputsPower":
                    {
                         "value":{"loc":"/sys/bus/i2c/devices/i2c-57/57-0058/hwmon/hwmon*/power2_input","way":"sysfs"},
                         "Min": threshold.PSU_OUTPUT_POWER_MIN ,
                         "Max": threshold.PSU_OUTPUT_POWER_MAX ,
                         "Unit": Unit.Power,
                         "format":"float(float(%s)/1000000)"
                          },
        },
    ],
    "temps":[
        {
            "name": "INLET_TEMP",
            "Temperature": {
                           "value": [
                                         {"loc": "/sys/bus/i2c/devices/64-0048/hwmon/hwmon*/temp1_input", "way": "sysfs"},
                                         {"loc": "/sys/bus/i2c/devices/66-004b/hwmon/hwmon*/temp1_input", "way": "sysfs"},
                                     ],
                           "Min": -40000,
                           "Max": 55000,
                           "Unit": Unit.Temperature,
                           "format":"float(float(%s)/1000)"
                }
        },
        {
            "name": "INLET_T_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/bus/i2c/devices/64-0048/hwmon/hwmon*/temp1_input",
                    "way": "sysfs"
                },
                "Min": -40000,
                "Max": 55000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        },
        {
            "name": "SWITCH_HOTSPOT_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/bus/i2c/devices/65-0049/hwmon/hwmon*/temp1_input",
                    "way": "sysfs"
                },
                "Min": -30000,
                "Max": 100000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        },
        {
            "name": "INLET_B_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/bus/i2c/devices/66-004b/hwmon/hwmon*/temp1_input",
                    "way": "sysfs"
                },
                "Min": -40000,
                "Max": 55000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        },
        {
            "name": "OUTLET_1_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/bus/i2c/devices/78-0049/hwmon/hwmon*/temp1_input",
                    "way": "sysfs"
                },
                "Min": -30000,
                "Max": 110000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        },
        {
            "name": "OUTLET_2_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/bus/i2c/devices/79-0048/hwmon/hwmon*/temp1_input",
                    "way": "sysfs"
                },
                "Min": -30000,
                "Max": 110000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        },
        {
            "name": "SWITCH_TEMP",
            "Temperature": {
                "value": {
                    "loc": "/sys/s3ip/temp_sensor/temp1/value", "way": "sysfs"
                },
                "Min": -30000,
                "Max": 105000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)",
                "prechk": "S0"
            }
        },
        {
            "name": "CPU_TEMP",
            "Temperature": {
                "value": {"loc":"/sys/bus/platform/devices/1e78b000.peci/hwmon/hwmon*/temp4_input","way":"sysfs"},
                "Min": -15000 ,
                "Max": 100000,
                "Unit": Unit.Temperature,
                "format": "float(float(%s)/1000)"
            }
        }
    ],
    "leds": [
        {
            "name": "led1",
            "sn": "123"
        },
        {
            "name": "led2",
            "sn": "456"
        }
    ],
    "fans": [
        {
            "name": "FAN1",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-72/72-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan1/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x25, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
            "EnableWatchdogConf": {"bus": 8, "addr": 0x0d, "offset": 0x0c, "way": "i2c", "enable_byte": 0x01,
                                   "disable_byte": 0x00},
            "WatchdogStatus": {
                            "bus": 8, "addr": 0x0d,  "offset":0x0c, "way":"i2c", "mask": 0x07,
                            "full_running_mask": 0x00, "full_running_off": 0x02,
                            "running_setting_mask": 0x00, "running_setting_off": 0x04,
                            "is_open_mask": 0x01, "is_open_off": 0x01,
                            "support_watchdog_mask": 0x00, "support_watchdog_off": 0x08
                               },
            "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x24, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x2f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x2f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan1/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x24, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x2f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x2f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan1/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            },
        },
        {
            "name": "FAN2",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-73/73-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan2/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x35, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
           "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x34, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x3f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x3f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan2/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x34, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x3f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x3f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan2/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            },
        },
        {
            "name": "FAN3",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-74/74-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan3/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x45, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
            "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x44, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x4f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x4f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan3/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x44, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x4f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x4f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan3/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            }
        },
        {
            "name": "FAN4",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-75/75-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan4/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x55, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
            "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x54, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x5f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x5f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan4/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                        },
                    },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x54, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x5f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x5f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan4/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            }
        },
        {
            "name": "FAN5",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-76/76-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan5/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x65, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
            "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x64, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x6f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x6f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan5/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x64, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x6f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x6f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan5/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            }
        },
        {
            "name": "FAN6",
            "airflow" : fanairflow,
            'e2loc': {'loc': '/sys/bus/i2c/devices/i2c-77/77-0050/eeprom', 'way': 'sysfs'},
            "present" : {'loc': '/sys/s3ip/fan/fan6/present', 'way': 'sysfs', 'okval': "1"},
            "SpeedMin" : threshold.FAN_SPEED_MIN,
            "SpeedMax" : threshold.FAN_SPEED_MAX,
            "led": {"bus": 8, "addr": 0x0d,  "offset":0x75, "way":"i2c"},
            "led_attrs" : {
                "green":0xfd, "red":0xfe, "yellow":0xf7, "default":0xfd,
                "flash":0xff, "light":0xfb, "off": 0xfb,
            },
            "Rotor": {
                "Rotor1_config": {
                    "name": "Rotor1",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x74, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x7f, "way":"i2c", "mask": 0x01},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x7f, "way":"i2c", "mask": 0x01},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan6/motor1/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
                "Rotor2_config": {
                    "name": "Rotor2",
                    "Set_speed": {"bus": 8, "addr": 0x0d, "offset": 0x74, "way": "i2c"},
                    "Running": {"bus": 8, "addr": 0x0d,  "offset":0x7f, "way":"i2c", "mask": 0x02},
                    "HwAlarm": {"bus": 8, "addr": 0x0d,  "offset":0x7f, "way":"i2c", "mask": 0x02},
                    "SpeedMin": threshold.FAN_SPEED_MIN,
                    "SpeedMax": threshold.FAN_SPEED_MAX,
                    "Speed": {
                        "value": {"loc": "/sys/s3ip/fan/fan6/motor2/speed", "way": "sysfs"},
                        "Min": threshold.FAN_SPEED_MIN,
                        "Max": threshold.FAN_SPEED_MAX,
                        "Unit": Unit.Speed,
                    },
                },
            }
        },
    ],
    "cards": [
        {
            "name": "psu1",
            "sn": "123"
        },
        {
            "name": "psu2",
            "sn": "456"
        },
    ],
    "dcdc": [
        {
            "name": "BASE_53134O_V1.0_V",
            "format": "float(float(%s)/1000)",
            "Min": 900,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_RTL8111_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_CPLD3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_53134O_V1.0_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 550,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_RTL8111_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 550,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_CPLD3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 2200,
            "value": {
                "loc": "/sys/bus/i2c/devices/24-0041/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_FPGA_V1.2_V",
            "format": "float(float(%s)/1000)",
            "Min": 1080,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_FPGA_V1.0_V",
            "format": "float(float(%s)/1000)",
            "Min": 900,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_OCM_V12_V",
            "format": "float(float(%s)/1000)",
            "Min": 10800,
            "Max": 13200,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_FPGA_V1.2_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 550,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_FPGA_V1.0_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1188,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_OCM_V12_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 7700,
            "value": {
                "loc": "/sys/bus/i2c/devices/25-0041/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_FPGA_V1.8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1620,
            "Max": 1980,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_BMC_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_FPGA_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_FPGA_V1.8_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 550,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_BMC_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 2750,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_FPGA_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 550,
            "value": {
                "loc": "/sys/bus/i2c/devices/26-0041/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "BASE_SSD_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/27-0041/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "BASE_SSD_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1650,
            "value": {
                "loc": "/sys/bus/i2c/devices/27-0041/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_CORE_V",
            "format": "float(float(%s)/1000)",
            "Min": 630,
            "Max": 880,
            "value": {
                "loc": "/sys/bus/i2c/devices/32-0060/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_CORE_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 409200,
            "value": {
                "loc": "/sys/bus/i2c/devices/32-0060/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_ANALOG0 V0.9_V",
            "format": "float(float(%s)/1000)",
            "Min": 810,
            "Max": 990,
            "value": {
                "loc": "/sys/bus/i2c/devices/33-0060/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_ANALOG0 V0.9_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 22704,
            "value": {
                "loc": "/sys/bus/i2c/devices/33-0060/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_ANALOG0 V0.75_V",
            "format": "float(float(%s)/1000)",
            "Min": 675,
            "Max": 825,
            "value": {
                "loc": "/sys/bus/i2c/devices/33-0060/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_ANALOG0 V0.75_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 12133,
            "value": {
                "loc": "/sys/bus/i2c/devices/33-0060/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_ANALOG1 V0.9_V",
            "format": "float(float(%s)/1000)",
            "Min": 810,
            "Max": 990,
            "value": {
                "loc": "/sys/bus/i2c/devices/34-0060/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_ANALOG1 V0.9_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 22704,
            "value": {
                "loc": "/sys/bus/i2c/devices/34-0060/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_ANALOG1 V0.75_V",
            "format": "float(float(%s)/1000)",
            "Min": 675,
            "Max": 825,
            "value": {
                "loc": "/sys/bus/i2c/devices/34-0060/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_ANALOG1 V0.75_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 12133,
            "value": {
                "loc": "/sys/bus/i2c/devices/34-0060/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_QSFP112G0 V3.3_V",
            "format": "round((float(float(%s)*748/499000)), 3)",
            "Min": 2091,
            "Max": 2312,
            "value": {
                "loc": "/sys/bus/i2c/devices/35-0060/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_QSFP112G0 V3.3_C",
            "format": "round((float(float(%s)*748/499000)), 3)",
            "Min": -3333,
            "Max": 58160,
            "value": {
                "loc": "/sys/bus/i2c/devices/35-0060/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_QSFP112G1 V3.3_V",
            "format": "round((float(float(%s)*748/499000)), 3)",
            "Min": 2091,
            "Max": 2312,
            "value": {
                "loc": "/sys/bus/i2c/devices/35-0060/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_QSFP112G1 V3.3_C",
            "format": "round((float(float(%s)*748/499000)), 3)",
            "Min": -3333,
            "Max": 58160,
            "value": {
                "loc": "/sys/bus/i2c/devices/35-0060/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_MDIO1.2_V",
            "format": "float(float(%s)/1000)",
            "Min": 1080,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/40-0040/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_V0.8V_V",
            "format": "float(float(%s)/1000)",
            "Min": 720,
            "Max": 880,
            "value": {
                "loc": "/sys/bus/i2c/devices/40-0040/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_CONVERT_V1.2_V",
            "format": "float(float(%s)/1000)",
            "Min": 1080,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/40-0040/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_MDIO1.2_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1232,
            "value": {
                "loc": "/sys/bus/i2c/devices/40-0040/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_V0.8V_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1229,
            "value": {
                "loc": "/sys/bus/i2c/devices/40-0040/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_CONVERT_V1.2_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 3212,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_STBY_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_CLK_V3.3_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_V5.0_V",
            "format": "float(float(%s)/1000)",
            "Min": 4500,
            "Max": 5500,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_STBY_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 2200,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_CLK_V3.3_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 440,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_V5.0_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1650,
            "value": {
                "loc": "/sys/bus/i2c/devices/41-0040/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_PLL1_V0.9_V",
            "format": "float(float(%s)/1000)",
            "Min": 810,
            "Max": 990,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_V1.5_V",
            "format": "float(float(%s)/1000)",
            "Min": 1350,
            "Max": 1650,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_V1.8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1620,
            "Max": 1980,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_PLL1_V0.9_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1606,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_V1.5_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1735.8,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_V1.8_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 3162,
            "value": {
                "loc": "/sys/bus/i2c/devices/42-0040/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "MAC_PLL0_V0.9_V",
            "format": "float(float(%s)/1000)",
            "Min": 810,
            "Max": 990,
            "value": {
                "loc": "/sys/bus/i2c/devices/43-0040/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_CPLD_V3.3V_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/43-0040/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "MAC_PLL0_V0.9_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1606,
            "value": {
                "loc": "/sys/bus/i2c/devices/43-0040/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_CPLD_V3.3V_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/43-0040/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_CLK_V1.8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1620,
            "Max": 1980,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_PHY_V1.0_V",
            "format": "float(float(%s)/1000)",
            "Min": 900,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_STBY_V1.8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1620,
            "Max": 1980,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "SWITCH_CLK_V1.8_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 880,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/curr1_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_PHY_V1.0_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 220,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/curr2_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "SWITCH_STBY_V1.8_C",
            "format": "float(float(%s)/1000)",
            "Min": -1000,
            "Max": 330,
            "value": {
                "loc": "/sys/bus/i2c/devices/44-0040/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_P1V05_V",
            "format": "float(float(%s)/1000)",
            "Min": 954,
            "Max": 1160,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in1_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_VCCIN_V",
            "format": "float(float(%s)/1000)",
            "Min": 1350,
            "Max": 2200,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in2_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P1V2_VDDQ_V",
            "format": "float(float(%s)/1000)",
            "Min": 1120,
            "Max": 1280,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P1V8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1690,
            "Max": 1910,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P0V6_VTT_V",
            "format": "float(float(%s)/1000)",
            "Min": 558,
            "Max": 682,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in5_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_VNN_PCH_V",
            "format": "float(float(%s)/1000)",
            "Min": 540,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in6_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_VNN_NAC_V",
            "format": "float(float(%s)/1000)",
            "Min": 540,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in7_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P2V5_VPP_V",
            "format": "float(float(%s)/1000)",
            "Min": 2250,
            "Max": 2750,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in8_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_VCC_ANA_V",
            "format": "float(float(%s)/1000)",
            "Min": 900,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in9_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P3V3_STBY_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in10_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P5V_AUX_V",
            "format": "float(float(%s)/1000)",
            "Min": 4000,
            "Max": 5750,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in11_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P1V8_AUX_V",
            "format": "float(float(%s)/1000)",
            "Min": 1690,
            "Max": 1910,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in12_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_P3V3_AUX_V",
            "format": "float(float(%s)/1000)",
            "Min": 2970,
            "Max": 3630,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in13_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_V1P80_EMMC_V",
            "format": "float(float(%s)/1000)",
            "Min": 1690,
            "Max": 1910,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in14_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_V3P3_EMMC_V",
            "format": "float(float(%s)/1000)",
            "Min": 3100,
            "Max": 3500,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005f/hwmon/hwmon*/in15_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_VCCIN_V",
            "format": "float(float(%s)/1000)",
            "Min": 1350,
            "Max": 2200,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0070/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_P1V8_V",
            "format": "float(float(%s)/1000)",
            "Min": 1690,
            "Max": 1910,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0070/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_VCCIN_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 147000,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0070/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_P1V8_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 4100,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0070/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_P1V05_V",
            "format": "float(float(%s)/1000)",
            "Min": 954,
            "Max": 1160,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-006e/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_VNN_PCH_V",
            "format": "float(float(%s)/1000)",
            "Min": 540,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-006e/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_P1V05_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 14300,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-006e/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_VNN_PCH_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 9100,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-006e/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_VNN_NAC_V",
            "format": "float(float(%s)/1000)",
            "Min": 540,
            "Max": 1320,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0068/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_VCC_ANA_V",
            "format": "float(float(%s)/1000)",
            "Min": 900,
            "Max": 1100,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0068/hwmon/hwmon*/in4_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_VNN_NAC_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 22000,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0068/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_VCC_ANA_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 4100,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-0068/hwmon/hwmon*/curr4_input",
                "way": "sysfs"
            },
            "Unit": "A"
        },
        {
            "name": "OCM_XDPE_P1V2_VDDQ_V",
            "format": "float(float(%s)/1000)",
            "Min": 1120,
            "Max": 1280,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005e/hwmon/hwmon*/in3_input",
                "way": "sysfs"
            },
            "Unit": "V"
        },
        {
            "name": "OCM_XDPE_P1V2_VDDQ_C",
            "format": "float(float(%s)/1000)",
            "Min": -3100,
            "Max": 19000,
            "value": {
                "loc": "/sys/bus/i2c/devices/17-005e/hwmon/hwmon*/curr3_input",
                "way": "sysfs"
            },
            "Unit": "A"
        }
    ],
    "cplds": [
        {
            "name": "BASE_CPLD",
            "UserReg": {"bus": 0, "addr": 0x0d,  "offset":0xf7, "way":"i2c"},
            "ConsoleReg": {"bus": 0, "addr": 0x0d,  "offset":0xa7, "way":"i2c"},
            "ConsoleRegAttrs" : {"cpu":0x00, "bmc":0x01},
            "VersionFile": {"loc": "/sys/s3ip/cpld/cpld2/firmware_version", "way": "sysfs"},
            "UpgradeResultFile": "/var/log/fw/refresh_upgrade_result",
        },
        {
            "name": "FAN_CPLD",
            "VersionFile": {"loc": "/sys/s3ip/cpld/cpld5/firmware_version", "way": "sysfs"},
            "UpgradeResultFile": "/var/log/fw/refresh_upgrade_result",
        },
        {
            "name": "MISC_CPLD",
            "VersionFile": {"loc": "/sys/s3ip/cpld/cpld4/firmware_version", "way": "sysfs"},
            "UpgradeResultFile": "/var/log/fw/refresh_upgrade_result",
        },
    ],
    "bioss": [
        {
            "name": "master",
            "FwVersion": "/var/log/fw/fw_version",
            "BiosFlash": "/usr/local/bin/bios.sh view_flash",
            "BiosBootReg": {"bus": 0, "addr": 0x0d, "offset": 0x1b, "way":"i2c"},
            "BiosFailReg": {"bus": 0, "addr": 0x0d, "offset": 0x1c, "way":"i2c"},
        },
    ],
    "bmcs": [
        {
            "name": "master",
            "ProductName" : "/etc/device/productname",
            "ProductFullName" : "/etc/device/fullproductname",
            "FwVersion": "/var/log/fw/fw_version",
            "SwitchBmcFlag": "/etc/device/altbmc",
            "CurrentFlashFlag": {"addr": 0x1E620064,  "digit":32, "way":"devmem", "mask": 0x10},
            "watchdog": "/usr/local/bin/switch_bmc.sh stop-watchdog",
            "SysLedReg": {"bus": 0, "addr": 0x0d, "offset":0x50, "way":"i2c"},
            "PwrLedReg": {"bus": 0, "addr": 0x0d, "offset":0x51, "way":"i2c"},
            "SysFanLedReg": {"bus": 8, "addr": 0x0d, "offset":0x08, "way":"i2c"},
            "SysLedAttrs": {"off": {"blink":0x00, "steady":0x00}, "red":{"blink":0x01, "steady":0x02}, "green": {"blink":0x03, "steady":0x04}, "yellow":{"blink":0x05, "steady":0x06}},
            "PwrLedAttrs": {"off": {"blink":0x10, "steady":0x10}, "red":{"blink":0x11, "steady":0x12}, "green": {"blink":0x13, "steady":0x14}, "yellow":{"blink":0x15, "steady":0x16}},
            "SysFanLedAttrs": {"off": {"blink":0x10, "steady":0x10}, "green":{"blink":0x13, "steady":0x14}, "yellow": {"blink":0x15, "steady":0x16}},
            "BmcResetCntReg": {"bus": 0, "addr": 0x0d, "offset": 0x20, "way": "i2c"},
            "SysEeprom": {'loc': '/sys/bus/i2c/devices/i2c-2/2-0057/eeprom', 'way': 'sysfs'},
            "ResetDevList": ["APLL_EVENT", "APLL_LOL_EVENT"],
        },
    ],
    "cpu": [
        {
            "name": "cpu",
            "UserReg": {"bus": 0, "addr": 0x0d, "offset": 0xf7, "way": "i2c"},
            "CpuStatus": {"bus": 16,"addr": 0x0d, "offset": 0x10, "way": "i2c"},
            "CpuStatusAttrs": {"on": 0x36, "off": 0x1b},
            "CpuResetCntReg": {"bus": 0, "addr": 0x0d, "offset": 0x11, "way": "i2c"},
            "CpuResetTypeReg": {"bus": 0, "addr": 0x0d, "offset": 0x10, "way": "i2c", "mask": 0x3},
            "CpuResetTypeAttrs":{"warm": 0x01, "cold": 0x02},
            "MachineResetReg": {"bus": 0, "addr": 0x0d, "offset": 0x93, "way": "i2c", "cmd": "shell"},
        }
    ],
    "fpga_fw": [
        {
            "name": "fpga_fw",
            "Capacity": {"upgradefpga": 1, "upgradebcm53134": 1, "getbcm53134version": 1, "upgrademac": 1,
                        "gettd4powerstatus": 1, "getportpowerstatus": 1, "bioscsfirst": 1,
                        "getssdpowerstatus": 1, "getforcecontrolpowerstatus": 1, "powerbmcemmc": 1,
                        "powerportwithtd4": 1},
            "Fwbcm53134EepromPath": "/sys/bus/spi/devices/spi0.0/eeprom",
            "Fw88e6321EepromPath": "/sys/bus/i2c/devices/45-0050/eeprom",
            "UpgradeFpgaPath": "/usr/local/bin/program_fpga.sh ",
            "UpgradeMacPath": "/usr/local/bin/program_mac.sh ",
        },
    ],
    "ext_firmwares_v2": [
        {
            "name": "bios",
            "select_master_cmd": [
                {"way": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": 0x3d, "delay":0.1},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": 0x02, "delay":0.1},
            ],
            "select_slave_cmd": [
                {"way": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": 0x3d, "delay":0.1},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": 0x02, "delay":0.1},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0x19, "value": 0x01, "delay":0.1},
            ],
            "init_cmd": [
                {"cmd": "echo 947 > /sys/class/gpio/export", "way": "cmd"},
                {"cmd": "echo high > /sys/class/gpio/gpio947/direction", "way": "cmd", "delay":0.1},
                {"cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind", "way": "cmd", "delay":0.1},
            ],
            "finish_cmd": [
                {"cmd": "echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind", "way": "cmd", "delay":0.1},
                {"cmd": "echo 0 > /sys/class/gpio/gpio947/value", "way": "cmd"},
                {"cmd": "echo 947 > /sys/class/gpio/unexport", "way": "cmd", "delay":0.1},
                {"way": "devfile", "path": "/dev/cpld0", "offset": 0x74, "value": 0x3f, "delay":0.1},
            ],
        },
        {
            "name": "fpga",
            "init_cmd": [
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x00]},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x00], "delay":0.1},
                {"cmd": "modprobe wb_spi_nor_device", "way": "cmd", "delay": 0.1},
            ],
            "finish_cmd": [
                {"cmd": "rmmod wb_spi_nor_device", "way": "cmd"},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x01],"delay":0.1},
            ],
        },
        {
            "name": "mac",
            "init_cmd": [
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x01], "delay":0.1},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf1, "value": [0x01]},
                {"cmd": "modprobe wb_spi_nor_device", "way": "cmd", "delay": 0.1},
            ],
            "finish_cmd": [
                {"cmd": "rmmod wb_spi_nor_device", "way": "cmd"},
                {"way": "devfile", "path": "/dev/cpld1", "offset": 0xf0, "value": [0x00], "delay":0.1},
            ],
        },
        {
            "name": "bcm53134",
            "init_cmd": [
                {"cmd": "echo 941 > /sys/class/gpio/export", "way": "cmd"},
                {"cmd": "echo low > /sys/class/gpio/gpio941/direction", "way": "cmd", "delay":0.1},
                {"cmd": "modprobe wb_spi_93xx46", "way": "cmd", "delay": 0.1},
            ],
            "finish_cmd": [
                {"cmd": " rmmod wb_spi_93xx46", "way": "cmd", "delay": 0.1},
                {"cmd": "echo 1 > /sys/class/gpio/gpio941/value", "way": "cmd", "delay":0.1},
                {"cmd": "echo in > /sys/class/gpio/gpio941/direction", "way": "cmd", "delay":0.1},
                {"cmd": "echo 941 > /sys/class/gpio/unexport", "way": "cmd"},
            ],
        },
    ],
    "devmon": [
        {
            "name": "APLL_EVENT",
            "Descr": "PLL lock history",
            "Default": "3",
            "Decoder": {
                    0: "Never",
                    1: "Locked to Unlocked",
                    2: "Unlocked to Locked",
                    3: "Unlocked to Locked or Locked to Unlocked"
                },
            "RW": "RW",
            "Expects": [0],
            "intbase": 16,
            "value": {
                "real_loc": "/sys/bus/i2c/devices/80-0009/apll_event",
                "way": "sysfs",
                "mask": 0x03
            },
            "prechk": "S0"
        },
        {
            "name": "APLL_STS",
            "Descr": "PLL lock status",
            "Default": "0",
            "Decoder": {
                0: "Unlocked",
                1: "Locked"
            },
            "RW": "RO",
            "Expects": [1],
            "intbase": 16,
            "value": {
                "real_loc": "/sys/bus/i2c/devices/80-0009/apll_sts",
                "way": "sysfs",
                "mask": 0x01
            },
            "prechk": "S0"
        },
        {
            "name": "APLL_LOL_EVENT",
            "Descr": "PLL lock de-assert count",
            "Default": "0",
            "Decoder": {
                0: "Never",
                1: "Lock de-asserts"
            },
            "RW": "RW",
            "Expects": [0],
            "intbase": 16,
            "value": {
                "real_loc": "/sys/bus/i2c/devices/80-0009/apll_lol_event",
                "way": "sysfs",
                "mask": 0x0f
            },
            "prechk": "S0"
        }
    ]
}
