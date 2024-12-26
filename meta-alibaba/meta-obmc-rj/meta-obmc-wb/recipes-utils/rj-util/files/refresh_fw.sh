#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

logger_indicate="cpld_refresh"

upgrade_tool="/usr/local/bin/upgrade.py"
upgrade_result_direct="/var/log/fw"
upgrade_refresh_result="/var/log/fw/refresh_upgrade_result"
upgrade_cpld_result="/tmp/upgrade_cpld_result"
upgrade_cpld_fpga_bios_result="/tmp/upgrade_cpld_fpga_bios_result"
str_failed="FAILED"
str_success="DONE"
str_transfr="transfr"
str_refresh_file=""
file_type=""
tmp_channels=""
cpu_board_cpld=0
cpu_board_cpld_file=""
bios_refresh_file_tag=0 #Whether upgrade bios or not, 0(no) 1(yes)
power_off_times=0 #Record the times of power off cpu
g_stop_service_times=0
g_refresh_before_shut_cpu_power=0
x86_arch=0 #sonic arch, 0: x86 1:arm

rm -rf $upgrade_cpld_result
rm -rf $upgrade_cpld_fpga_bios_result

#get sonic arch, 0: x86 1:arm
result=$(ast_product_func_call get_cpu_arch)
arch_type=$?

# Upgrade FPGA\CPLD end, power on CPU and reboot BMC
# But he power-on operation in arm causes the cpu to fail to start
function restore_cpu_bmc()
{
    if [ ${g_stop_service_times} -gt 0 ]; then
        # shut cpu if services have been stoped
        shut_cpu_power
    fi
    if [ ${power_off_times} -gt 0 ]; then
        if [ $arch_type -eq $x86_arch ];then
            logger -t ${logger_indicate} -p DEBUG "Powering on CPU module"
            product_power_on_cpu_module #power on cpu module
            logger -p DEBUG "Powering on CPU"
            ast_product_func_call power_on_cpu #power on cpu
        fi
        sleep 3
        logger -p DEBUG "End of refresh, reboot"
        reboot #reboot bmc
    fi
    exit 0
}

function stop_bmc_service()
{
    if [ ${g_stop_service_times} == 0 ]; then
        systemctl stop fanctrl.service #close ali fanctrl
        # Set fan full speed
        logger -t ${logger_indicate} -p DEBUG "Set fan full speed"
        ast_product_func_call set_full_fan
        #systemctl stop dev-monitor.service #close dev-monitor
        #avoid conflicts between detect mce and upgrade cpld refresh
        systemctl stop cpu-error-gpio.service  #close cpu-error-gpio
        sleep 3
    fi
    g_stop_service_times=$[ $g_stop_service_times+1 ]
}

function shut_cpu_power()
{
    if [ ${power_off_times} == 0 ]; then
        logger -p DEBUG "Powering off CPU"
        ast_product_func_call power_off_cpu #power off cpu
        if [ $arch_type -eq $x86_arch ];then
            sleep 10
            product_power_off_cpu_module #power off cpu module
            if [[ $LOCK_SIGNAL_SWITCH == 0 ]]; then
                product_set_register_hold_signal
            fi
            sleep 3
        fi
    fi
    power_off_times=$[ $power_off_times+1 ]

}
# Before upgrade FPGA\CPLD, close dev-monitor and power off cpu
# If  power_off_times=0 represents first operation, power_off_times != 0 indicates that it has been done
function shut_cpu_bmc_service()
{
    stop_bmc_service
    # 1: refresh first without shutting cpu power
    if [ ${g_refresh_before_shut_cpu_power} -eq 1 ]; then
        return
    fi
    shut_cpu_power
}

# Judge upgrade refresh file
function judege_refresh_file_channels()
{
    # refresh file does not empty
    if [ ! -s $str_refresh_file ]; then
        logger -t ${logger_indicate} -p DEBUG "$str_refresh_file does not exist"
        echo $str_failed > $upgrade_cpld_fpga_bios_result
        echo "$file_type : $str_failed" >> $upgrade_refresh_result
        restore_cpu_bmc
    fi

    tmp_channels=${PRODUCT_CPLDPROGRAM["${file_type}_ref_channels"]}
    if [[ "$tmp_channels" == "" ]]; then
        echo $str_failed > $upgrade_cpld_fpga_bios_result
        echo "$file_type : $str_failed" >> $upgrade_refresh_result
        logger -t ${logger_indicate} -p DEBUG "$file_type does not match $str_refresh_file"
        restore_cpu_bmc
    fi
}

