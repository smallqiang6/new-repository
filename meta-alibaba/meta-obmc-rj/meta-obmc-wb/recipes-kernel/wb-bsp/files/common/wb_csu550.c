// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Hardware monitoring driver for PMBus devices
 *
 * Copyright (c) 2010, 2011 Ericsson AB.
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/err.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/i2c.h>
#include <linux/hwmon.h>
#include <linux/hwmon-sysfs.h>
#include <linux/pmbus.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

#include "wb_pmbus.h"

struct pmbus_device_info {
    int pages;
    u32 flags;
};

static struct proc_dir_entry *psu_root = NULL;
static const struct i2c_device_id pmbus_id[];

#define MAX_RW_LEN                   (256)
#define MAX_UNIT_LEN                 (16)
#define DEV_NAME_LEN                 (64)
#define CSU550_READ_FAIL             "ACCESS FAILED"
#define PSU_SENSOR_COEFFICIENT       (100LL) /* Keep two decimal places and magnify 100 times */
#define PSU_SYSFS_RV_UNSUPPORT       (999)
#define PSU_DATA_MAX_LEN             (4 * PAGE_SIZE)
#define PSU_ATTR_NAME_MAX_LEN        (24)

/* blackbox type1 */
#define BLACKBOX_START_REG_DC        (0xDC)
#define BLACKBOX_START_REG_E4        (0xE4)
#define BLACKBOX_BLOCK_READ_SIZE     (238)
#define BLACKBOX_EVENT_SIZE          (5)

/* blackbox type2 */
#define BLACKBOX_CONFIG_REG          (0xE4)
#define BLACKBOX_REAL_TIME_DATA_PAGE (0xFF)
#define BLACKBOX_MFR_PAGE_NUM        (5)

/* blackbox clear */
#define BLACKBOX_CLEAR_REG_E0        (0xE0)
#define BLACKBOX_CLEAR_REG_E7        (0xE7)
#define BLACKBOX_CLEAR_REG_E7_VAL1   (0xCEBB)
#define BLACKBOX_CLEAR_REG_E7_VAL2   (0xBBCE)

/* psu reset config */
#define PSU_RESET_OPERATION_VAL      (0x40)
#define PSU_RESET_ON_OFF_CONFIG_VAL  (0x48)

typedef enum {
    BLOCK_DATA  = 0,
    BYTE_DATA   = 1,
    WORD_DATA   = 2,
    WIDTH_4BYTE = 4,
} pmbus_data_width_t;

typedef enum {
    RAWDATA_BYTE = 0,
    RAWDATA_WORD,
    RAWDATA_BUF,
    STRING_DATA,
    LINEAR11,
    LINEAR16,
    LE_DATA, /* Little Endian Data */
    BE_DATA, /* Big Endian Data */
} pmbus_data_type_t;

typedef enum {
    BLACKBOX_DC_BR238 = 1, /* Block read 238 bytes from the 0xdc register, using parsing method 1 */
    BLACKBOX_E4_BR238,     /* Block read 238 bytes from the 0xe4 register, using parsing method 1 */
    BLACKBOX_E4_RW,        /* First configure the 0xe4 register, then read the black box information, using parsing method 2 */
} blackbox_type_t;

typedef enum {
    BLACKBOX_CLEAR_E0 = 1,   /* send 0xE0 to clear blackbox info */
    BLACKBOX_CLEAR_E7_TYPE1, /* write 0xCEBB to 0xE7*/
    BLACKBOX_CLEAR_E7_TYPE2, /* write 0xBBCE to 0xE7*/
} blackbox_clear_type_t;

typedef struct {
    char psu_model[DEV_NAME_LEN];
    blackbox_type_t blackbox_type;
    blackbox_clear_type_t blackbox_clear_type;
    int blackbox_record_num;
} psu_info_t;

typedef struct {
    blackbox_type_t blackbox_type;
    uint8_t blackbox_reg;
    blackbox_clear_type_t blackbox_clear_type;
    char psu_model[DEV_NAME_LEN];
    struct pmbus_driver_info info;
    struct proc_dir_entry *psu_client_proc_ent;
    char psu_data[PSU_DATA_MAX_LEN];
    int blackbox_record_num;
} csu550_info_t;
#define to_csu550_data(_info) container_of(_info, csu550_info_t, info)

typedef struct blackbox_event_s {
    uint8_t power_supply_total_power_on_time[3];
    uint8_t real_time_clock_data_from_system[4];
    uint8_t number_of_ac_power_cycles[2];
    uint8_t number_of_pson_cycles[2];
    uint8_t status_word[2];
    uint8_t status_iout;
    uint8_t status_input;
    uint8_t status_temperature;
    uint8_t status_fan_1_2;
    uint8_t read_vin[2];
    uint8_t read_iin[2];
    uint8_t read_iout[2];
    uint8_t read_temperature_1[2];
    uint8_t read_temperature_2[2];
    uint8_t read_fan_speed_1[2];
    uint8_t read_pin[2];
    uint8_t read_vout[2];
    uint8_t unknown[5];
} blackbox_event_t;

typedef struct blackbox_s {
    /* Part 1 */
    uint8_t len;
    /* Part 2 */
    uint8_t system_top_assembly_number[10];
    uint8_t system_serial_number[10];
    uint8_t motherboard_assembly_number[10];
    uint8_t motherboard_serial_number[10];
    uint8_t present_total_psu_on_time[3];
    uint8_t present_number_of_ac_power_cycles[2];
    uint8_t present_number_of_pson_power_cycles[2];
    /* Part 3 */
    blackbox_event_t event[BLACKBOX_EVENT_SIZE];
} blackbox_t;

typedef struct csu500_procfs_attr_s {
    char name[PSU_ATTR_NAME_MAX_LEN];
    umode_t mode;
    const struct proc_ops *proc_op;
} csu500_procfs_attr_t;

static int psu_proc_data_show(struct seq_file *s, void *v);
static int psu_proc_release(struct inode *inode, struct file *file);

#define DEFINE_PROCFS_ATTRIBUTE(__fops, __show)                                                   \
static int __fops ## _open(struct inode *inode, struct file *file)                                \
{                                                                                                 \
    struct i2c_client *client = PDE_DATA(inode);                                                  \
    struct pmbus_data *data;                                                                      \
    int ret;                                                                                      \
                                                                                                  \
    data = i2c_get_clientdata(client);                                                            \
    mutex_lock(&data->update_lock);                                                               \
                                                                                                  \
    CSU550_DEBUG_DMESG("%d-%04x: Enter %s\n", client->adapter->nr, client->addr, __func__);       \
    __show(client);                                                                               \
    ret = single_open(file, psu_proc_data_show, PDE_DATA(inode));                                 \
    if (ret) {                                                                                    \
        CSU550_DEBUG_ERROR("%d-%04x: single_open failed, ret: %d\n",                              \
            client->adapter->nr, client->addr, ret);                                              \
        mutex_unlock(&data->update_lock);                                                         \
    }                                                                                             \
    CSU550_DEBUG_DMESG("%d-%04x: Leave %s\n",client->adapter->nr, client->addr, __func__);        \
    return ret;                                                                                   \
}                                                                                                 \
static const struct proc_ops __fops = {                                                           \
    .proc_open = __fops ## _open,                                                                 \
    .proc_read = seq_read,                                                                        \
    .proc_lseek = seq_lseek,                                                                      \
    .proc_release = psu_proc_release,                                                             \
}                                                                                                 \

