FILESEXTRAPATHS:prepend := "${THISDIR}/:"

SRC_URI += "file://as25-128q-dts/ \
           "

do_configure:prepend() {
  cp ${WORKDIR}/as25-128q-dts/* ${STAGING_KERNEL_DIR}/arch/${ARCH}/boot/dts
}
