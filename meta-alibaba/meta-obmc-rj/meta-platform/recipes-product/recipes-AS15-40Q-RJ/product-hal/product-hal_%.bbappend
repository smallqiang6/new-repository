FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://x86_64_alibaba_as15_40q_rj_r0_config.py \
            file://as15_40q_rj_sensors_config.json \
            file://as15_40q_rj_devices.py \
            file://as15_40q_product-utils.sh \
          "
inherit python3-dir
as15-40q_sh_dst="/usr/local/bin/as15-40q"
as15-40q_dst="${PYTHON_SITEPACKAGES_DIR}/as15-40q/product_hal"
as15-40q_json_dst="/etc/openbmc/devices/AS15-40Q-RJ"

do_install:append() {
   mkdir -p ${D}/${as15-40q_sh_dst}
   mkdir -p ${D}/${as15-40q_dst}
   mkdir -p ${D}/${as15-40q_json_dst}
   install ${WORKDIR}/as15_40q_product-utils.sh ${D}${as15-40q_sh_dst}/product-utils.sh
   install ${WORKDIR}/x86_64_alibaba_as15_40q_rj_r0_config.py ${D}${as15-40q_dst}/config.py
   install ${WORKDIR}/as15_40q_rj_devices.py ${D}${as15-40q_dst}/as15_40q_rj_devices.py
   install ${WORKDIR}/as15_40q_rj_sensors_config.json ${D}${as15-40q_json_dst}/sensors_config.json
}

FILES:${PN} += "${as15-40q_sh_dst}"
FILES:${PN} += "${as15-40q_dst}"
FILES:${PN} += "${as15-40q_json_dst}"
