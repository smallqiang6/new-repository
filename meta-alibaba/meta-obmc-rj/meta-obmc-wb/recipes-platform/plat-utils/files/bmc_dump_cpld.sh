#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

base_bus=0
cpu_bus=1
base_dev=0x0d
cpu_dev=0x0d

i2cdump_cpld() {
    local bus=$1
    local dev=$2
    local cpld_info=$(i2cdump -f -y $bus $dev 2>/dev/null)
    logger -p debug "dump $bus $dev: $cpld_info"
}

store_cpld_info() {
    ping_cpu_success=$(ping -c3 -w60 -I eth0.4088 240.1.1.2 2>/dev/null | grep "100% packet loss" | wc -l) # timeout: 60s
    # when cpu is hung, bmc will fail to ping cpu
    # when cpu is powered cycle/reset successfully, ping does not necessarily fail, which depends on when to reset/cycle within 60s
    if [ $ping_cpu_success -gt 0 ]; then
        logger -p debug "wtd timeout. If the BIOS post code was not output in the past minute, CPU is hung or powered down"
        if [ -f /etc/device/cpucpld_fpga ]; then
            base_dev=0x3d
            base_bus=6
            cpu_bus=6
        fi
        if [ -f /etc/device/cpucpld_bus14_icelake ]; then
            cpu_bus=14
        fi
        if [ -f /etc/device/cpucpld_bus16_icelake ]; then
            cpu_bus=16
        fi
        i2cdump_cpld $base_bus $base_dev # dump base cpld
        #judge whether CPU cpld exist
        result=$(ast_product_func_call get_cpu_arch)
        arch_type=$?
        if [ $arch_type -eq 0 ];then
            i2cdump_cpld $cpu_bus $cpu_dev # dump cpu cpld
        fi
    else
        logger -p debug "wtd timeout because of CPU being rebooted/reset/cycled，or busy restful"
    fi
}

store_cpld_info
