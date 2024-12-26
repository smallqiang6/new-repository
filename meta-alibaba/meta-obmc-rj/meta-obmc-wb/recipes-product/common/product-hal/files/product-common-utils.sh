# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
fw_upgrade_lock_file="/tmp/fw_upgrade_lock_file"
e2_5387_path="/sys/bus/spi/devices/spi2.0/eeprom"


product_com_get_mount_fpga_object() {
    return 1 # mount fpga/mac
}

product_com_get_cpu_arch()
{
    #0: x86, 1:arm
    return 0
}

product_com_get_post_mode()
{
    # 0: 1 Byte mode/1: 2 Byte mode/2: 4 Byte mode/3: Full mode
    return 1
}

product_com_get_support_capability()
{
#1: support this function, 0: unsupport
  case $1 in
    "power_cycle_cpu")
        return 0
    ;;
    "phy_set")
        return 1
    ;;
    "bmc_ready")
        return 1
    ;;
    *)
        logger -p DEBUG "parameter error $1, default support"
        return 1
    ;;
  esac
}

function product_com_sys_led_enable()
{
    echo 1 > $BMC_SYSFS_SYS_LED_PATH
}

function product_com_bmc_ready()
{
    echo 0 > $BMC_SYSFS_READY_PATH
    echo 1 > $BMC_SYSFS_READY_PATH
}

function product_com_set_full_fan() {
    fan_num=$(cat $BMC_SYSFS_FAN_NUM)
    for i in $(seq 1 ${fan_num})
    do
        fan_ctrl_sysfs="BMC_SYSFS_FAN${i}_SPEED_CTRL"
        echo 100 > ${!fan_ctrl_sysfs}
    done
}

#0: fw channel not exist !0: exist
function product_com_judge_fw_channel_exist()
{
    if [ $1 == "mac" -o $1 == "fpga" -o $1 == "5387" -o $1 == "88e6321" -o $1 == "bios" -o $1 == "bcm53134" \
            -o $1 == "atlas0" -o $1 == "atlas1" -o $1 == "rtl8372" -o $1 == "all" ];then
        # bcm53134 has the same e2 path as 5387
        if [ -e $e2_5387_path ];then
            logger -p debug "fw channel exist: $e2_5387_path"
            return -1
        fi

        # if 88e6321 bus is not returned by product_get_88e6321_e2_bus in product-utils.sh,
        # the device does not have 88e6321 chip
        bus_88e6321_log=$(product_get_88e6321_e2_bus 2>&1)
        bus_88e6321=$?
        err_num=$(echo $bus_88e6321_log | grep -E "(product_get_88e6321_e2_bus)*(command not found)" | wc -l)
        if [ $err_num -eq 0 ]; then
            e2_88e6321_path="/sys/bus/i2c/devices/${bus_88e6321}-0050/eeprom"
            if [ -e $e2_88e6321_path ];then
                logger -p debug "fw channel exist: $e2_88e6321_path"
                return -1
            fi
        fi

        mtd_ret=$(cat /proc/mtd)
        if [ $# == 2 ];then
            if [ $2 == "show_mtd" ];then
                logger -p debug "mtd : ${mtd_ret}"
            fi
        fi

        mtd=$(echo "${mtd_ret}" | grep extflash1 | cut -d ':' -f 1)
        if [[ $mtd != "" ]]; then
            logger -p debug "fw channel exist: extflash1."
            return -1
        fi
        mtd=$(echo "${mtd_ret}" | grep extflash0 | cut -d ':' -f 1)
        if [[ $mtd != "" ]]; then
            logger -p debug "fw channel exist: extflash0."
            return -1
        fi
    else
        logger -p debug "illegal fw type: $1"
        return -1
    fi
    return 0
}

function product_com_fw_upgrade_lock()
{
    if [ -f ${fw_upgrade_lock_file} ];then
        count=0
        while [ $count -lt 3 ]
        do
            product_com_judge_fw_channel_exist all
            if [ $? == 0 ];then
                #all fw channel not exist
                sleep 10s
                let count+=1
            else
                logger -p debug "fw channel exist, touch lock file failed"
                return -1
            fi
        done
        #all fw channel not exist, file exist,do not need to touch
        logger -p debug "all fw channel not exist, file exist,do not need to touch"
        return 0
        if [ $count == 3 ];then
            logger -p debug "fw channel exist, touch lock file failed"
            return -1
        else
            #all fw channel not exist, file exist,do not need to touch
            return 0
        fi
    else
        touch ${fw_upgrade_lock_file}
    fi

}

function product_com_fw_upgrade_unlock()
{
    if [ ! -f $fw_upgrade_lock_file ];then
        logger -p debug "$fw_upgrade_lock_file no exist, not need to unlock"
        return
    fi

    rm -f $fw_upgrade_lock_file
}

function product_com_cpu_status() {
    cpu_status=$(cat $BMC_SYSFS_CPU_BOARD_STATUS)
    if [ "${cpu_status}" == "1" ]; then
        return 0
    elif [ "${cpu_status}" == "2" ]; then
        return 1
    else
        echo $cpu_status
        return 2
    fi
}

function product_com_power_on_cpu() {
    echo 1 > $BMC_SYSFS_CPU_BOARD_CTRL
}

function product_com_power_off_cpu() {
    echo 0 > $BMC_SYSFS_CPU_BOARD_CTRL
}

function product_com_power_cycle_cpu() {
    echo 3 > $BMC_SYSFS_CPU_BOARD_CTRL
}

function product_com_power_reset_cpu() {
    echo 2 > $BMC_SYSFS_CPU_BOARD_CTRL
}

function product_com_get_cpu_rst_status() {
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x85)
    if [ -z $reg_val ]; then
        logger -p DEBUG "Error: read cpu switch status reg failed"
        return 0
    else
        value=$(printf "%d\n" $reg_val)
        return $value
    fi
}

