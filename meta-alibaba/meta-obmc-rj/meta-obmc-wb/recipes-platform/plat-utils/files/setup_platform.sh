#!/bin/sh
. /usr/local/bin/ast-functions
#Set BMC login timeout
echo "TMOUT=300" >> /etc/profile
echo "export TMOUT" >> /etc/profile

ast_product_func_call "sys_led_enable"
echo 4 >/proc/sys/kernel/printk
