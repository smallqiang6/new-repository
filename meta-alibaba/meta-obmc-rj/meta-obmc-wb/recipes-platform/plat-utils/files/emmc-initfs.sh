#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

MTD4_BACKUP_PATH="/tmp/data0_ro/fw"
MTD10_BACKUP_PATH="/tmp/data1_ro/fw"
FS_ERR_BLOCK="Bad magic number in super-block"
FS_ERR_INODE="Resize inode not valid."
FS_ERR_FS="a file system with errors"
FS_ERR_UNEXP="UNEXPECTED INCONSISTENCY"
EMMC_ERR_LIST="${FS_ERR_BLOCK}|${FS_ERR_INODE}|${FS_ERR_FS}|${FS_ERR_UNEXP}"

echomsg() {
    logger -p debug -t emmc-initfs.sh "$@"
}

_log_msg()
{
    if [ "$quiet" = "y" ]; then
        printf "$@\n"
    fi    
}

log_begin_msg()
{
    _log_msg "Begin $@...\n"
}

log_end_msg()
{
    _log_msg "Done $@\n\n"
}

check_retval()
{
    error_value="${?}"

    if [ ${error_value} = 0 ]; then
        return 0
    else
        echomsg "ERROR: $1"
        exit 0
    fi
}

check_program()
{
    for cmd in "$@"
    do
        which ${cmd} > /dev/null 2>&1
        if [ $? -ne 0 ]
        then
            echomsg "ERROR: ${cmd} is not found"
            exit 0
        fi
    done
}

get_mmc_size()
{
    part_name=$1
    mmc_size=`fdisk -l ${part_name} | grep "Disk $part_name:" | awk '{print $5}'`
    r_size=$((${mmc_size}/1024/1024))
    return 0
}

get_fstab_type()
{
    ret=$(cat /etc/fstab | grep "/dev/mmcblk0p1" |  wc -l )
    if [ $ret == 1 ]; then
        return 1 #旧品
    else
        return 2 #新品
    fi
}

mmc_make_part()
{
    part_name=$1
    size1=$2"M"
    size2=$3"M"
    fdisk ${part_name} 2>&1 1>/dev/null  << EOF
    d
    1
    d
    2
    d
    3
    d
    n
    p
    1
    
    +${size1}
    n
    p
    2
    
    
    w
EOF
    return $?
}

mmc_do_part()
{
    part_name=$3
    #make two part
    part_name1=$4
    part_name2=$5
    logger -p debug -t emmc-init.sh  ${part_name1} ${part_name2}
    if [ -b ${part_name1} ] && [ -b ${part_name2} ]; then
        _log_msg "Emmc parts already done."
        return 0
    fi

    echomsg "Do parts..."
    rsize=$1
    size1=$2
    if [ ${rsize} -gt ${size1} ]; then
        size2=$((${rsize}-${size1}))
    else
        size1=$((${rsize}>>1))
        size2=$((${rsize}-${size1}))
    fi

    echomsg "Part ${part_name}: ${size1} ${size2}"
    for((i=1;i<=3;i++));  
    do   
        mmc_make_part ${part_name} ${size1} ${size2}
        if [ $? -eq 0 ]; then
            echo "Success."
            #set format flag
            is_part_flag=1
            return 0
        fi
        echomsg "Try again..."
    done
    echomsg "ERROR: Failed to do part."
    exit 0
}

emmc_change_system_coredump()
{
    old_path="/var/lib/systemd/coredump"
    new_path=$2"/var/lib/systemd/coredump"
    mount_path=$2
    part_name=$1

    output_log=$(mount | grep $mount_path | grep $part_name)
    if [ ! -n "$output_log" ]; then
        echomsg "No change system coredump"
        return 0
    fi

    if [ ! -d ${new_path} ]; then
        mkdir -p ${new_path}
    fi

    if [ -h ${old_path} ]; then
        echomsg "Coredump already change"
        return 0
    fi

    if [ -d ${old_path} ]; then
        rm -rf ${old_path}
    fi

    ln -s ${new_path} ${old_path}
    echomsg "Charnge coredump directory"
}

