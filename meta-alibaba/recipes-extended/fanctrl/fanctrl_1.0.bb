SUMMARY = "Fan control daemon"
DESCRIPTION = "Fan speed control, with fan monitor and temperature monitor"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI = "file://COPYING \
           file://fand.pyc \
           file://fanmon.pyc \
           file://fsc.pyc \
           file://hal_log.pyc \
           file://tempmon.pyc \
           file://fan-ctrl \
           file://fanctrl.service \
           file://devices/AS23-128H-CL/tempmon_cfg.json \
           file://devices/AS23-128H-CL/pwm_alg_cfg.json \
           file://devices/AS23-128H-CL/psu_cfg.json \
           file://devices/AS13-32H-F-CL/tempmon_cfg.json \
           file://devices/AS13-32H-F-CL/pwm_alg_cfg.json \
           file://devices/AS13-32H-F-CL/psu_cfg.json \
           file://devices/AS13-32H-R-CL/tempmon_cfg.json \
           file://devices/AS13-32H-R-CL/pwm_alg_cfg.json \
           file://devices/AS13-32H-R-CL/psu_cfg.json \
           file://devices/AS13-48F8H-F-CL/tempmon_cfg.json \
           file://devices/AS13-48F8H-F-CL/pwm_alg_cfg.json \
           file://devices/AS13-48F8H-F-CL/psu_cfg.json \
           file://devices/AS13-48F8H-R-CL/tempmon_cfg.json \
           file://devices/AS13-48F8H-R-CL/pwm_alg_cfg.json \
           file://devices/AS13-48F8H-R-CL/psu_cfg.json \
           file://devices/AS23-128H-RJ/tempmon_cfg.json \
           file://devices/AS23-128H-RJ/pwm_alg_cfg.json \
           file://devices/AS23-128H-RJ/psu_cfg.json \
           file://devices/AS13-32H-F-RJ/tempmon_cfg.json \
           file://devices/AS13-32H-F-RJ/pwm_alg_cfg.json \
           file://devices/AS13-32H-F-RJ/psu_cfg.json \
           file://devices/AS13-32H-R-RJ/tempmon_cfg.json \
           file://devices/AS13-32H-R-RJ/pwm_alg_cfg.json \
           file://devices/AS13-32H-R-RJ/psu_cfg.json \
           file://devices/AS13-32H-L-RJ/tempmon_cfg.json \
           file://devices/AS13-32H-L-RJ/pwm_alg_cfg.json \
           file://devices/AS13-32H-L-RJ/psu_cfg.json \
           file://devices/AS13-48F8H-F-RJ/tempmon_cfg.json \
           file://devices/AS13-48F8H-F-RJ/pwm_alg_cfg.json \
           file://devices/AS13-48F8H-F-RJ/psu_cfg.json \
           file://devices/AS13-48F8H-R-RJ/tempmon_cfg.json \
           file://devices/AS13-48F8H-R-RJ/pwm_alg_cfg.json \
           file://devices/AS13-48F8H-R-RJ/psu_cfg.json \
           file://devices/AS14-40D-F-RJ/tempmon_cfg.json \
           file://devices/AS14-40D-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-40D-F-RJ/psu_cfg.json \
           file://devices/AS14-40D-F-RJ/fan_cfg.json \
           file://devices/AS14-128H-RJ/tempmon_cfg.json \
           file://devices/AS14-128H-RJ/pwm_alg_cfg.json \
           file://devices/AS14-128H-RJ/psu_cfg.json \
           file://devices/AS14-128H-RJ/fan_cfg.json \
           file://devices/AS24-128D-RJ/tempmon_cfg.json \
           file://devices/AS24-128D-RJ/pwm_alg_cfg.json \
           file://devices/AS24-128D-RJ/psu_cfg.json \
           file://devices/AS24-128D-RJ/fan_cfg.json \
           file://devices/AS14-40D-F-CL/tempmon_cfg.json \
           file://devices/AS14-40D-F-CL/pwm_alg_cfg.json \
           file://devices/AS14-40D-F-CL/psu_cfg.json \
           file://devices/AS14-40D-F-CL/fan_cfg.json \
           file://devices/AS14-128H-CL/tempmon_cfg.json \
           file://devices/AS14-128H-CL/pwm_alg_cfg.json \
           file://devices/AS14-128H-CL/psu_cfg.json \
           file://devices/AS14-128H-CL/fan_cfg.json \
           file://devices/AS24-128D-CL/tempmon_cfg.json \
           file://devices/AS24-128D-CL/pwm_alg_cfg.json \
           file://devices/AS24-128D-CL/psu_cfg.json \
           file://devices/AS24-128D-CL/fan_cfg.json \
           file://devices/AS61-48E4T-F-RJ/tempmon_cfg.json \
           file://devices/AS61-48E4T-F-RJ/pwm_alg_cfg.json \
           file://devices/AS61-48E4T-F-RJ/psu_cfg.json \
           file://devices/AS61-48E4T-F-RJ/fan_cfg.json \
           file://devices/AS61-48E4T-F-RJ/platform_cfg.json \
           file://devices/AS61-48X4T-F-RJ/tempmon_cfg.json \
           file://devices/AS61-48X4T-F-RJ/pwm_alg_cfg.json \
           file://devices/AS61-48X4T-F-RJ/psu_cfg.json \
           file://devices/AS61-48X4T-F-RJ/fan_cfg.json \
           file://devices/AS61-48X4T-F-RJ/platform_cfg.json \
           file://devices/AC51-48C2G-F-RJ/tempmon_cfg.json \
           file://devices/AC51-48C2G-F-RJ/pwm_alg_cfg.json \
           file://devices/AC51-48C2G-F-RJ/psu_cfg.json \
           file://devices/AC51-48C2G-F-RJ/fan_cfg.json \
           file://devices/AC51-48C2G-F-RJ/platform_cfg.json \
           file://devices/AS14F-40D-F-RJ/tempmon_cfg.json \
           file://devices/AS14F-40D-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14F-40D-F-RJ/psu_cfg.json \
           file://devices/AS14F-40D-F-RJ/fan_cfg.json \
           file://devices/AS15-20D4M-RJ/tempmon_cfg.json \
           file://devices/AS15-20D4M-RJ/pwm_alg_cfg.json \
           file://devices/AS15-20D4M-RJ/psu_cfg.json \
           file://devices/AS15-20D4M-RJ/fan_cfg.json \
           file://devices/AS61-48E4T-F-LC/tempmon_cfg.json \
           file://devices/AS61-48E4T-F-LC/pwm_alg_cfg.json \
           file://devices/AS61-48E4T-F-LC/psu_cfg.json \
           file://devices/AS61-48E4T-F-LC/fan_cfg.json \
           file://devices/AS61-48E4T-F-LC/platform_cfg.json \
           file://devices/AS61-48E4T-LD-RJ/tempmon_cfg.json \
           file://devices/AS61-48E4T-LD-RJ/platform_cfg.json \
           file://devices/AS61-48E4T-LC-RJ/tempmon_cfg.json \
           file://devices/AS61-48E4T-LC-RJ/platform_cfg.json \
           file://devices/AS61-48X4T-F-LC/tempmon_cfg.json \
           file://devices/AS61-48X4T-F-LC/pwm_alg_cfg.json \
           file://devices/AS61-48X4T-F-LC/psu_cfg.json \
           file://devices/AS61-48X4T-F-LC/fan_cfg.json \
           file://devices/AS61-48X4T-F-LC/platform_cfg.json \
           file://devices/AS14-24D8Q-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-LC-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-LC-RJ/platform_cfg.json \
           file://devices/AS14-24D8Q-LD-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-LD-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-LD-RJ/platform_cfg.json \
           file://devices/AS25-128Q-RJ/tempmon_cfg.json \
           file://devices/AS25-128Q-RJ/pwm_alg_cfg.json \
           file://devices/AS25-128Q-RJ/psu_cfg.json \
           file://devices/AS25-128Q-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-F-HQ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-F-HQ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-F-HQ/psu_cfg.json \
           file://devices/AS14-24D8Q-F-HQ/fan_cfg.json \
           file://devices/AS51-24D-A1-F-RJ/tempmon_cfg.json \
           file://devices/AS51-24D-A1-F-RJ/pwm_alg_cfg.json \
           file://devices/AS51-24D-A1-F-RJ/psu_cfg.json \
           file://devices/AS51-24D-A1-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-A1-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-A1-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-A1-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-A1-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-A2-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-A2-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-A2-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-A2-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-A3-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-A3-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-A3-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-A3-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-A4-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-A4-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-A4-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-A4-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-B0-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-B0-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-B0-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-B0-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-B1-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-B1-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-B1-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-B1-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-B2-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-B2-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-B2-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-B2-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-B3-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-B3-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-B3-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-B3-F-RJ/fan_cfg.json \
           file://devices/AS14-24D8Q-B4-F-RJ/tempmon_cfg.json \
           file://devices/AS14-24D8Q-B4-F-RJ/pwm_alg_cfg.json \
           file://devices/AS14-24D8Q-B4-F-RJ/psu_cfg.json \
           file://devices/AS14-24D8Q-B4-F-RJ/fan_cfg.json \
           file://devices/AS25-128Q-HQ/tempmon_cfg.json \
           file://devices/AS25-128Q-HQ/psu_cfg.json \
           file://devices/AS25-128Q-HQ/fan_cfg.json \
           file://devices/AS25-128Q-HQ/pwm_alg_cfg.json \
           file://devices/AS24-128D-2-HQ/tempmon_cfg.json \
           file://devices/AS24-128D-2-HQ/psu_cfg.json \
           file://devices/AS24-128D-2-HQ/fan_cfg.json \
           file://devices/AS24-128D-2-HQ/pwm_alg_cfg.json \
           file://devices/AS25-128Q-H-RJ/tempmon_cfg.json \
           file://devices/AS25-128Q-H-RJ/pwm_alg_cfg.json \
           file://devices/AS25-128Q-H-RJ/psu_cfg.json \
           file://devices/AS25-128Q-H-RJ/fan_cfg.json \
           file://devices/AS24-128D-2-RJ/tempmon_cfg.json \
           file://devices/AS24-128D-2-RJ/pwm_alg_cfg.json \
           file://devices/AS24-128D-2-RJ/psu_cfg.json \
           file://devices/AS24-128D-2-RJ/fan_cfg.json \
           file://devices/AS15-40Q-RJ/tempmon_cfg.json \
           file://devices/AS15-40Q-RJ/pwm_alg_cfg.json \
           file://devices/AS15-40Q-RJ/psu_cfg.json \
           file://devices/AS15-40Q-RJ/fan_cfg.json \
          "

