#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions
current_fw_file="/var/log/fw/fw_version"
program_fpga_file="/usr/local/bin/program_fpga.sh"
program_8367_file="/usr/local/bin/program_8367.sh"
e2_5387_path="/sys/bus/spi/devices/spi2.0/eeprom"
e2_bcm53134_path="/sys/bus/spi/devices/spi0.0/eeprom"
g_e2_vlanswitch_path=""
# 0: mount BIOS, 2: mount 5387/bmc53134
MOUNT_5387_OBJECT=2
logger_indicate="path_test"

function do_help()
{
    echo "USAGE: $0 option"
    echo " e.g.: $0 [bios-slave|bios-master|bmc-slave|set-bios-version|bmc-master|set-bmc-version|change_bios_path|fpga_flash|5387_flash|8367_flash|88e6321_flash|bcm53134_flash]"
    echo " e.g.: $0 set-bios-version [version]"
    exit 1
}

function echo_message()
{
    message=$1
    echo $message
    logger -t ${logger_indicate} -p DEBUG $message
}

judge_is_support_bios()
{
  result=$(ast_product_func_call get_cpu_arch)
  arch_type=$?  #get sonic arch, 0: x86 1:arm
  if [ $arch_type -ne 0 ];then
    echo_message "cpu arch is arm or type illegal, type: $arch_type"
    exit -1
  fi
}

function firmware_mount_renew_bmc_slave_version()
{
    logger -t ${logger_indicate} -p DEBUG "get md5 of mtd3/9"
    dd if=/dev/mtd3 of=/tmp/fs1.img
    dd if=/dev/mtd9 of=/tmp/fs2.img
    tmp_fd1_md5=`md5sum /tmp/fs1.img|awk '{print $1}'`
    tmp_fd2_md5=`md5sum /tmp/fs2.img|awk '{print $1}'`
    rm /tmp/fs1.img
    rm /tmp/fs2.img
    logger -t ${logger_indicate} -p DEBUG "Determine whether the same version: ${tmp_fd1_md5}, ${tmp_fd2_md5}"
    if [ ${tmp_fd1_md5} == ${tmp_fd2_md5} ]; then
        #update slave bmc firmware version
        current_fw="$(cat ${current_fw_file} |grep master-bmc-fw|sed  's/master/slave/g')"
        echo ${current_fw}

        masterversion="$(cat ${current_fw_file} | grep master-bmc-fw)"
        echo ${masterversion}
        oldversion="$(cat ${current_fw_file} | grep slave-bmc-fw)"
        echo ${oldversion}
        if [[ -z $oldversion ]]; then
            echo ${current_fw} >> ${current_fw_file}
        else
            sed -i 's/'"${oldversion}"'/'"${current_fw}"'/g' ${current_fw_file}
        fi

        #update slave bmc bulidid
        current_bi="$(cat ${current_fw_file} |grep master-bmc-buildid|sed  's/master/slave/g')"
        echo ${current_bi}

        masterversion_bi="$(cat ${current_fw_file} | grep master-bmc-buildid)"
        echo ${masterversion_bi}
        oldversion_bi="$(cat ${current_fw_file} | grep slave-bmc-buildid)"
        echo ${oldversion_bi}
        if [[ -z $oldversion_bi ]];  then
            echo ${current_bi} >> ${current_fw_file}
        else
            sed -i 's/'"${oldversion_bi}"'/'"${current_bi}"'/g' ${current_fw_file}
        fi
        ast_backup_to_single_data $current_fw_file
        return 0
    else
        echo_message "failed to renew bmc slave version, due to inconsistent bmc versions"
        ast_backup_to_single_data $current_fw_file
        return -1
    fi
}

