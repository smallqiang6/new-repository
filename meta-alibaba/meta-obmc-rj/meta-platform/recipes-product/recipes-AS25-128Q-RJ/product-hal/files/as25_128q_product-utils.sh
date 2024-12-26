
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
declare -A PRODUCT_CPLDPROGRAM
#name, chanels（多个使用逗号隔开）
#chanels为-1，不需要升级
PRODUCT_CPLDPROGRAM["CPU_MODULE_CPLD_name"]="as25-128q_cpld_0_0_cpu_pwr"
PRODUCT_CPLDPROGRAM["CPU_MODULE_CPLD_channels"]="0"
PRODUCT_CPLDPROGRAM["CPU_MODULE_CPLD_ref_channels"]="-1"
PRODUCT_CPLDPROGRAM["CPU_MODULE_CPLD_refresh"]="as25-128q_cpld_0_transfr_0_bmc"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD_name"]="as25-128q_cpld_1_1_cpu_pwr"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD_channels"]="1"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD_ref_channels"]="1"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD_refresh"]="as25-128q_cpld_1_transfr_1_bmc"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD-FAN_name"]="as25-128q_cpld_2_2_cpu_pwr"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD-FAN_channels"]="2"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD-FAN_ref_channels"]="2"
PRODUCT_CPLDPROGRAM["CPU_BOARD_CPLD-FAN_refresh"]="as25-128q_cpld_2_transfr_2_cpu"
PRODUCT_CPLDPROGRAM["LC_BOARD_CPLD_name"]="as25-128q_cpld_all_port_cpu_pwr"
PRODUCT_CPLDPROGRAM["LC_BOARD_CPLD_channels"]="3"
PRODUCT_CPLDPROGRAM["LC_BOARD_CPLD_ref_channels"]="-1"
PRODUCT_CPLDPROGRAM["LC_BOARD_CPLD_refresh"]="as25-128q_cpld_all_transfr_port_cpu"
PRODUCT_CPLDPROGRAM["PCIE_PORT_CPLD_name"]="as25-128q_cpld_4_4_cpu_pwr"
PRODUCT_CPLDPROGRAM["PCIE_PORT_CPLD_channels"]="4"
PRODUCT_CPLDPROGRAM["PCIE_PORT_CPLD_ref_channels"]="-1"
PRODUCT_CPLDPROGRAM["PCIE_PORT_CPLD_refresh"]="as25-128q_cpld_4_transfr_4_cpu"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_2_name"]="as25-128q_cpld_all_port_cpu_pwr"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_2_channels"]="5"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_2_ref_channels"]="-1"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_2_refresh"]="as25-128q_cpld_all_transfr_port_cpu"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_1_name"]="as25-128q_cpld_all_port_cpu_pwr"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_1_channels"]="6"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_1_ref_channels"]="-1"
PRODUCT_CPLDPROGRAM["MAC_BOARD_CPLD_1_refresh"]="as25-128q_cpld_all_transfr_port_cpu"
PRODUCT_CPLDPROGRAM["MAC_MISC_CPLD_name"]="as25-128q_cpld_7_7_cpu_pwr"
PRODUCT_CPLDPROGRAM["MAC_MISC_CPLD_channels"]="7"
PRODUCT_CPLDPROGRAM["MAC_MISC_CPLD_ref_channels"]="7"
PRODUCT_CPLDPROGRAM["MAC_MISC_CPLD_refresh"]="as25-128q_cpld_7_transfr_7_cpu"

# 升级BASE CPLD锁信号
# 32设备(0)与40d(1)设备不同
LOCK_SIGNAL_SWITCH=1

#Write register to hold signal when update CPLD refresh file
product_set_register_hold_signal() {
    obmc_i2cset -f -y 0 0xd 0xcc 0x01
    sleep 3
    obmc_i2cset -f -y 0 0xd 0xcc 0x00
}

product_upgrade_fpga_refresh() {
    obmc_i2cset -f -y 0 0xd 0xf2 0x00
    obmc_i2cset -f -y 0 0xd 0xf2 0x01
}

# Only 40d devices are supported to switch or free fpga channel
product_switch_fpga_channel() {
    obmc_i2cset -y -f 0 0x0d 0xf0 0x00
    obmc_i2cset -y -f 0 0x0d 0xf1 0x00
}

product_free_fpga_channel() {
    obmc_i2cset -y -f 0 0x0d 0xf0 0x00
    obmc_i2cset -y -f 0 0x0d 0xf1 0x01
}

