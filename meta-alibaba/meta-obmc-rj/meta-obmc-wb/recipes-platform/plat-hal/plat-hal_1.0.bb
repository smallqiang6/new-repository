SUMMARY = "platform hal"
DESCRIPTION = "The platform hal"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"


FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI = "file://COPYING \
           file://firmware.py \
           file://bmc.py \
           file://bios.py \
           file://cpu.py \
           file://cpld.py \
           file://misc.py \
           file://dcdc.py           \
           file://fan.py            \
           file://__init__.py       \
           file://temp.py           \
           file://sensor.py         \
           file://psu.py            \
           file://led.py            \
           file://card.py           \
           file://baseutil.py       \
           file://devicebase.py     \
           file://rotor.py    \
           file://osutil.py         \
           file://interface.py      \
           file://chassisbase.py    \
           file://rj_rawcmd.py \
           file://fpga_fw.py \
           file://flash.py \
           file://flash_v2.py \
           file://gpio.py \
           file://uboot.py \
           file://devmon.py \
          "

S = "${WORKDIR}"

inherit python3-dir

do_install() {
   mkdir -p ${D}/${PYTHON_SITEPACKAGES_DIR}/plat_hal

   for file in ${S}/*.py; do
     install -m 644 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/plat_hal
   done
}

FILES:${PN} = "${PYTHON_SITEPACKAGES_DIR}"
