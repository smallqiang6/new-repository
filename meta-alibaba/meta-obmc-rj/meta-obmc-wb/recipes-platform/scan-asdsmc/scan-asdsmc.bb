FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "file://scan-asdsmc.c \
           file://Rules.mk \
           file://Makefile \
           file://COPYING"

S = "${WORKDIR}"
inherit systemd

do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 0755 ${S}/build/scan-asdsmc ${D}/${localbindir}/scan-asdsmc
}

FILES:${PN} += "/usr/local"
RDEPENDS:${PN} = "bash"
