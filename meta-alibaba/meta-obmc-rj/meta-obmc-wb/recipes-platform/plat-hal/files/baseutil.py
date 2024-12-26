#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# baseutil.py
# Python implementation of the Class baseutil
# Original author: rd@ruijie.com.cn
#
#######################################################

import json
import subprocess
import importlib.machinery
import re
import syslog
from .osutil import osutil

SYSLOG_IDENTIFIER = "BMC"

class baseutil:

    CONFIG_PATH_FORMAT = "/usr/lib/python3.12/site-packages/%s/product_hal/%s_devices.py"
    CONFIG_NAME =  'devices'
    UBOOT_ENV_URL = '/etc/device/uboot_env'

    @staticmethod
    def get_config():
        platform = baseutil.get_platform()
        productname = baseutil.get_productname()
        real_path = baseutil.CONFIG_PATH_FORMAT % (platform, productname)
        devices = importlib.machinery.SourceFileLoader(baseutil.CONFIG_NAME, real_path).load_module()
        return devices.devices

    @staticmethod
    def get_productname():
        ret, val = osutil.command("cat %s |grep productname | awk -F\"=\" '{print $2;}'" % baseutil.UBOOT_ENV_URL)
        tmp = val.lower().replace('-', '_')
        if ret != 0 or len(val) <= 0:
            raise Exception("get productname error")
        else:
            return tmp

    @staticmethod
    def get_platform():
        ret, val = osutil.command("cat %s |grep conffitname | awk -F\"=\" '{print $2;}'" % baseutil.UBOOT_ENV_URL)
        if ret != 0 or len(val) <= 0:
            raise Exception("get platform error")
        else:
            return val

    @staticmethod
    def get_product_fullname():
        ret, val = osutil.command("cat %s |grep productname | awk -F\"=\" '{print $2;}'" % baseutil.UBOOT_ENV_URL)
        if ret != 0 or len(val) <= 0:
            raise Exception("get productname error")
        else:
            return val

    @staticmethod
    def logger_debug(msg):
        syslog.openlog(SYSLOG_IDENTIFIER)
        syslog.syslog(syslog.LOG_DEBUG, msg)
        syslog.closelog()