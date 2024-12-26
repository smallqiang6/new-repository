
#ifndef __SMI_H__
#define __SMI_H__

#include <rtk_types.h>
#include "rtk_error.h"
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>

extern rtk_uint32 smi_SCK;
extern rtk_uint32 smi_SDA;

#define MDC_MDIO_CTRL0_REG          31
#define MDC_MDIO_START_REG          29
#define MDC_MDIO_CTRL1_REG          21
#define MDC_MDIO_ADDRESS_REG        23
#define MDC_MDIO_DATA_WRITE_REG     24
#define MDC_MDIO_DATA_READ_REG      25
#define MDC_MDIO_PREAMBLE_LEN       32

#define MDC_MDIO_START_OP          0xFFFF
#define MDC_MDIO_ADDR_OP           0x000E
#define MDC_MDIO_READ_OP           0x0001
#define MDC_MDIO_WRITE_OP          0x0003

#define SPI_READ_OP                 0x3
#define SPI_WRITE_OP                0x2
#define SPI_READ_OP_LEN             0x8
#define SPI_WRITE_OP_LEN            0x8
#define SPI_REG_LEN                 16
#define SPI_DATA_LEN                16

#define GPIO_DIR_IN                 1
#define GPIO_DIR_OUT                0
#define GPIO_HIGH                   1
#define GPIO_LOW                    0

#define ack_timer                   5

#define DELAY                        1000
#define CLK_DURATION(clk)            { int i; for(i=0; i<clk; i++); }

#define UNDEFINE                    0

struct rg_gpio_group {
    int gpio;
    int direction;
    int value;
};

#define GPIO_IOC_MAGIC              'z'
#define GPIO_REQUEST                _IOWR(GPIO_IOC_MAGIC, 0, struct rg_gpio_group *)
#define GPIO_SET_DIR                _IOWR(GPIO_IOC_MAGIC, 1, struct rg_gpio_group *)
#define GPIO_SET_VAL                _IOWR(GPIO_IOC_MAGIC, 2, struct rg_gpio_group *)
#define GPIO_GET_VAL                _IOWR(GPIO_IOC_MAGIC, 3, struct rg_gpio_group *)
#define GPIO_RELEASE                _IOWR(GPIO_IOC_MAGIC, 4, struct rg_gpio_group *)

rtk_int32 smi_read(rtk_uint32 mAddrs, rtk_uint32 *rData);
rtk_int32 smi_write(rtk_uint32 mAddrs, rtk_uint32 rData);

#endif /* __SMI_H__ */


