/**
 * Copyright(C) 2018 Ruijie Network. All rights reserved.
 */
/*
 * cpu_peci-space.c
 * Original Author : fuguangchao@ruijie.com.cn, 2018-08-31
 *
 * del cpu_rror_gpio interrupt 
 *
 * History
 *    v1.0    fuguangchao@ruijie.com.cn  2018-08-31  Initial version.
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
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <dirent.h>

#include "cpu-peci-space.h"
static int g_beg_addr = 0;
static int g_end_addr = 0;
void host_peci_RdPCIConfigLocal_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, struct addr_msg *msg_addr)
{
    memset(msg, 0, sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x05;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0xe1; /* cmd */
    msg->tx_buf[1] = 0x00; /* Device Info */
    msg->tx_buf[2] = data1; 
    msg->tx_buf[3] = data2; 
    msg->tx_buf[4] = msg_addr->bus_addr; 
}

void host_peci_RdPCIConfig_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, struct addr_msg *msg_addr)
{
    memset(msg, 0, sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x06;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0x61; /* cmd */
    msg->tx_buf[1] = 0x00; /* Device Info */
    msg->tx_buf[2] = data1; 
    msg->tx_buf[3] = data2; 
    msg->tx_buf[4] = msg_addr->bus_addr;
    msg->tx_buf[5] = msg_addr->reserved_addr;
}

void host_peci_RdEndpoint_lpci_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, struct addr_msg *msg_addr)
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
    msg->tx_buf[10] = msg_addr->bus_addr;
    msg->tx_buf[11] = msg_addr->reserved_addr;
}

void host_peci_RdEndpoint_pci_init(struct xfer_msg *msg, unsigned char data1, unsigned char data2, struct addr_msg *msg_addr)
{
    int i;
    memset(msg, 0, sizeof(struct xfer_msg));
    msg->client_addr = 0x30;
    msg->tx_len = 0x0c;
    msg->rx_len = 0x05;
    msg->tx_buf[0] = 0xc1; /* cmd */
    msg->tx_buf[1] = 0x00; /* Device Info */
    msg->tx_buf[2] = 0x04; /* mess type */
    msg->tx_buf[3] = 0x00; /* endpoint id */
    msg->tx_buf[4] = 0x00; /* RSVD */
    msg->tx_buf[5] = 0x00; /* RSVD */
    msg->tx_buf[6] = 0x04; /* Address type */
    msg->tx_buf[7] = 0x00; /* segment 给多个cpu使用，soc segment为 0*/
    msg->tx_buf[8] = data1; 
    msg->tx_buf[9] = data2; 
    msg->tx_buf[10] = msg_addr->bus_addr;
    msg->tx_buf[11] = msg_addr->reserved_addr;
}

void host_read_peci_content(struct addr_msg *msg_addr)
{
    int offset                = 0;
    int i                     = 0;
    int count                 = 0;
    int read_tag              = 0;
    int ret                   = 0;
    unsigned char addr_fun    = 0;
    unsigned char addr_offset = 0;
    struct xfer_msg *msg_peci = NULL;

    msg_peci = malloc(sizeof(struct xfer_msg));
    if (msg_peci == NULL) {
        printf("cpu_error_gpio error: malloc xfer_msg failed\n");
        return ;
    }
    for (count = 0; count < RETRY_READ_PECI_TIMES; count ++) { /* retry 3 times */
        if (read_tag == 1) {
            break;
        }
        for (offset = g_beg_addr; offset < g_end_addr; offset = offset + READ_PECI_PER_LENGTH) {
            addr_offset = ((msg_addr->function_addr + offset) & 0xff); //low 
            addr_fun = (((msg_addr->function_addr + offset) >> FUNCTION_ADDR_OFFSET) & 0xff); // high

            if (msg_addr->extra_flag == 1) {
                host_peci_RdPCIConfig_init(msg_peci, addr_offset, addr_fun, msg_addr);
            } else if (msg_addr->extra_flag == 2) {/*endppoint_lpci*/
                host_peci_RdEndpoint_lpci_init(msg_peci, addr_offset, addr_fun, msg_addr);
            } else if (msg_addr->extra_flag == 3) {/*endppoint_pci*/
                host_peci_RdEndpoint_pci_init(msg_peci, addr_offset, addr_fun, msg_addr);
            } else {
                host_peci_RdPCIConfigLocal_init(msg_peci, addr_offset, addr_fun, msg_addr);
            }
            ret = ioctl(msg_addr->file_fd, AST_PECI_IOCXFER, msg_peci);
            if (ret < 0) {
                printf("cpu_error_gpio error: Open Machine Check Bank Sequence failed, ret = %d\n", ret);
            }
            
            if (count < (RETRY_READ_PECI_TIMES - 1)) {
                if (msg_peci->rx_buf[0] != COMPLETION_CODE && offset == 0) {
                    usleep(USLEEP_TIME);
                    printf("read peci space retry %d times failed \n", count + 1);
                    break;
                }
            }
            read_tag = 1;
            if (offset == 0) {
                printf("read peci space retry %d times\n", count + 1);
                printf("%02x: ", offset);
            } else if ((offset % ADECIMAL_VALUE) == 0) {
                printf("\n");
                printf("%02x: ", (offset/ADECIMAL_VALUE));
            }

            for (i = 0; i <= READ_PECI_PER_LENGTH ; i++) {
                printf("%02x ",  msg_peci->rx_buf[i]);
            } 
        }
    }
    printf("\n");
    free(msg_peci);
}

