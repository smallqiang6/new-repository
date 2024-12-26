FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRCREV="8600e9e279a638f3f1286d3c2dd7c45507385265"

SRC_URI += "file://defconfig-5.15/${SOC_MODEL}/defconfig \
            file://dts/ \
            file://patches/bmc.cfg \
            file://patches/0001-sync-aspeed-SDK.patch \
            file://patches/0002-Summary-kernel-5.15.80-first-review.patch \
            file://patches/0003-Summary-fix-ast-g5-dtsi-kcs-config.patch \
            file://patches/0004-support-ast26.patch \
            file://patches/0005-Summary-fix-rtc-pcf85063-bug.patch \
            file://patches/0006-fix-bug-53134-avoid.patch \
            file://patches/0007-add-wb_aspeed_common-dts-node.patch \
            file://patches/0008-Summary-add-emmc-recovery.patch \
            file://patches/0009-Summary-fix-aspeed-socinfo.patch \
            file://patches/0010-Summary-mtd-debugfs-add-jedec-id.patch \
            "

do_configure:prepend() {
  cp ${WORKDIR}/dts/* ${STAGING_KERNEL_DIR}/arch/${ARCH}/boot/dts
}
