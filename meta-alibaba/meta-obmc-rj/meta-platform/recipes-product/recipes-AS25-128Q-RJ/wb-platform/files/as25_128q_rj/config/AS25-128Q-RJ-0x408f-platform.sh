#!/bin/bash
echo "begin exec device platfom shell"
modprobe platform_common dfd_my_type=0x408f
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
modprobe s3ip_sysfs
modprobe wb_switch_driver
modprobe cpld_device_driver
modprobe fan_device_driver
modprobe sysled_device_driver
modprobe psu_device_driver
modprobe temp_sensor_device_driver
modprobe vol_sensor_device_driver
modprobe curr_sensor_device_driver
modprobe system_device_driver
modprobe eeprom_device_driver
modprobe hw_test


# eeprom
echo 24c02 0x50 > /sys/bus/i2c/devices/i2c-14/new_device
echo 24c02 0x53 > /sys/bus/i2c/devices/i2c-2/new_device
echo 24c02 0x57 > /sys/bus/i2c/devices/i2c-2/new_device
echo 24c02 0x51 > /sys/bus/i2c/devices/i2c-22/new_device
echo 24c02 0x52 > /sys/bus/i2c/devices/i2c-23/new_device
# fan
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-86/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-87/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-88/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-89/new_device
echo 24c64 0x50 > /sys/bus/i2c/devices/i2c-90/new_device
# fcb
echo 24c02 0x56 > /sys/bus/i2c/devices/i2c-92/new_device
# vr
echo wb_ucd90160 0x5f > /sys/bus/i2c/devices/i2c-15/new_device
echo wb_xdpe12284 0x5e > /sys/bus/i2c/devices/i2c-15/new_device
echo wb_xdpe12284 0x68 > /sys/bus/i2c/devices/i2c-15/new_device
echo wb_xdpe12284 0x6e > /sys/bus/i2c/devices/i2c-15/new_device
echo wb_xdpe12284 0x70 > /sys/bus/i2c/devices/i2c-15/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-30/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-31/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-32/new_device
echo wb_ina3221 0x41 > /sys/bus/i2c/devices/i2c-33/new_device
echo wb_xdpe132g5c_pmbus 0x40 > /sys/bus/i2c/devices/i2c-38/new_device
echo wb_xdpe132g5c_pmbus 0x40 > /sys/bus/i2c/devices/i2c-39/new_device
echo wb_xdpe132g5c_pmbus 0x40 > /sys/bus/i2c/devices/i2c-40/new_device
echo wb_xdpe12284 0x58 > /sys/bus/i2c/devices/i2c-41/new_device
echo wb_xdpe12284 0x58 > /sys/bus/i2c/devices/i2c-42/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-46/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-47/new_device
echo wb_xdpe12284 0x58 > /sys/bus/i2c/devices/i2c-48/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-54/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-55/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-56/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-57/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-58/new_device
echo wb_ina3221 0x40 > /sys/bus/i2c/devices/i2c-59/new_device
# psu
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-70/new_device
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-71/new_device
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-72/new_device
echo wb_fsp1200 0x58 > /sys/bus/i2c/devices/i2c-73/new_device
# temp
echo wb_tmp275 0x48 > /sys/bus/i2c/devices/i2c-74/new_device
echo wb_tmp275 0x48 > /sys/bus/i2c/devices/i2c-78/new_device
echo wb_tmp275 0x49 > /sys/bus/i2c/devices/i2c-93/new_device
echo wb_tmp275 0x48 > /sys/bus/i2c/devices/i2c-93/new_device

# rc32312
echo wb_rc32312 0x09 > /sys/bus/i2c/devices/i2c-102/new_device

# aspeed-smc probe is successful, but the MTD device is not created, so it needs to be unbind
echo 1e630000.spi > /sys/bus/platform/drivers/aspeed-smc/unbind


exit 0

