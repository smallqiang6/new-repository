FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://rsyslog.conf \
            file://rsyslog.logrotate \
            file://rotate_console_log \
            file://logrotate.conf \
            file://syslog.rsyslog \
            file://rsyslog.service \
"
inherit systemd
SYSTEMD_SERVICE:${PN} = "rsyslog.service"

do_install:append() {
  dst="${D}/usr/local/fbpackages/rotate"
  localbindir="/usr/local/bin"
  install -d $dst
  install -d ${D}${localbindir}
  install -m 644 ${WORKDIR}/rsyslog.conf ${D}${sysconfdir}/rsyslog.conf
  install -m 644 ${WORKDIR}/rsyslog.logrotate ${D}${sysconfdir}/logrotate.rsyslog
  install -m 755 ${WORKDIR}/rotate_console_log ${dst}/console_log
  #install -m 644 ${WORKDIR}/logrotate.conf ${D}${sysconfdir}/logrotate.conf

  sed -i "s/__PLATFORM_NAME__/${MACHINE}/g;s/__OPENBMC_VERSION__/${OPENBMC_VERSION}/g" ${D}${sysconfdir}/rsyslog.conf

  install -m 755 ${WORKDIR}/syslog.rsyslog ${D}${localbindir}/syslog.rsyslog
  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${WORKDIR}/rsyslog.service ${D}${systemd_unitdir}/system
}

FILES:${PN} += "/usr/local/fbpackages/rotate ${systemd_unitdir}/system /usr/local/bin "