product_power_on_cpu_module() {
    obmc_i2cset -f -y 0 0xd 0x75 0xff
}

product_power_off_cpu_module() {
    obmc_i2cset -f -y 0 0xd 0x75 0x00
}

product_location_led_normal() {
    obmc_i2cset -f -y 5 0x32 0x40 0x98
    obmc_i2cset -f -y 5 0x32 0x44 0x98
    obmc_i2cset -f -y 5 0x32 0x48 0x98
    obmc_i2cset -f -y 5 0x32 0x4C 0x98
}

product_location_led_byellow() {
    obmc_i2cset -f -y 5 0x32 0x40 0x85
    obmc_i2cset -f -y 5 0x32 0x44 0x85
    obmc_i2cset -f -y 5 0x32 0x48 0x85
    obmc_i2cset -f -y 5 0x32 0x4C 0x85
}

product_location_led_bgreen() {
    obmc_i2cset -f -y 5 0x32 0x40 0x83
    obmc_i2cset -f -y 5 0x32 0x44 0x83
    obmc_i2cset -f -y 5 0x32 0x48 0x83
    obmc_i2cset -f -y 5 0x32 0x4C 0x83
}

product_location_led_syellow() {
    obmc_i2cset -f -y 5 0x32 0x40 0x86
    obmc_i2cset -f -y 5 0x32 0x44 0x86
    obmc_i2cset -f -y 5 0x32 0x48 0x86
    obmc_i2cset -f -y 5 0x32 0x4C 0x86
}

product_location_led_sgreen() {
    obmc_i2cset -f -y 5 0x32 0x40 0x84
    obmc_i2cset -f -y 5 0x32 0x44 0x84
    obmc_i2cset -f -y 5 0x32 0x48 0x84
    obmc_i2cset -f -y 5 0x32 0x4C 0x84
}

product_location_led_location() {
    obmc_i2cset -f -y 5 0x32 0x40 0x85
    obmc_i2cset -f -y 5 0x32 0x44 0x85
    obmc_i2cset -f -y 5 0x32 0x48 0x85
    obmc_i2cset -f -y 5 0x32 0x4C 0x85
}

product_location_led_recover() {
    obmc_i2cset -f -y 5 0x32 0x40 0x98
    obmc_i2cset -f -y 5 0x32 0x44 0x98
    obmc_i2cset -f -y 5 0x32 0x48 0x98
    obmc_i2cset -f -y 5 0x32 0x4C 0x98
}

product_location_led_status() {
    led_status=""
    ledValue10=$(obmc_i2cget -f -y 5 0x32 0x40)
    ledValue14=$(obmc_i2cget -f -y 5 0x32 0x44)
    ledValue18=$(obmc_i2cget -f -y 5 0x32 0x48)
    ledValue1C=$(obmc_i2cget -f -y 5 0x32 0x4C)
    if [[ $ledValue10 != $ledValue14 ]] || [[ $ledValue14 != $ledValue18 ]] || [[ $ledValue18 != $ledValue1C ]]; then
        logger -p DEBUG "Unknown location led status $ledValue10 $ledValue14 $ledValue18 $ledValue1C"
        led_status="Unknown location led status"
        echo $led_status
    fi
    case $ledValue10 in
      0x98)
        led_status="1 normal"
      ;;
      0x85)
        led_status="2 blink yellow"
      ;;
      0x83)
        led_status="3 blink green"
      ;;
      0x86)
        led_status="4 steady on yellow"
      ;;
      0x84)
        led_status="5 steady on green"
      ;;
      *)
        logger -p DEBUG "Unknown location led status $ledValue10"
        led_status="Unknown location led status"
      ;;
    esac
    echo ${led_status}
}

product_machine_status()
{
    return 1 #current machine status is on
}

product_swithch_serial()
{
    serial_status=$(obmc_i2cget -f -y 0 0x0d 0xa7)
    serial_mask=0x1
    case $1 in
      "bmc")
        set_value=`printf "0x%02x" $[${serial_status}| ${serial_mask}]`
      ;;
      "cpu")
        set_value=`printf "0x%02x" $[${serial_status}& $((~($serial_mask)))]`
      ;;
      *)
        logger -p DEBUG "Unknown serial type $1"
        exit 
      ;;
    esac
    obmc_i2cset -f -y 0 0x0d 0xa7 $set_value
}

