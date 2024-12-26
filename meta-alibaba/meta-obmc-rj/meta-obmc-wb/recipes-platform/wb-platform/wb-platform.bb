FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "file://script \
           file://service \
           file://lib \
           "

inherit systemd
inherit python3-dir
RDEPENDS:${PN} = "bash python3-core"

SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE:${PN} += "platform_driver.service"
SYSTEMD_SERVICE:${PN} += "platform_process.service"
SYSTEMD_SERVICE:${PN} += "platform_driver_late.service"

S = "${WORKDIR}/"

do_work_systemd() {
  install -d ${D}${systemd_system_unitdir}

  install -m 0644 ${S}service/platform_driver.service ${D}${systemd_system_unitdir}
  install -m 0644 ${S}service/platform_process.service ${D}${systemd_system_unitdir}
  install -m 0644 ${S}service/platform_driver_late.service ${D}${systemd_system_unitdir}
}

do_lib_install() {
  install -d ${D}/${PYTHON_SITEPACKAGES_DIR}/

  cp -r ${S}/lib/algorithm ${D}${PYTHON_SITEPACKAGES_DIR}/algorithm
  cp -r ${S}/lib/wbutil ${D}${PYTHON_SITEPACKAGES_DIR}/wbutil
  cp -r ${S}/lib/eepromutil ${D}${PYTHON_SITEPACKAGES_DIR}/eepromutil
}

do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    
    install -m 755 ${S}script/platform-driver-init.sh  ${D}${localbindir}/platform-driver-init.sh
    install -m 755 ${S}script/gen_sw_config.py  ${D}${localbindir}/gen_sw_config.py
    install -m 755 ${S}script/platform_process.py  ${D}${localbindir}/platform_process.py
    install -m 755 ${S}script/platform_driver.py  ${D}${localbindir}/platform_driver.py
    install -m 755 ${S}script/platform_common.py  ${D}${localbindir}/platform_common.py
    install -m 755 ${S}script/platform_config.py  ${D}${localbindir}/platform_config.py
    install -m 755 ${S}script/platform_util.py  ${D}${localbindir}/platform_util.py
    install -m 755 ${S}script/upgrade.py  ${D}${localbindir}/upgrade.py
    install -m 755 ${S}script/warm_upgrade.py  ${D}${localbindir}/warm_upgrade.py
    install -m 755 ${S}script/dev_monitor.py  ${D}${localbindir}/dev_monitor.py
    install -m 755 ${S}script/hal_fanctrl.py  ${D}${localbindir}/hal_fanctrl.py
    install -m 755 ${S}script/hal_ledctrl.py  ${D}${localbindir}/hal_ledctrl.py
    install -m 755 ${S}script/hal_pltfm.py ${D}${localbindir}/hal_pltfm.py
    install -m 755 ${S}script/platform_e2.py ${D}${localbindir}/platform_e2.py
    install -m 755 ${S}script/avscontrol.py ${D}${localbindir}/avscontrol.py
    install -m 755 ${S}script/platform_manufacturer.py ${D}${localbindir}/platform_manufacturer.py
    install -m 755 ${S}script/dfx_xdpe_monitor.py ${D}${localbindir}/dfx_xdpe_monitor.py
    install -m 755 ${S}script/pltfm.py ${D}${localbindir}/pltfm.py
    
    do_work_systemd
    do_lib_install
}

FILES:${PN} += "/usr/sbin"
FILES:${PN} += "/usr/local/bin"
FILES:${PN} += "${PYTHON_SITEPACKAGES_DIR}"
