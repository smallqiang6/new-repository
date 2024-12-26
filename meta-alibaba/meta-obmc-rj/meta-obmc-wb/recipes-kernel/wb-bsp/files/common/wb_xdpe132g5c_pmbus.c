#include <linux/err.h>
#include <linux/i2c.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/hwmon-sysfs.h>
#include <linux/string.h>
#include <linux/sysfs.h>
#include <linux/delay.h>
#include <linux/mutex.h>
#include "wb_pmbus.h"

static int g_wb_xdpe132g5_pmbus_debug = 0;
static int g_wb_xdpe132g5_pmbus_error = 0;

module_param(g_wb_xdpe132g5_pmbus_debug, int, S_IRUGO | S_IWUSR);
module_param(g_wb_xdpe132g5_pmbus_error, int, S_IRUGO | S_IWUSR);

#define WB_XDPE132G5_PMBUS_DEBUG(fmt, args...) do {                                        \
    if (g_wb_xdpe132g5_pmbus_debug) { \
        printk(KERN_INFO "[WB_XDPE132G5_PMBUS][INFO][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define WB_XDPE132G5_PMBUS_ERROR(fmt, args...) do {                                        \
    if (g_wb_xdpe132g5_pmbus_error) { \
        printk(KERN_ERR "[WB_XDPE132G5_PMBUS][ERR][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define BUF_SIZE                    (256)
#define XDPE132G5C_PAGE_NUM         (2)
#define XDPE132G5C_PROT_VR12_5MV    (0x01) /* VR12.0 mode, 5-mV DAC */
#define XDPE132G5C_PROT_VR12_5_10MV (0x02) /* VR12.5 mode, 10-mV DAC */
#define XDPE132G5C_PROT_IMVP9_10MV  (0x03) /* IMVP9 mode, 10-mV DAC */
#define XDPE132G5C_PROT_VR13_10MV   (0x04) /* VR13.0 mode, 10-mV DAC */
#define XDPE132G5C_PROT_IMVP8_5MV   (0x05) /* IMVP8 mode, 5-mV DAC */
#define XDPE132G5C_PROT_VR13_5MV    (0x07) /* VR13.0 mode, 5-mV DAC */
#define RETRY_TIME                  (15)

#define WIDTH_1Byte          (1)
#define WIDTH_2Byte          (2)
#define DEV_NAME_LEN         (64)

typedef struct xdpe_vout_data_s {
    u8 vout_mode;
    int vout_precision;
} xdpe_vout_data_t;

static xdpe_vout_data_t g_xdpe_vout_group[] = {
    {.vout_mode = 0x18, .vout_precision = 256},
    {.vout_mode = 0x17, .vout_precision = 512},
    {.vout_mode = 0x16, .vout_precision = 1024},
    {.vout_mode = 0x15, .vout_precision = 2048},
    {.vout_mode = 0x14, .vout_precision = 4096},
};

typedef struct {
    char dfx_name[BUF_SIZE];
    uint8_t dfx_reg;
    uint8_t width;
} dfx_info_t;

static dfx_info_t dfx_infos[] = {
    {.dfx_name = "PMBUS_STATUS_BYTE", .dfx_reg = PMBUS_STATUS_BYTE, .width = 1},
    {.dfx_name = "PMBUS_STATUS_WORD", .dfx_reg = PMBUS_STATUS_WORD, .width = 2},
    {.dfx_name = "PMBUS_STATUS_VOUT", .dfx_reg = PMBUS_STATUS_VOUT, .width = 1},
    {.dfx_name = "PMBUS_STATUS_IOUT", .dfx_reg = PMBUS_STATUS_IOUT, .width = 1},
    {.dfx_name = "PMBUS_STATUS_INPUT", .dfx_reg = PMBUS_STATUS_INPUT, .width = 1},
    {.dfx_name = "PMBUS_STATUS_TEMPERATURE", .dfx_reg = PMBUS_STATUS_TEMPERATURE, .width = 1},
    {.dfx_name = "PMBUS_STATUS_CML", .dfx_reg = PMBUS_STATUS_CML, .width = 1},
    {.dfx_name = "PMBUS_STATUS_MFR_SPECIFIC", .dfx_reg = PMBUS_STATUS_MFR_SPECIFIC, .width = 1},
#if 0
    {.dfx_name = "PMBUS_STATUS_FAN_12", .dfx_reg = PMBUS_STATUS_FAN_12, .width = 1},
    {.dfx_name = "PMBUS_READ_VIN", .dfx_reg = PMBUS_READ_VIN, .width = 2},
    {.dfx_name = "PMBUS_READ_IIN", .dfx_reg = PMBUS_READ_IIN, .width = 2},
#endif
    {.dfx_name = "PMBUS_READ_VOUT", .dfx_reg = PMBUS_READ_VOUT, .width = 2},
    {.dfx_name = "PMBUS_READ_IOUT", .dfx_reg = PMBUS_READ_IOUT, .width = 2},
    {.dfx_name = "PMBUS_READ_TEMPERATURE_1", .dfx_reg = PMBUS_READ_TEMPERATURE_1, .width = 2},
#if 0
    {.dfx_name = "PMBUS_READ_TEMPERATURE_2", .dfx_reg = PMBUS_READ_TEMPERATURE_2, .width = 2},
    {.dfx_name = "PMBUS_READ_FAN_SPEED_1", .dfx_reg = PMBUS_READ_FAN_SPEED_1, .width = 2},
#endif
    {.dfx_name = "PMBUS_READ_POUT", .dfx_reg = PMBUS_READ_POUT, .width = 2},
    {.dfx_name = "PMBUS_READ_PIN", .dfx_reg = PMBUS_READ_PIN, .width = 2},
};


static ssize_t xdpe132_dfx_info_page_value(struct i2c_client *client,
                         int page,
                         char *buf)
{
    int tmp_value, offset;
    int i;
    ssize_t buf_len;

    offset = strlen(buf);
    for (i = 0; i < ARRAY_SIZE(dfx_infos); i++) {
        switch (dfx_infos[i].width) {
        case WIDTH_1Byte:
            tmp_value = wb_pmbus_read_byte_data(client, page, dfx_infos[i].dfx_reg);
            break;
        case WIDTH_2Byte:
            tmp_value = wb_pmbus_read_word_data(client, page, 0Xff, dfx_infos[i].dfx_reg);
            break;
        default:
            WB_XDPE132G5_PMBUS_ERROR("addr:0x%x width:%d unsupport\n", dfx_infos[i].dfx_reg, dfx_infos[i].width);
            return -ENODEV;
        }
        WB_XDPE132G5_PMBUS_DEBUG("read dfx reg 0x%x success, value: 0x%x\n", dfx_infos[i].dfx_reg, tmp_value);

        if (tmp_value < 0) {
            WB_XDPE132G5_PMBUS_ERROR("read dfx reg 0x%x fail ret = %d\n", dfx_infos[i].dfx_reg, tmp_value);
            return tmp_value;
        }

        if(i == 0) {
            offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "Page%d:\n", page);
        }

        offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "Name: %s, Reg: 0x%x ,Value: 0x%x\n",
                dfx_infos[i].dfx_name, dfx_infos[i].dfx_reg, tmp_value);
    }

    buf_len = strlen(buf);
    WB_XDPE132G5_PMBUS_DEBUG("get blackbox dfx_info success, buf_len: %ld, value: %s\n", buf_len, buf);

    return buf_len;
}

static ssize_t xdpe132_dfx_info_get_show(struct device *dev,
                    struct device_attribute *devattr,
                    char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret, i;

    memset(buf, 0, PAGE_SIZE);
    mutex_lock(&data->update_lock);
    for (i = 0; i < XDPE132G5C_PAGE_NUM; i++) {
        ret = xdpe132_dfx_info_page_value(client, i, buf);
        if(ret < 0) {
            WB_XDPE132G5_PMBUS_ERROR("read page%d reg failed. ret = %d\n", i, ret);
            goto error;
        }
    }
    WB_XDPE132G5_PMBUS_DEBUG("get dfx_info success, buf_len: %ld\n", ret);

error:
    mutex_unlock(&data->update_lock);
    return ret;
}

static ssize_t xdpe132_dfx_info_page_get_show(struct device *dev,
                    struct device_attribute *devattr,
                    char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret;

    memset(buf, 0, PAGE_SIZE);
    mutex_lock(&data->update_lock);
    ret = xdpe132_dfx_info_page_value(client, attr->index, buf);
    if(ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("read page%d reg failed. ret = %d\n", attr->index, ret);
        goto error;
    }
    WB_XDPE132G5_PMBUS_DEBUG("get dfx_info success, buf_len: %ld\n", ret);

error:
    mutex_unlock(&data->update_lock);
    return ret;
}

static ssize_t xdpe132_get_status_word_show(struct device *dev,
        struct device_attribute *devattr,
        char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret;

    mutex_lock(&data->update_lock);

    ret = wb_pmbus_read_word_data(client, attr->index, 0xff, PMBUS_STATUS_WORD);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("read page%d reg 0x%x failed. ret = %d\n", attr->index, PMBUS_STATUS_WORD, ret);
        goto error;
    }

    WB_XDPE132G5_PMBUS_DEBUG("read page%d reg 0x%x success. ret = %d\n", attr->index, PMBUS_STATUS_WORD, ret);
    ret = snprintf(buf, PAGE_SIZE, "0x%04x\n", ret);

error:
    mutex_unlock(&data->update_lock);
    return ret;
}

