FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
            file://profile \
           "
do_install:append() {
    if [ ${CONSOLE_IDLE_TIMEOUT} -ne "0" ]; then
        install -m 644 console_idle_logout.sh ${D}/${sysconfdir}/profile.d/console_idle_logout.sh
        sed -i 's/__TMOUT__/${CONSOLE_IDLE_TIMEOUT}/g' ${D}/${sysconfdir}/profile.d/console_idle_logout.sh
    fi
    sed -i '/data1/d' ${D}/${sysconfdir}/fstab
}
