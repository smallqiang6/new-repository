FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECTION = "base"
PR = "r0"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "file://smitool.c \
           file://smitool.h \
           file://mdio_base.c \
           file://mdio_base.h \
           file://mv88e6xxx.c \
           file://mv88e6xxx.h \
           file://bcm5xxx.c \
           file://bcm5xxx.h \
           file://Rules.mk \
           file://Makefile \
           file://COPYING"

S = "${WORKDIR}"
inherit systemd

do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 0755 ${S}/build/smitool ${D}/${localbindir}/smitool
}

FILES:${PN} += "/usr/local"
RDEPENDS:${PN} = "bash"
