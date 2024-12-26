#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.

. /usr/local/bin/ast-functions

logger_indicate="cpld_program"
upgrade_tool="/usr/local/bin/upgrade.py"
str_program_file=""
file_cpld_type=""
str_failed="FAILED"
str_success="DONE"
resultFile="/tmp/cpld_program_result" #Used to record the final upgrade result, DONE or FAILED
upgrade_cpld_result="/tmp/upgrade_cpld_result" #Used to judge whether firmware_upgrade_ispvme is executed successfully
upgrade_cpld_result_detail="/tmp/upgrade_cpld_result_detail" #Used to record the detailed upgrade results of each CPLD, X_CPLD : DONE or FAILED

rm -rf $resultFile
rm -rf $upgrade_cpld_result
rm -rf $upgrade_cpld_result_detail

# Judge upgrade cpld file
function judge_upgrade_file()
{
    # refresh file does not empty
    if [ ! -s $str_program_file ]; then
        logger -t ${logger_indicate} -p DEBUG "upgrade failed - $str_program_file no exist"
        echo $str_failed > $upgrade_cpld_result
        echo "$file_cpld_type: $str_failed" >> $upgrade_cpld_result_detail
        exit 0
    fi

    # refresh file corresponds to device
    tmp_name=${PRODUCT_CPLDPROGRAM["${file_cpld_type}_name"]}
    resultStr=$(echo $str_program_file | grep "${tmp_name}")
    if [[ "$tmp_name" == "" ]] || [[ "$resultStr" == "" ]]; then
        echo $str_failed > $upgrade_cpld_result
        echo "$file_cpld_type: $str_failed" >> $upgrade_cpld_result_detail
        logger -t ${logger_indicate} -p DEBUG "$str_program_file does not match $tmp_name"
        exit 0
    fi
}

function upgrade_cpld_program()
{
    judge_upgrade_file

    program_cmd="$upgrade_tool cold $str_program_file"
    logger -t ${logger_indicate} -p DEBUG "$program_cmd, please wait..."
    $program_cmd |tee $resultFile
    returnValue=$(grep -c "succeeded" $resultFile)

    if [ $returnValue != 0 ]; then
        logger -t ${logger_indicate} -p DEBUG "upgrade $str_program_file success"
        echo $str_success > $upgrade_cpld_result
        echo "$file_cpld_type: $str_success" >> $upgrade_cpld_result_detail
    else
        logger -t ${logger_indicate} -p DEBUG "upgrade $str_program_file failed"
        echo $str_failed > $upgrade_cpld_result
        echo "$file_cpld_type: $str_failed" >> $upgrade_cpld_result_detail
        exit 0
    fi
}

# Record CPLD upgrade\BIOS\FPGA information
echo $str_failed > $upgrade_cpld_result
touch $upgrade_cpld_result_detail

arg_cpld_types=$1
arg_cpld_files=$2
logger -t ${logger_indicate} -p DEBUG "arg, ${arg_cpld_types}, ${arg_cpld_files}"
array_cpld_types=(${arg_cpld_types//:/ })
array_cpld_files=(${arg_cpld_files//:/ })
# Upgrade CPLD file
for i in "${!array_cpld_types[@]}" ; 
do 
    logger -t ${logger_indicate} -p DEBUG ${array_cpld_types[$i]}
    logger -t ${logger_indicate} -p DEBUG ${array_cpld_files[$i]}
    file_cpld_type=${array_cpld_types[$i]}
    str_program_file=${array_cpld_files[$i]}
    if [[ $file_cpld_type =~ "PORT_BOARD_CPLD" ]]; then
        add_ret=$(ast_product_func_call jtag_add_port_cpld)
    else
        remove_ret=$(ast_product_func_call jtag_default_port_cpld)
    fi
    if [ $? -ne 0 ]; then
        echo $str_failed > $upgrade_cpld_result
        echo "$file_cpld_type: $str_failed" >> $upgrade_cpld_result_detail
        exit 0
    fi
    upgrade_cpld_program
    if [[ $file_cpld_type =~ "PORT_BOARD_CPLD" ]]; then
        remove_ret=$(ast_product_func_call jtag_default_port_cpld)
    fi
    if [ $? -ne 0 ]; then
        echo $str_failed > $upgrade_cpld_result
        sed -i 's/'"$file_cpld_type: $str_success"'/'"$file_cpld_type: $str_failed"'/g' $upgrade_cpld_result_detail
        exit 0
    fi
done
