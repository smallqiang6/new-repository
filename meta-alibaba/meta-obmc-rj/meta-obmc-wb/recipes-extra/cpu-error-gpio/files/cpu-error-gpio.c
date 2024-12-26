/**
 * Copyright(C) 2018 Ruijie Network. All rights reserved.
 */
/*
 * cpu_error_gpio.c
 * Original Author : huangch@ruijie.com.cn, 2018-08-31
 *
 * del cpu_rror_gpio interrupt
 *
 * History
 *    v1.0    huangch@ruijie.com.cn  2018-08-31  Initial version.
 *
 */
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <dirent.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <errno.h>
#include <stdio.h>
#include <poll.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <dirent.h>
#include <syslog.h>
#include <signal.h>
#include <stdbool.h>

#include "cpu-error-gpio.h"

#define GPIO_MAX_BUFFER_SIZE 16
#define FD_MAX_COUNT 6
#define STRING_SIZE 128
#define BUFF_SIZE 5
#define MILLISECOND 1000
#define ONE_VOLT 1000
#define GPIO_MAX_NUM 5
#define VALUE_STR_SIZE 16
#define BUFFERSIZE 32
#define HEX_STR_SIZE 4
#define ADECIMAL_VALUE  16   /* hexadecimal */
#define OFFSET_VALUE    8    /* offset value */
#define TRY_TIMES       4
#define DEFAULT_CPU_STATUS_MASK 0xfe
#define DEFAULT_CPU_STATUS_ON   58      /* 0011101x */
#define FPGA_CPU_STATUS_MASK    0xfc
#define FPGA_CPU_STATUS_ON      188     /* 1011 11xx */
#define ICELAKE_CTO_CPU_STATUS_MASK 0x0f   /* CTO: Customized to Order */
#define ICELAKE_CTO_CPU_STATUS_ON   15     /* xxxx 1111 */
#define BASE_CPLD 0
#define CPU_CPLD 1
#define DEFAULT_MCE_INFO_PATH "/var/log/mce/info.log"
#define BACKUP_MCE_ERROR_INFO_PATH "/var/log/mce/mce_iio_backup.log"
#define DEFAULT_PECI_INFO_PATH "/var/log/mce/peci_info.log"
#define BACKUP_MCE_INFO_PATH "/tmp/mce/info.log"
#define BACKUP_PECI_INFO_PATH "/tmp/mce/peci_info.log"
#define DEFAULT_MCE_ERROR_INFO_PATH "/var/log/mce/mce_iio.log"
#define CPU_MCE_PATH          "/var/log/fw/cpu_mcerr"
#define CPU_IERR_PATH         "/var/log/fw/cpu_ierr"
#define CPU_AER0_PATH         "/var/log/fw/cpu_aer_err0"
#define CPU_AER1_PATH         "/var/log/fw/cpu_aer_err1"
#define CPU_AER2_PATH         "/var/log/fw/cpu_aer_err2"
#define CPU_MSMI_PATH         "/var/log/fw/cpu_msmierr"
#define PRODUCT_NAME_PATH     "/etc/device/productname"
#define FULLPRODUCT_NAME_PATH "/etc/device/fullproductname"
#define COLLECT_DONE          "\nDONE : DONE\n"
#define COLLECT_STOP          "\nSTOP : STOP\n"
#define STOP_STR              "STOP"
#define NO_STOP               0
#define STOP_NUM_BUFF         4

#define PRINTF_BINARY_PATTERN_INT8 "%c%c%c%c%c%c%c%c"
#define PRINTF_BYTE_TO_BINARY_INT8(i)    \
    (((i) & 0x80) ? '1' : '0'), \
    (((i) & 0x40) ? '1' : '0'), \
    (((i) & 0x20) ? '1' : '0'), \
    (((i) & 0x10) ? '1' : '0'), \
    (((i) & 0x08) ? '1' : '0'), \
    (((i) & 0x04) ? '1' : '0'), \
    (((i) & 0x02) ? '1' : '0'), \
    (((i) & 0x01) ? '1' : '0')
/* 
 * 1. D1527(as23-32, as23-48, as23-128)
 * 2. D1527:CPU 4 core
 * 3. D1533(as14-40d, as14-128)
 * 4. D1533:CPU 6 core
 * 5. D1734(AS14-24D8Q)
 * 6. D1734:CPU 8 core
 */
#define CPU_D1527_CORE_NUM        4
#define CPU_D1533_CORE_NUM         6
#define CPU_D1734_CORE_NUM         8
#define SIX_CORE_PRODUCT_NUM       6
#define EIGHT_CORE_PRODUCT_NUM     6
#define PRODUCT_NAME_SIZE          32

#define RD_PCICFG_LOCAL     0
#define RD_ENDPOINT_lPCI     1
const char sex_core_product_list[SIX_CORE_PRODUCT_NUM][PRODUCT_NAME_SIZE] = {"AS14-40D", "AS14-128H", "AS24-128D", "AC51-48C2G",
    "AS24-128D-2-RJ"};
const char eight_core_product_list[EIGHT_CORE_PRODUCT_NUM][PRODUCT_NAME_SIZE] = {"AS14-24D8Q", "AS25-128Q", "AS51-24D", "AS15-40Q"};
static uint8_t cc_intervals_d17[][2] = {{0x40, 0x40}, {0x90, 0x94}, {0x83, 0x8f}, {0x98, 0x98}, {0x9b, 0x9c}};
static int cc_intervals_num_d17 = TABLE_SIZE(cc_intervals_d17, cc_intervals_d17[0]);

/* bank = 19, collection mce_iio log(parse) end */
#define BANK_FOR_COLLECTION_END    19
/* bank = 20, mains collect the specific msr register, not the bank*/
#define BANK_FOR_UNSED    20
#define THREAD0                    0
#define THREAD1                    1
#define BOOT_ING    0
#define WARM_RESET  0x01
#define RETRY_MAX   3
#define MIN         0
#define MAX         1

FILE * mce_iio_file;
static int judgePowerOff();
static void init_peci_addr_info(struct xfer_msg *msg, int peci_fd);
static void bdf_to_addr(unsigned char bus, unsigned char device, unsigned char function, uint16_t* addr_base, uint16_t* addr_bus);
int host_peci_fprintf_bank_content_D1734(int peci_fd, FILE * peci_file,  struct xfer_msg *msg, unsigned char* bus, unsigned char* device, unsigned char* func, int beg_addr, int end_addr, bool record_tag, bool record_total);
static void backup_mce_iio_file();

static char* HOST_MCE_INFO_PATH = DEFAULT_MCE_INFO_PATH;
static char* HOST_PECI_INFO_PATH = DEFAULT_PECI_INFO_PATH;
void *dump_mce_bank_D1734(struct xfer_msg *msg, int peci_fd, FILE * mce_file, int fd_num_index, int cpu_core_num);
static void i2cdump_cpld(FILE * peci_file);
static int get_value(const char *value_path, int mask);
static int ioctl_check(int peci_fd, struct xfer_msg *msg, uint8_t interval[][2], int rows, int retry_max);

sig_map_t default_fd_name[FD_MAX_COUNT] = {
    {"MCEFIFO", 0, (char *[]){"W_FILE"}},
    {"GPIOJ0",  0, (char *[]){"ERR[0]"}},
    {"GPIOJ1",  0, (char *[]){"ERR[1]"}},
    {"GPIOJ2",  0, (char *[]){"ERR[2]"}},
    {"GPIOJ3",  0, (char *[]){"IERR", "MCERR"}}
};

sig_map_t icelake_fd_name[FD_MAX_COUNT] = {
    {"MCEFIFO", 0, (char *[]){"W_FILE"}},
    {"GPIOF0",  0, (char *[]){"ERR[0]"}},
    {"GPIOF1",  0, (char *[]){"ERR[1]"}},
    {"GPIOF2",  0, (char *[]){"ERR[2]"}},
    {"GPIOF3",  0, (char *[]){"IERR", "MCERR"}},
    {"GPIOB2",  0, (char *[]){"MSMIERR"}},
};

enum pull_fds {
    MCE_FIFO = 0,
    GPIO_72,
    GPIO_73,
    GPIO_74,
    GPIO_75,
    GPIO_76
};

int g_fd_num_index;
int g_fd_num = 5; /* default: fd num */
int g_gpio_num = 4; /* default: gpio num */
char  product_name_buf[PRODUCT_NAME_SIZE];
char  fullproduct_name_buf[PRODUCT_NAME_SIZE];
const char* cpu_status_path;
const char* default_dev_name = "ALI_DEVICE";
uint8_t cpu_status_on = DEFAULT_CPU_STATUS_ON;
uint8_t cpu_status_mask = DEFAULT_CPU_STATUS_MASK;
static int g_mce_type = 0;/*0 旧cpu(D1527/D1533)流程、1:新cpu D1734流程*/
static int g_read_method = RD_PCICFG_LOCAL; /*0: RdPCIConfigLocal 1: RdEndpoint_lpci*/
sig_map_t * fd_name = default_fd_name;
cpld_addr_t cpld_list[] = {{0, 0x0d}, {1, 0x0d}};
cpld_table_t cpld_table = {cpld_list, sizeof(cpld_list)/sizeof(cpld_addr_t)};
uint32_t g_peci_error = 0;
bool g_handle_err2 = false;
const char* bios_boot_status_path;
int bios_boot_status_mask = 0;
const char* cpu_reset_status_path;
int cpu_reset_status_mask = 0;

/* ieh b30d00f03 */
static ieh_offset_table_t g_b30d00f03_to_offset_table[] = {{0x280, 0x2c0}};
static ieh_offset_table_t g_b30d12f00_to_offset_table[] = {{0x22c18, 0x22c68}};
static ieh_offset_table_t g_b30d26f00_to_offset_table[] = {{0x6, 0x0a}};

static ieh_function_table_t g_b30d00_to_func_table[] = {
    {03, g_b30d00f03_to_offset_table, TABLE_SIZE(g_b30d00f03_to_offset_table, ieh_offset_table_t)},
};
static ieh_function_table_t g_b30d12_to_func_table[] = {
    {00, g_b30d12f00_to_offset_table, TABLE_SIZE(g_b30d12f00_to_offset_table, ieh_offset_table_t)},
};
static ieh_function_table_t g_b30d26_to_func_table[] = {
    {00, g_b30d26f00_to_offset_table, TABLE_SIZE(g_b30d26f00_to_offset_table, ieh_offset_table_t)},
};

static ieh_device_table_t g_b30_to_dev_table[] = {
    {00, g_b30d00_to_func_table, TABLE_SIZE(g_b30d00_to_func_table, ieh_function_table_t)},
    {12, g_b30d12_to_func_table, TABLE_SIZE(g_b30d12_to_func_table, ieh_function_table_t)},
    {13, g_b30d12_to_func_table, TABLE_SIZE(g_b30d12_to_func_table, ieh_function_table_t)},
    {26, g_b30d26_to_func_table, TABLE_SIZE(g_b30d26_to_func_table, ieh_function_table_t)},
    {27, g_b30d26_to_func_table, TABLE_SIZE(g_b30d26_to_func_table, ieh_function_table_t)},
};

/* ieh b00d00f04 */
static ieh_offset_table_t g_b00d00f00_to_offset_table[] = {{0x190, 0x1c4}};
static ieh_offset_table_t g_b00d00f01_to_offset_table[] = {{0x260, 0x27c}};
static ieh_offset_table_t g_b00d00f02_to_offset_table[] = {{0xb0, 0xbc}, {0x208, 0x27c}, {0x2A0, 0x388}};

static ieh_function_table_t g_b00d00_to_func_table[] = {
    {00, g_b00d00f00_to_offset_table, TABLE_SIZE(g_b00d00f00_to_offset_table, ieh_offset_table_t)},
    {01, g_b00d00f01_to_offset_table, TABLE_SIZE(g_b00d00f01_to_offset_table, ieh_offset_table_t)},
    {02, g_b00d00f02_to_offset_table, TABLE_SIZE(g_b00d00f02_to_offset_table, ieh_offset_table_t)},
    {04, g_b30d00f03_to_offset_table, TABLE_SIZE(g_b30d00f03_to_offset_table, ieh_offset_table_t)},
};

static ieh_offset_table_t g_b00d01f01_to_offset_table[] = {{0x6, 0xe}, {0x4A, 0x56}, {0x104, 0x18c}};

