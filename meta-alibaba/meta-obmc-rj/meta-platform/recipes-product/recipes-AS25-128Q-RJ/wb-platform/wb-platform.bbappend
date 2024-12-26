FILESEXTRAPATHS:append := "${THISDIR}/files:"

SRC_URI += "file://as25_128q_rj \
            "

do_install:prepend() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    cp -r ${WORKDIR}/as25_128q_rj/config/* ${D}/${localbindir}/
    chmod 755 ${D}${localbindir}/*.sh

    install -d ${D}/etc
    install -d ${D}/etc/.upgrade_test/
    install -d ${D}/etc/.upgrade_test/as25_128q_rj
    cp -r ${WORKDIR}/as25_128q_rj/.upgrade_test/* ${D}/etc/.upgrade_test/as25_128q_rj/
    cp -rf ${WORKDIR}/as25_128q_rj/s3ip_sysfs_cfg ${D}/etc/
}
