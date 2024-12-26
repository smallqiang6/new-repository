FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://dhclient \
    "

do_install:append() {
    sed -i "/option dhcp6\.solmax-rt 120/d" ${D}${sysconfdir}/dhcpcd.conf
    sed -i "/option dhcp6\.inf-max-rt 120/d" ${D}${sysconfdir}/dhcpcd.conf
    echo "denyinterfaces eth0" >> ${D}${sysconfdir}/dhcpcd.conf
    echo "denyinterfaces eth0.4088" >> ${D}${sysconfdir}/dhcpcd.conf
    echo "denyinterfaces usb0" >> ${D}${sysconfdir}/dhcpcd.conf
}
