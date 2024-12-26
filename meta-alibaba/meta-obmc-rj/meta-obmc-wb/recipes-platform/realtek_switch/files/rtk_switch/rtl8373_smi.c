/*
* Copyright c                  Realtek Semiconductor Corporation, 2006
* All rights reserved.
*
* Program : Control smi connected RTL8366
* Abstract :
* Author : Yu-Mei Pan (ympan@realtek.com.cn)
*  $Id: smi.c,v 1.2 2008-04-10 03:04:19 shiehyy Exp $
*/
#include <rtk_types.h>
#include <rtl8373_smi.h>
#include "rtk_error.h"
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include "main.h"

#define I2C_RDWR                    (0x0707)
#if defined(MDC_MDIO_OPERATION)
/*******************************************************************************/
/*  MDC/MDIO porting                                                           */
/*******************************************************************************/
/* define the PHY ID currently used */
#define MDC_MDIO_PHY_ID     0  /* PHY ID 0 or 29 */

/* MDC/MDIO, redefine/implement the following Macro */
#define MDC_MDIO_WRITE(preamableLength, phyID, regID, data)
#define MDC_MDIO_READ(preamableLength, phyID, regID, pData)

#elif defined(SPI_OPERATION)
/*******************************************************************************/
/*  SPI porting                                                                */
/*******************************************************************************/
/* SPI, redefine/implement the following Macro */
#define SPI_WRITE(data, length)
#define SPI_READ(pData, length)

#else
/*******************************************************************************/
/*  I2C porting                                                                */
/*******************************************************************************/
/* Define the GPIO ID for SCK & SDA */
rtk_uint32  smi_SCK = 1;    /* GPIO used for SMI Clock Generation */
rtk_uint32  smi_SDA = 2;    /* GPIO used for SMI Data signal */

/* I2C, redefine/implement the following Macro */
#define GPIO_DIRECTION_SET(gpioID, direction)
#define GPIO_DATA_SET(gpioID, data)
#define GPIO_DATA_GET(gpioID, pData)

#endif

static void rtlglue_drvMutexLock(void)
{
    /* It is empty currently. Implement this function if Lock/Unlock function is needed */
    return;
}

static void rtlglue_drvMutexUnlock(void)
{
    /* It is empty currently. Implement this function if Lock/Unlock function is needed */
    return;
}

#if defined(MDC_MDIO_OPERATION) || defined(SPI_OPERATION)
    /* No local function in MDC/MDIO & SPI mode */
#else
static void _smi_start(void)
{
    /* change GPIO pin to Output only */
    GPIO_DIRECTION_SET(smi_SCK, GPIO_DIR_OUT);
    GPIO_DIRECTION_SET(smi_SDA, GPIO_DIR_OUT);

    /* Initial state: SCK: 0, SDA: 1 */
    GPIO_DATA_SET(smi_SCK, 0);
    GPIO_DATA_SET(smi_SDA, 1);
    CLK_DURATION(DELAY);

    /* CLK 1: 0 -> 1, 1 -> 0 */
    GPIO_DATA_SET(smi_SCK, 1);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 0);
    CLK_DURATION(DELAY);

    /* CLK 2: */
    GPIO_DATA_SET(smi_SCK, 1);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SDA, 0);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 0);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SDA, 1);

}

static void _smi_writeBit(rtk_uint16 signal, rtk_uint32 bitLen)
{
    for( ; bitLen > 0; bitLen--)
    {
        CLK_DURATION(DELAY);

        /* prepare data */
        if ( signal & (1<<(bitLen-1)) )
        {
            GPIO_DATA_SET(smi_SDA, 1);
        }
        else
        {
            GPIO_DATA_SET(smi_SDA, 0);
        }
        CLK_DURATION(DELAY);

        /* clocking */
        GPIO_DATA_SET(smi_SCK, 1);
        CLK_DURATION(DELAY);
        GPIO_DATA_SET(smi_SCK, 0);
    }
}

static void _smi_readBit(rtk_uint32 bitLen, rtk_uint32 *rData)
{
    rtk_uint32 u = 0;

    /* change GPIO pin to Input only */
    GPIO_DIRECTION_SET(smi_SDA, GPIO_DIR_IN);

    for (*rData = 0; bitLen > 0; bitLen--)
    {
        CLK_DURATION(DELAY);

        /* clocking */
        GPIO_DATA_SET(smi_SCK, 1);
        CLK_DURATION(DELAY);
        GPIO_DATA_GET(smi_SDA, &u);
        GPIO_DATA_SET(smi_SCK, 0);

        *rData |= (u << (bitLen - 1));
    }

    /* change GPIO pin to Output only */
    GPIO_DIRECTION_SET(smi_SDA, GPIO_DIR_OUT);
}

