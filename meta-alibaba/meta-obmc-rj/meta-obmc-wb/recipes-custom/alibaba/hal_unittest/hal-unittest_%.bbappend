FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://test_platinterface.py \
          "

S = "${WORKDIR}"

inherit python3-dir

do_install:append() {
  install -d ${D}${PYTHON_SITEPACKAGES_DIR}/hal/unittest

  for file in ${S}/*.py; do
    install -m 755 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/hal/unittest
  done
}

FILES:${PN} += "${PYTHON_SITEPACKAGES_DIR}"
