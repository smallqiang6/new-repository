#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

# Check switch mtd, if mtd does not exist to scan, or not.
function check_switch_mtd()
{
  flash_alias=$2
  if [ -z "${flash_alias}" ]; then
    flash_alias="extflash1"
  fi
  mtd_ret=$(cat /proc/mtd)
  mtd=$(echo "${mtd_ret}" | grep "$flash_alias" | cut -d ':' -f 1)
  if [[ $mtd == "" ]]; then
    logger -p debug "scan $1 mtd failed, ${mtd_ret}"
    echo -1
    return -1
  fi
  echo ${mtd}
}


function get_md5sum()
{
  mtd=$(check_switch_mtd $@)
  if [ "$mtd" == "-1" ]; then
    logger -p debug "get $1 md5sum failed"
    return -1
  fi

  md5sum=$(md5sum /dev/$mtd|awk '{print $1}')
  echo $md5sum
  return 0
}

function upgrade_mac()
{
  upgrade_switch "mac" $1 "spi0.1"
}

function upgrade_atlas0()
{
  upgrade_switch "atlas0" $1
}

function upgrade_atlas1()
{
  upgrade_switch "atlas1" $1
}

function upgrade_rtl8372()
{
  upgrade_switch "rtl8372" $1
}

function upgrade_switch()
{
  fw_type=$1
  upd_bin=$2
  flash_alias=$3
  # Scan switch flash
  mtd=$(check_switch_mtd $fw_type ${flash_alias})
  if [ "$mtd" == "-1" ]; then
    logger -p debug "upgrade $fw_type failed"
    return -1
  fi
  # Update swtich flash
  # With busybox, the upgrade tool is designated as an older version of flashcp，BusyBox v1.24.1
  # Otherwise, upgrading with the flashcp in mtd-utils, 2.0.0, will fail
  upgrade_sw_result=$(busybox flashcp $upd_bin /dev/$mtd)
  if [[ $? == 0 ]] && [[ ! -n "$upgrade_sw_result" ]] && [[ "$upgrade_sw_result" != "\n" ]]; then
    logger -p debug "upgrade $fw_type mtd($mtd) success"
    return 0
  else
    logger -p debug "upgrade $fw_type mtd($mtd) failed"
    return -1
  fi
}

case $1 in
   "get_mac_md5sum")
      get_md5sum mac "spi0.1"
   ;;
   "get_atlas0_md5sum")
      get_md5sum atlas0
   ;;
   "get_atlas1_md5sum")
      get_md5sum atlas1
   ;;
   "get_rtl8372_md5sum")
      get_md5sum rtl8372
   ;;
   "upgrade_mac")
      upgrade_mac $2
   ;;
   "upgrade_atlas0")
      upgrade_atlas0 $2
   ;;
   "upgrade_atlas1")
      upgrade_atlas1 $2
   ;;
   "upgrade_rtl8372")
      upgrade_rtl8372 $2
   ;;
   *)
      echo "unknown arg"
   ;;
esac
