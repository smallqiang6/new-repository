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
//#include <dal_rtl8373_port.h>
//#include <dal_rtl8373_drv.h>
#include <port.h>
#include <rtl8373_asicdrv.h>
#include <string.h>
#include <dal_mgmt.h>
#include <phy_rtl8224.h>

/* Function Name:
 *      rtk_port_phyReg_set
 * Description:
 *      Configure phy register data.
 * Input:
 *      phy_mask  - phy mask, bit[0:9]
 *      dev_addr   - device address
 *      reg_addr   - register address
 *      indata       - input data
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_QUEUE_NUM    - Invalid queue number.
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      This API will configure phy register data.
 */
rtk_api_ret_t rtk_port_phyReg_set(rtk_uint32 phy_mask, rtk_uint32 dev_addr, rtk_uint32 reg_addr, rtk_uint32 indata)
{
       rtk_api_ret_t retVal;
       
    if (NULL == RT_MAPPER->fMdrv_miim_mmd_write)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->fMdrv_miim_mmd_write(phy_mask,dev_addr,reg_addr,indata);
    RTK_API_UNLOCK();

    return retVal;

}

/* Function Name:
 *      rtk_port_phyReg_get
 * Description:
 *      Configure phy register data.
 * Input:
 *      phy_id  -  phy id
 *      dev_addr   - device address
 *      reg_addr   - register address
 *      indata       - input data
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_QUEUE_NUM    - Invalid queue number.
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      This API will configure phy register data.
 */
 
rtk_api_ret_t rtk_port_phyReg_get(rtk_uint32 phy_id, rtk_uint32 dev_addr, rtk_uint32 reg_addr, rtk_uint32 *pdata)
{
       rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->fMdrv_miim_mmd_read)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->fMdrv_miim_mmd_read(phy_id,dev_addr,reg_addr,pdata);
    RTK_API_UNLOCK();

    return retVal;

}

/* Function Name:
 *      rtk_port_phyReg_getBits
 * Description:
 *      Configure phy register data.
 * Input:
 *      phy_id - phy id
 *      dev_addr   - device address
 *      reg_addr   - register address
 *      indata       - input data
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_QUEUE_NUM    - Invalid queue number.
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      This API will configure phy register data.
 */
 
rtk_api_ret_t rtk_port_phyReg_getBits(rtk_uint32 phy_id, rtk_uint32 dev_addr, rtk_uint32 reg_addr,  rtk_uint32 bitsMask,rtk_uint32 *pdata)
{
    rtk_api_ret_t retVal;
    rtk_uint32 regData,regDatal,regDatah;
    rtk_uint32 bitsShift;
    
   if( !bitsMask )
        return RT_ERR_INPUT;

    bitsShift = 0;
    while(!(bitsMask & (1 << bitsShift)))
    {
        bitsShift++;
        if(bitsShift >= RTL8373_PHYBITLENGTH)
            return RT_ERR_INPUT;
    }

  if(dev_addr==RTL8224TOPDEVAD)
    {
          retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr,&regDatal);
          if(retVal != RT_ERR_OK)
             return RT_ERR_SMI;
          retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr+1,&regDatah);
          if(retVal != RT_ERR_OK)
             return RT_ERR_SMI;

          regData=regDatal|(regDatah<<16);
    }
  else
    {
        retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr,&regData);
        if(retVal != RT_ERR_OK)
            return RT_ERR_SMI;
    }
    *pdata = (regData & bitsMask) >> bitsShift;
    return retVal;
}

/* Function Name:
 *      rtk_port_phyReg_setBits
 * Description:
 *      Configure phy register data.
 * Input:
 *      phy_mask  - phy mask, bit[0:9]
 *      dev_addr   - device address
 *      reg_addr   - register address
 *      indata       - input data
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_QUEUE_NUM    - Invalid queue number.
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      This API will configure phy register data.
 */
 
