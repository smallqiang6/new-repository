#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysfs.h>
#include <linux/slab.h>
#include <linux/stat.h>
#include <linux/uaccess.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/i2c.h>
#include <linux/i2c-mux.h>
#include <linux/version.h>
#if LINUX_VERSION_CODE < KERNEL_VERSION(4,19,152)
#include <linux/i2c-mux-gpio.h>
#else
#include <linux/platform_data/i2c-mux-gpio.h>
#endif
#include <linux/platform_device.h>
#include <linux/delay.h>
#include <linux/i2c-smbus.h>
#include <linux/string.h>
#include "platform_common.h"

#define DFD_CPLD_I2C_RETRY_TIMES    3
#define PLATFORM_I2C_RETRY_TIMES    5

#define I2C_RETRY_DELAY    100  /* ms */

int debuglevel = DBG_START;
module_param(debuglevel, int, S_IRUGO | S_IWUSR);

s32 platform_i2c_smbus_read_byte_data(const struct i2c_client *client, u8 command)
{
    int try;
    s32 ret;

    ret = -1;
    for (try = 0; try < PLATFORM_I2C_RETRY_TIMES; try++) {
       if ((ret = i2c_smbus_read_byte_data(client, command) ) >= 0 )
            break;
       msleep(I2C_RETRY_DELAY);
    }
    return ret;

}
EXPORT_SYMBOL(platform_i2c_smbus_read_byte_data);

s32 platform_i2c_smbus_read_i2c_block_data(const struct i2c_client *client,
                u8 command, u8 length, u8 *values)
{
    int try;
    s32 ret;

    ret = -1;
    for (try = 0; try < PLATFORM_I2C_RETRY_TIMES; try++) {
       if ((ret = i2c_smbus_read_i2c_block_data(client, command, length, values) ) >= 0 )
            break;
       msleep(I2C_RETRY_DELAY);
    }
    return ret;
}
EXPORT_SYMBOL(platform_i2c_smbus_read_i2c_block_data);

s32 platform_i2c_smbus_read_word_data(const struct i2c_client *client, u8 command)
{
    int try;
    s32 ret;

    ret = -1;
    for (try = 0; try < PLATFORM_I2C_RETRY_TIMES; try++) {
       if ((ret = i2c_smbus_read_word_data(client, command) ) >= 0 )
            break;
       msleep(I2C_RETRY_DELAY);
    }
    return ret;
}
EXPORT_SYMBOL(platform_i2c_smbus_read_word_data);

static int __init wb_platform_init(void)
{
     /* do nothing just for cpld kernel interface */
    return 0;
}

static void __exit wb_platform_exit(void)
{

}

module_init(wb_platform_init);
module_exit(wb_platform_exit);

MODULE_DESCRIPTION("Platform Support");
MODULE_AUTHOR("support");
MODULE_LICENSE("GPL");