function product_com_power_cycle_machine()
{
    echo 1 > $BMC_SYSFS_MACHINE_PSU_CTRL
}


function product_com_jtag_default_port_cpld() {
    return 0 # Not required, and default success
}

function product_com_get_current_cpu_board_cpld_type()
{
    return 0 # default cpu board cpld type: CPU_BOARD_CPLD
}

function product_com_get_88e6321_e2_bus()
{
    return 0 # 88e6321 doesn't exist
}

function product_com_touch_cpucpld_type_file()
{
    return 0 # default, no need to touch
}

function product_com_get_s5_ok_mask()
{
    return 8
}

function product_com_get_cpu_rst_mask() {
    return 32
}

function product_com_get_is_bios_cs_required()
{
    return 1 # bios cs needs to be executed
}

function product_com_get_is_me_required()
{
    return 0 # 0: not required, 1 required
}

function product_com_shut_cpu_first_when_refresh_basecpld()
{
    return 0 # default 0, not required; 1, shut cpu first
}

function product_com_shut_cpu_first_when_refresh_misccpld()
{
    return 0 # default 0, not required; 1, shut cpu first
}

function product_com_set_register_hold_miscmac_signal()
{
    return 0 # not required
}

function product_com_support_power_bmcemmc()
{
    return 0 # 1: support; 0: unsupport
}

function product_com_support_power_cpuemmc()
{
    return 0 # 1: support; 0: unsupport
}

function product_com_get_is_support_reset_rtc()
{
    return 0 # 1: support this function, 0: unsupport
}

function product_com_get_post_data_mode()
{
    # 0: 1 Byte mode/1: 2 Byte mode/2: 4 Byte mode/3: Full mode
    return 0 #default
}

function product_com_clear_clock_reg()
{
    return 0 # default, no need to clear
}

function product_com_set_netcard_mode()
{
    return 0 # default, no need to set
}

function product_com_support_power_netcard()
{
    return 0 # 1: support; 0: unsupport
}

function product_com_support_dev_serial()
{
    return 0 # 1: support; 0: unsupport
}

function product_com_enable_dev_serial()
{
    return 0 # default, no need to set
}

function product_com_set_register_release_miscmac_signal()
{
    return 0 # default, no need to set
}
