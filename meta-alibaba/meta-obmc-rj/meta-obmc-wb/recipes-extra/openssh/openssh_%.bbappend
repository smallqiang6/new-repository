FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
            file://sshd.socket \
            file://ssh_host_dsa_key \
            file://ssh_host_dsa_key.pub \
            file://ssh_host_ecdsa_key \
            file://ssh_host_ecdsa_key.pub \
            file://ssh_host_ed25519_key \
            file://ssh_host_ed25519_key.pub \
            file://ssh_host_rsa_key \
            file://ssh_host_rsa_key.pub \
           "

etcsshdir="/etc/ssh"
do_install:append() {
    mkdir -p ${D}/${etcsshdir}
    install -m 600 ${WORKDIR}/ssh_host_dsa_key ${D}${etcsshdir}/ssh_host_dsa_key
    install -m 644 ${WORKDIR}/ssh_host_dsa_key.pub ${D}${etcsshdir}/ssh_host_dsa_key.pub
    install -m 600 ${WORKDIR}/ssh_host_ecdsa_key ${D}${etcsshdir}/ssh_host_ecdsa_key
    install -m 644 ${WORKDIR}/ssh_host_ecdsa_key.pub ${D}${etcsshdir}/ssh_host_ecdsa_key.pub
    install -m 600 ${WORKDIR}/ssh_host_ed25519_key ${D}${etcsshdir}/ssh_host_ed25519_key
    install -m 644 ${WORKDIR}/ssh_host_ed25519_key.pub ${D}${etcsshdir}/ssh_host_ed25519_key.pub
    install -m 600 ${WORKDIR}/ssh_host_rsa_key ${D}${etcsshdir}/ssh_host_rsa_key
    install -m 644 ${WORKDIR}/ssh_host_rsa_key.pub ${D}${etcsshdir}/ssh_host_rsa_key.pub
    sed -i "s/HostKey/#HostKey/g" ${D}${etcsshdir}/sshd_config
}
