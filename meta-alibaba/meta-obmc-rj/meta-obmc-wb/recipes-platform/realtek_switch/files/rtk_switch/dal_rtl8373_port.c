/*
 * Copyright (C) 2013 Realtek Semiconductor Corp.
 * All Rights Reserved.
 *
 * This program is the proprietary software of Realtek Semiconductor
 * Corporation and/or its licensors, and only be used, duplicated,
 * modified or distributed under the authorized license from Realtek.
 *
 * ANY USE OF THE SOFTWARE OTHER THAN AS AUTHORIZED UNDER
 * THIS LICENSE OR COPYRIGHT LAW IS PROHIBITED.
 *
 * $Revision$
 * $Date$
 *
 * Purpose : RTK switch high-level API for RTL8373
 * Feature : Here is a list of all functions and variables in port module.
 *
 */

#include <rtk_switch.h>
#include <rtk_error.h>
#include <dal_rtl8373_port.h>
#include <dal_rtl8373_switch.h>
#include <dal_rtl8373_drv.h>
#include <rtl8373_asicdrv.h>
#include <string.h>



rtk_uint16 rtl8373_rtct_patch[][2]=
{
    {0x81A3,0x2E},
    {0x81A4,0xE0},
    {0x81A5,0x2E},
    {0x81A6,0xE0},
    {0x81A8,0x1D},
    {0x81A9,0x00},
    {0x81AF,0x2D},
    {0x81B0,0x05},
    {0x81B2,0x09},
    {0x81B3,0x1F},
    {0x81BC,0x1D},
    {0x81BD,0x00},
    {0x81BE,0x00},
    {0x81BF,0xEA},
    {0x81C0,0x03},
    {0x81C1,0xCA},
    {0x81C2,0x1D},
    {0x81C3,0x00},
    {0x81C4,0x00},
    {0x81C5,0x3B},
    {0x81C6,0x00},
    {0x81C7,0x1A},
    {0x81C8,0x00},
    {0x81C9,0x54},
    {0x81CA,0xFF},
    {0x81CB,0xD5},
    {0x81CC,0x07},
    {0x81CD,0xFA},
    {0x81CE,0xFF},
    {0x81CF,0x14},
    {0x81D0,0x00},
    {0x81D1,0x74},
    {0x81D2,0xFF},
    {0x81D3,0xDB},
    {0x81D4,0x09},
    {0x81D5,0xF0},
    {0x81D6,0xFF},
    {0x81D7,0x97},
    {0x81D8,0xFF},
    {0x81D9,0xC2},
    {0x81DA,0x00},
    {0x81DB,0x28},
    {0x81DC,0xF1},
    {0x81DD,0xA0},
    {0x81DE,0x00},
    {0x81DF,0x94},
    {0x81E0,0x00},
    {0x81E1,0x76},
    {0x81E2,0xFF},
    {0x81E3,0xB8},
    {0x81E4,0xEA},
    {0x81E5,0xDD},
    {0x81E6,0x01},
    {0x81E7,0x6B},
    {0x81E8,0xFF},
    {0x81E9,0xAA},
    {0x81EA,0x00},
    {0x81EB,0x06},
    {0x81EC,0x05},
    {0x81ED,0x0A},
    {0x81EE,0xFF},
    {0x81EF,0x9D},
    {0x81F0,0x00},
    {0x81F1,0x10},
    {0x81F2,0x00},
    {0x81F3,0x05},
    {0x81F4,0x01},
    {0x81F5,0xE0},
    {0x81F6,0x00},
    {0x81F7,0x00},
    {0x81F8,0x00},
    {0x81F9,0x00},
    {0x81FA,0x00},
    {0x81FB,0x00},
};






