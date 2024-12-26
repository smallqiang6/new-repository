SUMMARY = "alibaba diag"
DESCRIPTION = "The alibaba diag"
#SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

inherit systemd

DEPENDS:append = " update-rc.d-native"
RDEPENDS:${PN} += "bash"

SRC_URI += "file://fru.py \
            file://diag_bmc.py \
            file://BMC_alibaba_as23_128h_rj_r0_config.py \
            file://BMC_alibaba_as14_128h_rj_r0_config.py \
            file://BMC_alibaba_as13_48f8h_rj_r0_config.py \
            file://BMC_alibaba_as13_32h_rj_r0_config.py \
            file://BMC_alibaba_as14_40d_rj_r0_config.py \
            file://BMC_alibaba_as24_128d_rj_r0_config.py \
            file://BMC_alibaba_ac51_48c2g_rj_r0_config.py \
            file://BMC_alibaba_as61_48e4t_rj_r0_config.py \
            file://BMC_alibaba_as61_48x4t_rj_r0_config.py \
            file://BMC_alibaba_as14f_40d_rj_r0_config.py \
            file://BMC_alibaba_as15_20d4m_rj_r0_config.py \
            file://BMC_alibaba_as14_24d8q_rj_r0_config.py \
            file://BMC_alibaba_as25_128q_rj_r0_config.py \
            file://BMC_alibaba_as51_24d_rj_r0_config.py \
            file://BMC_alibaba_as24_128d_2_rj_r0_config.py \
            file://BMC_alibaba_as15_40q_rj_r0_config.py \
            file://collect_info.conf \
            file://collect_bmc_log \
            file://COPYING \
            file://i18n/locale/en_US/LC_MESSAGES/diag_bmc.mo \
            file://i18n/locale/zh_CN/LC_MESSAGES/diag_bmc.mo \
          "

S = "${WORKDIR}"

do_install:append() {
   localbindir="/usr/local/bin"
   install -d ${D}${localbindir}/

   install -m 755 fru.py ${D}${localbindir}/fru.py
   install -m 755 diag_bmc.py ${D}${localbindir}/diag_bmc.py
   install -m 755 BMC_alibaba_as23_128h_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as23_128h_rj_r0_config.py
   install -m 755 BMC_alibaba_as14_128h_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as14_128h_rj_r0_config.py
   install -m 755 BMC_alibaba_as13_48f8h_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as13_48f8h_rj_r0_config.py
   install -m 755 BMC_alibaba_as13_32h_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as13_32h_rj_r0_config.py
   install -m 755 BMC_alibaba_as14_40d_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as14_40d_rj_r0_config.py
   install -m 755 BMC_alibaba_as24_128d_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as24_128d_rj_r0_config.py
   install -m 755 BMC_alibaba_ac51_48c2g_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_ac51_48c2g_rj_r0_config.py
   install -m 755 BMC_alibaba_as61_48e4t_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as61_48e4t_rj_r0_config.py
   install -m 755 BMC_alibaba_as61_48x4t_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as61_48x4t_rj_r0_config.py
   install -m 755 BMC_alibaba_as14f_40d_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as14f_40d_rj_r0_config.py
   install -m 755 BMC_alibaba_as15_20d4m_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as15_20d4m_rj_r0_config.py
   install -m 755 BMC_alibaba_as14_24d8q_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as14_24d8q_rj_r0_config.py
   install -m 755 BMC_alibaba_as25_128q_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as25_128q_rj_r0_config.py
   install -m 755 BMC_alibaba_as51_24d_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as51_24d_rj_r0_config.py
   install -m 755 BMC_alibaba_as24_128d_2_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as24_128d_2_rj_r0_config.py
   install -m 755 BMC_alibaba_as15_40q_rj_r0_config.py ${D}${localbindir}/BMC_alibaba_as15_40q_rj_r0_config.py
   install -m 755 collect_info.conf ${D}${localbindir}/collect_info.conf
   install -m 755 collect_bmc_log ${D}${localbindir}/collect_bmc_log
   install -d ${D}${localbindir}/i18n/locale/en_US/LC_MESSAGES
   install -d ${D}${localbindir}/i18n/locale/zh_CN/LC_MESSAGES
   install -m 755 ${S}/i18n/locale/en_US/LC_MESSAGES/diag_bmc.mo ${D}${localbindir}/i18n/locale/en_US/LC_MESSAGES
   install -m 755 ${S}/i18n/locale/zh_CN/LC_MESSAGES/diag_bmc.mo ${D}${localbindir}/i18n/locale/zh_CN/LC_MESSAGES
}

FILES:${PN} += "/usr/local"
