FILESEXTRAPATHS:prepend := "${THISDIR}/:"

SRC_URI += "file://as15-24d8o-dts/ \
           "

do_configure:prepend() {
  cp ${WORKDIR}/as15-24d8o-dts/* ${STAGING_KERNEL_DIR}/arch/${ARCH}/boot/dts
}