static ret_t _rtl8373_portlink_get(rtk_uint32 port, rtk_uint32* link)
{
    rtk_uint32 regData = 0;
    ret_t retVal;

    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    *link = (regData >> port) & 1;
    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_portFrcAblitiy_set
 * Description:
 *      Set port force ability
 * Input:
 *      port     - 0 ~ 9
 *      ability    - link, speed, duplex, rxpause, txpause
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portFrcAbility_set(rtk_uint32 port, rtk_port_ability_t* ability)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;

    /*if port now is link up,  force linkdown first, then set other ability*/
    _rtl8373_portlink_get(port, &tmp);
    if(tmp == 1)
    {
        retVal = rtl8373_setAsicRegBit(RTL8373_MAC_FORCE_MODE_CTRL0_ADDR(port), RTL8373_MAC_FORCE_MODE_CTRL0_FORCE_LINK_EN_OFFSET, 0);
        if(retVal != RT_ERR_OK)
            return retVal;

        retVal = rtl8373_setAsicRegBit(RTL8373_MAC_FORCE_MODE_CTRL0_ADDR(port), RTL8373_MAC_FORCE_MODE_CTRL0_MAC_FORCE_EN_OFFSET, 1);
        if(retVal != RT_ERR_OK)
            return retVal;
    }
    

    regData = ability->forcemode & 1;
    regData |= (ability->link << 1);
    regData |= (ability->duplex << 2);
    regData |= ((ability->speed & 0xf) << 3);
    regData |= (ability->txpause << 7);
    regData |= (ability->rxpause << 8);

    return rtl8373_setAsicRegBits(RTL8373_MAC_FORCE_MODE_CTRL0_ADDR(port), 0x1ff, regData);
}


/* Function Name:
 *      dal_rtl8373_portFrcAblitiy_get
 * Description:
 *      Get port force ability
 * Input:
 *      port     - 0 ~ 9
 *      ability    - link, speed, duplex, rxpause, txpause
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portFrcAbility_get(rtk_uint32 port, rtk_port_ability_t* ability)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;

    retVal = rtl8373_getAsicRegBits(RTL8373_MAC_FORCE_MODE_CTRL0_ADDR(port), 0x1ff, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;
    
    ability->forcemode = regData & 1;
    ability->link = (regData >> 1) & 1;
    ability->duplex = (regData >> 2) & 1;
    ability->speed = (regData >> 3) & 0xf;
    ability->txpause = (regData >> 7) & 1;
    ability->rxpause = (regData >> 8) & 1;

    return RT_ERR_OK;
}



/* Function Name:
 *      dal_rtl8373_portStatus_get
 * Description:
 *      Get port status
 * Input:
 *      port     - 0 ~ 9
 *      ability    - link, speed, duplex, rxpause, txpause
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portStatus_get(rtk_uint32 port, rtk_port_status_t* status)
{
    rtk_uint32 regData = 0;
    ret_t retVal;
    /*link status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->link = (regData >> port) & 1;

    /*speed status*/
    retVal = rtl8373_getAsicRegBits(RTL8373_MAC_LINK_SPD_STS_ADDR(port), RTL8373_MAC_LINK_SPD_STS_SPD_STS_9_0_MASK(port), &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->speed= regData;

    /*duplex status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_DUP_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->duplex= (regData >> port) & 1;

    /*tx pause status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_TX_PAUSE_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->txpause= (regData >> port) & 1;

    /*rx pause status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_TX_PAUSE_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->rxpause= (regData >> port) & 1;

    /*media status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_LINK_MEDIA_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->media= (regData >> port) & 1;

    /*eee status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_EEE_ABLTY_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->eee= (regData >> port) & 1;

    /*master status*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_MSTR_SLV_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->master= (regData >> port) & 1;

    /*master slave nway*/
    retVal = rtl8373_getAsicReg(RTL8373_MAC_MSTR_SLV_FAULT_STS_ADDR, &regData);
    if(retVal != RT_ERR_OK)
        return retVal;

    status->master_slave= (regData >> port) & 1;


    return RT_ERR_OK;
    
}


