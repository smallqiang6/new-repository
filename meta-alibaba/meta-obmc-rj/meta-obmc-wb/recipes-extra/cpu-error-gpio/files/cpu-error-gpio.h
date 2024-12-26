#ifndef __CPU_ERROR_GPIO_H__
#define __CPU_ERROR_GPIO_H__

#include <sys/ioctl.h>
#include <inttypes.h>
#include <sys/types.h>

# define REG_ATTR_SIZE  32
#define TABLE_SIZE(table, type) (sizeof(table)/sizeof(type))

struct xfer_msg {
    unsigned char    client_addr;
    unsigned char    tx_len;
    unsigned char    rx_len;
    unsigned char    tx_fcs;
    unsigned char    rx_fcs;
    unsigned char    fcs_en;
    unsigned char    sw_fcs;
    unsigned char    tx_buf[32];
    unsigned char    rx_buf[32];
    unsigned int     sts;
};

typedef struct reg_info {
    int    beg_addr;                      /* start address */
    char reg_attr[REG_ATTR_SIZE];         /* reg name attr */
}REG_INFO;

typedef struct iio_peci_msg {
    uint16_t  addr_base;     /* function and device address */
    unsigned  char adrr_bus; /* bus address */
    REG_INFO* peci_reg_info;
    int       cnt;           /* reg_info num */
}IIO_PECI_MSG;

typedef struct {
    uint8_t  bus;
    uint8_t  dev;
} cpld_addr_t;

typedef struct {
    cpld_addr_t *cpld_list;
    uint8_t cpld_num;
} cpld_table_t;

typedef struct {
    int beg_addr;
    int end_addr;
} ieh_offset_table_t;

typedef struct {
    uint8_t function;
    ieh_offset_table_t *ieh_offset_table;
    int table_size;
} ieh_function_table_t;

typedef struct {
    uint8_t device;
    ieh_function_table_t *ieh_func_table;
    int table_size;
} ieh_device_table_t;

typedef struct {
    uint8_t bus;
    ieh_device_table_t *ieh_device_table;
    int table_size;
} ieh_bus_table_t;

typedef struct {
    char *gpio_name;
    uint8_t sig_index;
    char **sig_arry;
} sig_map_t;

#define PECI_DEVICE "/dev/aspeed-peci"
#define PECIIOC_BASE 'P'
#define AST_PECI_IOCXFER    _IOWR(PECIIOC_BASE, 2, struct xfer_msg*)

#endif /* End of __CPU_ERROR_GPIO_H__ */