void usage(char *command)
{
    printf("   usage : %s Bus Device Function beg_addr end_addr\n", command);
    printf("   extra : read extra register\n");
    printf("   endpoint_lpcicfg : read endpoint local pci config\n");
    printf("   endpoint_pcicfg : read endpoint pci config\n");
}

/*
 * PCI Configuration Address has three parts
 * Bus 4 Bits 20-23
 * Device 5 Bits 15-19
 * Function 3 Bits 12-14
 * Register 12 Bits 0-11
 ****************************
 * PCI Configuration extra Address has four parts
 * Reserved 4 Bits 28-31
 * Bus 8 Bits 20-27
 * Device 5 Bits 15-19
 * Function 3 Bits 12-14
 * Register 12 Bits 0-11
 */
void addr_translation(struct addr_msg *msg_addr, char* param_one, char* param_two, char *param_three)
{
    char *ptr;
    int bus_base_addr             = 0; /* bus */
    int device_base_addr          = 0; /* device */
    int function_base_addr        = 0; /* function */
    unsigned char addr_trans      = 0;
    unsigned char reserved_addr   = 0xf0;
    bus_base_addr = strtol(param_one, &ptr, ADECIMAL_VALUE);
    if (bus_base_addr > BUS_MAX_VALUE) {
        if (msg_addr->extra_flag == 0) {
            bus_base_addr = 1;
        }
    }
    device_base_addr = strtol(param_two, &ptr, ADECIMAL_VALUE);
    function_base_addr = strtol(param_three, &ptr, ADECIMAL_VALUE);
    msg_addr->reserved_addr = reserved_addr + (bus_base_addr >> READ_PECI_PER_LENGTH);
    msg_addr->bus_addr = (bus_base_addr << READ_PECI_PER_LENGTH) + (device_base_addr >> 1);
    addr_trans = (device_base_addr << RETRY_READ_PECI_TIMES) + function_base_addr;
    msg_addr->function_addr = addr_trans << OFFSET_VALUE;

    host_read_peci_content(msg_addr);
}


int main(int argc, char *argv[])
{
    struct addr_msg *msg_addr = NULL;
    int    file_fd            = 0;
    msg_addr = malloc(sizeof(struct addr_msg));
    if (msg_addr == NULL) {
        printf("error: malloc xfer_msg failed\n");
        exit(0);
    }
    if (argc < ARGC_PARAMETER || argc > (ARGC_PARAMETER + 1)) {
        goto error;
    }

    memset(msg_addr, 0, sizeof(struct addr_msg));

    if ((file_fd = open(PECI_DEVICE, O_RDWR, S_IRWXU | S_IRWXG | S_IRWXO | S_IRUSR | S_IWUSR)) < 0) {
        printf("cpu_error_gpio error: Could not open file /dev/aspeed-peci\n");
        goto error;
    }

    msg_addr->file_fd = file_fd;
    if (argc == (ARGC_PARAMETER + 1)) {
        if (strcmp(argv[ARGC_PARAMETER], "extra") == 0) {
            msg_addr->extra_flag = 1;
        } else if (strcmp(argv[ARGC_PARAMETER], "endpoint_lpcicfg") == 0) {
            msg_addr->extra_flag = 2;
        } else if (strcmp(argv[ARGC_PARAMETER], "endpoint_pcicfg") == 0) {
            msg_addr->extra_flag = 3;
        }else {
            close(file_fd);
            goto error;
        }

    }
    char *ptr;
    g_beg_addr= strtol(argv[4], &ptr, ADECIMAL_VALUE);
    g_end_addr= strtol(argv[5], &ptr, ADECIMAL_VALUE);
    addr_translation(msg_addr, argv[1], argv[2], argv[3]);
    free(msg_addr);
    close(file_fd);
    return 0;
error:
    printf("parameter error\n");
    usage(argv[0]);
    free(msg_addr);
    exit(0);
}