static const psu_info_t psu_infos[] = {
    {.psu_model = "CSU550AP-3",      .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS550N2C",   .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "DPS-550AB-39",    .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "DPS-550AB-40",    .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS550N2RC",  .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "FSP550-21FH",     .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "FSP800-20FL",     .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "CSU800AP-3",      .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS800N2C",   .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS800N2WA",  .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "DPS-800AB-48",    .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "DPS-1300AB-6",    .blackbox_type = BLACKBOX_E4_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS1300D",    .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 5},
    {.psu_model = "GW-CRPS1300N2",   .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 5},
    {.psu_model = "CRPS1300N2",      .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 5},
    {.psu_model = "GW-CRPSD1300",    .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E0, .blackbox_record_num = 5},
    {.psu_model = "CRPS1300D3R",     .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 5},
    {.psu_model = "DPS-1300AB-11",   .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS1300D2WA", .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "DPS-1300-AB",     .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "AP-CA1300F12B1",  .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE2, .blackbox_record_num = 15},
    {.psu_model = "DPS-1600AB-53",   .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS1600D2",   .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "U1A-D1600-J",     .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "DLG2000BM12F10",  .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "CRPS2000D2",      .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "GW-CRPS2000DWA",  .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "DPST-2030AB",     .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE1, .blackbox_record_num = 15},
    {.psu_model = "AP-CA2000F12B1",  .blackbox_type = BLACKBOX_E4_RW,    .blackbox_clear_type = BLACKBOX_CLEAR_E7_TYPE2, .blackbox_record_num = 15},
    {.psu_model = "DLG2700AN12C11",  .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "ECDL270012Gh",    .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "CRPS2700D2",      .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "DLK3000AN12C31",  .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "ECDL3000123",     .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
    {.psu_model = "CRPS3000CL",      .blackbox_type = BLACKBOX_DC_BR238, .blackbox_clear_type = BLACKBOX_CLEAR_E0},
};

typedef struct {
    char pmbus_name[DEV_NAME_LEN];
    uint8_t pmbus_reg;
    pmbus_data_width_t width;
    pmbus_data_type_t data_type;
    char unit[MAX_UNIT_LEN];
} pmbus_info_t;

static pmbus_info_t dfx_infos[] = {
    {.pmbus_name = "STATUS_BYTE", .pmbus_reg = PMBUS_STATUS_BYTE, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_WORD", .pmbus_reg = PMBUS_STATUS_WORD, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "STATUS_VOUT", .pmbus_reg = PMBUS_STATUS_VOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_IOUT", .pmbus_reg = PMBUS_STATUS_IOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_INPUT", .pmbus_reg = PMBUS_STATUS_INPUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_TEMP", .pmbus_reg = PMBUS_STATUS_TEMPERATURE, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_CML", .pmbus_reg = PMBUS_STATUS_CML, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_MFR_SPEC", .pmbus_reg = PMBUS_STATUS_MFR_SPECIFIC, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_FAN", .pmbus_reg = PMBUS_STATUS_FAN_12, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "READ_VIN", .pmbus_reg = PMBUS_READ_VIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_IIN", .pmbus_reg = PMBUS_READ_IIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_VOUT", .pmbus_reg = PMBUS_READ_VOUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_IOUT", .pmbus_reg = PMBUS_READ_IOUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_TEMP1", .pmbus_reg = PMBUS_READ_TEMPERATURE_1, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_TEMP2", .pmbus_reg = PMBUS_READ_TEMPERATURE_2, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_FAN_SPEED", .pmbus_reg = PMBUS_READ_FAN_SPEED_1, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_POUT", .pmbus_reg = PMBUS_READ_POUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "READ_PIN", .pmbus_reg = PMBUS_READ_PIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
};

static pmbus_info_t pmbus_infos[] = {
    {.pmbus_name = "MFR_ID", .pmbus_reg = PMBUS_MFR_ID, .width = BLOCK_DATA, .data_type = STRING_DATA},
    {.pmbus_name = "MFR_MODEL", .pmbus_reg = PMBUS_MFR_MODEL, .width = BLOCK_DATA, .data_type = STRING_DATA},
    {.pmbus_name = "MFR_REVISION", .pmbus_reg = PMBUS_MFR_REVISION, .width = BLOCK_DATA, .data_type = STRING_DATA},
    {.pmbus_name = "MFR_DATE", .pmbus_reg = PMBUS_MFR_DATE, .width = BLOCK_DATA, .data_type = STRING_DATA},
    {.pmbus_name = "MFR_SERIAL", .pmbus_reg = PMBUS_MFR_SERIAL, .width = BLOCK_DATA, .data_type = STRING_DATA},
    /* {.pmbus_name = "PRI_FW_VER", .pmbus_reg = PMBUS_PRI_FW_VER, .width = WORD_DATA},
    {.pmbus_name = "SEC_FW_VER", .pmbus_reg = PMBUS_SEC_FW_VER, .width = WORD_DATA}, */
    {.pmbus_name = "STATUS_WORD", .pmbus_reg = PMBUS_STATUS_WORD, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "STATUS_VOUT", .pmbus_reg = PMBUS_STATUS_VOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_IOUT", .pmbus_reg = PMBUS_STATUS_IOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_INPUT", .pmbus_reg = PMBUS_STATUS_INPUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_TEMP", .pmbus_reg = PMBUS_STATUS_TEMPERATURE, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_CML", .pmbus_reg = PMBUS_STATUS_CML, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_FAN", .pmbus_reg = PMBUS_STATUS_FAN_12, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
};

static pmbus_info_t blackbox_infos[] = {
    {.pmbus_name = "STATUS_WORD", .pmbus_reg = PMBUS_STATUS_WORD, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "STATUS_VOUT", .pmbus_reg = PMBUS_STATUS_VOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_IOUT", .pmbus_reg = PMBUS_STATUS_IOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_INPUT", .pmbus_reg = PMBUS_STATUS_INPUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_TEMP", .pmbus_reg = PMBUS_STATUS_TEMPERATURE, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_CML", .pmbus_reg = PMBUS_STATUS_CML, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_MFR_SPEC", .pmbus_reg = PMBUS_STATUS_MFR_SPECIFIC, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_FAN", .pmbus_reg = PMBUS_STATUS_FAN_12, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "IN_VOLT", .pmbus_reg = PMBUS_READ_VIN, .width = WORD_DATA, .data_type = LINEAR11, .unit = "V"},
    {.pmbus_name = "IN_CURR", .pmbus_reg = PMBUS_READ_IIN, .width = WORD_DATA, .data_type = LINEAR11, .unit = "A"},
    {.pmbus_name = "VCAP", .pmbus_reg = PMBUS_READ_VCAP, .width = WORD_DATA, .data_type = LINEAR11, .unit = "V"},
    {.pmbus_name = "OUT_VOLT", .pmbus_reg = PMBUS_READ_VOUT, .width = WORD_DATA, .data_type = LINEAR16, .unit = "V"},
    {.pmbus_name = "OUT_CURR", .pmbus_reg = PMBUS_READ_IOUT, .width = WORD_DATA, .data_type = LINEAR11, .unit = "A"},
    {.pmbus_name = "TEMP1", .pmbus_reg = PMBUS_READ_TEMPERATURE_1, .width = WORD_DATA, .data_type = LINEAR11, .unit = "C"},
    {.pmbus_name = "TEMP2", .pmbus_reg = PMBUS_READ_TEMPERATURE_2, .width = WORD_DATA, .data_type = LINEAR11, .unit = "C"},
    {.pmbus_name = "TEMP3", .pmbus_reg = PMBUS_READ_TEMPERATURE_3, .width = WORD_DATA, .data_type = LINEAR11, .unit = "C"},
    {.pmbus_name = "FAN_SPEED", .pmbus_reg = PMBUS_READ_FAN_SPEED_1, .width = WORD_DATA, .data_type = LINEAR11, .unit = "RPM"},
    {.pmbus_name = "IN_POWER", .pmbus_reg = PMBUS_READ_POUT, .width = WORD_DATA, .data_type = LINEAR11, .unit = "W"},
    {.pmbus_name = "OUT_POWER", .pmbus_reg = PMBUS_READ_PIN, .width = WORD_DATA, .data_type = LINEAR11, .unit = "W"},
    {.pmbus_name = "MFR_POS_TOTAL", .pmbus_reg = PMBUS_MFR_POS_TOTAL, .width = WIDTH_4BYTE, .data_type = LE_DATA, .unit = "s"},
    {.pmbus_name = "MFR_POS_LAST", .pmbus_reg = PMBUS_MFR_POS_LAST, .width = WIDTH_4BYTE, .data_type = LE_DATA, .unit = "s"},
};

static pmbus_info_t blackbox_raw_infos[] = {
    {.pmbus_name = "STATUS_WORD", .pmbus_reg = PMBUS_STATUS_WORD, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "STATUS_VOUT", .pmbus_reg = PMBUS_STATUS_VOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_IOUT", .pmbus_reg = PMBUS_STATUS_IOUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_INPUT", .pmbus_reg = PMBUS_STATUS_INPUT, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_TEMP", .pmbus_reg = PMBUS_STATUS_TEMPERATURE, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_CML", .pmbus_reg = PMBUS_STATUS_CML, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_MFR_SPEC", .pmbus_reg = PMBUS_STATUS_MFR_SPECIFIC, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "STATUS_FAN", .pmbus_reg = PMBUS_STATUS_FAN_12, .width = BYTE_DATA, .data_type = RAWDATA_BYTE},
    {.pmbus_name = "IN_VOLT", .pmbus_reg = PMBUS_READ_VIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "IN_CURR", .pmbus_reg = PMBUS_READ_IIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "VCAP", .pmbus_reg = PMBUS_READ_VCAP, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "OUT_VOLT", .pmbus_reg = PMBUS_READ_VOUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "OUT_CURR", .pmbus_reg = PMBUS_READ_IOUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "TEMP1", .pmbus_reg = PMBUS_READ_TEMPERATURE_1, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "TEMP2", .pmbus_reg = PMBUS_READ_TEMPERATURE_2, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "TEMP3", .pmbus_reg = PMBUS_READ_TEMPERATURE_2, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "FAN_SPEED", .pmbus_reg = PMBUS_READ_FAN_SPEED_1, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "IN_POWER", .pmbus_reg = PMBUS_READ_POUT, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "OUT_POWER", .pmbus_reg = PMBUS_READ_PIN, .width = WORD_DATA, .data_type = RAWDATA_WORD},
    {.pmbus_name = "MFR_POS_TOTAL", .pmbus_reg = PMBUS_MFR_POS_TOTAL, .width = WIDTH_4BYTE, .data_type = RAWDATA_BUF},
    {.pmbus_name = "MFR_POS_LAST", .pmbus_reg = PMBUS_MFR_POS_LAST, .width = WIDTH_4BYTE, .data_type = RAWDATA_BUF},
};

static int g_csu550_debug = 0;
static int g_csu550_error = 0;

module_param(g_csu550_debug, int, S_IRUGO | S_IWUSR);
module_param(g_csu550_error, int, S_IRUGO | S_IWUSR);

#define CSU550_DEBUG_DMESG(fmt, args...) do {                                        \
    if (g_csu550_debug) { \
        printk(KERN_INFO "[CSU550][DEBUG][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define CSU550_DEBUG_ERROR(fmt, args...) do {                                        \
    if (g_csu550_error) { \
        printk(KERN_ERR "[CSU550][ERR][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

/*
* Removes trailing spaces from the end of a given string.
* @param str The string from which to remove trailing spaces.
*/
static void trim_trailing_spaces(char *str)
{
    int i, len;

    if (str == NULL) {
        return;
    }

    len = strlen(str);
    if (len == 0) {
        return;
    }

    /* Use a for loop to iterate from the end of the string to the beginning */
    for (i = len - 1; i >= 0; --i) {
        if (str[i] != ' ') {
            /* If a non-space character is found, break the loop */
            break;
        }
        str[i] = '\0'; /* Replace the space with the null terminator */
    }
}

static void reg2data_linear(struct pmbus_data *data, int reg_val, int linear, s64 *div_result, s64 *div_mod)
{
    s16 exponent;
    s32 mantissa;
    s64 val;

    if (linear == LINEAR16) {    /* LINEAR16 */
        exponent = data->exponent[0];
        mantissa = (u16)reg_val;
    } else {                /* LINEAR11 */
        exponent = ((s16)reg_val) >> 11;
        mantissa = ((s16)((reg_val & 0x7ff) << 5)) >> 5;
    }

    val = mantissa * PSU_SENSOR_COEFFICIENT;
    if (exponent >= 0) {
        val <<= exponent;
    } else {
        val >>= -exponent;
    }
    *div_result = val / PSU_SENSOR_COEFFICIENT;
    *div_mod = val % PSU_SENSOR_COEFFICIENT;
    return;
}

static int csu550_transfer_read(struct i2c_client *client, u8 *buf, u8 regaddr, size_t count)
{
    struct i2c_adapter *adap;
    struct i2c_msg msgs[2];
    int msgs_num, ret;

    if (!client) {
        CSU550_DEBUG_ERROR("can't get read client\n");
        return -ENODEV;
    }

    adap = client->adapter;
    if (!adap) {
        CSU550_DEBUG_ERROR("can't get read adap\n");
        return -ENODEV;
    }

    if (adap->algo->master_xfer) {
        memset(msgs, 0, sizeof(msgs));
        msgs[0].addr = client->addr;
        msgs[0].flags = 0;
        msgs[0].len = 1;
        msgs[0].buf = &regaddr;

        msgs[1].addr = client->addr;
        msgs[1].flags = I2C_M_RD;
        msgs[1].len = count;
        msgs[1].buf = buf;

        msgs_num = 2;
        ret = i2c_transfer(client->adapter, msgs, msgs_num);

        if (ret != msgs_num) {
            CSU550_DEBUG_ERROR("i2c_transfer read error\n");
            return -EINVAL;
        }
    } else {
        CSU550_DEBUG_ERROR("don't find read master_xfer\n");
        return -EINVAL;

    }
    return 0;
}

static int csu550_info_init(struct i2c_client *client, csu550_info_t *csu550_info)
{
    int i, block_size, match_flag;
    char block_data[I2C_SMBUS_BLOCK_MAX + 2] = { 0 };

    /* get psu blackbox parsing type by psu model */
    block_size = wb_pmbus_read_block_data(client, 0, PMBUS_MFR_MODEL, block_data);
    if (block_size < 0) {
        CSU550_DEBUG_ERROR("%d-%04x: Failed to get psu model, ret: %d\n",
            client->adapter->nr, client->addr, block_size);
        return -EIO;
    }

    memset(csu550_info->psu_model, 0, sizeof(csu550_info->psu_model));
    snprintf(csu550_info->psu_model, sizeof(csu550_info->psu_model), "%s", block_data);
    match_flag = 0;
    for (i = 0; i < ARRAY_SIZE(psu_infos); i++) {
        if (strncmp(block_data, psu_infos[i].psu_model, strlen(psu_infos[i].psu_model)) == 0) {
            CSU550_DEBUG_DMESG("Match psu model: %s, blackbox_type: %d\n", block_data, psu_infos[i].blackbox_type);
            match_flag = 1;
            csu550_info->blackbox_type = psu_infos[i].blackbox_type;
            csu550_info->blackbox_clear_type = psu_infos[i].blackbox_clear_type;
            csu550_info->blackbox_record_num = psu_infos[i].blackbox_record_num;
            if (csu550_info->blackbox_record_num <= 0) {
                csu550_info->blackbox_record_num = BLACKBOX_MFR_PAGE_NUM;
            }
            break;
        }
    }
    if (match_flag == 0) {
        CSU550_DEBUG_ERROR("%d-%04x: Unsupport PSU model: %s\n",
            client->adapter->nr, client->addr, block_data);
        return -EOPNOTSUPP;
    }

    if (csu550_info->blackbox_type == BLACKBOX_DC_BR238) {
        csu550_info->blackbox_reg = BLACKBOX_START_REG_DC;
    } else {
        csu550_info->blackbox_reg = BLACKBOX_START_REG_E4;
    }

    CSU550_DEBUG_DMESG("csu550_info_init success, psu_model: %s, blackbox_type: %d, blackbox_reg: 0x%02x, blackbox_record_num: %d\n",
        csu550_info->psu_model, csu550_info->blackbox_type, csu550_info->blackbox_reg, csu550_info->blackbox_record_num);
    return 0;
}

static int buf_to_data(int data_type, u8 *data_buf, int data_len, u64 *val)
{
    int i;
    u64 val_tmp;

    if ((data_len < 0) || (data_len > sizeof(val_tmp))) {
        CSU550_DEBUG_ERROR("Invalid date_len: %d, can't conversion\n", data_len);
        return -1;
    }

    val_tmp = 0;
    if (data_type == LE_DATA) {
        for (i = 0; i < data_len; i++) {
            val_tmp |= (data_buf[i] << (i * 8));
        }
    } else {
        for (i = 0; i < data_len; i++) {
            val_tmp |= data_buf[i] << (8 * (data_len -i - 1));
        }

    }

    *val = val_tmp;
    return 0;
}
static int get_pmbus_info(struct pmbus_data *data, struct i2c_client *client, pmbus_info_t *info, char *buf, int buf_len)
{
    int ret, tmp_value, size, i, offset = 0;
    s64 div_result, div_mod;
    char block_data[I2C_SMBUS_BLOCK_MAX + 2] = { 0 };
    u64 val;

    memset(buf, 0, buf_len);
    switch (info->width) {
    case BLOCK_DATA:
        tmp_value = wb_pmbus_read_block_data(client, 0, info->pmbus_reg, block_data);
        break;
    case BYTE_DATA:
        tmp_value = wb_pmbus_read_byte_data(client, 0, info->pmbus_reg);
        break;
    case WORD_DATA:
        tmp_value = wb_pmbus_read_word_data(client, 0, 0xff, info->pmbus_reg);
        break;
    default:
        if ((info->width <= 0) || (info->width > I2C_SMBUS_BLOCK_MAX)) {
            CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, Invalid width: %d\n",
                client->adapter->nr, client->addr, info->pmbus_name, info->pmbus_reg, info->width);
            return snprintf(buf, buf_len, "%-15s (0x%X) : Invalid width: %d\n", info->pmbus_name, info->pmbus_reg, info->width);
        }
        tmp_value = wb_pmbus_read_i2c_block_data(client, 0, info->pmbus_reg, info->width, block_data);
        break;
    }
    if (tmp_value < 0) {
        CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, read failed, ret: %d\n",
            client->adapter->nr, client->addr, info->pmbus_name, info->pmbus_reg, tmp_value);
        return snprintf(buf, buf_len, "%-15s (0x%X) : %s\n", info->pmbus_name, info->pmbus_reg, CSU550_READ_FAIL);
    }

    CSU550_DEBUG_DMESG("%d-%04x: %s reg addr: 0x%02x, read success, ret: %d\n",
        client->adapter->nr, client->addr, info->pmbus_name, info->pmbus_reg, tmp_value);

    switch (info->data_type) {
    case RAWDATA_BYTE:
        size = snprintf(buf, buf_len, "%-15s (0x%X) : 0x%02x\n", info->pmbus_name, info->pmbus_reg, tmp_value);
        break;
    case RAWDATA_WORD:
        size = snprintf(buf, buf_len, "%-15s (0x%X) : 0x%04x\n", info->pmbus_name, info->pmbus_reg, tmp_value);
        break;
    case RAWDATA_BUF:
        offset += snprintf(buf + offset, buf_len - offset, "%-15s (0x%X) : ", info->pmbus_name, info->pmbus_reg);
        for (i = 0; i < info->width; i++) {
            offset += snprintf(buf + offset, buf_len - offset, "0x%02x ", block_data[i]);
        }
        buf[offset] = '\n';
        size = strlen(buf);
        break;
    case STRING_DATA:
        trim_trailing_spaces(block_data);
        size = snprintf(buf, buf_len, "%-15s (0x%X) : %s\n", info->pmbus_name, info->pmbus_reg, block_data);
        break;
    case LE_DATA:
    case BE_DATA:
        ret = buf_to_data(info->data_type, block_data, info->width, &val);
        if (ret < 0) {
            size = snprintf(buf, buf_len, "%-15s (0x%X) : Invalid data width: %d, can't converted to value\n",
                info->pmbus_name, info->pmbus_reg, info->width);
        } else {
            size = snprintf(buf, buf_len, "%-15s (0x%X) : %llu %s\n", info->pmbus_name, info->pmbus_reg, val, info->unit);
        }
        break;
    case LINEAR11:
    case LINEAR16:
        reg2data_linear(data, tmp_value, info->data_type, &div_result, &div_mod);
        size = snprintf(buf, buf_len, "%-15s (0x%X) : %lld.%02lld %s\n",
            info->pmbus_name, info->pmbus_reg, div_result, div_mod, info->unit);
        break;
    default:
        CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, unsupport width: %d\n",
            client->adapter->nr, client->addr, info->pmbus_name, info->pmbus_reg, info->width);
        size = snprintf(buf, buf_len, "%-15s (0x%X) : Unsupport pmbus data type: %d\n",
            info->pmbus_name, info->pmbus_reg, info->data_type);
        break;
    }

    return size;
}

static int get_psu_blackbox_type1_info(struct pmbus_data *data, struct i2c_client *client,
               csu550_info_t *csu550_info, char *buf, int buf_len)
{
    int ret, reg, reg_val;
    int index, offset = 0;
    u8 block_buffer[MAX_RW_LEN];
    blackbox_t blackbox;
    u32 time_total, ac_power_cycle, pson_power_cycle;
    s64 div_result, div_mod;

    if (csu550_info->blackbox_type == BLACKBOX_DC_BR238) {
        reg = BLACKBOX_START_REG_DC;
    } else {
        reg = BLACKBOX_START_REG_E4;
    }

    memset(block_buffer, 0, sizeof(block_buffer));
    ret = csu550_transfer_read(client, block_buffer, reg, BLACKBOX_BLOCK_READ_SIZE);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to get %s blackbox info, reg: 0x%02x, ret: %d\n",
            csu550_info->psu_model, reg, ret);
        return ret;
    }

    memset(&blackbox, 0, sizeof(blackbox));
    memcpy(&blackbox, block_buffer, BLACKBOX_BLOCK_READ_SIZE);

    time_total = blackbox.present_total_psu_on_time[2] << 16|
                 blackbox.present_total_psu_on_time[1] << 8 |
                 blackbox.present_total_psu_on_time[0];

    ac_power_cycle = blackbox.present_number_of_ac_power_cycles[1] << 8 |
                     blackbox.present_number_of_ac_power_cycles[0];

    pson_power_cycle = blackbox.present_number_of_pson_power_cycles[1] << 8 |
                       blackbox.present_number_of_pson_power_cycles[0];

    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: PSU (Bus:%d Addr:0x%x)\n", "Blackbox Information",
        client->adapter->nr, client->addr);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %s\n", "PSU Model", csu550_info->psu_model);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %s\n", "--------------------", "-----------------------");
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d Bytes\n", "Read-Length", blackbox.len);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d Min\n", "PSU_ON_TOTAL_TIME", time_total);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d\n", "PSU_AC_POWER_CYCLE", ac_power_cycle);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d\n", "PSU_PSON_POWER_CYCLE", pson_power_cycle);

    for (index = 0; index < BLACKBOX_EVENT_SIZE; index++) {
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %s\n", "--------------------", "-----------------------");
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: [%d]\n\n", "Event", (index + 1));
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d Min\n", "POWER_ON_TIME",
               (blackbox.event[index].power_supply_total_power_on_time[2] << 16) |
               (blackbox.event[index].power_supply_total_power_on_time[1] << 8) |
               (blackbox.event[index].power_supply_total_power_on_time[0]));
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d\n", "REAL_TIME_CLOCK",
               (blackbox.event[index].real_time_clock_data_from_system[3] << 24) |
               (blackbox.event[index].real_time_clock_data_from_system[2] << 16) |
               (blackbox.event[index].real_time_clock_data_from_system[1] << 8) |
               (blackbox.event[index].real_time_clock_data_from_system[0]));
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d\n", "AC_POWER_CYCLE_TIMES",
               (blackbox.event[index].number_of_ac_power_cycles[1] << 8) |
               (blackbox.event[index].number_of_ac_power_cycles[0]));
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %d\n", "PSON_POWER_CYCLE_TIMES",
               (blackbox.event[index].number_of_pson_cycles[1] << 8) |
               (blackbox.event[index].number_of_pson_cycles[0]));
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x79) : 0x%04x\n", "STATUS_WORD",
               (blackbox.event[index].status_word[1] << 8) | blackbox.event[index].status_word[0]);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x7B) : 0x%02x\n", "STATUS_IOUT", blackbox.event[index].status_iout);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x7C) : 0x%02x\n", "STATUS_INPUT", blackbox.event[index].status_input);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x7D) : 0x%02x\n", "STATUS_TEMP", blackbox.event[index].status_temperature);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x81) : 0x%02x\n", "STATUS_FAN", blackbox.event[index].status_fan_1_2);

        reg_val = (blackbox.event[index].read_vin[1] << 8) | blackbox.event[index].read_vin[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x88) : %lld.%02lld V\n", "IN_VOLT", div_result, div_mod);

        reg_val = (blackbox.event[index].read_iin[1] << 8) | blackbox.event[index].read_iin[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x89) : %lld.%02lld A\n", "IN_CURR", div_result, div_mod);

        reg_val = (blackbox.event[index].read_vout[1] << 8) | blackbox.event[index].read_vout[0];
        reg2data_linear(data, reg_val, LINEAR16, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x8B) : %lld.%02lld V\n", "OUT_VOLT", div_result, div_mod);

        reg_val = (blackbox.event[index].read_iout[1] << 8) | blackbox.event[index].read_iout[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x8C) : %lld.%02lld A\n", "OUT_CURR", div_result, div_mod);

        reg_val = (blackbox.event[index].read_temperature_1[1] << 8) | blackbox.event[index].read_temperature_1[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x8D) : %lld.%02lld C\n", "TEMP1", div_result, div_mod);

        reg_val = (blackbox.event[index].read_temperature_2[1] << 8) | blackbox.event[index].read_temperature_2[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x8E) : %lld.%02lld C\n", "TEMP2", div_result, div_mod);

        reg_val = (blackbox.event[index].read_fan_speed_1[1] << 8) | blackbox.event[index].read_fan_speed_1[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x90) : %lld.%02lld RPM\n", "FAN_SPEED", div_result, div_mod);

        reg_val = (blackbox.event[index].read_pin[1] << 8) | blackbox.event[index].read_pin[0];
        reg2data_linear(data, reg_val, LINEAR11, &div_result, &div_mod);
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x97) : %lld.%02lld W\n\n", "IN_POWER", div_result, div_mod);
    }
    return strlen(buf);
}