static ssize_t xdpe132_get_status_byte_show(struct device *dev,
        struct device_attribute *devattr,
        char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret;

    mutex_lock(&data->update_lock);

    ret = wb_pmbus_read_byte_data(client, attr->index, PMBUS_STATUS_BYTE);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("read page%d reg 0x%x failed. ret = %d\n", attr->index, PMBUS_STATUS_BYTE, ret);
        goto error;
    }

    WB_XDPE132G5_PMBUS_DEBUG("read page%d reg 0x%x success. ret = %d\n", attr->index, PMBUS_STATUS_BYTE, ret);
    ret = snprintf(buf, PAGE_SIZE, "0x%02x\n", ret);

error:
    mutex_unlock(&data->update_lock);
    return ret;
}

static SENSOR_DEVICE_ATTR_RO(status0_byte, xdpe132_get_status_byte, 0);
static SENSOR_DEVICE_ATTR_RO(status1_byte, xdpe132_get_status_byte, 1);
static SENSOR_DEVICE_ATTR_RO(status0_word, xdpe132_get_status_word, 0);
static SENSOR_DEVICE_ATTR_RO(status1_word, xdpe132_get_status_word, 1);
static SENSOR_DEVICE_ATTR_RO(dfx_info, xdpe132_dfx_info_get, 0);
static SENSOR_DEVICE_ATTR_RO(dfx_info0, xdpe132_dfx_info_page_get, 0);
static SENSOR_DEVICE_ATTR_RO(dfx_info1, xdpe132_dfx_info_page_get, 1);

