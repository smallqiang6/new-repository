FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI += "file://0001-added-march-c-to-memtester.patch \
            "

INSANE_SKIP:${PN} = "ldflags"
