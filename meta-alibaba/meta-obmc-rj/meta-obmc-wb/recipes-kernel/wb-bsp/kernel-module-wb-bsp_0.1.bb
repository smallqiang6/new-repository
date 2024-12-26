# Copyright 2018-present Facebook. All Rights Reserved.
#
# This program file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#

SUMMARY = "White box BSP drivers"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=12f884d2ae1ff87c09e5b7ccc2c4ca7e"

inherit module kernel_extra_headers_export

PR = "r0"
PV = "0.1"

SRC_URI = "file://Makefile                  \
          file://COPYING                    \
          file://firmware_driver            \
          file://s3ip_sysfs                 \
          file://common                     \
          "

S = "${WORKDIR}"

KERNEL_MODULE_PROBECONF += " \
  wb_fpga_i2c_bus_drv \
  wb_fpga_pca954x_drv \
  wb_i2c_mux_pca954x \
  wb_i2c_mux_pca9641 \
  wb_i2c_dev \
  wb_platform_i2c_dev \
  wb_wdt \
  aspeed_vhub \
"

module_conf_wb_fpga_i2c_bus_drv = "blacklist wb_fpga_i2c_bus_drv"
module_conf_wb_fpga_pca954x_drv = "blacklist wb_fpga_pca954x_drv"
module_conf_wb_i2c_mux_pca954x = "blacklist wb_i2c_mux_pca954x"
module_conf_wb_i2c_mux_pca9641 = "blacklist wb_i2c_mux_pca9641"
module_conf_wb_i2c_dev = "blacklist wb_i2c_dev"
module_conf_wb_platform_i2c_dev = "blacklist wb_platform_i2c_dev"
module_conf_wb_wdt = "blacklist wb_wdt"
module_conf_aspeed_vhub = "blacklist aspeed_vhub"

