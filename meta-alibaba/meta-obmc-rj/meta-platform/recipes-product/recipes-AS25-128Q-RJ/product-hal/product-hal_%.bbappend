FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://x86_64_alibaba_as25_128q_rj_r0_config.py \
            file://as25_128q_rj_sensors_config.json \
            file://as25_128q_rj_devices.py \
            file://as25_128q_product-utils.sh \
          "
inherit python3-dir
as25-128q_sh_dst="/usr/local/bin/as25-128q"
as25-128q_dst="${PYTHON_SITEPACKAGES_DIR}/as25-128q/product_hal"
as25-128q_json_dst="/etc/openbmc/devices/AS25-128Q-RJ"

do_install:append() {
   mkdir -p ${D}/${as25-128q_sh_dst}
   mkdir -p ${D}/${as25-128q_dst}
   mkdir -p ${D}/${as25-128q_json_dst}
   install ${WORKDIR}/as25_128q_product-utils.sh ${D}${as25-128q_sh_dst}/product-utils.sh
   install ${WORKDIR}/x86_64_alibaba_as25_128q_rj_r0_config.py ${D}${as25-128q_dst}/config.py
   install ${WORKDIR}/as25_128q_rj_devices.py ${D}${as25-128q_dst}/as25_128q_rj_devices.py
   install ${WORKDIR}/as25_128q_rj_sensors_config.json ${D}${as25-128q_json_dst}/sensors_config.json
}

FILES:${PN} += "${as25-128q_sh_dst}"
FILES:${PN} += "${as25-128q_dst}"
FILES:${PN} += "${as25-128q_json_dst}"