# Upgrade FPGA refresh file
# Record FPGA upgrade result, default FAILED
function upgrade_fpga_refresh()
{
    shut_cpu_bmc_service #Preparation before upgrade
    logger -p DEBUG "Refreshing FPGA"
    ast_product_func_call upgrade_fpga_refresh
    if [ $? == 0 ] ; then
        echo $str_success > $upgrade_cpld_fpga_bios_result
        echo "FPGA : $str_success" >> $upgrade_refresh_result
    else
        echo $str_failed > $upgrade_cpld_fpga_bios_result
        echo "FPGA : $str_failed" >> $upgrade_refresh_result
        restore_cpu_bmc
    fi
}

function upgrade_bios_refresh()
{
    if [ ${bios_refresh_file_tag} == 1 ]; then
        shut_cpu_bmc_service
        logger -p DEBUG "Refreshing BIOS"
        echo "BIOS : $str_success" >> $upgrade_refresh_result
        echo $str_success > $upgrade_cpld_fpga_bios_result
    fi
}

function store_multiple_refresh_results()
{
    for i in "${!g_array_types_backup[@]}";
    do
        logger -t ${logger_indicate} -p DEBUG "refresh ${g_array_types_backup[$i]} $str_success"
        echo "${g_array_types_backup[$i]} : $str_success" >> $upgrade_refresh_result
    done
}

