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
 * Purpose : RTL8373 switch high-level API
 *
 * Feature : The file includes Interrupt module high-layer API defination
 *
 */

#ifndef __RTK_API_INTERRUPT_H__
#define __RTK_API_INTERRUPT_H__


/*
 * Data Type Declaration
 */


typedef enum rtk_int_type_e
{
    INT_TYPE_LINK_CHANGE = 0,
    INT_TYPE_GPHY,
    INT_TYPE_LEARN_OVER,
    INT_TYPE_RLFD,
    INT_TYPE_WOL,
    INT_TYPE_SDS_LINK_FAULT,
    INT_TYPE_SDS_UPDATE_PHY,
    INT_TYPE_END
}rtk_int_type_t;

typedef enum rtk_int_cpu_e
{
    INT_CPU_INTERNAL = 0,
    INT_CPU_EXTERNAL,
    INT_CPU_END
}rtk_int_cpu_t;



typedef enum rtk_int_polarity_e
{
    INT_POLAR_HIGH = 0,
    INT_POLAR_LOW,
    INT_POSITIVE_PULSE,
    INT_NEGATIVE_PULSE,
    INT_POLAR_END
} rtk_int_polarity_t;

/* Function Name:
 *      rtk_int_enable
 * Description:
 *      Enable interrupt function.
 * Input:
 *      enable - 0 disable, 1 enable.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      The API can set interrupt polarity configuration.
 */
extern rtk_api_ret_t rtk_int_enable(rtk_enable_t enable);



/* Function Name:
 *      rtk_int_polarity_set
 * Description:
 *      Set interrupt polarity configuration.
 * Input:
 *      type - Interruptpolarity type.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 * Note:
 *      The API can set interrupt polarity configuration.
 */
extern rtk_api_ret_t rtk_int_polarity_set(rtk_int_polarity_t type);

/* Function Name:
 *      rtk_int_polarity_get
 * Description:
 *      Get interrupt polarity configuration.
 * Input:
 *      None
 * Output:
 *      pType - Interruptpolarity type.
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 * Note:
 *      The API can get interrupt polarity configuration.
 */
extern rtk_api_ret_t rtk_int_polarity_get(rtk_int_polarity_t *pType);

/* Function Name:
 *      rtk_portInt_control_set
 * Description:
 *      Set interrupt trigger status configuration.
 * Input:
 *      port - port id
 *      intcpu - 0 internal cpu interrupt   1 external cpu interrupt
 *      type - Interrupt type.
 *      enable - Interrupt status.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 *      RT_ERR_ENABLE       - Invalid enable input.
 * Note:
 *      The API can set interrupt status configuration.
 *      The interrupt trigger status is shown in the following:
 *      - INT_TYPE_LINK_CHANGE,
 *      - INT_TYPE_GPHY,
 *      - INT_TYPE_LEARN_OVER,
 *      - INT_TYPE_RLFD,
 *      - INT_TYPE_WOL,
 *      - INT_TYPE_SDS_LINK_FAULT,
 *      - INT_TYPE_SDS_UPDATE_PHY,
 */
extern rtk_api_ret_t rtk_portInt_control_set(rtk_port_t port, rtk_int_cpu_t intcpu, rtk_int_type_t type, rtk_enable_t enable);

/* Function Name:
 *      rtk_portInt_control_get
 * Description:
 *      Get interrupt trigger status configuration.
 * Input:
 *      port - port id
 *      intcpu - 0 internal cpu interrupt   1 external cpu interrupt
 *      type - Interrupt type.
 *      enable - Interrupt status.
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 *      RT_ERR_INPUT        - Invalid input parameters.
 *      RT_ERR_ENABLE       - Invalid enable input.
 * Note:
 *      The API can set interrupt status configuration.
 *      The interrupt trigger status is shown in the following:
 *      - INT_TYPE_LINK_CHANGE,
 *      - INT_TYPE_GPHY,
 *      - INT_TYPE_LEARN_OVER,
 *      - INT_TYPE_RLFD,
 *      - INT_TYPE_WOL,
 *      - INT_TYPE_SDS_LINK_FAULT,
 *      - INT_TYPE_SDS_UPDATE_PHY,
 */

extern rtk_api_ret_t rtk_portInt_control_get(rtk_port_t port, rtk_int_cpu_t intcpu, rtk_int_type_t type, rtk_enable_t *pEnable);


#endif /* __RTK_API_INTERRUPT_H*/

