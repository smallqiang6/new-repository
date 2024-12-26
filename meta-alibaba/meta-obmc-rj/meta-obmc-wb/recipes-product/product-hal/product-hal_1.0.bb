SUMMARY = "platform hal"
DESCRIPTION = "The platform hal"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"


FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI = "file://COPYING \
           file://ruijieconfig.py \
          "

S = "${WORKDIR}"

inherit python3-dir
as_dst="${PYTHON_SITEPACKAGES_DIR}/product_hal"

do_install() {
   mkdir -p ${D}/${as_dst}
   install ${WORKDIR}/ruijieconfig.py ${D}${as_dst}/ruijieconfig.py
}

FILES:${PN} = "${as_dst}"
