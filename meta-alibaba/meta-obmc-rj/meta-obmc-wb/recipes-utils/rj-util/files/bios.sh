#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
. /usr/local/bin/ast-functions
function do_help ()
{
  echo "USAGE: $0 funtion chipnum"
  echo " e.g.: $0 switch 0/1"
  echo " e.g.: $0 view_flash"
  echo " e.g.: $0 me status/recovery/reset"
  echo " e.g.: $0 reset_rtc"
  exit 1
}

judge_is_support_bios()
{
  result=$(ast_product_func_call get_cpu_arch)
  arch_type=$?  #get sonic arch, 0: x86 1:arm
  if [ $arch_type -ne 0 ];then
    output="cpu arch is arm, unsupport operation"
    echo $output
    logger -p DEBUG $output
    return -1
  fi
}

function view_flash()
{
  judge_is_support_bios
  if [ $? -ne 0 ];then
    exit -1
  fi
  if [[ ! -e $BMC_SYSFS_BIOS_VIEW_PATH ]]; then
    echo "$BMC_SYSFS_BIOS_VIEW_PATH does not exist"
    return 2
  fi

  FLASH=$(cat $BMC_SYSFS_BIOS_VIEW_PATH)
  result=$(echo $?)
  if [ ${result} != 0 ]; then
    echo "get bios flash fail. result=${result}"
    return 2
  elif [ "${FLASH}" == "NA" ]; then
    echo "get bios flash not support"
    return 2
  fi

  if [ ${FLASH} == 0 ]; then
    echo "master flash"
    return 0
  elif [ ${FLASH} == 1 ]; then
    echo "slave flash"
    return 1
  else
    echo "Reg unknown value, bios may not started yet, please check ! bios_view = ${FLASH}"
    return 2
  fi
}

function switch()
{
  currentFlash=$(view_flash)
  result=$(echo $?)

  if [[ $1 != 0 ]] && [[ $1 != 1 ]]; then
    echo "parameter error"
    do_help
  fi

  if [[ $result != 0 ]] && [[ $result != 1 ]]; then
    echo "$currentFlash"
    return 0
  fi

  if [[ ! -e $BMC_SYSFS_BIOS_SWITCH_PATH ]]; then
    echo "$BMC_SYSFS_BIOS_SWITCH_PATH does not exist"
    return 0
  fi
  recovery_log=$(me recovery)
  recovery_ret=$?
  if [ $recovery_ret != 0 ]; then
    echo $recovery_log
    return 0
  fi
  echo $((~result & 1)) > $BMC_SYSFS_BIOS_SWITCH_PATH
  switch_result=$(echo $?)
  reset_log=$(me reset)
  if [[ $switch_result != 0 ]]; then
    return 0
  fi
  echo y | plat_power cpu cycle > /dev/null
}

function judge_is_me_required()
{
  result=$(ast_product_func_call get_is_me_required)
  me_required=$?  # 0: not required, 1 required
  if [ $me_required -ne 1 ];then
    echo "No need to set or get me status. Skip!"
    return -1
  fi
  return 0
}

function me_status()
{
  result=$(ast_product_func_call get_me_status)
  me_ret=$?
  case $me_ret in
    1)
      status="initialization"
    ;;
    2)
      status="recovery"
    ;;
    5)
      status="operational"
    ;;
    *)
      status="unknown"
    ;;
  esac
  echo $status
  return $me_ret
}

function me_stability()
{
  stability_log=$(ast_product_func_call get_me_stability)
  stability_ret=$?
  if [ $stability_ret -eq 1 ]; then
    echo "stable"
  elif [ $stability_ret -eq 0 ]; then
    echo "instable"
  else
    echo "unknown"
  fi
  return $stability_ret
}

function check_me_status()
{
  target_status=$1
  me_changed=0
  for i in {1..30}
  do
    # Check whether me status changes
    if [ $me_changed -eq 0 ]; then
      current_status=$(me_status)
      if [[ $current_status =~ $target_status ]]; then
        me_changed=1
        check_success="try $i times, and me reached the target status: $target_status"
        logger -p DEBUG $check_success
      else
        sleep 1
        continue
      fi
    fi
    # Check whether me status is stable
    stability=$(me_stability)
    if [ $stability == "stable" ]; then
      stable_status="try $i times, and me reached the stable target status: $target_status"
      logger -p DEBUG $stable_status
      return 0
    fi
    sleep 1
  done
  if [ $me_changed -eq 0 ]; then
    stability=$(me_stability)
  fi
  check_fail="try $i times, current me status: $current_status, target status: $target_status, stability: $stability, please check!"
  echo $check_fail
  logger -p DEBUG $check_fail
  return -1
}

