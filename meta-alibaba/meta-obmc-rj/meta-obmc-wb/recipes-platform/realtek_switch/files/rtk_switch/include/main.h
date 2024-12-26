#ifndef __MAIN_H__
#define __MAIN_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "rtk_types.h"

typedef struct _i2c_info_t {
    rtk_uint8 bus;
    rtk_uint8 addr;
} i2c_info_t;

extern int fd;
extern i2c_info_t rtk_i2c_info;

#ifdef __cplusplus
}
#endif

#endif
