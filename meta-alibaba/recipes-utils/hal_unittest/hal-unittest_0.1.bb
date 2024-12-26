SUMMARY = "HAL Unittest Interfaces"
DESCRIPTION = "It provides the unittest case of HAL interfaces"
SECTION = "base"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://COPYING;md5=fcc4d94f1de6dd438ee71c8d27483265"

SRC_URI += " \
    file://COPYING \
    file://hal_unittest \
    file://unittest_config.py \
    file://test_fan.py \
    file://test_psu.py \
    file://test_bmc.py \
    file://test_cpu.py \
    file://test_misc.py \
    file://test_firmware.py \
    file://test_temp.py \
    file://test_dcdc.py \
    file://test_sensor.py \
    "

S = "${WORKDIR}"

DEPENDS = "python3"

inherit python3-dir

do_install() {
  install -d ${D}${PYTHON_SITEPACKAGES_DIR}/hal/unittest
  localbindir="/usr/local/bin"
  install -d ${D}${localbindir}

  for file in ${S}/*.py; do
    install -m 755 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/hal/unittest
  done

  install -m 755 hal_unittest ${D}${localbindir}/hal_unittest
}

FILES:${PN} += "/usr/local ${PYTHON_SITEPACKAGES_DIR} ${localbindir} "
