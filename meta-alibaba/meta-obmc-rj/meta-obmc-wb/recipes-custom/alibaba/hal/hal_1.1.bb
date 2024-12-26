SUMMARY = "alibaba hal"
DESCRIPTION = "The alibaba hal"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI = "file://hal_bmc.py \
           file://hal_cpu.py \
           file://hal_dcdc.py \
           file://hal_fan.py \
           file://hal_firmware.py \
           file://hal_misc.py \
           file://hal_psu.py \
           file://hal_sensor.py \
           file://hal_temp.py \
           file://COPYING \
          "

S = "${WORKDIR}"

inherit python3-dir

do_install() {
  mkdir -p ${D}/${PYTHON_SITEPACKAGES_DIR}/hal

  for file in ${S}/*.py; do
    install -m 755 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/hal/
  done
}

FILES:${PN} = "${PYTHON_SITEPACKAGES_DIR}"
