SUMMARY = "OpenBMC dfd-debug app"
DESCRIPTION = "OpenBMC dfd-debug app."
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=12f884d2ae1ff87c09e5b7ccc2c4ca7e"

TARGET_CC_ARCH += "${LDFLAGS}"

inherit pkgconfig

S = "${WORKDIR}"
SRC_URI += "file://dfd_debug.c \
       file://COPYING \
       file://dfd_utest.c \
       file://dfd_utest.h \
       file://Rules.mk \
       file://Makefile  "


FILES:${PN} += "${sbindir}/dfd_debug"
RDEPENDS:${PN} = "bash"

SYSTEMD_PACKAGES = "${PN}"
do_install() {
    install -d ${D}/usr/sbin
	install -m 0755 ${S}/build/dfd_debug ${D}/${sbindir}/
}