static int get_psu_blackbox_type2_info(struct pmbus_data *data, struct i2c_client *client,
               csu550_info_t *csu550_info, char *buf, int buf_len, pmbus_info_t *blackbox_array, int a_size)
{
    int ret, tmp_value;
    int i, mfr_page, offset = 0;
    char tmp_buf[MAX_RW_LEN];

    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: PSU (Bus:%d Addr:0x%x)\n", "Blackbox Information",
        client->adapter->nr, client->addr);
    offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %s\n", "PSU Model", csu550_info->psu_model);

    for (mfr_page = 0; mfr_page < csu550_info->blackbox_record_num; mfr_page++) {
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: %s\n", "--------------------", "-----------------------");
        offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-23s: [%d]\n\n", "Event", (mfr_page + 1));
        /* set MFR_PAGE */
        tmp_value = wb_pmbus_write_byte_data(client, 0, BLACKBOX_CONFIG_REG, mfr_page);
        if (tmp_value < 0) {
            CSU550_DEBUG_ERROR("%d-%04x: Failed to set MFR_PAGE, set value: 0x%02x, ret: %d\n",
                client->adapter->nr, client->addr, mfr_page, tmp_value);
            offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "Failed to set MFR_PAGE register, set value: 0x%02x\n", mfr_page);
            continue;
        }
        /* read blackbox info */
        for (i = 0; i < a_size; i++) {
            ret = get_pmbus_info(data, client, &blackbox_array[i], tmp_buf, sizeof(tmp_buf));
            if (ret < 0) {
                CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, read failed, ret: %d\n",
                    client->adapter->nr, client->addr, blackbox_array[i].pmbus_name, blackbox_array[i].pmbus_reg, ret);
                offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%-15s (0x%X) : %s\n",
                    blackbox_array[i].pmbus_name, blackbox_array[i].pmbus_reg, CSU550_READ_FAIL);
                continue;
            }
            offset += snprintf(buf + offset, offset >= buf_len - 1 ? 0 : buf_len - offset, "%s", tmp_buf);
        }
    }

    /* Restore to real time data page */
    tmp_value = wb_pmbus_write_byte_data(client, 0, BLACKBOX_CONFIG_REG, BLACKBOX_REAL_TIME_DATA_PAGE);
    if (tmp_value < 0) {
        dev_err(&client->dev, "Failed to set MFR_PAGE(0x%02X) to real time data page, set value: 0x%02x, ret: %d\n",
            BLACKBOX_CONFIG_REG, BLACKBOX_REAL_TIME_DATA_PAGE, tmp_value);
    }

    return strlen(buf);
}

