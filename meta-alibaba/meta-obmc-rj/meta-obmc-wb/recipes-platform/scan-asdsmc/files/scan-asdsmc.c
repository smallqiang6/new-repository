/*
 * scan-asdsmc.c
 * Original Author:  gaojianhui@ruijie.com.cn, 2018-10-17
 *
 * Scan Flash interface
 *
 */

#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdlib.h>
#include <syslog.h>

#define SCULL_IOC_MAGIC           '$'
#define SCULL_IOC_ADD_SPI_DEVICE           _IO(SCULL_IOC_MAGIC, 0)
#define SCULL_IOC_REMOVE_SPI_DEVICE        _IO(SCULL_IOC_MAGIC, 1)
#define RG_SPI_ADD                    0
#define RG_SPI_REMOVE                 1

int main(int argc, char *argv[])
{
    int fd;
    int ret;
    int spi_flash;
    int operation;

    operation = -1;
    if (argc < 3) {
        syslog(LOG_DEBUG, "parameter error");
        return -1;
    }
    fd = open("/dev/scull", O_RDWR);
    if (fd < 0) {
        syslog(LOG_DEBUG, "Open scull device failed!");
        return -1;
    }
    
    operation = (!strcmp(argv[1], "add")) ? RG_SPI_ADD : ((!strcmp(argv[1], "remove")) ? RG_SPI_REMOVE : operation);
    spi_flash = strtoul(argv[2], 0, 0);
    switch (operation)
    {
        case RG_SPI_ADD:
            ret = ioctl(fd, SCULL_IOC_ADD_SPI_DEVICE, &spi_flash);
            break;
        case RG_SPI_REMOVE:
            ret = ioctl(fd, SCULL_IOC_REMOVE_SPI_DEVICE, &spi_flash);
            break;
        default:
            syslog(LOG_DEBUG, "cmd format: scan-asdsmc add|remove 0|1|2");
            break;
    }

    if (ret < 0) {
        syslog(LOG_DEBUG, "Can not scan and update flash!");
    }
    close(fd);

    return 0;
}
