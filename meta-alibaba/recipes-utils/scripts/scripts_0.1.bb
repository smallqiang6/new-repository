SUMMARY = "Scripts Interfaces"
DESCRIPTION = "It provides the scripts "
SECTION = "base"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

SRC_URI += "file://COPYING \
            file://power \
            file://led_location \
            "

S = "${WORKDIR}"


do_install() {
  localbindir="/usr/local/bin"
  install -d ${D}${localbindir}

  install -m 755 power ${D}${localbindir}/power
  install -m 755 led_location ${D}${localbindir}/led_location
}

FILES:${PN} += "/usr/local ${localbindir} "
