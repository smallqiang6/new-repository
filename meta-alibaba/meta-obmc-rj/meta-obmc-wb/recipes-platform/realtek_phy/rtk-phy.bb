FILESEXTRAPATHS:prepend := "${THISDIR}/files/rtk_phy:"

SECTION = "base"
PR = "r0"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "\
    file://COPYING \
    file://main.c \
    file://Makefile \
    file://port.c \
    file://rtk_switch.c \
    file://rtl8367c_asicdrv.c \
    file://rtl8367c_asicdrv_green.c \
    file://rtl8367c_asicdrv_inbwctrl.c \
    file://rtl8367c_asicdrv_lut.c \
    file://rtl8367c_asicdrv_mirror.c \
    file://rtl8367c_asicdrv_misc.c \
    file://rtl8367c_asicdrv_phy.c \
    file://rtl8367c_asicdrv_port.c \
    file://rtl8367c_asicdrv_portIsolation.c \
    file://rtl8367c_asicdrv_rma.c \
    file://rtl8367c_asicdrv_scheduling.c \
    file://Rules.mk \
    file://smi.c \
    file://include/main.h \
    file://include/mirror.h \
    file://include/port.h \
    file://include/rate.h \
    file://include/rtk_error.h \
    file://include/rtk_switch.h \
    file://include/rtk_types.h \
    file://include/rtl8367c_asicdrv_green.h \
    file://include/rtl8367c_asicdrv.h \
    file://include/rtl8367c_asicdrv_inbwctrl.h \
    file://include/rtl8367c_asicdrv_lut.h \
    file://include/rtl8367c_asicdrv_mirror.h \
    file://include/rtl8367c_asicdrv_misc.h \
    file://include/rtl8367c_asicdrv_phy.h \
    file://include/rtl8367c_asicdrv_port.h \
    file://include/rtl8367c_asicdrv_portIsolation.h \
    file://include/rtl8367c_asicdrv_rma.h \
    file://include/rtl8367c_asicdrv_scheduling.h \
    file://include/rtl8367c_base.h \
    file://include/rtl8367c_reg.h \
    file://include/smi.h \
    "

S = "${WORKDIR}"
inherit systemd

do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 0755 ${S}/build/rtk_phy ${D}/${localbindir}/rtk_phy
}

FILES:${PN} += "/usr/local"
RDEPENDS:${PN} = "bash"