product_current_serial()
{
    current_serial=""
    serial_mask=0x80
    serial_status=$(obmc_i2cget -f -y 0 0x0d 0xa0)
    val=`printf "0x%02x" $[${serial_status} & ${serial_mask}]`
    if [ $val == "0x80" ];then
        current_serial="bmc"
    elif [ $val == "0x00" ];then
        current_serial="cpu"
    else
        logger -p DEBUG "Unknown serial type $val"
        current_serial="Unknown"
    fi
    echo ${current_serial}
}

product_get_host_cpu_power_force_control_status()
{
    current_status=$(obmc_i2cget -f -y 0 0x0d 0x70)
    if [ $current_status != "0x59" ];then
        return 0 #off
    else
        return 1 #on
    fi
}

product_enable_host_cpu_power_force_control()
{
    obmc_i2cset -f -y 0 0x0d 0x70 0x59
}

product_disable_host_cpu_power_force_control()
{
    obmc_i2cset -f -y 0 0x0d 0x70 0x4E
}

product_ssd_status()
{
    ssd_mask=0x02
    ssd_status=$(obmc_i2cget -f -y 0 0x0d 0x72)
    val=`printf "0x%02x" $[${ssd_status} & ${ssd_mask}]`
    if [ $val == "0x00" ];then
        return 0 #off
    elif [ $val == "0x02" ];then
        return 1 #on
    else
        logger -p DEBUG "Unknown ssd status $val"
        return 2 #unknown
    fi
}

product_power_on_ssd()
{
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    ssd_mask=0x02
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x72)
    set_value=`printf "0x%02x" $[${reg_val}|${ssd_mask}]`
    obmc_i2cset -f -y 0 0x0d 0x72 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        return -1
    fi
    return 0
}

product_power_off_ssd()
{
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x72)
    ssd_mask=0x02
    set_value=`printf "0x%02x" $[${reg_val}& $((~($ssd_mask)))]`
    obmc_i2cset -f -y 0 0x0d 0x72 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        return -1
    fi
    return 0
}

product_mac_status()
{
    reg_val=$(obmc_i2cget -f -y 62 0x30 0x43 2>/dev/null)
    read_ret=$?
    if [ $read_ret -ne 0 ]; then
        logger -p DEBUG "failed to get mac status: $read_ret"
        return 3 #unknown
    fi
    mac_status_mask=0x1
    mac_status=`printf "0x%02x" $[${reg_val}&${mac_status_mask}]`
    if [ $mac_status == "0x00" ]; then
        return 0 #off
    elif [ $mac_status == "0x01" ]; then
        return 1 #on
    else
        logger -p DEBUG "Unknown mac status $mac_status"
        return 3 #unknown
    fi
}

product_power_on_mac()
{
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x72)
    mac_status_mask=0x01
    set_value=`printf "0x%02x" $[${reg_val}|${mac_status_mask}]`
    obmc_i2cset -f -y 0 0x0d 0x72 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        return -1
    fi
    return 0
}

product_power_off_mac()
{
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x72)
    mac_status_mask=0x01
    set_value=`printf "0x%02x" $[${reg_val}& $((~($mac_status_mask)))]`
    obmc_i2cset -f -y 0 0x0d 0x72 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        return -1
    fi
    return 0
}

function product_power_port_with_mac()
{
    # 0: automatically completed; 1: additional action required
    return 1
}

product_port_status()
{
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x71)
    port_status_mask=0x01
    port_status=`printf "0x%02x" $[${reg_val}&${port_status_mask}]`
    if [ $port_status == "0x00" ]; then
        return 0 #off
    elif [ $port_status == "0x01" ]; then
        return 1 #on
    else
        logger -p DEBUG "Unknown port status: $port_status"
        return 2 #Unknown
    fi
}

product_power_on_port()
{
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x71)
    port_status_mask=0x1
    failed=0
    set_value=`printf "0x%02x" $[${reg_val}|${port_status_mask}]`
    obmc_i2cset -f -y 0 0x0d 0x71 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        failed=-1
    fi
    product_release_reset_port
    if [ $? != 0 ]; then
        logger -p DEBUG "failed to reset port: $ret"
        failed=-1
    fi
    return $failed
}

