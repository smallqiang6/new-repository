#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions
TTY=/dev/ttyS0
RETRY_COUNT=3

INITIAL_SERIAL_VALUE=$(product_current_serial)

switch_serial_to_bmc()
{
    flag=true
    serial="bmc"
    retry_count=0
    while $flag
    do
        product_swithch_serial $serial
        current_serial=$(product_current_serial)
        if [ $current_serial == $serial ];then
            flag=false
        elif [ $retry_count -gt $RETRY_COUNT ];then
            logger -p DEBUG "switch_serial_to_bmc failed "
            echo "serial connect falid, exit SOL session."
            exit
        else
            let retry_count=retry_count+1
            logger -p DEBUG "check faild,retry $retry_count time current serial $current_serial"
        fi
    done
}

resume_serial()
{
    product_swithch_serial $INITIAL_SERIAL_VALUE
}

check_tty_baud()
{
    baudstr_env=$(fw_printenv baudrate 2>/dev/null)
    baudval_env=${baudstr_env#*=}
    if [ -z $baudval_env ];then
        logger -p DEBUG "failed to get env baudrate"
        echo "failed to get env baudrate"
        exit
    fi
    baudval_tty=$(stty -F $TTY speed 2>/dev/null)
    if [ x"$baudval_env" != x"$baudval_tty" ];then
        stty -F $TTY ispeed $baudval_env ospeed $baudval_env
        if [ $? != 0 ];then
            logger -p DEBUG "failed to synchronize env baudrate"
            echo "failed to synchronize env baudrate"
        else
            logger -p DEBUG "revise tty baudrate: $baudval_tty, to $baudval_env"
        fi
    fi
}

mTerm_server_running() {
  pid=$(ps | grep -v grep | grep '/usr/local/bin/mTerm_server' | grep $1 -m 1|
        awk '{print $1}')
  if [ "$pid" ] ; then
    return 0
  fi
  return 1
}

need_extra_option() {
    # return 0: need
    server=${1##*/}
    num=$(ps | grep -v grep | grep "/usr/local/bin/mTerm_client $server" | wc -l)
    return $num
}

start_cpu_sol_session()
{

    if [ $INITIAL_SERIAL_VALUE == "Unknown" ];then
        echo "unsupport SOL session!!"
        exit
    fi

    result=$(ast_product_func_call cpu_status)
    CPU_POWER_STATUS=$(echo $?)
    if [ $CPU_POWER_STATUS -ne 1 ];then
        echo "cpu currernt status off."
    fi

    BAUD=$(stty -F $TTY speed)
    if [ $BAUD != 9600 -a $BAUD != 115200 ]; then
        echo "$TTY: illegal baud rate $BAUD."
    fi

    switch_serial_to_bmc

    tty_name=${TTY##*/}
    if mTerm_server_running ${tty_name}; then
        /usr/local/bin/mTerm_client ${tty_name}
        if need_extra_option ${tty_name}; then
            resume_serial
        fi
    else
        start_dev_microcom_session ${TTY}
        resume_serial
        # In the case of executing the "one click to modify the baudrate" function through ssh sol,
        # keep consistent with env baudrate
        # to prevent tty baudrate from being restored to the original one when microcom exits
        check_tty_baud
    fi
}

start_dev_microcom_session() {
    dev_tty=/dev/$1
    BAUD=$(stty -F $dev_tty speed)
    echo "You are in SOL session."
    echo "Use ctrl-x to quit."
    echo "-----------------------"
    echo
    /usr/bin/microcom -s $BAUD "$dev_tty"
    echo
    echo
    echo "-----------------------"
    echo "Exit from SOL session."
}

start_dev_sol_session() {
    tty=${DEV_TO_TTY["$1"]}
    if [[ "${tty}" == "" ]]; then
        echo "$1: unsupport"
        exit
    fi
    ast_product_func_call support_dev_serial ${tty}
    if [ $? -ne 1 ]; then
        echo "$1: unsupport"
        exit
    fi
    if need_extra_option ${tty}; then
        ast_product_func_call enable_dev_serial ${tty}
    fi
    if [ $? -ne 0 ]; then
        logger -p DEBUG "failed to enable_dev_serial ${tty}"
        echo "serial enable falid, exit SOL session."
        exit
    fi
    if mTerm_server_running ${tty}; then
        exec /usr/local/bin/mTerm_client ${tty}
    else
        start_dev_microcom_session ${tty}
    fi
}


#start sol session
case $1 in
    "nic1"|"nic2")
        start_dev_sol_session $1
    ;;
    *)
        start_cpu_sol_session
    ;;
esac
