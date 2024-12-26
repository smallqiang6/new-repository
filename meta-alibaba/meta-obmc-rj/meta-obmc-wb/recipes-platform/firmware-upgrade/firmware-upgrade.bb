LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

S = "${WORKDIR}"
SRC_URI += "file://crc32.c                   \
            file://debug.c                   \
            file://firmware_app.c            \
            file://firmware_upgrade_isc.c    \
            file://firmware_upgrade_mtd.c    \
            file://firmware_upgrade_sysfs.c  \
            file://fw_upg_spi_logic_dev.c    \
            file://hardware.c                \
            file://include/                  \
            file://ispvm_ui.c                \
            file://ivm_core.c                \
            file://Makefile                  \
            file://Rules.mk                  "


RDEPENDS_${PN} = "bash"
do_install() {
    install -d ${D}/usr/sbin
	install -m 0755 ${S}/build/firmware_upgrade ${D}/${sbindir}/
}