function change_flash_path()
{
    judge_is_support_bios
    change_to_flash=$1
    if [ ${change_to_flash} != "master" -a ${change_to_flash} != "slave" ]; then
        echo_message "failed to change to ${change_to_flash}, and illegal param: ${change_to_flash}"
        return -1
    fi
    logger -t ${logger_indicate} -p debug "change bios flash path: $1"
    sip_sel_reg=`ast_obmc_i2cget -f -y default 1 0x0d 0x20 fpga 6 0x0d 0x20 icelake 0 0x0d 0x23 icelakecto 0 0x0d 0x18 \
        bus14default 14 0x0d 0x20`
    if [ ${sip_sel_reg} == 0x00 ]; then
        if [ ${change_to_flash} == "master" ]; then
            change_log=$(ast_obmc_i2cset -f -y default 1 0x0d 0x22 0x00 fpga 6 0x0d 0x22 0x00 icelake 0 0x0d 0x24 0x00 \
                icelakecto 0 0x0d 0x19 0x00 bus14default 14 0x0d 0x22 0x00 2>&1)
        else
            change_log=$(ast_obmc_i2cset -f -y default 1 0x0d 0x22 0x01 fpga 6 0x0d 0x22 0x01 icelake 0 0x0d 0x24 0x01 \
                icelakecto 0 0x0d 0x19 0x01 bus14default 14 0x0d 0x22 0x01 2>&1)
        fi
    else
        if [ ${change_to_flash} == "master" ]; then
            change_log=$(ast_obmc_i2cset -f -y default 1 0x0d 0x22 0x01 fpga 6 0x0d 0x22 0x01 icelake 0 0x0d 0x24 0x01 \
                icelakecto 0 0x0d 0x19 0x01 bus14default 14 0x0d 0x22 0x01 2>&1)
        else
            change_log=$(ast_obmc_i2cset -f -y default 1 0x0d 0x22 0x00 fpga 6 0x0d 0x22 0x00 icelake 0 0x0d 0x24 0x00 \
                icelakecto 0 0x0d 0x19 0x00 bus14default 14 0x0d 0x22 0x00 2>&1)
        fi
    fi

    if [ $? != 0 ]; then
        echo_message "failed to change to ${change_to_flash}, log: $change_log"
        return -1
    else
        logger -t ${logger_indicate} -p debug "changed to ${change_to_flash} successfully"
        return 0
    fi
}

function change_flash_path_with_me()
{
    recovery_log=$(/usr/local/bin/bios.sh me recovery)
    if [ $? != 0 ]; then
        echo_message $recovery_log
        return -1
    fi
    change_flash_path $1
    result=$?
    reset_log=$(/usr/local/bin/bios.sh me reset)
    return $result
}

function display_flash_bios_mtd()
{
    echo 947 > /sys/class/gpio/export
    echo high > /sys/class/gpio/gpio947/direction
    echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/bind

    mtd_ret=$(cat /proc/mtd)
    mtd=$(echo "${mtd_ret}" | grep BIOS | cut -d ':' -f 1)
    if [[ $mtd == "" ]]; then
        output="scan BIOS mtd failed, ${mtd_ret}"
        logger -t ${logger_indicate} -p debug "$output"
    fi
    echo ${mtd}
}

function release_flash_bios_mtd()
{
    echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind
    echo 0 > /sys/class/gpio/gpio947/value
    echo 947 > /sys/class/gpio/unexport

}

