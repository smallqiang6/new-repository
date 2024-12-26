FILESEXTRAPATHS:prepend := "${THISDIR}/:"

SRC_URI += "file://as15-40q-dts/ \
           "

do_configure:prepend() {
  cp ${WORKDIR}/as15-40q-dts/* ${STAGING_KERNEL_DIR}/arch/${ARCH}/boot/dts
}
