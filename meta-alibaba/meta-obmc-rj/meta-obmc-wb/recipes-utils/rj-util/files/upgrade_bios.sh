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
    echo "failed to upgrade bios, s5_status = $s5_status"
    exit 1
fi

ast_product_func_call "fw_upgrade_lock"
if [ $? -ne 0 ];then
    echo "fw upgrade lock fail"
    exit 1
fi

# Determine whethe fw channel is exist or not
ast_product_func_call "judge_fw_channel_exist" "bios"
if [ $? -ne 0 ];then
    echo "fw channel: BIOS exist."
    ast_product_func_call "fw_upgrade_unlock"
    exit 1
fi

# Set me recovery
recovery_log=$(/usr/local/bin/bios.sh me recovery)
if [ $? -ne 0 ]; then
    echo $recovery_log
    exit 1
fi

# To prevent repeated pulling of gpio
# BMC upgrade BIOS is interrupted, gpio is not released
gpio_path=/sys/class/gpio/gpio947
if [ -d $gpio_path ]; then
    echo 0 > /sys/class/gpio/gpio947/value
    echo 947 > /sys/class/gpio/unexport
fi

# Pull up GPIO947 to let BMC access bios flash
# Restore register 0x1e7800fc value, when upgrading BIOS and BMC reboot
# Causes CPU to hang
echo 947 > /sys/class/gpio/export
dev_value=$(devmem 0x1e7800fc 32)
dev_value=$((${dev_value} & 0x7FFFFFFF))
devmem 0x1e7800fc 32 $dev_value
echo high > /sys/class/gpio/gpio947/direction

ast_product_func_call get_cpu_rst_status
s5_status=$?
if [ $((${s5_status} & ${s5_ok_mask})) == 0 ]; then
    echo "failed to upgrade bios, s5_status = $s5_status"
    echo 0 > /sys/class/gpio/gpio947/value
    echo 947 > /sys/class/gpio/unexport
    reset_log=$(/usr/local/bin/bios.sh me reset)
    ast_product_func_call "fw_upgrade_unlock"
    exit 1
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

    ast_obmc_i2cset -f -y default 1 0x0d 0x22 $reg_value fpga 6 0x0d 0x22 $reg_value icelake 0 0x0d 0x24 $reg_value \
        icelakecto 0 0x0d 0x19 $reg_value bus14default 14 0x0d 0x22 $reg_value
}

# Reserve BIOS original boot setup
store_bios_boot=$(ast_obmc_i2cget -f -y default 1 0x0d 0x22 fpga 6 0x0d 0x22 icelake 0 0x0d 0x24 icelakecto 0 0x0d 0x19 \
    bus14default 14 0x0d 0x22)

# Chip select
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
          echo "unknown current flash"
          echo 0 > /sys/class/gpio/gpio127/value
          echo 127 > /sys/class/gpio/unexport
          reset_log=$(/usr/local/bin/bios.sh me reset)
          ast_product_func_call "fw_upgrade_unlock"
          exit
      ;;
    esac
else
    select_bios_cs $1
fi

# Scan bios flash
result=$(echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind)
mtd=$(cat /proc/mtd | grep BIOS | cut -d ':' -f 1)
if [[ $mtd == "" ]]; then
    logger -p debug "scan bios mtd failed. result: $result"
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

result=$(echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind)
if [ $? -ne 0 ]; then
    logger -p debug "remove bios mtd failed. result: $result"
fi

# Restore BIOS original boot setup
ast_obmc_i2cset -f -y default 1 0x0d 0x22 $store_bios_boot fpga 6 0x0d 0x22 $store_bios_boot icelake 0 0x0d 0x24 $store_bios_boot \
    icelakecto 0 0x0d 0x19 $store_bios_boot bus14default 14 0x0d 0x22 $store_bios_boot

# Release gpio127, otherwise CPU hook on
echo 0 > /sys/class/gpio/gpio947/value
echo 947 > /sys/class/gpio/unexport

# Set me reset
reset_log=$(/usr/local/bin/bios.sh me reset)

ast_product_func_call "fw_upgrade_unlock"
