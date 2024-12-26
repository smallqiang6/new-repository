#-------------------------------------------------------------------------------
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import sys
import os
import importlib.machinery
from plat_utils.plat_common_util import *

PRODUCT_CONFIG_MODULE_NAME = "config"

def get_productname():
    product_name = None
    productname_file = "/etc/device/conffitname"
    if not os.path.isfile(productname_file):
        return None
    with open(productname_file) as machine_file:
        for line in machine_file:
            product_name = line.strip()
            break
    return product_name

def get_product_configpath(product_name):
    if (product_name == None):
        return None
    return product_name + "/product_hal"

platcomutil = PlatCommonUtil()
producthal_path = get_product_configpath(get_productname())

global  module_product
if (producthal_path != None):
    configfile_pre   =  "/usr/lib/python3.12/site-packages/"
    grtd_productfile = configfile_pre + producthal_path+"/config.py"
    if os.path.exists(grtd_productfile):
        module_product = importlib.machinery.SourceFileLoader(PRODUCT_CONFIG_MODULE_NAME, grtd_productfile).load_module()
    else:
        #print("not exist(%s) file."%grtd_productfile)
        module_product = None
        #exit(-1)
else:
    #print("productpath is None. see cat /etc/device/productname for detail")
    module_product = None
    #exit(-1)