static struct attribute *dfx_info_attrs[] = {
    &sensor_dev_attr_status0_byte.dev_attr.attr,
    &sensor_dev_attr_status1_byte.dev_attr.attr,
    &sensor_dev_attr_status0_word.dev_attr.attr,
    &sensor_dev_attr_status1_word.dev_attr.attr,
    &sensor_dev_attr_dfx_info.dev_attr.attr,
    &sensor_dev_attr_dfx_info0.dev_attr.attr,
    &sensor_dev_attr_dfx_info1.dev_attr.attr,
    NULL,
};
static const struct attribute_group dfx_info_group = {
    .attrs = dfx_info_attrs,
};

static ssize_t set_xdpe132g5c_avs(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    int ret;
    unsigned long val;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;

    data = i2c_get_clientdata(client);
    ret = kstrtoul(buf, 0, &val);
    if (ret){
        return ret;
    }
    mutex_lock(&data->update_lock);
    /* set value */
    ret = wb_pmbus_write_word_data(client, attr->index, PMBUS_VOUT_COMMAND, (u16)val);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("set pmbus_vout_command fail\n");
        goto finish_set;
    }
finish_set:
    wb_pmbus_clear_faults(client);
    mutex_unlock(&data->update_lock);
    return (ret < 0) ? ret : count;

}

