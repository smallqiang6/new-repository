# Copyright 2015-present Facebook. All Rights Reserved.

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += " file://kcsd.service \
             file://kcsd.sh \
           "

CFLAGS:prepend = " -DCONFIG_FBTTN"
inherit systemd
SYSTEMD_SERVICE:${PN} = "kcsd.service"

do_install() {
  dst="${D}/usr/local/fbpackages/${pkgdir}"
  bin="${D}/usr/local/bin"
  install -d $dst
  install -d $bin
  install -m 755 kcsd ${dst}/kcsd
  install -m 755 ${WORKDIR}/kcsd.sh ${bin}/kcsd.sh
  ln -snf ../fbpackages/${pkgdir}/kcsd ${bin}/kcsd

  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${WORKDIR}/kcsd.service ${D}${systemd_unitdir}/system
}

FBPACKAGEDIR = "${prefix}/local/fbpackages"

FILES:${PN} = "${FBPACKAGEDIR}/kcsd ${prefix}/local/bin ${systemd_unitdir}/system "


INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_PACKAGE_STRIP = "1"
