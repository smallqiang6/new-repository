FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "file://cpu-error-gpio.c \
           file://cpu-error-gpio.h \
           file://cpu-error-gpio.service \
           file://Rules.mk \
           file://Makefile \
           file://COPYING"

S = "${WORKDIR}"
inherit systemd
SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE:${PN} = "cpu-error-gpio.service"
do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 755 ${WORKDIR}//build/cpu-error-gpio ${D}${localbindir}/cpu-error-gpio
    
    install -d ${D}${sysconfdir}/init.d
    install -d ${D}${sysconfdir}/rcS.d
    install -d ${D}${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/cpu-error-gpio.service ${D}${systemd_unitdir}/system
}

FILES:${PN} += "/usr/local ${sysconfdir} ${systemd_unitdir}/system"
RDEPENDS:${PN} = "bash"