static ssize_t show_xdpe132g5c_avs(struct device *dev, struct device_attribute *da, char *buf)
{
    int val;
    struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;

    data = i2c_get_clientdata(client);
    mutex_lock(&data->update_lock);
    val = wb_pmbus_read_word_data(client, attr->index, 0xff, PMBUS_VOUT_COMMAND);
    if (val < 0) {
        WB_XDPE132G5_PMBUS_ERROR("fail val = %d\n", val);
        goto finish_show;
    }
finish_show:
    wb_pmbus_clear_faults(client);
    mutex_unlock(&data->update_lock);
    return snprintf(buf, BUF_SIZE, "0x%04x\n", val);
}

static int xdpe_get_vout_precision(struct i2c_client *client, int page, int *vout_precision)
{
    int i, vout_mode, a_size;

    vout_mode = wb_pmbus_read_byte_data(client, page, PMBUS_VOUT_MODE);
    if (vout_mode < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: read xdpe page%d vout mode reg: 0x%x failed, ret: %d\n",
            client->adapter->nr, client->addr, page, PMBUS_VOUT_MODE, vout_mode);
        return vout_mode;
    }

    a_size = ARRAY_SIZE(g_xdpe_vout_group);
    for (i = 0; i < a_size; i++) {
        if (g_xdpe_vout_group[i].vout_mode == vout_mode) {
            *vout_precision = g_xdpe_vout_group[i].vout_precision;
            WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: match, page%d, vout mode: 0x%x, precision: %d\n",
                client->adapter->nr, client->addr, page, vout_mode, *vout_precision);
            break;
        }
    }
    if (i == a_size) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid, page%d, vout mode: 0x%x\n",client->adapter->nr, client->addr,
            page, vout_mode);
        return -EINVAL;
    }
    return 0;
}

static ssize_t xdpe132g5_avs_vout_show(struct device *dev, struct device_attribute *devattr,
                   char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int vout_cmd, ret, vout_precision;
    s64 vout;

    mutex_lock(&data->update_lock);
    ret = xdpe_get_vout_precision(client, attr->index, &vout_precision);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: get xdpe avs%d vout precision failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    vout_cmd = wb_pmbus_read_word_data(client, attr->index, 0xff, PMBUS_VOUT_COMMAND);
    if (vout_cmd < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: read page%d, vout command reg: 0x%x failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, PMBUS_VOUT_COMMAND, vout_cmd);
        mutex_unlock(&data->update_lock);
        return vout_cmd;
    }

    mutex_unlock(&data->update_lock);
    vout = div_s64((s64)vout_cmd * 1000L * 1000L, vout_precision);
    WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: page%d vout: %lld, vout_cmd: 0x%x, precision: %d\n", client->adapter->nr,
        client->addr, attr->index, vout, vout_cmd, vout_precision);
    return snprintf(buf, PAGE_SIZE, "%lld\n", vout);
}