function firmware_path_upgrade_bios()
{
    recovery_log=$(/usr/local/bin/bios.sh me recovery)
    if [ $? != 0 ]; then
        echo_message $recovery_log
        return -1
    fi
    tmp_image_file="/tmp/bios_image"
    # change flash
    change_ret=0
    if [ $1 == "master" ]; then
        change_flash_path master
        if [ $? != 0 ]; then
            change_ret=-1
        fi
    elif [ $1 == "slave" ]; then
        change_flash_path slave
        if [ $? != 0 ]; then
            change_ret=-1
        fi
    else
        echo_message "illegal param: $1"
        change_ret=-1
    fi
    if [ $change_ret -ne 0 ]; then
        reset_log=$(/usr/local/bin/bios.sh me reset)
        return -1
    fi

    logger -t ${logger_indicate} -p debug "judge whether bios channel exists"
    ast_product_func_call "judge_fw_channel_exist" "bios"
    if [ $? -ne 0 ];then
        echo_message "fw channel exist."
        reset_log=$(/usr/local/bin/bios.sh me reset)
        return -1
    fi

    logger -t ${logger_indicate} -p debug "add bios flash channel"
    curren_path_bios_flash=$(display_flash_bios_mtd)
    if [ -z ${curren_path_bios_flash} ]; then
        echo "scan BIOS mtd failed"
        reset_log=$(/usr/local/bin/bios.sh me reset)
        return -1
    fi
    echo /dev/${curren_path_bios_flash}
    logger -t ${logger_indicate} -p debug "read and write bios flash ..."
    dd if=/dev/${curren_path_bios_flash} of=${tmp_image_file} count=1 bs=1M
    dd if=${tmp_image_file} of=/dev${curren_path_bios_flash} count=1 bs=1M
    logger -t ${logger_indicate} -p debug "remove bios flash channel"
    release_flash_bios_mtd
    reset_log=$(/usr/local/bin/bios.sh me reset)
    return 0
}

function firmware_path_upgrade_bios_slave()
{
    firmware_path_upgrade_bios slave
    if [ $? == 0 ]; then
        return 0
    else
        return -1
    fi
}

function firmware_path_upgrade_bios_master()
{
    firmware_path_upgrade_bios master
    if [ $? == 0 ]; then
        return 0
    else
        return -1
    fi 
}

function firmware_path_upgrade_bmc_data()
{
	echo $1
	echo $2
    data0_mtd_char=$1
    data0_mtd_block=$2
    data0_mount_dir="/tmp/rw"

    [ -d $data0_mount_dir ] || mkdir -p $data0_mount_dir
    mount -t jffs2 $data0_mtd_block $data0_mount_dir 2>/dev/null
    # if the mount failed, format the partition and remount
    if [ $? -ne 0 ]
    then
        echo_message "retry: formatting $DATA_BLOCK_DEV and remounting."
        busybox flash_eraseall $data0_mtd_char
        mount -t jffs2 $data0_mtd_block $data0_mount_dir
    fi
    if [ $? -ne 0 ]
    then
        echo_message "mount -t jffs2  ${data0_mtd_block} ${data0_mount_dir} fail"
        return -1
    fi

    cd ${data0_mount_dir}
    echo test > test.txt
    sync
    tmp_test=`cat test.txt`
    echo ${tmp_test}
    rm test.txt
    cd /
    umount $data0_mtd_block
    rmdir ${data0_mount_dir}

    if [ ${tmp_test} == "test" ]; then
        return 0
    else
        echo_message "test failed, ${tmp_test} != test"
        return -1
    fi
}

function firmware_path_upgrade_bmc_master()
{
    cd /home/root
    echo test > test.txt
    sync
    tmp_test=`cat test.txt`
    echo ${tmp_test}
    rm test.txt
    cd /
    if [ ${tmp_test} == "test" ]; then
        return 0
    else
        return -1
    fi
}

function firmware_mount_renew_bios_slave_version()
{
    judge_is_support_bios
    if [ -z $1 ]; then
        echo_message "failed to renew bios slave version, and param is null: $1"
        ast_backup_to_single_data $current_fw_file
        return -1
    fi
    slave_prestr="slave-bios-fw"
    current_fw="${slave_prestr} : $1"
    echo ${current_fw}

    oldversion="$(cat ${current_fw_file} | grep ${slave_prestr})"
    echo ${oldversion}
    if [[ -z $oldversion ]]; then
        echo ${current_fw} >> ${current_fw_file}
    else
        sed -i "/^${slave_prestr}/c${current_fw}" ${current_fw_file}
    fi
    ast_backup_to_single_data $current_fw_file
    return 0
}

