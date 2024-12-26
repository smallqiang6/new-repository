FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://ntp.conf \
            file://ntpd.service \
           "

inherit systemd
SYSTEMD_SERVICE:${PN} = "ntpd.service"

do_install:append() {
  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${WORKDIR}/ntpd.service ${D}${systemd_unitdir}/system
}
FILES:${PN} += "${systemd_unitdir}/system"