function me_recovery()
{
  ast_product_func_call me_recovery
  if [ $? != 0 ]; then
    echo "failed to set me recovery by cpld"
    return 1
  fi
  check_status_log=$(check_me_status recovery)
  if [ $? -eq 0 ]; then
    echo "set me recovery success"
    return 0
  else
    echo "failed to set me recovery, $check_status_log"
    return 2
  fi
}

function me_reset()
{
  ast_product_func_call me_reset
  if [ $? != 0 ]; then
    echo "failed to reset me by cpld"
    return 1
  fi
  check_status_log=$(check_me_status operational)
  if [ $? -eq 0 ]; then
    echo "reset me success"
    return 0
  else
    echo "failed to reset me, $check_status_log"
    return 2
  fi
}

function me()
{
  judge_is_me_required
  if [ $? -ne 0 ];then
    exit 0 # skip, and return default success
  fi
  case $1 in
    "status")
      me_status
    ;;
    "recovery")
      me_recovery
    ;;
    "reset")
      me_reset
    ;;
    *)
      do_help
    ;;
  esac
}

function judge_is_support_reset_rtc()
{
  # 1: support this function, 0: unsupport
  ast_product_func_call get_is_support_reset_rtc
  if [ $? -ne 1 ]; then
    output="reset rtc: not supported"
    echo $output
    logger -p DEBUG $output
    return -1
  fi
  return 0
}

function reset_rtc_7_0()
{
  # power off cpu
  pwr_cpu_off=$(echo y | plat_power cpu off)
  if [[ ${pwr_cpu_off} =~ "failed" ]]; then
    echo ${pwr_cpu_off}
    output="failed to power off cpu and reset rtc"
    echo $output
    logger -p DEBUG $output
    exit -1
  else
    echo "power off cpu done"
  fi

  # disable ocm
  ast_product_func_call disable_ocm
  if [ $? -ne 0 ]; then
    echo "failed to disable ocm"
    echo "failed to reset rtc"
    echo y | plat_power cpu on
    exit -1
  else
    echo "disable ocm done"
  fi

  # Disconnect RTC power supply and release
  ast_product_func_call release_rtc
  if [ $? -ne 0 ]; then
    echo "failed to disconnect RTC power supply and release"
    failed_flag=1
  else
    echo "release rtc done"
  fi

  # enable ocm
  ast_product_func_call enable_ocm
  if [ $? -ne 0 ]; then
    echo "failed to enable ocm"
    failed_flag=1
  else
    echo "enable ocm done"
  fi

  # power on cpu
  pwr_cpu_on=$(echo y | plat_power cpu on)
  if [[ ${pwr_cpu_on} =~ "failed" ]]; then
    echo ${pwr_cpu_on}
    logger -p DEBUG "failed to power on cpu"
    failed_flag=1
  else
    echo "power on cpu done"
  fi
}

function reset_rtc_6_0()
{
  ast_product_func_call release_rtc
  if [ $? -ne 0 ]; then
    echo "failed to disconnect RTC power supply and release"
    failed_flag=1
  else
    echo "reset rtc done, and power cycle cpu automatically"
  fi
}

function reset_rtc()
{
  judge_is_support_reset_rtc
  if [ $? -ne 0 ];then
    exit -1 # unsupported operation
  fi
  failed_flag=0

  # get product type
  ast_product_func_call get_product_type
  type=$?
  reset_rtc_${type}_0
  if [ $? -ne 0 ]; then
    failed_flag=1
  fi

  if [ $failed_flag -ne 0 ]; then
    output="failed to reset rtc"
    ret=-1
  else
    output="reset rtc success"
    ret=0
  fi
  echo $output
  logger -p DEBUG $output
  return $ret
}

case $1 in
  "view_flash")
    view_flash
    result=$(echo $?)
    if [[ $result == 1 ]] || [[ $result == 0 ]]; then
      exit 0
    fi
  ;;
  "switch")
    if [ $# != 2 ]; then
      echo "parameter error"
      do_help
    fi
    switch $2
  ;;
  "me")
    if [ $# != 2 ]; then
      echo "parameter error"
      do_help
    fi
    me $2
  ;;
  "reset_rtc")
    reset_rtc
  ;;
  *)
    echo "parameter error"
    do_help
  ;; # help
esac