function add_fpga_mtd()
{
    ast_product_func_call switch_fpga_channel
    mtd=$(cat /proc/mtd | grep spi0.1 | cut -d ':' -f 1)
    if [[ $mtd == "" ]]; then
    # Scan fpga flash
        result=$(/usr/sbin/modprobe wb_spi_nor_device)
        mtd_ret=$(cat /proc/mtd)
        mtd=$(echo "${mtd_ret}" | grep spi0.1 | cut -d ':' -f 1)
        if [[ $mtd == "" ]]; then
            ast_product_func_call free_fpga_channel
            echo_message "scan fpga mtd failed, result: $result, ${mtd_ret}"
            return -1
        fi
    fi
}

function remove_fpga_mtd()
{
    logger -t ${logger_indicate} -p debug "remove fpag flash channel"
    result=$(/usr/sbin/rmmod wb_spi_nor_device)
    ast_product_func_call free_fpga_channel
    mtd_ret=$(cat /proc/mtd)
    mtd=$(echo "${mtd_ret}" | grep spi0.1 | cut -d ':' -f 1)
    if [[ $mtd != "" ]]; then
        echo_message "remove fpga mtd failed, result: $result, ${mtd_ret}"
        return -1
    fi
}

function fpga_flash_test()
{
    logger -t ${logger_indicate} -p debug "judge whether fpga channel exists"
    ast_product_func_call "judge_fw_channel_exist" "fpga"
    if [ $? -ne 0 ];then
        echo_message "failed, fw channel exist."
        return -1
    fi
    logger -t ${logger_indicate} -p debug "add fpag flash channel"
    add_fpga_mtd
    if [ $? -ne 0 ];then
        return -1
    fi
    logger -t ${logger_indicate} -p debug "read and write fpga flash ..."
    ${program_fpga_file} fpga_flash_test
    if [ $? -ne 0 ];then
        echo_message "fpga flash test failed"
        remove_fpga_mtd
        return -1
    fi
    logger -t ${logger_indicate} -p debug "fpga flash test successfully"
    remove_fpga_mtd
    if [ $? -ne 0 ];then
        return -1
    fi
}

function add_88e6321_path()
{
    ast_product_func_call get_88e6321_e2_bus
    g_bus_88e6321=$?
    if [ $g_bus_88e6321 == 0 ]; then
        echo_message "88e6321 does not exist，and exit"
        return -1
    fi
    cd /sys/class/gpio
    echo 109 > /sys/class/gpio/export
    cd gpio109
    echo out > direction
    echo 0 > value
    echo 24c02 0x50 > /sys/bus/i2c/devices/i2c-${g_bus_88e6321}/new_device
    g_e2_vlanswitch_path="/sys/bus/i2c/devices/${g_bus_88e6321}-0050/eeprom"
    if [ ! -e ${g_e2_vlanswitch_path} ];then
        echo_message "add 88e6321 path ${g_e2_vlanswitch_path} failed"
        return -1
    fi
}

function remove_88e6321_path()
{
    echo 0x50 > /sys/bus/i2c/devices/i2c-${g_bus_88e6321}/delete_device

    cd /
    echo 1 > /sys/class/gpio/gpio109/value
    echo 109 > /sys/class/gpio/unexport
    if [ -e ${g_e2_vlanswitch_path} ];then
        echo_message "remove 88e6321 path failed"
        return -1
    fi
}

function add_5387_path()
{
    cd /sys/class/gpio
    echo 109 > /sys/class/gpio/export
    cd gpio109
    echo out > direction
    echo 1 > value

    result=$(/usr/local/bin/scan-asdsmc add ${MOUNT_5387_OBJECT})
    g_e2_vlanswitch_path=${e2_5387_path}
    if [ ! -e ${g_e2_vlanswitch_path} ];then
        echo_message "add 5387 path failed, result: $result"
        return -1
    fi
}

function remove_5387_path()
{
    result=$(/usr/local/bin/scan-asdsmc remove ${MOUNT_5387_OBJECT})

    cd /
    echo 0 > /sys/class/gpio/gpio109/value
    echo 109 > /sys/class/gpio/unexport

    if [ -e ${g_e2_vlanswitch_path} ];then
        echo_message "remove 5387 path failed, result: $result"
        return -1
    fi
}

