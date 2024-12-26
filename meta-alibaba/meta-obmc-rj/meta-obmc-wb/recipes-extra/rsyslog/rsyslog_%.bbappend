FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

S1= "${WORKDIR}/"
SRC_URI += "file://rsyslog.service \
            file://mce_peci_logrotater.syslog \
"

do_install:append() {
  dst="${D}/usr/local/fbpackages/rotate"
  localbindir="/usr/local/bin"
  install -d $dst
  install -d ${D}${localbindir}
  install -m 644 ${WORKDIR}/mce_peci_logrotater.syslog ${D}${sysconfdir}/mce_peci_logrotater.syslog
  cp -r ${D}/etc/mce_peci_logrotater.syslog ${D}/etc/logrotate.d/
  install -m 644 ${WORKDIR}/rsyslog.service ${D}${systemd_unitdir}/system
}

FILES:${PN} += "${systemd_unitdir}/system"