rtk_api_ret_t rtk_port_phyReg_setBits(rtk_uint32 phy_mask, rtk_uint32 dev_addr, rtk_uint32 reg_addr,  rtk_uint32 bitsMask,rtk_uint32 indata)
{
   rtk_uint32 regDatah,regDatal,regData;
    rtk_api_ret_t retVal;
    rtk_uint32 bitsShift;
    rtk_uint32 valueShifted;
    rtk_uint32 phy_id;

    if( !bitsMask )
        return RT_ERR_INPUT;

    bitsShift = 0;
    while(!(bitsMask & (1 << bitsShift)))
    {
        bitsShift++;
        if(bitsShift >= RTL8373_REGBITLENGTH)
            return RT_ERR_INPUT;
    }
    valueShifted = indata << bitsShift;

    if(valueShifted > RTL8373_REGDATAMAX)
        return RT_ERR_INPUT;
    
    phy_id =0;
    if(dev_addr==RTL8224TOPDEVAD)
    {
        for(phy_id=0;phy_id<RTL8373_PORTIDMAX;phy_id++)
        {
            if((1<<phy_id)&phy_mask)
            {
                  retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr+1,&regDatah);
             if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;
                  retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr,&regDatal);
             if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;

            regData = regDatal|(regDatah<<16);
            regData = regData & (~bitsMask);
            regData = regData | (valueShifted & bitsMask);

            regDatah= regData>>16;
            regDatal = regData&0xffff;
            retVal = rtk_port_phyReg_set(1<<phy_id,dev_addr, reg_addr+1,regDatah);
            if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;
           retVal = rtk_port_phyReg_set(1<<phy_id,dev_addr, reg_addr,regDatal);
            if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;
            }
        }
    }
    else
    {
        for(phy_id=0;phy_id<RTL8373_PORTIDMAX;phy_id++)
        {
            if((1<<phy_id)&phy_mask)
            {
                  retVal = rtk_port_phyReg_get(phy_id,dev_addr, reg_addr,&regData);
             if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;
           
            regData = regData & (~bitsMask);
            regData = regData | (valueShifted & bitsMask);

            retVal = rtk_port_phyReg_set(1<<phy_id,dev_addr, reg_addr,regData);
            if(retVal != RT_ERR_OK)
                return RT_ERR_SMI;
            }
        }
    }
      
    return RT_ERR_OK;
}


/* Function Name:
 *      rtk_port_macForceLink_set
 * Description:
 *      Set port force linking configuration.
 * Input:
 *      port            - port id.
 *      pPortability    - port ability configuration
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 * Note:
 *      This API can set Port/MAC force mode properties.
 */
rtk_api_ret_t rtk_port_macForceLink_set(rtk_port_t port, rtk_port_ability_t *pPortability)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_macForceLink_set)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_macForceLink_set(port, pPortability);
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_port_macForceLink_get
 * Description:
 *      Get port force linking configuration.
 * Input:
 *      port - Port id.
 * Output:
 *      pPortability - port ability configuration
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      This API can get Port/MAC force mode properties.
 */
rtk_api_ret_t rtk_port_macForceLink_get(rtk_port_t port, rtk_port_ability_t *pPortability)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_macForceLink_get)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_macForceLink_get(port, pPortability);
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_port_macStatus_get
 * Description:
 *      Get port link status.
 * Input:
 *      port - Port id.
 * Output:
 *      pPortstatus - port ability configuration
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 * Note:
 *      This API can get Port/PHY properties.
 */
rtk_api_ret_t rtk_port_macStatus_get(rtk_port_t port, rtk_port_status_t *pPortstatus)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_macStatus_get)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_macStatus_get(port, pPortstatus);
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_port_macLocalLoopbackEnable_set
 * Description:
 *      Set Port Local Loopback. (Redirect TX to RX.)
 * Input:
 *      port    - Port id.
 *      enable  - Loopback state, 0:disable, 1:enable
 * Output:
 *      None.
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 * Note:
 *      This API can enable/disable Local loopback in MAC.
 *      For UTP port, This API will also enable the digital
 *      loopback bit in PHY register for sync of speed between
 *      PHY and MAC. For EXT port, users need to force the
 *      link state by themself.
 */
rtk_api_ret_t rtk_port_macLocalLoopbackEnable_set(rtk_port_t port, rtk_enable_t enable)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_macLocalLoopbackEnable_set)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_macLocalLoopbackEnable_set(port, enable);
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_port_macLocalLoopbackEnable_get
 * Description:
 *      Get Port Local Loopback. (Redirect TX to RX.)
 * Input:
 *      port    - Port id.
 * Output:
 *      pEnable  - Loopback state, 0:disable, 1:enable
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 * Note:
 *      None.
 */