/* Function Name:
 *      dal_rtl8373_portMaxLen_set
 * Description:
 *      Set port rx max length
 * Input:
 *      port     - 0 ~ 9
 *      type    - 0 FE:10M,100M,   1 giga:1G, 2.5G, 5G, 10G
 *      len      - max length
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portMaxLen_set(rtk_uint32 port, rtk_uint32 type, rtk_uint32 len)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;


    if(type == 0)
    {
        retVal = rtl8373_setAsicRegBits(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_100M_10M_SEL_MASK, len);
        if(retVal != RT_ERR_OK)
            return retVal;
    }
    else if(type == 1)
    {
        retVal = rtl8373_setAsicRegBits(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_1G_2P5G_5G_10G_SEL_MASK, len);
        if(retVal != RT_ERR_OK)
            return retVal;
    }
    else 
        return RT_ERR_INPUT;
    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_portMaxLen_get
 * Description:
 *      Get port rx max length
 * Input:
 *      port     - 0 ~ 9
 *      type    - 0 FE:10M,100M,   1 giga:1G, 2.5G, 5G, 10G
 *      pLen    - max length
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portMaxLen_get(rtk_uint32 port, rtk_uint32 type, rtk_uint32* pLen)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;


    if(type == 0)
    {
        retVal = rtl8373_getAsicRegBits(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_100M_10M_SEL_MASK, pLen);
        if(retVal != RT_ERR_OK)
            return retVal;
    }
    else if(type == 1)
    {
        retVal = rtl8373_getAsicRegBits(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_1G_2P5G_5G_10G_SEL_MASK, pLen);
        if(retVal != RT_ERR_OK)
            return retVal;
    }
    else 
        return RT_ERR_INPUT;
    
    return RT_ERR_OK;
}




/* Function Name:
 *      dal_rtl8373_portMaxLenIncTag_set
 * Description:
 *      Set port rx max length include tag length: cputag ctag, stag
 * Input:
 *      port     - 0 ~ 9
 *      enaleb  - 1: include tag length,   0: not include tag length
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portMaxLenIncTag_set(rtk_uint32 port, rtk_uint32 enable)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;


    return rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_TAG_INC_OFFSET, enable);

}


/* Function Name:
 *      dal_rtl8373_portMaxLenIncTag_get
 * Description:
 *      Get port rx max length include tag length: cputag ctag, stag
 * Input:
 *      port     - 0 ~ 9
 *      enaleb  - 1: include tag length,   0: not include tag length
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portMaxLenIncTag_get(rtk_uint32 port, rtk_uint32* pEnable)
{
    rtk_uint32 regData = 0;
    rtk_uint32 tmp;
    ret_t retVal;


    return rtl8373_getAsicRegBit(RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_MAX_LEN_CTRL_MAX_LEN_TAG_INC_OFFSET, pEnable);

}


/* Function Name:
 *      dal_rtl8373_portLoopbackEn_set
 * Description:
 *      Set port mac tx loopback to rx
 * Input:
 *      port     - 0 ~ 9
 *      enable    - 0 disable loopback,   1 enable loopback
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portLoopbackEn_set(rtk_uint32 port, rtk_enable_t enable)
{
    ret_t retVal;


    retVal = rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_CTRL_CFG_PORT_L_LPBK_OFFSET, enable);
    if(retVal != RT_ERR_OK)
        return retVal;

    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_portLoopbackEn_get
 * Description:
 *      Get port mac tx loopback to rx
 * Input:
 *      port     - 0 ~ 9
 *      pEnable    - 0 disable loopback,   1 enable loopback
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portLoopbackEn_get(rtk_uint32 port, rtk_enable_t * pEnable)
{
    ret_t retVal;


    retVal = rtl8373_getAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(port), RTL8373_MAC_L2_PORT_CTRL_CFG_PORT_L_LPBK_OFFSET, pEnable);
    if(retVal != RT_ERR_OK)
        return retVal;

    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_portBackpressureEn_set
 * Description:
 *      Set port half back pressure enable
 * Input:
 *      port     - 0 ~ 9
 *      enable    - 0 disable backpressure,   1 enable backpressure
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portBackpressureEn_set(rtk_uint32 port, rtk_enable_t enable)
{
    ret_t retVal;


    retVal = rtl8373_setAsicRegBit(RTL8373_MAC_PORT_CTRL_ADDR(port), RTL8373_MAC_PORT_CTRL_BKPRES_EN_OFFSET, enable);
    if(retVal != RT_ERR_OK)
        return retVal;

    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_portBackpressureEn_get
 * Description:
 *      Get port half back pressure enable
 * Input:
 *      port     - 0 ~ 9
 *      pEnable    - 0 disable backpressure,   1 enable backpressure
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_SMI      - SMI access error
 * Note:
 *      None
 */

