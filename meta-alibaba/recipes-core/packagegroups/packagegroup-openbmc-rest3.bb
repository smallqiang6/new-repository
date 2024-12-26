SUMMARY = "Facebook OpenBMC RESTful packages"

LICENSE = "GPLv2"
PR = "r1"

inherit packagegroup

RDEPENDS:${PN} += " \
  python3-aiohttp \
  python3-async-timeout \
  python3-chardet \
  python3-multidict \
  packagegroup-openbmc-python3 \
  python3-yarl \
  "
