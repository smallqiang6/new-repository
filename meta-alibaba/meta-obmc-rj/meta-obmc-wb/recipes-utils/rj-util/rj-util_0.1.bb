# Copyright 2019-present Facebook. All Rights Reserved.
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
# You should have received a copy of the GNU General Public License
# along with this program in a file named COPYING; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
SUMMARY = "Configure the sensors"
DESCRIPTION = "The script configure sensors"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"
RDEPENDS:${PN} += "bash"

SRC_URI += "file://obmc_i2cget \
            file://obmc_i2cset \
            file://ast_obmc_i2cget \
            file://ast_obmc_i2cset \
            file://switch_bmc.sh \
            file://refresh_fw.sh \
            file://program_bmc.sh \
            file://program_cpld.sh \
            file://id_rsa.pub \
            file://plat_power \
            file://plat_led_location \
            file://upgrade_info.py \
            file://bios.sh \
            file://program_bios.sh \
            file://store_bios_version.sh \
            file://firmware_path_upgrade.sh \
            file://bmc_module_version\
            file://ftg100_tool \
            file://program_fpga.sh \
            file://COPYING \
            file://program_mac.sh \
            file://program_8367.sh \
            file://upgrade_bios.sh \
            file://store_host_uboot_version.sh \
            file://host_uboot.sh \
            "

S = "${WORKDIR}"

do_install:append() {
    install -d ${D}/etc
    install -m 0644 ${WORKDIR}/id_rsa.pub ${D}/etc/
    install -m 0644 ${WORKDIR}/bmc_module_version ${D}/etc/

    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 755 ${WORKDIR}/obmc_i2cget ${D}${localbindir}/obmc_i2cget
    install -m 755 ${WORKDIR}/obmc_i2cset ${D}${localbindir}/obmc_i2cset
    install -m 755 ${WORKDIR}/ast_obmc_i2cget ${D}${localbindir}/ast_obmc_i2cget
    install -m 755 ${WORKDIR}/ast_obmc_i2cset ${D}${localbindir}/ast_obmc_i2cset
    install -m 755 ${WORKDIR}/switch_bmc.sh ${D}${localbindir}/switch_bmc.sh
    install -m 755 ${WORKDIR}/program_bmc.sh ${D}${localbindir}/program_bmc.sh
    install -m 755 ${WORKDIR}/program_cpld.sh ${D}${localbindir}/program_cpld.sh
    install -m 755 ${WORKDIR}/plat_power ${D}${localbindir}/plat_power
    install -m 755 ${WORKDIR}/plat_led_location ${D}${localbindir}/plat_led_location
    install -m 755 ${WORKDIR}/upgrade_info.py ${D}${localbindir}/upgrade_info.py
    install -m 755 ${WORKDIR}/refresh_fw.sh ${D}${localbindir}/refresh_fw.sh
    install -m 755 ${WORKDIR}/bios.sh ${D}${localbindir}/bios.sh
    install -m 755 ${WORKDIR}/program_bios.sh ${D}${localbindir}/program_bios.sh
    install -m 755 ${WORKDIR}/store_bios_version.sh ${D}${localbindir}/store_bios_version.sh
    install -m 755 ${WORKDIR}/firmware_path_upgrade.sh ${D}${localbindir}/firmware_path_upgrade.sh
    install -m 755 ${WORKDIR}/program_fpga.sh ${D}${localbindir}/program_fpga.sh
    install -m 755 ${WORKDIR}/ftg100_tool ${D}${localbindir}/ftg100_tool
    install -m 755 ${WORKDIR}/program_mac.sh ${D}${localbindir}/program_mac.sh
    install -m 755 ${WORKDIR}/program_8367.sh ${D}${localbindir}/program_8367.sh
    install -m 755 ${WORKDIR}/upgrade_bios.sh ${D}${localbindir}/upgrade_bios.sh
    install -m 755 ${WORKDIR}/store_host_uboot_version.sh ${D}${localbindir}/store_host_uboot_version.sh
    install -m 755 ${WORKDIR}/host_uboot.sh ${D}${localbindir}/host_uboot.sh
}

FILES:${PN} += "/usr/local"
