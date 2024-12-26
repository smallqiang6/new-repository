#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

upgrade_bmc_result=""
BMC_IMAGE_SIZE=20971520 #20M
BMC_EREASE_SIZE=33554432 #32M
g_env_image=/tmp/env.img

# recovery usage
do_help() {
  echo "usage:"
  echo "  recovery dst_flash file_name"
  echo "    dst_flash : can be master or slave or normal"
  echo "    file_name : image file_name"
  echo " "
  exit
}

# view current flash
view_flash() {
  /usr/local/bin/switch_bmc.sh view_flash
}

get_upgrade_cmd() {
  flash_datapart=$1
  flash_dev=/dev/$2
  upgrade_file=$3
  cmd=""

  #Get the rootfs partition termination address, that is, the start address of data partition
  data_path="/sys/devices/platform/ahb/1e620000.spi/mtd/$flash_datapart/offset"
  data_offset=$(cat $data_path 2>/dev/null)
  if [[ $? -ne 0 ]]; then
    logger -p DEBUG "Warning : failed to cat $data_path!"
    return -1
  fi

  #If the rootfs partition termination address exceeds 32M, the entire flash will be erased completely
  image_size=`ls -l $upgrade_file | awk '{ print $5 }'`
  if [ $data_offset -gt $BMC_EREASE_SIZE -o $image_size -gt $BMC_EREASE_SIZE ]; then
    cmd="pflash -F $flash_dev -f -E -p $upgrade_file"
  else
    cmd="pflash -F $flash_dev -f -e -s $BMC_EREASE_SIZE -p $upgrade_file"
  fi
  echo $cmd
  return 0
}

store_env_mtd() {
  if [ -e $g_env_image ];then
    rm $g_env_image
  fi
  dd if=$1 of=$g_env_image 2>/dev/null
  if [ $? != 0 ]; then
    logger -p DEBUG "failed to store env mtd: $1"
    return -1
  fi
  logger -p DEBUG "store env mtd successfully: $1"
  return 0
}

#upgrade current flash to /dev/mtd5
#upgrade another flash to /dev/mtd11
update_bmc_flash() {
  #Judge whether the upgraded file is normal
  image_size=`ls -l $2 | awk '{ print $5 }'`
  if [[ $image_size -lt $BMC_IMAGE_SIZE ]] ; then
      logger -p DEBUG "Warning : image size $image_size is not 20MB, wrong image file !"
      return -1
  fi
  logger -p DEBUG "The size of image file($2): $image_size"

  #If the baudrate acquisition fails, the current baudrate is considered as the default value of 9600
  baud_env_orgn=$(/usr/local/bin/get-baudrate bmc)
  if [ $? != 0 ]; then
    logger -p DEBUG "Failed to get env baudrate, and default baud rate: 9600"
    baud_env_orgn=9600
  fi

  #Upgrade mode $3:  -e --upgrade master/slave bmc without retaining env
  #If the baudrate is 9600, it will be upgrade without retaining env
  if [[ $3 == "-e" || $baud_env_orgn == 9600 ]]; then
    g_retain_env=0
    logger -p DEBUG "Upgrading bmc without retaining original env, parm:$3, current baudrate: $baud_env_orgn"
  else
    g_retain_env=1
    logger -p DEBUG "Upgrading bmc with retaining original env, parm:$3, current baudrate: $baud_env_orgn"
  fi

  #Construct the command according to the flash to be upgraded
  if [ "$1"x == "normal"x ]; then
    g_env_mtd=/dev/mtd7
    upgrad_cmd=$(get_upgrade_cmd mtd10 mtd11 $2)
  else
    current_flash="$(view_flash)"
    if [ $? -ne 0 ]; then
      logger -p DEBUG "Warning : failed to get current bmc flash, $current_flash"
      return -1
    fi
    if [[ "${current_flash}" =~ "$1" ]] ; then
      g_env_mtd=/dev/mtd1
      upgrad_cmd=$(get_upgrade_cmd mtd4 mtd5 $2)
    else
      g_env_mtd=/dev/mtd7
      upgrad_cmd=$(get_upgrade_cmd mtd10 mtd11 $2)
    fi
  fi
  if [[ $? -ne 0 ]] || [[ -z $upgrad_cmd ]]; then
    return -1
  fi

  # store env
  if [ $g_retain_env -eq 1 ]; then
    store_env_mtd $g_env_mtd
    if [ $? != 0 ]; then
      return -1
    fi
  fi

  #Upgrade bmc flash
  logger -p DEBUG "Upgrade bmc upgrad_cmd: $upgrad_cmd"
  upgrade_bmc_result=`$upgrad_cmd`
  upgrade_bmc_ret=$?
  if [[ $upgrade_bmc_ret == 0 ]] && [[ -n "$upgrade_bmc_result" ]] && [[ "$upgrade_bmc_result" != "\n" ]]; then
    logger -p DEBUG "Upgrade bmc $1 successfully"
  else
    logger -p DEBUG "Failed to upgrade bmc $1"
    return -1
  fi

  # restore env
  if [ $g_retain_env -eq 1 ]; then
    restore_bmc_result=$(pflash -F $g_env_mtd -f -E -p $g_env_image)
    restore_env_ret=$?
    rm $g_env_image 2>/dev/null
    if [[ $restore_env_ret == 0 ]] && [[ -n "$restore_bmc_result" ]] && [[ "$restore_bmc_result" != "\n" ]]; then
      logger -p DEBUG "restore $g_env_mtd successfully"
    else
      logger -p DEBUG "failed to restore $g_env_mtd"
      return -1
    fi
  fi

  return 0
}

case "$1" in
  master | slave | normal)
    # Avoid upgrade be affected, umount mtd
    #ast_umount_mtd
    output_result=$(update_bmc_flash $1 $2 $3)
    ret_value=$(echo $?)
    ;;
  help)
    do_help
    ;;
  *)
    do_help
    ;;
esac

if [[ $ret_value == 0 ]]; then
 echo "success"
else
 echo "failed"
fi

# Because BMC to erase mtd, need to remount mtd and rebackup data
#ast_mount_mtd "/dev/mtd4" "/dev/mtdblock4" "/tmp/data0_ro"
#ast_mount_mtd "/dev/mtd10" "/dev/mtdblock10" "/tmp/data1_ro"
#ast_backup_to_all_data
