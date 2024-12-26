#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
. /usr/local/bin/ast-functions

master_flash_str="master flash"
switchbmc_flag="/etc/device/altbmc"

function usage()
{
    echo "switch_bmc.sh [master|slave|get-next-boot|stop-watchdog]"
    exit 1
}

function view_flash()
{
    boot_code_source=$(cat $BMC_SYSFS_BMC_VIEW_PATH 2>&1)
    boot_source="master flash"
    if [[ $boot_code_source == 0 ]]; then
        boot_source="master flash"
    elif [[ $boot_code_source == 1 ]]; then
        boot_source="slave flash"
    else
        boot_source="unknown flash: $boot_code_source"
    fi
    echo $boot_source
}

function switch_stop_watchdog()
{
    sync
    #down eth, for stop all restful service and wait reboot
    ip link set dev eth0.4088 down
    #stop wtd
    echo V > /dev/watchdog1
    #switch bmc after 30s
    echo 30 > $BMC_SYSFS_BMC_SWITCH_PATH
    sleep 1
    #Before restarting, enter emergency mode, close most processes, and avoid I2C access
    systemctl isolate emergency.target > /dev/nul
}

function switch()
{
    echo "BMC will switch to the other flash in less then 30 seconds"
    switch_stop_watchdog
}

function switch_master()
{
    if [[ ${master_flash_str} =~ ${current_flash} ]]; then
        rm -rf ${switchbmc_flag}
    else
        touch ${switchbmc_flag}
    fi
    logger -p DEBUG "SET next bmc boot master"
    return 0
}

function switch_slave()
{
    if [[ ${master_flash_str} =~ ${current_flash} ]]; then
        touch ${switchbmc_flag}
    else
        rm -rf ${switchbmc_flag}
    fi
    logger -p DEBUG "SET next bmc boot slave"
    return 0
}

function switch_get_next_boot()
{
    if [[ ${master_flash_str} =~ ${current_flash} ]]; then
        #master bmc flash
        if [ -f ${switchbmc_flag} ]; then
            echo "slave"
        else
            echo "master"
        fi
        return 0
    else
        #slave bmc flash
        if [ -f ${switchbmc_flag} ]; then
            echo "master"
        else
            echo "slave"
        fi
        return 0
    fi 
}

current_flash=$(view_flash)
if [[ "$current_flash" != "master flash" ]] && [[ "$current_flash" != "slave flash" ]]; then
    echo "$current_flash"
    exit 1
fi

case $# in
    0)
        switch
    ;;
    1)
        if [ $1 = "master" ]; then
            switch_master
        elif [ $1 = "slave" ]; then
            switch_slave
        elif [ $1 = "get-next-boot" ]; then
            switch_get_next_boot
        elif [ $1 = "stop-watchdog" ]; then
            switch_stop_watchdog
        elif [ $1 = "view_flash" ]; then
            echo "$current_flash"
        else
            usage
        fi
    ;;
    *)
        usage
    ;;
esac
