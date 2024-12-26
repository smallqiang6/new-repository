#include "mdio_base.h"

int fd;
int mdio_open_fd(void)
{
    fd = open("/dev/mdio_cdev", O_RDWR);
    if (fd < 0) {
        MSD_DBG_ERROR("Open /dev/mdio_cdev device failed!");
        return -1;
    }
    return fd;
}

void mdio_close_fd(void)
{
    close(fd);
}

void mdio_debug(void)
{
    int size;
    FILE *fp;
    char debug_info[DEBUG_INFO_LEN];

    fp = fopen(PHYTOOL_DEBUG_FILE, "r");
    if (fp == NULL) {
        debuglevel = 0;
        return;
    }
    
    memset(debug_info, 0, DEBUG_INFO_LEN);
    size = fread(debug_info, DEBUG_INFO_LEN - 1, 1, fp);
    if (size < 0) {
        fclose(fp);
        debuglevel = 0;
        return;
    }

    if (strncmp(debug_info, DEBUG_OFF_INFO, 1) == 0) {
        fclose(fp);
        debuglevel = 0;
        return;
    }

    if (strncmp(debug_info, DEBUG_ON_INFO, 1) == 0) {
        fclose(fp);
        debuglevel = 1;
        return;
    }

    if (strncmp(debug_info, DEBUG_ON_ERROR, 1) == 0) {
        fclose(fp);
        debuglevel = 2;
        return;
    }

    fclose(fp);

    return;
}

int ast_mdiobus_read(int addr, int reg)
{
    int ret;
    struct mdio_arg args;

    args.addr = addr;
    args.reg = reg;
    ret = ioctl(fd, MDIO_READ, &args);
    if (ret < 0) {
        printf("mdio read 0x%x 0x%x error\n",addr, reg);
        return ret;
    }
    printf("mdio read 0x%x 0x%x 0x%x\n",addr, reg, args.value);
    return args.value;
}

int ast_mdiobus_write(int addr, int reg, unsigned int value)
{
    int ret;
    struct mdio_arg args;

    args.addr = addr;
    args.reg = reg;
    args.value = value;
    ret = ioctl(fd, MDIO_WRITE, &args);
    if (ret < 0) {
        printf("mdio write 0x%x 0x%x error\n",addr, reg);
        return ret;
    }
    return ret;
}
