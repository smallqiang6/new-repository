FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "file://ast-functions \
           file://emmc-initfs.sh \
           file://emmc-initfs.service \
           file://setup_platform.sh \
           file://init-platform.service \
           file://device_config.sh  \
           file://device-config.service \
           file://fw_version.sh \
           file://COPYING \
           file://plat_common_util.py \
           file://bmc_monitor.service \
           file://bmc_monitor.sh \
           file://bmc_dump_cpld.sh \
           file://init_once.sh \
           file://bmc-ready.service \
           file://init_early.sh \
           file://init-early.service \
           file://bios_post_code_monitor.service \
           file://bios_post_code_monitor.py \
           file://bmc.target \
           file://sonic.target \
           file://get-baudrate \
           file://set-baudrate \
           file://dev_baudrate.exp \
           "

S = "${WORKDIR}"
inherit systemd
SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE:${PN} = "emmc-initfs.service \
                         init-platform.service \
                         device-config.service \
                         bmc_monitor.service \
                         bmc-ready.service \
                         init-early.service \
                         bios_post_code_monitor.service \
                         bmc.target \
                         sonic.target \
                         "

inherit python3-dir
pydst="${PYTHON_SITEPACKAGES_DIR}/plat_utils"

do_install:append() {
    mkdir -p ${D}/${pydst}
    install -m 755 plat_common_util.py ${D}${pydst}/plat_common_util.py

    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 0755 ${WORKDIR}/ast-functions ${D}${localbindir}/ast-functions
    install -m 0755 ${WORKDIR}/emmc-initfs.sh ${D}${localbindir}/emmc-initfs.sh
    install -m 0755 ${WORKDIR}/setup_platform.sh ${D}${localbindir}/setup_platform.sh
    install -m 0755 ${WORKDIR}/device_config.sh  ${D}${localbindir}/device_config.sh
    install -m 755 ${WORKDIR}/fw_version.sh ${D}${localbindir}/fw_version.sh
    install -m 755 ${WORKDIR}/bmc_monitor.sh ${D}${localbindir}/bmc_monitor.sh
    install -m 755 ${WORKDIR}/bmc_dump_cpld.sh ${D}${localbindir}/bmc_dump_cpld.sh
    install -m 755 ${WORKDIR}/init_once.sh ${D}${localbindir}/init_once.sh
    install -m 755 ${WORKDIR}/init_early.sh ${D}${localbindir}/init_early.sh
    install -m 755 ${WORKDIR}/bios_post_code_monitor.py ${D}${localbindir}/bios_post_code_monitor.py
    install -m 755 ${WORKDIR}/get-baudrate ${D}${localbindir}/get-baudrate
    install -m 755 ${WORKDIR}/set-baudrate ${D}${localbindir}/set-baudrate
    install -m 755 ${WORKDIR}/dev_baudrate.exp ${D}${localbindir}/dev_baudrate.exp

    install -d ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/emmc-initfs.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/init-platform.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/device-config.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/bmc_monitor.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/bmc-ready.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/init-early.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/bios_post_code_monitor.service ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/bmc.target ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/sonic.target ${D}${systemd_unitdir}/system
}

FILES:${PN} += "/usr/local ${pydst} ${sysconfdir} ${systemd_unitdir}"

RDEPENDS:${PN} = "bash expect"
