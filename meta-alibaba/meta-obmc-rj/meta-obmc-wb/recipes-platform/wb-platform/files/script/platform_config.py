#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import subprocess


BOARD_ID_PATH = "/sys/module/platform_common/parameters/dfd_my_type"
PRODUCT_NAME_PATH = "/etc/device/productname"


def wb_os_system(cmd):
    status, output = subprocess.getstatusoutput(cmd)
    return status, output


def get_platform_device_name():
    if not os.path.exists(PRODUCT_NAME_PATH):
        print("get product name error, %s not exists" % PRODUCT_NAME_PATH)
        sys.exit(-1)

    with open(PRODUCT_NAME_PATH) as fd:
        product_name = fd.read().strip().lower()
    return product_name


def get_product_board_id():
    if not os.path.exists(BOARD_ID_PATH):
        return "NA"

    with open(BOARD_ID_PATH) as fd:
        id_str = fd.read().strip()
    return "0x%x" % (int(id_str, 10))


platform_name = get_platform_device_name()
platform_config_file = (platform_name+ "_platform_config").replace("-","_")
product_board_id = get_product_board_id()
platform_board_id_config_file = (platform_name+ "_" + product_board_id + "_platform_config").replace("-","_")
common_config_file = "platform_common"
config_file_path   =  "/usr/local/bin/"
sys.path.append(config_file_path)


############################################################################################
if os.path.exists(config_file_path + platform_board_id_config_file + ".py"):
    module_product  = __import__(platform_board_id_config_file, globals(), locals(), [], 0)
elif os.path.exists(config_file_path + platform_config_file + ".py"):
    module_product  = __import__(platform_config_file, globals(), locals(), [], 0)
elif os.path.exists(config_file_path + common_config_file + ".py"):
    module_product  = __import__(common_config_file, globals(), locals(), [], 0)
else:
    print("config file not exist")
    sys.exit(-1)
############################################################################################

DEVICE = module_product.DEVICE

WB_GLOBALCONFIG = {
    "DRIVERLISTS": module_product.DRIVERLISTS,
    "DRIVERLISTS_CHECK":module_product.DRIVERLISTS_CHECK,
    "DEVS": DEVICE,
}
GLOBALCONFIG = WB_GLOBALCONFIG
# Initialization parameters
GLOBALINITPARAM = module_product.INIT_PARAM
GLOBALINITCOMMAND = module_product.INIT_COMMAND
GLOBALINITPARAM_PRE = module_product.INIT_PARAM_PRE
GLOBALINITCOMMAND_PRE = module_product.INIT_COMMAND_PRE

UPGRADE_SUMMARY = module_product.UPGRADE_SUMMARY
WARM_UPGRADE_PARAM = module_product.WARM_UPGRADE_PARAM
WARM_UPGRADE_STARTED_FLAG = module_product.WARM_UPGRADE_STARTED_FLAG
# dev_monitor parameter
DEV_MONITOR_PARAM = module_product.DEV_MONITOR_PARAM
# start module parameters
STARTMODULE = module_product.STARTMODULE

# platform_e2 parameter
PLATFORM_E2_CONF = module_product.PLATFORM_E2_CONF

# avscontrol parameter
MAC_DEFAULT_PARAM = module_product.MAC_DEFAULT_PARAM

# platform_manufacturer parameter
MANUINFO_CONF = module_product.MANUINFO_CONF

# generate_mgmt_version parameter
MGMT_VERSION_PATH = module_product.MGMT_VERSION_PATH

# bsp common log path
BSP_COMMON_LOG_PATH = module_product.BSP_COMMON_LOG_PATH

# xdpe monitor info
DFX_XDPE_MONITOR_INFO = module_product.DFX_XDPE_MONITOR_INFO

# generate_sw_config parameter
SW_CONFIG_PATH = module_product.SW_CONFIG_PATH
GEN_SW_CONFIG_PARAM = module_product.GEN_SW_CONFIG_PARAM

