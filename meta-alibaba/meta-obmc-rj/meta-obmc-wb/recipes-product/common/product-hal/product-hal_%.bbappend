FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://product-common-utils.sh \
            file://wb_sysfs_common_path.sh \
          "
common_sh_dst="/usr/local/bin/common"

do_install:append() {
   mkdir -p ${D}/${common_sh_dst}

   install ${WORKDIR}/product-common-utils.sh ${D}${common_sh_dst}/product-common-utils.sh
   install ${WORKDIR}/wb_sysfs_common_path.sh ${D}${common_sh_dst}/wb_sysfs_common_path.sh

}

FILES:${PN} += "${common_sh_dst}"