static int get_psu_blackbox_rawdata(struct pmbus_data *data, struct i2c_client *client,
               csu550_info_t *csu550_info, char *buf, int buf_len)
{
    int ret, i, offset = 0;
    u8 block_buffer[MAX_RW_LEN];

    CSU550_DEBUG_DMESG("get blackbox info, type: %d, blackbox_reg: 0x%x\n",
        csu550_info->blackbox_type, csu550_info->blackbox_reg);
    memset(block_buffer, 0, sizeof(block_buffer));

    switch(csu550_info->blackbox_type) {
    case BLACKBOX_DC_BR238:
    case BLACKBOX_E4_BR238:
        ret = csu550_transfer_read(client, block_buffer, csu550_info->blackbox_reg, BLACKBOX_BLOCK_READ_SIZE);
        if (ret < 0) {
            CSU550_DEBUG_ERROR("Failed to get %s blackbox info, reg: 0x%02x, ret: %d\n",
                csu550_info->psu_model, csu550_info->blackbox_reg, ret);
            return ret;
        }
        for (i = 0; i < BLACKBOX_BLOCK_READ_SIZE; i++) {
            offset += snprintf(buf + offset, buf_len - offset, "0x%02x ", block_buffer[i]);
        }
        buf[offset] = '\n';
        break;
    case BLACKBOX_E4_RW:
        ret = get_psu_blackbox_type2_info(data, client, csu550_info, buf, buf_len, blackbox_raw_infos, ARRAY_SIZE(blackbox_raw_infos));
        break;
    default:
        ret = -EOPNOTSUPP;
        CSU550_DEBUG_ERROR("Unsupport blackbox type: %d\n", csu550_info->blackbox_type);
        return ret;
    }
    return ret;
}

