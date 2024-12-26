#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

fw_file="/var/log/fw/fw_version"
if [ ! -d "/var/log/fw" ]; then
  mkdir /var/log/fw
fi

if [ $# -lt 2 ]; then
  echo "BIOS version cannot be set"
  exit 1
fi

if [ "$1"x != "master"x -a "$1"x != "slave"x ]; then
  echo "Warning : $1 parameter error."
  exit 1
fi

bios_version="$2"
bios_flash="$1"
bios_fw="${bios_flash}-bios-fw"
current_fw="${bios_fw} : ${bios_version}"

# find and replace
str_replase() {
  oldversion="$(cat ${fw_file} | grep ${bios_fw})"
  if [[ -z $oldversion ]]; then
    echo ${current_fw} >> ${fw_file}
  else
    sed -i "/^${bios_fw}/c${current_fw}" ${fw_file}
  fi
}

if [ ! -f ${fw_file} ] ; then
  touch ${fw_file}
  echo ${current_fw} >>${fw_file}
else
  str_replase
fi
#backup bios version
ast_backup_to_single_data $fw_file
