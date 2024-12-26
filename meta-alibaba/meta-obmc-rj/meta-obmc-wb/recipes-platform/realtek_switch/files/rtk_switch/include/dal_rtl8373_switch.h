/*
 * Copyright (C) 2012 Realtek Semiconductor Corp.
 * All Rights Reserved.
 *
 * This program is the proprietary software of Realtek Semiconductor
 * Corporation and/or its licensors, and only be used, duplicated,
 * modified or distributed under the authorized license from Realtek.
 *
 * ANY USE OF THE SOFTWARE OTHER THAN AS AUTHORIZED UNDER
 * THIS LICENSE OR COPYRIGHT LAW IS PROHIBITED.
 *
 * Purpose : Definition of Switch Global API
 *
 * Feature : The file have include the following module and sub-modules
 *           (1) Switch parameter settings
 *
 */

#ifndef __DAL_RTL8373_SWITCH_H__
#define __DAL_RTL8373_SWITCH_H__

/*
 * Include Files
 */
#include <rtk_types.h>
#include <rtk_switch.h>


typedef enum chip_mode_type_e
{
    CHIP_RTL8373_MODE,
    CHIP_RTL8372_MODE,
    CHIP_RTL8224_MODE,
    CHIP_MODE_END
}chip_mode_type_t;
/*
 * Symbol Definition
 */

typedef enum rtl8373_sds_mode_e 
{
    SERDES_10GQXG,
    SERDES_10GUSXG,
    SERDES_10GR,
    SERDES_HSG,
    SERDES_2500BASEX,
    SERDES_SG,
    SERDES_1000BASEX,
    SERDES_100FX,    
    SERDES_OFF,
    SERDES_END
    
}rtl8373_sds_mode_t;


/*
 * Data Declaration
 */

/*
 * Function Declaration
 */

/* Module Name    : Switch     */
/* Sub-module Name: Switch parameter settings */

/* Function Name:
 *      dal_rtl8373_switch_init
 * Description:
 *      Initialize switch module of the specified device.
 * Input:
 *      None
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK
 *      RT_ERR_FAILED
 * Note:
 *      Module must be initialized before using all of APIs in this module
 */
extern rtk_api_ret_t dal_rtl8373_switch_init(void);

extern rtk_api_ret_t serdes_patch (rtk_uint32 CHIP_MODE, rtk_uint32 SDS_INDX ,rtk_uint32 SDS_MODE);

extern rtk_api_ret_t fw_reset_flow_tgr(rtk_uint32 sdsid);

extern void uc1_sram_write_8b(rtk_uint32 port,rtk_uint32 addr,rtk_uint32 val);

extern rtk_uint32 uc1_sram_read_8b(rtk_uint32 port,rtk_uint32 addr);


#endif /* __DAL_RTL8373_SWITCH_H__ */
