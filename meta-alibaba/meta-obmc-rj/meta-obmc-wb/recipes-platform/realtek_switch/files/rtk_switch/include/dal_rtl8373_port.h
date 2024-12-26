#ifndef __DAL_RTL8373_PORT_H__
#define __DAL_RTL8373_PORT_H__


#include <port.h>


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

extern ret_t dal_rtl8373_portFrcAbility_set(rtk_uint32 port, rtk_port_ability_t* ability);


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

extern ret_t dal_rtl8373_portFrcAbility_get(rtk_uint32 port, rtk_port_ability_t* ability);



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

extern ret_t dal_rtl8373_portStatus_get(rtk_uint32 port, rtk_port_status_t* status);

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

extern ret_t dal_rtl8373_portMaxLen_set(rtk_uint32 port, rtk_uint32 type, rtk_uint32 len);


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

extern ret_t dal_rtl8373_portMaxLen_get(rtk_uint32 port, rtk_uint32 type, rtk_uint32* pLen);




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

extern ret_t dal_rtl8373_portMaxLenIncTag_set(rtk_uint32 port, rtk_uint32 enable);


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

extern ret_t dal_rtl8373_portMaxLenIncTag_get(rtk_uint32 port, rtk_uint32* pEnable);


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

extern ret_t dal_rtl8373_portLoopbackEn_set(rtk_uint32 port, rtk_enable_t enable);


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

extern ret_t dal_rtl8373_portLoopbackEn_get(rtk_uint32 port, rtk_enable_t * pEnable);


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

extern ret_t dal_rtl8373_portBackpressureEn_set(rtk_uint32 port, rtk_enable_t enable);


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

extern ret_t dal_rtl8373_portBackpressureEn_get(rtk_uint32 port, rtk_enable_t * pEnable);


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

extern ret_t dal_rtl8373_rtct_init();



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
extern ret_t dal_rtl8373_rtct_start(rtk_uint32 phymask);


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
extern ret_t dal_rtl8373_rtct_status_get(rtk_uint32 phyid, rtk_rtct_result_t * pResult);


#endif

