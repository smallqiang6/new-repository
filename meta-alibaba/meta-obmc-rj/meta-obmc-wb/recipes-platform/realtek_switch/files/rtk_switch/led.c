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
 * Feature : Here is a list of all functions and variables in LED module.
 *
 */

#include <rtk_switch.h>
#include <rtk_error.h>
#include <led.h>
#include <string.h>
#include <dal_mgmt.h>



/* Function Name:
 *      rtk_led_blinkRate_set
 * Description:
 *      Set LED blinking rate
 * Input:
 *      blinkRate - blinking rate.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      ASIC support 6 types of LED blinking rates at 32ms, 64ms, 128ms, 256ms, 512ms and 1024ms.
 */
rtk_api_ret_t rtk_led_blinkRate_set(rtk_led_blink_rate_t blinkRate)
{
     rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->led_blinkRate_set)
        return RT_ERR_DRIVER_NOT_FOUND;
    
    RTK_API_LOCK();
    retVal = RT_MAPPER->led_blinkRate_set(blinkRate);    
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_led_blinkRate_get
 * Description:
 *      Get LED blinking rate at mode 0 to mode 3
 * Input:
 *      None
 * Output:
 *      pBlinkRate - blinking rate.
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      There are  6 types of LED blinking rates at32ms, 64ms, 128ms, 256ms, 512ms and 1024ms.
 */
rtk_api_ret_t rtk_led_blinkRate_get(rtk_led_blink_rate_t *pBlinkRate)
{
     rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->led_blinkRate_get)
        return RT_ERR_DRIVER_NOT_FOUND;
    
    RTK_API_LOCK();
    retVal = RT_MAPPER->led_blinkRate_get(pBlinkRate);    
    RTK_API_UNLOCK();

    return retVal;
}

/* Function Name:
 *      rtk_led_groupConfig_set
 * Description:
 *      Set per group Led to congiuration mode
 * Input:
 *      group   - LED group.
 *      config  - LED configuration
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      The API can set LED indicated information configuration for each LED group with 1 to 1 led mapping to each port.
 *      - Definition  LED Statuses      Description
 *      - 0000        LED_Off           LED pin Tri-State.
 *      - 0001        Dup/Col           Collision, Full duplex Indicator.
 *      - 0010        Link/Act          Link, Activity Indicator.
 *      - 0011        Spd1000           1000Mb/s Speed Indicator.
 *      - 0100        Spd100            100Mb/s Speed Indicator.
 *      - 0101        Spd10             10Mb/s Speed Indicator.
 *      - 0110        Spd1000/Act       1000Mb/s Speed/Activity Indicator.
 *      - 0111        Spd100/Act        100Mb/s Speed/Activity Indicator.
 *      - 1000        Spd10/Act         10Mb/s Speed/Activity Indicator.
 *      - 1001        Spd100 (10)/Act   10/100Mb/s Speed/Activity Indicator.
 *      - 1010        LoopDetect        LoopDetect Indicator.
 *      - 1011        EEE               EEE Indicator.
 *      - 1100        Link/Rx           Link, Activity Indicator.
 *      - 1101        Link/Tx           Link, Activity Indicator.
 *      - 1110        Master            Link on Master Indicator.
 *      - 1111        Act               Activity Indicator. Low for link established.
 */
rtk_api_ret_t rtk_led_groupConfig_set(rtk_led_set_t setid, rtk_uint32 ledid, rtk_led_config_t * config)
{
    rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->led_groupConfig_set)
        return RT_ERR_DRIVER_NOT_FOUND;
    
    RTK_API_LOCK();
    retVal = RT_MAPPER->led_groupConfig_set(setid, ledid, config);    
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_led_portSelConfig_set
 * Description:
 *      Set led group connfig for per port
 * Input:
 *      port   - port id 0 ~ 8
 *      setid  - led config group id 0 ~ 3 
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      ASIC support 6 types of LED blinking rates at 32ms, 64ms, 128ms, 256ms, 512ms and 1024ms.
 */
rtk_api_ret_t rtk_led_portSelConfig_set(rtk_port_t port, rtk_led_set_t setid)
{
     rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->led_portSelConfig_set)
        return RT_ERR_DRIVER_NOT_FOUND;
    
    RTK_API_LOCK();
    retVal = RT_MAPPER->led_portSelConfig_set(port, setid);    
    RTK_API_UNLOCK();

    return retVal;
}


/* Function Name:
 *      rtk_led_portSelConfig_get
 * Description:
 *      Get led group connfig for per port
 * Input:
 *      port   - port id 0 ~ 8
 *      setid  - led config group id 0 ~ 3 
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      ASIC support 6 types of LED blinking rates at 32ms, 64ms, 128ms, 256ms, 512ms and 1024ms.
 */
rtk_api_ret_t rtk_led_portSelConfig_get(rtk_port_t port, rtk_led_set_t * setid)
{
     rtk_api_ret_t retVal;

    if (NULL == RT_MAPPER->led_portSelConfig_get)
        return RT_ERR_DRIVER_NOT_FOUND;
    
    RTK_API_LOCK();
    retVal = RT_MAPPER->led_portSelConfig_get(port, setid);    
    RTK_API_UNLOCK();

    return retVal;
}

