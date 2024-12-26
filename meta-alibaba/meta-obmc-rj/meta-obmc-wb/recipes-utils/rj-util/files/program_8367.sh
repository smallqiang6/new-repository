#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
. /usr/local/bin/ast-functions

e2_8367_path="/sys/bus/i2c/devices/13-0050/eeprom"
function releas_gpio()
{
  # To prevent repeated pulling of gpio
  gpio_path=/sys/class/gpio/gpio125
  if [ -d $gpio_path ]; then
    echo 0 > /sys/class/gpio/gpio125/value
    echo 125 > /sys/class/gpio/unexport
  fi
}

function delete_8367_channel()
{
  restult=$(ast_product_func_call disable_8367_channel)
  ret=$?
  if [ $ret != 0 ];then
    logger -p debug "disable 8367 channel failed, result: $ret"
  fi
  releas_gpio
  logger -p debug "delete 8367 channel successfully"
}
# Check 8367 mtd, if mtd does not exist to scan, or not.
function check_8367_channel()
{
  # To prevent repeated pulling of gpio
  releas_gpio

  # Pull up GPIO125 to enable 8367 channel
  echo 125 > /sys/class/gpio/export
  echo out > /sys/class/gpio/gpio125/direction
  echo 1 > /sys/class/gpio/gpio125/value

  restult=$(ast_product_func_call enable_8367_channel)
  ret=$?
  if [ $ret != 0 ];then
    logger -p debug "enable 8367 channel failed, result: $ret"
    releas_gpio
    exit -1
  fi

  if [ ! -f ${e2_8367_path} ];then
    logger -p debug "${e2_8367_path} no exist"
    delete_8367_channel
    exit -1
  fi
  logger -p debug "add 8367 channel successfully"
}

# upgrade process:
# 1.check 8367 bin
# 2.Scan 8367 channel
# 3.upgrade 8367 flash
# 4.releas gpio
function upgrade_8367()
{
  #check 8367 bin
  if [ ! -s ${1} ];then
    logger -p debug "${1} no exist or empty"
    exit -1
  fi

  # Scan 8367 channel
  check_8367_channel

  # upgrade 8367 flash
  restult=$(cat ${1} > ${e2_8367_path})
  ret=$?
  if [ $? == 0 ];then
    logger -p debug "upgrade 8367 success"
    delete_8367_channel
    exit 0
  else
    logger -p debug "upgrade 8367 failed, $ret, $restult"
    delete_8367_channel
    exit -1
  fi
}

function flash_8367_test()
{
  tmp_file="/tmp/8367_dd_test"

  # Scan 8367 channel
  check_8367_channel

  logger -p debug "read and wirte 8367 e2 ..."
  dd if=${e2_8367_path} of=${tmp_file} count=1 bs=1K
  if [[ $? != 0 ]]; then
    logger -p debug "dd if=${e2_8367_path} of=${tmp_file} count=1 bs=1K failed"
    rm -f ${tmp_file}
    delete_8367_channel
    exit -1
  fi

  dd if=${tmp_file} of=${e2_8367_path} count=1 bs=1K
  if [[ $? != 0 ]]; then
    logger -p debug "dd if=${tmp_file} of=${e2_8367_path} count=1 bs=1K failed"
    rm -f ${tmp_file}
    delete_8367_channel
    exit -1
  fi
  rm -f ${tmp_file}
  logger -p debug "remove 8367 channel"
  delete_8367_channel
  exit 0
}

function get_md5sum()
{
  check_8367_channel
  md5sum=$(md5sum ${e2_8367_path}|awk '{print $1}')
  echo $md5sum
  delete_8367_channel
  exit 0
}

case $1 in
   "upgrade_8367")
      upgrade_8367 $2
   ;;
   "get_md5sum")
      get_md5sum
   ;;
   "flash_8367_test")
      flash_8367_test
   ;;
   *)
      echo "unknown arg"
   ;;
esac