static int get_psu_blackbox_info(struct pmbus_data *data, struct i2c_client *client, csu550_info_t *csu550_info, char *buf, int buf_len)
{
    int ret;

    CSU550_DEBUG_DMESG("get %s blackbox info, type: %d\n", csu550_info->psu_model, csu550_info->blackbox_type);
    switch(csu550_info->blackbox_type) {
    case BLACKBOX_DC_BR238:
    case BLACKBOX_E4_BR238:
        ret = get_psu_blackbox_type1_info(data, client, csu550_info, buf, buf_len);
        break;
    case BLACKBOX_E4_RW:
        ret = get_psu_blackbox_type2_info(data, client, csu550_info, buf, buf_len, blackbox_infos, ARRAY_SIZE(blackbox_infos));
        break;
    default:
        ret = -EOPNOTSUPP;
        CSU550_DEBUG_ERROR("unsupport get blackbox way, type: %d\n", csu550_info->blackbox_type);
        break;
    }
    return ret;
}

static ssize_t show_csu550_pmbus_info(struct device *dev, struct device_attribute *da, char *buf)
{
    int i, offset = 0;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    ssize_t buf_len;
    int ret;
    char tmp_buf[MAX_RW_LEN];

    memset(buf, 0, PAGE_SIZE);
    data = i2c_get_clientdata(client);
    mutex_lock(&data->update_lock);

    offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "%-23s: PSU (Bus:%d Addr:0x%x)\n", "PSU Information",
        client->adapter->nr, client->addr);
    offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "%-23s: %s\n", "--------------------", "-----------------------");
    for (i = 0; i < ARRAY_SIZE(pmbus_infos); i++) {
        ret = get_pmbus_info(data, client, &pmbus_infos[i], tmp_buf, sizeof(tmp_buf));
        if (ret < 0) {
            CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, read failed, ret: %d\n",
                client->adapter->nr, client->addr, pmbus_infos[i].pmbus_name, pmbus_infos[i].pmbus_reg, ret);
            offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "%-15s (0x%X) : %s\n",
                pmbus_infos[i].pmbus_name, pmbus_infos[i].pmbus_reg, CSU550_READ_FAIL);
            continue;
        }
        offset += snprintf(buf + offset, offset >= PAGE_SIZE - 1 ? 0 : PAGE_SIZE - offset, "%s", tmp_buf);
    }

    buf_len = strlen(buf);
    CSU550_DEBUG_DMESG("get blackbox pmbus_info success, buf_len: %ld\n", buf_len);
    mutex_unlock(&data->update_lock);
    return buf_len;
}

static ssize_t show_csu550_block_data(struct device *dev, struct device_attribute *da, char *buf)
{
    int ret;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    char block_data[I2C_SMBUS_BLOCK_MAX + 2] = { 0 };
    struct sensor_device_attribute *attr;

    data = i2c_get_clientdata(client);
    attr = to_sensor_dev_attr(da);
    mutex_lock(&data->update_lock);
    ret = wb_pmbus_read_block_data(client, 0, attr->index, block_data);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("%d-%04x: read csu550 block data failed, reg offset: 0x%02x, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    CSU550_DEBUG_DMESG("%d-%04x: read csu550 block data success, reg offset: 0x%02x, ret: %d, value: %s\n",
        client->adapter->nr, client->addr, attr->index, ret, block_data);

    mutex_unlock(&data->update_lock);
    return snprintf(buf, PAGE_SIZE, "%s\n", block_data);
}

static ssize_t show_csu550_byte_data(struct device *dev, struct device_attribute *da, char *buf)
{
    int ret;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    struct sensor_device_attribute *attr;

    data = i2c_get_clientdata(client);
    attr = to_sensor_dev_attr(da);
    mutex_lock(&data->update_lock);
    ret = wb_pmbus_read_byte_data(client, 0, attr->index);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("%d-%04x: read csu550 byte data failed, reg offset: 0x%02x, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    CSU550_DEBUG_DMESG("%d-%04x: read csu550 byte data success, reg offset: 0x%02x, read val: 0x%02x\n",
        client->adapter->nr, client->addr, attr->index, ret);

    mutex_unlock(&data->update_lock);
    return snprintf(buf, PAGE_SIZE, "0x%02x\n", ret);
}