ret_t dal_rtl8373_portBackpressureEn_get(rtk_uint32 port, rtk_enable_t * pEnable)
{
    ret_t retVal;


    retVal = rtl8373_getAsicRegBit(RTL8373_MAC_PORT_CTRL_ADDR(port), RTL8373_MAC_PORT_CTRL_BKPRES_EN_OFFSET, pEnable);
    if(retVal != RT_ERR_OK)
        return retVal;

    
    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_sdsMode_set
 * Description:
 *      Set sds mode
 * Input:
 *      sdsid     - 0 ~ 1
 *      mode  - 
 *      SERDES_10GQXG,
 *      SERDES_10GUSXG,
 *      SERDES_10GR,
 *      SERDES_HSG,
 *      SERDES_2500BASEX,
 *      SERDES_SG,
 *      SERDES_1000BASEX,
 *      SERDES_100FX,    
 *      SERDES_OFF, 
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_NOT_ALLOWED      - mode is not support
 * Note:
 *      None
 */

ret_t dal_rtl8373_sdsMode_set(rtk_uint32 sdsid, rtl8373_sds_mode_t mode)
{
    ret_t retVal;
    rtk_uint32 regdata, chiptype, i;

    if((retVal = rtl8373_getAsicReg(0x4, &regdata)) != RT_ERR_OK)
        return retVal;

    regdata = regdata >> 16;

    if(regdata == 0x8373)
    {
        if((sdsid == 0) && (mode != SERDES_10GQXG) && (mode != SERDES_OFF))
            return RT_ERR_NOT_ALLOWED;
        chiptype = CHIP_RTL8373_MODE;
    }
    else if (regdata == 0x8372)
        chiptype = CHIP_RTL8372_MODE;
    else if (regdata == 0x8224)
        chiptype = CHIP_RTL8224_MODE;
    

    if (mode == SERDES_10GQXG)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GQXG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GQXG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_USX_SUB_MODE_MASK, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD

        }    

    }
    else if (mode == SERDES_10GUSXG)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GUSXG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK, 0);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GUSXG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_USX_SUB_MODE_MASK, 0);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD

        }    

    }
    else if (mode == SERDES_10GR)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GR),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1A);//SDS0_MODE_SEL = 0x1A

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_10GR),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1A);//SDS0_MODE_SEL = 0x1A

        }    

    }
    else if (mode == SERDES_HSG)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_HSG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x12);//SDS0_MODE_SEL = 0x12

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_HSG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x12);//SDS0_MODE_SEL = 0x12

        }    

    }
    else if (mode == SERDES_2500BASEX)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_HSG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x16);//SDS0_MODE_SEL = 0x16

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_HSG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x16);//SDS0_MODE_SEL = 0x16

        }    

    }
    else if (mode == SERDES_SG)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x2);//SDS0_MODE_SEL = 0x2

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x2);//SDS0_MODE_SEL = 0x2

        }    

    }
    else if (mode == SERDES_1000BASEX)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x4);//SDS0_MODE_SEL = 0x4

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x4);//SDS0_MODE_SEL = 0x4

        }    

    }
    else if (mode == SERDES_100FX)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x5);//SDS0_MODE_SEL = 0x5

        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
            serdes_patch(chiptype,sdsid,SERDES_SG),
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x5);//SDS0_MODE_SEL = 0x5

        }    

    }
    else if (mode == SERDES_OFF)
    {
        if(sdsid == 0)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
        }
        else if (sdsid == 1)
        {
            rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
        }    

    }

    for (i = 0; i < 20000; i++)
        ;
    fw_reset_flow_tgr(sdsid);

    for (i = 0; i < 20000; i++)
        ;

    return RT_ERR_OK;

}


