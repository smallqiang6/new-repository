# Copyright 2018-present Facebook. All Rights Reserved.

inherit wb_kernel_fitimage

require recipes-core/images/fb-openbmc-image.bb
require recipes-core/images/wb-openbmc-common.inc


# Include modules in rootfs
IMAGE_INSTALL += " \
  packagegroup-openbmc-base \
  packagegroup-openbmc-net \
  packagegroup-openbmc-python3 \
  packagegroup-openbmc-rest3 \
  ast-mdio \
  bitbang \
  e2fsprogs \
  flashrom \
  expect \
  fio \
  i2c-tools \
  mtd-utils \
  kcsd \
  ipmbd \
  ipmitool \
  ipmb-util \
  ethtool \
  pflash \
  plat-hal \
  plat-utils \
  product-hal \
  rj-util \
  cpu-error-gpio \
  hal \
  hal-unittest \
  cli \
  os-release \
  diag \
  cpu-peci-space \
  fanctrl \
  restful \
  devmon \
  scripts \
  rj-cli \
  base-files \
  memtester \
  ipmid \
  mterm \
  python3-click \
  stressapptest \
  dhcpcd \
  "
IMAGE_FEATURES += " \
  ssh-server-openssh \
  tools-debug \
  "

DISTRO_FEATURES += " \
  ext2 \
  ipv6 \
  nfs \
  usbgadget \
  usbhost \
  "
PACKAGE_ECCLUDE += " \
  python3-crypt \
  python3-email \
  "