rtk_api_ret_t rtk_port_macLocalLoopbackEnable_get(rtk_port_t port, rtk_enable_t *pEnable)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_macLocalLoopbackEnable_get)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_macLocalLoopbackEnable_get(port, pEnable);
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_port_backpressureEnable_set
 * Description:
 *      Set the half duplex backpressure enable status of the specific port.
 * Input:
 *      port    - port id.
 *      enable  - Back pressure status.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 *      RT_ERR_ENABLE       - Invalid enable input.
 * Note:
 *      This API can set the half duplex backpressure enable status of the specific port.
 *      The half duplex backpressure enable status of the port is as following:
 *      - DISABLE(Defer)
 *      - ENABLE (Backpressure)
 */
rtk_api_ret_t rtk_port_backpressureEnable_set(rtk_port_t port, rtk_enable_t enable)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_backpressureEnable_set)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_backpressureEnable_set(port, enable);
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_port_backpressureEnable_get
 * Description:
 *      Get the half duplex backpressure enable status of the specific port.
 * Input:
 *      port - Port id.
 * Output:
 *      pEnable - Back pressure status.
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_PORT_ID      - Invalid port number.
 * Note:
 *      This API can get the half duplex backpressure enable status of the specific port.
 *      The half duplex backpressure enable status of the port is as following:
 *      - DISABLE(Defer)
 *      - ENABLE (Backpressure)
 */
rtk_api_ret_t rtk_port_backpressureEnable_get(rtk_port_t port, rtk_enable_t *pEnable)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_backpressureEnable_get)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_backpressureEnable_get(port, pEnable);
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_port_rtctEnable_set
 * Description:
 *      Enable RTCT test
 * Input:
 *      portmask    - Port mask of RTCT enabled port
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK               - OK
 *      RT_ERR_FAILED           - Failed
 *      RT_ERR_SMI              - SMI access error
 *      RT_ERR_PORT_MASK        - Invalid port mask.
 * Note:
 *      The API can enable RTCT Test
 */
rtk_api_ret_t rtk_port_rtctEnable_set(rtk_uint32 portmask)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_rtct_start)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_rtct_start(portmask);
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_port_rtct_init
 * Description:
 *      Init RTCT test
 * Input:
 *      pPortmask    - Port mask of RTCT disabled port
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK               - OK
 *      RT_ERR_FAILED           - Failed
 *      RT_ERR_SMI              - SMI access error
 *      RT_ERR_PORT_MASK        - Invalid port mask.
 * Note:
 *      The API can disable RTCT Test
 */
rtk_api_ret_t rtk_port_rtct_init(void)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_rtct_init)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_rtct_init();
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_port_rtctResult_get
 * Description:
 *      Get the result of RTCT test
 * Input:
 *      port        - Port ID
 * Output:
 *      pRtctResult - The result of RTCT result
 * Return:
 *      RT_ERR_OK                   - OK
 *      RT_ERR_FAILED               - Failed
 *      RT_ERR_SMI                  - SMI access error
 *      RT_ERR_PORT_ID              - Invalid port ID.
 *      RT_ERR_PHY_RTCT_NOT_FINISH  - Testing does not finish.
 * Note:
 *      The API can get RTCT test result.
 *      RTCT test may takes 4.8 seconds to finish its test at most.
 *      Thus, if this API return RT_ERR_PHY_RTCT_NOT_FINISH or
 *      other error code, the result can not be referenced and
 *      user should call this API again until this API returns
 *      a RT_ERR_OK.
 *      The result is stored at pRtctResult->ge_result
 *      pRtctResult->linkType is unused.
 *      The unit of channel length is 2.5cm. Ex. 300 means 300 * 2.5 = 750cm = 7.5M
 */
rtk_api_ret_t rtk_port_rtctResult_get(rtk_port_t port, rtk_rtct_result_t *pRtctResult)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->port_rtctResult_get)
        return RT_ERR_DRIVER_NOT_FOUND;

    RTK_API_LOCK();
    retVal = RT_MAPPER->port_rtctResult_get(port, pRtctResult);
    RTK_API_UNLOCK();

    return retVal;
}




