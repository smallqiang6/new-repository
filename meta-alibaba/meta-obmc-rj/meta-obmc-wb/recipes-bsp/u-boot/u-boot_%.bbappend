FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRCREV = "d5a421c0b3234a848a18ab207aec50f39ebd8787"

SRC_URI += "file://0001-uboot-base-revise.patch \
            file://0002-Summary-uboot-add-ast2600.patch \
            file://0003-Summary-uboot-add-fru-eeprom-decode.patch \
            file://0004-Summary-config-2600-mac2-fixed-link.patch \
            file://0005-Summary-add-26-uboot-stop-wdt2.patch \
            file://0006-Summary-ast26-enable-ecc.patch \
            file://0007-add-bus8-in-uboot.patch \
            file://0008-Summary-uboot-env-add-mac_increased-and-e2-type.patch \
            file://0009-Summary-fix-bug-53134-avoid.patch \
            file://0010-add-9600-defconfig-and-uboot-boardid-match.patch \
            file://0011-get-mac-addr-conformity-and-set-spi-width-single.patch \
            file://0012-Summary-ast2600-add-CONFIG_ENV_ADDR.patch \
            "
