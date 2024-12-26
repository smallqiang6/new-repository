#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <syslog.h>
#include <rtl8367c_asicdrv_phy.h>
#include <rtk_types.h>
#include <rtk_error.h>
#include <smi.h>
#include <port.h>
#include <rtk_switch.h>

int fd;

static rtk_api_ret_t gpio_request(struct rg_gpio_group gpio, int gpio_pin) {
    rtk_api_ret_t ret;

    gpio.gpio = gpio_pin;
    gpio.direction = UNDEFINE;
    gpio.value = GPIO_HIGH;

    ret = ioctl(fd, GPIO_REQUEST, &gpio);
    if (ret < 0) {
        printf("gpio_request ioctl error %d\n", ret);
        return ret;
    }
    return 0;
}

static rtk_api_ret_t gpio_free(struct rg_gpio_group gpio, int gpio_pin) {
    rtk_api_ret_t ret;

    gpio.gpio = gpio_pin;
    ret = ioctl(fd, GPIO_RELEASE, &gpio);
    if (ret < 0) {
        printf("gpio_free ioctl error %d\n", ret);
        return ret;
    }
    return 0;
}

int main(int argc, char **argv) {
    rtk_api_ret_t ret;
    rtk_uint32 result;
    int addr;
    int data;
    rtk_uint32 port_id;
    rtk_uint32 port_reg;
    rtk_uint32 phy_data;
    rtk_uint32 sgmii_id;
    rtk_uint32 tx_delay;
    rtk_uint32 rx_delay;
    struct rg_gpio_group mdc;
    struct rg_gpio_group mdio;

    fd = open("/dev/rg_gpio", O_RDWR);
    if (fd < 0) {
        printf("open failed %d\n", fd);
        goto exit;
    }

    result = 0;
    ret = gpio_request(mdc, smi_SCK);
    if (ret < 0) {
        printf("ioctl error %d\n", ret);
        goto exit;
    }

    ret = gpio_request(mdc, smi_SDA);
    if (ret < 0) {
        printf("ioctl error %d\n", ret);
        goto free_sck;
    }

    if (argc < 5) {
        printf("Usage: rtk_phy phy [rd | wr] [phyid] [phyreg] [write data]\n");
        goto finish;
    }

    if (!strcmp(argv[1], "smi")) {
        addr = (argv[3]) ? strtoul(argv[2], 0, 0) : 0;
        if (!strcmp(argv[2], "rd")) {
            ret = smi_read(addr, &data);
            if (ret < 0) {
                printf("[error] smi_read failed:%d\n", ret);
                goto finish;
            }
            printf("0x%x\n", data);
        } else if (!strcmp(argv[2], "wr")) {
            if (!argv[4]) {
                printf("[error] error empty data\n");
                goto finish;
            }
            data = strtoul(argv[4], 0, 0);
            ret = smi_write(addr, data);
            if (ret < 0) {
                printf("[error] smi_write failed:%d\n", ret);
                goto finish;
            }
        } 
    } else if (!strcmp(argv[1], "phy")) {
        port_id = (argv[3]) ? strtoul(argv[3], 0, 0) : 0;
        port_reg = (argv[4]) ? strtoul(argv[4], 0, 0) : 0;
        if (port_reg > 31) {
            printf("[error] phy reg out of range\n");
            goto finish;
        }
        if (!strcmp(argv[2], "rd")) {
            ret = rtl8367c_getAsicPHYReg(port_id, port_reg, &phy_data);
            if (ret != 0) {
                printf("[error] rtl8367c_getAsicPHYReg failed:%d\n", ret);
                goto finish;
            }
            printf("0x%x\n", phy_data);
        }

        if (!strcmp(argv[2], "wr")) {
            if (!argv[5]) {
                printf("[error] error empty data\n");
                goto finish;
            }
            phy_data = strtoul(argv[5], 0, 0);
            ret = rtl8367c_setAsicPHYReg(port_id, port_reg, phy_data);
            if (ret != 0) {
                printf("[error] rtl8367c_setAsicPHYReg failed:%d\n", ret);
                goto finish;
            }
        }
    } else if (!strcmp(argv[1], "delay")) {
        ret = rtk_switch_init();
        if (ret != 0) {
            printf("[error] rtk_switch_init failed:%d\n", ret);
            goto finish;
        }

        if (!strcmp(argv[2], "get")) {
            sgmii_id = (argv[3]) ? strtoul(argv[3], 0, 0) : 0;
            ret = rtk_port_rgmiiDelayExt_get(sgmii_id, &tx_delay, &rx_delay);
            if (ret != 0) {
                printf("[error] rtl8367c_setAsicPHYReg failed:%d\n", ret);
                goto finish;
            }
            printf("Rtk Tx delay:[%d] Rx delay:[%d]\n", tx_delay, rx_delay);
        } else if (!strcmp(argv[2], "set")) {
            sgmii_id = (argv[3]) ? strtoul(argv[3], 0, 0) : 0;
            tx_delay = (argv[4]) ? strtoul(argv[4], 0, 0) : 0;
            rx_delay = (argv[5]) ? strtoul(argv[5], 0, 0) : 0;
            ret = rtk_port_rgmiiDelayExt_set(sgmii_id, tx_delay, rx_delay);
            if (ret != 0) {
                printf("[error] rtk_port_rgmiiDelayExt_set failed:%d\n", ret);
                goto finish;
            }
        }
    } else {
        printf("Usage: rtk_phy phy [rd | wr] [phyid] [phyreg] [write data]\n");
    }
finish:
    gpio_free(mdio, smi_SCK);
free_sck:
    gpio_free(mdc, smi_SDA);
exit:
    close(fd);
    return 0;
}