static ssize_t xdpe132g5_avs_vout_store(struct device *dev, struct device_attribute *devattr,
                   const char *buf, size_t count)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int vout_max, vout_min;
    int ret, vout_cmd, vout_cmd_set;
    int vout_precision;
    s64 vout;

    if ((attr->index < 0) || (attr->index >= PMBUS_PAGES)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid index: %d \n", client->adapter->nr, client->addr,
            attr->index);
        return -EINVAL;
    }

    ret = kstrtos64(buf, 0, &vout);
    if (ret) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid value: %s \n", client->adapter->nr, client->addr, buf);
        return -EINVAL;
    }

    if (vout <= 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid value: %lld \n", client->adapter->nr, client->addr, vout);
        return -EINVAL;
    }

    vout_max = data->vout_max[attr->index];
    vout_min = data->vout_min[attr->index];
    if ((vout > vout_max) || (vout < vout_min)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: vout value: %lld, out of range [%d, %d] \n", client->adapter->nr,
            client->addr, vout, vout_min, vout_max);
        return -EINVAL;
    }

    mutex_lock(&data->update_lock);
    ret = xdpe_get_vout_precision(client, attr->index, &vout_precision);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: get xdpe avs%d vout precision failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    vout_cmd_set = div_s64(vout * vout_precision, 1000L * 1000L);
    if (vout_cmd_set > 0xffff) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid value, page%d, vout: %lld, vout_precision: %d, vout_cmd_set: 0x%x\n",
            client->adapter->nr, client->addr, attr->index, vout, vout_precision, vout_cmd_set);
        mutex_unlock(&data->update_lock);
        return -EINVAL;
    }

    /* Read the VOUT_COMMAND register to confirm whether it needs to be set */
    vout_cmd = wb_pmbus_read_word_data(client, attr->index, 0xff, PMBUS_VOUT_COMMAND);
    if (vout_cmd < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: read page%d, vout command reg: 0x%x failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, PMBUS_VOUT_COMMAND, vout_cmd);
        mutex_unlock(&data->update_lock);
        return vout_cmd;
    }
    if (vout_cmd == vout_cmd_set) {
        WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: page%d vout cmd read: 0x%x is equal to vout cmd set: 0x%x, do nothing\n",
            client->adapter->nr, client->addr, attr->index, vout_cmd, vout_cmd_set);
        mutex_unlock(&data->update_lock);
        return count;
    }

    /* set VOUT_COMMAND */
    ret = wb_pmbus_write_word_data(client, attr->index, PMBUS_VOUT_COMMAND, (u16)vout_cmd_set);
    if (ret < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: set xdpe page%d vout cmd reg: 0x%x, value: 0x%x failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, PMBUS_VOUT_COMMAND, vout_cmd_set, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    /* read back VOUT_COMMAND */
    vout_cmd = wb_pmbus_read_word_data(client, attr->index, 0xff, PMBUS_VOUT_COMMAND);
    if (vout_cmd < 0) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: read page%d, vout command reg: 0x%x failed, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, PMBUS_VOUT_COMMAND, vout_cmd);
        mutex_unlock(&data->update_lock);
        return vout_cmd;
    }

    if (vout_cmd != vout_cmd_set) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: page%d vout cmd value check error, vout cmd read: 0x%x, vout cmd set: 0x%x\n",
            client->adapter->nr, client->addr, attr->index, vout_cmd, vout_cmd_set);
        mutex_unlock(&data->update_lock);
        return -EIO;
    }
    mutex_unlock(&data->update_lock);
    WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: set page%d vout cmd success, vout: %lld uV, vout_cmd_set: 0x%x\n",
        client->adapter->nr, client->addr, attr->index, vout, vout_cmd_set);
    return count;
}

static ssize_t xdpe132g5_avs_vout_max_store(struct device *dev,
                   struct device_attribute *devattr, const char *buf, size_t count)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret, vout_threshold;

    if ((attr->index < 0) || (attr->index >= PMBUS_PAGES)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid index: %d \n", client->adapter->nr, client->addr,
            attr->index);
        return -EINVAL;
    }

    ret = kstrtoint(buf, 0, &vout_threshold);
    if (ret) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid value: %s \n", client->adapter->nr, client->addr, buf);
        return -EINVAL;
    }

    WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: vout%d max threshold: %d", client->adapter->nr, client->addr,
        attr->index, vout_threshold);

    data->vout_max[attr->index] = vout_threshold;
    return count;
}

static ssize_t xdpe132g5_avs_vout_max_show(struct device *dev,
                   struct device_attribute *devattr, char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);

    if ((attr->index < 0) || (attr->index >= PMBUS_PAGES)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid index: %d \n", client->adapter->nr, client->addr,
            attr->index);
        return -EINVAL;
    }

    return snprintf(buf, PAGE_SIZE, "%d\n", data->vout_max[attr->index]);
}

static ssize_t xdpe132g5_avs_vout_min_store(struct device *dev,
                   struct device_attribute *devattr, const char *buf, size_t count)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);
    int ret, vout_threshold;

    if ((attr->index < 0) || (attr->index >= PMBUS_PAGES)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid index: %d \n", client->adapter->nr, client->addr,
            attr->index);
        return -EINVAL;
    }

    ret = kstrtoint(buf, 0, &vout_threshold);
    if (ret) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid value: %s \n", client->adapter->nr, client->addr, buf);
        return -EINVAL;
    }

    WB_XDPE132G5_PMBUS_DEBUG("%d-%04x: vout%d min threshold: %d", client->adapter->nr, client->addr,
        attr->index, vout_threshold);

    data->vout_min[attr->index] = vout_threshold;
    return count;
}

static ssize_t xdpe132g5_avs_vout_min_show(struct device *dev,
                   struct device_attribute *devattr, char *buf)
{
    struct i2c_client *client = to_i2c_client(dev->parent);
    struct sensor_device_attribute *attr = to_sensor_dev_attr(devattr);
    struct pmbus_data *data = i2c_get_clientdata(client);