static void _smi_stop(void)
{
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SDA, 0);
    GPIO_DATA_SET(smi_SCK, 1);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SDA, 1);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 1);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 0);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 1);

    /* add a click */
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 0);
    CLK_DURATION(DELAY);
    GPIO_DATA_SET(smi_SCK, 1);

    /* change GPIO pin to Input only */
    GPIO_DIRECTION_SET(smi_SDA, GPIO_DIR_IN);
    GPIO_DIRECTION_SET(smi_SCK, GPIO_DIR_IN);
}

#endif /* End of #if defined(MDC_MDIO_OPERATION) || defined(SPI_OPERATION) */

int i2c_fd_open(int i2cbus)
{
    int file, ret;
    char filename[128];

    ret = snprintf(filename, 128, "/dev/i2c-%d", i2cbus);
    filename[ret] = '\0';
    if ((file = open(filename, O_RDWR, S_IRWXU | S_IRWXG | S_IRWXO)) < 0) {
        fprintf(stderr, "Error: Could not open file "
                "`%s': %s\n", filename, strerror(errno));
    }

    return file;
}

rtk_int32 rtl8373_smi_read(rtk_uint32 mAddrs, rtk_uint32 *rData)
{
#if (!defined(MDC_MDIO_OPERATION) && !defined(SPI_OPERATION))
    rtk_uint32 rawData=0, ACK, regData;
    rtk_uint8  con;
    rtk_uint32 ret = RT_ERR_OK;
    rtk_uint16 datah, datal;
#endif

    if(mAddrs > 0xFFFF)
        return RT_ERR_INPUT;

    if(rData == NULL)
        return RT_ERR_NULL_POINTER;
    rtlglue_drvMutexLock();
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data msg;
    rtk_uint8 cmd[2];
    rtk_uint8 data[4];
    int fd;

    cmd[0] = (mAddrs >> 8) & 0xff;
    cmd[1] = (mAddrs & 0xff);

    msgs[0].len = 2;
    msgs[0].addr = rtk_i2c_info.addr;
    msgs[0].buf = cmd;
    msgs[0].flags = 0;

    msgs[1].len = 4;
    msgs[1].addr = rtk_i2c_info.addr;
    msgs[1].buf = data;
    msgs[1].flags = I2C_M_RD;

    msg.nmsgs = 2;
    msg.msgs = msgs;

    fd = i2c_fd_open(rtk_i2c_info.bus);
    ret = ioctl(fd, I2C_RDWR, &msg);
    if (ret < 0) {
        printf("i2c_transfer ioctl failed ret %d.\n", ret);
        close(fd);
        return RT_ERR_FAILED;
    }
    close(fd);

    *rData = data[0];
    *rData |= (data[1] << 8);
    *rData |= (data[2] << 16);
    *rData |= (data[3] << 24);
    rtlglue_drvMutexUnlock();
    return RT_ERR_OK;
}

rtk_int32 rtl8373_smi_write(rtk_uint32 mAddrs, rtk_uint32 rData)
{
#if (!defined(MDC_MDIO_OPERATION) && !defined(SPI_OPERATION))
    rtk_int8 con;
    rtk_uint32 ACK, regData;
    rtk_uint32 ret = RT_ERR_OK;
    rtk_uint16 datal,datah;
#endif

    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data msg;
    unsigned char cmd[6];
    int fd;

    cmd[0] = (mAddrs >> 8) & 0xff;
    cmd[1] = (mAddrs & 0xff);
    cmd[2] = rData & 0xff;
    cmd[3] = (rData >> 8) & 0xff;
    cmd[4] = (rData >> 16) & 0xff;
    cmd[5] = (rData >> 24) & 0xff;

    msgs[0].len = 6;
    msgs[0].addr = rtk_i2c_info.addr;
    msgs[0].buf = cmd;
    msgs[0].flags = 0;

    msg.nmsgs = 1;
    msg.msgs = msgs;

    fd = i2c_fd_open(rtk_i2c_info.bus);
    ret = ioctl(fd, I2C_RDWR, &msg);
    if (ret < 0) {
        printf("i2c_transfer ioctl failed ret %d.\n", ret);
        close(fd);
        return RT_ERR_FAILED;
    }
    close(fd);
    return RT_ERR_OK;
}

