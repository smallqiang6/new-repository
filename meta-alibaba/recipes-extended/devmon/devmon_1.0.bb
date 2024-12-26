SUMMARY = "Device monitor daemons collection"
DESCRIPTION = "CPU, Power, DC/DC current/voltage/power monitor"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI = "file://COPYING \
           file://cpumon.pyc \
           file://powermon.pyc \
           file://dcdcmon.pyc \
           file://hal_log.pyc \
           file://evstmon.pyc \
           file://hal_evst_sensor.pyc \
           file://cpumon.service \
           file://powermon.service \
           file://dcdcmon.service \
           file://evstmon.service \
          "

S = "${WORKDIR}"

DEPENDS = "python3"
inherit python3-dir
inherit systemd

do_install() {
  mkdir -p ${D}/${PYTHON_SITEPACKAGES_DIR}/devmon

  for file in ${S}/*.pyc; do
    install -m 644 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/devmon/
  done

  install -d ${D}${systemd_unitdir}/system
  cp -f ${S}/cpumon.service ${D}${systemd_unitdir}/system
  cp -f ${S}/powermon.service ${D}${systemd_unitdir}/system
  cp -f ${S}/dcdcmon.service ${D}${systemd_unitdir}/system
  cp -f ${S}/evstmon.service ${D}${systemd_unitdir}/system
}
INSANE_SKIP:${PN} = "usrmerge"
FILES:${PN} = "${systemd_unitdir} ${PYTHON_SITEPACKAGES_DIR}"
SYSTEMD_SERVICE:${PN} = "cpumon.service powermon.service dcdcmon.service evstmon.service"
