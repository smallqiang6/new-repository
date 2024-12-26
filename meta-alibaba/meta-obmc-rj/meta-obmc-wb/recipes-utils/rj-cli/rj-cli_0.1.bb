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

SRC_URI += "file://phy.sh \
            file://bmc.sh \
            file://sol.sh \
            file://platformutil.py \
            file://cpuparser \
            file://COPYING \
            file://cpuparser_D1734.py \
            file://psu-util.py \
            "

S = "${WORKDIR}"
inherit python3-dir
do_install:append() {

    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 755 ${WORKDIR}/phy.sh ${D}${localbindir}/phy.sh
    install -m 755 ${WORKDIR}/bmc.sh ${D}${localbindir}/bmc.sh
    install -m 755 ${WORKDIR}/sol.sh ${D}${localbindir}/sol.sh
    install -m 755 ${WORKDIR}/platformutil.py ${D}${localbindir}/platformutil.py
    install -m 755 ${WORKDIR}/cpuparser ${D}${localbindir}/cpuparser
    install -m 755 ${WORKDIR}/psu-util.py ${D}${localbindir}/psu-util.py
    dst="${PYTHON_SITEPACKAGES_DIR}"
    install -d ${D}${dst}/
    install -m 644 ${WORKDIR}/cpuparser_D1734.py     ${D}${dst}/cpuparser_D1734.py
}

FILES:${PN} += "/usr/local"
FILES:${PN} += "${PYTHON_SITEPACKAGES_DIR}"