S = "${WORKDIR}"

DEPENDS = "python3"
inherit python3-dir
inherit systemd

do_install() {
  mkdir -p ${D}/${PYTHON_SITEPACKAGES_DIR}/fanctrl

  install -d $$D}/etc/openbmc/devices
  mkdir -p ${D}/etc/openbmc/devices/AS23-128H-CL
  mkdir -p ${D}/etc/openbmc/devices/AS23-128H-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS13-32H-F-CL
  mkdir -p ${D}/etc/openbmc/devices/AS13-32H-R-CL
  mkdir -p ${D}/etc/openbmc/devices/AS13-32H-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS13-32H-R-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS13-32H-L-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS13-48F8H-F-CL
  mkdir -p ${D}/etc/openbmc/devices/AS13-48F8H-R-CL
  mkdir -p ${D}/etc/openbmc/devices/AS13-48F8H-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS13-48F8H-R-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-40D-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-128H-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS24-128D-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-40D-F-CL
  mkdir -p ${D}/etc/openbmc/devices/AS14-128H-CL
  mkdir -p ${D}/etc/openbmc/devices/AS24-128D-CL
  mkdir -p ${D}/etc/openbmc/devices/AS61-48E4T-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS61-48E4T-LD-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS61-48E4T-LC-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS61-48X4T-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AC51-48C2G-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14F-40D-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS15-20D4M-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS61-48E4T-F-LC
  mkdir -p ${D}/etc/openbmc/devices/AS61-48X4T-F-LC
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-LC-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-LD-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS25-128Q-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-F-HQ
  mkdir -p ${D}/etc/openbmc/devices/AS51-24D-A1-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-A1-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-A2-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-A3-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-A4-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-B0-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-B1-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-B2-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-B3-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS14-24D8Q-B4-F-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS25-128Q-HQ
  mkdir -p ${D}/etc/openbmc/devices/AS24-128D-2-HQ
  mkdir -p ${D}/etc/openbmc/devices/AS25-128Q-H-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS24-128D-2-RJ
  mkdir -p ${D}/etc/openbmc/devices/AS15-40Q-RJ

  for file in ${S}/*.pyc; do
    install -m 644 "$file" ${D}${PYTHON_SITEPACKAGES_DIR}/fanctrl/
  done

  install -d ${D}${systemd_unitdir}/system
  cp -r ${S}/devices ${D}/etc/openbmc
  cp -f ${S}/fanctrl.service ${D}${systemd_unitdir}/system

  mkdir -p ${D}/usr/bin
  install -m 755 ${S}/fan-ctrl ${D}/usr/bin/fan-ctrl
}
INSANE_SKIP:${PN} = "usrmerge"
FILES:${PN} = "${systemd_unitdir} ${PYTHON_SITEPACKAGES_DIR} /etc"
FILES:${PN} += "/usr/bin"
SYSTEMD_SERVICE:${PN} = "fanctrl.service"
