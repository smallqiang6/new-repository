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
  exit 1
}

judge_is_support_uboot()
{
  result=$(ast_product_func_call get_cpu_arch)
  arch_type=$?  #get sonic arch, 0: x86 1:arm
  if [ $arch_type -eq 0 ];then
    output="cpu arch is x86, unsupport operation"
    echo $output
    logger -p DEBUG $output
    return -1
  fi
}

function view_flash()
{
  judge_is_support_uboot
  if [ $? -ne 0 ];then
    exit -1
  fi

  result=$(ast_product_func_call uboot_view_flash)
  flash_type=$?  #flash type 0 :master 1 :slave others: err
  if [ ${flash_type} == 0 ]; then
    echo "master flash"
    return 0
  elif [ ${flash_type} == 1 ]; then
    echo "slave flash"
    return 1
  else
    echo "Reg unknown value ${FLASH}, failed."
    return 2
  fi
}

function switch()
{
  currentFlash=$(view_flash)
  result=$?
  switch_flash="master"
  if [[ $1 != 0 ]] && [[ $1 != 1 ]]; then
    echo "parameter error"
    do_help
  fi

  if [[ $result != 0 ]] && [[ $result != 1 ]]; then
    return 0
  fi

  case $1 in
    0)
      if [ $result == 0 ]; then
        echo "current flash --master flash,does not need switch"
        return 0
      fi
      switch_flash="master"
    ;;
    1)
      if [ $result == 1 ]; then
        echo "current flash --slave flash,does not need switch"
        return 0
      fi
      switch_flash="slave"
    ;;
    *)
       do_help
    ;; # help
  esac

  result=$(ast_product_func_call set_uboot_next_boot $switch_flash)
  ret=$?  #flash type 0 :master 1 :slave others: err
  if [ $ret == 0 ]; then
    echo y | plat_power cpu reset > /dev/null #bug解决后使用cycle
  else
    output="uboot switch $switch_flash flash failed, ret: $ret"
    echo $output
    logger -p DEBUG $output
    return -1
  fi
}

case $1 in
  "view_flash")
    view_flash
    result=$(echo $?)
    if [[ $result == 1 ]] || [[ $result == 0 ]]; then
      exit 0
    else
      exit -1
    fi
  ;;
  "switch")
    if [ $# != 2 ]; then
      echo "parameter error"
      do_help
    fi
    switch $2
  ;;
  *)
    echo "parameter error"
    do_help
  ;; # help
esac