/* Function Name:
 *      dal_rtl8373_sdsMode_get
 * Description:
 *      Get sds mode
 * Input:
 *      sdsid     - 0 ~ 1
 *      pMode  - 
 *      SERDES_10GQXG,
 *      SERDES_10GUSXG,
 *      SERDES_10GR,
 *      SERDES_HSG,
 *      SERDES_2500BASEX,
 *      SERDES_SG,
 *      SERDES_1000BASEX,
 *      SERDES_100FX,    
 *      SERDES_OFF, 
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK         - Success
 *      RT_ERR_NOT_ALLOWED      - mode is not support
 * Note:
 *      None
 */

ret_t dal_rtl8373_sdsMode_get(rtk_uint32 sdsid, rtl8373_sds_mode_t * pMode)
{
    rtk_uint32 regdata, subtype;

    if(sdsid == 0)
    {
        rtl8373_getAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK,&regdata);
        rtl8373_getAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK,&subtype);
    }
    else if(sdsid == 1)
    {
        rtl8373_getAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_MODE_SEL_MASK,&regdata);
        rtl8373_getAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS1_USX_SUB_MODE_MASK,&subtype);
    }
    else RT_ERR_INPUT;

    if(regdata == 0xD)
    {
        /*USXG*/
        if(subtype == 0)
            *pMode = SERDES_10GUSXG;
        else if (subtype == 2)
            *pMode = SERDES_10GQXG;
        else
            return RT_ERR_FAILED;

    }
    else if (regdata == 0x1A)
        *pMode = SERDES_10GR;    
    else if (regdata == 0x12)
            *pMode = SERDES_HSG;
    else if (regdata == 0x16)
            *pMode = SERDES_2500BASEX;
    else if (regdata == 0x2)
            *pMode = SERDES_SG;
    else if (regdata == 0x4)
            *pMode = SERDES_1000BASEX;
    else if (regdata == 0x5)
            *pMode = SERDES_100FX;
    else if (regdata == 0x1F)
            *pMode = SERDES_OFF;

    return RT_ERR_OK;    
}


#if 1


/* Function Name:
 *      dal_rtl8373_rtct_init
 * Description:
 *      Init RTCT
 * Input:
 *      None.
 * Output:
 *      None.
 * Return:
 *      RT_ERR_OK           - Success
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_MASK    - Invalid port mask
 * Note:
 *      RTCT test takes 4.8 seconds at most.
 */

ret_t dal_rtl8373_rtct_init()
{
    ret_t retVal;
    rtk_uint32 phyid, len, regaddr, regdata, i;
    rtk_uint32 rg_dll_one_ch_en, pn_rate, rg_biquad_coef_sel, enlongpn, rg_rtct_hpf_coef_sel, reg_pnrate; 


    for(phyid = 4; phyid < 8; phyid++)
    {
        dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xa46a, 3, 0x1);
        dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xa422, 1, 0x0);
    }

    rg_dll_one_ch_en = 1;
    pn_rate = 1;
    rg_biquad_coef_sel = 0;
    enlongpn = 0;
    rg_rtct_hpf_coef_sel = 2;

    dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xc010, 1<<9, rg_dll_one_ch_en);
    dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xc010, 1<<10, pn_rate);
    dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xc010, 3<<13, rg_biquad_coef_sel);
    dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xc000, 1<<0, enlongpn);
    dal_rtl8373_phy_regbits_write(1<<phyid, 31, 0xc020, 7<<1, rg_rtct_hpf_coef_sel);


    dal_rtl8373_phy_regbits_read(1<<phyid, 31, 0xc010, 1<<10, &reg_pnrate);

    len= sizeof(rtl8373_rtct_patch)/4;

    for(i=0;i<len;i++)
    {
        regaddr=rtl8373_rtct_patch[i][0];
        regdata=rtl8373_rtct_patch[i][1];        
        uc1_sram_write_8b(phyid,regaddr,regdata);    
                            
    }
    

}



/* Function Name:
 *      dal_rtl8373_rtct_start
 * Description:
 *      Set RTCT start
 * Input:
 *      portmask    - Port mask of RTCT enabled (4 - 7)
 * Output:
 *      None.
 * Return:
 *      RT_ERR_OK           - Success
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_MASK    - Invalid port mask
 * Note:
 *      RTCT test takes 4.8 seconds at most.
 */