#mount mtd4 and mtd10
function mount_data()
{
    data_mtd_char=$1
    data_mtd_block=$2
    data_mount_dir=$3

    [ -d $data_mount_dir ] || mkdir -p $data_mount_dir
    #do not user bmc flash to backup
    return
    count=1
    while [ $count -le 3 ]; do
        mount -t jffs2 $data_mtd_block $data_mount_dir 2>/dev/null
        # if the mount failed, format the partition and remount
        if [ $? -ne 0 ]; then
            echo "Mount failed; formatting $data_mtd_char and remounting."
            busybox flash_eraseall $data_mtd_char
            mount -t jffs2 $data_mtd_block $data_mount_dir 2>/dev/null
        fi
        output=$(mount | grep $data_mtd_block)
        if [ ! -n "$output" ]; then
            echo "mount -t jffs2  ${data_mtd_block} ${data_mount_dir} fail"
        else
            break
        fi
        count=`expr $count + 1`
    done
}

#umount mtd4 and mtd10
function umount_data()
{
    mount_path=$1
    part_name=$2

    #do not umount because it does not  mount
    return 0
    if [ ! -d "${mount_path}" ]; then
        echomsg "${mount_path} no exist,return"
        return 0
    fi

    count=1
    while [ $count -le 3 ]; do
        umount -l ${mount_path}
        error_value=$?
        if [ ${error_value} -eq 0 ]; then
            return 0
        fi
        count=`expr $count + 1`
    done
    return 0
}

function reformat_emmc()
{
    count=1
    while [ $count -le 3 ]; do
        mkfs.ext4 -F $1 2>/dev/null
        e2fsck -a $1 2>/dev/null
        mount -o rw $1 $2 2>/dev/null
        output=$(mount | grep $1)
        if [ ! -n "$output" ]; then
            echo "reformat $1 fail, retry $count times"
        else
            return 0
        fi
        count=`expr $count + 1`
    done

    return 1
}


function fw_file_update()
{
    fw_dir1="/var/volatile/fw"
    fw_dir2="/var/volatile/log/fw"

    if [ -d $fw_dir2 ];then
        return
    elif [ -d $fw_dir1 ];then
        result=$(cp $fw_dir1 $fw_dir2 -rf -a)
        echomsg "cp $fw_dir1 to $fw_dir2, result: $?"
        return
    else
        echomsg "$fw_dir1 $fw_dir2 no exist"
    fi
}

function wait_emmc_partition()
{
    count=0
    max_count=20
    fstab_type=$1
    if [ $fstab_type == 1 ]; then
        while [ $count -lt $max_count ]
        do
            local part1=$(mount | grep "/dev/mmcblk0p1" | grep "/var/volatile" | wc -l)
            local part2=$(mount | grep "/dev/mmcblk0p2" | grep "/data" | wc -l)
            if [ $part1 -eq 1 ]&&[ $part2 -eq 1 ];then
                break
            else
                sleep 3s
                let count+=1
            fi
        done

        if [ $count -eq $max_count ];then
            part1=$(mount | grep "/dev/mmcblk0p1" | grep "/var/volatile" | wc -l)
            part2=$(mount | grep "/dev/mmcblk0p2" | grep "/data" | wc -l)
            echomsg "wait emmc_partition time: timeout. part1: $part1 part2: $part2"
        else
            echomsg "wait emmc_partition time: $count *3s"
        fi
    else
        while [ $count -lt $max_count ]
        do
            local part=$(mount | grep "/dev/mmcblk0 " | grep "/var/volatile" | wc -l)
            if [ $part -eq 1 ];then
                break
            else
                sleep 3s
                let count+=1
            fi
        done

        if [ $count -eq $max_count ];then
            part=$(mount | grep "/dev/mmcblk0 " | grep "/var/volatile" | wc -l)
            echomsg "wait emmc_partition time: timeout. part: $part"
        else
            echomsg "wait emmc_partition time: $count *3s"
        fi
    fi
}

function check_emmc_path()
{
    local path=$1

    if [ ! -d $path ];then
        echomsg "$path no exist, creat it"
        mkdir -p $path
    fi
}

function e2fsck_check()
{
    local e2fsck_err_num=$(e2fsck -a $1 2>&1 | grep -E "${EMMC_ERR_LIST}" | wc -l)
    return $e2fsck_err_num
}