static ssize_t show_csu550_word_data(struct device *dev, struct device_attribute *da, char *buf)
{
    int ret;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    struct sensor_device_attribute *attr;

    data = i2c_get_clientdata(client);
    attr = to_sensor_dev_attr(da);
    mutex_lock(&data->update_lock);
    ret = wb_pmbus_read_word_data(client, 0, 0xff, attr->index);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("%d-%04x: read csu550 word data failed, reg offset: 0x%02x, ret: %d\n",
            client->adapter->nr, client->addr, attr->index, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    CSU550_DEBUG_DMESG("%d-%04x: read csu550 word data success, reg offset: 0x%02x, read val: 0x%04x\n",
        client->adapter->nr, client->addr, attr->index, ret);

    mutex_unlock(&data->update_lock);
    return snprintf(buf, PAGE_SIZE, "0x%04x\n", ret);
}

static ssize_t psu_reset_store(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    int ret, val;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    struct sensor_device_attribute *attr;

    data = i2c_get_clientdata(client);
    attr = to_sensor_dev_attr(da);

    ret = kstrtoint(buf, 0, &val);
    if (ret) {
        dev_err(&client->dev,"Invalid val: %s, kstrtoint failed, ret: %d\n", buf, ret);
        return ret;
    }

    if (val != 1) {
        dev_err(&client->dev,"Invalid val: %d, can't do psu reset operation\n", val);
        return -EINVAL;
    }

    mutex_lock(&data->update_lock);
    ret = wb_pmbus_write_byte_data(client, 0, PMBUS_ON_OFF_CONFIG, PSU_RESET_ON_OFF_CONFIG_VAL);
    if (ret < 0) {
        dev_err(&client->dev,"Failed to write ON_OFF_CONFIG register(0x%02X), write value: 0x%02x, ret: %d\n",
            PMBUS_ON_OFF_CONFIG, PSU_RESET_ON_OFF_CONFIG_VAL, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    ret = wb_pmbus_write_byte_data(client, 0, PMBUS_OPERATION, PSU_RESET_OPERATION_VAL);
    if (ret < 0) {
        dev_err(&client->dev,"Failed to write OPERATION register(0x%02X), write value: 0x%02x, ret: %d\n",
            PMBUS_OPERATION, PSU_RESET_OPERATION_VAL, ret);
        mutex_unlock(&data->update_lock);
        return ret;
    }

    CSU550_DEBUG_DMESG("%d-%04x: psu reset success\n", client->adapter->nr, client->addr);
    mutex_unlock(&data->update_lock);
    return count;
}

static int clear_psu_blackbox_e0(struct i2c_client *client)
{
    int ret;

    ret = wb_pmbus_write_byte(client, 0, BLACKBOX_CLEAR_REG_E0);
    if (ret < 0) {
        CSU550_DEBUG_DMESG("Failed to send 0xE0 to clear blackbox info, ret: %d\n", ret);
        return -EIO;
    }
    CSU550_DEBUG_DMESG("Send 0xE0 to clear blackbox info successfully\n");
    return 0;
}

static int clear_psu_blackbox_e7(struct i2c_client *client, int clear_type)
{
    int ret;
    u16 wr_val;

    if (clear_type == BLACKBOX_CLEAR_E7_TYPE1) {
        wr_val = BLACKBOX_CLEAR_REG_E7_VAL1;
    } else {
        wr_val = BLACKBOX_CLEAR_REG_E7_VAL2;
    }

    ret = wb_pmbus_write_word_data(client, 0, BLACKBOX_CLEAR_REG_E7, wr_val);
    if (ret < 0) {
        CSU550_DEBUG_DMESG("Failed to write 0xE7 register to clear blackbox info, write value: 0x%04X, ret: %d\n",
            wr_val, ret);
        return -EIO;
    }
    CSU550_DEBUG_DMESG("Write 0xE7 register to clear blackbox info successfully, write value: 0x%04X\n",
        wr_val);
    return 0;
}

static int clear_psu_blackbox(struct i2c_client *client, csu550_info_t *csu550_info)
{
    int ret;

    CSU550_DEBUG_DMESG("Clear %s blackbox info, type: %d\n",
        csu550_info->psu_model, csu550_info->blackbox_clear_type);
    switch(csu550_info->blackbox_clear_type) {
    case BLACKBOX_CLEAR_E0:
        ret = clear_psu_blackbox_e0(client);
        break;
    case BLACKBOX_CLEAR_E7_TYPE1:
    case BLACKBOX_CLEAR_E7_TYPE2:
        ret = clear_psu_blackbox_e7(client, csu550_info->blackbox_clear_type);
        break;
    default:
        ret = -EOPNOTSUPP;
        CSU550_DEBUG_ERROR("Unsupport clear blackbox type: %d\n", csu550_info->blackbox_clear_type);
        break;
    }
    return ret;
}

static ssize_t clear_blackbox_store(struct device *dev, struct device_attribute *da, const char *buf, size_t count)
{
    int ret, val;
    struct i2c_client *client = to_i2c_client(dev);
    struct pmbus_data *data;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    ret = kstrtoint(buf, 0, &val);
    if (ret) {
        dev_err(&client->dev,"Invalid val: %s, kstrtoint failed, ret: %d\n", buf, ret);
        return ret;
    }

    if (val != 1) {
        dev_err(&client->dev,"Invalid val: %d, can't clear psu reset operation\n", val);
        return -EINVAL;
    }

    data = i2c_get_clientdata(client);
    mutex_lock(&data->update_lock);

    ret = csu550_info_init(client, csu550_info);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to init csu550 info, ret: %d\n", ret);
        if (ret == -EOPNOTSUPP) {
            ret = -PSU_SYSFS_RV_UNSUPPORT;
        }
        mutex_unlock(&data->update_lock);
        return ret;
    }

    ret = clear_psu_blackbox(client, csu550_info);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to clear %s blackbox information, clear type: %d, ret: %d\n",
            csu550_info->psu_model, csu550_info->blackbox_clear_type, ret);
        if (ret == -EOPNOTSUPP) {
            ret = -PSU_SYSFS_RV_UNSUPPORT;
        }
        mutex_unlock(&data->update_lock);
        return ret;
    }
    CSU550_DEBUG_DMESG("Clear %s blackbox information success, clear type: %d\n",
        csu550_info->psu_model, csu550_info->blackbox_clear_type);
    mutex_unlock(&data->update_lock);
    return count;
}

static SENSOR_DEVICE_ATTR(pmbus_info, S_IRUGO , show_csu550_pmbus_info, NULL, 0);
static SENSOR_DEVICE_ATTR(mfr_id, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_ID);
static SENSOR_DEVICE_ATTR(mfr_model, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_MODEL);
static SENSOR_DEVICE_ATTR(mfr_revision, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_REVISION);
static SENSOR_DEVICE_ATTR(mfr_location, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_LOCATION);
static SENSOR_DEVICE_ATTR(mfr_date, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_DATE);
static SENSOR_DEVICE_ATTR(mfr_serial, S_IRUGO , show_csu550_block_data, NULL, PMBUS_MFR_SERIAL);
static SENSOR_DEVICE_ATTR(status_byte, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_BYTE);
static SENSOR_DEVICE_ATTR(status_word, S_IRUGO , show_csu550_word_data, NULL, PMBUS_STATUS_WORD);
static SENSOR_DEVICE_ATTR(status_vout, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_VOUT);
static SENSOR_DEVICE_ATTR(status_iout, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_IOUT);
static SENSOR_DEVICE_ATTR(status_input, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_INPUT);
static SENSOR_DEVICE_ATTR(status_temp, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_TEMPERATURE);
static SENSOR_DEVICE_ATTR(status_cml, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_CML);
static SENSOR_DEVICE_ATTR(status_fan12, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_FAN_12);
static SENSOR_DEVICE_ATTR(status_fan34, S_IRUGO , show_csu550_byte_data, NULL, PMBUS_STATUS_FAN_34);
static SENSOR_DEVICE_ATTR(psu_reset, S_IWUSR, NULL, psu_reset_store, 0);
static SENSOR_DEVICE_ATTR(clear_blackbox, S_IWUSR, NULL, clear_blackbox_store, 0);


static struct attribute *csu550_attrs[] = {
    &sensor_dev_attr_pmbus_info.dev_attr.attr,
    &sensor_dev_attr_mfr_id.dev_attr.attr,
    &sensor_dev_attr_mfr_model.dev_attr.attr,
    &sensor_dev_attr_mfr_revision.dev_attr.attr,
    &sensor_dev_attr_mfr_location.dev_attr.attr,
    &sensor_dev_attr_mfr_date.dev_attr.attr,
    &sensor_dev_attr_mfr_serial.dev_attr.attr,
    &sensor_dev_attr_status_byte.dev_attr.attr,
    &sensor_dev_attr_status_word.dev_attr.attr,
    &sensor_dev_attr_status_vout.dev_attr.attr,
    &sensor_dev_attr_status_iout.dev_attr.attr,
    &sensor_dev_attr_status_input.dev_attr.attr,
    &sensor_dev_attr_status_temp.dev_attr.attr,
    &sensor_dev_attr_status_cml.dev_attr.attr,
    &sensor_dev_attr_status_fan12.dev_attr.attr,
    &sensor_dev_attr_status_fan34.dev_attr.attr,
    &sensor_dev_attr_psu_reset.dev_attr.attr,
    &sensor_dev_attr_clear_blackbox.dev_attr.attr,
    NULL
};

static const struct attribute_group csu550_sysfs_group = {
    .attrs = csu550_attrs,
};

static void blackbox_info_show(struct i2c_client *client)
{
    int ret;
    struct pmbus_data *data;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    CSU550_DEBUG_DMESG("%d-%04x: Enter blackbox_info_show\n",
        client->adapter->nr, client->addr);

    memset(csu550_info->psu_data, 0, sizeof(csu550_info->psu_data));
    data = i2c_get_clientdata(client);
    ret = csu550_info_init(client, csu550_info);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to init csu550 info, ret: %d\n", ret);
        if (ret == -EOPNOTSUPP) {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Unsupport psu model: %s, can't get psu blackbox information\n", csu550_info->psu_model);
        } else {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Failed to get psu blackbox information, get psu model failed\n");
        }
        return;
    }

    ret = get_psu_blackbox_info(data, client, csu550_info, csu550_info->psu_data, sizeof(csu550_info->psu_data));
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to get %s blackbox information, ret: %d\n", csu550_info->psu_model, ret);
        if (ret == -EOPNOTSUPP) {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Unsupport blackbox type: %d, failed to get %s blackbox information\n", csu550_info->blackbox_type, csu550_info->psu_model);
        } else {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data), "Failed to get %s blackbox information\n", csu550_info->psu_model);
        }
    } else {
        CSU550_DEBUG_DMESG("Get %s blackbox information successfully, buf_len: %d\n",
            csu550_info->psu_model, ret);
    }
    return;
}

