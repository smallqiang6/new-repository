#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions
logger_indicate="phy_operation"
g_up_phy_val="0x1140"
g_down_phy_val="0x1940"

function do_help()
{
    echo "USAGE: $0 option"
    echo " e.g.: $0 [show|down|up|show_port]"
}

function is_support_phy_operation()
{
    restult=$(ast_product_func_call get_support_capability phy_set)
    capability=$?
    if [ $capability != 1 ];then
        echo "unsupport phy operation"
        logger -t ${logger_indicate} -p debug "unsupport phy operation, capability_val: $capability"
        exit
    fi
}

function get_phy_type()
{
    is_support_phy_operation
    phy_name=$(cat /etc/sw_config.json 2>/dev/null | grep "name")
    ret=0 #default: 5387
    if [[ ${phy_name} =~ "88e6321" ]]; then
        ret=1
    elif [[ ${phy_name} =~ "bcm53134" ]]; then
        ret=2
    fi
    logger -t ${logger_indicate} -p debug "phy type: $phy_name"
    return $ret
}

function show_5387_status()
{
    ret=$(cat /sys/bus/mdio_bus/devices/ftgmac100_mii:18/hw_test01 | awk '{print $7;}')
    logger -t ${logger_indicate} -p debug "phy status ret_val: $ret"
    #ret=0x79c9
    ret=$(($ret))
    mask=$((0x20))
    echo -n "show phy state: "
    if [[ $((${ret}&${mask})) = 0 ]]
    then
        echo "down"
    else
        echo "up"
    fi
}

function show_88e6321_status()
{
    ret=$(smitool phy rd 88e6321 0x01 0x00)
    logger -t ${logger_indicate} -p debug "phy status ret_val: $ret"
    echo -n "show phy state: "
    if [[ $ret == $g_up_phy_val ]]; then
        echo "up"
    elif [[ $ret == $g_down_phy_val ]]; then
        echo "down"
    else
        echo "unknown status: $ret"
    fi
}

function show_bcm53134_status()
{
    ret=$(dfd_debug phydev_rd 4 1)
    ret=$(dfd_debug phydev_rd 4 1) # Need to read twice
    check_char=`echo ${ret: -1}` # check the last char
    logger -t ${logger_indicate} -p debug "phy status ret_val: $ret"
    echo -n "show phy state: "
    if [[ $check_char == "d" ]]; then
        echo "up"
    elif [[ $check_char == "9" ]]; then
        echo "down"
    else
        echo "unknown status: $ret"
    fi
}

function show_phy()
{
    get_phy_type
    phy_type=$?
    if [ $phy_type -eq 1 ]; then
        show_88e6321_status
    elif [ $phy_type -eq 2 ]; then
        show_bcm53134_status
    else
        show_5387_status
    fi
}

function down_phy()
{
    get_phy_type
    phy_type=$? # default: 5387; 1: 88e6321; 2: bcm53134
    echo "set phy down"
    if [ $phy_type -eq 1 ]; then
        smitool phy wr 88e6321 0x01 0x00 $g_down_phy_val
    elif [ $phy_type -eq 2 ]; then
        dfd_debug phydev_wr 4 0 $g_down_phy_val
    else
        echo $g_down_phy_val > /sys/bus/mdio_bus/devices/ftgmac100_mii:18/hw_test00
    fi
    logger -t ${logger_indicate} -p debug "set phy down($g_down_phy_val) done: $?"
}

function up_phy()
{
    get_phy_type
    phy_type=$? # default: 5387; 1: 88e6321; 2: bcm53134
    echo "set phy up"
    if [ $phy_type -eq 1 ]; then
        smitool phy wr 88e6321 0x01 0x00 $g_up_phy_val
    elif [ $phy_type -eq 2 ]; then
        dfd_debug phydev_wr 4 0 $g_up_phy_val
    else
        echo $g_up_phy_val > /sys/bus/mdio_bus/devices/ftgmac100_mii:18/hw_test00
    fi
    logger -t ${logger_indicate} -p debug "set phy up($g_up_phy_val) done: $?"
}

function show_88e6321_port_status()
{
    declare -A port_map
    port_map["port1"]="88e6321 0x01"
    port_map["port3"]="88e6321 0x03"
    port_map["bcm54616"]="general 0x11"
    keys=("${!port_map[@]}")
    sorted_keys=($(printf "%s\n" "${keys[@]}" | sort))
    for key in "${sorted_keys[@]}"; do
        ret=$(smitool phy rd ${port_map[$key]} 0x00)
        logger -t ${logger_indicate} -p debug "phy $key status ret_val: $ret"
        echo -n "show phy $key state: "
        if [[ $ret == $g_up_phy_val ]]; then
            echo "up"
        elif [[ $ret == $g_down_phy_val ]]; then
            echo "down"
        else
            echo "unknown status: $ret"
        fi
    done
}

function show_bcm53134_port_status()
{
    declare -A port_map
    port_map["port0"]="0"
    port_map["port1"]="1"
    port_map["port2"]="2"
    port_map["port3"]="3"
    port_map["portmgmt"]="4"
    keys=("${!port_map[@]}")
    sorted_keys=($(printf "%s\n" "${keys[@]}" | sort))
    for key in "${sorted_keys[@]}"; do
        ret=$(dfd_debug phydev_rd ${port_map[$key]} 1)
        ret=$(dfd_debug phydev_rd ${port_map[$key]} 1)
        check_char=`echo ${ret: -1}`
        logger -t ${logger_indicate} -p debug "phy $key status ret_val: $ret"
        echo -n "show phy $key state: "
        if [[ $check_char == "d" ]]; then
            echo "up"
        elif [[ $check_char == "9" ]]; then
            echo "down"
        else
            echo "unknown status: $ret"
        fi
    done
}

function show_5387_port_status()
{
    declare -A port_map
    port_map["port0"]="00"
    port_map["port1"]="01"
    port_map["port2"]="02"
    port_map["port3"]="03"
    port_map["54616_1"]="11"
    port_map["54616_3"]="18"
    keys=("${!port_map[@]}")
    sorted_keys=($(printf "%s\n" "${keys[@]}" | sort))
    mask=$((0x20))
    for key in "${sorted_keys[@]}"; do
        ret=$(cat /sys/bus/mdio_bus/devices/ftgmac100_mii:18/hw_test${port_map[$key]} | awk '{print $7;}')
        logger -t ${logger_indicate} -p debug "phy $key status ret_val: $ret"
        ret=$(($ret))
        echo -n "show phy $key state: "
        if [[ $((${ret}&${mask})) = 0 ]]
        then
            echo "down"
        else
            echo "up"
        fi
    done
}

function show_all_port()
{
    get_phy_type
    phy_type=$?
    if [ $phy_type -eq 1 ]; then
        show_88e6321_port_status
    elif [ $phy_type -eq 2 ]; then
        show_bcm53134_port_status
    else
        show_5387_port_status
    fi
}

case $1 in
    show)
        show_phy
        ;;

    down)
        down_phy
        ;;

    up)
        up_phy
        ;;
    show_port)
        show_all_port
        ;;
    *)
        do_help
    ;;
esac
