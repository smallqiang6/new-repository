#ifndef __MDIO_BASE_H__
#define __MDIO_BASE_H__
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdlib.h>
#include <syslog.h>
#include <sys/types.h>
#include <string.h>

#define PHYTOOL_DEBUG_FILE           "/.smitool_flag"
#define DEBUG_INFO_LEN               (20)
#define DEBUG_ON_ERROR               "2"
#define DEBUG_ON_INFO                "1"
#define DEBUG_OFF_INFO               "0"
#define DBG_INFO                     (1)
#define DBG_ERROR                    (2)

/* IOCTL CMD */
#define MDIO_MAGIC                              'M'
#define MDIO_READ                               _IO(MDIO_MAGIC, 0)
#define MDIO_WRITE                              _IO(MDIO_MAGIC, 1)
#define MDIO_READ_OP                            (0)
#define MDIO_WRITE_OP                           (1)

int debuglevel;

#define MSD_DBG_ERROR(fmt, arg...)  do { \
    if ( debuglevel >= DBG_ERROR) {  \
        printf("[ERROR]:<%s, %d>:"fmt, __FUNCTION__, __LINE__, ##arg); \
    } \
} while (0)

#define MSD_DBG_INFO(fmt, arg...)  do { \
    if ( debuglevel >= DBG_INFO) {  \
        printf("[ERROR]:<%s, %d>:"fmt, __FUNCTION__, __LINE__, ##arg); \
    } \
} while (0)

struct mdio_arg {
    int addr;
    int reg;
    unsigned int value;
};

int ast_mdiobus_read(int addr, int reg);
int ast_mdiobus_write(int addr, int reg, unsigned int value);
int open_fd(void);
void close_fd(void);
void mdio_debug(void);
#endif /* End of __MDIO_BASE_H__ */