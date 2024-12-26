#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

retry_get_three_value_equle()
{
    while true
    do
        rvalue1=`ast_obmc_i2cget -f -y default 0 0xd 0x0 fpga 6 0x3d 0x0 icelake 0 0x0d 0x0 icelakecto 0 0x0d 0x0 bus14default 0 0x0d 0x0`
        rvalue2=`ast_obmc_i2cget -y -f default 0 0xd 0x0 fpga 6 0x3d 0x0 icelake 0 0x0d 0x0 icelakecto 0 0x0d 0x0 bus14default 0 0x0d 0x0`
        rvalue3=`ast_obmc_i2cget -y -f default 0 0xd 0x0 fpga 6 0x3d 0x0 icelake 0 0x0d 0x0 icelakecto 0 0x0d 0x0 bus14default 0 0x0d 0x0`
        echo "get three value ${rvalue1}, ${rvalue2}, ${rvalue3}"
        logger -p DEBUG "get three value ${rvalue1}, ${rvalue2}, ${rvalue3}"
        if [ "$rvalue1" = "$rvalue2" -a  "$rvalue1" = "$rvalue3" ];then
            break
        fi
        sleep 1
    done
}

retry_touch_file()
{
    count=1
    while [ $count -le 3 ]; do
        count=`expr $count + 1`
        touch $1
        if [[ ! -f $1 ]]; then
            logger -p debug "Touch file ($1) failed, please try again..."
            continue
        fi
        return 
    done
}

touch_service_action_file()
{
    action=$1
    upper_action=$(echo $action | tr '[:lower:]' '[:upper:]')

    product_capacity_tmp_folder="/etc/device/product_capacity/$action/"
    output=$(more $2 | awk -F "[$upper_action]" '/'$upper_action'/{print$0}')
    if [[ ! -n "$output" ]]; then
        logger -p DEBUG "Get $action service str: ${output}"
        return
    fi
    service_str=$(echo ${output} | awk -F":" '{print $2;}')
    if [[ ! -n "$service_str" ]]; then
        logger -p DEBUG "Get need $action service failed: ${service_str}"
        return
    fi
    service_name=$(echo $(echo ${service_str%?}) | awk '{print substr($1,2)}')
    if [[ ! -n "$service_name" ]]; then
        logger -p DEBUG "Deal with $action service failed: ${service_name}"
        return
    fi

    if [[ ! -d ${product_capacity_tmp_folder} ]]; then
        mkdir -p $product_capacity_tmp_folder
    fi
    logger -p DEBUG "$action startup servcie: ${service_name}"
    service_list="${service_name//,/ }"
    service_types=($service_list)
    for i in "${!service_types[@]}";
    do
        service_tmp_file=$product_capacity_tmp_folder${service_types[$i]}
        retry_touch_file $service_tmp_file
    done
    # Prevent services from starting before touching files
    [[ x"$action" == x"disable" ]] && systemctl stop ${service_list}
}

touch_service_file()
{
    product_capacity_path="/usr/local/bin/${PRODUCTNAME_CONFFIT}/capacity.json"
    #Compatible with old products(eg.32|48|128|40d..., not oob products)
    if [[ ! -f $product_capacity_path ]]; then
        return
    fi
    touch_service_action_file "disable" $product_capacity_path
    touch_service_action_file "enable" $product_capacity_path
}

# init ttyS0 ttyS1 ttyS4 baudrate
baudrate_env=$(fw_printenv baudrate 2>/dev/null)
baud_val=${baudrate_env#*=}
if [  $baud_val == 115200 ]; then
    sed -i 's/9600/'"$baud_val"'/g' /lib/systemd/system/serial-getty@.service \
        /etc/device/baudrate.conf
    systemctl daemon-reload
    systemctl restart serial-getty@ttyS4.service
    stty -F /dev/ttyS0 ispeed $baud_val ospeed $baud_val cs8
    stty -F /dev/ttyS1 ispeed $baud_val ospeed $baud_val cs8
    stty -F /dev/ttyS2 ispeed $baud_val ospeed $baud_val cs8
    stty -F /dev/ttyS3 ispeed $baud_val ospeed $baud_val cs8
fi

# for the drive
if [ -x /var/log/rc0_debug.early ]; then
   /var/log/rc0_debug.early
fi

rm -rf /etc/config_done

# read conffitname
PRODUCTNAME_CONFFIT=`fw_printenv conffitname | awk -F"=" '{print $2;}'`
export PRODUCTNAME_ENV=${PRODUCTNAME_CONFFIT}
if [ -z ${PRODUCTNAME_CONFFIT} ]; then
    echo "error: fw_printenv conffitname is null, please check detail"
    exit 1
fi

# read productname
PRODUCTNAME_FULL_ENV=$(fw_printenv productname)
if [ -z $PRODUCTNAME_FULL_ENV ]; then
    echo "error: fw_printenv productname is null, please check detail"
    exit 1
fi

PRODUCTNAME=${PRODUCTNAME_FULL_ENV##*=}
PRODUCTNAME_SHORT=`echo $PRODUCTNAME | awk -F "-" '{printf $1 "-"; print $2}'`
DEVICE_PATH="/etc/device"
if [ ! -d $DEVICE_PATH ]; then
    mkdir -p $DEVICE_PATH
fi

# read uboot_env
fw_printenv > /etc/device/uboot_env
echo ${PRODUCTNAME_SHORT} > /etc/device/productname
echo ${PRODUCTNAME} > /etc/device/fullproductname
echo ${PRODUCTNAME_CONFFIT} > /etc/device/conffitname
echo "config done" > /etc/config_done
# the file, /etc/device/productname, must be created befroe this
/usr/local/bin/ast-functions ast_product_func_call touch_cpucpld_type_file

#read three time equle, for i2c residue , bug 608349
retry_get_three_value_equle

touch_service_file

#for debug bmc service
if [ -x /var/log/rc_debug.early ]; then
   /var/log/rc_debug.early
fi
exit 0;
