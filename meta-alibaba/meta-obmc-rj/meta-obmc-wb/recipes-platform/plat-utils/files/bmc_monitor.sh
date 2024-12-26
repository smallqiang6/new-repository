#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

CYCLE_DETECT_WAT_WAIT_TIMER=3000000
CYCLE_DETECT_COUNT_STEP=${CYCLE_DETECT_WAT_WAIT_TIMER}/1000000

WAT_INFO_FILE="/tmp/watchdog_info"
DUMP_CPLD_INFO="/usr/local/bin/bmc_dump_cpld.sh"
host_watchdog_enabled=0
host_watchdog_count=0

# Host CPU watchdog disabled
watchdog_disabled() {
    if [ ${host_watchdog_enabled} -eq 1 ]; then
        logger -p warning "Host CPU watchdog disabled"
        host_watchdog_enabled=0
        host_watchdog_count=0
        rm /tmp/watchdog
    fi
}

# Host CPU watchdog remain time
watchdog_remain_time() {
    wat_start_status="Enabled : ${host_watchdog_enabled}"
    wat_remain_time="RemainTime : ${host_watchdog_count}"
    echo $wat_start_status > ${WAT_INFO_FILE}
    echo $wat_remain_time >> ${WAT_INFO_FILE}
}

# Host CPU watchdog enabled
watchdog_enabled_feeded() {
    if [ ${host_watchdog_enabled} -eq 0 ]; then
        host_watchdog_enabled=1
        logger -p warning "Host CPU watchdog enabled"
    fi
    host_watchdog_count=$1
    rm /tmp/watchdog
}

judge_is_doing_dump() {
    dump_pid=$(ps | grep -v grep | grep "bmc_dump_cpld" | awk '{print $1}')
    if [ $dump_pid ]; then
        logger -p debug "wtd timeout, but the last information collection is in progress, skip!"
    else
        $DUMP_CPLD_INFO &
    fi
}

# Host CPU watchdog timeout
watchdog_timeout_check() {
    if [ ${host_watchdog_enabled} -eq 1 ]; then
        if [ ${host_watchdog_count} -gt 0 ]; then
            host_watchdog_count=$((${host_watchdog_count}-${CYCLE_DETECT_COUNT_STEP}))
        else
            logger -p crit "Host cpu watchdog timeout"
            host_watchdog_enabled=0
            judge_is_doing_dump
        fi
    fi
    watchdog_remain_time
}

watchdog_monitor() {
    watchdog_timeout_check
    if [ -f "/tmp/watchdog" ]; then
        value=$(cat /tmp/watchdog)
        if [ ${value} -eq 0 ]; then
            watchdog_disabled
        else
            watchdog_enabled_feeded ${value}
        fi
    fi
}

delete_log_backupfile() {
    backup_num=$(ls /var/log/*.backup 2> /dev/null | wc -l)
    if [ ${backup_num} -gt 0 ]; then
        rm -rf /var/log/*.backup
        logger -p debug "Backupfiles in /var/log have been deleted"
    fi
}

while true; do
    #host watchdog monitor
    watchdog_monitor
    #delete backup file in /var/log
    delete_log_backupfile
    usleep ${CYCLE_DETECT_WAT_WAIT_TIMER}
done
