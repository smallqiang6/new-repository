FILESEXTRAPATHS:prepend := "${THISDIR}/files:${THISDIR}/policy.conf:"

SRC_URI += " \
        file://journald-maxlevel.conf \
        file://timesyncd.conf \
"

do_install:append() {
    mkdir -p ${D}/etc/systemd/
    install -m 644 ${WORKDIR}/timesyncd.conf ${D}/etc/systemd/timesyncd.conf
}

