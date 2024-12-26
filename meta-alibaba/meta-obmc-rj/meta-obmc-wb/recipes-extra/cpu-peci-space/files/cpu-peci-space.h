#ifndef __CPU_ERROR_GPIO_H__
#define __CPU_ERROR_GPIO_H__

#include <sys/ioctl.h>
#include <inttypes.h>
#include <sys/types.h>

#define ADECIMAL_VALUE        16  /* hexadecimal */
#define OFFSET_VALUE          12  /* offset 12 */
#define BUS_MAX_VALUE         15  /* The maximum of bus is 15*/
#define COMPLETION_CODE       64  /* Completion Code 0X40 */
#define BUFFER_MAX_SIZE       32
#define RETRY_READ_PECI_TIMES 3   /* retry read peci times */
#define READ_PECI_PER_LENGTH  4   /* read peci(dword)  */
#define FUNCTION_ADDR_OFFSET  8
#define ARGC_PARAMETER        6
#define USLEEP_TIME           10000

struct xfer_msg {
    unsigned char    client_addr;
    unsigned char    tx_len;
    unsigned char    rx_len;
    unsigned char    tx_fcs;
    unsigned char    rx_fcs;
    unsigned char    fcs_en;
    unsigned char    sw_fcs;
    unsigned char    tx_buf[BUFFER_MAX_SIZE];
    unsigned char    rx_buf[BUFFER_MAX_SIZE];
    unsigned int     sts;
};

struct addr_msg {
    unsigned char    bus_addr;
    unsigned char    reserved_addr;
    uint16_t         function_addr;
    int              extra_flag; /* extra_flag = 1 read extra register */
    int              file_fd;
    int              read_num;
};

#define PECI_DEVICE "/dev/aspeed-peci"
#define PECIIOC_BASE 'P'
#define AST_PECI_IOCXFER    _IOWR(PECIIOC_BASE, 2, struct xfer_msg*)

#endif /* End of __CPU_ERROR_GPIO_H__ */