function check_emmc_partition_status()
{
    part_name=$1
    mount_path=$2
    part_num=$(mount | grep "${mount_path}" | grep "${part_name}" | wc -l)
    e2fsck_check ${part_name}
    judge_err_num=$?
    if [ $part_num -eq 0 -a $judge_err_num -ne 0 ];then
        echomsg "ERROR: $judge_err_num error(s) in $part_name"
        fsck -y "${part_name}" > /dev/null
        e2fsck_check ${part_name}
        if [ $? -ne 0 ];then
            echomsg "ERROR: Failed to repair $part_name"
            reformat_emmc ${part_name} ${mount_path}
            if [ $? -ne 0 ]; then
                echomsg "ERROR: Failed to reformat ${part_name}."
                return 1
            fi
        fi
        is_reboot_flag=1
        echomsg "check partition ${part_name} done."
        return 0
    fi
}

function do_mount()
{
    get_fstab_type
    type=$?
    if [ $type == 1 ]; then
        do_mount_for_5_2_product $type
    else
        do_mount_for_6_0_product $type
    fi
}

function do_mount_for_5_2_product()
{
    part=/dev/mmcblk0
    part1=${part}"p1"
    part2=${part}"p2"
    path1=/var/volatile
    path2=/data
    fstab_type=$1

    r_size=0
    part1_size=4000

    mkdir -p $MTD4_BACKUP_PATH
    mkdir -p $MTD10_BACKUP_PATH

    #when make part, need to format the parts,
    is_part_flag=0
    is_reboot_flag=0

    if [ ! -b ${part} ]; then
        echomsg "No support mmc block!!!"
        return
    fi

    get_mmc_size ${part}

    #two part: 1-/var/volatile/log, size 4G; 2-/data, size: real_size-4G
    mmc_do_part ${r_size} ${part1_size} ${part} ${part1} ${part2}

    #check emmc partition status
    check_emmc_partition_status ${part1} ${path1}
    check_emmc_partition_status ${part2} ${path2}

    if [ $is_reboot_flag -eq 1 ]; then
        reboot
    fi

    check_emmc_path $path1
    check_emmc_path $path2

    #wait emmc partition mount
    wait_emmc_partition $fstab_type

    check_emmc_path ${path1}"/log"

    #upgrade fw dir
    fw_file_update
    emmc_change_system_coredump ${part2} ${path2}
    sync
    #check_emmc_mount_status
}

function check_emmc_for_no_partition()
{
    local part=$1
    local path=$2
    local part1=${part}"p1"
    local part2=${part}"p2"
    if [ -b ${part1} ] || [ -b ${part2} ]; then
        echomsg "There are partitions in EMMC, and reformat it"
        reformat_emmc ${part} ${path}
        if [ $? -ne 0 ]; then
            echomsg "ERROR: Failed to reformat ${part}."
            return 1
        fi
        echomsg "Reformat ${part} done."
        is_reboot_flag=1
        return 0
    fi
}

function do_mount_for_6_0_product()
{
    part=/dev/mmcblk0
    path=/var/volatile
    fstab_type=$1
    is_part_flag=0
    is_reboot_flag=0
    mkdir -p $MTD4_BACKUP_PATH
    mkdir -p $MTD10_BACKUP_PATH

    if [ ! -b ${part} ]; then
        echomsg "No support mmc block!!!"
        return
    fi

    #check emmc partition number
    check_emmc_for_no_partition $part $path

    check_emmc_partition_status ${part} ${path}
    if [ $is_reboot_flag -eq 1 ]; then
        reboot
    fi

    check_emmc_path ${path}

    #wait emmc partition mount
    wait_emmc_partition  $fstab_type
    check_emmc_path ${path}"/log"

    #upgrade fw dir
    fw_file_update
    emmc_change_system_coredump ${part} ${path}
    sync
}

function do_umount()
{
    part=/dev/mmcblk0
    #part1=${part}"p1"
    #part2=${part}"p2"
    #path1=/var/volatile/log
    #path2=/data
    umount_data "/tmp/data1_ro" "/dev/mtdblock10"
    umount_data "/tmp/data0_ro" "/dev/mtdblock4"
}

function do_usage()
{
    echo "     USAGE: $0 mount/umount
    e.g.: $0 mount/umount
    mount: mount emmc
    umount: umount emmc"
    exit 1
}

case $1 in
    "mount")
        do_mount
    ;;
    "umount")
        do_umount
    ;;
    *)
        do_usage # help
    ;;
esac