static void blackbox_rawdata_show(struct i2c_client *client)
{
    int ret;
    struct pmbus_data *data;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    CSU550_DEBUG_DMESG("%d-%04x: Enter blackbox_rawdata_show\n",
        client->adapter->nr, client->addr);

    memset(csu550_info->psu_data, 0, sizeof(csu550_info->psu_data));
    data = i2c_get_clientdata(client);
    ret = csu550_info_init(client, csu550_info);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to init csu550 info, ret: %d\n", ret);
        if (ret == -EOPNOTSUPP) {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Unsupport psu model: %s, can't get psu blackbox rawdata\n", csu550_info->psu_model);
        } else {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Failed to get psu blackbox rawdata, get psu model failed\n");
        }
        return;
    }

    ret = get_psu_blackbox_rawdata(data, client, csu550_info, csu550_info->psu_data, sizeof(csu550_info->psu_data));
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to get %s blackbox rawdata, ret: %d\n", csu550_info->psu_model, ret);
        if (ret == -EOPNOTSUPP) {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Unsupport blackbox type: %d, failed to get %s blackbox rawdata\n", csu550_info->blackbox_type, csu550_info->psu_model);
        } else {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data), "Failed to get %s blackbox rawdata\n", csu550_info->psu_model);
        }
    } else {
        CSU550_DEBUG_DMESG("Get %s blackbox rawdata information successfully, buf_len: %d\n",
            csu550_info->psu_model, ret);
    }
    return;
}

static void dfx_info_show(struct i2c_client *client)
{
    int i, ret, page, offset = 0;
    int psu_data_len;
    char tmp_buf[MAX_RW_LEN];
    struct pmbus_data *data;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    CSU550_DEBUG_DMESG("%d-%04x: Enter dfx_info_show\n",
        client->adapter->nr, client->addr);

    memset(csu550_info->psu_data, 0, sizeof(csu550_info->psu_data));
    data = i2c_get_clientdata(client);
    ret = csu550_info_init(client, csu550_info);
    if (ret < 0) {
        CSU550_DEBUG_ERROR("Failed to init csu550 info, ret: %d\n", ret);
        if (ret == -EOPNOTSUPP) {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Unsupport psu model: %s, can't get psu dfx info\n", csu550_info->psu_model);
        } else {
            snprintf(csu550_info->psu_data, sizeof(csu550_info->psu_data),
                "Failed to get psu dfx info, get psu model failed\n");
        }
        return;
    }
    psu_data_len = sizeof(csu550_info->psu_data);
    for (page = 0; page < csu550_info->info.pages; page++) {
        offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset, "%-23s: %d\n", "PAGE", page);
        for (i = 0; i < ARRAY_SIZE(dfx_infos); i++) {
            ret = get_pmbus_info(data, client, &dfx_infos[i], tmp_buf, sizeof(tmp_buf));
            if (ret < 0) {
                CSU550_DEBUG_ERROR("%d-%04x: %s reg addr: 0x%02x, read failed, ret: %d\n",
                    client->adapter->nr, client->addr, dfx_infos[i].pmbus_name, dfx_infos[i].pmbus_reg, ret);
                offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset, "%-15s (0x%X) : %s\n",
                    dfx_infos[i].pmbus_name, dfx_infos[i].pmbus_reg, CSU550_READ_FAIL);
                continue;
            }
            offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset, "%s", tmp_buf);
        }
    }

    offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset, "%-23s: %s\n", "--------------------", "-----------------------");
    ret = get_psu_blackbox_info(data, client, csu550_info, csu550_info->psu_data + offset, psu_data_len - offset);
    if (ret < 0) {
        if (ret == -EOPNOTSUPP) {
            offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset,
                "Unsupport blackbox type: %d, failed to get %s blackbox information\n", csu550_info->blackbox_type, csu550_info->psu_model);
        } else {
            offset += scnprintf(csu550_info->psu_data + offset, psu_data_len - offset, "Failed to get %s blackbox information\n", csu550_info->psu_model);
        }
    }

    CSU550_DEBUG_DMESG("Get %s dfx_info, buf_len: %lu\n", csu550_info->psu_model, strlen(csu550_info->psu_data));
    return;
}

static int psu_proc_data_show(struct seq_file *s, void *v)
{
    struct i2c_client *client = s->private;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    CSU550_DEBUG_DMESG("%d-%04x: Enter psu_proc_data_show\n",
        client->adapter->nr, client->addr);
    CSU550_DEBUG_DMESG("seq_file->size: %lu, seq_file->from: %lu, seq_file->count: %lu\n",
        s->size, s->from, s->count);
    CSU550_DEBUG_DMESG("seq_file->index: %lld, seq_file->read_pos: %lld\n",
        s->index, s->read_pos);
    seq_printf(s, "%s", csu550_info->psu_data);
    return 0;
}

static int psu_proc_release(struct inode *inode, struct file *file)
{
    struct i2c_client *client = PDE_DATA(inode);
    struct pmbus_data *data;
    int ret;

    CSU550_DEBUG_DMESG("%d-%04x: Enter psu_proc_release\n",
        client->adapter->nr, client->addr);

    data = i2c_get_clientdata(client);
    ret = single_release(inode, file);
    mutex_unlock(&data->update_lock);
    CSU550_DEBUG_DMESG("Leave psu_proc_release\n");
    return ret;
}

DEFINE_PROCFS_ATTRIBUTE(blackbox_rawdata_proc_ops, blackbox_rawdata_show);
DEFINE_PROCFS_ATTRIBUTE(blackbox_info_proc_ops, blackbox_info_show);
DEFINE_PROCFS_ATTRIBUTE(dfx_info_proc_ops, dfx_info_show);

static const csu500_procfs_attr_t psu_procfs_attrs[] = {
    {.name = "blackbox", .mode = S_IRUGO, .proc_op = &blackbox_rawdata_proc_ops},
    {.name = "blackbox_info", .mode = S_IRUGO, .proc_op = &blackbox_info_proc_ops},
    {.name = "dfx_info", .mode = S_IRUGO, .proc_op = &dfx_info_proc_ops},
};

/*
 * Find sensor groups and status registers on each page.
 */
static void pmbus_find_sensor_groups(struct i2c_client *client,
                     struct pmbus_driver_info *info)
{
    int page;

    /* Sensors detected on page 0 only */
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_VIN))
        info->func[0] |= PMBUS_HAVE_VIN;
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_IIN))
        info->func[0] |= PMBUS_HAVE_IIN;
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_PIN))
        info->func[0] |= PMBUS_HAVE_PIN;
    if (info->func[0]
        && wb_pmbus_check_byte_register(client, 0, PMBUS_STATUS_INPUT))
        info->func[0] |= PMBUS_HAVE_STATUS_INPUT;
    if (wb_pmbus_check_byte_register(client, 0, PMBUS_FAN_CONFIG_12) &&
        wb_pmbus_check_word_register(client, 0, PMBUS_READ_FAN_SPEED_1)) {
        info->func[0] |= PMBUS_HAVE_FAN12;
        if (wb_pmbus_check_byte_register(client, 0, PMBUS_STATUS_FAN_12))
            info->func[0] |= PMBUS_HAVE_STATUS_FAN12;
    }
    if (wb_pmbus_check_byte_register(client, 0, PMBUS_FAN_CONFIG_34) &&
        wb_pmbus_check_word_register(client, 0, PMBUS_READ_FAN_SPEED_3)) {
        info->func[0] |= PMBUS_HAVE_FAN34;
        if (wb_pmbus_check_byte_register(client, 0, PMBUS_STATUS_FAN_34))
            info->func[0] |= PMBUS_HAVE_STATUS_FAN34;
    }
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_TEMPERATURE_1))
        info->func[0] |= PMBUS_HAVE_TEMP;
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_TEMPERATURE_2))
        info->func[0] |= PMBUS_HAVE_TEMP2;
    if (wb_pmbus_check_word_register(client, 0, PMBUS_READ_TEMPERATURE_3))
        info->func[0] |= PMBUS_HAVE_TEMP3;
    if (info->func[0] & (PMBUS_HAVE_TEMP | PMBUS_HAVE_TEMP2
                 | PMBUS_HAVE_TEMP3)
        && wb_pmbus_check_byte_register(client, 0,
                     PMBUS_STATUS_TEMPERATURE))
            info->func[0] |= PMBUS_HAVE_STATUS_TEMP;

    /* Sensors detected on all pages */
    for (page = 0; page < info->pages; page++) {
        if (wb_pmbus_check_word_register(client, page, PMBUS_READ_VOUT)) {
            info->func[page] |= PMBUS_HAVE_VOUT;
            if (wb_pmbus_check_byte_register(client, page,
                              PMBUS_STATUS_VOUT))
                info->func[page] |= PMBUS_HAVE_STATUS_VOUT;
        }
        if (wb_pmbus_check_word_register(client, page, PMBUS_READ_IOUT)) {
            info->func[page] |= PMBUS_HAVE_IOUT;
            if (wb_pmbus_check_byte_register(client, 0,
                              PMBUS_STATUS_IOUT))
                info->func[page] |= PMBUS_HAVE_STATUS_IOUT;
        }
        if (wb_pmbus_check_word_register(client, page, PMBUS_READ_POUT))
            info->func[page] |= PMBUS_HAVE_POUT;
    }
}

/*
 * Identify chip parameters.
 */
static int pmbus_identify(struct i2c_client *client,
              struct pmbus_driver_info *info)
{
    int ret = 0;

