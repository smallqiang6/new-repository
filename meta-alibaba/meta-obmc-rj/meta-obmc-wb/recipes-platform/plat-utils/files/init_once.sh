#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
. /usr/local/bin/ast-functions

#judge is support bmc ready or not
restult=$(ast_product_func_call get_support_capability bmc_ready)
capability=$?
if [ $capability != 1 ];then
    logger -p DEBUG "unsupport bmc ready operation"
    exit 0
fi

#设置网卡模式
ast_product_func_call set_netcard_mode

#设置BMC READY
logger -p DEBUG "Bmc ready."
ast_product_func_call bmc_ready

#判断是否被设置整机复位标志
count=1
while [ $count -le 3 ]; do
    count=$((count + 1))
    #判断是CPU所有硬件是否已就绪，可正常工作
    ret=$(ast_product_func_call get_cpu_rst_status)
    tmp=$?
    ret=$(ast_product_func_call get_cpu_rst_mask)
    mask=$?
    value=$((tmp & mask))
    if [ "0" -ne "$((value))" ]; then
        logger -p DEBUG "Power is up..."
        logger -p WARNING "CPU state changed to S0"
        exit 0
    fi
    sleep 1
done

exit 0;
