#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

function do_help()
{
    echo "USAGE: $0 option"
    echo " e.g.: $0 switch bmc"
    echo " e.g.: $0 switch bios 0/1"
    echo " e.g.: $0 switch uboot 0/1"
    echo " e.g.: $0 view_flash [bmc|bios|uboot]"
    echo " e.g.: $0 upgrade [bmc|bios] image [master|slave]"
    echo " e.g.: $0 port led normal/byellow/bgreen/syellow/sgreen/status/location/recover"
    exit 1
}

function do_view_flash()
{
    /usr/local/bin/switch_bmc.sh view_flash
}

function do_port_led()
{
    if [ "$1"x != "led"x ]; then
        do_help
    fi

    case $2 in
      "normal")
        product_location_led_normal
      ;;
      "byellow")
        product_location_led_byellow
      ;;
      "bgreen")
        product_location_led_bgreen
      ;;
      "syellow")
        product_location_led_syellow
      ;;
      "sgreen")
        product_location_led_sgreen
      ;;
      "location")
        product_location_led_location
      ;;
      "recover")
        product_location_led_recover
      ;;
      "status")
        product_location_led_status
      ;;
      *)
       do_help
      ;; # help
    esac
}

function switch_bmc()
{
  current_flash="$(do_view_flash)"
  echo -ne "Current $current_flash, are you sure switch flash [y/n]:"
  read tmp_value
  case "$tmp_value" in
    "y" | "Y" | "yes")
      /usr/local/bin/switch_bmc.sh
    ;;
    *)
      exit 0
    ;;
  esac
}

function switch_flash_bios()
{
  case "$1" in
    "y" | "Y" | "yes")
      if [ "$2"x == "master"x ]; then
        /usr/local/bin/bios.sh switch 0
      else
        /usr/local/bin/bios.sh switch 1
      fi
    ;;
    *)
      exit 0
    ;;
  esac
}

function switch_flash_uboot()
{
  case "$1" in
    "y" | "Y" | "yes")
      if [ "$2"x == "master"x ]; then
        /usr/local/bin/host_uboot.sh switch 0
      else
        /usr/local/bin/host_uboot.sh switch 1
      fi
    ;;
    *)
      exit 0
    ;;
  esac
}

function switch_bios()
{
  master_flash="master"
  slave_flash="slave"
  current_flash="$(/usr/local/bin/bios.sh view_flash)"
  if [ $? -eq 255 ];then
    echo $current_flash
    exit -1
  fi
  case $1 in
    0)
      echo -ne "Current $current_flash, are you sure switch flash [y/n]:"
      read tmp_value
      switch_flash_bios $tmp_value $master_flash
    ;;
    1)
      echo -ne "Current $current_flash, are you sure switch flash [y/n]:"
      read tmp_value
      switch_flash_bios $tmp_value $slave_flash
    ;;
    *)
      echo "parameter error"
      do_help
    ;;
  esac
}

function switch_uboot()
{
  master_flash="master"
  slave_flash="slave"
  current_flash="$(/usr/local/bin/host_uboot.sh view_flash)"
  if [ $? -eq 255 ];then
    echo $current_flash
    exit -1
  fi
  case $1 in
    0)
      echo -ne "Current $current_flash, are you sure switch flash [y/n]:"
      read tmp_value
      switch_flash_uboot $tmp_value $master_flash
    ;;
    1)
      echo -ne "Current $current_flash, are you sure switch flash [y/n]:"
      read tmp_value
      switch_flash_uboot $tmp_value $slave_flash
    ;;
    *)
      echo "parameter error"
      do_help
    ;;
  esac
}


function switch_flash()
{
  tmp_flash=$2
  case $1 in
    "bmc")
      switch_bmc
    ;;
    "bios")
      switch_bios $tmp_flash
    ;;
    "uboot")
      switch_uboot $tmp_flash
    ;;
    *)
      echo "parameter error"
      do_help
    ;;
  esac
}

function bmc_bios_view_flash()
{
  case $1 in
    "bmc")
      do_view_flash
    ;;
    "bios")
      /usr/local/bin/bios.sh view_flash
    ;;
    "uboot")
      /usr/local/bin/host_uboot.sh view_flash
    ;;
    *)
      echo "parameter error"
      do_help
    ;;
  esac
}

function upgrade_firmware()
{
    # bmc or bios image check
    if [ ! -s $2 ]; then
        echo "image($2) does not exist or empty"
        exit
    fi
    # bmc or bios flash(master|slave) check
    if [ "$3"x != "master"x -a "$3"x != "slave"x ] ; then
        echo "flash($3) must be master|slave"
        exit
    fi
    # upgrade bmc or bios
    case $1 in
      "bmc")
          # $4 == -e: upgrade master/slave bmc without retention env
          /usr/local/bin/program_bmc.sh $3 $2 $4
      ;;
      "bios")
          /usr/local/bin/upgrade_bios.sh $3 $2
      ;;
       *)
          do_help
       ;; # help
    esac
}

case $1 in
   "view_flash")
        if [ $# -gt 2 ]; then
           echo "failed, parameter error"
           do_help
        fi
        if [ $# == 2 ]; then
           bmc_bios_view_flash $2
        else
           do_view_flash
        fi
   ;;
   "port")
        if [ $# != 3 ]; then
            echo "parameter error"
            do_help
        fi
        do_port_led $2 $3
   ;;
   "switch")
        if [ $# == 2 ]; then
          switch_flash $2
        elif [ $# == 3 ]; then
          switch_flash $2 $3
        else
          echo "parameter error"
          do_help
        fi
   ;;
   "upgrade")
        if [ $# != 4  -a $# != 5 ]; then
          echo "parameter error"
          do_help
        fi
        upgrade_firmware $2 $3 $4 $5
   ;;
   *)
        do_help
   ;; # help
esac
