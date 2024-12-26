#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import sys
import os
import logging
from platform_config import GEN_SW_CONFIG_PARAM, SW_CONFIG_PATH
from platform_util import get_value, setup_logger

DEBUG_FILE = "/etc/.gen_sw_debug_flag"
LOG_FILE = "/var/log/bsp_tech/gen_sw_debug.log"
logger = setup_logger(LOG_FILE)

def debug_init():
    if os.path.exists(DEBUG_FILE):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


default_decode_dict = {0x04:"88e6321", 0x00: "bcm5387", 0xff: "bcm5387"}
default_reg_config = {"bus": 0, "loc": 0x0d, "offset": 0x07, "gettype": "i2c"}

def write_json(switch_name):
    data = {
        "name": switch_name
    }
    with open(SW_CONFIG_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def do_switch_judge():
    if not GEN_SW_CONFIG_PARAM:
        reg_config = default_reg_config
        config_decode_dict = default_decode_dict
    else:
        switch_name = GEN_SW_CONFIG_PARAM.get("name", None)
        reg_config = GEN_SW_CONFIG_PARAM.get("type_confg", None)
        config_decode_dict = GEN_SW_CONFIG_PARAM.get("decode", None)
        if switch_name is None and reg_config is None:
            logger.error("Not find name and type_config, get switch config failed.")
            return -1
        if config_decode_dict is None:
            config_decode_dict = default_decode_dict
    if reg_config:
        ret, key = get_value(reg_config)
        if ret is False:
            logger.error("get reg_config failed, log: %s" % key)
            return -1
        if key in config_decode_dict:
            value = config_decode_dict[key]
        else:
            value = None
            logger.error("Unknown version: key: 0x%x, get switch name failed." % key)
            return -1
        write_json(value)
    else:
        write_json(switch_name)
    logger.info("gen sw config success!")
    return 0


def main():
    debug_init()
    logger.info("gen sw config start!")
    ret = do_switch_judge()
    if ret == 0 :
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()