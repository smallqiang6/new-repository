KERNEL_DEVICETREE = "aspeed-bmc-as15-24d8o.dtb \
                     aspeed-bmc-as25-128q.dtb \
                     aspeed-bmc-as15-40q.dtb \
                    "

require conf/machine/include/ast2620.inc

UBOOT_MACHINE = "wb-ast2600-9600_config"
DEFAULT_TIMEZONE = "Asia/Shanghai"
SERIAL_CONSOLES = "9600;ttyS4"
