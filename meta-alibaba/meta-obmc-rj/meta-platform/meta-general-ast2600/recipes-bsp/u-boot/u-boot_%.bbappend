FILESEXTRAPATHS:prepend := "${THISDIR}/:"

SRC_URI += "file://src/ \
            "

S = "${WORKDIR}/git"

do_configure:prepend () {
  cp ${WORKDIR}/src/product_info.h ${S}/include/configs/
}