function add_bcm53134_path()
{
    result=$(/usr/sbin/modprobe wb_spi_93xx46)
    g_e2_vlanswitch_path=${e2_bcm53134_path}
    if [ ! -e ${g_e2_vlanswitch_path} ];then
        echo_message "add bcm53134 path failed, result: $result"
        return -1
    fi
}

function remove_bcm53134_path()
{
    result=$(/usr/sbin/rmmod wb_spi_93xx46)
    if [ -e ${g_e2_vlanswitch_path} ];then
        echo_message "remove bcm53134 path failed, result: $result"
        return -1
    fi
}

function flash_vlanswitch_test()
{
    tmp_path="/tmp/vlanswitch_dd_test"
    fw_type=$1
    logger -t ${logger_indicate} -p debug "judge whether ${fw_type} path exists"
    ast_product_func_call "judge_fw_channel_exist" ${fw_type}
    if [ $? -ne 0 ];then
        echo_message "${fw_type} channel exist."
        return -1
    fi

    # add and check eeprom path
    logger -t ${logger_indicate} -p debug "add and check ${fw_type} path"
    add_${fw_type}_path
    if [ $? -ne 0 ];then
        return -1
    fi

    logger -t ${logger_indicate} -p debug "read and write ${fw_type} e2 ..."
    dd if=${g_e2_vlanswitch_path} of=${tmp_path} count=1 bs=64
    if [ $? -ne 0 ]; then
        echo_message "dd if=${g_e2_vlanswitch_path} of=${tmp_path} count=1 bs=64 failed"
        rm -f ${tmp_path}
        remove_${fw_type}_path
        return -1
    fi

    dd if=${tmp_path} of=${g_e2_vlanswitch_path} count=1 bs=64
    if [ $? -ne 0 ]; then
        echo_message "dd if=${tmp_path} of=${g_e2_vlanswitch_path} count=1 bs=64 failed"
        rm -f ${tmp_path}
        remove_${fw_type}_path
        return -1
    fi
    rm -f ${tmp_path}
    logger -t ${logger_indicate} -p debug "remove and check ${fw_type} path"
    remove_${fw_type}_path
    if [ $? -ne 0 ];then
        return -1
    fi
    return 0
}

function flash_5387_test()
{
    flash_vlanswitch_test "5387"
    if [ $? != 0 ]; then
        return -1
    fi
    return 0
}

function flash_88e6321_test()
{
    flash_vlanswitch_test "88e6321"
    if [ $? != 0 ]; then
        return -1
    fi
    return 0
}

function flash_bcm53134_test()
{
    flash_vlanswitch_test "bcm53134"
    if [ $? != 0 ]; then
        return -1
    fi
    return 0
}

logger -t ${logger_indicate} -p debug "start $1 test"
case $1 in
    "bios-slave")
        firmware_path_upgrade_bios_slave
    ;;
    "bios-master")
        firmware_path_upgrade_bios_master
    ;;
    "set-bios-version")
        firmware_mount_renew_bios_slave_version $2
    ;;
    "bmc-slave")
        firmware_path_upgrade_bmc_data "/dev/mtd10" "/dev/mtdblock10"
    ;;
    "bmc-master")
        firmware_path_upgrade_bmc_data "/dev/mtd4" "/dev/mtdblock4"
    ;;
    "set-bmc-version")
        firmware_mount_renew_bmc_slave_version
    ;;
    "change_bios_path")
        change_flash_path_with_me $2
    ;;
    "fpga_flash")
        fpga_flash_test
    ;;
    "5387_flash")
        flash_5387_test
    ;;
    "88e6321_flash")
        flash_88e6321_test
    ;;
    "8367_flash")
        ${program_8367_file} flash_8367_test
    ;;
    "bcm53134_flash")
        flash_bcm53134_test
    ;;
    *)
        do_help
    ;; # help
esac

test_ret=$?
if [ $test_ret == 0 ]; then
    echo "success"
else
    echo "failed"
fi
logger -t ${logger_indicate} -p debug "end of $1 test, result code: $test_ret"
exit $test_ret
