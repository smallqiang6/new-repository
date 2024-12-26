#!/bin/bash
echo "begin exec device platfom shell"
modprobe platform_common dfd_my_type=0x40e6
modprobe wb_i2c_mux_pca954x
modprobe wb_i2c_dev
modprobe wb_eeprom_93xx46
modprobe wb_lm75
modprobe wb_pmbus_core
modprobe wb_csu550
modprobe wb_xdpe12284
modprobe wb_xdpe132g5c_pmbus
modprobe wb_ina3221
modprobe wb_ucd9000
modprobe wb_rc32312
modprobe firmware_driver_ispvme
modprobe firmware_driver_sysfs
modprobe wb_dev_resume
modprobe s3ip_sysfs
modprobe wb_switch_driver
modprobe cpld_device_driver
modprobe fan_device_driver
modprobe sysled_device_driver
modprobe psu_device_driver
modprobe temp_sensor_device_driver
modprobe vol_sensor_device_driver
modprobe system_device_driver
modprobe hw_test


# eeprom
echo 24c02 0x50 > /sys/bus/i2c/devices/i2c-16/new_device
echo 24c02 0x53 > /sys/bus/i2c/devices/i2c-2/new_device
echo 24c02 0x57 > /sys/bus/i2c/devices/i2c-2/new_device
echo 24c02 0x51 > /sys/bus/i2c/devices/i2c-2/new_device
echo 24c128 0x50 > /sys/bus/i2c/devices/i2c-80/new_device
# fan
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-72/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-73/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-74/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-75/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-76/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-77/new_device
# fcb
echo 24c02 0x56 > /sys/bus/i2c/devices/i2c-8/new_device
# vr
echo wb_ucd90160 0x5f > /sys/bus/i2c/devices/i2c-17/new_device
echo wb_xdpe12284 0x5e > /sys/bus/i2c/devices/i2c-17/new_device
echo wb_xdpe12284 0x68 > /sys/bus/i2c/devices/i2c-17/new_device
echo wb_xdpe12284 0x6e > /sys/bus/i2c/devices/i2c-17/new_device
echo wb_xdpe12284 0x70 > /sys/bus/i2c/devices/i2c-17/new_device

echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-24/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-25/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-26/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-27/new_device

echo wb_xdpe132g5c_pmbus 0x60 > /sys/bus/i2c/devices/i2c-32/new_device
echo wb_xdpe12284 0x60 > /sys/bus/i2c/devices/i2c-33/new_device
echo wb_xdpe12284 0x60 > /sys/bus/i2c/devices/i2c-34/new_device
echo wb_xdpe12284 0x60 > /sys/bus/i2c/devices/i2c-35/new_device

echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-40/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-41/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-42/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-43/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-44/new_device
# psu
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-56/new_device
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-57/new_device
# temp
echo wb_tmp275 0x48 > /sys/bus/i2c/devices/i2c-64/new_device
echo wb_tmp275 0x49 > /sys/bus/i2c/devices/i2c-65/new_device
echo wb_tmp275 0x4b > /sys/bus/i2c/devices/i2c-66/new_device
echo wb_tmp275 0x49 > /sys/bus/i2c/devices/i2c-78/new_device
echo wb_tmp275 0x48 > /sys/bus/i2c/devices/i2c-79/new_device

# rc32312
echo wb_rc32312 0x09 > /sys/bus/i2c/devices/i2c-80/new_device

# aspeed-smc probe is successful, but the MTD device is not created, so it needs to be unbind
echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind


exit 0