ret_t dal_rtl8373_rtct_start(rtk_uint32 phymask)
{
    ret_t       retVal;
    rtk_uint32  regData;
    rtk_uint32  port, i, rtct_done, count;

    for(port = 0; port <= 8 ; port++)
    {
        if(phymask & (0x0001 << port))
        {
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa400, 1 << 9, 1);

            for(i=0; i<10000; i++);

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa422, 1 << 1, 1);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa400, 1 << 15, 0);
             
            dal_rtl8373_phy_regbits_read(1<<port, 31, 0xa400, 1 << 15, &rtct_done);
            if(rtct_done != 0)
                return RT_ERR_FAILED;

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa422, 0xf << 4, 0xf);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa422, 1, 1);

            count = 1000;
            do
            {
                dal_rtl8373_phy_regbits_read(1<<port, 31, 0xa400, 1 << 15, &rtct_done);
                count--;
                if (count == 0)
                    break;
            }while(rtct_done!=1);

            if(count == 0)
                return RT_ERR_BUSYWAIT_TIMEOUT;
        }
        return RT_ERR_OK;
    }

    return RT_ERR_OK;
}


/* Function Name:
 *      dal_rtl8373_rtct_status_get
 * Description:
 *      Get RTCT result
 * Input:
 *      phyid    - Port id of RTCT result (4 - 7)
 *      pResult  - result of RTCT
 * Output:
 *      None.
 * Return:
 *      RT_ERR_OK           - Success
 *      RT_ERR_SMI          - SMI access error
 * Note:
 *      RTCT test takes 4.8 seconds at most.
 */
ret_t dal_rtl8373_rtct_status_get(rtk_uint32 phyid, rtk_rtct_result_t * pResult)
{
	ret_t       retVal;
    rtk_uint32  channalA, channalB, channalC, channalD;

	if(pResult == NULL)
		return RT_ERR_NULL_POINTER;

	channalA = uc1_sram_read_8b(phyid, 0x8026);
	channalB = uc1_sram_read_8b(phyid, 0x802A);
	channalC = uc1_sram_read_8b(phyid, 0x802E);
	channalD = uc1_sram_read_8b(phyid, 0x8032);

	pResult->channelABusy = channalA & 1;
	pResult->channelAMisOpen = (channalA >> 1) & 1;
	pResult->channelAMisShort = (channalA >> 2) & 1;
	pResult->channelAOpen = (channalA >> 3) & 1;
	pResult->channelAShort = (channalA >> 4) & 1;
	pResult->channelANormal = (channalA >> 5) & 1;
	pResult->channelADone = (channalA >> 6) & 1;
	pResult->channelAInterShort = (channalA >> 7) & 1;

	pResult->channelBBusy = channalB & 1;
	pResult->channelBMisOpen = (channalB >> 1) & 1;
	pResult->channelBMisShort = (channalB >> 2) & 1;
	pResult->channelBOpen = (channalB >> 3) & 1;
	pResult->channelBShort = (channalB >> 4) & 1;
	pResult->channelBNormal = (channalB >> 5) & 1;
	pResult->channelBDone = (channalB >> 6) & 1;
	pResult->channelBInterShort = (channalB >> 7) & 1;

	pResult->channelCBusy = channalC & 1;
	pResult->channelCMisOpen = (channalC >> 1) & 1;
	pResult->channelCMisShort = (channalC >> 2) & 1;
	pResult->channelCOpen = (channalC >> 3) & 1;
	pResult->channelCShort = (channalC >> 4) & 1;
	pResult->channelCNormal = (channalC >> 5) & 1;
	pResult->channelCDone = (channalC >> 6) & 1;
	pResult->channelCInterShort = (channalC >> 7) & 1;

	pResult->channelDBusy = channalD & 1;
	pResult->channelDMisOpen = (channalD >> 1) & 1;
	pResult->channelDMisShort = (channalD >> 2) & 1;
	pResult->channelDOpen = (channalD >> 3) & 1;
	pResult->channelDShort = (channalD >> 4) & 1;
	pResult->channelDNormal = (channalD >> 5) & 1;
	pResult->channelDDone = (channalD >> 6) & 1;
	pResult->channelDInterShort = (channalD >> 7) & 1;

	return RT_ERR_OK;

}



#endif




