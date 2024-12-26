#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <syslog.h>
#include <rtk_types.h>
#include <rtk_error.h>
#include <port.h>
#include <rtk_switch.h>
#include <vlan.h>
#include "main.h"

int fd;
i2c_info_t rtk_i2c_info = {
    .bus = 2,
    .addr = 0x5c
};

static void rtk_switch_help(void)
{
    printf("Usage:\n");
    printf("%-12s rtk_switch phy [rd | wr] i2c_bus i2c_addr phyid phyreg [write data]\n", "phy");
    printf("%-12s rtk_switch smi [rd | wr] i2c_bus i2c_addr reg_addr [write data]\n", "smi");
    printf("%-12s rtk_switch vlan i2c_bus i2c_addr port1 port2 vid\n", "vlan");
}

static rtk_api_ret_t rtk_switch_phy_process(char **argv)
{
    rtk_uint32 phy_id;
    rtk_uint32 dev_addr;
    rtk_uint32 reg_addr;
    rtk_uint32 phy_data;
    rtk_api_ret_t ret;

    phy_id = (argv[5]) ? strtoul(argv[5], 0, 0) : 0;
    dev_addr = (argv[6]) ? strtoul(argv[6], 0, 0) : 0;
    reg_addr = (argv[7]) ? strtoul(argv[7], 0, 0) : 0;

    if (!strcmp(argv[2], "rd")) {
        ret = dal_rtl8373_phy_read(phy_id, dev_addr, reg_addr, &phy_data);
        if (ret != RT_ERR_OK) {
            printf("[error] dal_rtl8373_phy_read failed:0x%x\n", ret);
            return ret;
        }
        printf("0x%x\n", phy_data);
    } else if (!strcmp(argv[2], "wr")) {
        phy_data = (argv[8]) ? strtoul(argv[8], NULL, 0) : 0;
        ret = dal_rtl8373_phy_write(1 << phy_id, dev_addr, reg_addr, phy_data);
        if (ret != RT_ERR_OK) {
            printf("[error] dal_rtl8373_phy_write failed:0x%x\n", ret);
        }
    }

    return ret;
}

static rtk_api_ret_t rtk_switch_smi_process(char **argv)
{
    rtk_uint32 mAddrs;
    rtk_uint32 smi_data;
    rtk_api_ret_t ret;

    mAddrs = (argv[5]) ? strtoul(argv[5], 0, 0) : 0;

    if (!strcmp(argv[2], "rd")) {
        ret = rtl8373_smi_read(mAddrs, &smi_data);
        if (ret != RT_ERR_OK) {
            printf("[error] rtl8373_smi_read failed:0x%x\n", ret);
        }
        printf("0x%x\n", smi_data);
    } else if (!strcmp(argv[2], "wr")) {
        smi_data = (argv[6]) ? strtoul(argv[6], NULL, 0) : 0;
        ret = rtl8373_smi_write(mAddrs, smi_data);
        if (ret != RT_ERR_OK) {
            printf("[error] rtl8373_smi_write failed:0x%x\n", ret);
        }
    }

    return ret;
}

static rtk_api_ret_t rtk_switch_vlan_process(char **argv)
{
    rtk_vlan_entry_t vlan1;
    rtk_vlan_t vid;
    rtk_port_t port1;
    rtk_port_t port2;
    rtk_api_ret_t ret;

    ret = dal_rtl8373_switch_init();
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_switch_init failed:0x%x\n", ret);
        return ret;
    }

    memset(&vlan1, 0x00, sizeof(rtk_vlan_entry_t));

    ret = dal_rtl8373_vlan_init();
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_vlan_init failed:0x%x\n", ret);
        return ret;
    }

    port1 = (argv[4]) ? strtoul(argv[4], 0, 0) : 0;
    port2 = (argv[5]) ? strtoul(argv[5], 0, 0) : 0;
    vid = (argv[6]) ? strtoul(argv[6], 0, 0) : 0;

    RTK_PORTMASK_PORT_SET(vlan1.mbr, port1);
    RTK_PORTMASK_PORT_SET(vlan1.mbr, port2);
    ret = dal_rtl8373_vlan_set(vid, &vlan1);
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_vlan_set failed:0x%x\n", ret);
        return ret;
    }
    ret = dal_rtl8373_vlan_portPvid_set(port1, vid);
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_vlan_portPvid_set failed:0x%x\n", ret);
        return ret;
    }
    ret = dal_rtl8373_vlan_portPvid_set(port2, vid);
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_vlan_portPvid_set failed:0x%x\n", ret);
        return ret;
    }
    ret = dal_rtl8373_vlan_portIgrFilterEnable_set(port1, ENABLED);
    if (ret != RT_ERR_OK) {
        printf("[error] dal_rtl8373_vlan_portIgrFilterEnable_set failed:0x%x\n", ret);
        return ret;
    }

    return ret;
}

static rtk_api_ret_t rtk_switch_i2c_info(char **argv)
{
    rtk_uint8 i2c_bus;
    rtk_uint8 i2c_addr;
    rtk_api_ret_t ret;

    i2c_bus = (argv[3]) ? strtoul(argv[3], 0, 0) : 0;
    i2c_addr = (argv[4]) ? strtoul(argv[4], 0, 0) : 0;

    if (i2c_addr > 0x7f) {
        printf("i2c addr err\n");
        return RT_ERR_INPUT;
    }

    rtk_i2c_info.bus = i2c_bus;
    rtk_i2c_info.addr = i2c_addr;

    return RT_ERR_OK;
}

int main(int argc, char **argv) {

    rtk_uint8 i2c_bus;
    rtk_uint8 i2c_addr;
    rtk_api_ret_t ret;

    if (argc < 2) {
        rtk_switch_help();
        goto finish;
    }

    rtk_switch_i2c_info(argv);

    if (!strcmp(argv[1], "phy")) {
        ret = rtk_switch_phy_process(argv);
    } else if (!strcmp(argv[1], "smi")) {
        ret = rtk_switch_smi_process(argv);
    } else if (!strcmp(argv[1], "vlan")) {
        ret = rtk_switch_vlan_process(argv);
    } else if (!strcmp(argv[1], "init")) {
        ret = dal_rtl8373_switch_init();
        if (ret != RT_ERR_OK) {
            printf("[error] dal_rtl8373_switch_init failed:0x%x\n", ret);
        }
    } else {
        rtk_switch_help();
    }

finish:
free_sck:
exit:
    close(fd);
    return 0;
}