# Classification and upgrade CPLD
function upgrade_cpld_refresh()
{
    # 0:upgrade success, 1:upgrade failed
    success_or_fail=0
    judege_refresh_file_channels
    shut_cpu_bmc_service #Preparation before upgrade
    logger -t ${logger_indicate} -p DEBUG "${file_type}_channels, ${tmp_channels}"
    logger -p DEBUG "Refreshing ${file_type}"
    tmp_array_tmp_channels=(${tmp_channels//,/ })
    for cpld_jtag_chain in ${tmp_array_tmp_channels[*]} ;
    do
        if [[ "${cpld_jtag_chain}" == "-1" ]]; then
            echo $str_success > $upgrade_cpld_fpga_bios_result
            logger -t ${logger_indicate} -p DEBUG "$file_type $str_refresh_file $cpld_jtag_chain does not upgrade"
            success_or_fail=0
            break
        fi
        refresh_cmd="$upgrade_tool cold $str_refresh_file"
        logger -t ${logger_indicate} -p DEBUG "$refresh_cmd, please wait..."
        $refresh_cmd |tee $upgrade_cpld_result
        returnValue=$(grep -c "succeeded" $upgrade_cpld_result)
        if [ $returnValue != 0 ]; then
            logger -t ${logger_indicate} -p DEBUG "upgrade $str_refresh_file success"
            echo $str_success > $upgrade_cpld_fpga_bios_result
            success_or_fail=0
        else
            logger -t ${logger_indicate} -p DEBUG "upgrade $str_refresh_file failed"
            echo $str_failed > $upgrade_cpld_fpga_bios_result
            success_or_fail=1
            break
        fi
    done

    if [[ ${file_type} == "MAC_MISC_CPLD" ]]; then
        ast_product_func_call set_register_release_miscmac_signal
    fi

    if [[ $success_or_fail == 0 ]]; then
        if [ $arch_type -ne $x86_arch ];then
            store_multiple_refresh_results
        else
            echo "$file_type : $str_success" >> $upgrade_refresh_result
        fi
    else
        echo "$file_type : $str_failed" >> $upgrade_refresh_result
        restore_cpu_bmc
    fi
}

function init_upgrade_refresh_result()
{
    if [ ! -d $upgrade_result_direct ];then
        mkdir -p $upgrade_result_direct
    else
        echo -ne "" > $upgrade_refresh_result
    fi
}

#remove all cpld except ctrl_cpld
#not ctrl_cpld: remain the last cpld
function remain_ctrl_cpld()
{
    type=" "
    file=" "
    g_array_types_backup=()
    backup_index=0
    is_find_ctrl_cpld=0
    for i in "${!array_types[@]}";
    do
        if [[ ${array_types[$i]} =~ "CTRL_MODULE_CPLD" ]]; then
            logger -t ${logger_indicate} -p DEBUG "CTRL_MODULE_CPLD find, use it to refresh"
            is_find_ctrl_cpld=1
            type=${array_types[$i]}
            file=${array_files[$i]}
            g_array_types_backup[$backup_index]=${array_types[$i]}
            let backup_index++
            continue
        elif [[ ${array_types[$i]} =~ "CPLD" ]]; then
            if [ $is_find_ctrl_cpld == 0 ]; then
                type=${array_types[$i]}
                file=${array_files[$i]}
            fi
            logger -t ${logger_indicate} -p DEBUG "find cpld key: ${array_types[$i]}, ${array_files[$i]}, $i, remove it."
            g_array_types_backup[$backup_index]=${array_types[$i]}
            let backup_index++
            unset array_types[$i]
            unset array_files[$i]
        elif [[ ${array_types[$i]} =~ "BIOS" ]]; then
            logger -t ${logger_indicate} -p DEBUG "find bios key: ${array_types[$i]}, $i, remove it."
            unset array_types[$i]
            unset array_files[$i]
        elif [[ ${array_types[$i]} =~ "FPGA" ]]; then
            logger -t ${logger_indicate} -p DEBUG "find fpga key: ${array_types[$i]}, $i, remove it."
            unset array_types[$i]
            unset array_files[$i]
        fi
    done
    array_types[0]=${type}
    array_files[0]=${file}
}

#$1:array_types_cpld
#$2:array_files_cpld
function judege_arry_refresh_file_channels()
{
    for i in "${!array_types[@]}";
    do
        file_type=${array_types[$i]}
        str_refresh_file=${array_files[$i]}
        judege_refresh_file_channels
    done
}

# Record CPLD upgrade\BIOS\FPGA information
echo $str_failed > $upgrade_cpld_fpga_bios_result

# Init last upgrade refresh file
init_upgrade_refresh_result

arg_types=$1
arg_files=$2
logger -t ${logger_indicate} -p DEBUG "arg, ${arg_types}, ${arg_files}"
array_types=(${arg_types//:/ })
array_files=(${arg_files//:/ })
if [ $arch_type -ne $x86_arch ];then
        judege_arry_refresh_file_channels
        remain_ctrl_cpld
fi

# Recover default port cpld jtag. In fact, only OOB and ATS will do it.
remove_ret=$(ast_product_func_call jtag_default_port_cpld)
if [ $? -ne 0 ]; then
    echo "${array_types[0]} : $str_failed" >> $upgrade_refresh_result
    restore_cpu_bmc
fi

# Upgrade CPLD file
# MAC_MISC_CPLD will always be the first one, if it exists
for i in "${!array_types[@]}";
do
    logger -t ${logger_indicate} -p DEBUG ${array_types[$i]}
    logger -t ${logger_indicate} -p DEBUG ${array_files[$i]}
    file_type=${array_types[$i]}
    str_refresh_file=${array_files[$i]}
    if [[ $file_type =~ "BIOS" ]]; then
        bios_refresh_file_tag=1
    elif [[ $file_type =~ "FPGA" ]]; then
        upgrade_fpga_refresh
    # CPU_BOARD_CPLD contains CPU_BOARD_CPLD and CPU_BOARD_CPLD2
    elif [[ $file_type == "CPU_BOARD_CPLD" || $file_type == "CPU_BOARD_CPLD2" ]]; then
        g_cpu_board_cpld=1
        g_cpu_board_cpld_name=$file_type
        g_cpu_board_cpld_file=$str_refresh_file
        continue
    elif [[ $file_type == "MAC_MISC_CPLD" ]]; then
        ast_product_func_call shut_cpu_first_when_refresh_misccpld
        if [ $? -eq 1 ]; then
            shut_cpu_bmc_service
        fi
        ast_product_func_call set_register_hold_miscmac_signal
        upgrade_cpld_refresh
    else
        upgrade_cpld_refresh
    fi
done

# last upgrade: CPU_BOARD_CPLD
# After lock signal prevented, CPU cannot power up or enter the shell interface
if [[ $g_cpu_board_cpld == 1 ]]; then
    if [[ $LOCK_SIGNAL_SWITCH == 1 ]]; then
        # bug862143：revise the refresh process (when the base CPLD is refreshed separately)
        # return: 1-shut cpu first, which changes the process, 0-keep the original process
        ast_product_func_call shut_cpu_first_when_refresh_basecpld
        if [ $? -eq 1 ]; then
            shut_cpu_bmc_service
        fi
        product_set_register_hold_signal
    fi
    file_type=$g_cpu_board_cpld_name
    str_refresh_file=$g_cpu_board_cpld_file
    upgrade_cpld_refresh
fi

#judge whethe CPU support bios(x86 arch)
#sonic arch, 0: x86 1:arm
if [ $arch_type -eq $x86_arch ];then
# last upgrade: bios refresh
# biso refresh: only power on\off cpu, if cpld or fpga has upgraded, does not upgrade refresh
    upgrade_bios_refresh
else
    logger -p DEBUG "unspoort bios arch_type is arm or illegal arch_type: $arch_type"
fi

# Backup upgrade result
ast_backup_to_single_data $upgrade_refresh_result

#cpu power on and reboot bmc
restore_cpu_bmc

