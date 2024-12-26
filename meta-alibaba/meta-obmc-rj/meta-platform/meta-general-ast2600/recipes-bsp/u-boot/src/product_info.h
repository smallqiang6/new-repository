/*
 * Copyright 2016 IBM Corporation
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version
 * 2 of the License, or (at your option) any later version.
 */
#ifndef _PRODUCT_INFO_H
#define _PRODUCT_INFO_H
#include <platform_common_module.h>

eeprom_list_t g_eeprom_list[] = {
    { 2, 0x57, NOT_PCA9641, E2_TLV},
};

typedef enum card_type_e {
    AS15_24D8O_RJ = 0x40E7,
    AS15_40Q_RJ = 0x40E6,
    AS25_128Q_RJ = 0x408F,
} card_type_t;

dev_info_t g_dev_info_list[] = {
    {
       .dev_type   = AS25_128Q_RJ,
       .eth_prime = "eth3",
       .dev_name   = "AS25-128Q-RJ",
       .conffit_name = "AS25-128Q",
       .mac_addr_valid_flag = 0,
       .mac_increased = 1,
       .fru_mac_extra_index = 2,
    },
    {
       .dev_type   = AS15_24D8O_RJ,
       .eth_prime = "eth3",
       .dev_name   = "AS15-24D8O-RJ",
       .conffit_name = "AS15-24D8O",
       .mac_addr_valid_flag = 0,
       .mac_increased = 1,
       .fru_mac_extra_index = 2,
    },
    {
       .dev_type   = AS15_40Q_RJ,
       .eth_prime = "eth3",
       .dev_name   = "AS15-40Q-RJ",
       .conffit_name = "AS15-40Q",
       .mac_addr_valid_flag = 0,
       .mac_increased = 1,
       .fru_mac_extra_index = 2,
    }
};

#endif/* _PRODUCT_INFO_H */