    if (!info->pages) {
        /*
         * Check if the PAGE command is supported. If it is,
         * keep setting the page number until it fails or until the
         * maximum number of pages has been reached. Assume that
         * this is the number of pages supported by the chip.
         */
        if (wb_pmbus_check_byte_register(client, 0, PMBUS_PAGE)) {
            int page;

            for (page = 1; page < PMBUS_PAGES; page++) {
                if (wb_pmbus_set_page(client, page, 0xff) < 0)
                    break;
            }
            wb_pmbus_set_page(client, 0, 0xff);
            info->pages = page;
        } else {
            info->pages = 1;
        }

        wb_pmbus_clear_faults(client);
    }

    if (wb_pmbus_check_byte_register(client, 0, PMBUS_VOUT_MODE)) {
        int vout_mode, i;

        vout_mode = wb_pmbus_read_byte_data(client, 0, PMBUS_VOUT_MODE);
        if (vout_mode >= 0 && vout_mode != 0xff) {
            switch (vout_mode >> 5) {
            case 0:
                break;
            case 1:
                info->format[PSC_VOLTAGE_OUT] = vid;
                for (i = 0; i < info->pages; i++)
                    info->vrm_version[i] = vr11;
                break;
            case 2:
                info->format[PSC_VOLTAGE_OUT] = direct;
                break;
            default:
                ret = -ENODEV;
                goto abort;
            }
        }
    }

    /*
     * We should check if the COEFFICIENTS register is supported.
     * If it is, and the chip is configured for direct mode, we can read
     * the coefficients from the chip, one set per group of sensor
     * registers.
     *
     * To do this, we will need access to a chip which actually supports the
     * COEFFICIENTS command, since the command is too complex to implement
     * without testing it. Until then, abort if a chip configured for direct
     * mode was detected.
     */
    if (info->format[PSC_VOLTAGE_OUT] == direct) {
        ret = -ENODEV;
        goto abort;
    }

    /* Try to find sensor groups  */
    pmbus_find_sensor_groups(client, info);
abort:
    return ret;
}

static int create_psu_procfs(struct i2c_client *client, csu550_info_t *csu550_info)
{
    char name[PSU_ATTR_NAME_MAX_LEN];
    int attr_index, i;
    struct proc_dir_entry *psu_attr_proc_ent;

    /* create psu client procfs */
    memset(name, 0, sizeof(name));
    scnprintf(name, sizeof(name), "%d-%04x", client->adapter->nr, client->addr);
    csu550_info->psu_client_proc_ent = proc_mkdir(name, psu_root);
    if (!csu550_info->psu_client_proc_ent) {
        dev_err(&client->dev, "Failed to create psu client procfs\n");
        return -ENOMEM;
    }

    for (attr_index = 0; attr_index < ARRAY_SIZE(psu_procfs_attrs); attr_index++) {
        psu_attr_proc_ent = proc_create_data(psu_procfs_attrs[attr_index].name, psu_procfs_attrs[attr_index].mode,
            csu550_info->psu_client_proc_ent, psu_procfs_attrs[attr_index].proc_op, client);
        if (!psu_attr_proc_ent) {
            dev_err(&client->dev, "Failed to create %s procfs\n", psu_procfs_attrs[i].name);
            goto err;
        }
        CSU550_DEBUG_DMESG("%d-%04x: Create %s procfs successfully\n",
            client->adapter->nr, client->addr, psu_procfs_attrs[attr_index].name);
    }
    return 0;
err:
    for (i = attr_index - 1; i >= 0; i--) {
        remove_proc_entry(psu_procfs_attrs[i].name, csu550_info->psu_client_proc_ent);
    }
    proc_remove(csu550_info->psu_client_proc_ent);
    csu550_info->psu_client_proc_ent = NULL;
    return -ENOMEM;
}

static void remove_psu_procfs(csu550_info_t *csu550_info)
{
    int i, attr_num;

    attr_num = ARRAY_SIZE(psu_procfs_attrs);
    for (i = attr_num - 1; i >= 0; i--) {
        if (csu550_info->psu_client_proc_ent) {
            remove_proc_entry(psu_procfs_attrs[i].name, csu550_info->psu_client_proc_ent);
        }
    }
    /* remove psu client procfs */
    if (csu550_info->psu_client_proc_ent) {
        proc_remove(csu550_info->psu_client_proc_ent);
        csu550_info->psu_client_proc_ent = NULL;
    }

    return;
}

static int pmbus_probe(struct i2c_client *client)
{
    struct pmbus_driver_info *info;
    struct pmbus_platform_data *pdata = NULL;
    struct device *dev = &client->dev;
    struct pmbus_device_info *device_info;
    csu550_info_t *csu550_info;
    int ret;

    info = devm_kzalloc(dev, sizeof(struct pmbus_driver_info), GFP_KERNEL);
    if (!info)
        return -ENOMEM;

    csu550_info = devm_kzalloc(&client->dev, sizeof(csu550_info_t), GFP_KERNEL);
    if (!csu550_info) {
        dev_err(&client->dev, "devm_kzalloc csu550_info error.\n");
        return -ENOMEM;
    }

    device_info = (struct pmbus_device_info *)i2c_match_id(pmbus_id, client)->driver_data;
    if (device_info->flags & PMBUS_SKIP_STATUS_CHECK) {
        pdata = devm_kzalloc(dev, sizeof(struct pmbus_platform_data),
                     GFP_KERNEL);
        if (!pdata)
            return -ENOMEM;

        pdata->flags = PMBUS_SKIP_STATUS_CHECK;
    }

    info = &csu550_info->info;
    info->pages = device_info->pages;
    info->identify = pmbus_identify;
    dev->platform_data = pdata;

    ret = sysfs_create_group(&client->dev.kobj, &csu550_sysfs_group);
    if (ret != 0) {
        CSU550_DEBUG_ERROR("sysfs_create_group error %d\n", ret);
        return ret;
    }

    /* create procfs */
    ret = create_psu_procfs(client, csu550_info);
    if (ret) {
        sysfs_remove_group(&client->dev.kobj, &csu550_sysfs_group);
        return ret;
    }
    ret = wb_pmbus_do_probe(client, info);
    if (ret) {
        remove_psu_procfs(csu550_info);
        sysfs_remove_group(&client->dev.kobj, &csu550_sysfs_group);
    }
    return ret;
}

static const struct pmbus_device_info pmbus_info_one = {
    .pages = 1,
    .flags = 0
};

static const struct pmbus_device_info pmbus_info_zero = {
    .pages = 0,
    .flags = 0
};

static const struct pmbus_device_info pmbus_info_one_skip = {
    .pages = 1,
    .flags = PMBUS_SKIP_STATUS_CHECK
};

static const struct pmbus_device_info pmbus_info_zero_skip = {
    .pages = 0,
    .flags = PMBUS_SKIP_STATUS_CHECK
};

static int pmbus_remove(struct i2c_client *client)
{
    int ret;
    csu550_info_t *csu550_info = to_csu550_data(wb_pmbus_get_driver_info(client));

    remove_psu_procfs(csu550_info);
    sysfs_remove_group(&client->dev.kobj, &csu550_sysfs_group);
    ret = wb_pmbus_do_remove(client);
    if (ret != 0){
        CSU550_DEBUG_ERROR("fail remove pmbus %d\n", ret);
    }
    return ret;
}

/*
 * Use driver_data to set the number of pages supported by the chip.
 */
static const struct i2c_device_id pmbus_id[] = {
    {"wb_csu550", (kernel_ulong_t)&pmbus_info_zero_skip},
    {"wb_csu800", (kernel_ulong_t)&pmbus_info_one_skip},
    {"wb_fsp1200", (kernel_ulong_t)&pmbus_info_one_skip},
    {"wb_dps550", (kernel_ulong_t)&pmbus_info_one_skip},
    {}
};

MODULE_DEVICE_TABLE(i2c, pmbus_id);

/* This is the driver that will be inserted */
static struct i2c_driver pmbus_driver = {
    .driver = {
           .name = "wb_pmbus",
           },
    .probe_new = pmbus_probe,
    .remove = pmbus_remove,
    .id_table = pmbus_id,
};

static int __init pmbus_driver_init(void)
{
    int ret;

    psu_root = proc_mkdir("psu", NULL);
    if (!psu_root) {
        printk(KERN_ERR "Failed to create psu procfs\n");
        return -ENOMEM;
    }

    ret = i2c_add_driver(&pmbus_driver);
    if (ret) {
        printk(KERN_ERR "Failed to add csu550 driver\n");
        proc_remove(psu_root);
        psu_root = NULL;
    }

    return ret;
}
module_init(pmbus_driver_init);

static void __exit pmbus_driver_exit(void)
{
    i2c_del_driver(&pmbus_driver);

    if (psu_root) {
        proc_remove(psu_root);
        psu_root = NULL;
    }

}
module_exit(pmbus_driver_exit);

MODULE_AUTHOR("support");
MODULE_DESCRIPTION("Generic PMBus driver");
MODULE_LICENSE("GPL");
