# Copyright 2014-present Facebook. All Rights Reserved.
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

DEPENDS:append = " libipmi libfruid update-rc.d-native libpal"
RDEPENDS:${PN} += "libipmi libfruid"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://ipmid.service \
           file://sensor.c \
           file://lan.c \
          "

S = "${WORKDIR}"

CFLAGS:prepend = " -DDEBUG -Wno-unused-but-set-variable "
inherit systemd
SYSTEMD_SERVICE:${PN} = "ipmid.service"

do_install() {
  dst="${D}/usr/local/fbpackages/${pkgdir}"
  bin="${D}/usr/local/bin"
  install -d $dst
  install -d $bin
  install -m 755 ipmid ${dst}/ipmid
  ln -snf ../fbpackages/${pkgdir}/ipmid ${bin}/ipmid

  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${WORKDIR}/ipmid.service ${D}${systemd_unitdir}/system
}

FBPACKAGEDIR = "${prefix}/local/fbpackages"

FILES:${PN} = "${FBPACKAGEDIR}/ipmid ${prefix}/local/bin ${systemd_unitdir}/system "

INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_PACKAGE_STRIP = "1"