product_reset_port()
{
    mask=0x01
    reg_val1=$(obmc_i2cget -f -y 63 0x31 0xf3)
    set_val1=`printf "0x%02x" $[${reg_val1}& $((~($mask)))]`
    reg_val2=$(obmc_i2cget -f -y 64 0x31 0xf3)
    set_val2=`printf "0x%02x" $[${reg_val2}& $((~($mask)))]`
    reg_val3=$(obmc_i2cget -f -y 65 0x31 0xf3)
    set_val3=`printf "0x%02x" $[${reg_val3}& $((~($mask)))]`
    obmc_i2cset -f -y 63 0x31 0xf3 $set_val1
    ret1=$?
    obmc_i2cset -f -y 64 0x31 0xf3 $set_val2
    ret2=$?
    obmc_i2cset -f -y 65 0x31 0xf3 $set_val3
    ret3=$?
    if [[ $ret1 != 0 || $ret2 != 0 || $ret3 != 0 ]]; then
        logger -p DEBUG "i2c set failed :$ret1, $ret2, $ret3"
        return -1
    fi
    return 0
}

product_release_reset_port()
{
    mask=0x01
    reg_val1=$(obmc_i2cget -f -y 63 0x31 0xf3)
    set_val1=`printf "0x%02x" $[${reg_val1} | $mask]`
    reg_val2=$(obmc_i2cget -f -y 64 0x31 0xf3)
    set_val2=`printf "0x%02x" $[${reg_val2} | $mask]`
    reg_val3=$(obmc_i2cget -f -y 65 0x31 0xf3)
    set_val3=`printf "0x%02x" $[${reg_val3} | $mask]`
    obmc_i2cset -f -y 63 0x31 0xf3 $set_val1
    ret1=$?
    obmc_i2cset -f -y 64 0x31 0xf3 $set_val2
    ret2=$?
    obmc_i2cset -f -y 65 0x31 0xf3 $set_val3
    ret3=$?
    if [[ $ret1 != 0 || $ret2 != 0 || $ret3 != 0 ]]; then
        logger -p DEBUG "i2c set failed :$ret1, $ret2, $ret3"
        return -1
    fi
    return 0
}

product_power_off_port()
{
    failed=0
    product_reset_port
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to reset port: $ret"
        failed=-1
    fi
    product_get_host_cpu_power_force_control_status
    ret=$?
    if [ $ret != 1 ]; then
        logger -p DEBUG "cpu host power force control disable $ret"
        return -1
    fi
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x71)
    port_status_mask=0x01
    set_value=`printf "0x%02x" $[${reg_val}& $((~($port_status_mask)))]`
    product_enable_host_cpu_power_force_control
    obmc_i2cset -f -y 0 0x0d 0x71 $set_value
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "i2c set failed :$ret"
        failed=-1
    fi
    return $failed
}

product_support_power_bmcemmc()
{
    return 1 # 1: support; 0: unsupport
}

product_bmc_emmc_status()
{
    cur_val=$(obmc_i2cget -f -y 0 0x0d 0x4f)
    mask=0x02
    emmc_status=`printf "0x%02x" $[${cur_val}&${mask}]`
    if [ $emmc_status == "0x00" ]; then
        return 0 #off
    elif [ $emmc_status == "0x02" ]; then
        return 1 #on
    else
        logger -p DEBUG "Unknown bmc emmc status: $emmc_status"
        return 2
    fi
}

product_power_cycle_bmcemmc()
{
    emmc_status_mask=0x02
    # pull down rst gpio
    echo 3 > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio3/direction
    echo 0 > /sys/class/gpio/gpio3/value
    # set clk mode: gpio and pull down
    devmem 0x1e6e2090 32 0x87F000A
    echo 16 > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio16/direction
    echo 0 > /sys/class/gpio/gpio16/value
    # power off bmc emmc
    product_enable_host_cpu_power_force_control
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x4f)
    set_value=`printf "0x%02x" $[${reg_val}& $((~($emmc_status_mask)))]`
    obmc_i2cset -f -y 0 0x0d 0x4f $set_value
    product_disable_host_cpu_power_force_control
    product_bmc_emmc_status
    ret=$?
    if [ $ret -ne 0 ]; then
        logger -p DEBUG "failed to power off bmc emmc, current status: $ret"
    fi
    sleep 0.5
    # release clk gpio and set clk mode: clk
    echo 16 > /sys/class/gpio/unexport
    devmem 0x1e6e2090 32 0x87F000B
    # power on bmc emmc
    product_enable_host_cpu_power_force_control
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x4f)
    set_value=`printf "0x%02x" $[${reg_val}|${emmc_status_mask}]`
    obmc_i2cset -f -y 0 0x0d 0x4f $set_value
    product_disable_host_cpu_power_force_control
    product_bmc_emmc_status
    ret=$?
    if [ $ret -ne 1 ]; then
        logger -p DEBUG "failed to power on bmc emmc, current status: $ret"
    fi
    sleep 0.01
    echo 1 > /sys/class/gpio/gpio3/value
    echo 3 > /sys/class/gpio/unexport
    # operation done, regardless of success
    return 0
}

