SUMMARY = "alibaba diag"
DESCRIPTION = "The alibaba diag"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

inherit systemd

DEPENDS:append = " update-rc.d-native"
RDEPENDS:${PN} += "bash"

SRC_URI += "file://COPYING \
            file://bmc.py \
            file://bios.py \
            file://fw.py \
            file://cpu.py \
            file://led.py \
            file://power.py \
            file://pltfm_ali.py \
            file://pltfm_test.py \
            file://bg_diag_cmd \
          "

S = "${WORKDIR}"

do_install:append() {
   localbindir="/usr/local/bin"
   install -d ${D}${localbindir}/
   install -m 755 bmc.py ${D}${localbindir}/bmc.py
   install -m 755 bios.py ${D}${localbindir}/bios.py
   install -m 755 pltfm_ali.py ${D}${localbindir}/pltfm_ali.py
   install -m 755 fw.py ${D}${localbindir}/fw.py
   install -m 755 cpu.py ${D}${localbindir}/cpu.py
   install -m 755 led.py ${D}${localbindir}/led.py
   install -m 755 power.py ${D}${localbindir}/power.py
   install -m 755 pltfm_test.py ${D}${localbindir}/pltfm_test.py
   install -m 755 bg_diag_cmd ${D}${localbindir}/bg_diag_cmd
}

FILES:${PN} += "/usr/local"
