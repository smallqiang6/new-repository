FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://usbcons.service \
            file://usbcons.sh \
          "

S = "${WORKDIR}"

inherit systemd
SYSTEMD_SERVICE:${PN} = "usbcons.service"

do_install() {
  localbindir="${D}/usr/local/bin"
  install -d ${localbindir}
  install -m 755 usbmon.sh ${localbindir}/usbmon.sh
  install -m 755 usbcons.sh ${localbindir}/usbcons.sh

  install -d ${D}${systemd_unitdir}/system
  install -m 644 ${WORKDIR}/usbcons.service ${D}${systemd_unitdir}/system
}

FILES:${PN} = " ${sysconfdir} /usr/local/bin ${systemd_unitdir}/system "
