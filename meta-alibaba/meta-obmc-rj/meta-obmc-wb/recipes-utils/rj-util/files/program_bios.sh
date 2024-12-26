#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
. /usr/local/bin/ast-functions

#judge whethe CPU support bios
result=$(ast_product_func_call get_cpu_arch)
#get sonic arch, 0: x86 1:arm
arch_type=$?
if [ $arch_type -ne 0 ];then
    output="cpu arch is arm or type illegal, type: $arch_type"
    echo $output
    logger -p DEBUG $output
    exit -1
fi

# Determine whethe CPU does power off
ast_product_func_call get_cpu_rst_status
s5_status=$?
ast_product_func_call get_s5_ok_mask
s5_ok_mask=$?
if [ $((${s5_status} & ${s5_ok_mask})) == 0 ]; then
    output="failed to upgrade bios, s5_status = $s5_status"
    echo $output
    logger -p debug "$output"
    return -1
fi

# Selected BIOS, CS = 0 (master), CS = 1 (slave)
# Selected BIOS depend on register offset address 0x20 and 0x22
function select_bios_cs()
{
    spi_sel=$(ast_obmc_i2cget -f -y default 1 0x0d 0x20 fpga 6 0x0d 0x20 icelake 0 0x0d 0x23 icelakecto 0 0x0d 0x18 \
        bus14default 14 0x0d 0x20)
    reg_value=0x01
    if [[ "$1" == "master" ]]; then
        if [ $((${spi_sel} & 0x02)) == 0 ]; then
            #Switch to first bios flash
            reg_value=0x00
        fi
    else
        if [ $((${spi_sel} & 0x02)) != 0 ]; then
            #Switch to first bios flash
            reg_value=0x00
        fi
    fi
         
    ast_obmc_i2cset -f -y default 1 0x0d 0x22 $reg_value  fpga 6 0x0d 0x22 $reg_value icelake 0 0x0d 0x24 $reg_value \
        icelakecto 0 0x0d 0x19 $reg_value bus14default 14 0x0d 0x22 $reg_value
}

# Determine whether cs is required
# 0: no, which meams cs has been done before
# 1: yes, which meams cs needs to be executed here
ast_product_func_call get_is_bios_cs_required
cs_req=$?

if [ $cs_req == 1 ]; then
    # Reserve BIOS original boot setup
    store_bios_boot=$(ast_obmc_i2cget -f -y default 1 0x0d 0x22 fpga 6 0x0d 0x22 icelake 0 0x0d 0x24 icelakecto 0 0x0d 0x19 \
        bus14default 14 0x0d 0x22)
    if [[ "$1" == "normal" ]]; then
        bios_flash=$(/usr/local/bin/bios.sh view_flash)
        case "$bios_flash" in
            "master flash")
                select_bios_cs "slave"
            ;;
            "slave flash")
                select_bios_cs "master"
            ;;
            *)
                output="unknown current flash $bios_flash"
                echo $output
                logger -p debug "$output"
                return -1
            ;;
        esac
    else
        select_bios_cs $1
    fi
fi

# Scan bios flash
mtd_ret=$(cat /proc/mtd)
mtd=$(echo "${mtd_ret}" | grep BIOS | cut -d ':' -f 1)
if [[ $mtd == "" ]]; then
    output="scan BIOS mtd failed, "${mtd_ret}""
    echo $output
    logger -p debug " $output"
    if [ $cs_req == 1 ]; then
        ast_obmc_i2cset -f -y default 1 0x0d 0x22 $store_bios_boot fpga 6 0x0d 0x22 $store_bios_boot icelake 0 0x0d 0x24 $store_bios_boot \
            icelakecto 0 0x0d 0x19 $store_bios_boot bus14default 14 0x0d 0x22 $store_bios_boot
    fi
    return -1
fi

# Update bios flash
# With busybox, the upgrade tool is designated as an older version of flashcp，BusyBox v1.24.1
# Otherwise, upgrading with the flashcp in mtd-utils, 2.0.0, will fail
upgrade_bios_result=$(busybox flashcp $2 /dev/$mtd)
if [[ $? == 0 ]] && [[ ! -n "$upgrade_bios_result" ]] && [[ "$upgrade_bios_result" != "\n" ]]; then
    echo "success"
else
    echo "failed"
fi

if [ $cs_req == 1 ]; then
    # Restore BIOS original boot setup
    ast_obmc_i2cset -f -y default 1 0x0d 0x22 $store_bios_boot fpga 6 0x0d 0x22 $store_bios_boot icelake 0 0x0d 0x24 $store_bios_boot \
        icelakecto 0 0x0d 0x24 $store_bios_boot bus14default 14 0x0d 0x22 $store_bios_boot
fi