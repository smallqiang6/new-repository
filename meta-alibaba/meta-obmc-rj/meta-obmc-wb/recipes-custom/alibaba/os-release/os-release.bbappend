# WARNING!
#
# These modifications to os-release disable the bitbake parse
# cache (for the os-release recipe only).  Before copying
# and pasting into another recipe ensure it is understood
# what that means!

bmc_version := "v1.0-001"
bmc_id := "OpenBMC"

python() {
    bmc_date = "${@time.strftime('%Y%m%d',time.gmtime())}"
    bmc_version_id = "${bmc_version}" + "-bmc-" + bmc_date
    if bmc_version_id:
        d.setVar('VERSION_ID', bmc_version_id)
    version = "${bmc_version}"
    if version:
        d.setVar('VERSION', version)
    build_id = d.getVar('RELEASE_ID')
    if build_id:
        d.setVar('BUILD_ID', build_id)
    id = "${bmc_id}"
    if id:
        d.setVar('ID', id)
    pretty_name = "Facebook " + "${bmc_id}" + " ${bmc_version}"
    if pretty_name:
        d.setVar('PRETTY_NAME', pretty_name)
}
BUILD_DATE = "${BUILD_ID}"
OS_RELEASE_FIELDS:append = "BUILD_DATE"

# Ensure the git commands run every time bitbake is invoked.
BB_DONT_CACHE = "1"

# Make os-release available to other recipes.
SYSROOT_DIRS:append = " ${sysconfdir}"
