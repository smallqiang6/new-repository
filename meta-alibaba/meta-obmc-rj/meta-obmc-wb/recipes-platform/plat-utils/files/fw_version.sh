#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

RELEASE_TAG="obmc-rj-"
BUILD_ID="BUILD_DATE"

if [ ! -d "/var/log/fw" ]; then
  mkdir /var/log/fw
  logger -t INITSERVICE -p DEBUG "log fw dir first create"
fi

fw_file="/var/log/fw/fw_version"
# Get bmc firmware version
bmc_fw_version() {
  fw="$(cat /etc/issue | grep $RELEASE_TAG)"
  fw="${fw#*$RELEASE_TAG}"
  echo "${fw}"
}

# Get bmc flash
bmc_flash() {
  flash="$(bmc.sh view_flash)"
  flash="${flash%% *}"
  echo "${flash}"
}

bmc_fw="$(bmc_fw_version)"
bmc_flash="$(bmc_flash)"
prestr="${bmc_flash}-bmc-fw"

curr_fw="${prestr} : ${bmc_fw}"

# Get bmc build_id
bmc_buildid() {
  bi="$(cat /etc/os-release | grep $BUILD_ID)"
  bi="${bi#*"="}" 
  bi="$(echo $bi | sed 's/\"//g')"
  echo "${bi}"
  logger -t INITSERVICE -p DEBUG "BMC version ${bi}"
}

bmc_bi="$(bmc_buildid)"
prestr_bi="${bmc_flash}-bmc-buildid"
curr_bi="${prestr_bi} : ${bmc_bi}"

# find and replace
str_replase() {
  #replace bmc firmware version
  oldversion="$(cat ${fw_file} | grep ${prestr})"
  #echo ${oldversion}
  if [[ -z $oldversion ]]; then
    echo ${curr_fw} >> ${fw_file}
  else
    sed -i 's/'"${oldversion}"'/'"${curr_fw}"'/g' ${fw_file}
  fi
  
  #replace bmc buildid
  oldversion_bi="$(cat ${fw_file} | grep ${prestr_bi})"
  if [[ -z $oldversion_bi ]]; then
    echo ${curr_bi} >> ${fw_file}
  else
    sed -i 's/'"${oldversion_bi}"'/'"${curr_bi}"'/g' ${fw_file}
  fi
}

if [ ! -f ${fw_file} ] ; then
  touch ${fw_file}
  echo ${curr_fw} >>${fw_file}
  echo ${curr_bi} >>${fw_file}
else
  str_replase
fi

# read the register and record the value to the log file
record_wdt_timeout_reg()
{
    wdt=$1
    addr=$2
    val=$(devmem ${addr} 32 2>&1)
    if [ $? -eq 0 ]; then
        logger -p DEBUG "${wdt}(${addr}) timeout status: ${val}."
    else
        logger -p DEBUG "failed to get ${wdt}(${addr}) timeout status: ${val}."
    fi
}

record_bmc_wdt_timeout_status()
{
    record_wdt_timeout_reg wdt1 0x1e785010
    record_wdt_timeout_reg wdt2 0x1e785050
    record_wdt_timeout_reg wdt3 0x1e785090
    record_wdt_timeout_reg wdt4 0x1e7850d0
    record_wdt_timeout_reg wdt5 0x1e785110
    record_wdt_timeout_reg wdt6 0x1e785150
    record_wdt_timeout_reg wdt7 0x1e785190
    record_wdt_timeout_reg wdt8 0x1e7851d0
}

# recored wdt1~wdt8 timeout status
record_bmc_wdt_timeout_status

#BMC boot, all data to backup
ast_backup_to_all_data
