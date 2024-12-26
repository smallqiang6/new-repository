FILESEXTRAPATHS:prepend := "${THISDIR}/files/rtk_switch:"

SECTION = "base"
PR = "r0"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

DEPENDS:append = " update-rc.d-native"

SRC_URI = "\
    file://acl.c \
    file://chip.c \
    file://COPYING \
    file://cpuTag.c \
    file://dal_mgmt.c \
    file://dal_rtl8373_acl.c \
    file://dal_rtl8373_cpuTag.c \
    file://dal_rtl8373_dos.c \
    file://dal_rtl8373_dot1x.c \
    file://dal_rtl8373_drv.c \
    file://dal_rtl8373_eee.c \
    file://dal_rtl8373_fc.c \
    file://dal_rtl8373_gpio.c \
    file://dal_rtl8373_hsb.c \
    file://dal_rtl8373_i2c.c \
    file://dal_rtl8373_igmp.c \
    file://dal_rtl8373_interrupt.c \
    file://dal_rtl8373_isolation.c \
    file://dal_rtl8373_led.c \
    file://dal_rtl8373_lut.c \
    file://dal_rtl8373_macsec.c \
    file://dal_rtl8373_mapper.c \
    file://dal_rtl8373_mib.c \
    file://dal_rtl8373_mirror.c \
    file://dal_rtl8373_nic.c \
    file://dal_rtl8373_parser.c \
    file://dal_rtl8373_port.c \
    file://dal_rtl8373_ptp.c \
    file://dal_rtl8373_qos.c \
    file://dal_rtl8373_rate.c \
    file://dal_rtl8373_rma.c \
    file://dal_rtl8373_rtkpp.c \
    file://dal_rtl8373_sharemeter.c \
    file://dal_rtl8373_storm.c \
    file://dal_rtl8373_stp.c \
    file://dal_rtl8373_svlan.c \
    file://dal_rtl8373_switch.c \
    file://dal_rtl8373_trunk.c \
    file://dal_rtl8373_vlan.c \
    file://dal_rtl8373_wol.c \
    file://dos.c \
    file://dot1x.c \
    file://eee.c \
    file://gpio.c \
    file://i2c.c \
    file://identify.c \
    file://igmp.c \
    file://interrupt.c \
    file://isolation.c \
    file://l2.c \
    file://led.c \
    file://macsec.c \
    file://main.c \
    file://Makefile \
    file://mdio_base.c \
    file://mib.c \
    file://miim.c \
    file://mirror.c \
    file://nic.c \
    file://phy_rtl8224.c \
    file://port.c \
    file://ptp.c \
    file://qos.c \
    file://rate.c \
    file://rldp.c \
    file://rma.c \
    file://rtk_switch.c \
    file://rtl8373_asicdrv.c \
    file://rtl8373_regField_list.c \
    file://rtl8373_reg_list.c \
    file://rtl8373_smi.c \
    file://rtl8373_tableField_list.c \
    file://rtl8373_table_list.c \
    file://Rules.mk \
    file://sharemeter.c \
    file://storm.c \
    file://svlan.c \
    file://trunk.c \
    file://vlan.c \
    file://include/acl.h \
    file://include/chip.h \
    file://include/cpuTag.h \
    file://include/dal_mapper.h \
    file://include/dal_mgmt.h \
    file://include/dal_rtl8373_acl.h \
    file://include/dal_rtl8373_cpuTag.h \
    file://include/dal_rtl8373_dos.h \
    file://include/dal_rtl8373_dot1x.h \
    file://include/dal_rtl8373_drv.h \
    file://include/dal_rtl8373_eee.h \
    file://include/dal_rtl8373_fc.h \
    file://include/dal_rtl8373_gpio.h \
    file://include/dal_rtl8373_hsb.h \
    file://include/dal_rtl8373_i2c.h \
    file://include/dal_rtl8373_igmp.h \
    file://include/dal_rtl8373_interrupt.h \
    file://include/dal_rtl8373_isolation.h \
    file://include/dal_rtl8373_led.h \
    file://include/dal_rtl8373_lut.h \
    file://include/dal_rtl8373_macsec.h \
    file://include/dal_rtl8373_macsec_ip_reg.h \
    file://include/dal_rtl8373_mapper.h \
    file://include/dal_rtl8373_mib.h \
    file://include/dal_rtl8373_mirror.h \
    file://include/dal_rtl8373_nic.h \
    file://include/dal_rtl8373_parser.h \
    file://include/dal_rtl8373_port.h \
    file://include/dal_rtl8373_ptp.h \
    file://include/dal_rtl8373_qos.h \
    file://include/dal_rtl8373_rate.h \
    file://include/dal_rtl8373_rma.h \
    file://include/dal_rtl8373_rtkpp.h \
    file://include/dal_rtl8373_sharemeter.h \
    file://include/dal_rtl8373_storm.h \
    file://include/dal_rtl8373_stp.h \
    file://include/dal_rtl8373_svlan.h \
    file://include/dal_rtl8373_switch.h \
    file://include/dal_rtl8373_trunk.h \
    file://include/dal_rtl8373_vlan.h \
    file://include/dal_rtl8373_wol.h \
    file://include/dos.h \
    file://include/dot1x.h \
    file://include/eee.h \
    file://include/gpio.h \
    file://include/i2c.h \
    file://include/identify.h \
    file://include/igmp.h \
    file://include/interrupt.h \
    file://include/isolation.h \
    file://include/l2.h \
    file://include/led.h \
    file://include/macsec.h \
    file://include/main.h \
    file://include/mdio_base.h \
    file://include/mib.h \
    file://include/miim.h \
    file://include/mirror.h \
    file://include/nic.h \
    file://include/phydef.h \
    file://include/phy_rtl8224.h \
    file://include/port.h \
    file://include/ptp.h \
    file://include/qos.h \
    file://include/rate.h \
    file://include/rldp.h \
    file://include/rma.h \
    file://include/rtk_error.h \
    file://include/rtk_switch.h \
    file://include/rtk_types.h \
    file://include/rtl8373_asicdrv.h \
    file://include/rtl8373_reg_definition.h \
    file://include/rtl8373_regField_list.h \
    file://include/rtl8373_reg_struct.h \
    file://include/rtl8373_smi.h \
    file://include/rtl8373_tableField_list.h \
    file://include/rtl8373_table_struct.h \
    file://include/sharemeter.h \
    file://include/smi.h \
    file://include/storm.h \
    file://include/svlan.h \
    file://include/trunk.h \
    file://include/vlan.h \
    "

S = "${WORKDIR}"
inherit systemd

do_install:append() {
    localbindir="/usr/local/bin"
    install -d ${D}${localbindir}/
    install -m 0755 ${S}/build/rtk_switch ${D}/${localbindir}/rtk_switch
}

FILES:${PN} += "/usr/local"
RDEPENDS:${PN} = "bash"
