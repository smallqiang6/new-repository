SUMMARY = "RESTful server"
DESCRIPTION = "RESTful server"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI += " \
    file://COPYING \
    file://restful.service \
    file://host-watchdog.service \
    file://restore-config.service \
    file://hal_log.pyc \
    file://rest_bmc.pyc \
    file://rest_common.pyc \
    file://rest_fan.pyc \
    file://rest_firmware.pyc \
    file://rest_mgmt.pyc \
    file://rest_misc.pyc \
    file://rest_psu.pyc \
    file://rest_sensor.pyc \
    file://rest_server.pyc \
    file://host_watchdog.pyc \
    file://sysmgmt.pyc \
    file://sysconf.pyc \
    file://restore-config.pyc \
    file://rest_evst_sensor.pyc \
    "

S = "${WORKDIR}"

DEPENDS = "python3"

inherit python3-dir
inherit systemd

do_install() {
  mkdir -p ${D}/${PYTHON_SITEPACKAGES_DIR}/restful

  for file in ${S}/*.pyc; do
    install -m 644 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/restful/
  done

  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${S}/restful.service ${D}${systemd_unitdir}/system
  install -m 644 ${S}/host-watchdog.service ${D}${systemd_unitdir}/system
  install -m 644 ${S}/restore-config.service ${D}${systemd_unitdir}/system
}
INSANE_SKIP:${PN} = "usrmerge"
FILES:${PN} += "${systemd_unitdir} ${PYTHON_SITEPACKAGES_DIR}"
SYSTEMD_SERVICE:${PN} = "restful.service host-watchdog.service restore-config.service"
