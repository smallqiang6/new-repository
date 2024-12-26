import os
import  json
import time
from hal.hal_misc import HalMisc

#unittest configuration of HAL code.

HAL_UNITTEST_TEST_LOG_PATH = '/var/log/unittest'
HAL_FAN_TEST_LOG_FILE = 'test_hal_fan.log'
HAL_PSU_TEST_LOG_FILE = 'test_hal_psu.log'
HAL_DCDC_TEST_LOG_FILE = 'test_hal_dcdc.log'
HAL_TEMP_TEST_LOG_FILE = 'test_hal_temp.log'
HAL_SENSOR_TEST_LOG_FILE = 'test_hal_sensor.log'

######## Get Product Info ############
PRODUCT_CONFIG_FILE_PATH = '/etc/openbmc/devices/'
PRODUCT_INFO = {
    "VENDER_INFO":  'N/A',
    "ARCH_PLATFORM": 'X86',
    "PSU_FRULESS": False,
    "FAN_FRULESS": False
}

hal_misc = HalMisc()
platform_fullname = hal_misc.get_platform_name()
if platform_fullname != "N/A":
    platform_split = platform_fullname.split("-")
    PRODUCT_INFO["VENDER_INFO"] = platform_split[-1].upper()
    config_file = "{}{}/platform_cfg.json".format(PRODUCT_CONFIG_FILE_PATH, platform_fullname)
    if os.path.isfile(config_file):
        with open (config_file) as config:
            config_json = json.load(config)
            PRODUCT_INFO["ARCH_PLATFORM"] = config_json["arch"].upper() if "arch" in config_json.keys()  else "X86"
            PRODUCT_INFO["PSU_FRULESS"] = True if "psu_fruless" in config_json.keys()  and config_json["psu_fruless"] else False
            PRODUCT_INFO["FAN_FRULESS"] = True if "fan_fruless" in config_json.keys()  and config_json["fan_fruless"] else False


##### CPLD IMAGE LIST ####
CPLD_IMAGEMAP_FILE = '/tmp/cpld_image_map'
CPLD_NAME_LIST = None
CPLD_IMAGE_LIST = None
if os.path.isfile(CPLD_IMAGEMAP_FILE):
    with open(CPLD_IMAGEMAP_FILE) as config_info:
        cpld_image_info = json.load(config_info)
        CPLD_NAME_LIST = cpld_image_info["name_list"] if "name_list" in cpld_image_info.keys() else None
        CPLD_IMAGE_LIST= cpld_image_info["file_list"] if "file_list" in cpld_image_info.keys() else None

########FAN configure######
FAN_NUMS_MAX = 10
FAN_ROTOR_NUMS = 2
FAN_SPEED_MIN = 1000
FAN_SPEED_MAX = 45000

########PSU configure######
PSU_NUMS_MAX = 10
PSU_SPEED_MIN = 900
PSU_SPEED_MAX = 45000
PSU_TEMP_MIN = -30.0
PSU_TEMP_MAX = 100.0
PSU_VOLTAGE_IN_MIN = 10
PSU_VOLTAGE_IN_MAX = 310
PSU_VOLTAGE_OUT_MIN = 6
PSU_VOLTAGE_OUT_MAX = 24
PSU_CURRENT_IN_MIN = 0.0
PSU_CURRENT_IN_MAX = 100.0
PSU_CURRENT_OUT_MIN = 0.0
PSU_CURRENT_OUT_MAX = 200.0
PSU_POWER_IN_MIN = -1
PSU_POWER_IN_MAX = 2300
PSU_POWER_OUT_MIN = -1
PSU_POWER_OUT_MAX = 2000

########RJ product configure######
#1 support; 0 unsupport
CAP_INFO = {
    "as61-48x4t":{
        "fan_rotor_nums": 1, "is_support_bios": 0, "is_support_mac": 0,
        "is_support_fancpld": 0, "is_support_force_power_ctl": 1,
        "is_support_port_power_ctl": 1, "is_support_mac_power_ctl": 1,
    },
    "as61-48e4t":{
        "fan_rotor_nums": 1, "is_support_bios": 0, "is_support_mac": 0,
        "is_support_fancpld": 0, "is_support_force_power_ctl": 1,
        "is_support_port_power_ctl": 1, "is_support_mac_power_ctl": 1,
    },
    "as14-40d":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1, "is_support_ssd_power_ctl": 1,
    },
    "as24-128d":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1, "is_support_ssd_power_ctl": 1,
    },
    "as14-128h":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1,
    },
    "ac51-48c2g":{
        "fan_rotor_nums": 1, "is_support_mac": 0, "is_support_fancpld": 0,
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
    },
    "as14-24d8q":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1, "is_support_ssd_power_ctl": 1,
    },
    "as25-128q":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1, "is_support_ssd_power_ctl": 1,
    },
    "as51-24d":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 0, "is_support_ssd_power_ctl": 1,
        "is_support_mac": 0, "is_support_location_led": 0,
    },
    "as15-40q":{
        "is_support_force_power_ctl": 1, "is_support_port_power_ctl": 1,
        "is_support_mac_power_ctl": 1, "is_support_ssd_power_ctl": 1,
    },
    "rj-default":{
        "fan_rotor_nums": 2, "is_support_bios": 1, "is_support_mac": 1,
        "is_support_fancpld": 1, "is_support_force_power_ctl": 0,
        "is_support_port_power_ctl": 0, "is_support_mac_power_ctl": 0,
        "is_support_ssd_power_ctl": 0, "is_support_location_led": 1,
    },
}

def get_product_capacity(capacity_name):
    hal_misc = HalMisc()
    platform_fullname = hal_misc.get_platform_name()
    if platform_fullname != "N/A":
        platform_split = platform_fullname.split("-", 2)
        platform_name = (platform_split[0] + "-" + platform_split[1]).lower()
        product_capacity = CAP_INFO.get(platform_name, None)
        if product_capacity != None:
            special_capacity = product_capacity.get(capacity_name, None)
            if special_capacity != None:
                return special_capacity
    return CAP_INFO["rj-default"].get(capacity_name, 2) #return default function configure

def determine_whether_test_is_required(capacity_name):
    if PRODUCT_INFO["VENDER_INFO"] == "CL" or get_product_capacity(capacity_name) !=0:
        return True
    else:
        return False

def wait_cpu_ready(min_time=60):
    # Wait for the CPU to start
    time.sleep(min_time)
    if PRODUCT_INFO["VENDER_INFO"] != "RJ":
        return
    run_cycle = 5
    max_times = 24
    cpu_ready = False
    cmd_err = False
    # Make sure the CPU watchdog has timed out
    time.sleep(5)
    # Wait for CPU startup to complete, timeout: (run_cycle * max_times)s
    for times in range(1, max_times + 1):
        ret, ret_info = hal_misc.execute_command("/usr/local/bin/rj_rawcmd_cli get watchdog")
        if ret:
            cmd_err = True
            break
        if ret_info.get("Enabled", "0") == "1":
            cpu_ready = True
            break
        time.sleep(run_cycle)
    if cmd_err:
        return
    if cpu_ready:
        time.sleep(10)
