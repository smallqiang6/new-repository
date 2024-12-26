#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

# Check fpga mtd, if mtd does not exist to scan, or not.
function check_fpga_mtd()
{
  # Scan fpga flash
    mtd_ret=$(cat /proc/mtd)
    mtd=$(echo "${mtd_ret}" | grep spi0.1 | cut -d ':' -f 1)
  if [[ $mtd == "" ]]; then
    logger -p debug "scan fpga mtd failed, "${mtd_ret}""
    echo -1
    return -1
  fi
  echo ${mtd}
}

# upgrade process:
# 1.check fpga power on or not
# 2.force switch of fpga channel
# 3.mount fpga
# 4.flascp fpga
# 5.permission to release
function upgrade_fpga()
{
  # Scan fpga flash
  mtd=$(check_fpga_mtd)
  if [ "$mtd" == "-1" ]; then
    logger -p debug "upgrade fpga failed"
    return -1
  fi
  # Update fpga flash
  # With busybox, the upgrade tool is designated as an older version of flashcp，BusyBox v1.24.1
  # Otherwise, upgrading with the flashcp in mtd-utils, 2.0.0, will fail
  upgrade_fpga_result=$(busybox flashcp $1 /dev/$mtd)
  if [[ $? == 0 ]] && [[ ! -n "$upgrade_fpga_result" ]] && [[ "$upgrade_fpga_result" != "\n" ]]; then
    logger -p debug "upgrade fpga mtd($mtd) success"
    return 0
  else
    logger -p debug "upgrade fpga mtd($mtd) failed"
    return -1
  fi
}

function fpga_flash_test()
{
  tmp_file="/tmp/fpga_dd_test"
  # Scan fpga flash
  mtd=$(check_fpga_mtd)
  if [ "$mtd" == "-1" ]; then
    logger -p debug "fpga flash test failed"
    return -1
  fi

  dd if=/dev/$mtd of=${tmp_file} count=1 bs=1K
  if [[ $? != 0 ]]; then
    logger -p debug "dd if=/dev/$mtd of=${tmp_file} count=1 bs=1K failed"
    rm -f ${tmp_file}
    return -1
  fi

  dd if=${tmp_file} of=/dev/$mtd count=1 bs=1K
  if [[ $? != 0 ]]; then
    logger -p debug "dd if=${tmp_file} of=/dev/$mtd count=1 bs=1K failed"
    rm -f ${tmp_file}
    return -1
  fi
  rm -f ${tmp_file}
  return 0
}

function get_md5sum()
{
  mtd=$(check_fpga_mtd)
  if [ "$mtd" == "-1" ]; then
    logger -p debug "get flash md5sum failed"
    return -1
  fi

  md5sum=$(md5sum /dev/$mtd|awk '{print $1}')
  echo $md5sum
  return 0
}

case $1 in
   "upgrade_fpga")
      upgrade_fpga $2
   ;;
   "get_md5sum")
      get_md5sum
   ;;
   "fpga_flash_test")
      fpga_flash_test
   ;;
   *)
      echo "unknown arg"
   ;;
esac