static ieh_function_table_t g_b00d01_to_func_table[] = {
    {01, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {02, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {03, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {04, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {05, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {06, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
    {07, g_b00d01f01_to_offset_table, TABLE_SIZE(g_b00d01f01_to_offset_table, ieh_offset_table_t)},
};

static ieh_offset_table_t g_b00d02f00_to_offset_table[] = {{0x4, 0x10}, {0x1A8, 0x1B4}};
static ieh_offset_table_t g_b00d02f01_to_offset_table[] = {{0x4, 0x10}};

static ieh_function_table_t g_b00d02_to_func_table[] = {
    {00, g_b00d02f00_to_offset_table, TABLE_SIZE(g_b00d02f00_to_offset_table, ieh_offset_table_t)},
    {01, g_b00d02f01_to_offset_table, TABLE_SIZE(g_b00d02f01_to_offset_table, ieh_offset_table_t)},
    {04, g_b00d02f01_to_offset_table, TABLE_SIZE(g_b00d02f01_to_offset_table, ieh_offset_table_t)},
};

static ieh_device_table_t g_b00_to_dev_table[] = {
    {00, g_b00d00_to_func_table, TABLE_SIZE(g_b00d00_to_func_table, ieh_function_table_t)},
    {01, g_b00d01_to_func_table, TABLE_SIZE(g_b00d01_to_func_table, ieh_function_table_t)},
    {02, g_b00d02_to_func_table, TABLE_SIZE(g_b00d02_to_func_table, ieh_function_table_t)},
};

/* ieh b01d00f04 */
static ieh_function_table_t g_b01d00_to_func_table[] = {
    {00, g_b00d00f00_to_offset_table, TABLE_SIZE(g_b00d00f00_to_offset_table, ieh_offset_table_t)},
    {01, g_b00d00f01_to_offset_table, TABLE_SIZE(g_b00d00f01_to_offset_table, ieh_offset_table_t)},
    {02, g_b00d00f02_to_offset_table, TABLE_SIZE(g_b00d00f02_to_offset_table, ieh_offset_table_t)},
    {04, g_b30d00f03_to_offset_table, TABLE_SIZE(g_b30d00f03_to_offset_table, ieh_offset_table_t)},
};

static ieh_offset_table_t g_b01d02f00_to_offset_table[] = {
    {0x6, 0x0a}, {0x4a, 0x4e}, {0x104, 0x108}, {0x110, 0x114}, {0x130, 0x134}, {0x19c, 0x1a0},
    {0x1b0, 0x1b4}, {0x1b4, 0x1b8}, {0x1b8, 0x1bc}, {0x1bc, 0x1c0}, {0x208, 0x20c}, {0x620, 0x624},
    {0x624, 0x628}, {0x628, 0x62c}, {0x62c, 0x630}, {0x630, 0x634}, {0x634, 0x638}, {0x638, 0x63c},
    {0x63c, 0x640}, {0x764, 0x768}, {0xb58, 0xb5c}, {0xb6c, 0xb70}, {0xb70, 0xb74}, {0xb74, 0xb78},
};
static ieh_function_table_t g_b01d02_to_func_table[] = {
    {00, g_b01d02f00_to_offset_table, TABLE_SIZE(g_b01d02f00_to_offset_table, ieh_offset_table_t)},
};

static ieh_device_table_t g_b01_to_dev_table[] = {
    {00, g_b01d00_to_func_table, TABLE_SIZE(g_b01d00_to_func_table, ieh_function_table_t)},
    {02, g_b01d02_to_func_table, TABLE_SIZE(g_b01d02_to_func_table, ieh_function_table_t)},
    {03, g_b01d02_to_func_table, TABLE_SIZE(g_b01d02_to_func_table, ieh_function_table_t)},
    {04, g_b01d02_to_func_table, TABLE_SIZE(g_b01d02_to_func_table, ieh_function_table_t)},
    {05, g_b01d02_to_func_table, TABLE_SIZE(g_b01d02_to_func_table, ieh_function_table_t)},
};

/* ieh b02d00f04 */
static ieh_offset_table_t g_b02d00f02_to_offset_table[] = {{0x208, 0x27c}, {0x2A0, 0x388}};

static ieh_function_table_t g_b02d00_to_func_table[] = {
    {01, g_b00d00f01_to_offset_table, TABLE_SIZE(g_b00d00f01_to_offset_table, ieh_offset_table_t)},
    {02, g_b02d00f02_to_offset_table, TABLE_SIZE(g_b02d00f02_to_offset_table, ieh_offset_table_t)},
    {04, g_b30d00f03_to_offset_table, TABLE_SIZE(g_b30d00f03_to_offset_table, ieh_offset_table_t)},
};

static ieh_device_table_t g_b02_to_dev_table[] = {
    {00, g_b02d00_to_func_table, TABLE_SIZE(g_b02d00_to_func_table, ieh_function_table_t)},
};

static ieh_bus_table_t g_bus_table[] = {
    {30, g_b30_to_dev_table, TABLE_SIZE(g_b30_to_dev_table, ieh_device_table_t)},
    {00, g_b00_to_dev_table, TABLE_SIZE(g_b00_to_dev_table, ieh_device_table_t)},
    {01, g_b01_to_dev_table, TABLE_SIZE(g_b01_to_dev_table, ieh_device_table_t)},
    {02, g_b02_to_dev_table, TABLE_SIZE(g_b02_to_dev_table, ieh_device_table_t)},
};

/*
 * return:
 * 0: successed in getting device name
 * -1: failed to get device name
 */

static int get_device_name(char *path, char *name_buf)
{
    FILE* file;
    int   ret;

    file = fopen(path, "r");
    if (file == NULL) {
        syslog(LOG_DEBUG, "open product name path(%s) failed\n", path);
        snprintf(name_buf, strlen(default_dev_name), "%s", default_dev_name);
        return -1;
    }

    memset(name_buf, 0, PRODUCT_NAME_SIZE);
    if (fgets(name_buf, PRODUCT_NAME_SIZE, file) == NULL ) {
        syslog(LOG_DEBUG, "get product name(%s) failed\n", name_buf);
        fclose(file);
        snprintf(name_buf, strlen(default_dev_name), "%s", default_dev_name);
        return -1;
    }

    if (name_buf[strlen(name_buf) -1 ] == '\n') {
        name_buf[strlen(name_buf) -1 ] = '\0';
    }
    fclose(file);

    return 0;
}

/*
 * return:
 * product core num
 */

static int get_product_core_num()
{
    int ret;
    int i;

    if (strncmp(default_dev_name, product_name_buf, strlen(product_name_buf)) == 0) {
        return CPU_D1527_CORE_NUM;
    }
    for (i = 0; i < SIX_CORE_PRODUCT_NUM; i++) {
        ret = strncmp(sex_core_product_list[i], product_name_buf, strlen(product_name_buf));
        if (ret == 0) {
            return CPU_D1533_CORE_NUM;
        }
    }

    for (i = 0; i < EIGHT_CORE_PRODUCT_NUM; i++) {
        ret = strncmp(eight_core_product_list[i], product_name_buf, strlen(product_name_buf));
        if (ret == 0) {
            g_mce_type = 1;
            return CPU_D1734_CORE_NUM;
        }
    }

    return CPU_D1527_CORE_NUM;
}

pthread_t cpu_error_gpio_mce_info_pid = 0;

void host_mce_fprintf_bank_name(FILE * mce_file, unsigned char bank,unsigned char secondary_bank)
{
    switch(bank) {
        case 0:
            fprintf(mce_file, "IFU bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 1:
            fprintf(mce_file, "DCU bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 2:
            fprintf(mce_file, "DTLB bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 3:
            fprintf(mce_file, "ML2 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 4:
            fprintf(mce_file, "PCU bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 6:
            fprintf(mce_file, "IIO bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 7:
            fprintf(mce_file, "HA0 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 9:
            fprintf(mce_file, "IMC0 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 10:
            fprintf(mce_file, "IMC1 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        case 17: {
                if(secondary_bank == 0) {
                    fprintf(mce_file, "Cbo SLICE0 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
                if(secondary_bank == 1) {
                    fprintf(mce_file, "Cbo SLICE3 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
                if(secondary_bank == 2) {
                    fprintf(mce_file, "Cbo SLICE6 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
            }
            break;
        case 18: {
                if(secondary_bank == 0) {
                    fprintf(mce_file, "Cbo SLICE1 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
                if(secondary_bank == 1) {
                    fprintf(mce_file, "Cbo SLICE4 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
                if(secondary_bank == 2) {
                    fprintf(mce_file, "Cbo SLICE7 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
            }
            break;
        case 19: {
                if(secondary_bank == 0) {
                    fprintf(mce_file, "Cbo SLICE2 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
                if(secondary_bank == 1) {
                    fprintf(mce_file, "Cbo SLICE5 bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
                }
            }
            break;
        case 128:
            fprintf(mce_file, "IA32_MCG_STATUS bank=%u, secondary_bank=%u : \n", bank, secondary_bank);
            break;
        default:
            break;
    }
    return;
}

static int record_mce_ierr_value(unsigned char bank, unsigned char secondary_bank, unsigned char core, char* buffer)
{
    switch(bank) {
        case 17:
        case 18:
        case 19:
            if(secondary_bank == 0) {
                fprintf(mce_iio_file, "CORE%uMC%u%s : ", core, bank, buffer);
                break;
            }
            return 1;
        case 128:
            return 1;
        default:
            fprintf(mce_iio_file, "CORE%uMC%u%s : ", core, bank, buffer);
            break;
    }
    return 0;
}

void host_mce_fprintf_bank_content(FILE * mce_file, int j, struct xfer_msg *msg, unsigned char bank,
                                       unsigned char secondary_bank, unsigned char core)
{
    /*
     * log_collect_tag = -1, default
     * log_collect_tag = 0, bit 31-0, need record key
     * log_collect_tag = 1, bit 63:32, only collect
     */
    int i;
    int log_collect_tag;
    char buffer[STRING_SIZE];

    memset(buffer, 0, STRING_SIZE);
    log_collect_tag = -1;
    switch(j) {
        case 0:
            fprintf(mce_file, "CTL[31:0] : \n");
            break;
        case 1:
            fprintf(mce_file, "CTL[63:32] : \n");
            break;
        case 2:
            fprintf(mce_file, "STATUS[31:0] : \n");
            sprintf(buffer, "%s", "STATUS");
            log_collect_tag = 0;
            break;
        case 3:
            fprintf(mce_file, "STATUS[63:32] : \n");
            log_collect_tag = 1;
            break;
        case 4:
            fprintf(mce_file, "ADDR[31:0] : \n");
            sprintf(buffer, "%s", "ADDR");
            log_collect_tag = 0;
            break;
        case 5:
            fprintf(mce_file, "ADDR[63:32] : \n");
            log_collect_tag = 1;
            break;
        case 6:
            fprintf(mce_file, "MISC[31:0] : \n");
            sprintf(buffer, "%s", "MISC");
            log_collect_tag = 0;
            break;
        case 7:
            fprintf(mce_file, "MISC[63:32] : \n");
            log_collect_tag = 1;
            break;
        case 8:
            fprintf(mce_file, "CTL2[31:0] : \n");
            break;
        case 9:
            fprintf(mce_file, "CTL2[63:32] : \n");
            break;
        default:
            break;
    }
    if (log_collect_tag == 0) {
        record_mce_ierr_value(bank, secondary_bank, core, buffer);
    }

    for (i = 0; i <= 4 ; i++) {
        fprintf(mce_file, "rx_buf[%d] = 0x%02x ", i, msg->rx_buf[i]);
        if (log_collect_tag == 0 && i > 0 && secondary_bank == 0) {
            fprintf(mce_iio_file, "%02x ", msg->rx_buf[i]);
        }
        if (log_collect_tag == 1 && i > 0 && secondary_bank == 0){
            fprintf(mce_iio_file, "%02x ", msg->rx_buf[i]);
        }
    }
    if (log_collect_tag == 1 && secondary_bank == 0) {
        fprintf(mce_iio_file, "\n");
    }
    fprintf(mce_file, "\n\n\n");

    return;
}

void host_mce_RdPkgConfig_init(struct xfer_msg *msg)
{
    memset(msg, 0 ,sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x05;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0xa1; /* cmd */
    msg->tx_buf[1] = 0x00; /* Device Info */
    msg->tx_buf[2] = 0x80; /* index */
    msg->tx_buf[3] = 0x07;
    msg->tx_buf[4] = 0x00;
    return;
}

void host_peci_RdEndpoint_lpci_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, unsigned char data3, unsigned char data4)
{
    int i;
    memset(msg, 0, sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x0c;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0xc1; /* cmd */
    msg->tx_buf[1] = 0x00; /* Device Info */
    msg->tx_buf[2] = 0x03; /* mess type */
    msg->tx_buf[3] = 0x00; /* endpoint id */
    msg->tx_buf[4] = 0x00; /* RSVD */
    msg->tx_buf[5] = 0x00; /* RSVD */
    msg->tx_buf[6] = 0x04; /* Address type */
    msg->tx_buf[7] = 0x00; /* segment 给多个cpu使用，soc segment为 0*/
    msg->tx_buf[8] = data1; 
    msg->tx_buf[9] = data2; 
    msg->tx_buf[10] = data3;
    msg->tx_buf[11] = data4;
}

/*
 * PCI Configuration Address has three parts
 * Bus 4 Bits 20-23
 * Device 5 Bits 15-19
 * Function 3 Bits 12-14
 * Register 12 Bits 0-11
 */
void host_peci_RdPCIConfigLocal_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, unsigned char data3)
{
    memset(msg, 0 ,sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x05;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0xe1; /* cmd */
    msg->tx_buf[1] = 0x00; /* Host ID[7:1] & Retry[0] */
    msg->tx_buf[2] = data1;
    msg->tx_buf[3] = data2;
    msg->tx_buf[4] = data3;
    return;
}

void host_mce_Rdiamsr_init(struct xfer_msg *msg, unsigned char processor_id, uint16_t parameter)
{
    memset(msg, 0 ,sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x05;
    msg->rx_len = 0x09;
    msg->tx_buf[0] = 0xb1; /* cmd */
    msg->tx_buf[1] = 0x0; /* Host ID[7:1] & Retry[0] */
    msg->tx_buf[2] = processor_id;
    msg->tx_buf[3] = (unsigned char)(parameter & 0xff);
    msg->tx_buf[4] = (unsigned char)((parameter & 0xff00) >> 8);
    return;
}

void host_mce_WrPkgConfig_init(
    struct xfer_msg *msg,
    unsigned char param0,
    unsigned char param1,
    unsigned char data0,
    unsigned char data1,
    unsigned char data2,
    unsigned char data3)
{
    memset(msg, 0 ,sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x0a;
    msg->rx_len = 0x01;
    msg->tx_buf[0] = 0xa5; /* cmd */
    msg->tx_buf[1] = 0x00; /* Host ID[7:1] & Retry[0] */
    msg->tx_buf[2] = 0x80; /* index */
    msg->tx_buf[3] = param0;
    msg->tx_buf[4] = param1;
    msg->tx_buf[5] = data0;
    msg->tx_buf[6] = data1;
    msg->tx_buf[7] = data2;
    msg->tx_buf[8] = data3;
    msg->tx_buf[9] = 0x01; /* aw fcs */
    msg->fcs_en = 0x01;
    return;
}

static void read_peci_iio_reg_addr(struct xfer_msg *msg, int peci_fd)
{
    REG_INFO* ret_info;
    unsigned  char addr_fun;
    unsigned  char addr_offset;
    int ret;
    int reg;
    int i;

    if (judgePowerOff() < 0) {
        syslog(LOG_DEBUG, "read iio peci space end\n");
        /* In subsequent func, information is collected into the mce_iio_file */
        fprintf(mce_iio_file, COLLECT_STOP);
        return;
    }
    /* To convert hexadecimal into decimal for ease of calculation
     * eg, 448 be offset 0x1C0
     */
    REG_INFO reg_a000_02[] = {
            {448, "GNERRST"}, {452, "GFERRST"}, {424, "GCERRST"}, {476, "GFFERRST"},
            {488, "GFNERRST"}, {492, "GNFERRST"}, {504, "GNNERRST"}, {428, "GCFERRST"},
            {440, "GCNERRST"}, {592, "IRP0ER_250"}, {720, "IRP1ER_2D0"}, {568, "IRP0ER_238"},
            {696, "IRP1ER_2B8"}, {572, "IRP0ER_23C"}, {700, "IRP1ER_2BC"}, {600, "IRP0HD_258"},
            {604, "IRP0HD_25C"}, {608, "IRP0HD_260"}, {612, "IRP0HD_264"}, {728, "IRP1HD_2D8"},
            {732, "IRP1HD_2DC"}, {736, "IRP1HD_2E0"}, {740, "IRP1HD_2E4"}, {576, "IRP0HD_240"},
            {580, "IRP0HD_244"}, {584, "IRP0HD_248"}, {588, "IRP0HD_24C"}, {704, "IRP1HD_2C0"},
            {708, "IRP1HD_2C4"}, {712, "IRP1HD_2C8"}, {716, "IRP1HD_2CC"}, {776, "IIOFFERRST"},
            {780, "IIOFFERRHD_30C"}, {784, "IIOFFERRHD_310"}, {788, "IIOFFERRHD_314"}, {792, "IIOFFERRHD_318"},
            {796, "IIOFNERRST"}, {800, "IIONFERRST"}, {768, "IIOERRST"}, {804, "IIONFHD_324"},
            {808, "IIONFHD_328"}, {812, "IIONFHD_32C"}, {816, "IIONFHD_330"}, {820, "IIONNERRST"},
            {896, "MIERRST"}, {904, "MIFFERRST"}, {908, "MIFFHDR_38C"}, {912, "MIFFHDR_390"},
            {916, "MIFFHDR_394"}, {920, "MIFFHDR_398"}, {924, "MIFNERRST"}, {928, "MINFERRST"},
            {932, "MINFHD_3A4"}, {936, "MINFHD_3A8"}, {940, "MINFHD_3AC"}, {944, "MINFHD_3B0"},
            {948, "MINNERRST"} };
    REG_INFO reg_8000_00[] = { {332, "UNCER_1_0"}, {344, "CORER_1_0"}, {154, "DEVSTS_1_0"}, {560, "XPGLB_1_0"} };
    REG_INFO reg_9000_00[] = { {332, "UNCER_1_1"}, {344, "CORER_1_1"}, {154, "DEVSTS_1_1"}, {344, "XPGLB_1_1"} };
    REG_INFO reg_8000_01[] = { {332, "UNCER_3_0"}, {344, "CORER_3_0"}, {154, "DEVSTS_3_0"}, {344, "XPGLB_3_0"} };
    REG_INFO reg_9000_01[] = { {332, "UNCER_3_1"}, {344, "CORER_3_1"}, {154, "DEVSTS_3_1"}, {344, "XPGLB_3_1"} };
    REG_INFO reg_a000_01[] = { {332, "UNCER_3_2"}, {344, "CORER_3_2"}, {154, "DEVSTS_3_2"}, {344, "XPGLB_3_2"} };
    REG_INFO reg_b000_01[] = { {332, "UNCER_3_3"}, {344, "CORER_3_3"}, {154, "DEVSTS_3_3"}, {344, "XPGLB_3_3"} };

    IIO_PECI_MSG peci_addr_info[] = {
        {0xa000, 0x02, reg_a000_02, 57}, {0x8000, 0x00, reg_8000_00, 4},
        {0x9000, 0x00, reg_9000_00, 4}, {0x8000, 0x01, reg_8000_01, 4},
        {0x9000, 0x01, reg_9000_01, 4}, {0xa000, 0x01, reg_a000_01, 4},
        {0xb000, 0x01, reg_b000_01, 4} };

    for (ret = 0; ret < sizeof(peci_addr_info)/sizeof(peci_addr_info[0]); ret++) {
        ret_info = peci_addr_info[ret].peci_reg_info;
        for (reg = 0; reg < peci_addr_info[ret].cnt; reg++) {
            addr_offset = ((peci_addr_info[ret].addr_base + ret_info[reg].beg_addr) & 0xff); //low
            addr_fun = (((peci_addr_info[ret].addr_base + ret_info[reg].beg_addr) >> OFFSET_VALUE) & 0xff); // high
            host_peci_RdPCIConfigLocal_init(msg, addr_offset, addr_fun, peci_addr_info[ret].adrr_bus);
            /* Invalid data for evading drive detection
             * if ioctl return -1, upper layer also to read data
             * Maybe data be invalid, It has no effect on parsing
             */
            if (ioctl(peci_fd, AST_PECI_IOCXFER, msg) < 0) {
                syslog(LOG_DEBUG, "cpu_error_peci error: RdPCIConfigLocal failed\n");
            }
            fprintf(mce_iio_file, "%s : ", ret_info[reg].reg_attr);
            /* rx_buf[0] data be valid flags, useless for parsing*/
            for (i = 1; i <= 4 ; i++) {
                fprintf(mce_iio_file, "%02x ", msg->rx_buf[i]);
            }
            fprintf(mce_iio_file, "\n");
        }
    }

    fflush(mce_iio_file);
    fdatasync(fileno(mce_iio_file));
}

static bool err2_caused_by_reboot(void)
{
    struct xfer_msg *msg      = NULL;
    int fd;
    REG_INFO* ret_info;
    unsigned  char addr_fun;
    unsigned  char addr_offset;
    int ret;
    int reg;
    bool result = false;
    uint32_t reg_val;


    if ((fd = open(PECI_DEVICE, O_RDWR, S_IRWXU | S_IRWXG | S_IRWXO | S_IRUSR | S_IWUSR)) < 0) {
        syslog(LOG_DEBUG, "error: Could not open file /dev/aspeed-peci: %s\n", strerror(errno));
        return result;
    }

    msg = malloc(sizeof(struct xfer_msg));
    if (msg == NULL) {
        syslog(LOG_DEBUG, "error: malloc xfer_msg failed\n");
        close(fd);
        return result;
    }

    REG_INFO reg_a000_02[] = {
        {448, "GNERRST"}, {452, "GFERRST"}, {424, "GCERRST"}, {476, "GFFERRST"},
        {488, "GFNERRST"}, {492, "GNFERRST"}, {504, "GNNERRST"}, {428, "GCFERRST"},
        {440, "GCNERRST"}};

    IIO_PECI_MSG peci_addr_info[] = {{0xa000, 0x02, reg_a000_02, 9}};

    for (ret = 0; ret < sizeof(peci_addr_info)/sizeof(peci_addr_info[0]); ret++) {
        ret_info = peci_addr_info[ret].peci_reg_info;
        for (reg = 0; reg < peci_addr_info[ret].cnt; reg++) {
            addr_offset = ((peci_addr_info[ret].addr_base + ret_info[reg].beg_addr) & 0xff); //low
            addr_fun = (((peci_addr_info[ret].addr_base + ret_info[reg].beg_addr) >> OFFSET_VALUE) & 0xff); // high
            host_peci_RdPCIConfigLocal_init(msg, addr_offset, addr_fun, peci_addr_info[ret].adrr_bus);
            /* Invalid data for evading drive detection
             * if ioctl return -1, upper layer also to read data
             * Maybe data be invalid, It has no effect on parsing
             */
            if (ioctl(fd, AST_PECI_IOCXFER, msg) < 0) {
                syslog(LOG_DEBUG, "cpu_error_peci error: RdPCIConfigLocal failed\n");
            }
            /* bit8-11: Port 2 PCIe* logical port  != 0 && bit0-1、5-7、12-15、20、23-26 == 0*/
            reg_val = (msg->rx_buf[4] << 24 | msg->rx_buf[3] << 16
                | msg->rx_buf[2] << 8 | msg->rx_buf[1]);
            if (((reg_val & 0x00000f00) != 0) && ((reg_val & 0x0790f0e3) == 0)) {
                result = true;
                break;
            }
        }
    }

    free(msg);
    close(fd);
    return result;
}

static int ioctl_check(int peci_fd,  struct xfer_msg *msg, uint8_t interval[][2], int rows, int retry_max)
{
    int retry;
    uint8_t interval_index;
    bool exit_retry;
    int ret;

    exit_retry = false;
    for (retry = 0; retry < retry_max; retry++) {
        ret = ioctl(peci_fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            return ret;
        } else {
            for (interval_index = 0; interval_index < rows - 1; interval_index++) {
                if (msg->rx_buf[0] >= interval[interval_index][MIN] &&
                        msg->rx_buf[0] <= interval[interval_index][MAX]) {
                    exit_retry = true;
                    break;
                }
            }
            if (exit_retry) {
                break;
            }
        }
        if (retry < retry_max - 1) {
            memset(msg->rx_buf, 0, sizeof(msg->rx_buf));
        }
    }
    return 0;
}

int host_peci_fprintf_bank_content_D1734(int peci_fd, FILE * peci_file,  struct xfer_msg *msg,
        unsigned char* bus, unsigned char* device, unsigned char* func,
        int beg_addr, int end_addr, bool record_tag, bool record_total)
{
    int offset                  = 0;
    unsigned char addr_fun      = 0;
    unsigned char addr_offset   = 0;
    unsigned char addr_bus_lsb  = 0;
    unsigned char addr_bus_msb  = 0;
    int bus_loop, dev_loop, func_loop, rx_loop;//bus、device、function、rx_buf
    int devfunc_index = 0;
    int ret                     = 0;
    uint16_t adrr_bus;
    uint16_t addr_base;
    int bus_temp;

    for (bus_loop = 1; bus_loop < bus[0]; bus_loop++) {
        if (bus[bus_loop] > 15) {
            g_read_method = RD_ENDPOINT_lPCI;
            /*endpoint bus要减一，原有未知*/
            bus_temp = bus[bus_loop] - 1;
        } else {
            g_read_method = RD_PCICFG_LOCAL;
            bus_temp = bus[bus_loop];
        }
        for (dev_loop = 1; dev_loop < device[0]; dev_loop++) {
            for (func_loop = 1; func_loop < func[0]; func_loop++) {
                devfunc_index = 0;
                bdf_to_addr(bus_temp, device[dev_loop], func[func_loop], &addr_base, &adrr_bus);
                fprintf(peci_file, "Bus: %d, Device: %d, Function: %d, address: %x-%x\n", bus[bus_loop], device[dev_loop], func[func_loop], beg_addr, end_addr);
                if (record_tag) {
                    fprintf(mce_iio_file, "B%dD%dF%dAddr%x: ", bus[bus_loop], device[dev_loop], func[func_loop], beg_addr);/*bus dev fun beg_addr*/
                }
                for (offset = beg_addr; offset < end_addr ; offset = offset + 4)  {
                    if (judgePowerOff() < 0) {
                        syslog(LOG_DEBUG, "Bus: %d, Device: %d, Function: %d, address: %x-%x\n", bus[bus_loop], device[dev_loop], func[func_loop], beg_addr, end_addr);
                        syslog(LOG_DEBUG, "read peci space end\n");
                        if (record_tag) {
                            /* In subsequent func, information is collected into the mce_iio_file */
                            fprintf(mce_iio_file, COLLECT_STOP);
                        }
                        return -1;
                    }

                    addr_offset = ((addr_base + offset) & 0xff); //low
                    addr_fun = (((addr_base + offset) >> OFFSET_VALUE) & 0xff); // high
                    addr_bus_lsb = adrr_bus & 0xff;  //low
                    addr_bus_msb = (adrr_bus >> OFFSET_VALUE) & 0xff;  //high
                    if (g_read_method == RD_PCICFG_LOCAL){
                        host_peci_RdPCIConfigLocal_init(msg, addr_offset, addr_fun, addr_bus_lsb);
                    } else if (g_read_method == RD_ENDPOINT_lPCI) {
                        host_peci_RdEndpoint_lpci_init(msg, addr_offset, addr_fun, addr_bus_lsb, addr_bus_msb);
                    } else {
                        syslog(LOG_ERR, "cpu_error_peci error: g_read_method type %d err\n", g_read_method);
                        break;
                    }
                    ret = ioctl_check(peci_fd, msg, cc_intervals_d17, cc_intervals_num_d17, RETRY_MAX);
                    if (ret < 0) {
                        fprintf(peci_file, "cpu_error_peci error: RdPCIConfigLocal failed, ret = %d\n", ret);
                    }
                    if (offset == 0) {
                        fprintf(peci_file, "%02x: ", offset);
                    } else if ((offset % ADECIMAL_VALUE) == 0) {
                        fprintf(peci_file, "\n");
                        fprintf(peci_file, "%02x: ", (offset / ADECIMAL_VALUE));
                    }

                    for (rx_loop = 0; rx_loop <= 4 ; rx_loop++) {
                        if (record_tag && rx_loop > 0) {
                            fprintf(mce_iio_file, "%02x ",  msg->rx_buf[rx_loop]);
                        }
                        fprintf(peci_file, "%02x ",  msg->rx_buf[rx_loop]);
                    }
                    if (record_total) {
                        g_peci_error |= (msg->rx_buf[4] << 24 | msg->rx_buf[3] << 16
                            | msg->rx_buf[2] << 8 | msg->rx_buf[1]);
                    }
                }
                    if (record_tag) {
                        fprintf(mce_iio_file, "\n");
                    }
                    fflush(mce_iio_file);
                    fdatasync(fileno(mce_iio_file));
                    fprintf(peci_file, "\n");
                    fflush(peci_file);
                    fdatasync(fileno(peci_file));
            }
        }
    }

    return 0;
}

int host_peci_fprintf_bank_content(int peci_fd, FILE * peci_file,  struct xfer_msg *msg, uint16_t addr_base, unsigned char adrr_bus, int init_addr, int read_length, int record_tag)
{
    int offset                  = 0;
    unsigned char addr_fun      = 0;
    unsigned char addr_offset   = 0;
    int  i                      = 0;
    int ret                     = 0;

    if (record_tag == 1) {
        fprintf(mce_iio_file, "%02x : ", init_addr);
    }

    for (offset = init_addr; offset < read_length ; offset = offset + 4) {
        if (judgePowerOff() < 0) {
            syslog(LOG_DEBUG, "read peci space end\n");
            if (record_tag == 1) {
                /* In subsequent func, information is collected into the mce_iio_file */
                fprintf(mce_iio_file, COLLECT_STOP);
            }
            return -1;
        }
        addr_offset = ((addr_base + offset) & 0xff); //low
        addr_fun = (((addr_base + offset) >> OFFSET_VALUE) & 0xff); // high
        host_peci_RdPCIConfigLocal_init(msg, addr_offset, addr_fun, adrr_bus);
        ret = ioctl(peci_fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(peci_file, "cpu_error_peci error: RdPCIConfigLocal failed, ret = %d\n", ret);
        }

        if (offset == 0) {
            fprintf(peci_file, "%02x: ", offset);
        } else if ((offset % ADECIMAL_VALUE) == 0) {
            fprintf(peci_file, "\n");
            fprintf(peci_file, "%02x: ", (offset / ADECIMAL_VALUE));
        }

        for (i = 0; i <= 4 ; i++) {
            if (record_tag == 1 && i > 0) {
                fprintf(mce_iio_file, "%02x ",  msg->rx_buf[i]);
            }
            fprintf(peci_file, "%02x ",  msg->rx_buf[i]);
        }
    }

    if (record_tag == 1) {
        fprintf(mce_iio_file, "\n");
    }
    fflush(mce_iio_file);
    fdatasync(fileno(mce_iio_file));
    fprintf(peci_file, "\n");

    return 0;
}

int host_mce_read_mce_content(
    int fd,
    FILE * mce_file,
    struct xfer_msg *msg,
    unsigned char core,
    unsigned char bank,
    unsigned char secondary_bank
    )
{
    int j;
    int ret;

    for (j = 0; j < 10; j++) {
        host_mce_RdPkgConfig_init(msg);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: core(%u) RdPkgConfig serial = %d, ret = %d\n", core, j, ret);
            return -1;
        }

        fprintf(mce_file, "core=%u : ", core);
        host_mce_fprintf_bank_name(mce_file, bank, secondary_bank);
        host_mce_fprintf_bank_content( mce_file, j, msg, bank, secondary_bank, core);
    }

    if ((bank == BANK_FOR_COLLECTION_END) && (secondary_bank == 0)) {
        fprintf(mce_iio_file, COLLECT_DONE);
        syslog(LOG_DEBUG, "Collect mce-iio log end\n");
    }

    return 0;
}
void bdf_to_addr(unsigned char bus, unsigned char device, unsigned char function, uint16_t* addr_base, uint16_t* addr_bus)
{
    uint32_t value;

    value = (((bus << 20 ) & 0xff00000 ) | ((device << 15) & 0xf8000) | ((function << 12) & 0x7000));
    *addr_bus = (value >> 16) & 0xffff;
    *addr_base = value & 0xffff;
}

static int transfer_bdf_to_offset_table(unsigned char bus, unsigned char device,
        unsigned char function, ieh_function_table_t **function_to_offset_table)
{
    int bus_count;
    int bus_index;
    int device_index;
    int function_index;
    ieh_device_table_t *device_table;
    ieh_function_table_t *function_table;
    int device_count;
    int function_count;

    bus_count = TABLE_SIZE(g_bus_table, ieh_bus_table_t);
    for (bus_index = 0; bus_index < bus_count; bus_index++) {
        if (g_bus_table[bus_index].bus != bus) {
            continue;
        }
        device_table = g_bus_table[bus_index].ieh_device_table;
        device_count = g_bus_table[bus_index].table_size;
        for (device_index = 0; device_index < device_count; device_index++) {
            if (device_table[device_index].device != device) {
                continue;
            }
            function_table = device_table[device_index].ieh_func_table;
            function_count = device_table[device_index].table_size;
            for (function_index = 0; function_index < function_count; function_index++) {
                if (function_table[function_index].function == function) {
                    *function_to_offset_table = &function_table[function_index];
                    return 0;
                }
            }
        }
    }
    return -1;
}

static void record_ieh_err_status(int peci_fd, FILE * peci_file,  struct xfer_msg *msg,
                unsigned char* bus, unsigned char* dev, unsigned char* func) {
    int i;
    int devfun_n;
    unsigned char device;
    unsigned char function;
    unsigned char device_list[32];
    unsigned char function_list[32];
    unsigned char find_index;
    bool find_flag;
    unsigned char dev_tmp[10] = {2, 0};
    unsigned char func_tmp[10] = {2, 4};
    ieh_function_table_t *function_to_offset_table;
    int table_size;
    int ret;

    find_index = 0;
    for (devfun_n = 0; devfun_n < 32; devfun_n++) {
        if (g_peci_error & (1 << devfun_n)) {
            if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                    0x300 + devfun_n * 4, 0x300 + (devfun_n + 1) * 4, true, false) == -1) {
                continue;
            }
            find_flag = false;
            /*7:3 Satellite IEH Bit0 Device Number*/
            device = (msg->rx_buf[1] >> 3) & 0x1f;
            /*2:0 Satellite IEH Bit0 Function Number*/
            function = msg->rx_buf[1] & 0x7;
            if (find_index == 0) {
                device_list[find_index] = device;
                function_list[find_index++] = function;
            } else if (find_index < 32) {
                for (i = 0; i < find_index; i++) {
                    if (device_list[i] == device && function_list[i] == function) {
                        find_flag = true;
                        break;
                    }
                }
                if (find_flag) {
                    continue;
                } else {
                    device_list[find_index] = device;
                    function_list[find_index++] = function;
                }
            }
            dev_tmp[1] = device;
            func_tmp[1] = function;
            ret = transfer_bdf_to_offset_table(bus[1], device, function, &function_to_offset_table);
            if (ret != 0) {
                continue;
            }
            for (i = 0; i < function_to_offset_table->table_size; i++) {
                host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev_tmp, func_tmp,
                    function_to_offset_table->ieh_offset_table[i].beg_addr,
                    function_to_offset_table->ieh_offset_table[i].end_addr, true, false);
            }
        }
    }
}

void * host_peci_msr_info_D1734(struct xfer_msg *msg, int peci_fd, FILE * mce_file,
        int fd_num_index, int cpu_core_num)
{
    /*xxx[0] 位该数组的长度*/
    unsigned char bus[] = {2, 31};
    unsigned char dev[] = {2, 30};
    unsigned char func[] = {2, 2};
    uint32_t mca_err_src_log;
    time_t timep;

    time(&timep);
    fprintf(mce_file, "---------------------begin---------------------------------\n");
    fprintf(mce_file, "cpu_error_gpio : at %s occur ", ctime(&timep));
    fprintf(mce_file, "%s(%s)input\n", fd_name[fd_num_index].gpio_name,
        fd_name[fd_num_index].sig_arry[fd_name[fd_num_index].sig_index]);

    /* 查看 MCA_ERR_SRC_LOG 记录到错误时 dump msr sheet */
    /* Bus: 31, Device: 30, Function: 2, address: EC-EF */
    if (host_peci_fprintf_bank_content_D1734(peci_fd, mce_file, msg, bus, dev, func, 0xec, 0xef, true, false) == -1) {
        goto finish;
    }
    mca_err_src_log = msg->rx_buf[4] << 24 | msg->rx_buf[3] << 16 | msg->rx_buf[2] << 8 | msg->rx_buf[1];
    if (mca_err_src_log == 0) {
        /* No error occurred */
        goto finish;
    }

    /* Bus: 30, Device: 0, Function: 0, address: A4-A7 A8-AB */
    bus[1] = 30;
    dev[1] = 0;
    func[1] = 0;
    if (host_peci_fprintf_bank_content_D1734(peci_fd, mce_file, msg, bus, dev, func, 0xa4, 0xa7, true, false) == -1) {
        goto finish;
    }
    if (host_peci_fprintf_bank_content_D1734(peci_fd, mce_file, msg, bus, dev, func, 0xa8, 0xab, true, false) == -1) {
        goto finish;
    }

    /* dump bank */
    dump_mce_bank_D1734(msg, peci_fd, mce_file, fd_num_index, cpu_core_num);

finish:
    time(&timep);
    fprintf(mce_file, "cpu_error_gpio : end at %s ", ctime(&timep));
    fprintf(mce_file, "-----------------------end-------------------------------\n");
    fflush(mce_file);
    fdatasync(fileno(mce_file));
    return NULL;
}

void * host_peci_cpu_block_info_D1734(struct xfer_msg *msg, int peci_fd, FILE * peci_file)
{
    int i;

    /*xxx[0] 为需要解析的数组长度，有效数据从xxx[1]开始*/
    unsigned char bus[2] = {2, 30};
    unsigned char dev[2] = {2, 0};
    unsigned char func[2] = {2, 3};

    /*Bus: 30, Device: 0, Function: 3, address: 200-22c  */
    g_peci_error = 0;
    if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
            0x200, 0x22c, true, true) == -1) {
        goto finish;
    }
    if (g_peci_error > 0) {
        record_ieh_err_status(peci_fd, peci_file, msg, bus, dev, func);
    }

    /* Bus: 0-2, Device: 0, Function: 4, address: 200-22c */
    func[1] = 4;
    for (i = 0; i <= 2; i++) {
        bus[1] = i;
        g_peci_error = 0;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x200, 0x22c, true, true) == -1) {
            goto finish;
        }
        if (g_peci_error > 0) {
            record_ieh_err_status(peci_fd, peci_file, msg, bus, dev, func);
        }
    }

finish:
    return NULL;
}

void * host_peci_pch_block_info_D1734(struct xfer_msg *msg, int peci_fd, FILE * peci_file)
{
    int i;
    /*xxx[0] 为需要解析的数组长度，有效数据从xxx[1]开始*/
    unsigned char bus[10] = {7, 0, 1, 2, 3, 4, 5};
    unsigned char dev[10] = {2, 0};
    unsigned char func[10] = {2, 4};

    /* PCH ERR
     * Bus: 0, Device: 29, Function: 0, address: 200-230 
     */
    bus[0] = 2;
    bus[1] = 0;
    dev[0] = 2;
    dev[1] = 29;
    func[0] = 2;
    func[1] = 0;
    g_peci_error = 0;
    if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
            0x200, 0x230, true, true) == -1) {
        goto finish;
    }

    if (g_peci_error & (1 << 0)) {
        /* IEH部分
        * Bus: 0, Device: 29, Function: 0, address: 280-2c0
        */
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x280, 0x2c0, true, false) == -1) {
            goto finish;
        }
    }
    if (g_peci_error & (1 << 16)) {
        /* SATA接口部分
        * Bus: 0, Device: 14, Function: 0, address: 6-12
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 14;
        func[0] = 2;
        func[1] = 0;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x6, 0x12, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 17)) {
        /* USB接口部分
        * Bus: 0, Device: 30, Function: 0, address: 6-12
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 30;
        func[0] = 2;
        func[1] = 0;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x6, 0x12, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 18)) {
        /* LPC接口部分
        * Bus: 0, Device: 31, Function: 0, address: 6-12
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 31;
        func[0] = 2;
        func[1] = 0;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x6, 0x12, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 19)) {
        /* Legacy SMBUS 部分
        * Bus: 0, Device: 31, Function: 4, address: 6-12
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 31;
        func[0] = 2;
        func[1] = 4;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x6, 0x12, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 20)) {
        /* SPI控制器部分
        * Bus: 0, Device: 31, Function: 5, address: 4-10 D0-DC
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 31;
        func[0] = 2;
        func[1] = 5;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x4, 0x10, true, false) == -1) {
            goto finish;
        }

        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0xd0, 0xdc, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 21)) {
        /* Trace Hub 部分
        * Bus: 0, Device: 31, Function: 7, address: 4-10
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 31;
        func[0] = 2;
        func[1] = 7;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x4, 0x10, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 22)) {
        /* HSUART部分
        * Bus: 0, Device: 26 Function:0-2 address: 4-10
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 26;
        func[0] = 4;
        for (i=1; i<4;i++) {
            func[i] = i-1;
        }
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x4, 0x10, true, false) == -1) {
            goto finish;
        }
    }

    if (g_peci_error & (1 << 23)) {
        /* SMBUS接口部分
        * Bus: 0, Device: 15, Function: 0, address: 4-10 4a-56
        */
        bus[0] = 2;
        bus[1] = 0;
        dev[0] = 2;
        dev[1] = 15;
        func[0] = 2;
        func[1] = 0;
        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x4, 0x10, true, false) == -1) {
            goto finish;
        }

        if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func,
                0x4a, 0x56, true, false) == -1) {
            goto finish;
        }
    }

finish:
    return NULL;
}

void * host_peci_csr_info_D1734(struct xfer_msg *msg, int peci_fd, FILE * peci_file)
{
    /*xxx[0] 位该数组的长度*/
    unsigned char bus[] = {2, 30};
    unsigned char dev[] = {2, 0};
    unsigned char func[] = {2, 0};

    /* 新增部分仅记录，不解析 */
    /* Bus: 30, Device: 0, Function: 0, address: D8-DB */
    if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func, 0xd8, 0xdb, false, false) == -1) {
        goto finish;
    }
    /* Bus: 31, Device: 30, Function: 4, address: 84-87 F0-FF*/
    bus[1] = 31;
    dev[1] = 30;
    func[1] = 4;
    if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func, 0x84, 0x87, false, false) == -1) {
        goto finish;
    }
    if (host_peci_fprintf_bank_content_D1734(peci_fd, peci_file, msg, bus, dev, func, 0xF0, 0xFF, false, false) == -1) {
        goto finish;
    }

finish:
    return NULL;
}

void * host_peci_key_info(struct xfer_msg *msg, int peci_fd, FILE * peci_file, int fd_num_index)
{
    time_t timep;
    time(&timep);
    fprintf(peci_file, "---------------------begin---------------------------------\n");
    fprintf(peci_file, "cpu_error_gpio : at %s occur ", ctime(&timep));
    fprintf(peci_file, "%s(%s) input\n", fd_name[fd_num_index].gpio_name,
        fd_name[fd_num_index].sig_arry[fd_name[fd_num_index].sig_index]);

    read_peci_iio_reg_addr(msg, peci_fd);

    fprintf(peci_file, "Bus: ff, Device: 1E, Function: 2, address: EC-EF\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x2000, 0x1f, 236, 239, 1) == -1) {
        goto finish;
    }

    fprintf(peci_file, "Bus: ff, Device: 10, Function: 5, address: A4-A7\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x5000, 0x18, 164, 167, 1) == -1) {
        goto finish;
    }

    fprintf(peci_file, "Bus: ff, Device: 10, Function: 5, address: A8-AB\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x5000, 0x18, 168, 171, 1) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 00, Function: 0, address: 14C-14F\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x00, 332, 335, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 00, Function: 0, address: 158-15B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x00, 344, 347, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 00, Function: 0, address: 164-173\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x00, 356, 371, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 00, Function: 0, address: 178-17B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x00, 376, 379, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 00, Function: 0, address: 200-203\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x00, 512, 515, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 01, Function: 0, address: 14C-14F\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x00, 332, 335, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 01, Function: 0, address: 158-15B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x00, 344, 347, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 01, Function: 0, address: 164-173\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x00, 356, 371, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 01, Function: 0, address: 178-17B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x00, 376, 379, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 01, Function: 0, address: 200-203\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x00, 512, 515, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 0, address: 14C-14F\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x01, 332, 335, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 0, address: 158-15B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x01, 344, 347, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 0, address: 164-173\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x01, 356, 371, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 0, address: 178-17B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x01, 376, 379, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 0, address: 200-203\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x0000, 0x01, 512, 515, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 1, address: 14C-14F\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x1000, 0x01, 332, 335, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 1, address: 158-15B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x1000, 0x01, 344, 347, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 1, address: 164-173\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x1000, 0x01, 356, 371, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 1, address: 178-17B\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x1000, 0x01, 376, 379, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: 00, Device: 02, Function: 1, address: 200-203\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x1000, 0x01, 512, 515, 0) == -1) {
        goto finish;
    }
    fflush(peci_file);
    fdatasync(fileno(peci_file));

finish:
    return NULL;
    }

void * host_peci_info(struct xfer_msg *msg, int peci_fd, FILE * peci_file, int fd_num_index)
{
    time_t timep;

    fprintf(peci_file, "Bus: 00, Device: 05, Function: 2, address: 0-400\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0xa000, 0x02, 0, 1024, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: ff, Device: 13, Function: 0, address: 0-200\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x8000, 0x19, 0, 512, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: ff, Device: 13, Function: 1, address: 0-514\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x9000, 0x19, 0, 1300, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: ff, Device: 14, Function: 2, address: 0-800\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x2000, 0x1a, 0, 2048, 0) == -1) {
        goto finish;
    }
    fprintf(peci_file, "Bus: ff, Device: 14, Function: 3, address: 0-578\n");
    if (host_peci_fprintf_bank_content(peci_fd, peci_file, msg, 0x3000, 0x1a, 0, 1400, 0) == -1) {
        goto finish;
    }

finish:
    time(&timep);
    fprintf(peci_file, "cpu_error_gpio : end at %s  ", ctime(&timep));
    fprintf(peci_file, "-----------------------end-------------------------------\n");
    fflush(peci_file);
    fdatasync(fileno(peci_file));
    return NULL;
}

int host_mce_read_channel_content_D1734(
    int fd,
    int channel_loop_num,
    FILE * mce_file,
    struct xfer_msg *msg)
{
    int channel_loop, reg_loop, ret, rx_loop;
    uint16_t parm_reg_info[5] = {0x8001, 0x8000, 0x8002, 0x8003, 0x8004};
    /* 是否记录到解析文件的依据从哪里来，保持之前设置 */
    bool record_tag[5] = {1, 0, 1, 1, 1};
    char reg_name[5][REG_ATTR_SIZE] = {{"STATUS"}, {"CTL"}, {"ADDR"}, {"MISC"}, {"MISC2"}};

    for(channel_loop=0; channel_loop< channel_loop_num; channel_loop++) {
        fprintf(mce_file, "cpu_error_gpio error: CHA%d, processer id=%x\n", channel_loop, channel_loop);
        for (reg_loop=0; reg_loop<5; reg_loop++) {
            host_mce_Rdiamsr_init(msg, channel_loop, parm_reg_info[reg_loop]);
            ret = ioctl_check(fd, msg, cc_intervals_d17, cc_intervals_num_d17, RETRY_MAX);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: read CHA%d reg %x failed,  ret = %d\n", channel_loop, parm_reg_info[channel_loop], ret);
                return -1;
            }
            fprintf(mce_file, "%x: ", parm_reg_info[reg_loop]);
            if(record_tag[reg_loop]) {
                fprintf(mce_iio_file, "CHA%dMC_%s : ", channel_loop, reg_name[reg_loop]);
            }
            for (rx_loop = 0; rx_loop <= 8 ; rx_loop++) {
                fprintf(mce_file, "%02x ",  msg->rx_buf[rx_loop]);
                if(record_tag[reg_loop] && rx_loop > 0) {
                    fprintf(mce_iio_file, "%02x ",  msg->rx_buf[rx_loop]);
                    if (rx_loop == 8) {
                        fprintf(mce_iio_file, "\n");
                    }
                }
            }
            /* STATUS bit63为0时，不需要读取后续寄存器 */
            if (reg_loop == 0 && (msg->rx_buf[8] >> 7) == 0) {
                break;
            }
        }
        fprintf(mce_file, "\n");
    }

    return 0;
}

int host_mce_read_bank_content_D1734(
    int fd,
    FILE * mce_file,
    struct xfer_msg *msg,
    unsigned char core,
    unsigned char bank,
    unsigned char *core_id,
    int type)
{
    int msr_loop, ret, rx_loop;
    char bank_name[17][REG_ATTR_SIZE] = {{"IFU"}, {"DCU"}, {"DTLB"}, {"MLC"}, {"PCU"}, {"Unused"}, {"UBOX"}, {"Unused"}, {"Unused"},
                                        {"CHA0"}, {"CHA1"}, {"CHA2"}, {"M2M0"}, {"IMC0_Ch0"}, {"IMC0_Ch1"}, {"IMC0_Ch2"},{"M2M1"}};

    char msr_name[5][REG_ATTR_SIZE] = {{"STATUS"}, {"CTL"}, {"ADDR"}, {"MISC"}, {"CTL2"}};
    /* 是否记录到解析文件的依据从哪里来，保持之前设置 */
    /* 取消了单独获取CTL2, 因此这里设置记录CTRL2 */
    bool record_tag[5] = {1, 0, 1, 1, 1};
    /* 先根据STATUS状态确定是否读取后续寄存器 */
    uint16_t bank_reg_info[17][5] = {{0x401, 0x400, 0x402, 0x403, 0x280}, {0x405, 0x404, 0x406, 0x407, 0x281},
                                    {0x409, 0x408, 0x40A, 0x40B, 0x282}, {0x40D, 0x40C, 0x40E, 0x40F, 0x283},
                                    {0x411, 0x410, 0x412, 0x413, 0x284}, {0, 0, 0, 0, 0},
                                    {0x419, 0x418, 0x41A, 0x41B, 0x286}, {0, 0, 0, 0, 0},
                                    {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0},
                                    {0x431, 0x430, 0x432, 0x433, 0x28C}, {0x435, 0x434, 0x436, 0x437, 0x28D},
                                    {0x439, 0x438, 0x43A, 0x43B, 0x28E}, {0x43D, 0x43C, 0x43E, 0x43F, 0x28F},
                                    {0x441, 0x440, 0x442, 0x443, 0x290} };

    if((core > 7) || (core_id[core] == 0xff)) {
        fprintf(mce_file, "cpu_error_gpio error: core %d ,%x\n", core, core_id[core]);
        return -1;
    }
    if ((bank == BANK_FOR_COLLECTION_END)) {
        fprintf(mce_iio_file, COLLECT_DONE);
        syslog(LOG_DEBUG, "Collect mce-iio log end\n");
        return 0;
    }

    fprintf(mce_file, "core=%u , processer id=%x: ", core, core_id[core]);
    /*record bank name*/
    fprintf(mce_file, "%s bank=%u: \n", bank_name[bank], bank);
    /*record bank msr vlaue*/
    for(msr_loop=0; msr_loop<5; msr_loop++) {
        host_mce_Rdiamsr_init(msg, core_id[core], bank_reg_info[bank][msr_loop]);
        ret = ioctl_check(fd, msg, cc_intervals_d17, cc_intervals_num_d17, RETRY_MAX);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: read msr:%x failed, ret = %d\n", bank_reg_info[bank][msr_loop], ret);
            return -1;
        }
        fprintf(mce_file, "%x: ", bank_reg_info[bank][msr_loop]);
        if(record_tag[msr_loop]) {
            if (type == THREAD0) {
                fprintf(mce_iio_file, "CORE%uMC%u%sTHREAD0 : ", core, bank, msr_name[msr_loop]);
            } else if (type == THREAD1) {
                fprintf(mce_iio_file, "CORE%uMC%u%sTHREAD1 : ", core, bank, msr_name[msr_loop]);
            }
        }
        for (rx_loop = 0; rx_loop <= 8 ; rx_loop++) {
            fprintf(mce_file, "%02x ",  msg->rx_buf[rx_loop]);
            if(record_tag[msr_loop] && rx_loop > 0) {
                fprintf(mce_iio_file, "%02x ",  msg->rx_buf[rx_loop]);
                if (rx_loop == 8) {
                    fprintf(mce_iio_file, "\n");
                }
            }
        }
        /* STATUS bit63为0时，不需要读取后续寄存器 */
        if (msr_loop == 0 && (msg->rx_buf[8] >> 7) == 0) {
            break;
        }
    }

    fprintf(mce_file, "\n");

    return 0;
}

void *dump_mce_bank_D1734(struct xfer_msg *msg, int peci_fd, FILE * mce_file, int fd_num_index, int cpu_core_num)
{
    uint16_t adrr_bus;
    uint16_t addr_base;
    unsigned char addr_bus_lsb;
    unsigned char addr_bus_msb;
    unsigned char addr_fun;
    unsigned char addr_offset;
    unsigned char core;
    unsigned char bank;
    int rx_loop;
    int ret, core_loop, bit_loop, core_mask_bit;
    uint32_t core_mask;
    unsigned char core_id[8], core_id_sec[8];

    /*Bus: B(31), Device: 30, Function: 3 (PCU CR3 Registers) 0xd0-0xd4
     *endpoint bus要减一，原因未知,因此传入30
     */
    bdf_to_addr(30, 30, 3, &addr_base, &adrr_bus);
    addr_offset = ((addr_base + 0xd0) & 0xff); //low
    addr_fun = (((addr_base + 0xd0) >> OFFSET_VALUE) & 0xff); // high
    addr_bus_lsb = adrr_bus & 0xff;  //low
    addr_bus_msb = (adrr_bus >> OFFSET_VALUE) & 0xff;  //high
    host_peci_RdEndpoint_lpci_init(msg, addr_offset, addr_fun, addr_bus_lsb, addr_bus_msb);

    ret = ioctl(peci_fd, AST_PECI_IOCXFER, msg);
    if (ret < 0) {
        fprintf(mce_file, "cpu_error_peci error: RdEndpoint_lpci failed, ret = %d\n", ret);
        goto finish;
    }

    fprintf(mce_file, "B31D30F3Addr0xd0-0xd4: \n", ret);
    fprintf(mce_file, "%02x ", msg->rx_buf[0]);
    for (rx_loop = 4; rx_loop >=1 ; rx_loop--) {
        fprintf(mce_file, PRINTF_BINARY_PATTERN_INT8,  PRINTF_BYTE_TO_BINARY_INT8(msg->rx_buf[rx_loop]));
    }
    fprintf(mce_file, "\n");

    /* 获取各个core的processor id */
    core_mask = msg->rx_buf[4] << 24 | msg->rx_buf[3] << 16 | msg->rx_buf[2] << 8 | msg->rx_buf[1];
    core_mask_bit = 0;
    for (core_loop=0; core_loop<cpu_core_num ; core_loop++) {
        for (bit_loop=core_mask_bit; bit_loop<=31 ; bit_loop++) {
            core_id[core_loop] = 0xff;
            core_id_sec[core_loop] = 0xff;
            if ((core_mask & (1 << bit_loop))) {
                core_id[core_loop] = 2 * bit_loop;
                core_id_sec[core_loop] = 2 * bit_loop + 1;
                core_mask_bit = bit_loop+1;
                fprintf(mce_file, "core%u: prosessor0: %u, prosessor1 %u\n", core_loop, core_id[core_loop], core_id_sec[core_loop]);
                break;
            }
        }
    }

    /*core0-7 bank 0-3*/
    for (core = 0 ; core < cpu_core_num; core++) {
        for (bank = 0 ; bank <= 3; bank++) {
            host_mce_read_bank_content_D1734(peci_fd, mce_file, msg, core, bank, core_id, THREAD0);
        }
    }

    /*CHA0-CHA5*/
    host_mce_read_channel_content_D1734(peci_fd, 6, mce_file, msg);

    /*core0 bank 4-14, except bank 5,7-11*/
    core = 0;
    core_id[core] = 0;
    for(bank = 4 ; bank <= 14; bank++) {
        if(bank == 5 || (bank >= 7 && bank <= 11))
            continue;
        host_mce_read_bank_content_D1734(peci_fd, mce_file, msg, core, bank, core_id, THREAD0);
    }
    /*end of collection*/

finish:
    return NULL;
}


void * dump_mce_bank(struct xfer_msg *msg, int fd, FILE * mce_file, int fd_num_index, int cpu_core_num)
{
    int    i, ret;
    time_t timep;
    time(&timep);
    fprintf(mce_file, "---------------------begin---------------------------------\n");
    fprintf(mce_file, "cpu_error_gpio : at %s occur ", ctime(&timep));
    fprintf(mce_file, "%s(%s) input\n", fd_name[fd_num_index].gpio_name,
        fd_name[fd_num_index].sig_arry[fd_name[fd_num_index].sig_index]);

    for (unsigned char core = 0 ; core < cpu_core_num; core++) {
        for (unsigned char bank = 0 ; bank <= 3; bank++) {
            unsigned char secondary_bank = 0;
            host_mce_WrPkgConfig_init(msg, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
                goto finish;
            }

            host_mce_WrPkgConfig_init(msg, 0x02, 0x10, bank, core, 0x00, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: core(%u) Bank requested (bank=%u) to  dump failed , ret = %d\n", core, bank, ret);
                goto finish;
            }

            host_mce_read_mce_content(fd, mce_file, msg, core, bank, secondary_bank);
            host_mce_WrPkgConfig_init(msg, 0x03, 0x00, 0x01, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Close Machine Check Bank Sequence, ret = %d\n", ret);
                goto finish;
            }
        }
    }

    for( unsigned char bank = 4 ; bank <= 10; bank++) {
        unsigned char core = 0;
        unsigned char secondary_bank = 0;
        if(bank == 5 || bank == 8)
            continue;
        host_mce_WrPkgConfig_init(msg, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
            goto finish;
        }

        host_mce_WrPkgConfig_init(msg, 0x02, 0x10, bank, 0x00, 0x00, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: Bank requested (bank=%u) to  dump failed , ret = %d\n", bank, ret);
            goto finish;
        }

        host_mce_read_mce_content(fd, mce_file, msg, core, bank, secondary_bank);
        host_mce_WrPkgConfig_init(msg, 0x03, 0x00, 0x01, 0x00, 0x01, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "Host_mce Error: Close Machine Check Bank Sequence, ret = %d\n", ret);
            goto finish;
        }
    }

    for(unsigned char bank = 17 ; bank <= 18; bank++){
        unsigned char core = 0;
        for(unsigned char secondary_bank = 0; secondary_bank <= 2; secondary_bank++){
            host_mce_WrPkgConfig_init(msg, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
                goto finish;
            }

            host_mce_WrPkgConfig_init(msg, 0x02, 0x10, bank, 0x00, 0x00, secondary_bank);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Bank requested (bank=%u,secondary=%u) to  dump failed , ret = %d\n", bank, secondary_bank, ret);
                goto finish;
            }

            host_mce_read_mce_content(fd, mce_file, msg, core, bank, secondary_bank);
            host_mce_WrPkgConfig_init(msg, 0x03, 0x00, 0x01, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Close Machine Check Bank Sequence, ret = %d\n", ret);
                goto finish;
            }
        }
    }

    for(unsigned char bank = 19 ; bank <= 19; bank++){
        unsigned char core = 0;
        for(unsigned char secondary_bank = 0; secondary_bank <= 1; secondary_bank++){
            host_mce_WrPkgConfig_init(msg, 0x02, 0x00, 0x10, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
                goto finish;
            }

            host_mce_WrPkgConfig_init(msg, 0x02, 0x10, bank, 0x00, 0x00, secondary_bank);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "cpu_error_gpio error: Bank requested (bank=%u,secondary=%u) to  dump failed , ret = %d\n", bank, secondary_bank, ret);
                goto finish;
            }

            host_mce_read_mce_content(fd, mce_file, msg, core, bank, secondary_bank);
            host_mce_WrPkgConfig_init(msg, 0x03, 0x00, 0x01, 0x00, 0x01, 0x00);
            ret = ioctl(fd, AST_PECI_IOCXFER, msg);
            if (ret < 0) {
                fprintf(mce_file, "Host_mce Error: Close Machine Check Bank Sequence, ret = %d\n", ret);
                goto finish;
            }
        }
    }

    for(unsigned char core = 0 ; core < cpu_core_num; core++) {
        unsigned char bank = 128;
        unsigned char secondary_bank = 0;
        host_mce_WrPkgConfig_init(msg, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
            goto finish;
        }

        host_mce_WrPkgConfig_init(msg, 0x02, 0x10, bank, core, 0x00, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: core(%u) Bank requested (bank=%u) to  dump failed , ret = %d\n", core, bank, ret);
            goto finish;
        }

        host_mce_RdPkgConfig_init(msg);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "cpu_error_gpio error: core(%u) RdPkgConfig serial = %d, ret = %d\n", core, 1, ret);
            goto finish;
        }

        fprintf(mce_file, "core=%u : ", core);
        host_mce_fprintf_bank_name(mce_file, bank, secondary_bank);

        fprintf(mce_file, "IA32_MCG_STATUS : \n");
        for (i = 0; i <=4 ; i++) {
            fprintf(mce_file, "rx_buf[%d] = 0x%02x ", i, msg->rx_buf[i]);
        }

        fprintf(mce_file, "\n\n\n");
        host_mce_WrPkgConfig_init(msg, 0x03, 0x00, 0x01, 0x00, 0x01, 0x00);
        ret = ioctl(fd, AST_PECI_IOCXFER, msg);
        if (ret < 0) {
            fprintf(mce_file, "Host_mce Error: Close Machine Check Bank Sequence, ret = %d\n", ret);
            goto finish;
        }
    }

finish:
    time(&timep);
    fprintf(mce_file, "cpu_error_gpio : end at %s ", ctime(&timep));
    fprintf(mce_file, "-----------------------end-------------------------------\n");
    fflush(mce_file);
    fdatasync(fileno(mce_file));
    return NULL;

}

void * host_mce_info_D1734(struct xfer_msg *msg, int peci_fd, FILE * mce_file, FILE * peci_file,
        int fd_num_index, int cpu_core_num)
{
    time_t timep;

    time(&timep);
    fprintf(peci_file, "---------------------begin---------------------------------\n");
    fprintf(peci_file, "cpu_error_gpio : at %s occur ", ctime(&timep));
    fprintf(peci_file, "%s(%s)input\n", fd_name[fd_num_index].gpio_name,
        fd_name[fd_num_index].sig_arry[fd_name[fd_num_index].sig_index]);

    i2cdump_cpld(peci_file);
    host_peci_msr_info_D1734(msg, peci_fd, mce_file, fd_num_index, cpu_core_num);
    host_peci_cpu_block_info_D1734(msg, peci_fd, peci_file);
    host_peci_pch_block_info_D1734(msg, peci_fd, peci_file);
    host_peci_csr_info_D1734(msg, peci_fd, peci_file);

    time(&timep);
    fprintf(peci_file, "cpu_error_gpio : end at %s  ", ctime(&timep));
    fprintf(peci_file, "-----------------------end-------------------------------\n");
    fflush(peci_file);
    fdatasync(fileno(peci_file));

    fprintf(mce_iio_file, COLLECT_DONE);
    syslog(LOG_DEBUG, "Collect mce-iio log end\n");
    fflush(mce_iio_file);
}

void * host_mce_info(void *arg)
{
    int    ret                = 0;
    int    fd                 = 0;
    int    i                  = 0;
    struct xfer_msg *msg      = NULL;
    struct xfer_msg *msg_peci = NULL;
    FILE*  mce_file;
    FILE*  peci_file;

    int   fd_num_index        = (int)(*(int *)arg);
    int   cpu_core_num;

    syslog(LOG_DEBUG, "host_mce_info begin\n");
    mce_file = fopen(HOST_MCE_INFO_PATH, "a+" );
    if (mce_file == NULL) {
        syslog(LOG_INFO, "fopen %s failed\n", HOST_MCE_INFO_PATH);
        return NULL;
    }

    peci_file = fopen(HOST_PECI_INFO_PATH, "a+" );
    if (peci_file == NULL) {
        fclose(mce_file);
        syslog(LOG_INFO, "fopen %s failed\n", HOST_PECI_INFO_PATH);
        return NULL;
    }

    backup_mce_iio_file();
    mce_iio_file = fopen(DEFAULT_MCE_ERROR_INFO_PATH, "w");
    if (mce_iio_file == NULL) {
        syslog(LOG_INFO, "fopen %s failed\n", DEFAULT_MCE_ERROR_INFO_PATH);
        fclose(mce_file);
        fclose(peci_file);
        return NULL;
    }

    if ((fd = open(PECI_DEVICE, O_RDWR, S_IRWXU | S_IRWXG | S_IRWXO | S_IRUSR | S_IWUSR)) < 0) {
        fprintf(mce_file, "cpu_error_gpio error: Could not open file /dev/aspeed-peci: %s\n", strerror(errno));
        fclose(mce_file);
        fclose(peci_file);
        fclose(mce_iio_file);
        return NULL;
    }

    msg = malloc(sizeof(struct xfer_msg));
    if (msg == NULL) {
        fprintf(mce_file, "cpu_error_gpio error: malloc xfer_msg failed\n");
        fclose(mce_file);
        fclose(peci_file);
        fclose(mce_iio_file);
        close(fd);
        return NULL;
    }
    /* get cpu core number */
    cpu_core_num = get_product_core_num();
    if( g_mce_type == 0 ) {
        /* read peci key register information */
        host_peci_key_info(msg, fd, peci_file, fd_num_index);
        /* dump cpld */
        i2cdump_cpld(peci_file);
         /* dump mce bank */
        dump_mce_bank(msg, fd,  mce_file, fd_num_index, cpu_core_num);
        /* read peci space register */
        host_peci_info(msg, fd, peci_file, fd_num_index);
    } else {
        host_mce_info_D1734(msg, fd, mce_file, peci_file, fd_num_index, cpu_core_num);
    }

finish:
    free(msg);
    close(fd);
    fclose(mce_file);
    fclose(peci_file);
    fclose(mce_iio_file);
    return NULL;
}

static void backup_mce_iio_file()
{
    char matchstr_buf[STRING_SIZE]  = {'\0'};
    char backup_buf[STRING_SIZE]    = {'\0'};
    FILE *system_popen_fs = NULL;
    char stop_num_stream[STOP_NUM_BUFF];
    uint8_t stop_num;
    char* stop;

    if(access(DEFAULT_MCE_ERROR_INFO_PATH, F_OK) == -1) {
        return;
    }
    sprintf(matchstr_buf, "%s %s %s %s %s", "cat", DEFAULT_MCE_ERROR_INFO_PATH, "| grep", STOP_STR, "| wc -l");
    system_popen_fs = popen(matchstr_buf, "r");
    if (fgets(stop_num_stream, sizeof(stop_num_stream), system_popen_fs) != NULL) {
        stop_num = strtol(stop_num_stream, &stop, 10);
        if (stop_num != NO_STOP) {
            pclose(system_popen_fs);
            return;
        }
    }
    pclose(system_popen_fs);
    sprintf(backup_buf, "%s %s %s", "cp -f", DEFAULT_MCE_ERROR_INFO_PATH, BACKUP_MCE_ERROR_INFO_PATH);
    system(backup_buf);
    if(access(BACKUP_MCE_ERROR_INFO_PATH, F_OK) == -1) {
        syslog(LOG_INFO, "failed to backup %s", DEFAULT_MCE_ERROR_INFO_PATH);
        return;
    }
    sync();
}

void cpu_error_gpio_mce_info_pthread(int fd_num_index_param)
{
    int ret;

    if(cpu_error_gpio_mce_info_pid != 0) {
        syslog(LOG_DEBUG, "Detect GPIO(%s) signal, begin to read register data\n", fd_name[fd_num_index_param].gpio_name);
        pthread_join(cpu_error_gpio_mce_info_pid, NULL);
        cpu_error_gpio_mce_info_pid = 0;
        g_fd_num_index = fd_num_index_param;
        pthread_create(&cpu_error_gpio_mce_info_pid, NULL, host_mce_info, &g_fd_num_index);
        syslog(LOG_DEBUG, "Detect GPIO(%s) signal, end to read register data\n", fd_name[fd_num_index_param].gpio_name);
    } else {
        g_fd_num_index = fd_num_index_param;
        pthread_create(&cpu_error_gpio_mce_info_pid, NULL, host_mce_info, &g_fd_num_index);
    }
    return;
}

int init_gpio(const char *pin, const char *edge, const char *direction)
{
    char fileName[STRING_SIZE] = {'\0'};
    char path[STRING_SIZE]     = {'\0'};
    char pinStr[STRING_SIZE]   = {'\0'};
    char edgeStr[STRING_SIZE]  = {'\0'};
    char dirStr[STRING_SIZE]   = {'\0'};
    int  status                = 0;

    sprintf(fileName, "%s%s", "gpio", pin);
    sprintf(path, "%s%s", "/sys/class/gpio/", fileName);
    sprintf(pinStr, "%s%s%s%s%s", "echo ", "\"", pin, "\"", " > /sys/class/gpio/export");
    sprintf(edgeStr, "%s%s%s%s%s%s%s", "echo ", "\"", edge, "\"", " > /sys/class/gpio/", fileName, "/edge");
    sprintf(dirStr, "%s%s%s%s%s%s%s", "echo ", "\"", direction, "\"", " > /sys/class/gpio/", fileName, "/direction");

    /*open gpio*/
    if(access(path, F_OK) == -1) {
        status = system(pinStr);
        if (-1 == status) {
            printf("system error\n");
            fflush(stdout);
            return -1;
        }
        if (WIFEXITED(status) && (0 != WEXITSTATUS(status))) {
            printf("run shell fail\n");
            fflush(stdout);
            return -2;
        }
    }

    /*set gpio triggered*/
    status = system(edgeStr);
    if (-1 == status) {
        printf("system error\n");
        fflush(stdout);
        return -1;
    }
    if (WIFEXITED(status) && (0 != WEXITSTATUS(status))) {
        printf("run shell fail\n");
        fflush(stdout);
        return -2;
    }

    /*set gpio direction*/
    status = system(dirStr);
    if (-1 == status) {
        printf("system error\n");
        fflush(stdout);
        return -1;
    }
    if (WIFEXITED(status) && (0 != WEXITSTATUS(status))) {
        printf("run shell fail\n");
        fflush(stdout);
        return -2;
    }

    return 0;
}

/** @note   Determine whether the CPU is powered off
*   @return -1  CPU power-off state or open i2c failed
*   @return 0 CPU power-on state
**/
static int judgePowerOff()
{
    int cpu_status;

    cpu_status = get_value(cpu_status_path, cpu_status_mask);
    if (cpu_status == -1) {
        return -1;
    } else if (cpu_status == cpu_status_on) {
        return 0;
    } else {
        syslog(LOG_INFO, "cpu status does off\n");
        return -1;
    }
}

void exec_cpu_err_cmd(int cpu_err, char* cpu_err_path)
{
    char cpu_err_buf[STRING_SIZE];

    memset(cpu_err_buf, 0, STRING_SIZE);
    sprintf(cpu_err_buf, "%s%d%s%s", "echo ", cpu_err, " > ", cpu_err_path);
    system(cpu_err_buf);
}



static int init_device_info()
{
    int i;
    int productname_ret;
    int fullproductname_ret;
    int productname_len;
    int fullproductname_len;

    /* 获取设备名称 */
    for (i = 1; i <= TRY_TIMES; i++) {
        productname_ret = get_device_name(PRODUCT_NAME_PATH, product_name_buf);
        fullproductname_ret = get_device_name(FULLPRODUCT_NAME_PATH, fullproduct_name_buf);
        if (productname_ret == 0 && fullproductname_ret == 0) {
            break;
        }
    }

    /* 获取cpu开关状态寄存器路径 及 CPLD 信息*/
    productname_len = strlen(product_name_buf);
    fullproductname_len = strlen(fullproduct_name_buf);
    if (strncmp("AC51-48C2G", product_name_buf, productname_len) == 0) {
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x13";
    } else if (strncmp("AS15-20D4M", product_name_buf, productname_len) == 0) {
        cpu_status_path = "obmc_i2cget -f -y 6 0x3d 0x3e";
        cpu_status_on = FPGA_CPU_STATUS_ON;
        cpu_status_mask = FPGA_CPU_STATUS_MASK;
        cpld_table.cpld_list[BASE_CPLD].bus = 6;
        cpld_table.cpld_list[BASE_CPLD].dev = 0x3d;
        cpld_table.cpld_list[CPU_CPLD].bus = 6;
    } else if (strncmp("AS25-128Q", product_name_buf, productname_len) == 0) {
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x13";
        cpu_status_on = ICELAKE_CTO_CPU_STATUS_ON;
        cpu_status_mask = ICELAKE_CTO_CPU_STATUS_MASK;
        cpld_table.cpld_list[CPU_CPLD].bus = 14;
    } else if (strncmp("AS15-40Q", product_name_buf, productname_len) == 0) {
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x13";
        cpu_status_on = ICELAKE_CTO_CPU_STATUS_ON;
        cpu_status_mask = ICELAKE_CTO_CPU_STATUS_MASK;
        cpld_table.cpld_list[CPU_CPLD].bus = 16;
    } else if (strncmp("AS24-128D-2-RJ", fullproduct_name_buf, fullproductname_len) == 0) {
        memset(product_name_buf, 0, PRODUCT_NAME_SIZE);
        strcpy(product_name_buf, fullproduct_name_buf);
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x13";
        cpu_status_on = ICELAKE_CTO_CPU_STATUS_ON;
        cpu_status_mask = ICELAKE_CTO_CPU_STATUS_MASK;
        cpld_table.cpld_list[CPU_CPLD].bus = 14;
        g_handle_err2 = true;
        bios_boot_status_path = "obmc_i2cget -f -y 14 0x0d 0x21";
        bios_boot_status_mask = 0x01;
        cpu_reset_status_path = "obmc_i2cget -f -y 0 0x0d 0x10";
        cpu_reset_status_mask = 0x03;
    } else if (strncmp("AS51-24D", product_name_buf, productname_len) == 0) {
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x85";
        cpld_table.cpld_list[CPU_CPLD].bus = 14;
    }else {
        cpu_status_path = "obmc_i2cget -f -y 0 0x0d 0x85";
    }

    return 0;
}

static void init_device_gpio(int *gpio_tmp)
{
    /* 不同的设备初始化的gpio不一样 */
    if (strncmp("AS14-24D8Q", product_name_buf, strlen(product_name_buf)) == 0
            || strncmp("AS25-128Q", product_name_buf, strlen(product_name_buf)) == 0
            || strncmp("AS51-24D", product_name_buf, strlen(product_name_buf)) == 0
            || strncmp("AS15-40Q", product_name_buf, strlen(product_name_buf)) == 0) {
        init_gpio("826", "falling", "in");
        init_gpio("856", "falling", "in");
        init_gpio("857", "falling", "in");
        init_gpio("858", "falling", "in");
        init_gpio("859", "falling", "in");
        gpio_tmp[0] = open("/sys/class/gpio/gpio826/value", O_RDWR);
        gpio_tmp[1] = open("/sys/class/gpio/gpio856/value", O_RDWR);
        gpio_tmp[2] = open("/sys/class/gpio/gpio857/value", O_RDWR);
        gpio_tmp[3] = open("/sys/class/gpio/gpio858/value", O_RDWR);
        gpio_tmp[4] = open("/sys/class/gpio/gpio859/value", O_RDWR);
        fd_name = icelake_fd_name;
        g_fd_num = 6; /* changed: fd num */
        g_gpio_num = 5; /* changed: gpio num */
    } else if (strncmp("AS24-128D-2-RJ", product_name_buf, strlen(product_name_buf)) == 0) {
        init_gpio("40", "falling", "in");
        init_gpio("41", "falling", "in");
        init_gpio("42", "falling", "in");
        init_gpio("43", "falling", "in");
        gpio_tmp[0] = open("/sys/class/gpio/gpio40/value", O_RDWR);
        gpio_tmp[1] = open("/sys/class/gpio/gpio41/value", O_RDWR);
        gpio_tmp[2] = open("/sys/class/gpio/gpio42/value", O_RDWR);
        gpio_tmp[3] = open("/sys/class/gpio/gpio43/value", O_RDWR);
        fd_name = icelake_fd_name;
    } else {
        init_gpio("72", "falling", "in");
        init_gpio("73", "falling", "in");
        init_gpio("74", "falling", "in");
        init_gpio("75", "falling", "in");
        gpio_tmp[0] = open("/sys/class/gpio/gpio72/value", O_RDWR);
        gpio_tmp[1] = open("/sys/class/gpio/gpio73/value", O_RDWR);
        gpio_tmp[2] = open("/sys/class/gpio/gpio74/value", O_RDWR);
        gpio_tmp[3] = open("/sys/class/gpio/gpio75/value", O_RDWR);
    }
}

static void i2cdump_cpld(FILE * peci_file)
{
    uint8_t index;
    char dump_cmd[STRING_SIZE];
    FILE *fp;
    char dump_stream[STRING_SIZE];

    for (index = 0; index < cpld_table.cpld_num; index++) {
        memset(dump_cmd, 0, STRING_SIZE);
        memset(dump_stream, 0, STRING_SIZE);
        fprintf(peci_file, "\n%d 0x%02x:\n",
            cpld_table.cpld_list[index].bus, cpld_table.cpld_list[index].dev);
        /* i2cdump: need to specify the read mode. b: byte, default */
        sprintf(dump_cmd, "i2cdump -f -y %d %d b",
            cpld_table.cpld_list[index].bus, cpld_table.cpld_list[index].dev);
        fp = popen(dump_cmd, "r");
        if (fp == NULL) {
            fprintf(peci_file, "failed to dump %d %02x\n",
                cpld_table.cpld_list[index].bus, cpld_table.cpld_list[index].dev);
                continue;
        }
        while (fgets(dump_stream, sizeof(dump_stream) - 1, fp) != NULL) {
            fprintf(peci_file, "%s", dump_stream);
        }
        pclose(fp);
    }
    fprintf(peci_file, "\n");
    fflush(peci_file);
    fdatasync(fileno(peci_file));
}

static int get_value(const char *value_path, int mask)
{
    FILE* system_popen_fs = NULL;
    char value_stream[VALUE_STR_SIZE];
    int value;
    char* stop;

    if (value_path == NULL) {
        syslog(LOG_INFO, "error : value_path is null\n");
        return -1;
    }

    memset(value_stream, 0x00, sizeof(value_stream));

    system_popen_fs = popen(value_path, "r");
    if (system_popen_fs == NULL) {
        syslog(LOG_INFO, "error : popen (%s) fail\n", value_path);
        return -1;
    }

    if (fgets(value_stream, sizeof(value_stream), system_popen_fs) != NULL) {
        value = strtol(value_stream, &stop, 0) & mask;
    } else {
        syslog(LOG_INFO, "error : fgets %s fail\n", value_path);
        value = -1;
    }
    pclose(system_popen_fs);
    return value;
}

static bool ingore_cur_err2(void)
{
    int boot_status;
    int reset_status;

    boot_status = get_value(bios_boot_status_path, bios_boot_status_mask);
    if (boot_status != BOOT_ING) {
        syslog(LOG_DEBUG, "%s: non booting status", __func__);
        return false;
    }
    reset_status = get_value(cpu_reset_status_path, cpu_reset_status_mask);
    if (reset_status != WARM_RESET) {
        syslog(LOG_DEBUG, "%s: non WARM_RESET", __func__);
        return false;
    }
    if (!err2_caused_by_reboot()) {
        syslog(LOG_DEBUG, "%s: errors not caused by reboot", __func__);
        return false;
    }
    return true;
}

int main(int argc, char *argv[])
{
    int           mcefifo_fd             = 0;
    int           gpio_fd[GPIO_MAX_NUM] = {0};
    int           i                      = 0;
    int           ret                    = 0;
    char          buffer[GPIO_MAX_BUFFER_SIZE];
    int           read_len               = 0;
    long int      mcerr_count            = 0;
    long int      ierr_count             = 0;
    long int      err0_count             = 0;
    long int      err1_count             = 0;
    long int      err2_count             = 0;
    long int      msmierr_count          = 0;
    struct pollfd fds[FD_MAX_COUNT];

    /*initialization device info*/
    init_device_info();

    /*initialization mce info*/
    memset(fds, 0, sizeof(struct pollfd) * FD_MAX_COUNT);
    ret = access("/var/log", F_OK);
    if (ret == -1) {
        HOST_MCE_INFO_PATH = BACKUP_MCE_INFO_PATH;
        if (access("/tmp/mce", F_OK) == -1) {
            system("mkdir /tmp/mce");
        }

    } else {
        if (access("/var/log/mce", F_OK) == -1) {
            system("mkdir /var/log/mce");
        }

        if (access("/var/log/fw", F_OK) == -1) {
            system("mkdir /var/log/fw");
        }
    }

    if (access("/tmp/mcefifo", F_OK) == -1) {
        ret = mkfifo("/tmp/mcefifo", 0777);
        if (ret < 0) {
            syslog(LOG_INFO, "error : mkfifo /tmp/mcefifo fail\n");
            return -1 ;
        }
    }

    mcefifo_fd = open("/tmp/mcefifo", O_RDWR);
    if (mcefifo_fd == -1 ) {
        goto finish;
    } else {
        fds[0].fd     = mcefifo_fd;
        fds[0].events = POLLIN;
    }

    /*initialization gpio*/
    init_device_gpio(gpio_fd);

    /*initialization cpu err info*/
    exec_cpu_err_cmd(mcerr_count, CPU_MCE_PATH);
    exec_cpu_err_cmd(ierr_count, CPU_IERR_PATH);
    exec_cpu_err_cmd(err0_count, CPU_AER0_PATH);
    exec_cpu_err_cmd(err1_count, CPU_AER1_PATH);
    exec_cpu_err_cmd(err2_count, CPU_AER2_PATH);
    exec_cpu_err_cmd(msmierr_count, CPU_MSMI_PATH);


    for (i = 0; i < g_gpio_num; i++) {
        if (gpio_fd[i] < 0) {
            syslog(LOG_INFO, "open gpio_fd[%d] fail\n", i);
            goto finish;
        }
    }

    for (i = 0; i < g_gpio_num; i++) {
        fds[i + 1].fd      = gpio_fd[i];
        fds[i + 1].events  = POLLPRI;

        memset(buffer, 0, GPIO_MAX_BUFFER_SIZE);
        read(gpio_fd[i], buffer, 1);

        ret = lseek(gpio_fd[i], 0, SEEK_SET);
        if (ret == -1) {
            syslog(LOG_INFO, "lseek gpio %d error\n", i);
            goto finish;
        }
    }

    while (1) {
        memset(buffer, 0, sizeof(buffer));
        if (poll(fds, g_fd_num, -1) == -1) {
            syslog(LOG_INFO, "error : poll gpio fd fail\n");
            goto finish;
        }
        for (i = 0; i < g_fd_num; i++) {
            memset(buffer, 0, GPIO_MAX_BUFFER_SIZE);
            /* pull /tmp/mcefifo*/
            if ((i == MCE_FIFO) && (fds[i].revents & POLLIN)) {
                if ((read_len = read(fds[i].fd, buffer, sizeof(buffer))) == -1) {
                    syslog(LOG_INFO, "error : read fd[%d] fail\n", i);
                    goto finish;
                } else {
                    cpu_error_gpio_mce_info_pthread(i);
                }
                continue;
            }

            /*gpio75, IERR or MCERR*/
            if ((i == GPIO_75) && fds[i].revents & POLLPRI) {
                if ((read_len = read(fds[i].fd, buffer, sizeof(buffer))) == -1) {
                    syslog(LOG_INFO, "error : read fds[%d] fail\n", i);
                    goto finish;
                } else {
                    ret = lseek(fds[i].fd, 0, SEEK_SET);
                    if ( ret == -1) {
                        syslog(LOG_INFO, "error : lseek fds[%d] fail\n", i);
                        goto finish;
                    }
                }

                if (judgePowerOff() < 0 ) {
                    syslog(LOG_INFO, "does not record mce err(%s)\n", fd_name[i].gpio_name);
                    continue;
                }

                /*If gpio75 is low, IERR; else MCERR*/
                if (buffer[0] == '0') {                                         /*Low level, Express ierr event*/
                    ierr_count++;
                    exec_cpu_err_cmd(ierr_count, CPU_IERR_PATH);
                    fd_name[i].sig_index = 0;
                    syslog(LOG_CRIT, "CPU %s(%s) detected, total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                        fd_name[i].gpio_name, ierr_count);
                } else {                                                        /*High level, Express mcerr event*/
                    mcerr_count++;
                    exec_cpu_err_cmd(mcerr_count, CPU_MCE_PATH);
                    fd_name[i].sig_index = 1;
                    syslog(LOG_CRIT, "CPU %s(%s) detected, total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                        fd_name[i].gpio_name, mcerr_count);
                }
                cpu_error_gpio_mce_info_pthread(i);
                continue;
            }

            /*gpio76, MSMI_I*/
            if ((i == GPIO_76) && fds[i].revents & POLLPRI) {
                if ((read_len = read(fds[i].fd, buffer, sizeof(buffer))) == -1) {
                    syslog(LOG_INFO, "error : read fd[%d] fail\n", i);
                    goto finish;
                } else {
                    ret = lseek(fds[i].fd, 0, SEEK_SET);
                    if (ret == -1) {
                        syslog(LOG_INFO, "error : lseek fds[%d] fail\n", i);
                        goto finish;
                    }
                }
                if (judgePowerOff() < 0) {
                    syslog(LOG_INFO, "does not record mce err(%s)\n", fd_name[i].gpio_name);
                    continue;
                }
                msmierr_count++;
                exec_cpu_err_cmd(msmierr_count, CPU_MSMI_PATH);
                syslog(LOG_CRIT, "CPU %s(%s) detected, total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                    fd_name[i].gpio_name, msmierr_count);
                cpu_error_gpio_mce_info_pthread(i);
                continue;
            }

            /* Monitor gpio status, falling edge trigger
            *  gpio72: Hardware correctable error (no software action necessary)
            *  gpio73: Non-fatal error (OS or firmware action required to contain and recover)
            *  gpio74: Fatal error (system reset likely required to recover)
            */
            if (fds[i].revents & POLLPRI) {
                ret = lseek(gpio_fd[i - 1], 0, SEEK_SET);
                if (ret == -1) {
                    syslog(LOG_INFO, "lseek gpio_fd[%d] fail", i - 1);
                    goto finish;
                }

                if (judgePowerOff() < 0) {
                    if ((ret = read(gpio_fd[i-1], buffer, GPIO_MAX_BUFFER_SIZE)) < 0) {
                        syslog(LOG_INFO, "read gpio_fd[%d] fail", i - 1);
                        goto finish;
                    }
                    syslog(LOG_INFO, "does not record mce err(%s)\n", fd_name[i].gpio_name);
                    continue;
                }

                ret = read(gpio_fd[i - 1], buffer, GPIO_MAX_BUFFER_SIZE);
                if (ret == -1 ) {
                    syslog(LOG_INFO, "read gpio_fd[%d] fail", i - 1);
                    goto finish;
                }

                switch (i) {
                    case GPIO_72 :
                        err0_count++;
                        exec_cpu_err_cmd(err0_count, CPU_AER0_PATH);
                        syslog(LOG_ERR, "%s(%s) asserted, CPU hardware correctable error detected, "
                            "total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                            fd_name[i].gpio_name, err0_count);
                        break;
                    case GPIO_73 :
                        err1_count++;
                        exec_cpu_err_cmd(err1_count, CPU_AER1_PATH);
                        syslog(LOG_CRIT, "%s(%s) asserted, Non-fatal error detected, "
                            "total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                            fd_name[i].gpio_name, err1_count);
                        break;
                    case GPIO_74 :
                        if(g_handle_err2 && ingore_cur_err2()) {
                            syslog(LOG_INFO, "%s(%s) asserted, but can be ingored "
                                "because of CPU's WARM_RESET status\n",
                                fd_name[i].sig_arry[fd_name[i].sig_index], fd_name[i].gpio_name);
                            continue;
                        }
                        err2_count++;
                        exec_cpu_err_cmd(err2_count, CPU_AER2_PATH);
                        syslog(LOG_CRIT, "%s(%s) asserted, Fatal error detected, "
                            "total count is %d\n", fd_name[i].sig_arry[fd_name[i].sig_index],
                            fd_name[i].gpio_name, err2_count);
                        break;
                    default:
                        syslog(LOG_INFO, "unknow error");
                }
                cpu_error_gpio_mce_info_pthread(i);
            }/* End of if */
        }/* End of for */
    }/* End of while */

finish:
    if (mcefifo_fd > 0) {
        close(mcefifo_fd);
    }

    for (i = 0; i < g_gpio_num; i++) {
        if (gpio_fd[i] > 0) {
            close(gpio_fd[i]);
        }
    }

    return 0;
}