    if ((attr->index < 0) || (attr->index >= PMBUS_PAGES)) {
        WB_XDPE132G5_PMBUS_ERROR("%d-%04x: invalid index: %d \n", client->adapter->nr, client->addr,
            attr->index);
        return -EINVAL;
    }

    return snprintf(buf, PAGE_SIZE, "%d\n", data->vout_min[attr->index]);
}

static SENSOR_DEVICE_ATTR_RW(avs0_vout, xdpe132g5_avs_vout, 0);
static SENSOR_DEVICE_ATTR_RW(avs1_vout, xdpe132g5_avs_vout, 1);
static SENSOR_DEVICE_ATTR_RW(avs0_vout_max, xdpe132g5_avs_vout_max, 0);
static SENSOR_DEVICE_ATTR_RW(avs0_vout_min, xdpe132g5_avs_vout_min, 0);
static SENSOR_DEVICE_ATTR_RW(avs1_vout_max, xdpe132g5_avs_vout_max, 1);
static SENSOR_DEVICE_ATTR_RW(avs1_vout_min, xdpe132g5_avs_vout_min, 1);

static struct attribute *avs_ctrl_attrs[] = {
    &sensor_dev_attr_avs0_vout.dev_attr.attr,
    &sensor_dev_attr_avs1_vout.dev_attr.attr,
    &sensor_dev_attr_avs0_vout_max.dev_attr.attr,
    &sensor_dev_attr_avs0_vout_min.dev_attr.attr,
    &sensor_dev_attr_avs1_vout_max.dev_attr.attr,
    &sensor_dev_attr_avs1_vout_min.dev_attr.attr,
    NULL,
};

static const struct attribute_group avs_ctrl_group = {
    .attrs = avs_ctrl_attrs,
};

static const struct attribute_group *xdpe132g5_attribute_groups[] = {
    &avs_ctrl_group,
    &dfx_info_group,
    NULL,
};

static SENSOR_DEVICE_ATTR(avs0_vout_command, S_IRUGO | S_IWUSR, show_xdpe132g5c_avs, set_xdpe132g5c_avs, 0);
static SENSOR_DEVICE_ATTR(avs1_vout_command, S_IRUGO | S_IWUSR, show_xdpe132g5c_avs, set_xdpe132g5c_avs, 1);

static struct attribute *xdpe132g5c_sysfs_attrs[] = {
    &sensor_dev_attr_avs0_vout_command.dev_attr.attr,
    &sensor_dev_attr_avs1_vout_command.dev_attr.attr,
    NULL,
};

static const struct attribute_group xdpe132g5c_sysfs_attrs_group = {
    .attrs = xdpe132g5c_sysfs_attrs,
};

static int xdpe132g5c_identify(struct i2c_client *client, struct pmbus_driver_info *info)
{
    u8 vout_params;
    int ret, i, retry;

    /* Read the register with VOUT scaling value.*/
    for (i = 0; i < XDPE132G5C_PAGE_NUM; i++) {
        for (retry = 0; retry < RETRY_TIME; retry++) {
            ret = wb_pmbus_read_byte_data(client, i, PMBUS_VOUT_MODE);
            if (ret < 0 || ret == 0xff) {
                msleep(5);
                continue;
            } else {
                break;
            }
        }
        if (ret < 0) {
            return ret;
        }

        switch (ret >> 5) {
        case 0: /* linear mode      */
            if (info->format[PSC_VOLTAGE_OUT] != linear) {
                return -ENODEV;
            }
            break;
        case 1: /* VID mode         */
            if (info->format[PSC_VOLTAGE_OUT] != vid) {
                return -ENODEV;
            }
            vout_params = ret & GENMASK(4, 0);
            switch (vout_params) {
            case XDPE132G5C_PROT_VR13_10MV:
            case XDPE132G5C_PROT_VR12_5_10MV:
                info->vrm_version[i] = vr13;
                break;
            case XDPE132G5C_PROT_VR13_5MV:
            case XDPE132G5C_PROT_VR12_5MV:
            case XDPE132G5C_PROT_IMVP8_5MV:
                info->vrm_version[i] = vr12;
                break;
            case XDPE132G5C_PROT_IMVP9_10MV:
                info->vrm_version[i] = imvp9;
                break;
            default:
                return -EINVAL;
            }
            break;
        case 2: /* direct mode      */
            if (info->format[PSC_VOLTAGE_OUT] != direct) {
                return -ENODEV;
            }
            break;
        default:
            return -ENODEV;
        }
    }

    return 0;
}