function product_touch_cpucpld_type_file()
{
    # new CPU model, whose related registers are on the base cpld
    #cto: Customized to Order
    touch /etc/device/cpucpld_icelakecto
    touch /etc/device/cpucpld_bus14_icelake # cpu cpld bus: 14, not the default bus: 0
    return 0
}

function product_get_is_bios_cs_required()
{
    return 0 # bios cs is not required
}

function product_get_is_me_required()
{
    return 1 # 0: not required, 1 required
}

function product_get_me_status()
{
    peci_log=$(dfd_debug peci_pcicfglocal_rd 0 0x18 0 0x40 1 2>&1)
    peci_value=$(echo $peci_log | awk 'NR==1{print $24}')
    case "$peci_value" in
    ?1)
        status_ret=1 # initialization, me will exit this status within 2 s
    ;;
    ?2)
        status_ret=2 # recovery
    ;;
    ?5)
        status_ret=5 # operational
    ;;
    *)
        # *0-ME is in reset status, will exit this status within 1 ms
        status_ret=8
        logger -p DEBUG "current me status: unknown, $peci_log!"
    ;;
    esac
    return $status_ret
}

function product_get_me_stability()
{
    stability_log=$(dfd_debug peci_pcicfglocal_rd 0 0x18 0 0x41 1 2>&1)
    if [ $? -ne 0 ]; then
        logger -p DEBUG "current me stability: unknown, $stability_log!"
        return -1
    fi
    stability_val="0x"$(echo $stability_log | awk 'NR==1{print $24}')
    mask=0x02
    val=`printf "0x%02x" $[${stability_val}&${mask}]`
    if [ x"$val" == x"0x02" ]; then
        stability_ret=1 # stable
    elif [ x"$val" == x"0x00" ]; then
        stability_ret=0 # instable
    else
        stability_ret=-1
        logger -p DEBUG "current me stability: unknown, $stability_log!"
    fi
    return $stability_ret
}

function product_me_recovery()
{
    obmc_i2cset -f -y 14 0x0d 0x74 0x3d
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to write reg(me recovery), ret: $ret"
        return -1
    fi
    return 0
}

function product_me_reset()
{
    obmc_i2cset -f -y 14 0x0d 0x74 0x3f
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to write reg(reset me), ret: $ret"
        return -1
    fi
    return 0
}

function product_shut_cpu_first_when_refresh_basecpld()
{
    return 1 # default 0, not required; 1, shut cpu first
}

function product_get_is_support_reset_rtc()
{
    return 1 # 1: support this function, 0: unsupport
}

function product_get_product_type()
{
    return 7 # 6: 6.0, 7: 7.0
}

function product_disable_ocm()
{
    obmc_i2cset -f -y 0 0x0d 0x75 0x00
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to disable ocm, ret: $ret"
        return -1
    fi
    sleep 2
    return 0
}

function product_enable_ocm()
{
    obmc_i2cset -f -y 0 0x0d 0x75 0x01
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to enable ocm, ret: $ret"
        return -1
    fi
    sleep 2
    return 0
}

function product_release_rtc()
{
    obmc_i2cset -f -y 0 0x0d 0xed 0x01
    sleep 2
    obmc_i2cset -f -y 0 0x0d 0xed 0x03
    sleep 4
    obmc_i2cset -f -y 0 0x0d 0xed 0x01
    sleep 2
    obmc_i2cset -f -y 0 0x0d 0xed 0x00
    ret=$?
    if [ $ret != 0 ]; then
        logger -p DEBUG "failed to release rtc, ret: $ret"
        return -1
    fi
    sleep 2
}

function product_get_post_data_mode()
{
    # 0: 1 Byte mode/1: 2 Byte mode/2: 4 Byte mode/3: Full mode
    return 1
}

function product_get_cpu_rst_status() {
    reg_val=$(obmc_i2cget -f -y 0 0x0d 0x13)
    if [ -z $reg_val ]; then
        logger -p DEBUG "Error: read cpu switch status reg failed"
        return 0
    else
        value=$(printf "%d\n" $reg_val)
        return $value
    fi
}

function product_get_cpu_rst_mask() {
    return 1
}

function product_get_s5_ok_mask()
{
    return 2
}