static struct pmbus_driver_info xdpe132g5c_info = {
    .pages = XDPE132G5C_PAGE_NUM,
    .format[PSC_VOLTAGE_IN] = linear,
    .format[PSC_VOLTAGE_OUT] = linear,
    .format[PSC_TEMPERATURE] = linear,
    .format[PSC_CURRENT_IN] = linear,
    .format[PSC_CURRENT_OUT] = linear,
    .format[PSC_POWER] = linear,
    .func[0] = PMBUS_HAVE_VIN | PMBUS_HAVE_IIN | PMBUS_HAVE_PIN
        | PMBUS_HAVE_STATUS_INPUT | PMBUS_HAVE_TEMP
        | PMBUS_HAVE_STATUS_TEMP
        | PMBUS_HAVE_VOUT | PMBUS_HAVE_STATUS_VOUT
        | PMBUS_HAVE_IOUT | PMBUS_HAVE_STATUS_IOUT | PMBUS_HAVE_POUT,
    .func[1] = PMBUS_HAVE_VIN | PMBUS_HAVE_IIN | PMBUS_HAVE_PIN
        | PMBUS_HAVE_STATUS_INPUT | PMBUS_HAVE_TEMP | PMBUS_HAVE_STATUS_TEMP
        | PMBUS_HAVE_VOUT | PMBUS_HAVE_STATUS_VOUT
        | PMBUS_HAVE_IOUT | PMBUS_HAVE_STATUS_IOUT | PMBUS_HAVE_POUT,
    .groups = xdpe132g5_attribute_groups,
    .identify = xdpe132g5c_identify,
};

static int xdpe132g5c_probe(struct i2c_client *client,
             const struct i2c_device_id *id)
{
    int status;
    struct pmbus_driver_info *info;

    info = devm_kmemdup(&client->dev, &xdpe132g5c_info, sizeof(*info), GFP_KERNEL);
    if (!info) {
        return -ENOMEM;
    }

    status = wb_pmbus_do_probe(client, &xdpe132g5c_info);
    if (status != 0) {
        WB_XDPE132G5_PMBUS_ERROR("pmbus probe error %d\n", status);
        return status;
    }

    status = sysfs_create_group(&client->dev.kobj, &xdpe132g5c_sysfs_attrs_group);
    if (status != 0) {
        WB_XDPE132G5_PMBUS_ERROR("sysfs_create_group error %d\n", status);
        return status;
    }

    return status;
}

static int xdpe132g5c_remove(struct i2c_client *client)
{
    int ret;

    sysfs_remove_group(&client->dev.kobj, &xdpe132g5c_sysfs_attrs_group);
    ret = wb_pmbus_do_remove(client);
    if (ret != 0){
        WB_XDPE132G5_PMBUS_ERROR("fail remove xdpe132g5c %d\n", ret);
    }
    return ret;
}

static const struct i2c_device_id xdpe132g5c_id[] = {
    {"wb_xdpe132g5c_pmbus", 0},
    {}
};

MODULE_DEVICE_TABLE(i2c, xdpe132g5c_id);

static const struct of_device_id __maybe_unused xdpe132g5c_of_match[] = {
    {.compatible = "infineon,wb_xdpe132g5c_pmbus"},
    {}
};
MODULE_DEVICE_TABLE(of, xdpe132g5c_of_match);

static struct i2c_driver xdpe132g5c_driver = {
    .driver = {
        .name = "wb_xdpe132g5c_pmbus",
        .of_match_table = of_match_ptr(xdpe132g5c_of_match),
    },
    .probe = xdpe132g5c_probe,
    .remove = xdpe132g5c_remove,
    .id_table = xdpe132g5c_id,
};

module_i2c_driver(xdpe132g5c_driver);

MODULE_AUTHOR("support");
MODULE_DESCRIPTION("PMBus driver for Infineon XDPE132g5 family");
MODULE_LICENSE("GPL");
