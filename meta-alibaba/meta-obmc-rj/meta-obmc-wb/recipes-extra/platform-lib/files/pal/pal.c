/*
 *
 * Copyright 2018-present Facebook. All Rights Reserved.
 *
 * This file contains code to support IPMI2.0 Specificaton available @
 * http://www.intel.com/content/www/us/en/servers/ipmi/ipmi-specifications.html
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

 /*
  * This file contains functions and logics that depends on Wedge100 specific
  * hardware and kernel drivers. Here, some of the empty "default" functions
  * are overridden with simple functions that returns non-zero error code.
  * This is for preventing any potential escape of failures through the
  * default functions that will return 0 no matter what.
  */

//  #define DEBUG

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <syslog.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <linux/limits.h>
#include "pal.h"
#include <math.h>
#include <facebook/bic.h>
#include <openbmc/kv.h>
#include <openbmc/obmc-i2c.h>
#include <openbmc/obmc_pal_sensors.h>
#include <openbmc/sensor-correction.h>

typedef struct {
  char name[32];
} sensor_desc_t;

struct threadinfo {
  uint8_t is_running;
  uint8_t fru;
  pthread_t pt;
};

typedef struct {
  uint16_t flag;
  float ucr;
  float unc;
  float unr;
  float lcr;
  float lnc;
  float lnr;
  float pos_hyst;
  float neg_hyst;
  int curr_st;
  char name[32];
} _sensor_thresh_t;

typedef struct {
  char name[NAME_MAX];
} sensor_path_t;

static sensor_desc_t m_snr_desc[MAX_NUM_FRUS][MAX_SENSOR_NUM] = {0};
static struct threadinfo t_dump[MAX_NUM_FRUS] = {0, };
static sensor_path_t snr_path[MAX_NUM_FRUS][MAX_SENSOR_NUM] = {0};

/* List of BIC Discrete sensors to be monitored */
const uint8_t bic_discrete_list[] = {
  BIC_SENSOR_SYSTEM_STATUS,
  BIC_SENSOR_PROC_FAIL,
  BIC_SENSOR_SYS_BOOT_STAT,
  BIC_SENSOR_CPU_DIMM_HOT,
  BIC_SENSOR_VR_HOT,
  BIC_SENSOR_POWER_THRESH_EVENT,
  BIC_SENSOR_POST_ERR,
  BIC_SENSOR_POWER_ERR,
  BIC_SENSOR_PROC_HOT_EXT,
  BIC_SENSOR_MACHINE_CHK_ERR,
  BIC_SENSOR_PCIE_ERR,
  BIC_SENSOR_OTHER_IIO_ERR,
  BIC_SENSOR_MEM_ECC_ERR,
  BIC_SENSOR_SPS_FW_HLTH,
  BIC_SENSOR_CAT_ERR,
};

// List of BIC sensors which need to do negative reading handle
const uint8_t bic_neg_reading_sensor_support_list[] = {
  /* Temperature sensors*/
  BIC_SENSOR_MB_OUTLET_TEMP,
  BIC_SENSOR_MB_INLET_TEMP,
  BIC_SENSOR_PCH_TEMP,
  BIC_SENSOR_SOC_TEMP,
  BIC_SENSOR_SOC_DIMMA0_TEMP,
  BIC_SENSOR_SOC_DIMMB0_TEMP,
  BIC_SENSOR_VCCIN_VR_CURR,
};

/* List of SCM sensors to be monitored */
const uint8_t scm_sensor_list[] = {
  SCM_SENSOR_OUTLET_LOCAL_TEMP,
  SCM_SENSOR_OUTLET_REMOTE_TEMP,
  SCM_SENSOR_INLET_LOCAL_TEMP,
  SCM_SENSOR_INLET_REMOTE_TEMP,
  SCM_SENSOR_HSC_VOLT,
  SCM_SENSOR_HSC_CURR,
  SCM_SENSOR_HSC_POWER,
};

/* List of SCM and BIC sensors to be monitored */
const uint8_t scm_all_sensor_list[] = {
  SCM_SENSOR_OUTLET_LOCAL_TEMP,
  SCM_SENSOR_OUTLET_REMOTE_TEMP,
  SCM_SENSOR_INLET_LOCAL_TEMP,
  SCM_SENSOR_INLET_REMOTE_TEMP,
  SCM_SENSOR_HSC_VOLT,
  SCM_SENSOR_HSC_CURR,
  SCM_SENSOR_HSC_POWER,
  BIC_SENSOR_MB_OUTLET_TEMP,
  BIC_SENSOR_MB_INLET_TEMP,
  BIC_SENSOR_PCH_TEMP,
  BIC_SENSOR_VCCIN_VR_TEMP,
  BIC_SENSOR_1V05MIX_VR_TEMP,
  BIC_SENSOR_SOC_TEMP,
  BIC_SENSOR_SOC_THERM_MARGIN,
  BIC_SENSOR_VDDR_VR_TEMP,
  BIC_SENSOR_SOC_DIMMA0_TEMP,
  BIC_SENSOR_SOC_DIMMB0_TEMP,
  BIC_SENSOR_SOC_PACKAGE_PWR,
  BIC_SENSOR_VCCIN_VR_POUT,
  BIC_SENSOR_VDDR_VR_POUT,
  BIC_SENSOR_SOC_TJMAX,
  BIC_SENSOR_P3V3_MB,
  BIC_SENSOR_P12V_MB,
  BIC_SENSOR_P1V05_PCH,
  BIC_SENSOR_P3V3_STBY_MB,
  BIC_SENSOR_P5V_STBY_MB,
  BIC_SENSOR_PV_BAT,
  BIC_SENSOR_PVDDR,
  BIC_SENSOR_P1V05_MIX,
  BIC_SENSOR_1V05MIX_VR_CURR,
  BIC_SENSOR_VDDR_VR_CURR,
  BIC_SENSOR_VCCIN_VR_CURR,
  BIC_SENSOR_VCCIN_VR_VOL,
  BIC_SENSOR_VDDR_VR_VOL,
  BIC_SENSOR_P1V05MIX_VR_VOL,
  BIC_SENSOR_P1V05MIX_VR_POUT,
  BIC_SENSOR_INA230_POWER,
  BIC_SENSOR_INA230_VOL,
};

/* List of SMB sensors to be monitored */
const uint8_t smb_sensor_list[] = {
#if 0
  /*
   * mikechoi@fb.com : Jul 11 2019,
   * Temporarily disable the sensor reading of this power chip, as per
   * FB Network HW team's request. Reading the sensor of this chip rarely
   * causes this power chip to go to a bad state, and turn off the
   * power to TH3. Until we have a new revision of HW (with verified HW fix),
   * we will skip reading these sensors.
   */
  SMB_SENSOR_1220_VMON1,
  SMB_SENSOR_1220_VMON2,
  SMB_SENSOR_1220_VMON3,
  SMB_SENSOR_1220_VMON4,
  SMB_SENSOR_1220_VMON5,
  SMB_SENSOR_1220_VMON6,
  SMB_SENSOR_1220_VMON7,
  SMB_SENSOR_1220_VMON8,
  SMB_SENSOR_1220_VMON9,
  SMB_SENSOR_1220_VMON10,
  SMB_SENSOR_1220_VMON11,
  SMB_SENSOR_1220_VMON12,
  SMB_SENSOR_1220_VCCA,
  SMB_SENSOR_1220_VCCINP,
#endif
  SMB_SENSOR_TH3_SERDES_VOLT,
  SMB_SENSOR_TH3_SERDES_CURR,
  SMB_SENSOR_TH3_SERDES_TEMP,
  SMB_SENSOR_TH3_CORE_VOLT,
  SMB_SENSOR_TH3_CORE_CURR,
  SMB_SENSOR_TH3_CORE_TEMP,
  SMB_SENSOR_TEMP1,
  SMB_SENSOR_TEMP2,
  SMB_SENSOR_TEMP3,
  SMB_SENSOR_TEMP4,
  SMB_SENSOR_TEMP5,
  SMB_SENSOR_TH3_DIE_TEMP1,
  SMB_SENSOR_TH3_DIE_TEMP2,
  /* Sensors on PDB */
  SMB_SENSOR_PDB_L_TEMP1,
  SMB_SENSOR_PDB_L_TEMP2,
  SMB_SENSOR_PDB_R_TEMP1,
  SMB_SENSOR_PDB_R_TEMP2,
  /* Sensors on FCM */
  SMB_SENSOR_FCM_T_TEMP1,
  SMB_SENSOR_FCM_T_TEMP2,
  SMB_SENSOR_FCM_B_TEMP1,
  SMB_SENSOR_FCM_B_TEMP2,
  SMB_SENSOR_FCM_T_HSC_VOLT,
  SMB_SENSOR_FCM_T_HSC_CURR,
  SMB_SENSOR_FCM_T_HSC_POWER,
  SMB_SENSOR_FCM_B_HSC_VOLT,
  SMB_SENSOR_FCM_B_HSC_CURR,
  SMB_SENSOR_FCM_B_HSC_POWER,
  /* Sensors FAN Speed */
  SMB_SENSOR_FAN1_FRONT_TACH,
  SMB_SENSOR_FAN1_REAR_TACH,
  SMB_SENSOR_FAN2_FRONT_TACH,
  SMB_SENSOR_FAN2_REAR_TACH,
  SMB_SENSOR_FAN3_FRONT_TACH,
  SMB_SENSOR_FAN3_REAR_TACH,
  SMB_SENSOR_FAN4_FRONT_TACH,
  SMB_SENSOR_FAN4_REAR_TACH,
  SMB_SENSOR_FAN5_FRONT_TACH,
  SMB_SENSOR_FAN5_REAR_TACH,
  SMB_SENSOR_FAN6_FRONT_TACH,
  SMB_SENSOR_FAN6_REAR_TACH,
  SMB_SENSOR_FAN7_FRONT_TACH,
  SMB_SENSOR_FAN7_REAR_TACH,
  SMB_SENSOR_FAN8_FRONT_TACH,
  SMB_SENSOR_FAN8_REAR_TACH,
};

const uint8_t pim1_sensor_list[] = {
  PIM1_SENSOR_TEMP1,
  PIM1_SENSOR_TEMP2,
  PIM1_SENSOR_QSFP_TEMP,
  PIM1_SENSOR_HSC_VOLT,
  PIM1_SENSOR_HSC_CURR,
  PIM1_SENSOR_HSC_POWER,
  PIM1_SENSOR_34461_VOLT1,
  PIM1_SENSOR_34461_VOLT2,
  PIM1_SENSOR_34461_VOLT3,
  PIM1_SENSOR_34461_VOLT4,
  PIM1_SENSOR_34461_VOLT5,
  PIM1_SENSOR_34461_VOLT6,
  PIM1_SENSOR_34461_VOLT7,
  PIM1_SENSOR_34461_VOLT8,
  PIM1_SENSOR_34461_VOLT9,
  PIM1_SENSOR_34461_VOLT10,
  PIM1_SENSOR_34461_VOLT11,
  PIM1_SENSOR_34461_VOLT12,
  PIM1_SENSOR_34461_VOLT13,
  PIM1_SENSOR_34461_VOLT14,
  PIM1_SENSOR_34461_VOLT15,
  PIM1_SENSOR_34461_VOLT16,
};

const uint8_t pim2_sensor_list[] = {
  PIM2_SENSOR_TEMP1,
  PIM2_SENSOR_TEMP2,
  PIM2_SENSOR_QSFP_TEMP,
  PIM2_SENSOR_HSC_VOLT,
  PIM2_SENSOR_HSC_CURR,
  PIM2_SENSOR_HSC_POWER,
  PIM2_SENSOR_34461_VOLT1,
  PIM2_SENSOR_34461_VOLT2,
  PIM2_SENSOR_34461_VOLT3,
  PIM2_SENSOR_34461_VOLT4,
  PIM2_SENSOR_34461_VOLT5,
  PIM2_SENSOR_34461_VOLT6,
  PIM2_SENSOR_34461_VOLT7,
  PIM2_SENSOR_34461_VOLT8,
  PIM2_SENSOR_34461_VOLT9,
  PIM2_SENSOR_34461_VOLT10,
  PIM2_SENSOR_34461_VOLT11,
  PIM2_SENSOR_34461_VOLT12,
  PIM2_SENSOR_34461_VOLT13,
  PIM2_SENSOR_34461_VOLT14,
  PIM2_SENSOR_34461_VOLT15,
  PIM2_SENSOR_34461_VOLT16,
};

const uint8_t pim3_sensor_list[] = {
  PIM3_SENSOR_TEMP1,
  PIM3_SENSOR_TEMP2,
  PIM3_SENSOR_QSFP_TEMP,
  PIM3_SENSOR_HSC_VOLT,
  PIM3_SENSOR_HSC_CURR,
  PIM3_SENSOR_HSC_POWER,
  PIM3_SENSOR_34461_VOLT1,
  PIM3_SENSOR_34461_VOLT2,
  PIM3_SENSOR_34461_VOLT3,
  PIM3_SENSOR_34461_VOLT4,
  PIM3_SENSOR_34461_VOLT5,
  PIM3_SENSOR_34461_VOLT6,
  PIM3_SENSOR_34461_VOLT7,
  PIM3_SENSOR_34461_VOLT8,
  PIM3_SENSOR_34461_VOLT9,
  PIM3_SENSOR_34461_VOLT10,
  PIM3_SENSOR_34461_VOLT11,
  PIM3_SENSOR_34461_VOLT12,
  PIM3_SENSOR_34461_VOLT13,
  PIM3_SENSOR_34461_VOLT14,
  PIM3_SENSOR_34461_VOLT15,
  PIM3_SENSOR_34461_VOLT16,
};

const uint8_t pim4_sensor_list[] = {
  PIM4_SENSOR_TEMP1,
  PIM4_SENSOR_TEMP2,
  PIM4_SENSOR_QSFP_TEMP,
  PIM4_SENSOR_HSC_VOLT,
  PIM4_SENSOR_HSC_CURR,
  PIM4_SENSOR_HSC_POWER,
  PIM4_SENSOR_34461_VOLT1,
  PIM4_SENSOR_34461_VOLT2,
  PIM4_SENSOR_34461_VOLT3,
  PIM4_SENSOR_34461_VOLT4,
  PIM4_SENSOR_34461_VOLT5,
  PIM4_SENSOR_34461_VOLT6,
  PIM4_SENSOR_34461_VOLT7,
  PIM4_SENSOR_34461_VOLT8,
  PIM4_SENSOR_34461_VOLT9,
  PIM4_SENSOR_34461_VOLT10,
  PIM4_SENSOR_34461_VOLT11,
  PIM4_SENSOR_34461_VOLT12,
  PIM4_SENSOR_34461_VOLT13,
  PIM4_SENSOR_34461_VOLT14,
  PIM4_SENSOR_34461_VOLT15,
  PIM4_SENSOR_34461_VOLT16,
};

const uint8_t pim5_sensor_list[] = {
  PIM5_SENSOR_TEMP1,
  PIM5_SENSOR_TEMP2,
  PIM5_SENSOR_QSFP_TEMP,
  PIM5_SENSOR_HSC_VOLT,
  PIM5_SENSOR_HSC_CURR,
  PIM5_SENSOR_HSC_POWER,
  PIM5_SENSOR_34461_VOLT1,
  PIM5_SENSOR_34461_VOLT2,
  PIM5_SENSOR_34461_VOLT3,
  PIM5_SENSOR_34461_VOLT4,
  PIM5_SENSOR_34461_VOLT5,
  PIM5_SENSOR_34461_VOLT6,
  PIM5_SENSOR_34461_VOLT7,
  PIM5_SENSOR_34461_VOLT8,
  PIM5_SENSOR_34461_VOLT9,
  PIM5_SENSOR_34461_VOLT10,
  PIM5_SENSOR_34461_VOLT11,
  PIM5_SENSOR_34461_VOLT12,
  PIM5_SENSOR_34461_VOLT13,
  PIM5_SENSOR_34461_VOLT14,
  PIM5_SENSOR_34461_VOLT15,
  PIM5_SENSOR_34461_VOLT16,
};

const uint8_t pim6_sensor_list[] = {
  PIM6_SENSOR_TEMP1,
  PIM6_SENSOR_TEMP2,
  PIM6_SENSOR_QSFP_TEMP,
  PIM6_SENSOR_HSC_VOLT,
  PIM6_SENSOR_HSC_CURR,
  PIM6_SENSOR_HSC_POWER,
  PIM6_SENSOR_34461_VOLT1,
  PIM6_SENSOR_34461_VOLT2,
  PIM6_SENSOR_34461_VOLT3,
  PIM6_SENSOR_34461_VOLT4,
  PIM6_SENSOR_34461_VOLT5,
  PIM6_SENSOR_34461_VOLT6,
  PIM6_SENSOR_34461_VOLT7,
  PIM6_SENSOR_34461_VOLT8,
  PIM6_SENSOR_34461_VOLT9,
  PIM6_SENSOR_34461_VOLT10,
  PIM6_SENSOR_34461_VOLT11,
  PIM6_SENSOR_34461_VOLT12,
  PIM6_SENSOR_34461_VOLT13,
  PIM6_SENSOR_34461_VOLT14,
  PIM6_SENSOR_34461_VOLT15,
  PIM6_SENSOR_34461_VOLT16,
};

const uint8_t pim7_sensor_list[] = {
  PIM7_SENSOR_TEMP1,
  PIM7_SENSOR_TEMP2,
  PIM7_SENSOR_QSFP_TEMP,
  PIM7_SENSOR_HSC_VOLT,
  PIM7_SENSOR_HSC_CURR,
  PIM7_SENSOR_HSC_POWER,
  PIM7_SENSOR_34461_VOLT1,
  PIM7_SENSOR_34461_VOLT2,
  PIM7_SENSOR_34461_VOLT3,
  PIM7_SENSOR_34461_VOLT4,
  PIM7_SENSOR_34461_VOLT5,
  PIM7_SENSOR_34461_VOLT6,
  PIM7_SENSOR_34461_VOLT7,
  PIM7_SENSOR_34461_VOLT8,
  PIM7_SENSOR_34461_VOLT9,
  PIM7_SENSOR_34461_VOLT10,
  PIM7_SENSOR_34461_VOLT11,
  PIM7_SENSOR_34461_VOLT12,
  PIM7_SENSOR_34461_VOLT13,
  PIM7_SENSOR_34461_VOLT14,
  PIM7_SENSOR_34461_VOLT15,
  PIM7_SENSOR_34461_VOLT16,
};

const uint8_t pim8_sensor_list[] = {
  PIM8_SENSOR_TEMP1,
  PIM8_SENSOR_TEMP2,
  PIM8_SENSOR_QSFP_TEMP,
  PIM8_SENSOR_HSC_VOLT,
  PIM8_SENSOR_HSC_CURR,
  PIM8_SENSOR_HSC_POWER,
  PIM8_SENSOR_34461_VOLT1,
  PIM8_SENSOR_34461_VOLT2,
  PIM8_SENSOR_34461_VOLT3,
  PIM8_SENSOR_34461_VOLT4,
  PIM8_SENSOR_34461_VOLT5,
  PIM8_SENSOR_34461_VOLT6,
  PIM8_SENSOR_34461_VOLT7,
  PIM8_SENSOR_34461_VOLT8,
  PIM8_SENSOR_34461_VOLT9,
  PIM8_SENSOR_34461_VOLT10,
  PIM8_SENSOR_34461_VOLT11,
  PIM8_SENSOR_34461_VOLT12,
  PIM8_SENSOR_34461_VOLT13,
  PIM8_SENSOR_34461_VOLT14,
  PIM8_SENSOR_34461_VOLT15,
  PIM8_SENSOR_34461_VOLT16,
};

const uint8_t psu1_sensor_list[] = {
  PSU1_SENSOR_IN_VOLT,
  PSU1_SENSOR_12V_VOLT,
  PSU1_SENSOR_STBY_VOLT,
  PSU1_SENSOR_IN_CURR,
  PSU1_SENSOR_12V_CURR,
  PSU1_SENSOR_STBY_CURR,
  PSU1_SENSOR_IN_POWER,
  PSU1_SENSOR_12V_POWER,
  PSU1_SENSOR_STBY_POWER,
  PSU1_SENSOR_FAN_TACH,
  PSU1_SENSOR_TEMP1,
  PSU1_SENSOR_TEMP2,
  PSU1_SENSOR_TEMP3,
};

const uint8_t psu2_sensor_list[] = {
  PSU2_SENSOR_IN_VOLT,
  PSU2_SENSOR_12V_VOLT,
  PSU2_SENSOR_STBY_VOLT,
  PSU2_SENSOR_IN_CURR,
  PSU2_SENSOR_12V_CURR,
  PSU2_SENSOR_STBY_CURR,
  PSU2_SENSOR_IN_POWER,
  PSU2_SENSOR_12V_POWER,
  PSU2_SENSOR_STBY_POWER,
  PSU2_SENSOR_FAN_TACH,
  PSU2_SENSOR_TEMP1,
  PSU2_SENSOR_TEMP2,
  PSU2_SENSOR_TEMP3,
};

const uint8_t psu3_sensor_list[] = {
  PSU3_SENSOR_IN_VOLT,
  PSU3_SENSOR_12V_VOLT,
  PSU3_SENSOR_STBY_VOLT,
  PSU3_SENSOR_IN_CURR,
  PSU3_SENSOR_12V_CURR,
  PSU3_SENSOR_STBY_CURR,
  PSU3_SENSOR_IN_POWER,
  PSU3_SENSOR_12V_POWER,
  PSU3_SENSOR_STBY_POWER,
  PSU3_SENSOR_FAN_TACH,
  PSU3_SENSOR_TEMP1,
  PSU3_SENSOR_TEMP2,
  PSU3_SENSOR_TEMP3,
};

const uint8_t psu4_sensor_list[] = {
  PSU4_SENSOR_IN_VOLT,
  PSU4_SENSOR_12V_VOLT,
  PSU4_SENSOR_STBY_VOLT,
  PSU4_SENSOR_IN_CURR,
  PSU4_SENSOR_12V_CURR,
  PSU4_SENSOR_STBY_CURR,
  PSU4_SENSOR_IN_POWER,
  PSU4_SENSOR_12V_POWER,
  PSU4_SENSOR_STBY_POWER,
  PSU4_SENSOR_FAN_TACH,
  PSU4_SENSOR_TEMP1,
  PSU4_SENSOR_TEMP2,
  PSU4_SENSOR_TEMP3,
};

float scm_sensor_threshold[MAX_SENSOR_NUM][MAX_SENSOR_THRESHOLD + 1] = {0};
float smb_sensor_threshold[MAX_SENSOR_NUM][MAX_SENSOR_THRESHOLD + 1] = {0};
float pim_sensor_threshold[MAX_SENSOR_NUM][MAX_SENSOR_THRESHOLD + 1] = {0};
float psu_sensor_threshold[MAX_SENSOR_NUM][MAX_SENSOR_THRESHOLD + 1] = {0};

size_t bic_discrete_cnt = sizeof(bic_discrete_list)/sizeof(uint8_t);
size_t scm_sensor_cnt = sizeof(scm_sensor_list)/sizeof(uint8_t);
size_t scm_all_sensor_cnt = sizeof(scm_all_sensor_list)/sizeof(uint8_t);
size_t smb_sensor_cnt = sizeof(smb_sensor_list)/sizeof(uint8_t);
size_t pim1_sensor_cnt = sizeof(pim1_sensor_list)/sizeof(uint8_t);
size_t pim2_sensor_cnt = sizeof(pim2_sensor_list)/sizeof(uint8_t);
size_t pim3_sensor_cnt = sizeof(pim3_sensor_list)/sizeof(uint8_t);
size_t pim4_sensor_cnt = sizeof(pim4_sensor_list)/sizeof(uint8_t);
size_t pim5_sensor_cnt = sizeof(pim5_sensor_list)/sizeof(uint8_t);
size_t pim6_sensor_cnt = sizeof(pim6_sensor_list)/sizeof(uint8_t);
size_t pim7_sensor_cnt = sizeof(pim7_sensor_list)/sizeof(uint8_t);
size_t pim8_sensor_cnt = sizeof(pim8_sensor_list)/sizeof(uint8_t);
size_t psu1_sensor_cnt = sizeof(psu1_sensor_list)/sizeof(uint8_t);
size_t psu2_sensor_cnt = sizeof(psu2_sensor_list)/sizeof(uint8_t);
size_t psu3_sensor_cnt = sizeof(psu3_sensor_list)/sizeof(uint8_t);
size_t psu4_sensor_cnt = sizeof(psu4_sensor_list)/sizeof(uint8_t);

static sensor_info_t g_sinfo[MAX_NUM_FRUS][MAX_SENSOR_NUM] = {0};

static float hsc_rsense[MAX_NUM_FRUS] = {0};

const char pal_fru_list[] = "all, scm, smb, pim1, pim2, pim3, \
pim4, pim5, pim6, pim7, pim8, psu1, psu2, psu3, psu4";

char * key_list[] = {
"pwr_server_last_state",
"sysfw_ver_server",
"timestamp_sled",
"server_por_cfg",
"server_sel_error",
"scm_sensor_health",
"smb_sensor_health",
"pim1_sensor_health",
"pim2_sensor_health",
"pim3_sensor_health",
"pim4_sensor_health",
"pim5_sensor_health",
"pim6_sensor_health",
"pim7_sensor_health",
"pim8_sensor_health",
"psu1_sensor_health",
"psu2_sensor_health",
"psu3_sensor_health",
"psu4_sensor_health",
"server_boot_order",
"server_restart_cause",
"server_cpu_ppin",
/* Add more Keys here */
LAST_KEY /* This is the last key of the list */
};

char * def_val_list[] = {
  "on", /* pwr_server_last_state */
  "0", /* sysfw_ver_server */
  "0", /* timestamp_sled */
  "lps", /* server_por_cfg */
  "1", /* server_sel_error */
  "1", /* scm_sensor_health */
  "1", /* smb_sensor_health */
  "1", /* pim1_sensor_health */
  "1", /* pim2_sensor_health */
  "1", /* pim3_sensor_health */
  "1", /* pim4_sensor_health */
  "1", /* pim5_sensor_health */
  "1", /* pim6_sensor_health */
  "1", /* pim7_sensor_health */
  "1", /* pim8_sensor_health */
  "1", /* psu1_sensor_health */
  "1", /* psu2_sensor_health */
  "1", /* psu3_sensor_health */
  "1", /* psu4_sensor_health */
  "0000000", /* scm_boot_order */
  "3", /* scm_restart_cause */
  "0", /* scm_cpu_ppin */
  /* Add more def values for the correspoding keys*/
  LAST_KEY /* Same as last entry of the key_list */
};

/*
 * Sensor Offset string Look up table.
 * SENSOR SPEC  EVENT DATA  EVENT DATA  EVENT DATA  EVENT DATA  EVENT DATA  EVENT DATA  STRING
 * OFFSET,      2 MASK,     2 OR,       2 VALUE,    3 MASK,     3 OR,       3 VALUE,
 */
/* Sensor Type: 0x05 - Physical Security Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x05[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "General Chassis Intrusion"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Drive Bay Intrusion"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "I/O Card Area Intrusion"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Processor Area Intrusion"},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "LAN Leash Lost(system is unplugged from LAN)"},
  {0x04, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Network controller the leash was lost on: "},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Unauthorized Dock"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FAN Area Intrusion"},
};

/* Sensor Type: 0x06 - Platform Security Violation Attempt Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x06[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Secure Mode Violation Attempt"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Pre-boot Password Violation - User"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Pre-boot Password Violation - Setup"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Pre-boot Password Violation - Network Boot"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Pre-boot Password Violation - Other"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Out-of-band Access Password Violation"},
};

/* Sensor Type: 0x07 - Processor Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x07[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "IERR"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Thermal Trip"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRB1/BIST Failure"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRB2/Hand in POST Failure"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRB3/Processor Startup/Initialization Failure"},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Configuration Error"},
  {0x05, 0xF0, 0xF0, 0xF0, 0x00, 0x00, 0x00, "CPU Socket: "},
  {0x05, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_NONE"},
  {0x05, 0x0F, 0x00, 0x01, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_IFU"},
  {0x05, 0x0F, 0x00, 0x02, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_DCU"},
  {0x05, 0x0F, 0x00, 0x03, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_DTLB"},
  {0x05, 0x0F, 0x00, 0x04, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_MLC"},
  {0x05, 0x0F, 0x00, 0x05, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_PCU"},
  {0x05, 0x0F, 0x00, 0x06, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_IIO"},
  {0x05, 0x0F, 0x00, 0x07, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_CHA"},
  {0x05, 0x0F, 0x00, 0x08, 0x00, 0x00, 0x00, "Bank Type: MCA_UNIT_KTI"},
  {0x05, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0xF0, "Error Type: "},
  {0x05, 0x00, 0x00, 0x00, 0x0E, 0x0F, 0x0F, "Error Severity: "},
  {0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, "Current Boot Error"},
  {0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, "Current Last Error"},

  {0x05, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "MCA unit: "},
  {0x05, 0xF0, 0xF0, 0xF0, 0x00, 0x00, 0x00, "Socket: "},
  {0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, "Current Boot"},
  {0x05, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, "Last Boot"},
  {0x05, 0x00, 0x00, 0x00, 0x0E, 0x0E, 0x0E, "Severity: "},
  {0x05, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0xF0, "ErrorType: "},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "SM BIOS Uncorrectable CPU-Complex Error"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Processor Presence Detected"},
  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Processor Disabled"},
  {0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Terminator Presence Detected"},
  {0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Processor Automatically Throttled"},
  {0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Machine Check Exception(Uncorrectable)"},
  {0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Correctable Machine check Error"},
};

/* Sensor Type: 0x08 - Power Supply Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x08[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Presence Detected"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Supply Failure Detected"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Predictive Failure"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Supply Input Lost (AC/DC)"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Supply Input Lost or Out-of-range"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Supply Input Out-of-range"},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Configuration Error"},
  {0x06, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, "Error Type: Vendor Mismatch"},
  {0x06, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x01, "Error Type: Revision Mismatch"},
  {0x06, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x02, "Error Type: Processor Missing"},
  {0x06, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x03, "Error Type: Power Supply rating Mismatch"},
  {0x06, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x04, "Error Type: Voltage rating Mismatch"},
};

/* Sensor Type: 0x09 - Power Unit Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x09[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Off/Power Down"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Cycle"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "240VA Power Down"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Interlock Power Down"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "AC Lost/Power Input Lost"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Soft Power Control Failure"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Unit Failure Detected"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Predictive Failure"},
};

/* Sensor Type: 0x0C - Memory Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x0c[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Correctable ECC/Other Correctable Memory Error"},
  {0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, "Current Boot Error"},
  {0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, "Last Boot Error"},
  {0x00, 0x06, 0x0F, 0x0F, 0x00, 0x00, 0x00, "MemoryController: "},
  {0x00, 0x00, 0x00, 0x00, 0xC0, 0xF0, 0xF0, "CPU Socket: "},
  {0x00, 0x00, 0x00, 0x00, 0x30, 0xF0, 0xF0, "Channel: "},
  {0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, "Dimm: "},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Uncorrectable ECC/Other Uncorrectable Memory Error"},
  {0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, "Current Boot Error"},
  {0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, "Last Boot Error"},
  {0x01, 0x06, 0x0F, 0x0F, 0x00, 0x00, 0x00, "MemoryController: "},
  {0x01, 0x00, 0x00, 0x00, 0xC0, 0xF0, 0xF0, "CPU Socket: "},
  {0x01, 0x00, 0x00, 0x00, 0x30, 0xF0, 0xF0, "Channel: "},
  {0x01, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, "Dimm: "},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Parity"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Memory Scrub Failed (Stuck Bit)"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Memory Device Disabled"},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Correctable Memory Error Logging Limit Reached"},
  {0x05, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, "Current Boot Error"},
  {0x05, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, "Last Boot Error"},
  {0x05, 0x06, 0x0F, 0x0F, 0x00, 0x00, 0x00, "MemoryController: "},
  {0x05, 0x00, 0x00, 0x00, 0xC0, 0xF0, 0xF0, "CPU Socket: "},
  {0x05, 0x00, 0x00, 0x00, 0x30, 0xF0, 0xF0, "Channel: "},
  {0x05, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, "Dimm: "},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Presence Detected"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Configuration Error"},
  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Spare"},
  {0x08, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, "Memory Module/device identification: "},
  {0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Memory Automatically throttled"},
  {0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Critical Over temperature"},
};

/* Sensor Type: 0x0D - Drive Slot (BAY) Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x0d[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Drive Presence"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Drive Fault"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Predictive Failure"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Hot Spare"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Consistency Check/ Parity Check in progress"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "In Critical Array"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "In failed Array"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Rebuild/Remap in Progress"},
  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Rebuild/Remap Aborted"},
};

/* Sensor Type: 0x0F - System Firmware Progress Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x0f[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "System Firmware Error"},
  {0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Unspecified"},
  {0x00, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "No System Memory is Physically Installed in The System"},
  {0x00, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "No Usable System Memory, all installed memory has experienced an unrecoverable failure"},
  {0x00, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Unrecoverable Hard-Disk/ATAPI/IDE device failure"},
  {0x00, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Unrecoverable System-board Failure"},
  {0x00, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Unrecoverable Diskette Subsystem Failure"},
  {0x00, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Unrecoverable Hard-Disk Controller Failure"},
  {0x00, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Unrecoverable Unrecoverable PS/2 or USB keyboard Failure"},
  {0x00, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Removable Boot Media Not Found"},
  {0x00, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Unrecoverable Video Controller Failure"},
  {0x00, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "No Video Device Detected"},
  {0x00, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Firmware (BIOS) ROM corruption Detected"},
  {0x00, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "CPU Voltage Mismatch"},
  {0x00, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "CPU Speed Matching Failure"},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "System Firmware Hang"},
  {0x01, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Unspecified"},
  {0x01, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Memory Initialization"},
  {0x01, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Hard-Disk Initialization"},
  {0x01, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Secondary Processor(s) Initialization"},
  {0x01, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "User Authentication"},
  {0x01, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "User-Initiated System Setup"},
  {0x01, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "USB Resource Configuration"},
  {0x01, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "PCI Resource Configuration"},
  {0x01, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Option ROM Initialization"},
  {0x01, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Video Initialization"},
  {0x01, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Cache Initialization"},
  {0x01, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "SM Bus Initialization"},
  {0x01, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Keyboard Controller Initialization"},
  {0x01, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Embedded Controller/Management Controller Initialization"},
  {0x01, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Docking Station Attachment"},
  {0x01, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Enabling Docking Station"},
  {0x01, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Docking Station Ejection"},
  {0x01, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Disabling Docking Station"},
  {0x01, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Calling Operating System Wake-up Vector"},
  {0x01, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Starting Operating System Boot Process"},
  {0x01, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Baseboard or Motherboard Initialization"},
  {0x01, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Floppy Initialization"},
  {0x01, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Keyboard Test"},
  {0x01, 0xFF, 0x00, 0x18, 0x00, 0x00, 0x00, "Pointing Device Test"},
  {0x01, 0xFF, 0x00, 0x19, 0x00, 0x00, 0x00, "Primary Processor Initialization"},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "System Firmware Progress"},
  {0x02, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Unspecified"},
  {0x02, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Memory Initialization"},
  {0x02, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Hard-Disk Initialization"},
  {0x02, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Secondary Processor(s) Initialization"},
  {0x02, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "User Authentication"},
  {0x02, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "User-Initiated System Setup"},
  {0x02, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "USB Resource Configuration"},
  {0x02, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "PCI Resource Configuration"},
  {0x02, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Option ROM Initialization"},
  {0x02, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Video Initialization"},
  {0x02, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Cache Initialization"},
  {0x02, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "SM Bus Initialization"},
  {0x02, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Keyboard Controller Initialization"},
  {0x02, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Embedded Controller/Management Controller Initialization"},
  {0x02, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Docking Station Attachment"},
  {0x02, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Enabling Docking Station"},
  {0x02, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Docking Station Ejection"},
  {0x02, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Disabling Docking Station"},
  {0x02, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Calling Operating System Wake-up Vector"},
  {0x02, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Starting Operating System Boot Process"},
  {0x02, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Baseboard or Motherboard Initialization"},
  {0x02, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Floppy Initialization"},
  {0x02, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Keyboard Test"},
  {0x02, 0xFF, 0x00, 0x18, 0x00, 0x00, 0x00, "Pointing Device Test"},
  {0x02, 0xFF, 0x00, 0x19, 0x00, 0x00, 0x00, "Primary Processor Initialization"},
};

/* Sensor Type: 0x10 - Event Logging Disabled Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x10[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Correctable Memory Error Logging Disabled"},
  {0x00, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Memory module/device identification: "},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Event 'Type' Logging Disabled"},
  {0x01, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Event/Reading Type Code: "},
  {0x01, 0x00, 0x00, 0x00, 0x20, 0x00, 0x20, "Logging Disabled For all Event of This Type"},
  {0x01, 0x00, 0x00, 0x00, 0x10, 0x00, 0x10, "Assertion Event"},
  {0x01, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, "Deassertion Event"},
  {0x01, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, "Event Offset: "},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Log Area Reset/Cleared"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "All Event Logging Disabled"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "SEL Full"},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "SEL Almost Full"},
  {0x05, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, "Currently (0=Empty, 64=Full): "},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Correctable Machine Check Error Logging Disabled"},
  {0x06, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, "Entity Instance Number"},
  {0x06, 0x00, 0x00, 0x00, 0x80, 0x00, 0x80, "Vendor-Specific Processor Number"},
  {0x06, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Instance ID/Processor Number: "},
};

/* Sensor Type: 0x12 - System Event Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x12[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "System Reconfiguration"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "OEM System Boot Event"},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Undetermined System Hardware Failure"},

  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entry Added To Auxiliary Log"},
  {0x03, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Log Entry Action: Entry Added"},
  {0x03, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Log Entry Action: Entry Added Because Event Did Not Map To Standard IPMI Event"},
  {0x03, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Log Entry Action: Entry Added Along With One or More Corrosponding SEL Entries"},
  {0x03, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Log Entry Action: Log Cleared"},
  {0x03, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Log Entry Action: Log Disabled"},
  {0x03, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Log Entry Action: Log Enabled"},
  {0x03, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, "Log Type: MCA Log"},
  {0x03, 0x0F, 0x00, 0x01, 0x00, 0x00, 0x00, "Log Type: OEM 1"},
  {0x03, 0x0F, 0x00, 0x02, 0x00, 0x00, 0x00, "Log Type: OEM 2"},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PEF Action"},
  {0x04, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, "Alert"},
  {0x04, 0x02, 0x00, 0x02, 0x00, 0x00, 0x00, "Power Off"},
  {0x04, 0x04, 0x00, 0x04, 0x00, 0x00, 0x00, "Reset"},
  {0x04, 0x08, 0x00, 0x08, 0x00, 0x00, 0x00, "Power Cycle"},
  {0x04, 0x10, 0x00, 0x10, 0x00, 0x00, 0x00, "OEM Action"},
  {0x04, 0x20, 0x00, 0x20, 0x00, 0x00, 0x00, "Diagnostic Interrupt (NMI)"},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "TimeStamp Clock Synch"},
  {0x05, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, "Event is First of Pair"},
  {0x05, 0x80, 0x00, 0x80, 0x00, 0x00, 0x00, "Event is Second of Pair"},
  {0x05, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, "SEL TimeStamp Clock Updated"},
  {0x05, 0x0F, 0x00, 0x01, 0x00, 0x00, 0x00, "SDR TimeStamp Clock Updated"},
};

/* Sensor Type: 0x13 - Critical Interrupt Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x13[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Front Panel NMI/Diagnostic Interrupt"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Bus Timeout"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "I/O Channel Check NMI"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Software NMI"},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PCI PERR"},
  {0x04, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x04, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x04, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PCI SERR"},
  {0x05, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x05, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x05, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "EISA Fail Safe Timeout"},

  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Bus Correctable Error"},
  {0x07, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x07, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x07, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},

  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Bus Uncorrectable Error"},
  {0x08, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x08, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x08, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},

  {0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Fatal NMI"},

  {0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Bus Fatal Error"},
  {0x0A, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x0A, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x0A, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},

  {0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Bus Degraded"},

  {0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PCI LastBoot Error"},
  {0x0F, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Bus: "},
  {0x0F, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, "Device: "},
  {0x0F, 0x00, 0x00, 0x00, 0x07, 0x07, 0x07, "Function: "},
};

/* Sensor Type: 0x14 - Button / Switch Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x14[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Button Pressed"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Sleep Button Pressed"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Reset Button Pressed"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Latch Open"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Service Request Button"},
};

/* Sensor Type: 0x19 - Chip Set Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x19[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Soft Power Control Feature"},
  {0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Requested power state: S0/G0 Working"},
  {0x00, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Requested power state: S1 Sleeping With System H/W & Processor Context Maintained"},
  {0x00, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Requested power state: S2 Sleeping, Processor Context Lost"},
  {0x00, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Requested power state: S3 Sleeping, Processor & H/W Context Lost, Memory Retained"},
  {0x00, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Requested power state: S4 Non-Volatile Sleep/Suspend-to Disk"},
  {0x00, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Requested power state: S5/G2 Soft-Off"},
  {0x00, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Requested power state: S4/S5 Soft-Off, Particular S4/S5 State Cannot be Determined"},
  {0x00, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Requested power state: G3/Mechanical Off"},
  {0x00, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Requested power state: Sleeping In An S1, S2, or S3 States"},
  {0x00, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Requested power state: G1 Sleeping"},
  {0x00, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Requested power state: S5 Entered By Override"},
  {0x00, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Requested power state: Legacy ON State"},
  {0x00, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Requested power state: Legacy OFF State"},

  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, "Power State At Time Of Request: S0/G0 Working"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x01, "Power State At Time Of Request: S1 Sleeping With System H/W & Processor Context Maintained"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x02, "Power State At Time Of Request: S2 Sleeping, Processor Context Lost"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x03, "Power State At Time Of Request: S3 Sleeping, Processor & H/W Context Lost, Memory Retained"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x04, "Power State At Time Of Request: S4 Non-Volatile Sleep/Suspend-to Disk"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x05, "Power State At Time Of Request: S5/G2 Soft-Off"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x06, "Power State At Time Of Request: S4/S5 Soft-Off, Particular S4/S5 State Cannot be Determined"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x07, "Power State At Time Of Request: G3/Mechanical Off"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x08, "Power State At Time Of Request: Sleeping In An S1, S2, or S3 States"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x09, "Power State At Time Of Request: G1 Sleeping"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x0A, "Power State At Time Of Request: S5 Entered By Override"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x0B, "Power State At Time Of Request: Legacy ON State"},
  {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x0C, "Power State At Time Of Request: Legacy OFF State"},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Thermal Trip"},
};

/* Sensor Type: 0x1B - Cable/Interconnect Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x1b[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Cable/Interconnect is connected"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Configuration Error -Incorrect Cable Connected/Incorrect Interconnection"},
};

/* Sensor Type: 0x1D - System Boot/Restart Initiated Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x1d[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Initiated By Power Up"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Initiated By Hard Reset"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Initiated By Warm Reset"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "User Requested PXE Boot"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Automatic Boot To Diagnostic"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "OS/Run-time Software initiated Hard Reset"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "OS/Run-time Software initiated Warm Reset"},

  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "System restart"},
  {0x07, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Restart Cause(As per Get System Restart Cause command): "},
  {0x07, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, "Channel number(As per Get System Restart Cause command): "},
};

/* Sensor Type: 0x1E - Boot Error Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x1e[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "No Bootable Media"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Non-Bootable Diskette Left In Drive"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PXE Server Not Found"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Invalid Boot Sector"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Timeout Waiting for User Selection of Boot Source"},
};

/* Sensor Type: 0x1F - OS Boot Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x1f[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "A: Boot Completed"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "C: Boot Completed"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "PXE Boot Completed"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Diagnostic Boot Completed"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "CD-ROM Boot Completed"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "ROM Boot Completed"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Boot Completed (Device Not Specified)"},
};

/* Sensor Type: 0x20 - OS Stop/ShutDown Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x20[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Critical Stop During OS Load/Initialization"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Run-Time Critical Stop"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "OS Graceful Stop"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "OS Graceful Shutdown"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Soft Shutdown Initiated by PEF"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Agent Not responding"},
};

/* Sensor Type: 0x21 - Slot Connector Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x21[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Fault Status Asserted"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Identity Status Asserted"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot/Connector Device Installed/Attached"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot/Connector Ready for Device Installation"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot/Connector Ready for Device Removal"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot Power is Off"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot/Connector Device Removal Request"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Interlock Asserted"},
  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot is Disabled"},

  {0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot Holds Spare Device"},
  {0x09, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, "Slot/Connector Type: PCI"},
  {0x09, 0x7F, 0x00, 0x01, 0x00, 0x00, 0x00, "Slot/Connector Type: Drive Array"},
  {0x09, 0x7F, 0x00, 0x02, 0x00, 0x00, 0x00, "Slot/Connector Type: External Peripheral Connector"},
  {0x09, 0x7F, 0x00, 0x03, 0x00, 0x00, 0x00, "Slot/Connector Type: Docking"},
  {0x09, 0x7F, 0x00, 0x04, 0x00, 0x00, 0x00, "Slot/Connector Type: Other Standard Internal Expansion Slot"},
  {0x09, 0x7F, 0x00, 0x05, 0x00, 0x00, 0x00, "Slot/Connector Type: Slot Associated with Entity Specified by Entity ID for Sensor"},
  {0x09, 0x7F, 0x00, 0x06, 0x00, 0x00, 0x00, "Slot/Connector Type: AdvancedTCA"},
  {0x09, 0x7F, 0x00, 0x07, 0x00, 0x00, 0x00, "Slot/Connector Type: DIMM/Memory Devices"},
  {0x09, 0x7F, 0x00, 0x08, 0x00, 0x00, 0x00, "Slot/Connector Type: Fan"},
  {0x09, 0x7F, 0x00, 0x09, 0x00, 0x00, 0x00, "Slot/Connector Type: PCI Express"},
  {0x09, 0x7F, 0x00, 0x0A, 0x00, 0x00, 0x00, "Slot/Connector Type: SCSI (Parallel)"},
  {0x09, 0x7F, 0x00, 0x0B, 0x00, 0x00, 0x00, "Slot/Connector Type: SATA/SAS"},
  {0x09, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, "Slot Connector Number: "},
};

/* Sensor Type: 0x22 - System ACPI Power State Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x22[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S0/G0 Working"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S1 Sleeping With System H/W & Processor Context Maintained"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S2 Sleeping, Processor Context Lost"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S3 Sleeping, Processor & H/W Context Lost, Memory Retained"},
  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S4 Non-Volatile Sleep/Suspend-to Disk"},
  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S5/G2 Soft-Off"},
  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S4/S5 Soft-Off, Particular S4/S5 State Cannot be Determined"},
  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "G3/Mechanical Off"},
  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Sleeping In An S1, S2, or S3 States"},
  {0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "G1 Sleeping"},
  {0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "S5 Entered By Override"},
  {0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Legacy ON State"},
  {0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Legacy OFF State"},
  {0x0E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Unknown"},
};

/* Sensor Type: 0x23 - Watchdog 2 Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x23[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Timer Expired"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Hard Reset"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Down"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Power Cycle"},

  {0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Timer Interrupt"},
  {0x08, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Interrupt Type: None"},
  {0x08, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Interrupt Type: SMI"},
  {0x08, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Interrupt Type: NMI"},
  {0x08, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Interrupt Type: Messaging Interrupt"},
  {0x08, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Interrupt Type: Unspecified"},
  {0x08, 0x0F, 0x00, 0x01, 0x00, 0x00, 0x00, "Timer Use At Expiration: BIOS FRB2"},
  {0x08, 0x0F, 0x00, 0x02, 0x00, 0x00, 0x00, "Timer Use At Expiration: BIOS POST"},
  {0x08, 0x0F, 0x00, 0x03, 0x00, 0x00, 0x00, "Timer Use At Expiration: OS Load"},
  {0x08, 0x0F, 0x00, 0x04, 0x00, 0x00, 0x00, "Timer Use At Expiration: SMS/OS"},
  {0x08, 0x0F, 0x00, 0x05, 0x00, 0x00, 0x00, "Timer Use At Expiration: OEM"},
  {0x08, 0x0F, 0x00, 0x0F, 0x00, 0x00, 0x00, "Timer Use At Expiration: Unspecified"},
};

/* Sensor Type: 0x24 - Platform Alert Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x24[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Platform Generated Page"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Platform Generated LAN Alert"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Platform Event Trap Generated"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Platform Generated SNMP Trap"},
};

/* Sensor Type: 0x25 - Entity Presence Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x25[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entity Present"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entity Absent"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entity Disabled"},
};

/* Sensor Type: 0x27 - LAN Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x27[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "LAN Heartbeat Lost"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "LAN Heartbeat"},
};

/* Sensor Type: 0x28 - Management Subsystem Health Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x28[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Sensor Access Degraded or Unavailable"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Controller Access Degraded or Unavailable"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Management Controller Off-Line"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Management Controller Unavailable"},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Sensor Failure"},
  {0x04, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, "Failed Sensor Number: "},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Failure"},
  {0x05, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, "Device is not a Logical FRU device"},
  {0x05, 0x80, 0x00, 0x80, 0x00, 0x00, 0x00, "Device is a Logical FRU device"},
  {0x05, 0x18, 0xFF, 0xFF, 0x00, 0x00, 0x00, "LUN for Master Write-Read Command/FRU Command: "},
  {0x05, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, "Device is non-intelligent device directly on IPMB"},

  {0x05, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, "Device directly on IPMB, or device is a logical FRU Device"},
  {0x05, 0x07, 0x00, 0x01, 0x00, 0x00, 0x00, "Private BUS ID: 0x01"},
  {0x05, 0x07, 0x00, 0x02, 0x00, 0x00, 0x00, "Private BUS ID: 0x02"},
  {0x05, 0x07, 0x00, 0x03, 0x00, 0x00, 0x00, "Private BUS ID: 0x03"},
  {0x05, 0x07, 0x00, 0x04, 0x00, 0x00, 0x00, "Private BUS ID: 0x04"},
  {0x05, 0x07, 0x00, 0x05, 0x00, 0x00, 0x00, "Private BUS ID: 0x05"},
  {0x05, 0x07, 0x00, 0x06, 0x00, 0x00, 0x00, "Private BUS ID: 0x06"},
  {0x05, 0x07, 0x00, 0x07, 0x00, 0x00, 0x00, "Private BUS ID: 0x07"},
  /* Based on ED2, the data interpretation for ED3 differs. So print the value as is. */
  {0x05, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, "Event Data 3: "},
};

/* Sensor Type: 0x29 - Battery Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x29[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Battery Low"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Battery Failed"},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Battery Presence Detected"},
};

/* Sensor Type: 0x2A - Session Audit Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x2a[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Session Activated"},
  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Session Deactivated"},
  {0x01, 0x3F, 0x3F, 0x3F, 0x00, 0x00, 0x00, "User ID for user that activated session: "},
  {0x01, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, "Session Deactivation Cause Unspecified"},
  {0x01, 0x00, 0x00, 0x00, 0x30, 0x00, 0x10, "Session Deactivated by Close Session Command"},
  {0x01, 0x00, 0x00, 0x00, 0x30, 0x00, 0x20, "Session Deactivated by Timeout"},
  {0x01, 0x00, 0x00, 0x00, 0x30, 0x00, 0x30, "Session Deactivated by Configuration Change"},
  {0x01, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, "Channel Number Session activated/deactivated: "},
  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Invalid Username or Password"},
  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Invalid Password Disable"},
};

/* Sensor Type: 0x2B - Version Change Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x2b[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Hardware Change Detected with Associated Entity"},
  {0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x00, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x00, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x00, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x00, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x00, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x00, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x00, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x00, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x00, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x00, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x00, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x00, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x00, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x00, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x00, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x00, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x00, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x00, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x00, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x00, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x00, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x00, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x00, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Firmware or Software Change Detected with Associated Entity"},
  {0x01, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x01, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x01, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x01, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x01, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x01, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x01, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x01, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x01, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x01, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x01, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x01, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x01, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x01, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x01, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x01, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x01, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x01, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x01, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x01, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x01, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x01, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x01, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x01, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Hardware Incompatibility Detected With Associated Entity"},
  {0x02, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x02, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x02, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x02, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x02, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x02, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x02, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x02, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x02, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x02, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x02, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x02, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x02, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x02, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x02, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x02, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x02, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x02, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x02, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x02, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x02, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x02, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x02, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x02, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Firmware or Software Incompatibility detected with Associated Entity"},
  {0x03, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x03, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x03, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x03, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x03, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x03, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x03, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x03, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x03, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x03, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x03, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x03, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x03, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x03, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x03, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x03, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x03, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x03, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x03, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x03, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x03, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x03, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x03, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x03, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entity is of an Invalid or Unsupported Firmware or Software Version"},
  {0x04, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x04, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x04, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x04, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x04, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x04, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x04, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x04, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x04, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x04, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x04, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x04, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x04, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x04, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x04, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x04, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x04, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x04, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x04, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x04, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x04, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x04, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x04, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x04, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Entity Contains an Invalid or Unsupported Firmware or Software Version"},
  {0x05, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x05, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x05, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x05, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x05, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x05, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x05, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x05, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x05, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x05, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x05, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x05, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x05, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x05, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x05, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x05, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x05, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x05, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x05, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x05, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x05, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x05, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x05, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x05, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Hardware Change Detected with Associated Entity was Successful"},
  {0x06, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x06, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x06, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x06, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x06, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x06, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x06, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x06, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x06, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x06, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x06, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x06, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x06, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x06, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x06, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x06, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x06, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x06, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x06, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x06, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x06, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x06, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x06, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x06, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},

  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "Software or Firmware Change Detected with Associated Entity was Successful"},
  {0x07, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, "Version change type: Unspecified"},
  {0x07, 0xFF, 0x00, 0x01, 0x00, 0x00, 0x00, "Version change type: Management Controller Device ID"},
  {0x07, 0xFF, 0x00, 0x02, 0x00, 0x00, 0x00, "Version change type: Management Controller Firmware Revision"},
  {0x07, 0xFF, 0x00, 0x03, 0x00, 0x00, 0x00, "Version change type: Management Controller Device Revision"},
  {0x07, 0xFF, 0x00, 0x04, 0x00, 0x00, 0x00, "Version change type: Management Controller Manufacturer ID"},
  {0x07, 0xFF, 0x00, 0x05, 0x00, 0x00, 0x00, "Version change type: Management Controller IPMI Version"},
  {0x07, 0xFF, 0x00, 0x06, 0x00, 0x00, 0x00, "Version change type: Management Controller Auxiliary Firmware ID"},
  {0x07, 0xFF, 0x00, 0x07, 0x00, 0x00, 0x00, "Version change type: Management Controller FirmWare Boot Block"},
  {0x07, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, "Version change type: Other Management Controller Firmware"},
  {0x07, 0xFF, 0x00, 0x09, 0x00, 0x00, 0x00, "Version change type: System Firmware (EFI/BIOS) Change"},
  {0x07, 0xFF, 0x00, 0x0A, 0x00, 0x00, 0x00, "Version change type: SMBIOS Change"},
  {0x07, 0xFF, 0x00, 0x0B, 0x00, 0x00, 0x00, "Version change type: OS Change"},
  {0x07, 0xFF, 0x00, 0x0C, 0x00, 0x00, 0x00, "Version change type: OS Loader Change"},
  {0x07, 0xFF, 0x00, 0x0D, 0x00, 0x00, 0x00, "Version change type: Service or Diagnostic Partition Change"},
  {0x07, 0xFF, 0x00, 0x0E, 0x00, 0x00, 0x00, "Version change type: Management Software Agent Change"},
  {0x07, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, "Version change type: Management Software Application Change"},
  {0x07, 0xFF, 0x00, 0x10, 0x00, 0x00, 0x00, "Version change type: Management Software Middleware Change"},
  {0x07, 0xFF, 0x00, 0x11, 0x00, 0x00, 0x00, "Version change type: Programmable Hardware Change"},
  {0x07, 0xFF, 0x00, 0x12, 0x00, 0x00, 0x00, "Version change type: Board/FRU Module Change"},
  {0x07, 0xFF, 0x00, 0x13, 0x00, 0x00, 0x00, "Version change type: Board/FRU Component Change"},
  {0x07, 0xFF, 0x00, 0x14, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Equivalent Version"},
  {0x07, 0xFF, 0x00, 0x15, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Newer Version"},
  {0x07, 0xFF, 0x00, 0x16, 0x00, 0x00, 0x00, "Version change type: Board/FRU Replaced with Older Version"},
  {0x07, 0xFF, 0x00, 0x17, 0x00, 0x00, 0x00, "Version change type: Board/FRU Hardware Configuration Change"},
};

/* Sensor Type: 0x2C - FRU State Sensor Type. */
static sensor_offset_str_table_t g_sensor_offset_str_table0x2c[] =
{
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Not Installed"},
  {0x00, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x00, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x00, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x00, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x00, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x00, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x00, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x00, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x00, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x00, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x00, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x00, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x00, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Inactive"},
  {0x01, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x01, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x01, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x01, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x01, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x01, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x01, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x01, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x01, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x01, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x01, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x01, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x01, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Activation Requested"},
  {0x02, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x02, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x02, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x02, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x02, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x02, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x02, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x02, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x02, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x02, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x02, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x02, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x02, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Activation In Progress"},
  {0x03, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x03, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x03, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x03, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x03, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x03, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x03, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x03, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x03, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x03, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x03, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x03, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x03, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Active"},
  {0x04, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x04, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x04, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x04, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x04, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x04, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x04, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x04, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x04, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x04, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x04, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x04, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x04, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Deactivation Requested"},
  {0x05, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x05, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x05, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x05, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x05, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x05, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x05, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x05, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x05, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x05, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x05, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x05, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x05, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Deactivation In Progress"},
  {0x06, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x06, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x06, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x06, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x06, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x06, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x06, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x06, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x06, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x06, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x06, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x06, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x06, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "},

  {0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, "FRU Communication Lost"},
  {0x07, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, "Cause of State Change: Normal State Change"},
  {0x07, 0xF0, 0x00, 0x10, 0x00, 0x00, 0x00, "Cause of State Change: Change Commanded By Software External To FRU"},
  {0x07, 0xF0, 0x00, 0x20, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Changing a Handle Latch"},
  {0x07, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To Operator Pressing the Hot Swap Button"},
  {0x07, 0xF0, 0x00, 0x40, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due To FRU Programmatic Action"},
  {0x07, 0xF0, 0x00, 0x50, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost"},
  {0x07, 0xF0, 0x00, 0x60, 0x00, 0x00, 0x00, "Cause of State Change: Communication Lost Due to Local Failure"},
  {0x07, 0xF0, 0x00, 0x70, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Unexpected Extraction"},
  {0x07, 0xF0, 0x00, 0x80, 0x00, 0x00, 0x00, "Cause of State Change: State Change Due to Operator Intervention/Update"},
  {0x07, 0xF0, 0x00, 0x90, 0x00, 0x00, 0x00, "Cause of State Change: Unable To Compute IPMB Address"},
  {0x07, 0xF0, 0x00, 0xA0, 0x00, 0x00, 0x00, "Cause of State Change: Unexpected Deactivation"},
  {0x07, 0xF0, 0x00, 0xF0, 0x00, 0x00, 0x00, "Cause of State Change: Cause Unknown"},
  {0x07, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, "Previous State Offset Value: "}
};

static sensor_type_val_to_desc_str_t g_sensor_type_val_to_desc_str_table[] =
{
  {0x05, "Physical Security", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x05), g_sensor_offset_str_table0x05},
  {0x06, "Platform Security", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x06), g_sensor_offset_str_table0x06},
  {0x07, "Processsor", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x07), g_sensor_offset_str_table0x07},
  {0x08, "Power Supply", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x08), g_sensor_offset_str_table0x08},
  {0x09, "Power Unit", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x09), g_sensor_offset_str_table0x09},
  {0x0C, "Memory", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x0c), g_sensor_offset_str_table0x0c},
  {0x0D, "Drive Slot", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x0d), g_sensor_offset_str_table0x0d},
  {0x0F, "System Firmware Progress", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x0f), g_sensor_offset_str_table0x0f},
  {0x10, "Event Logging Disabled", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x10), g_sensor_offset_str_table0x10},
  {0x12, "System Event", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x12), g_sensor_offset_str_table0x12},
  {0x13, "Critical Interrupt", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x13), g_sensor_offset_str_table0x13},
  {0x14, "Button", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x14), g_sensor_offset_str_table0x14},
  {0x19, "Chip Set", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x19), g_sensor_offset_str_table0x19},
  {0x1B, "Cable", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x1b), g_sensor_offset_str_table0x1b},
  {0x1D, "System Boot", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x1d), g_sensor_offset_str_table0x1d},
  {0x1E, "Boot Error", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x1e), g_sensor_offset_str_table0x1e},
  {0x1F, "Base OS Boot", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x1f), g_sensor_offset_str_table0x1f},
  {0x20, "OS Stop", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x20), g_sensor_offset_str_table0x20},
  {0x21, "Slot", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x21), g_sensor_offset_str_table0x21},
  {0x22, "System ACPI Power State", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x22), g_sensor_offset_str_table0x22},
  {0x23, "Watchdog2", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x23), g_sensor_offset_str_table0x23},
  {0x24, "Platform Alert", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x24), g_sensor_offset_str_table0x24},
  {0x25, "Entity Presence", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x25), g_sensor_offset_str_table0x25},
  {0x27, "LAN", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x27), g_sensor_offset_str_table0x27},
  {0x28, "Management Subsysterm Health", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x28), g_sensor_offset_str_table0x28},
  {0x29, "Battery", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x29), g_sensor_offset_str_table0x29},
  {0x2A, "Session Audit", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x2a), g_sensor_offset_str_table0x2a},
  {0x2B, "Version Change", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x2b), g_sensor_offset_str_table0x2b},
  {0x2C, "Fru State", SENSOR_OFFSET_STRING_TABLE_SIZE(g_sensor_offset_str_table0x2c), g_sensor_offset_str_table0x2c},
};

static sensor_num_val_to_desc_str_t g_sensor_num_val_to_desc_str_table[] = {
  {0x00, "Unspecified"},
  {0x01, "Other"},
  {0x02, "Unknown"},
  {0x03, "Processor"},
  {0x04, "Disk or Disk Bay"},
  {0x05, "Peripheral Bay"},
  {0x06, "System Management Module"},
  {0x07, "System Board"},
  {0x08, "Memory Module"},
  {0x09, "Processor Module"},
  {0x0A, "Power Supply"},
  {0x0B, "Add-in Card"},
  {0x0C, "Front Panel Board"},
  {0x0D, "Back Panel Board"},
  {0x0E, "Power System Board"},
  {0x0F, "Drive Backplane"},
  {0x10, "System Internal Expan. Board"},
  {0x11, "Other System Board"},
  {0x12, "Processor Board"},
  {0x13, "Power Unit/Domain"},
  {0x14, "Power Module (DC-to-DC)"},
  {0x15, "Power Management/Distribution"},
  {0x16, "Chassis Back Panel Board"},
  {0x17, "System Chassis"},
  {0x18, "Sub-Chassis"},
  {0x19, "Other Chassis Board"},
  {0x1A, "Disk Drive Bay"},
  {0x1B, "Peripheral Bay"},
  {0x1C, "Device Bay"},
  {0x1D, "Fan/Cooling Device"},
  {0x1E, "Cooling Unit/Cooling Domain"},
  {0x1F, "Cable/Interconnect"},
  {0x20, "Memory Device"},
  {0x21, "System Management Software"},
  {0x22, "System firmware(BIOS/EFI)"},
  {0x23, "Operating System"},
  {0x24, "System Bus"},
  {0x25, "Group"},
  {0x26, "Remote Manage. Comm. Device"},
  {0x27, "External Environment"},
  {0x28, "Battery"},
  {0x29, "Processing Blade"},
  {0x2A, "Connectivity Switch"},
  {0x2B, "Processor/Memory Module"},
  {0x2C, "I/O Module"},
  {0x2D, "Processor/IO Module"},
  {0x2E, "Management Controller Firmware"},
  {0x2F, "IPMI Channel"},
  {0x30, "PCI Bus"},
  {0x31, "PCI Express Bus"},
  {0x32, "SCSI Bus(Parallel)"},
  {0x33, "SATA/SAS Bus"},
  {0x34, "Processor/Front-Side Bus"},
  {0x35, "Real Time Clock"},
  {0x36, "Reserved"},
  {0x37, "Air Inlet"},
  {0x40, "Air inlet"},
  {0x41, "Processor/CPU"},
  {0x42, "Baseboard/Main System board"},
};

// Helper Functions
static int
read_device(const char *device, int *value) {
  FILE *fp;
  int rc;

  fp = fopen(device, "r");
  if (!fp) {
    int err = errno;
#ifdef DEBUG
    syslog(LOG_INFO, "failed to open device %s", device);
#endif
    return err;
  }

  rc = fscanf(fp, "%i", value);
  fclose(fp);
  if (rc != 1) {
#ifdef DEBUG
    syslog(LOG_INFO, "failed to read device %s", device);
#endif
    return ENOENT;
  } else {
    return 0;
  }
}

// Helper Functions
static int
read_device_float(const char *device, float *value) {
  FILE *fp;
  int rc;

  fp = fopen(device, "r");
  if (!fp) {
    int err = errno;
#ifdef DEBUG
    syslog(LOG_INFO, "failed to open device %s", device);
#endif
    return err;
  }

  rc = fscanf(fp, "%f", value);
  fclose(fp);
  if (rc != 1) {
#ifdef DEBUG
    syslog(LOG_INFO, "failed to read device %s", device);
#endif
    return ENOENT;
  } else {
    return 0;
  }
}

static int
write_device(const char *device, const char *value) {
  FILE *fp;
  int rc;

  fp = fopen(device, "w");
  if (!fp) {
    int err = errno;
#ifdef DEBUG
    syslog(LOG_INFO, "failed to open device for write %s", device);
#endif
    return err;
  }

  rc = fputs(value, fp);
  fclose(fp);

  if (rc < 0) {
#ifdef DEBUG
    syslog(LOG_INFO, "failed to write device %s", device);
#endif
    return ENOENT;
  } else {
    return 0;
  }
}

int
pal_detect_i2c_device(uint8_t bus, uint8_t addr, uint8_t mode, uint8_t force) {

  int fd = -1, rc = -1;
  char fn[32];
  uint32_t funcs;

  snprintf(fn, sizeof(fn), "/dev/i2c-%d", bus);
  fd = open(fn, O_RDWR);
  if (fd == -1) {
    syslog(LOG_WARNING, "Failed to open i2c device %s", fn);
    return I2C_BUS_ERROR;
  }

  if (ioctl(fd, I2C_FUNCS, &funcs) < 0) {
    syslog(LOG_WARNING, "Failed to get %s functionality matrix", fn);
    close(fd);
    return I2C_FUNC_ERROR;
  }

  if (force) {
    if (ioctl(fd, I2C_SLAVE_FORCE, addr)) {
      syslog(LOG_WARNING, "Failed to open slave @ address 0x%x", addr);
      close(fd);
      return I2C_DEVICE_ERROR;
    }
   } else {
    if (ioctl(fd, I2C_SLAVE, addr) < 0) {
      syslog(LOG_WARNING, "Failed to open slave @ address 0x%x", addr);
      close(fd);
      return I2c_DRIVER_EXIST;
    }
  }

  /* Probe this address */
  switch (mode) {
    case MODE_QUICK:
      /* This is known to corrupt the Atmel AT24RF08 EEPROM */
      rc = i2c_smbus_write_quick(fd, I2C_SMBUS_WRITE);
      break;
    case MODE_READ:
      /* This is known to lock SMBus on various
         write-only chips (mainly clock chips) */
      rc = i2c_smbus_read_byte(fd);
      break;
    default:
      if ((addr >= 0x30 && addr <= 0x37) || (addr >= 0x50 && addr <= 0x5F))
        rc = i2c_smbus_read_byte(fd);
      else
        rc = i2c_smbus_write_quick(fd, I2C_SMBUS_WRITE);
  }
  close(fd);

  if (rc < 0) {
    return I2C_DEVICE_ERROR;
  } else {
    return 0;
  }
}

int
pal_add_i2c_device(uint8_t bus, uint8_t addr, char *device_name) {

  int ret = -1;
  char cmd[64];

  snprintf(cmd, sizeof(cmd),
            "echo %s %d > /sys/bus/i2c/devices/i2c-%d/new_device",
              device_name, addr, bus);

#if DEBUG
  syslog(LOG_WARNING, "[%s] Cmd: %s", __func__, cmd);
#endif

  ret = run_command(cmd);

  return ret;
}

int
pal_del_i2c_device(uint8_t bus, uint8_t addr) {

  int ret = -1;
  char cmd[64];

  sprintf(cmd, "echo %d > /sys/bus/i2c/devices/i2c-%d/delete_device",
           addr, bus);

#if DEBUG
  syslog(LOG_WARNING, "[%s] Cmd: %s", __func__, cmd);
#endif

  ret = run_command(cmd);

  return ret;
}

int
pal_get_pim_type(uint8_t fru) {
  int retry = 10, ret = -1, val;
  char path[LARGEST_DEVICE_NAME + 1];
  uint8_t bus = ((fru - FRU_PIM1) * 8) + 80;

  snprintf(path, LARGEST_DEVICE_NAME,
           I2C_SYSFS_DEVICES"/%d-0060/board_ver", bus);

  while ((ret = read_device(path, &val)) != 0 && retry--) {
    msleep(500);
  }
  if (ret) {
    return -1;
  }

#if DEBUG
  syslog(LOG_WARNING, "[%s] val: 0x%x", __func__, val);
#endif

  if (val == 0x0) {
    ret = PIM_TYPE_16Q;
  } else if ((val & 0xf0) == 0xf0) {
    ret = PIM_TYPE_16O;
  } else if (val == 0x10) {
    ret = PIM_TYPE_4DD;
  } else {
    return -1;
  }

  return ret;
}

int
pal_set_pim_type_to_file(uint8_t fru, char *type) {
  char fru_name[16];
  char key[MAX_KEY_LEN];

  pal_get_fru_name(fru, fru_name);
  sprintf(key, "%s_type", fru_name);

  return kv_set(key, type, 0, 0);
}

int
pal_get_pim_type_from_file(uint8_t fru) {
  char fru_name[16];
  char key[MAX_KEY_LEN];
  char type[12] = {0};

  pal_get_fru_name(fru, fru_name);
  sprintf(key, "%s_type", fru_name);

  if (kv_get(key, type, NULL, 0)) {
#if DEBUG
    syslog(LOG_WARNING,
            "pal_get_pim_type_from_file: %s get tpye fail", fru_name);
#endif
    return -1;
  }

  if (!strncmp(type, "16q", sizeof("16q"))) {
    return PIM_TYPE_16Q;
  } else if (!strncmp(type, "16o", sizeof("16o"))) {
    return PIM_TYPE_16O;
  } else if (!strncmp(type, "4dd", sizeof("4dd"))) {
    return PIM_TYPE_4DD;
  } else if (!strncmp(type, "unplug", sizeof("unplug"))) {
    return PIM_TYPE_UNPLUG;
  } else {
    return PIM_TYPE_NONE;
  }
}

static void
pim_thresh_array_init(uint8_t fru) {
  int i = 0;
  int type;

  switch (fru) {
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      i = fru - FRU_PIM1;
      pim_sensor_threshold[PIM1_SENSOR_TEMP1+(i*0x15)][UCR_THRESH] = 70;
      pim_sensor_threshold[PIM1_SENSOR_TEMP2+(i*0x15)][UCR_THRESH] = 80;
      pim_sensor_threshold[PIM1_SENSOR_QSFP_TEMP+i][UCR_THRESH] = 58;
      pim_sensor_threshold[PIM1_SENSOR_HSC_VOLT+(i*0x15)][UCR_THRESH] = 12.6;
      pim_sensor_threshold[PIM1_SENSOR_HSC_VOLT+(i*0x15)][LCR_THRESH] = 11.4;
      pim_sensor_threshold[PIM1_SENSOR_HSC_CURR+(i*0x15)][UCR_THRESH] = 12;
      pim_sensor_threshold[PIM1_SENSOR_HSC_POWER+(i*0x15)][UCR_THRESH] = 144;

      type = pal_get_pim_type_from_file(fru);
      if (type == PIM_TYPE_16Q) {
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][LCR_THRESH] = 1.656;
      } else if (type == PIM_TYPE_16O) {
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][UCR_THRESH] = 5.25;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][LCR_THRESH] = 4.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][UCR_THRESH] = 3.465;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][LCR_THRESH] = 3.135;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][UCR_THRESH] = 1.89;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][LCR_THRESH] = 1.71;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][UCR_THRESH] = 1.155;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][LCR_THRESH] = 1.045;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][UCR_THRESH] = 0.84;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][LCR_THRESH] = 0.76;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][UCR_THRESH] = 0.84;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][LCR_THRESH] = 0.76;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][UCR_THRESH] = 0.84;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][LCR_THRESH] = 0.76;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][UCR_THRESH] = 0.84;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][LCR_THRESH] = 0.76;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][UCR_THRESH] = 0.84;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][LCR_THRESH] = 0.76;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][UCR_THRESH] = 3.465;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][LCR_THRESH] = 3.135;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][UCR_THRESH] = 2.625;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][LCR_THRESH] = 2.375;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][UCR_THRESH] = 1.89;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][LCR_THRESH] = 1.71;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][LCR_THRESH] = -100;
      } else if (type == PIM_TYPE_4DD) {
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT1+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT2+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT3+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT4+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT5+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT6+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT7+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT8+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT9+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT10+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT11+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT12+(i*0x15)][LCR_THRESH] = -100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][UCR_THRESH] = 0.82;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT13+(i*0x15)][LCR_THRESH] = 0.56;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][UCR_THRESH] = 0.864;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT14+(i*0x15)][LCR_THRESH] = 0.75;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][UCR_THRESH] = 1.944;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT15+(i*0x15)][LCR_THRESH] = 1.656;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][UCR_THRESH] = 100;
        pim_sensor_threshold[PIM1_SENSOR_34461_VOLT16+(i*0x15)][LCR_THRESH] = -100;
      }
      break;
  }
}

int
pal_set_pim_thresh(uint8_t fru) {
  uint8_t snr_num;

  pim_thresh_array_init(fru);

  switch(fru) {
    case FRU_PIM1:
      for (snr_num = PIM1_SENSOR_TEMP1;
           snr_num <= PIM1_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM2:
      for (snr_num = PIM2_SENSOR_TEMP1;
           snr_num <= PIM2_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM3:
      for (snr_num = PIM3_SENSOR_TEMP1;
           snr_num <= PIM3_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM4:
      for (snr_num = PIM4_SENSOR_TEMP1;
           snr_num <= PIM4_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM5:
      for (snr_num = PIM5_SENSOR_TEMP1;
           snr_num <= PIM5_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM6:
      for (snr_num = PIM6_SENSOR_TEMP1;
           snr_num <= PIM6_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM7:
      for (snr_num = PIM7_SENSOR_TEMP1;
           snr_num <= PIM7_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
    case FRU_PIM8:
      for (snr_num = PIM8_SENSOR_TEMP1;
           snr_num <= PIM8_SENSOR_34461_VOLT16; snr_num++) {
        pal_sensor_thresh_modify(fru, snr_num, UCR_THRESH,
                             pim_sensor_threshold[snr_num][UCR_THRESH]);
        pal_sensor_thresh_modify(fru, snr_num, LCR_THRESH,
                             pim_sensor_threshold[snr_num][LCR_THRESH]);
      }
      break;
      default:
        return -1;
  }

  return 0;
}

int
pal_clear_thresh_value(uint8_t fru) {
  int ret;
  char fpath[64] = {0};
  char cmd[128] = {0};
  char fruname[16] = {0};

  ret = pal_get_fru_name(fru, fruname);
  if (ret < 0) {
    printf("%s: Fail to get fru%d name\n",__func__,fru);
    return ret;
  }

  memset(fpath, 0, sizeof(fpath));
  sprintf(fpath, THRESHOLD_BIN, fruname);
  sprintf(cmd,"rm -rf %s",fpath);
  system(cmd);

  memset(fpath, 0, sizeof(fpath));
  sprintf(fpath, THRESHOLD_RE_FLAG, fruname);
  sprintf(cmd,"touch %s",fpath);
  system(cmd);

  return 0;
}

void
pal_inform_bic_mode(uint8_t fru, uint8_t mode) {
  switch(mode) {
  case BIC_MODE_NORMAL:
    // Bridge IC entered normal mode
    // Inform BIOS that BMC is ready
    bic_set_gpio(fru, BMC_READY_N, 0);
    break;
  case BIC_MODE_UPDATE:
    // Bridge IC entered update mode
    // TODO: Might need to handle in future
    break;
  default:
    break;
  }
}

//For OEM command "CMD_OEM_GET_PLAT_INFO" 0x7e
int
pal_get_plat_sku_id(void){
  return 0x06; // Minipack
}


//Use part of the function for OEM Command "CMD_OEM_GET_POSS_PCIE_CONFIG" 0xF4
int
pal_get_poss_pcie_config(uint8_t slot, uint8_t *req_data, uint8_t req_len,
                         uint8_t *res_data, uint8_t *res_len) {

  uint8_t completion_code = CC_SUCCESS;
  uint8_t pcie_conf = 0x02;//Minipack
  uint8_t *data = res_data;

  *data++ = pcie_conf;
  *res_len = data - res_data;
  return completion_code;
}

static int
pal_key_check(char *key) {
  int i;

  i = 0;
  while(strcmp(key_list[i], LAST_KEY)) {
    // If Key is valid, return success
    if (!strcmp(key, key_list[i]))
      return 0;

    i++;
  }

#ifdef DEBUG
  syslog(LOG_WARNING, "pal_key_check: invalid key - %s", key);
#endif
  return -1;
}

int
pal_get_key_value(char *key, char *value) {
  int ret;
  // Check is key is defined and valid
  if (pal_key_check(key))
    return -1;

  ret = kv_get(key, value, NULL, KV_FPERSIST);
  return ret;
}

int
pal_set_key_value(char *key, char *value) {

  // Check is key is defined and valid
  if (pal_key_check(key))
    return -1;

  return kv_set(key, value, 0, KV_FPERSIST);
}

int
pal_set_sysfw_ver(uint8_t slot, uint8_t *ver) {
  int i;
  char key[MAX_KEY_LEN];
  char str[MAX_VALUE_LEN] = {0};
  char tstr[10];
  sprintf(key, "%s", "sysfw_ver_server");

  for (i = 0; i < SIZE_SYSFW_VER; i++) {
    sprintf(tstr, "%02x", ver[i]);
    strcat(str, tstr);
  }

  return pal_set_key_value(key, str);
}

int
pal_get_sysfw_ver(uint8_t slot, uint8_t *ver) {
  int i;
  int j = 0;
  int ret;
  int msb, lsb;
  char key[MAX_KEY_LEN];
  char str[MAX_VALUE_LEN] = {0};
  char tstr[4];

  sprintf(key, "%s", "sysfw_ver_server");

  ret = pal_get_key_value(key, str);
  if (ret) {
    return ret;
  }

  for (i = 0; i < 2*SIZE_SYSFW_VER; i += 2) {
    sprintf(tstr, "%c\n", str[i]);
    msb = strtol(tstr, NULL, 16);

    sprintf(tstr, "%c\n", str[i+1]);
    lsb = strtol(tstr, NULL, 16);
    ver[j++] = (msb << 4) | lsb;
  }

  return 0;
}

int
pal_get_fru_list(char *list) {
  strcpy(list, pal_fru_list);
  return 0;
}

int
pal_get_fru_id(char *str, uint8_t *fru) {
  if (!strcmp(str, "all")) {
    *fru = FRU_ALL;
  } else if (!strcmp(str, "smb")) {
    *fru = FRU_SMB;
  } else if (!strcmp(str, "scm")) {
    *fru = FRU_SCM;
  } else if (!strcmp(str, "pim1")) {
    *fru = FRU_PIM1;
  } else if (!strcmp(str, "pim2")) {
    *fru = FRU_PIM2;
  } else if (!strcmp(str, "pim3")) {
    *fru = FRU_PIM3;
  } else if (!strcmp(str, "pim4")) {
    *fru = FRU_PIM4;
  } else if (!strcmp(str, "pim5")) {
    *fru = FRU_PIM5;
  } else if (!strcmp(str, "pim6")) {
    *fru = FRU_PIM6;
  } else if (!strcmp(str, "pim7")) {
    *fru = FRU_PIM7;
  } else if (!strcmp(str, "pim8")) {
    *fru = FRU_PIM8;
  } else if (!strcmp(str, "psu1")) {
    *fru = FRU_PSU1;
  } else if (!strcmp(str, "psu2")) {
    *fru = FRU_PSU2;
  } else if (!strcmp(str, "psu3")) {
    *fru = FRU_PSU3;
  } else if (!strcmp(str, "psu4")) {
    *fru = FRU_PSU4;
  } else if (!strcmp(str, "fan1")) {
    *fru = FRU_FAN1;
  } else if (!strcmp(str, "fan2")) {
    *fru = FRU_FAN2;
  } else if (!strcmp(str, "fan3")) {
    *fru = FRU_FAN3;
  } else if (!strcmp(str, "fan4")) {
    *fru = FRU_FAN4;
  } else if (!strcmp(str, "fan5")) {
    *fru = FRU_FAN5;
  } else if (!strcmp(str, "fan6")) {
    *fru = FRU_FAN6;
  } else if (!strcmp(str, "fan7")) {
    *fru = FRU_FAN7;
  } else if (!strcmp(str, "fan8")) {
    *fru = FRU_FAN8;
  } else {
    syslog(LOG_WARNING, "pal_get_fru_id: Wrong fru#%s", str);
    return -1;
  }

  return 0;
}

int
pal_get_fru_name(uint8_t fru, char *name) {
  switch(fru) {
    case FRU_SMB:
      strcpy(name, "smb");
      break;
    case FRU_SCM:
      strcpy(name, "scm");
      break;
    case FRU_PIM1:
      strcpy(name, "pim1");
      break;
    case FRU_PIM2:
      strcpy(name, "pim2");
      break;
    case FRU_PIM3:
      strcpy(name, "pim3");
      break;
    case FRU_PIM4:
      strcpy(name, "pim4");
      break;
    case FRU_PIM5:
      strcpy(name, "pim5");
      break;
    case FRU_PIM6:
      strcpy(name, "pim6");
      break;
    case FRU_PIM7:
      strcpy(name, "pim7");
      break;
    case FRU_PIM8:
      strcpy(name, "pim8");
      break;
    case FRU_PSU1:
      strcpy(name, "psu1");
      break;
    case FRU_PSU2:
      strcpy(name, "psu2");
      break;
    case FRU_PSU3:
      strcpy(name, "psu3");
      break;
    case FRU_PSU4:
      strcpy(name, "psu4");
      break;
    case FRU_FAN1:
      strcpy(name, "fan1");
      break;
    case FRU_FAN2:
      strcpy(name, "fan2");
      break;
    case FRU_FAN3:
      strcpy(name, "fan3");
      break;
    case FRU_FAN4:
      strcpy(name, "fan4");
      break;
    case FRU_FAN5:
      strcpy(name, "fan5");
      break;
    case FRU_FAN6:
      strcpy(name, "fan6");
      break;
    case FRU_FAN7:
      strcpy(name, "fan7");
      break;
    case FRU_FAN8:
      strcpy(name, "fan8");
      break;
    default:
      if (fru > MAX_NUM_FRUS)
        return -1;
      sprintf(name, "fru%d", fru);
      break;
  }
  return 0;
}

// Platform Abstraction Layer (PAL) Functions
int
pal_get_platform_name(char *name) {
  strcpy(name, PLATFORM_NAME);

  return 0;
}

int
pal_is_fru_prsnt(uint8_t fru, uint8_t *status) {
  int val;
  char tmp[LARGEST_DEVICE_NAME];
  char path[LARGEST_DEVICE_NAME + 1];
  *status = 0;

  switch (fru) {
    case FRU_SMB:
      *status = 1;
      return 0;
    case FRU_SCM:
      snprintf(path, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, SCM_PRSNT_STATUS);
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, PIM_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, fru - 2);
      break;
    case FRU_PSU1:
      snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, PSU_L_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, 2);
      break;
    case FRU_PSU2:
      snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, PSU_L_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, 1);
      break;
    case FRU_PSU3:
      snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, PSU_R_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, 2);
      break;
    case FRU_PSU4:
      snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, PSU_R_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, 1);
      break;
    case FRU_FAN1:
    case FRU_FAN3:
    case FRU_FAN5:
    case FRU_FAN7:
      snprintf(tmp, LARGEST_DEVICE_NAME,
               TOP_FCMCPLD_PATH_FMT, FAN_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, ((fru - 14) / 2) + 1);
      break;
    case FRU_FAN2:
    case FRU_FAN4:
    case FRU_FAN6:
    case FRU_FAN8:
      snprintf(tmp, LARGEST_DEVICE_NAME,
               BOTTOM_FCMCPLD_PATH_FMT, FAN_PRSNT_STATUS);
      snprintf(path, LARGEST_DEVICE_NAME, tmp, (fru - 14) / 2);
      break;
    default:
      return -1;
    }

    if (read_device(path, &val)) {
      return -1;
    }

    if (val == 0x0) {
      *status = 1;
    } else {
      *status = 0;
    }
  return 0;
}

int
pal_is_fru_ready(uint8_t fru, uint8_t *status) {
  *status = 1;

  return 0;
}

int
pal_get_fru_sensor_list(uint8_t fru, uint8_t **sensor_list, int *cnt) {
  switch(fru) {
  case FRU_SCM:
    *sensor_list = (uint8_t *) scm_all_sensor_list;
    *cnt = scm_all_sensor_cnt;
    break;
  case FRU_SMB:
    *sensor_list = (uint8_t *) smb_sensor_list;
    *cnt = smb_sensor_cnt;
    break;
  case FRU_PIM1:
    *sensor_list = (uint8_t *) pim1_sensor_list;
    *cnt = pim1_sensor_cnt;
    break;
  case FRU_PIM2:
    *sensor_list = (uint8_t *) pim2_sensor_list;
    *cnt = pim2_sensor_cnt;
    break;
  case FRU_PIM3:
    *sensor_list = (uint8_t *) pim3_sensor_list;
    *cnt = pim3_sensor_cnt;
    break;
  case FRU_PIM4:
    *sensor_list = (uint8_t *) pim4_sensor_list;
    *cnt = pim4_sensor_cnt;
    break;
  case FRU_PIM5:
    *sensor_list = (uint8_t *) pim5_sensor_list;
    *cnt = pim5_sensor_cnt;
    break;
  case FRU_PIM6:
    *sensor_list = (uint8_t *) pim6_sensor_list;
    *cnt = pim6_sensor_cnt;
    break;
  case FRU_PIM7:
    *sensor_list = (uint8_t *) pim7_sensor_list;
    *cnt = pim7_sensor_cnt;
    break;
  case FRU_PIM8:
    *sensor_list = (uint8_t *) pim8_sensor_list;
    *cnt = pim8_sensor_cnt;
    break;
  case FRU_PSU1:
    *sensor_list = (uint8_t *) psu1_sensor_list;
    *cnt = psu1_sensor_cnt;
    break;
  case FRU_PSU2:
    *sensor_list = (uint8_t *) psu2_sensor_list;
    *cnt = psu2_sensor_cnt;
    break;
  case FRU_PSU3:
    *sensor_list = (uint8_t *) psu3_sensor_list;
    *cnt = psu3_sensor_cnt;
    break;
  case FRU_PSU4:
    *sensor_list = (uint8_t *) psu4_sensor_list;
    *cnt = psu4_sensor_cnt;
    break;
  default:
    if (fru > MAX_NUM_FRUS)
      return -1;
    // Nothing to read yet.
    *sensor_list = NULL;
    *cnt = 0;
  }
  return 0;
}

void
pal_update_ts_sled(void)
{
  char key[MAX_KEY_LEN];
  char tstr[MAX_VALUE_LEN] = {0};
  struct timespec ts;

  clock_gettime(CLOCK_REALTIME, &ts);
  sprintf(tstr, "%lld", ts.tv_sec);

  sprintf(key, "timestamp_sled");

  pal_set_key_value(key, tstr);
}

int
pal_get_fru_discrete_list(uint8_t fru, uint8_t **sensor_list, int *cnt) {
  switch(fru) {
  case FRU_SCM:
    *sensor_list = (uint8_t *) bic_discrete_list;
    *cnt = bic_discrete_cnt;
    break;
  default:
    if (fru > MAX_NUM_FRUS)
      return -1;
    // Nothing to read yet.
    *sensor_list = NULL;
    *cnt = 0;
  }
    return 0;
}

static void
_print_sensor_discrete_log(uint8_t fru, uint8_t snr_num, char *snr_name,
    uint8_t val, char *event) {
  if (val) {
    syslog(LOG_CRIT, "ASSERT: %s discrete - raised - FRU: %d, num: 0x%X,"
        " snr: %-16s val: %d", event, fru, snr_num, snr_name, val);
  } else {
    syslog(LOG_CRIT, "DEASSERT: %s discrete - settled - FRU: %d, num: 0x%X,"
        " snr: %-16s val: %d", event, fru, snr_num, snr_name, val);
  }
  pal_update_ts_sled();
}

int
pal_sensor_discrete_check(uint8_t fru, uint8_t snr_num, char *snr_name,
    uint8_t o_val, uint8_t n_val) {

  char name[32], crisel[128];
  bool valid = false;
  uint8_t diff = o_val ^ n_val;

  if (GETBIT(diff, 0)) {
    if (fru == FRU_SCM) {
      switch(snr_num) {
        case BIC_SENSOR_SYSTEM_STATUS:
          snprintf(name, sizeof(name), "SOC_Thermal_Trip");
          valid = true;
          snprintf(crisel, sizeof(crisel), "%s - %s,FRU:%u",
                          name, GETBIT(n_val, 0)?"ASSERT":"DEASSERT", fru);
          pal_add_cri_sel(crisel);
          break;
        case BIC_SENSOR_VR_HOT:
          snprintf(name, sizeof(name), "SOC_VR_Hot");
          valid = true;
          break;
      }
      if (valid) {
        _print_sensor_discrete_log(fru, snr_num, snr_name,
                                        GETBIT(n_val, 0), name);
        valid = false;
      }
    }
  }

  if (GETBIT(diff, 1)) {
    if (fru == FRU_SCM) {
      switch(snr_num) {
        case BIC_SENSOR_SYSTEM_STATUS:
          snprintf(name, sizeof(name), "SOC_FIVR_Fault");
          valid = true;
          break;
        case BIC_SENSOR_VR_HOT:
          snprintf(name, sizeof(name), "SOC_DIMM_AB_VR_Hot");
          valid = true;
          break;
        case BIC_SENSOR_CPU_DIMM_HOT:
          snprintf(name, sizeof(name), "SOC_MEMHOT");
          valid = true;
          break;
      }
      if (valid) {
        _print_sensor_discrete_log(fru, snr_num, snr_name,
                                        GETBIT(n_val, 1), name);
        valid = false;
      }
    }
  }

  if (GETBIT(diff, 2)) {
    if (fru == FRU_SCM) {
      switch(snr_num) {
        case BIC_SENSOR_SYSTEM_STATUS:
          snprintf(name, sizeof(name), "SYS_Throttle");
          valid = true;
          break;
        case BIC_SENSOR_VR_HOT:
          snprintf(name, sizeof(name), "SOC_DIMM_DE_VR_Hot");
          valid = true;
          break;
      }
      if (valid) {
        _print_sensor_discrete_log(fru, snr_num, snr_name,
                                        GETBIT(n_val, 2), name);
        valid = false;
      }
    }
  }

  if (GETBIT(diff, 4)) {
    if (fru == FRU_SCM) {
      if (snr_num == BIC_SENSOR_PROC_FAIL) {
          _print_sensor_discrete_log(fru, snr_num, snr_name,
                                          GETBIT(n_val, 4), "FRB3");
      }
    }
  }

  return 0;
}

int
pal_is_debug_card_prsnt(uint8_t *status) {
  int val;
  char path[LARGEST_DEVICE_NAME + 1];

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_SCM_USB_PRSNT, "value");

  if (read_device(path, &val)) {
    return -1;
  }

  if (val) {
    *status = 1;
  } else {
    *status = 0;
  }

  return 0;
}

// Enable POST buffer for the server in given slot
int
pal_post_enable(uint8_t slot) {
  int ret;

  bic_config_t config = {0};
  bic_config_u *t = (bic_config_u *) &config;

  ret = bic_get_config(IPMB_BUS, &config);
  if (ret) {
#ifdef DEBUG
    syslog(LOG_WARNING,
           "post_enable: bic_get_config failed for fru: %d\n", slot);
#endif
    return ret;
  }

  if (0 == t->bits.post) {
    t->bits.post = 1;
    ret = bic_set_config(IPMB_BUS, &config);
    if (ret) {
#ifdef DEBUG
      syslog(LOG_WARNING, "post_enable: bic_set_config failed\n");
#endif
      return ret;
    }
  }

  return 0;
}

// Disable POST buffer for the server in given slot
int
pal_post_disable(uint8_t slot) {
  int ret;

  bic_config_t config = {0};
  bic_config_u *t = (bic_config_u *) &config;

  ret = bic_get_config(IPMB_BUS, &config);
  if (ret) {
    return ret;
  }

  t->bits.post = 0;

  ret = bic_set_config(IPMB_BUS, &config);
  if (ret) {
    return ret;
  }

  return 0;
}

// Get the last post code of the given slot
int
pal_post_get_last(uint8_t slot, uint8_t *status) {
  int ret;
  uint8_t buf[MAX_IPMB_RES_LEN] = {0x0};
  uint8_t len;


  ret = bic_get_post_buf(IPMB_BUS, buf, &len);
  if (ret) {
    return ret;
  }

  *status = buf[0];

  return 0;
}

// Display the given POST code using GPIO port
static int
pal_post_display(uint8_t status) {
  char path[LARGEST_DEVICE_NAME + 1];
  int ret;
  char *val;

#ifdef DEBUG
  syslog(LOG_WARNING, "pal_post_display: status is %d\n", status);
#endif

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_0, "value");
  if (BIT(status, 0)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_1, "value");
  if (BIT(status, 1)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_2, "value");
  if (BIT(status, 2)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_3, "value");
  if (BIT(status, 3)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_4, "value");
  if (BIT(status, 4)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_5, "value");
  if (BIT(status, 5)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_6, "value");
  if (BIT(status, 6)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_POSTCODE_7, "value");
  if (BIT(status, 7)) {
    val = "1";
  } else {
    val = "0";
  }

  ret = write_device(path, val);
  if (ret) {
    goto post_exit;
  }

post_exit:
  if (ret) {
#ifdef DEBUG
    syslog(LOG_WARNING, "write_device failed for %s\n", path);
#endif
    return -1;
  } else {
    return 0;
  }
}

// Handle the received post code, for now display it on debug card
int
pal_post_handle(uint8_t slot, uint8_t status) {
  uint8_t prsnt, pos;
  int ret;

  // Check for debug card presence
  ret = pal_is_debug_card_prsnt(&prsnt);
  if (ret) {
    return ret;
  }

  // No debug card present, return
  if (!prsnt) {
    return 0;
  }

  // Get the hand switch position
  ret = pal_get_hand_sw(&pos);
  if (ret) {
    return ret;
  }

  /* If the give server is not selected, return */
  if (pos != HAND_SW_SERVER) {
    return 0;
  }

  /* Enable POST codes for SCM slot */
  ret = pal_post_enable(slot);
  if (ret) {
    return ret;
  }

  // Display the post code in the debug card
  ret = pal_post_display(status);
  if (ret) {
    return ret;
  }

  return 0;
}

// Return the Front panel Power Button
int
pal_get_board_rev(int *rev) {
  char path[LARGEST_DEVICE_NAME + 1];
  int val_id_0, val_id_1, val_id_2;

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_SMB_REV_ID_0, "value");
  if (read_device(path, &val_id_0)) {
    return -1;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_SMB_REV_ID_1, "value");
  if (read_device(path, &val_id_1)) {
    return -1;
  }

  snprintf(path, LARGEST_DEVICE_NAME, GPIO_SMB_REV_ID_2, "value");
  if (read_device(path, &val_id_2)) {
    return -1;
  }

  *rev = val_id_0 | (val_id_1 << 1) | (val_id_2 << 2);
  syslog(LOG_ERR, "Board rev: %d\n", *rev);

  return 0;
}

int
pal_get_cpld_board_rev(int *rev, const char *device) {
  char full_name[LARGEST_DEVICE_NAME + 1];

  snprintf(full_name, LARGEST_DEVICE_NAME, device, "board_ver");
  if (read_device(full_name, rev)) {
    return -1;
  }

  return 0;
}

int
pal_set_last_pwr_state(uint8_t fru, char *state) {

  int ret;
  char key[MAX_KEY_LEN];

  sprintf(key, "%s", "pwr_server_last_state");

  ret = pal_set_key_value(key, state);
  if (ret < 0) {
#ifdef DEBUG
    syslog(LOG_WARNING, "pal_set_last_pwr_state: pal_set_key_value failed for "
        "fru %u", fru);
#endif
  }
  return ret;
}

int
pal_get_last_pwr_state(uint8_t fru, char *state) {
  int ret;
  char key[MAX_KEY_LEN];

  sprintf(key, "%s", "pwr_server_last_state");

  ret = pal_get_key_value(key, state);
  if (ret < 0) {
#ifdef DEBUG
    syslog(LOG_WARNING, "pal_get_last_pwr_state: pal_get_key_value failed for "
      "fru %u", fru);
#endif
  }
  return ret;
}

int
pal_set_com_pwr_btn_n(char *status) {
  int ret;

  ret = write_device(SCM_COM_PWR_BTN, status);
  if (ret) {
#ifdef DEBUG
  syslog(LOG_WARNING, "write_device failed for %s\n", SCM_COM_PWR_BTN);
#endif
    return -1;
  }

  return 0;
}

static bool
is_server_on(void) {
  int ret;
  uint8_t status;

  ret = pal_get_server_power(FRU_SCM, &status);
  if (ret || status != SERVER_POWER_ON) {
    return false;
  }

  return true;
}

// Power On the server
static int
server_power_on(void) {
  int ret, val;

  ret = read_device(SCM_COM_PWR_ENBLE, &val);
  if (ret || val) {
    if (pal_set_com_pwr_btn_n("1")) {
      return -1;
    }

    if (pal_set_com_pwr_btn_n("0")) {
      return -1;
    }
    sleep(1);

    if (pal_set_com_pwr_btn_n("1")) {
      return -1;
    }
    /* Wait for server power good ready */
    sleep(1);

    if (!is_server_on()) {
      return -1;
    }
  } else {
    ret = write_device(SCM_COM_PWR_ENBLE, "1");
    if (ret) {
      syslog(LOG_WARNING, "%s: Power on is failed", __func__);
      return -1;
    }
  }

  return 0;
}

// Power Off the server in given slot
static int
server_power_off(bool gs_flag) {
  int ret;

  if (gs_flag) {
    ret = pal_set_com_pwr_btn_n("0");
    if (ret) {
      return -1;
    }
    sleep(DELAY_GRACEFUL_SHUTDOWN);

    ret = pal_set_com_pwr_btn_n("1");
    if (ret) {
      return -1;
    }
  } else {
    ret = write_device(SCM_COM_PWR_ENBLE, "0");
    if (ret) {
      syslog(LOG_WARNING, "%s: Power off is failed",__func__);
      return -1;
    }
  }

  return 0;
}

int
pal_get_server_power(uint8_t slot_id, uint8_t *status) {

  int ret;
  char value[MAX_VALUE_LEN];
  bic_gpio_t gpio;
  uint8_t retry = MAX_READ_RETRY;

  /* check if the CPU is turned on or not */
  while (retry) {
    ret = bic_get_gpio(IPMB_BUS, &gpio);
    if (!ret)
      break;
    msleep(50);
    retry--;
  }
  if (ret) {
    // Check for if the BIC is irresponsive due to 12V_OFF or 12V_CYCLE
    syslog(LOG_INFO, "pal_get_server_power: bic_get_gpio returned error hence"
        " reading the kv_store for last power state  for fru %d", slot_id);
    pal_get_last_pwr_state(slot_id, value);
    if (!(strncmp(value, "off", strlen("off")))) {
      *status = SERVER_POWER_OFF;
    } else if (!(strncmp(value, "on", strlen("on")))) {
      *status = SERVER_POWER_ON;
    } else {
      return ret;
    }
    return 0;
  }

  if (gpio.pwrgood_cpu) {
    *status = SERVER_POWER_ON;
  } else {
    *status = SERVER_POWER_OFF;
  }

  return 0;
}

// Power Off, Power On, or Power Reset the server in given slot
int
pal_set_server_power(uint8_t slot_id, uint8_t cmd) {
  int ret;
  uint8_t status;
  bool gs_flag = false;

  if (pal_get_server_power(slot_id, &status) < 0) {
    return -1;
  }

  switch(cmd) {
    case SERVER_POWER_ON:
      if (status == SERVER_POWER_ON)
        return 1;
      else
        return server_power_on();
      break;

    case SERVER_POWER_OFF:
      if (status == SERVER_POWER_OFF)
        return 1;
      else
        return server_power_off(gs_flag);
      break;

    case SERVER_POWER_CYCLE:
      if (status == SERVER_POWER_ON) {
        if (server_power_off(gs_flag))
          return -1;

        sleep(DELAY_POWER_CYCLE);

        return server_power_on();

      } else if (status == SERVER_POWER_OFF) {

        return (server_power_on());
      }
      break;

    case SERVER_POWER_RESET:
      if (status == SERVER_POWER_ON) {
        ret = pal_set_rst_btn(slot_id, 0);
        if (ret < 0) {
          syslog(LOG_CRIT, "Micro-server can't power reset");
          return ret;
        }
        msleep(100); //some server miss to detect a quick pulse, so delay 100ms between low high
        ret = pal_set_rst_btn(slot_id, 1);
        if (ret < 0) {
          syslog(LOG_CRIT, "Micro-server in reset state, "
                           "can't go back to normal state");
          return ret;
        }
      } else if (status == SERVER_POWER_OFF) {
          syslog(LOG_CRIT, "Micro-server power status is off, "
                            "ignore power reset action");
        return -2;
      }
      break;

    case SERVER_GRACEFUL_SHUTDOWN:
      if (status == SERVER_POWER_OFF) {
        return 1;
      } else {
        gs_flag = true;
        return server_power_off(gs_flag);
      }
      break;

    default:
      return -1;
  }

  return 0;
}

static int
get_current_dir(const char *device, char *dir_name) {
  char cmd[LARGEST_DEVICE_NAME + 1];
  FILE *fp;
  int ret=-1;
  int size;

  // Get current working directory
  snprintf(
      cmd, LARGEST_DEVICE_NAME, "cd %s;pwd", device);

  fp = popen(cmd, "r");
  if(NULL == fp)
     return -1;
  fgets(dir_name, LARGEST_DEVICE_NAME, fp);

  ret = pclose(fp);
  if(-1 == ret)
     syslog(LOG_ERR, "%s pclose() fail ", __func__);

  // Remove the newline character at the end
  size = strlen(dir_name);
  dir_name[size-1] = '\0';

  return 0;
}

static int
check_and_read_sensor_value(uint8_t fru, uint8_t snr_num, const char *device,
                            const char *attr, int *value) {
  char dir_name[LARGEST_DEVICE_NAME + 1];

  if (strlen(snr_path[fru][snr_num].name) > 0) {
    if (!read_device(snr_path[fru][snr_num].name, value))
      return 0;
  }

  if (strstr(device, "hwmon*") != NULL) {
    /* Get current working directory */
    if (get_current_dir(device, dir_name)) {
      return -1;
    }
    snprintf(snr_path[fru][snr_num].name, sizeof(snr_path[fru][snr_num].name),
             "%s/%s", dir_name, attr);
  } else {
    snprintf(snr_path[fru][snr_num].name, sizeof(snr_path[fru][snr_num].name),
             "%s/%s", device, attr);
  }

  if (read_device(snr_path[fru][snr_num].name, value)) {
    return -1;
  }

  return 0;
}

static int
read_attr(uint8_t fru, uint8_t snr_num, const char *device,
          const char *attr, float *value) {
  int tmp;

  if (check_and_read_sensor_value(fru, snr_num, device, attr, &tmp))
    return -1;

  *value = ((float)tmp)/UNIT_DIV;

  return 0;
}

static int
read_hsc_attr(uint8_t fru, uint8_t snr_num, const char *device,
              const char* attr, float r_sense, float *value) {
  int tmp;

  if (check_and_read_sensor_value(fru, snr_num, device, attr, &tmp))
    return -1;

  *value = ((float)tmp)/r_sense/UNIT_DIV;

  return 0;
}

static int
read_hsc_volt(uint8_t fru, uint8_t snr_num,
              const char *device, float r_sense, float *value) {
  return read_hsc_attr(fru, snr_num, device, VOLT(1), r_sense, value);
}

static int
read_hsc_curr(uint8_t fru, uint8_t snr_num,
              const char *device, float r_sense, float *value) {
  return read_hsc_attr(fru, snr_num, device, CURR(1), r_sense, value);
}

static int
read_hsc_power(uint8_t fru, uint8_t snr_num,
               const char *device, float r_sense, float *value) {
  return read_hsc_attr(fru, snr_num, device, POWER(1), r_sense, value);
}

static int
read_fan_rpm_f(const char *device, uint8_t fan, float *value) {
  char full_name[LARGEST_DEVICE_NAME + 1];
  char device_name[11];
  int tmp;

  snprintf(device_name, 11, "fan%d_input", fan);
  snprintf(full_name, sizeof(full_name), "%s/%s", device, device_name);
  if (read_device(full_name, &tmp)) {
    return -1;
  }

  *value = (float)tmp;

  return 0;
}

static int
read_fan_rpm(const char *device, uint8_t fan, int *value) {
  char full_name[LARGEST_DEVICE_NAME + 1];
  char device_name[13];
  int tmp;

  snprintf(device_name, sizeof(device_name), "fan%d_input", fan);
  snprintf(full_name, sizeof(full_name), "%s/%s", device, device_name);
  if (read_device(full_name, &tmp)) {
    return -1;
  }

  *value = tmp;

  return 0;
}

int
pal_get_fan_speed(uint8_t fan, int *rpm) {

  if (fan > 15) {
    syslog(LOG_INFO, "get_fan_speed: invalid fan#:%d", fan);
    return -1;
  }
  if (fan <= 7) {
    fan = fan + 1;
    return read_fan_rpm(SMB_FCM_T_TACH_DEVICE, (fan + 1), rpm);
  } else {
    return read_fan_rpm(SMB_FCM_B_TACH_DEVICE, (fan - 7), rpm);
  }
}

static int
bic_sensor_sdr_path(uint8_t fru, char *path) {

  char fru_name[16];

  switch(fru) {
    case FRU_SCM:
      sprintf(fru_name, "%s", "scm");
      break;
    default:
  #ifdef DEBUG
      syslog(LOG_WARNING, "bic_sensor_sdr_path: Wrong Slot ID\n");
  #endif
      return -1;
  }

  sprintf(path, MINIPACK_SDR_PATH, fru_name);

  if (access(path, F_OK) == -1) {
    return -1;
  }

  return 0;
}

/* Populates all sensor_info_t struct using the path to SDR dump */
static int
sdr_init(char *path, sensor_info_t *sinfo) {
  int fd;
  int ret = 0;
  uint8_t buf[sizeof(sdr_full_t)] = {0};
  uint8_t bytes_rd = 0;
  uint8_t snr_num = 0;
  sdr_full_t *sdr;

  while (access(path, F_OK) == -1) {
    sleep(5);
  }

  fd = open(path, O_RDONLY);
  if (fd < 0) {
    syslog(LOG_ERR, "%s: open failed for %s\n", __func__, path);
    return -1;
  }

  ret = pal_flock_retry(fd);
  if (ret == -1) {
   syslog(LOG_WARNING, "%s: failed to flock on %s", __func__, path);
   close(fd);
   return -1;
  }

  while ((bytes_rd = read(fd, buf, sizeof(sdr_full_t))) > 0) {
    if (bytes_rd != sizeof(sdr_full_t)) {
      syslog(LOG_ERR, "%s: read returns %d bytes\n", __func__, bytes_rd);
      pal_unflock_retry(fd);
      close(fd);
      return -1;
    }

    sdr = (sdr_full_t *) buf;
    snr_num = sdr->sensor_num;
    sinfo[snr_num].valid = true;
    memcpy(&sinfo[snr_num].sdr, sdr, sizeof(sdr_full_t));
  }

  ret = pal_unflock_retry(fd);
  if (ret == -1) {
    syslog(LOG_WARNING, "%s: failed to unflock on %s", __func__, path);
    close(fd);
    return -1;
  }

  close(fd);
  return 0;
}

static int
bic_sensor_sdr_init(uint8_t fru, sensor_info_t *sinfo) {
  char path[64];
  int retry = 0;

  switch(fru) {
    case FRU_SCM:
      if (bic_sensor_sdr_path(fru, path) < 0) {
#ifdef DEBUG
        syslog(LOG_WARNING,
               "bic_sensor_sdr_path: get_fru_sdr_path failed\n");
#endif
        return ERR_NOT_READY;
      }
      while (retry <= 3) {
        if (sdr_init(path, sinfo) < 0) {
          if (retry == 3) { //if the third retry still failed, return -1
#ifdef DEBUG
            syslog(LOG_ERR,
                   "bic_sensor_sdr_init: sdr_init failed for FRU %d", fru);
#endif
            return -1;
          }
          retry++;
          sleep(1);
        } else {
          break;
        }
      }
      break;
  }

  return 0;
}

static int
bic_sdr_init(uint8_t fru) {

  static bool init_done[MAX_NUM_FRUS] = {false};

  if (!init_done[fru - 1]) {

    sensor_info_t *sinfo = g_sinfo[fru-1];

    if (bic_sensor_sdr_init(fru, sinfo) < 0)
      return ERR_NOT_READY;

    init_done[fru - 1] = true;
  }

  return 0;
}

/* Get the threshold values from the SDRs */
static int
bic_get_sdr_thresh_val(uint8_t fru, uint8_t snr_num,
                       uint8_t thresh, void *value) {
  int ret, retry = 0;
  int8_t b_exp, r_exp;
  uint8_t x, m_lsb, m_msb, b_lsb, b_msb, thresh_val;
  uint16_t m = 0, b = 0;
  sdr_full_t *sdr;
  char cvalue[MAX_VALUE_LEN] = {0};

  ret = kv_get(SCM_INIT_THRESH_STATUS, cvalue, NULL, 0);
  if (!strncmp(cvalue, "done", sizeof("done"))) {
    ret = bic_sdr_init(fru);
  } else {
    while ((ret = bic_sdr_init(fru)) == ERR_NOT_READY &&
      retry++ < MAX_SDR_THRESH_RETRY) {
      sleep(1);
    }
  }

  if (ret < 0) {
    syslog(LOG_CRIT, "BIC threshold value can't get");
    return -1;
  }
  sdr = &g_sinfo[fru-1][snr_num].sdr;

  switch (thresh) {
    case UCR_THRESH:
      thresh_val = sdr->uc_thresh;
      break;
    case UNC_THRESH:
      thresh_val = sdr->unc_thresh;
      break;
    case UNR_THRESH:
      thresh_val = sdr->unr_thresh;
      break;
    case LCR_THRESH:
      thresh_val = sdr->lc_thresh;
      break;
    case LNC_THRESH:
      thresh_val = sdr->lnc_thresh;
      break;
    case LNR_THRESH:
      thresh_val = sdr->lnr_thresh;
      break;
    case POS_HYST:
      thresh_val = sdr->pos_hyst;
      break;
    case NEG_HYST:
      thresh_val = sdr->neg_hyst;
      break;
    default:
#ifdef DEBUG
      syslog(LOG_ERR, "bic_get_sdr_thresh_val: reading unknown threshold val");
#endif
      return -1;
  }

  // y = (mx + b * 10^b_exp) * 10^r_exp
  x = thresh_val;

  m_lsb = sdr->m_val;
  m_msb = sdr->m_tolerance >> 6;
  m = (m_msb << 8) | m_lsb;

  b_lsb = sdr->b_val;
  b_msb = sdr->b_accuracy >> 6;
  b = (b_msb << 8) | b_lsb;

  // exponents are 2's complement 4-bit number
  b_exp = sdr->rb_exp & 0xF;
  if (b_exp > 7) {
    b_exp = (~b_exp + 1) & 0xF;
    b_exp = -b_exp;
  }

  r_exp = (sdr->rb_exp >> 4) & 0xF;
  if (r_exp > 7) {
    r_exp = (~r_exp + 1) & 0xF;
    r_exp = -r_exp;
  }
  * (float *) value = ((m * x) + (b * pow(10, b_exp))) * (pow(10, r_exp));

  return 0;
}

static int
bic_read_sensor_wrapper(uint8_t fru, uint8_t sensor_num, bool discrete,
    void *value) {

  int ret, i;
  ipmi_sensor_reading_t sensor;
  sdr_full_t *sdr;

  ret = bic_read_sensor(IPMB_BUS, sensor_num, &sensor);
  if (ret) {
    return ret;
  }

  if (sensor.flags & BIC_SENSOR_READ_NA) {
#ifdef DEBUG
    syslog(LOG_ERR, "bic_read_sensor_wrapper: Reading Not Available");
    syslog(LOG_ERR, "bic_read_sensor_wrapper: sensor_num: 0x%X, flag: 0x%X",
        sensor_num, sensor.flags);
#endif
    return -1;
  }

  if (discrete) {
    *(float *) value = (float) sensor.status;
    return 0;
  }

  sdr = &g_sinfo[fru-1][sensor_num].sdr;

  // If the SDR is not type1, no need for conversion
  if (sdr->type !=1) {
    *(float *) value = sensor.value;
    return 0;
  }

  // y = (mx + b * 10^b_exp) * 10^r_exp
  uint8_t x;
  uint8_t m_lsb, m_msb;
  uint16_t m = 0;
  uint8_t b_lsb, b_msb;
  uint16_t b = 0;
  int8_t b_exp, r_exp;

  x = sensor.value;

  m_lsb = sdr->m_val;
  m_msb = sdr->m_tolerance >> 6;
  m = (m_msb << 8) | m_lsb;

  b_lsb = sdr->b_val;
  b_msb = sdr->b_accuracy >> 6;
  b = (b_msb << 8) | b_lsb;

  // exponents are 2's complement 4-bit number
  b_exp = sdr->rb_exp & 0xF;
  if (b_exp > 7) {
    b_exp = (~b_exp + 1) & 0xF;
    b_exp = -b_exp;
  }
  r_exp = (sdr->rb_exp >> 4) & 0xF;
  if (r_exp > 7) {
    r_exp = (~r_exp + 1) & 0xF;
    r_exp = -r_exp;
  }

  * (float *) value = ((m * x) + (b * pow(10, b_exp))) * (pow(10, r_exp));

  if ((sensor_num == BIC_SENSOR_SOC_THERM_MARGIN) && (* (float *) value > 0)) {
   * (float *) value -= (float) THERMAL_CONSTANT;
  }

  if (*(float *) value > MAX_POS_READING_MARGIN) {     //Negative reading handle
    for(i=0;i<sizeof(bic_neg_reading_sensor_support_list)/sizeof(uint8_t);i++) {
      if (sensor_num == bic_neg_reading_sensor_support_list[i]) {
        * (float *) value -= (float) THERMAL_CONSTANT;
      }
    }
  }

  return 0;
}

static int
get_fan_speed(uint8_t snr_num, float *rpm) {

  int tmp;
  char device_name[LARGEST_DEVICE_NAME + 1];

  if (snr_num >= SMB_SENSOR_FAN1_FRONT_TACH &&
      snr_num <= SMB_SENSOR_FAN8_REAR_TACH) {

    snprintf(device_name, LARGEST_DEVICE_NAME,
             "/tmp/cache_store/smb_sensor%d", snr_num);
    if (read_device(device_name, &tmp)) {
      return -1;
    }
    *rpm = (float)tmp;
  } else {
    return -1;
  }
  return 0;
}

static void apply_inlet_correction(float *value) {
  float rpm[16] = {0};
  float avg_rpm = 0;
  uint8_t i;
  uint8_t cnt = 0;
  static bool inited = false;

  /* Get RPM value */
  for (i = SMB_SENSOR_FAN1_FRONT_TACH; i <= SMB_SENSOR_FAN8_REAR_TACH; i++) {
    if (get_fan_speed(i, &rpm[cnt]) == 0) {
      avg_rpm += rpm[cnt];
      cnt++;
    }
  }
  if (cnt) {
    avg_rpm = avg_rpm / (float)cnt;

    if (!inited) {
      if (sensor_correction_init("/etc/sensor-correction-conf.json")) {
        syslog(LOG_ERR, "sensor_correction_init fail!");
      }
      inited = true;
    }
    sensor_correction_apply(FRU_SCM,
                            SCM_SENSOR_INLET_REMOTE_TEMP, avg_rpm, value);
  }
}

static void
hsc_rsense_init(uint8_t hsc_id, const char* device) {
  static bool rsense_inited[MAX_NUM_FRUS] = {false};

  if (!rsense_inited[hsc_id]) {
    int brd_rev = -1;

    switch (hsc_id) {
      case HSC_FCM_T:
        pal_get_cpld_board_rev(&brd_rev, device);
        /* R0D or R0E FCM */
        if (brd_rev == 0x4 || brd_rev == 0x5) {
          hsc_rsense[hsc_id] = 1.14;
        } else {
          hsc_rsense[hsc_id] = 0.33;
        }
        break;
      case HSC_FCM_B:
        pal_get_cpld_board_rev(&brd_rev, device);
        /* R0D or R0E FCM */
        if (brd_rev == 0x4 || brd_rev == 0x5) {
          hsc_rsense[hsc_id] = 1.15;
        } else {
          hsc_rsense[hsc_id] = 0.33;
        }
        break;
    }
    rsense_inited[hsc_id] = true;
  }
}

static int
scm_sensor_read(uint8_t fru, uint8_t sensor_num, float *value) {

  int ret = -1;
  int i = 0;
  int j = 0;
  bool discrete = false;
  bool scm_sensor = false;

  while (i < scm_sensor_cnt) {
    if (sensor_num == scm_sensor_list[i++]) {
      scm_sensor = true;
      break;
    }
  }
  if (scm_sensor) {
    switch(sensor_num) {
      case SCM_SENSOR_OUTLET_LOCAL_TEMP:
        ret = read_attr(fru, sensor_num, SCM_OUTLET_TEMP_DEVICE, TEMP(1), value);
        break;
      case SCM_SENSOR_OUTLET_REMOTE_TEMP:
        ret = read_attr(fru, sensor_num, SCM_OUTLET_TEMP_DEVICE, TEMP(2), value);
        break;
      case SCM_SENSOR_INLET_LOCAL_TEMP:
        ret = read_attr(fru, sensor_num, SCM_INLET_TEMP_DEVICE, TEMP(1), value);
        break;
      case SCM_SENSOR_INLET_REMOTE_TEMP:
        ret = read_attr(fru, sensor_num, SCM_INLET_TEMP_DEVICE, TEMP(2), value);
        if (!ret)
          apply_inlet_correction(value);
        break;
      case SCM_SENSOR_HSC_VOLT:
        ret = read_hsc_volt(fru, sensor_num, SCM_HSC_DEVICE, 1, value);
        break;
      case SCM_SENSOR_HSC_CURR:
        ret = read_hsc_curr(fru, sensor_num, SCM_HSC_DEVICE, SCM_RSENSE, value);
        break;
      case SCM_SENSOR_HSC_POWER:
        ret = read_hsc_power(fru, sensor_num, SCM_HSC_DEVICE, SCM_RSENSE, value);
        break;
      default:
        ret = READING_NA;
        break;
    }
  } else if (!scm_sensor && is_server_on()) {
    ret = bic_sdr_init(FRU_SCM);
    if (ret < 0) {
#ifdef DEBUG
    syslog(LOG_INFO, "bic_sdr_init fail\n");
#endif
      return ret;
    }

    while (j < bic_discrete_cnt) {
      if (sensor_num == bic_discrete_list[j++]) {
        discrete = true;
        break;
      }
    }
    ret = bic_read_sensor_wrapper(FRU_SCM, sensor_num, discrete, value);
  } else {
    ret = READING_NA;
  }
  return ret;
}

static int
cor_th3_volt(void) {
  int tmp_volt, i;
  int val_volt = 0;
  char str[32];
  char tmp[LARGEST_DEVICE_NAME];
  char path[LARGEST_DEVICE_NAME + 1];
  snprintf(tmp, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, SMB_MAC_CPLD_ROV);

  for(i = SMB_MAC_CPLD_ROV_NUM - 1; i >= 0; i--) {
    snprintf(path, LARGEST_DEVICE_NAME, tmp, i);
    if(read_device(path, &tmp_volt)) {
      syslog(LOG_ERR, "%s, Cannot read th3 voltage from smbcpld\n", __func__);
      return -1;
    }
    val_volt += tmp_volt;
    if(i)
      val_volt = (val_volt << 1);
  }
  val_volt = (int)(round((1.6 - (((double)val_volt - 3) * 0.00625)) * 1000));

  if(val_volt > TH3_VOL_MAX || val_volt < TH3_VOL_MIN)
    return -1;

  snprintf(str, sizeof(str), "%d", val_volt);
  snprintf(path, LARGEST_DEVICE_NAME, SMB_ISL_DEVICE"/%s", VOLT_SET(0));
  if(write_device(path, str)) {
    syslog(LOG_ERR, "%s, Cannot write th3 voltage into ISL68127\n", __func__);
    return -1;
  }

  return 0;
}

static int
smb_sensor_read(uint8_t fru, uint8_t sensor_num, float *value) {

  int ret = -1, th3_ret = -1;
  static uint8_t bootup_check = 0;
  switch(sensor_num) {
    case SMB_SENSOR_TH3_SERDES_TEMP:
      ret = read_attr(fru, sensor_num, SMB_IR_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TH3_CORE_TEMP:
      ret = read_attr(fru, sensor_num, SMB_ISL_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_TEMP1_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_TEMP2_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TEMP3:
      ret = read_attr(fru, sensor_num, SMB_TEMP3_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TEMP4:
      ret = read_attr(fru, sensor_num, SMB_TEMP4_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TEMP5:
      ret = read_attr(fru, sensor_num, SMB_TH3_TEMP_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_TH3_DIE_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_TH3_TEMP_DEVICE, TEMP(2), value);
      break;
    case SMB_SENSOR_TH3_DIE_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_TH3_TEMP_DEVICE, TEMP(3), value);
      break;
    case SMB_SENSOR_PDB_L_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_PDB_L_TEMP1_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_PDB_L_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_PDB_L_TEMP2_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_PDB_R_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_PDB_R_TEMP1_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_PDB_R_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_PDB_R_TEMP2_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_FCM_T_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_FCM_T_TEMP1_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_FCM_T_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_FCM_T_TEMP2_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_FCM_B_TEMP1:
      ret = read_attr(fru, sensor_num, SMB_FCM_B_TEMP1_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_FCM_B_TEMP2:
      ret = read_attr(fru, sensor_num, SMB_FCM_B_TEMP2_DEVICE, TEMP(1), value);
      break;
    case SMB_SENSOR_1220_VMON1:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(0), value);
      break;
    case SMB_SENSOR_1220_VMON2:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(1), value);
      break;
    case SMB_SENSOR_1220_VMON3:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(2), value);
      break;
    case SMB_SENSOR_1220_VMON4:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(3), value);
      break;
    case SMB_SENSOR_1220_VMON5:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(4), value);
      break;
    case SMB_SENSOR_1220_VMON6:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(5), value);
      break;
    case SMB_SENSOR_1220_VMON7:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(6), value);
      break;
    case SMB_SENSOR_1220_VMON8:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(7), value);
      break;
    case SMB_SENSOR_1220_VMON9:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(8), value);
      break;
    case SMB_SENSOR_1220_VMON10:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(9), value);
      break;
    case SMB_SENSOR_1220_VMON11:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(10), value);
      break;
    case SMB_SENSOR_1220_VMON12:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(11), value);
      break;
    case SMB_SENSOR_1220_VCCA:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(12), value);
      break;
    case SMB_SENSOR_1220_VCCINP:
      ret = read_attr(fru, sensor_num, SMB_1220_DEVICE, VOLT(13), value);
      break;
    case SMB_SENSOR_TH3_SERDES_VOLT:
      ret = read_attr(fru, sensor_num, SMB_IR_DEVICE, VOLT(0), value);
      break;
    case SMB_SENSOR_TH3_CORE_VOLT:
      ret = read_attr(fru, sensor_num, SMB_ISL_DEVICE, VOLT(0), value);
      if (bootup_check == 0) {
        th3_ret = cor_th3_volt();
        if (!th3_ret)
          bootup_check = 1;
      }
      break;
    case SMB_SENSOR_FCM_T_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, SMB_FCM_T_HSC_DEVICE, 1, value);
      break;
    case SMB_SENSOR_FCM_B_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, SMB_FCM_B_HSC_DEVICE, 1, value);
      break;
    case SMB_SENSOR_TH3_SERDES_CURR:
      ret = read_attr(fru, sensor_num, SMB_IR_DEVICE, CURR(1), value);
      break;
    case SMB_SENSOR_TH3_CORE_CURR:
      ret = read_attr(fru, sensor_num, SMB_ISL_DEVICE,  CURR(1), value);
      break;
    case SMB_SENSOR_FCM_T_HSC_CURR:
      hsc_rsense_init(HSC_FCM_T, TOP_FCMCPLD_PATH_FMT);
      ret = read_hsc_curr(fru, sensor_num, SMB_FCM_T_HSC_DEVICE,
                          hsc_rsense[HSC_FCM_T], value);
      break;
    case SMB_SENSOR_FCM_B_HSC_CURR:
      hsc_rsense_init(HSC_FCM_B, BOTTOM_FCMCPLD_PATH_FMT);
      ret = read_hsc_curr(fru, sensor_num, SMB_FCM_B_HSC_DEVICE,
                          hsc_rsense[HSC_FCM_B], value);
      break;
    case SMB_SENSOR_FCM_T_HSC_POWER:
      hsc_rsense_init(HSC_FCM_T, TOP_FCMCPLD_PATH_FMT);
      ret = read_hsc_power(fru, sensor_num, SMB_FCM_T_HSC_DEVICE,
                           hsc_rsense[HSC_FCM_T], value);
      break;
    case SMB_SENSOR_FCM_B_HSC_POWER:
      hsc_rsense_init(HSC_FCM_B, BOTTOM_FCMCPLD_PATH_FMT);
      ret = read_hsc_power(fru, sensor_num, SMB_FCM_B_HSC_DEVICE,
                           hsc_rsense[HSC_FCM_B], value);
      break;
    case SMB_SENSOR_FAN1_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 1, value);
      break;
    case SMB_SENSOR_FAN1_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 2, value);
      break;
    case SMB_SENSOR_FAN2_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 1, value);
      break;
    case SMB_SENSOR_FAN2_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 2, value);
      break;
    case SMB_SENSOR_FAN3_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 3, value);
      break;
    case SMB_SENSOR_FAN3_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 4, value);
      break;
    case SMB_SENSOR_FAN4_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 3, value);
      break;
    case SMB_SENSOR_FAN4_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 4, value);
      break;
    case SMB_SENSOR_FAN5_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 5, value);
      break;
    case SMB_SENSOR_FAN5_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 6, value);
      break;
    case SMB_SENSOR_FAN6_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 5, value);
      break;
    case SMB_SENSOR_FAN6_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 6, value);
      break;
    case SMB_SENSOR_FAN7_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 7, value);
      break;
    case SMB_SENSOR_FAN7_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_T_TACH_DEVICE, 8, value);
      break;
    case SMB_SENSOR_FAN8_FRONT_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 7, value);
      break;
    case SMB_SENSOR_FAN8_REAR_TACH:
      ret = read_fan_rpm_f(SMB_FCM_B_TACH_DEVICE, 8, value);
      break;
    default:
      ret = READING_NA;
      break;
  }
  return ret;
}

static int
pim_sensor_read(uint8_t fru, uint8_t sensor_num, float *value) {
  int ret = -1;
  int type = pal_get_pim_type_from_file(fru);

  switch(sensor_num) {
    case PIM1_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM1_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM1_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM1_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM1_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM1_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM1_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM1_HSC_DEVICE, 1, value);
      break;
    case PIM1_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM1_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM1_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM1_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM1_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM1_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM1_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(3), value);
      break;
    case PIM1_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(4), value);
      break;
    case PIM1_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(5), value);
      break;
    case PIM1_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(6), value);
      break;
    case PIM1_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(7), value);
      break;
    case PIM1_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(8), value);
      break;
    case PIM1_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(9), value);
      break;
    case PIM1_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM1_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM1_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(12), value);
      break;
    case PIM1_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(13), value);
      break;
    case PIM1_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(14), value);
      break;
    case PIM1_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(15), value);
      break;
    case PIM1_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM1_34461_DEVICE, VOLT(16), value);
      break;
    case PIM2_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM2_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM2_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM2_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM2_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM2_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM2_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM2_HSC_DEVICE, 1, value);
      break;
    case PIM2_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM2_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM2_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM2_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM2_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM2_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM2_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(3), value);
      break;
    case PIM2_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(4), value);
      break;
    case PIM2_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(5), value);
      break;
    case PIM2_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(6), value);
      break;
    case PIM2_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(7), value);
      break;
    case PIM2_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(8), value);
      break;
    case PIM2_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(9), value);
      break;
    case PIM2_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM2_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM2_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(12), value);
      break;
    case PIM2_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(13), value);
      break;
    case PIM2_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(14), value);
      break;
    case PIM2_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(15), value);
      break;
    case PIM2_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM2_34461_DEVICE, VOLT(16), value);
      break;
    case PIM3_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM3_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM3_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM3_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM3_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM3_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM3_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM3_HSC_DEVICE, 1, value);
      break;
    case PIM3_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM3_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM3_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM3_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM3_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM3_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM3_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(3), value);
      break;
    case PIM3_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(4), value);
      break;
    case PIM3_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(5), value);
      break;
    case PIM3_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(6), value);
      break;
    case PIM3_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(7), value);
      break;
    case PIM3_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(8), value);
      break;
    case PIM3_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(9), value);
      break;
    case PIM3_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM3_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM3_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(12), value);
      break;
    case PIM3_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(13), value);
      break;
    case PIM3_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(14), value);
      break;
    case PIM3_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(15), value);
      break;
    case PIM3_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM3_34461_DEVICE, VOLT(16), value);
      break;
    case PIM4_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM4_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM4_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM4_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM4_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM4_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM4_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM4_HSC_DEVICE, 1, value);
      break;
    case PIM4_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM4_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM4_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM4_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM4_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM4_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM4_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(3), value);
      break;
    case PIM4_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(4), value);
      break;
    case PIM4_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(5), value);
      break;
    case PIM4_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(6), value);
      break;
    case PIM4_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(7), value);
      break;
    case PIM4_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(8), value);
      break;
    case PIM4_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(9), value);
      break;
    case PIM4_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM4_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM4_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(12), value);
      break;
    case PIM4_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(13), value);
      break;
    case PIM4_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(14), value);
      break;
    case PIM4_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(15), value);
      break;
    case PIM4_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM4_34461_DEVICE, VOLT(16), value);
      break;
    case PIM5_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM5_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM5_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM5_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM5_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM5_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM5_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM5_HSC_DEVICE, 1, value);
      break;
    case PIM5_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM5_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM5_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM5_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM5_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM5_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM5_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(3), value);
      break;
    case PIM5_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(4), value);
      break;
    case PIM5_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(5), value);
      break;
    case PIM5_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(6), value);
      break;
    case PIM5_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(7), value);
      break;
    case PIM5_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(8), value);
      break;
    case PIM5_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(9), value);
      break;
    case PIM5_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM5_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM5_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(12), value);
      break;
    case PIM5_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(13), value);
      break;
    case PIM5_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(14), value);
      break;
    case PIM5_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(15), value);
      break;
    case PIM5_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM5_34461_DEVICE, VOLT(16), value);
      break;
    case PIM6_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM6_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM6_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM6_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM6_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM6_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM6_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM6_HSC_DEVICE, 1, value);
      break;
    case PIM6_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM6_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM6_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM6_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM6_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM6_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM6_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(3), value);
      break;
    case PIM6_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(4), value);
      break;
    case PIM6_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(5), value);
      break;
    case PIM6_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(6), value);
      break;
    case PIM6_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(7), value);
      break;
    case PIM6_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(8), value);
      break;
    case PIM6_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(9), value);
      break;
    case PIM6_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM6_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM6_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(12), value);
      break;
    case PIM6_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(13), value);
      break;
    case PIM6_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(14), value);
      break;
    case PIM6_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(15), value);
      break;
    case PIM6_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM6_34461_DEVICE, VOLT(16), value);
      break;
    case PIM7_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM7_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM7_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM7_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM7_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM7_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM7_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM7_HSC_DEVICE, 1, value);
      break;
    case PIM7_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM7_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM7_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM7_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM7_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM7_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM7_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(3), value);
      break;
    case PIM7_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(4), value);
      break;
    case PIM7_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(5), value);
      break;
    case PIM7_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(6), value);
      break;
    case PIM7_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(7), value);
      break;
    case PIM7_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(8), value);
      break;
    case PIM7_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(9), value);
      break;
    case PIM7_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM7_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM7_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(12), value);
      break;
    case PIM7_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(13), value);
      break;
    case PIM7_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(14), value);
      break;
    case PIM7_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(15), value);
      break;
    case PIM7_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM7_34461_DEVICE, VOLT(16), value);
      break;
    case PIM8_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PIM8_TEMP1_DEVICE, TEMP(1), value);
      break;
    case PIM8_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PIM8_TEMP2_DEVICE, TEMP(1), value);
      break;
    case PIM8_SENSOR_QSFP_TEMP:
      ret = read_attr(fru, sensor_num, PIM8_DOM_DEVICE, TEMP(1), value);
      break;
    case PIM8_SENSOR_HSC_VOLT:
      ret = read_hsc_volt(fru, sensor_num, PIM8_HSC_DEVICE, 1, value);
      break;
    case PIM8_SENSOR_HSC_CURR:
      ret = read_hsc_curr(fru, sensor_num, PIM8_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM8_SENSOR_HSC_POWER:
      ret = read_hsc_power(fru, sensor_num, PIM8_HSC_DEVICE, PIM_RSENSE, value);
      break;
    case PIM8_SENSOR_34461_VOLT1:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(1), value);
      if(type == PIM_TYPE_16O)  *value = *value * 4;
      break;
    case PIM8_SENSOR_34461_VOLT2:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(2), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM8_SENSOR_34461_VOLT3:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(3), value);
      break;
    case PIM8_SENSOR_34461_VOLT4:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(4), value);
      break;
    case PIM8_SENSOR_34461_VOLT5:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(5), value);
      break;
    case PIM8_SENSOR_34461_VOLT6:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(6), value);
      break;
    case PIM8_SENSOR_34461_VOLT7:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(7), value);
      break;
    case PIM8_SENSOR_34461_VOLT8:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(8), value);
      break;
    case PIM8_SENSOR_34461_VOLT9:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(9), value);
      break;
    case PIM8_SENSOR_34461_VOLT10:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(10), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM8_SENSOR_34461_VOLT11:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(11), value);
      if(type == PIM_TYPE_16O)  *value = *value * 2;
      break;
    case PIM8_SENSOR_34461_VOLT12:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(12), value);
      break;
    case PIM8_SENSOR_34461_VOLT13:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(13), value);
      break;
    case PIM8_SENSOR_34461_VOLT14:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(14), value);
      break;
    case PIM8_SENSOR_34461_VOLT15:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(15), value);
      break;
    case PIM8_SENSOR_34461_VOLT16:
      ret = read_attr(fru, sensor_num, PIM8_34461_DEVICE, VOLT(16), value);
      break;
    default:
      ret = READING_NA;
      break;
  }
  return ret;
}

static int
psu_init_acok_key(uint8_t fru) {
  uint8_t psu_num = fru - 10;
  char key[MAX_KEY_LEN + 1];

  snprintf(key, MAX_KEY_LEN, "psu%d_acok_state", psu_num);
  kv_set(key, "1", 0, KV_FCREATE);

  return 0;
}

static int
psu_acok_log(uint8_t fru, uint8_t curr_state) {
  uint8_t psu_num = fru - 10;
  int ret, old_state;
  char key[MAX_KEY_LEN + 1];
  char cvalue[MAX_VALUE_LEN] = {0};

  snprintf(key, MAX_KEY_LEN, "psu%d_acok_state", psu_num);
  ret = kv_get(key, cvalue, NULL, 0);
  if (ret < 0) {
    return ret;
  }

  old_state = atoi(cvalue);

  if (curr_state != old_state) {
    if (curr_state == PSU_ACOK_UP) {
      pal_update_ts_sled();
      syslog(LOG_CRIT, "DEASSERT: PSU%d AC OK state - AC power up - FRU: %d",
             psu_num, fru);
      kv_set(key, "1", 0, 0);
    } else {
      pal_update_ts_sled();
      syslog(LOG_CRIT, "ASSERT: PSU%d AC OK state - AC power down - FRU: %d",
             psu_num, fru);
      kv_set(key, "0", 0, 0);
    }
  }

  return 0;
}

static int
psu_acok_check(uint8_t fru) {
  int val;
  char path[LARGEST_DEVICE_NAME + 1];

  if (fru == FRU_PSU1) {
    snprintf(path, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, "psu_L2_input_ok");
  } else if (fru == FRU_PSU2) {
    snprintf(path, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, "psu_L1_input_ok");
  } else if (fru == FRU_PSU3) {
    snprintf(path, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, "psu_R2_input_ok");
  } else if (fru == FRU_PSU4) {
    snprintf(path, LARGEST_DEVICE_NAME, SMBCPLD_PATH_FMT, "psu_R1_input_ok");
  }

  if (read_device(path, &val)) {
    syslog(LOG_ERR, "%s cannot get value from %s", __func__, path);
    return 0;
  }
  if (!val) {
    return READING_NA;
  }

  return val;
}

static int
psu_sensor_read(uint8_t fru, uint8_t sensor_num, float *value) {
  int ret = -1;

  ret = psu_acok_check(fru);
  if (ret == READING_NA) {
    psu_acok_log(fru, PSU_ACOK_DOWN);
    goto psu_out;
  }
  psu_acok_log(fru, PSU_ACOK_UP);

  switch(sensor_num) {
    case PSU1_SENSOR_IN_VOLT:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, VOLT(0), value);
      break;
    case PSU1_SENSOR_12V_VOLT:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, VOLT(1), value);
      break;
    case PSU1_SENSOR_STBY_VOLT:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, VOLT(2), value);
      break;
    case PSU1_SENSOR_IN_CURR:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, CURR(1), value);
      break;
    case PSU1_SENSOR_12V_CURR:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, CURR(2), value);
      break;
    case PSU1_SENSOR_STBY_CURR:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, CURR(3), value);
      break;
    case PSU1_SENSOR_IN_POWER:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, POWER(1), value);
      break;
    case PSU1_SENSOR_12V_POWER:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, POWER(2), value);
      break;
    case PSU1_SENSOR_STBY_POWER:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, POWER(3), value);
      break;
    case PSU1_SENSOR_FAN_TACH:
      ret = read_fan_rpm_f(PSU1_DEVICE, 1, value);
      break;
    case PSU1_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, TEMP(1), value);
      break;
    case PSU1_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, TEMP(2), value);
      break;
    case PSU1_SENSOR_TEMP3:
      ret = read_attr(fru, sensor_num, PSU1_DEVICE, TEMP(3), value);
      break;
    case PSU2_SENSOR_IN_VOLT:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, VOLT(0), value);
      break;
    case PSU2_SENSOR_12V_VOLT:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, VOLT(1), value);
      break;
    case PSU2_SENSOR_STBY_VOLT:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, VOLT(2), value);
      break;
    case PSU2_SENSOR_IN_CURR:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, CURR(1), value);
      break;
    case PSU2_SENSOR_12V_CURR:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, CURR(2), value);
      break;
    case PSU2_SENSOR_STBY_CURR:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, CURR(3), value);
      break;
    case PSU2_SENSOR_IN_POWER:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, POWER(1), value);
      break;
    case PSU2_SENSOR_12V_POWER:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, POWER(2), value);
      break;
    case PSU2_SENSOR_STBY_POWER:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, POWER(3), value);
      break;
    case PSU2_SENSOR_FAN_TACH:
      ret = read_fan_rpm_f(PSU2_DEVICE, 1, value);
      break;
    case PSU2_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, TEMP(1), value);
      break;
    case PSU2_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, TEMP(2), value);
      break;
    case PSU2_SENSOR_TEMP3:
      ret = read_attr(fru, sensor_num, PSU2_DEVICE, TEMP(3), value);
      break;
    case PSU3_SENSOR_IN_VOLT:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, VOLT(0), value);
      break;
    case PSU3_SENSOR_12V_VOLT:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, VOLT(1), value);
      break;
    case PSU3_SENSOR_STBY_VOLT:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, VOLT(2), value);
      break;
    case PSU3_SENSOR_IN_CURR:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, CURR(1), value);
      break;
    case PSU3_SENSOR_12V_CURR:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, CURR(2), value);
      break;
    case PSU3_SENSOR_STBY_CURR:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, CURR(3), value);
      break;
    case PSU3_SENSOR_IN_POWER:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, POWER(1), value);
      break;
    case PSU3_SENSOR_12V_POWER:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, POWER(2), value);
      break;
    case PSU3_SENSOR_STBY_POWER:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, POWER(3), value);
      break;
    case PSU3_SENSOR_FAN_TACH:
      ret = read_fan_rpm_f(PSU3_DEVICE, 1, value);
      break;
    case PSU3_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, TEMP(1), value);
      break;
    case PSU3_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, TEMP(2), value);
      break;
    case PSU3_SENSOR_TEMP3:
      ret = read_attr(fru, sensor_num, PSU3_DEVICE, TEMP(3), value);
      break;
    case PSU4_SENSOR_IN_VOLT:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, VOLT(0), value);
      break;
    case PSU4_SENSOR_12V_VOLT:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, VOLT(1), value);
      break;
    case PSU4_SENSOR_STBY_VOLT:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, VOLT(2), value);
      break;
    case PSU4_SENSOR_IN_CURR:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, CURR(1), value);
      break;
    case PSU4_SENSOR_12V_CURR:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, CURR(2), value);
      break;
    case PSU4_SENSOR_STBY_CURR:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, CURR(3), value);
      break;
    case PSU4_SENSOR_IN_POWER:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, POWER(1), value);
      break;
    case PSU4_SENSOR_12V_POWER:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, POWER(2), value);
      break;
    case PSU4_SENSOR_STBY_POWER:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, POWER(3), value);
      break;
    case PSU4_SENSOR_FAN_TACH:
      ret = read_fan_rpm_f(PSU4_DEVICE, 1, value);
      break;
    case PSU4_SENSOR_TEMP1:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, TEMP(1), value);
      break;
    case PSU4_SENSOR_TEMP2:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, TEMP(2), value);
      break;
    case PSU4_SENSOR_TEMP3:
      ret = read_attr(fru, sensor_num, PSU4_DEVICE, TEMP(3), value);
      break;
    default:
      ret = READING_NA;
      break;
  }

psu_out:
  return ret;
}

int
pal_sensor_read_raw(uint8_t fru, uint8_t sensor_num, void *value) {

  char key[MAX_KEY_LEN];
  char fru_name[32];
  int ret , delay = 500;
  uint8_t prsnt = 0;

  pal_get_fru_name(fru, fru_name);

  ret = pal_is_fru_prsnt(fru, &prsnt);
  if (ret) {
    return ret;
  }
  if (!prsnt) {
#ifdef DEBUG
  syslog(LOG_INFO, "pal_sensor_read_raw(): %s is not present\n", fru_name);
#endif
    return -1;
  }

  sprintf(key, "%s_sensor%d", fru_name, sensor_num);
  switch(fru) {
    case FRU_SCM:
      ret = scm_sensor_read(fru, sensor_num, value);
      if (sensor_num == SCM_SENSOR_INLET_REMOTE_TEMP) {
        delay = 100;
      }
      break;
    case FRU_SMB:
      ret = smb_sensor_read(fru, sensor_num, value);
      if (sensor_num == SMB_SENSOR_TH3_DIE_TEMP1 ||
          sensor_num == SMB_SENSOR_TH3_DIE_TEMP2) {
        delay = 100;
      }
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      ret = pim_sensor_read(fru, sensor_num, value);
      if (sensor_num >= PIM1_SENSOR_QSFP_TEMP &&
          sensor_num <= PIM8_SENSOR_QSFP_TEMP) {
        delay = 100;
      }
      break;
    case FRU_PSU1:
    case FRU_PSU2:
    case FRU_PSU3:
    case FRU_PSU4:
      ret = psu_sensor_read(fru, sensor_num, value);
      break;
    default:
      return -1;
  }

  if (ret == READING_NA || ret == -1) {
    return READING_NA;
  }
  msleep(delay);

  return 0;
}

static int
get_scm_sensor_name(uint8_t sensor_num, char *name) {

  switch(sensor_num) {
    case SCM_SENSOR_OUTLET_LOCAL_TEMP:
      sprintf(name, "SCM_OUTLET_LOCAL_TEMP");
      break;
    case SCM_SENSOR_OUTLET_REMOTE_TEMP:
      sprintf(name, "SCM_OUTLET_REMOTE_TEMP");
      break;
    case SCM_SENSOR_INLET_LOCAL_TEMP:
      sprintf(name, "SCM_INLET_LOCAL_TEMP");
      break;
    case SCM_SENSOR_INLET_REMOTE_TEMP:
      sprintf(name, "SCM_INLET_REMOTE_TEMP");
      break;
    case SCM_SENSOR_HSC_VOLT:
      sprintf(name, "SCM_HSC_VOLT");
      break;
    case SCM_SENSOR_HSC_CURR:
      sprintf(name, "SCM_HSC_CURR");
      break;
    case SCM_SENSOR_HSC_POWER:
      sprintf(name, "SCM_HSC_POWER");
      break;
    case BIC_SENSOR_MB_OUTLET_TEMP:
      sprintf(name, "MB_OUTLET_TEMP");
      break;
    case BIC_SENSOR_MB_INLET_TEMP:
      sprintf(name, "MB_INLET_TEMP");
      break;
    case BIC_SENSOR_PCH_TEMP:
      sprintf(name, "PCH_TEMP");
      break;
    case BIC_SENSOR_VCCIN_VR_TEMP:
      sprintf(name, "VCCIN_VR_TEMP");
      break;
    case BIC_SENSOR_1V05MIX_VR_TEMP:
      sprintf(name, "1V05MIX_VR_TEMP");
      break;
    case BIC_SENSOR_SOC_TEMP:
      sprintf(name, "SOC_TEMP");
      break;
    case BIC_SENSOR_SOC_THERM_MARGIN:
      sprintf(name, "SOC_THERM_MARGIN_TEMP");
      break;
    case BIC_SENSOR_VDDR_VR_TEMP:
      sprintf(name, "VDDR_VR_TEMP");
      break;
    case BIC_SENSOR_SOC_DIMMA0_TEMP:
      sprintf(name, "SOC_DIMMA0_TEMP");
      break;
    case BIC_SENSOR_SOC_DIMMB0_TEMP:
      sprintf(name, "SOC_DIMMB0_TEMP");
      break;
    case BIC_SENSOR_SOC_PACKAGE_PWR:
      sprintf(name, "SOC_PACKAGE_POWER");
      break;
    case BIC_SENSOR_VCCIN_VR_POUT:
      sprintf(name, "VCCIN_VR_OUT_POWER");
      break;
      case BIC_SENSOR_VDDR_VR_POUT:
      sprintf(name, "VDDR_VR_OUT_POWER");
      break;
    case BIC_SENSOR_SOC_TJMAX:
      sprintf(name, "SOC_TJMAX_TEMP");
      break;
    case BIC_SENSOR_P3V3_MB:
      sprintf(name, "P3V3_MB_VOLT");
      break;
    case BIC_SENSOR_P12V_MB:
      sprintf(name, "P12V_MB_VOLT");
      break;
    case BIC_SENSOR_P1V05_PCH:
      sprintf(name, "P1V05_PCH_VOLT");
      break;
    case BIC_SENSOR_P3V3_STBY_MB:
      sprintf(name, "P3V3_STBY_MB_VOLT");
      break;
    case BIC_SENSOR_P5V_STBY_MB:
      sprintf(name, "P5V_STBY_MB_VOLT");
      break;
    case BIC_SENSOR_PV_BAT:
      sprintf(name, "PV_BAT_VOLT");
      break;
    case BIC_SENSOR_PVDDR:
      sprintf(name, "PVDDR_VOLT");
      break;
    case BIC_SENSOR_P1V05_MIX:
      sprintf(name, "P1V05_MIX_VOLT");
      break;
    case BIC_SENSOR_1V05MIX_VR_CURR:
      sprintf(name, "1V05MIX_VR_CURR");
      break;
    case BIC_SENSOR_VDDR_VR_CURR:
      sprintf(name, "VDDR_VR_CURR");
      break;
    case BIC_SENSOR_VCCIN_VR_CURR:
      sprintf(name, "VCCIN_VR_CURR");
      break;
    case BIC_SENSOR_VCCIN_VR_VOL:
      sprintf(name, "VCCIN_VR_VOLT");
      break;
    case BIC_SENSOR_VDDR_VR_VOL:
      sprintf(name, "VDDR_VR_VOLT");
      break;
    case BIC_SENSOR_P1V05MIX_VR_VOL:
      sprintf(name, "1V05MIX_VR_VOLT");
      break;
    case BIC_SENSOR_P1V05MIX_VR_POUT:
      sprintf(name, "1V05MIX_VR_OUT_POWER");
      break;
    case BIC_SENSOR_INA230_POWER:
      sprintf(name, "INA230_POWER");
      break;
    case BIC_SENSOR_INA230_VOL:
      sprintf(name, "INA230_VOLT");
      break;
    case BIC_SENSOR_SYSTEM_STATUS:
      sprintf(name, "SYSTEM_STATUS");
      break;
    case BIC_SENSOR_SYS_BOOT_STAT:
      sprintf(name, "SYS_BOOT_STAT");
      break;
    case BIC_SENSOR_CPU_DIMM_HOT:
      sprintf(name, "CPU_DIMM_HOT");
      break;
    case BIC_SENSOR_PROC_FAIL:
      sprintf(name, "PROC_FAIL");
      break;
    case BIC_SENSOR_VR_HOT:
      sprintf(name, "VR_HOT");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_smb_sensor_name(uint8_t sensor_num, char *name) {

  switch(sensor_num) {
    case SMB_SENSOR_TH3_SERDES_TEMP:
      sprintf(name, "TH3_SERDES_TEMP");
      break;
    case SMB_SENSOR_TH3_CORE_TEMP:
      sprintf(name, "TH3_CORE_TEMP");
      break;
    case SMB_SENSOR_TEMP1:
      sprintf(name, "SMB_TEMP1");
      break;
    case SMB_SENSOR_TEMP2:
      sprintf(name, "SMB_TEMP2");
      break;
    case SMB_SENSOR_TEMP3:
      sprintf(name, "SMB_TEMP3");
      break;
    case SMB_SENSOR_TEMP4:
      sprintf(name, "SMB_TEMP4");
      break;
    case SMB_SENSOR_TEMP5:
      sprintf(name, "SMB_TEMP5");
      break;
    case SMB_SENSOR_TH3_DIE_TEMP1:
      sprintf(name, "TH3_DIE_TEMP1");
      break;
    case SMB_SENSOR_TH3_DIE_TEMP2:
      sprintf(name, "TH3_DIE_TEMP2");
      break;
    case SMB_SENSOR_PDB_L_TEMP1:
      sprintf(name, "PDB_L_TEMP1");
      break;
    case SMB_SENSOR_PDB_L_TEMP2:
      sprintf(name, "PDB_L_TEMP2");
      break;
    case SMB_SENSOR_PDB_R_TEMP1:
      sprintf(name, "PDB_R_TEMP1");
      break;
    case SMB_SENSOR_PDB_R_TEMP2:
      sprintf(name, "PDB_R_TEMP2");
      break;
    case SMB_SENSOR_FCM_T_TEMP1:
      sprintf(name, "FCM_T_TEMP1");
      break;
    case SMB_SENSOR_FCM_T_TEMP2:
      sprintf(name, "FCM_T_TEMP2");
      break;
    case SMB_SENSOR_FCM_B_TEMP1:
      sprintf(name, "FCM_B_TEMP1");
      break;
    case SMB_SENSOR_FCM_B_TEMP2:
      sprintf(name, "FCM_B_TEMP2");
      break;
    case SMB_SENSOR_1220_VMON1:
      sprintf(name, "POWR1220_VMON1");
      break;
    case SMB_SENSOR_1220_VMON2:
      sprintf(name, "POWR1220_VMON2");
      break;
    case SMB_SENSOR_1220_VMON3:
      sprintf(name, "POWR1220_VMON3");
      break;
    case SMB_SENSOR_1220_VMON4:
      sprintf(name, "POWR1220_VMON4");
      break;
    case SMB_SENSOR_1220_VMON5:
      sprintf(name, "POWR1220_VMON5");
      break;
    case SMB_SENSOR_1220_VMON6:
      sprintf(name, "POWR1220_VMON6");
      break;
    case SMB_SENSOR_1220_VMON7:
      sprintf(name, "POWR1220_VMON7");
      break;
    case SMB_SENSOR_1220_VMON8:
      sprintf(name, "POWR1220_VMON8");
      break;
    case SMB_SENSOR_1220_VMON9:
      sprintf(name, "POWR1220_VMON9");
      break;
    case SMB_SENSOR_1220_VMON10:
      sprintf(name, "POWR1220_VMON10");
      break;
    case SMB_SENSOR_1220_VMON11:
      sprintf(name, "POWR1220_VMON11");
      break;
    case SMB_SENSOR_1220_VMON12:
      sprintf(name, "POWR1220_VMON12");
      break;
    case SMB_SENSOR_1220_VCCA:
      sprintf(name, "POWR1220_VCCA");
      break;
    case SMB_SENSOR_1220_VCCINP:
      sprintf(name, "POWR1220_VCCINP");
      break;
    case SMB_SENSOR_TH3_SERDES_VOLT:
      sprintf(name, "TH3_SERDES_VOLT");
      break;
    case SMB_SENSOR_TH3_CORE_VOLT:
      sprintf(name, "TH3_CORE_VOLT");
      break;
    case SMB_SENSOR_FCM_T_HSC_VOLT:
      sprintf(name, "FCM_T_HSC_VOLT");
      break;
    case SMB_SENSOR_FCM_B_HSC_VOLT:
      sprintf(name, "FCM_B_HSC_VOLT");
      break;
    case SMB_SENSOR_TH3_SERDES_CURR:
      sprintf(name, "TH3_SERDES_CURR");
      break;
    case SMB_SENSOR_TH3_CORE_CURR:
      sprintf(name, "TH3_CORE_CURR");
      break;
    case SMB_SENSOR_FCM_T_HSC_CURR:
      sprintf(name, "FCM_T_HSC_CURR");
      break;
    case SMB_SENSOR_FCM_B_HSC_CURR:
      sprintf(name, "FCM_B_HSC_CURR");
      break;
    case SMB_SENSOR_FCM_T_HSC_POWER:
      sprintf(name, "FCM_T_HSC_POWER");
      break;
    case SMB_SENSOR_FCM_B_HSC_POWER:
      sprintf(name, "FCM_B_HSC_POWER");
      break;
    case SMB_SENSOR_FAN1_FRONT_TACH:
      sprintf(name, "FAN1_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN1_REAR_TACH:
      sprintf(name, "FAN1_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN2_FRONT_TACH:
      sprintf(name, "FAN2_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN2_REAR_TACH:
      sprintf(name, "FAN2_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN3_FRONT_TACH:
      sprintf(name, "FAN3_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN3_REAR_TACH:
      sprintf(name, "FAN3_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN4_FRONT_TACH:
      sprintf(name, "FAN4_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN4_REAR_TACH:
      sprintf(name, "FAN4_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN5_FRONT_TACH:
      sprintf(name, "FAN5_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN5_REAR_TACH:
      sprintf(name, "FAN5_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN6_FRONT_TACH:
      sprintf(name, "FAN6_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN6_REAR_TACH:
      sprintf(name, "FAN6_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN7_FRONT_TACH:
      sprintf(name, "FAN7_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN7_REAR_TACH:
      sprintf(name, "FAN7_REAR_SPEED");
      break;
    case SMB_SENSOR_FAN8_FRONT_TACH:
      sprintf(name, "FAN8_FRONT_SPEED");
      break;
    case SMB_SENSOR_FAN8_REAR_TACH:
      sprintf(name, "FAN8_REAR_SPEED");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_pim_sensor_name(uint8_t sensor_num, char *name) {

  switch(sensor_num) {
    case PIM1_SENSOR_TEMP1:
      sprintf(name, "PIM1_TEMP1");
      break;
    case PIM1_SENSOR_TEMP2:
      sprintf(name, "PIM1_TEMP2");
      break;
    case PIM1_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM1_QSFP_TEMP");
      break;
    case PIM1_SENSOR_HSC_VOLT:
      sprintf(name, "PIM1_HSC_VOLT");
      break;
    case PIM1_SENSOR_HSC_CURR:
      sprintf(name, "PIM1_HSC_CURR");
      break;
    case PIM1_SENSOR_HSC_POWER:
      sprintf(name, "PIM1_HSC_POWER");
      break;
    case PIM1_SENSOR_34461_VOLT1:
      sprintf(name, "PIM1_MAX34461_VOLT1");
      break;
    case PIM1_SENSOR_34461_VOLT2:
      sprintf(name, "PIM1_MAX34461_VOLT2");
      break;
    case PIM1_SENSOR_34461_VOLT3:
      sprintf(name, "PIM1_MAX34461_VOLT3");
      break;
    case PIM1_SENSOR_34461_VOLT4:
      sprintf(name, "PIM1_MAX34461_VOLT4");
      break;
    case PIM1_SENSOR_34461_VOLT5:
      sprintf(name, "PIM1_MAX34461_VOLT5");
      break;
    case PIM1_SENSOR_34461_VOLT6:
      sprintf(name, "PIM1_MAX34461_VOLT6");
      break;
    case PIM1_SENSOR_34461_VOLT7:
      sprintf(name, "PIM1_MAX34461_VOLT7");
      break;
    case PIM1_SENSOR_34461_VOLT8:
      sprintf(name, "PIM1_MAX34461_VOLT8");
      break;
    case PIM1_SENSOR_34461_VOLT9:
      sprintf(name, "PIM1_MAX34461_VOLT9");
      break;
    case PIM1_SENSOR_34461_VOLT10:
      sprintf(name, "PIM1_MAX34461_VOLT10");
      break;
    case PIM1_SENSOR_34461_VOLT11:
      sprintf(name, "PIM1_MAX34461_VOLT11");
      break;
    case PIM1_SENSOR_34461_VOLT12:
      sprintf(name, "PIM1_MAX34461_VOLT12");
      break;
    case PIM1_SENSOR_34461_VOLT13:
      sprintf(name, "PIM1_MAX34461_VOLT13");
      break;
    case PIM1_SENSOR_34461_VOLT14:
      sprintf(name, "PIM1_MAX34461_VOLT14");
      break;
    case PIM1_SENSOR_34461_VOLT15:
      sprintf(name, "PIM1_MAX34461_VOLT15");
      break;
    case PIM1_SENSOR_34461_VOLT16:
      sprintf(name, "PIM1_MAX34461_VOLT16");
      break;
    case PIM2_SENSOR_TEMP1:
      sprintf(name, "PIM2_TEMP1");
      break;
    case PIM2_SENSOR_TEMP2:
      sprintf(name, "PIM2_TEMP2");
      break;
    case PIM2_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM2_QSFP_TEMP");
      break;
    case PIM2_SENSOR_HSC_VOLT:
      sprintf(name, "PIM2_HSC_VOLT");
      break;
    case PIM2_SENSOR_HSC_CURR:
      sprintf(name, "PIM2_HSC_CURR");
      break;
    case PIM2_SENSOR_HSC_POWER:
      sprintf(name, "PIM2_HSC_POWER");
      break;
    case PIM2_SENSOR_34461_VOLT1:
      sprintf(name, "PIM2_MAX34461_VOLT1");
      break;
    case PIM2_SENSOR_34461_VOLT2:
      sprintf(name, "PIM2_MAX34461_VOLT2");
      break;
    case PIM2_SENSOR_34461_VOLT3:
      sprintf(name, "PIM2_MAX34461_VOLT3");
      break;
    case PIM2_SENSOR_34461_VOLT4:
      sprintf(name, "PIM2_MAX34461_VOLT4");
      break;
    case PIM2_SENSOR_34461_VOLT5:
      sprintf(name, "PIM2_MAX34461_VOLT5");
      break;
    case PIM2_SENSOR_34461_VOLT6:
      sprintf(name, "PIM2_MAX34461_VOLT6");
      break;
    case PIM2_SENSOR_34461_VOLT7:
      sprintf(name, "PIM2_MAX34461_VOLT7");
      break;
    case PIM2_SENSOR_34461_VOLT8:
      sprintf(name, "PIM2_MAX34461_VOLT8");
      break;
    case PIM2_SENSOR_34461_VOLT9:
      sprintf(name, "PIM2_MAX34461_VOLT9");
      break;
    case PIM2_SENSOR_34461_VOLT10:
      sprintf(name, "PIM2_MAX34461_VOLT10");
      break;
    case PIM2_SENSOR_34461_VOLT11:
      sprintf(name, "PIM2_MAX34461_VOLT11");
      break;
    case PIM2_SENSOR_34461_VOLT12:
      sprintf(name, "PIM2_MAX34461_VOLT12");
      break;
    case PIM2_SENSOR_34461_VOLT13:
      sprintf(name, "PIM2_MAX34461_VOLT13");
      break;
    case PIM2_SENSOR_34461_VOLT14:
      sprintf(name, "PIM2_MAX34461_VOLT14");
      break;
    case PIM2_SENSOR_34461_VOLT15:
      sprintf(name, "PIM2_MAX34461_VOLT15");
      break;
    case PIM2_SENSOR_34461_VOLT16:
      sprintf(name, "PIM2_MAX34461_VOLT16");
      break;
    case PIM3_SENSOR_TEMP1:
      sprintf(name, "PIM3_TEMP1");
      break;
    case PIM3_SENSOR_TEMP2:
      sprintf(name, "PIM3_TEMP2");
      break;
    case PIM3_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM3_QSFP_TEMP");
      break;
    case PIM3_SENSOR_HSC_VOLT:
      sprintf(name, "PIM3_HSC_VOLT");
      break;
    case PIM3_SENSOR_HSC_CURR:
      sprintf(name, "PIM3_HSC_CURR");
      break;
    case PIM3_SENSOR_HSC_POWER:
      sprintf(name, "PIM3_HSC_POWER");
      break;
    case PIM3_SENSOR_34461_VOLT1:
      sprintf(name, "PIM3_MAX34461_VOLT1");
      break;
    case PIM3_SENSOR_34461_VOLT2:
      sprintf(name, "PIM3_MAX34461_VOLT2");
      break;
    case PIM3_SENSOR_34461_VOLT3:
      sprintf(name, "PIM3_MAX34461_VOLT3");
      break;
    case PIM3_SENSOR_34461_VOLT4:
      sprintf(name, "PIM3_MAX34461_VOLT4");
      break;
    case PIM3_SENSOR_34461_VOLT5:
      sprintf(name, "PIM3_MAX34461_VOLT5");
      break;
    case PIM3_SENSOR_34461_VOLT6:
      sprintf(name, "PIM3_MAX34461_VOLT6");
      break;
    case PIM3_SENSOR_34461_VOLT7:
      sprintf(name, "PIM3_MAX34461_VOLT7");
      break;
    case PIM3_SENSOR_34461_VOLT8:
      sprintf(name, "PIM3_MAX34461_VOLT8");
      break;
    case PIM3_SENSOR_34461_VOLT9:
      sprintf(name, "PIM3_MAX34461_VOLT9");
      break;
    case PIM3_SENSOR_34461_VOLT10:
      sprintf(name, "PIM3_MAX34461_VOLT10");
      break;
    case PIM3_SENSOR_34461_VOLT11:
      sprintf(name, "PIM3_MAX34461_VOLT11");
      break;
    case PIM3_SENSOR_34461_VOLT12:
      sprintf(name, "PIM3_MAX34461_VOLT12");
      break;
    case PIM3_SENSOR_34461_VOLT13:
      sprintf(name, "PIM3_MAX34461_VOLT13");
      break;
    case PIM3_SENSOR_34461_VOLT14:
      sprintf(name, "PIM3_MAX34461_VOLT14");
      break;
    case PIM3_SENSOR_34461_VOLT15:
      sprintf(name, "PIM3_MAX34461_VOLT15");
      break;
    case PIM3_SENSOR_34461_VOLT16:
      sprintf(name, "PIM3_MAX34461_VOLT16");
      break;
    case PIM4_SENSOR_TEMP1:
      sprintf(name, "PIM4_TEMP1");
      break;
    case PIM4_SENSOR_TEMP2:
      sprintf(name, "PIM4_TEMP2");
      break;
    case PIM4_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM4_QSFP_TEMP");
      break;
    case PIM4_SENSOR_HSC_VOLT:
      sprintf(name, "PIM4_HSC_VOLT");
      break;
    case PIM4_SENSOR_HSC_CURR:
      sprintf(name, "PIM4_HSC_CURR");
      break;
    case PIM4_SENSOR_HSC_POWER:
      sprintf(name, "PIM4_HSC_POWER");
      break;
    case PIM4_SENSOR_34461_VOLT1:
      sprintf(name, "PIM4_MAX34461_VOLT1");
      break;
    case PIM4_SENSOR_34461_VOLT2:
      sprintf(name, "PIM4_MAX34461_VOLT2");
      break;
    case PIM4_SENSOR_34461_VOLT3:
      sprintf(name, "PIM4_MAX34461_VOLT3");
      break;
    case PIM4_SENSOR_34461_VOLT4:
      sprintf(name, "PIM4_MAX34461_VOLT4");
      break;
    case PIM4_SENSOR_34461_VOLT5:
      sprintf(name, "PIM4_MAX34461_VOLT5");
      break;
    case PIM4_SENSOR_34461_VOLT6:
      sprintf(name, "PIM4_MAX34461_VOLT6");
      break;
    case PIM4_SENSOR_34461_VOLT7:
      sprintf(name, "PIM4_MAX34461_VOLT7");
      break;
    case PIM4_SENSOR_34461_VOLT8:
      sprintf(name, "PIM4_MAX34461_VOLT8");
      break;
    case PIM4_SENSOR_34461_VOLT9:
      sprintf(name, "PIM4_MAX34461_VOLT9");
      break;
    case PIM4_SENSOR_34461_VOLT10:
      sprintf(name, "PIM4_MAX34461_VOLT10");
      break;
    case PIM4_SENSOR_34461_VOLT11:
      sprintf(name, "PIM4_MAX34461_VOLT11");
      break;
    case PIM4_SENSOR_34461_VOLT12:
      sprintf(name, "PIM4_MAX34461_VOLT12");
      break;
    case PIM4_SENSOR_34461_VOLT13:
      sprintf(name, "PIM4_MAX34461_VOLT13");
      break;
    case PIM4_SENSOR_34461_VOLT14:
      sprintf(name, "PIM4_MAX34461_VOLT14");
      break;
    case PIM4_SENSOR_34461_VOLT15:
      sprintf(name, "PIM4_MAX34461_VOLT15");
      break;
    case PIM4_SENSOR_34461_VOLT16:
      sprintf(name, "PIM4_MAX34461_VOLT16");
      break;
    case PIM5_SENSOR_TEMP1:
      sprintf(name, "PIM5_TEMP1");
      break;
    case PIM5_SENSOR_TEMP2:
      sprintf(name, "PIM5_TEMP2");
      break;
    case PIM5_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM5_QSFP_TEMP");
      break;
    case PIM5_SENSOR_HSC_VOLT:
      sprintf(name, "PIM5_HSC_VOLT");
      break;
    case PIM5_SENSOR_HSC_CURR:
      sprintf(name, "PIM5_HSC_CURR");
      break;
    case PIM5_SENSOR_HSC_POWER:
      sprintf(name, "PIM5_HSC_POWER");
      break;
    case PIM5_SENSOR_34461_VOLT1:
      sprintf(name, "PIM5_MAX34461_VOLT1");
      break;
    case PIM5_SENSOR_34461_VOLT2:
      sprintf(name, "PIM5_MAX34461_VOLT2");
      break;
    case PIM5_SENSOR_34461_VOLT3:
      sprintf(name, "PIM5_MAX34461_VOLT3");
      break;
    case PIM5_SENSOR_34461_VOLT4:
      sprintf(name, "PIM5_MAX34461_VOLT4");
      break;
    case PIM5_SENSOR_34461_VOLT5:
      sprintf(name, "PIM5_MAX34461_VOLT5");
      break;
    case PIM5_SENSOR_34461_VOLT6:
      sprintf(name, "PIM5_MAX34461_VOLT6");
      break;
    case PIM5_SENSOR_34461_VOLT7:
      sprintf(name, "PIM5_MAX34461_VOLT7");
      break;
    case PIM5_SENSOR_34461_VOLT8:
      sprintf(name, "PIM5_MAX34461_VOLT8");
      break;
    case PIM5_SENSOR_34461_VOLT9:
      sprintf(name, "PIM5_MAX34461_VOLT9");
      break;
    case PIM5_SENSOR_34461_VOLT10:
      sprintf(name, "PIM5_MAX34461_VOLT10");
      break;
    case PIM5_SENSOR_34461_VOLT11:
      sprintf(name, "PIM5_MAX34461_VOLT11");
      break;
    case PIM5_SENSOR_34461_VOLT12:
      sprintf(name, "PIM5_MAX34461_VOLT12");
      break;
    case PIM5_SENSOR_34461_VOLT13:
      sprintf(name, "PIM5_MAX34461_VOLT13");
      break;
    case PIM5_SENSOR_34461_VOLT14:
      sprintf(name, "PIM5_MAX34461_VOLT14");
      break;
    case PIM5_SENSOR_34461_VOLT15:
      sprintf(name, "PIM5_MAX34461_VOLT15");
      break;
    case PIM5_SENSOR_34461_VOLT16:
      sprintf(name, "PIM5_MAX34461_VOLT16");
      break;
    case PIM6_SENSOR_TEMP1:
      sprintf(name, "PIM6_TEMP1");
      break;
    case PIM6_SENSOR_TEMP2:
      sprintf(name, "PIM6_TEMP2");
      break;
    case PIM6_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM6_QSFP_TEMP");
      break;
    case PIM6_SENSOR_HSC_VOLT:
      sprintf(name, "PIM6_HSC_VOLT");
      break;
    case PIM6_SENSOR_HSC_CURR:
      sprintf(name, "PIM6_HSC_CURR");
      break;
    case PIM6_SENSOR_HSC_POWER:
      sprintf(name, "PIM6_HSC_POWER");
      break;
    case PIM6_SENSOR_34461_VOLT1:
      sprintf(name, "PIM6_MAX34461_VOLT1");
      break;
    case PIM6_SENSOR_34461_VOLT2:
      sprintf(name, "PIM6_MAX34461_VOLT2");
      break;
    case PIM6_SENSOR_34461_VOLT3:
      sprintf(name, "PIM6_MAX34461_VOLT3");
      break;
    case PIM6_SENSOR_34461_VOLT4:
      sprintf(name, "PIM6_MAX34461_VOLT4");
      break;
    case PIM6_SENSOR_34461_VOLT5:
      sprintf(name, "PIM6_MAX34461_VOLT5");
      break;
    case PIM6_SENSOR_34461_VOLT6:
      sprintf(name, "PIM6_MAX34461_VOLT6");
      break;
    case PIM6_SENSOR_34461_VOLT7:
      sprintf(name, "PIM6_MAX34461_VOLT7");
      break;
    case PIM6_SENSOR_34461_VOLT8:
      sprintf(name, "PIM6_MAX34461_VOLT8");
      break;
    case PIM6_SENSOR_34461_VOLT9:
      sprintf(name, "PIM6_MAX34461_VOLT9");
      break;
    case PIM6_SENSOR_34461_VOLT10:
      sprintf(name, "PIM6_MAX34461_VOLT10");
      break;
    case PIM6_SENSOR_34461_VOLT11:
      sprintf(name, "PIM6_MAX34461_VOLT11");
      break;
    case PIM6_SENSOR_34461_VOLT12:
      sprintf(name, "PIM6_MAX34461_VOLT12");
      break;
    case PIM6_SENSOR_34461_VOLT13:
      sprintf(name, "PIM6_MAX34461_VOLT13");
      break;
    case PIM6_SENSOR_34461_VOLT14:
      sprintf(name, "PIM6_MAX34461_VOLT14");
      break;
    case PIM6_SENSOR_34461_VOLT15:
      sprintf(name, "PIM6_MAX34461_VOLT15");
      break;
    case PIM6_SENSOR_34461_VOLT16:
      sprintf(name, "PIM6_MAX34461_VOLT16");
      break;
    case PIM7_SENSOR_TEMP1:
      sprintf(name, "PIM7_TEMP1");
      break;
    case PIM7_SENSOR_TEMP2:
      sprintf(name, "PIM7_TEMP2");
      break;
    case PIM7_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM7_QSFP_TEMP");
      break;
    case PIM7_SENSOR_HSC_VOLT:
      sprintf(name, "PIM7_HSC_VOLT");
      break;
    case PIM7_SENSOR_HSC_CURR:
      sprintf(name, "PIM7_HSC_CURR");
      break;
    case PIM7_SENSOR_HSC_POWER:
      sprintf(name, "PIM7_HSC_POWER");
      break;
    case PIM7_SENSOR_34461_VOLT1:
      sprintf(name, "PIM7_MAX34461_VOLT1");
      break;
    case PIM7_SENSOR_34461_VOLT2:
      sprintf(name, "PIM7_MAX34461_VOLT2");
      break;
    case PIM7_SENSOR_34461_VOLT3:
      sprintf(name, "PIM7_MAX34461_VOLT3");
      break;
    case PIM7_SENSOR_34461_VOLT4:
      sprintf(name, "PIM7_MAX34461_VOLT4");
      break;
    case PIM7_SENSOR_34461_VOLT5:
      sprintf(name, "PIM7_MAX34461_VOLT5");
      break;
    case PIM7_SENSOR_34461_VOLT6:
      sprintf(name, "PIM7_MAX34461_VOLT6");
      break;
    case PIM7_SENSOR_34461_VOLT7:
      sprintf(name, "PIM7_MAX34461_VOLT7");
      break;
    case PIM7_SENSOR_34461_VOLT8:
      sprintf(name, "PIM7_MAX34461_VOLT8");
      break;
    case PIM7_SENSOR_34461_VOLT9:
      sprintf(name, "PIM7_MAX34461_VOLT9");
      break;
    case PIM7_SENSOR_34461_VOLT10:
      sprintf(name, "PIM7_MAX34461_VOLT10");
      break;
    case PIM7_SENSOR_34461_VOLT11:
      sprintf(name, "PIM7_MAX34461_VOLT11");
      break;
    case PIM7_SENSOR_34461_VOLT12:
      sprintf(name, "PIM7_MAX34461_VOLT12");
      break;
    case PIM7_SENSOR_34461_VOLT13:
      sprintf(name, "PIM7_MAX34461_VOLT13");
      break;
    case PIM7_SENSOR_34461_VOLT14:
      sprintf(name, "PIM7_MAX34461_VOLT14");
      break;
    case PIM7_SENSOR_34461_VOLT15:
      sprintf(name, "PIM7_MAX34461_VOLT15");
      break;
    case PIM7_SENSOR_34461_VOLT16:
      sprintf(name, "PIM7_MAX34461_VOLT16");
      break;
    case PIM8_SENSOR_TEMP1:
      sprintf(name, "PIM8_TEMP1");
      break;
    case PIM8_SENSOR_TEMP2:
      sprintf(name, "PIM8_TEMP2");
      break;
    case PIM8_SENSOR_QSFP_TEMP:
      sprintf(name, "PIM8_QSFP_TEMP");
      break;
    case PIM8_SENSOR_HSC_VOLT:
      sprintf(name, "PIM8_HSC_VOLT");
      break;
    case PIM8_SENSOR_HSC_CURR:
      sprintf(name, "PIM8_HSC_CURR");
      break;
    case PIM8_SENSOR_HSC_POWER:
      sprintf(name, "PIM8_HSC_POWER");
      break;
    case PIM8_SENSOR_34461_VOLT1:
      sprintf(name, "PIM8_MAX34461_VOLT1");
      break;
    case PIM8_SENSOR_34461_VOLT2:
      sprintf(name, "PIM8_MAX34461_VOLT2");
      break;
    case PIM8_SENSOR_34461_VOLT3:
      sprintf(name, "PIM8_MAX34461_VOLT3");
      break;
    case PIM8_SENSOR_34461_VOLT4:
      sprintf(name, "PIM8_MAX34461_VOLT4");
      break;
    case PIM8_SENSOR_34461_VOLT5:
      sprintf(name, "PIM8_MAX34461_VOLT5");
      break;
    case PIM8_SENSOR_34461_VOLT6:
      sprintf(name, "PIM8_MAX34461_VOLT6");
      break;
    case PIM8_SENSOR_34461_VOLT7:
      sprintf(name, "PIM8_MAX34461_VOLT7");
      break;
    case PIM8_SENSOR_34461_VOLT8:
      sprintf(name, "PIM8_MAX34461_VOLT8");
      break;
    case PIM8_SENSOR_34461_VOLT9:
      sprintf(name, "PIM8_MAX34461_VOLT9");
      break;
    case PIM8_SENSOR_34461_VOLT10:
      sprintf(name, "PIM8_MAX34461_VOLT10");
      break;
    case PIM8_SENSOR_34461_VOLT11:
      sprintf(name, "PIM8_MAX34461_VOLT11");
      break;
    case PIM8_SENSOR_34461_VOLT12:
      sprintf(name, "PIM8_MAX34461_VOLT12");
      break;
    case PIM8_SENSOR_34461_VOLT13:
      sprintf(name, "PIM8_MAX34461_VOLT13");
      break;
    case PIM8_SENSOR_34461_VOLT14:
      sprintf(name, "PIM8_MAX34461_VOLT14");
      break;
    case PIM8_SENSOR_34461_VOLT15:
      sprintf(name, "PIM8_MAX34461_VOLT15");
      break;
    case PIM8_SENSOR_34461_VOLT16:
      sprintf(name, "PIM8_MAX34461_VOLT16");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_psu_sensor_name(uint8_t sensor_num, char *name) {

  switch(sensor_num) {
    case PSU1_SENSOR_IN_VOLT:
      sprintf(name, "PSU1_IN_VOLT");
      break;
    case PSU1_SENSOR_12V_VOLT:
      sprintf(name, "PSU1_12V_VOLT");
      break;
    case PSU1_SENSOR_STBY_VOLT:
      sprintf(name, "PSU1_STBY_VOLT");
      break;
    case PSU1_SENSOR_IN_CURR:
      sprintf(name, "PSU1_IN_CURR");
      break;
    case PSU1_SENSOR_12V_CURR:
      sprintf(name, "PSU1_12V_CURR");
      break;
    case PSU1_SENSOR_STBY_CURR:
      sprintf(name, "PSU1_STBY_CURR");
      break;
    case PSU1_SENSOR_IN_POWER:
      sprintf(name, "PSU1_IN_POWER");
      break;
    case PSU1_SENSOR_12V_POWER:
      sprintf(name, "PSU1_12V_POWER");
      break;
    case PSU1_SENSOR_STBY_POWER:
      sprintf(name, "PSU1_STBY_POWER");
      break;
    case PSU1_SENSOR_FAN_TACH:
      sprintf(name, "PSU1_FAN_SPEED");
      break;
    case PSU1_SENSOR_TEMP1:
      sprintf(name, "PSU1_TEMP1");
      break;
    case PSU1_SENSOR_TEMP2:
      sprintf(name, "PSU1_TEMP2");
      break;
    case PSU1_SENSOR_TEMP3:
      sprintf(name, "PSU1_TEMP3");
      break;
    case PSU2_SENSOR_IN_VOLT:
      sprintf(name, "PSU2_IN_VOLT");
      break;
    case PSU2_SENSOR_12V_VOLT:
      sprintf(name, "PSU2_12V_VOLT");
      break;
    case PSU2_SENSOR_STBY_VOLT:
      sprintf(name, "PSU2_STBY_VOLT");
      break;
    case PSU2_SENSOR_IN_CURR:
      sprintf(name, "PSU2_IN_CURR");
      break;
    case PSU2_SENSOR_12V_CURR:
      sprintf(name, "PSU2_12V_CURR");
      break;
    case PSU2_SENSOR_STBY_CURR:
      sprintf(name, "PSU2_STBY_CURR");
      break;
    case PSU2_SENSOR_IN_POWER:
      sprintf(name, "PSU2_IN_POWER");
      break;
    case PSU2_SENSOR_12V_POWER:
      sprintf(name, "PSU2_12V_POWER");
      break;
    case PSU2_SENSOR_STBY_POWER:
      sprintf(name, "PSU2_STBY_POWER");
      break;
    case PSU2_SENSOR_FAN_TACH:
      sprintf(name, "PSU2_FAN_SPEED");
      break;
    case PSU2_SENSOR_TEMP1:
      sprintf(name, "PSU2_TEMP1");
      break;
    case PSU2_SENSOR_TEMP2:
      sprintf(name, "PSU2_TEMP2");
      break;
    case PSU2_SENSOR_TEMP3:
      sprintf(name, "PSU2_TEMP3");
      break;
    case PSU3_SENSOR_IN_VOLT:
      sprintf(name, "PSU3_IN_VOLT");
      break;
    case PSU3_SENSOR_12V_VOLT:
      sprintf(name, "PSU3_12V_VOLT");
      break;
    case PSU3_SENSOR_STBY_VOLT:
      sprintf(name, "PSU3_STBY_VOLT");
      break;
    case PSU3_SENSOR_IN_CURR:
      sprintf(name, "PSU3_IN_CURR");
      break;
    case PSU3_SENSOR_12V_CURR:
      sprintf(name, "PSU3_12V_CURR");
      break;
    case PSU3_SENSOR_STBY_CURR:
      sprintf(name, "PSU3_STBY_CURR");
      break;
    case PSU3_SENSOR_IN_POWER:
      sprintf(name, "PSU3_IN_POWER");
      break;
    case PSU3_SENSOR_12V_POWER:
      sprintf(name, "PSU3_12V_POWER");
      break;
    case PSU3_SENSOR_STBY_POWER:
      sprintf(name, "PSU3_STBY_POWER");
      break;
    case PSU3_SENSOR_FAN_TACH:
      sprintf(name, "PSU3_FAN_SPEED");
      break;
    case PSU3_SENSOR_TEMP1:
      sprintf(name, "PSU3_TEMP1");
      break;
    case PSU3_SENSOR_TEMP2:
      sprintf(name, "PSU3_TEMP2");
      break;
    case PSU3_SENSOR_TEMP3:
      sprintf(name, "PSU3_TEMP3");
      break;
    case PSU4_SENSOR_IN_VOLT:
      sprintf(name, "PSU4_IN_VOLT");
      break;
    case PSU4_SENSOR_12V_VOLT:
      sprintf(name, "PSU4_12V_VOLT");
      break;
    case PSU4_SENSOR_STBY_VOLT:
      sprintf(name, "PSU4_STBY_VOLT");
      break;
    case PSU4_SENSOR_IN_CURR:
      sprintf(name, "PSU4_IN_CURR");
      break;
    case PSU4_SENSOR_12V_CURR:
      sprintf(name, "PSU4_12V_CURR");
      break;
    case PSU4_SENSOR_STBY_CURR:
      sprintf(name, "PSU4_STBY_CURR");
      break;
    case PSU4_SENSOR_IN_POWER:
      sprintf(name, "PSU4_IN_POWER");
      break;
    case PSU4_SENSOR_12V_POWER:
      sprintf(name, "PSU4_12V_POWER");
      break;
    case PSU4_SENSOR_STBY_POWER:
      sprintf(name, "PSU4_STBY_POWER");
      break;
    case PSU4_SENSOR_FAN_TACH:
      sprintf(name, "PSU4_FAN_SPEED");
      break;
    case PSU4_SENSOR_TEMP1:
      sprintf(name, "PSU4_TEMP1");
      break;
    case PSU4_SENSOR_TEMP2:
      sprintf(name, "PSU4_TEMP2");
      break;
    case PSU4_SENSOR_TEMP3:
      sprintf(name, "PSU4_TEMP3");
      break;
    default:
      return -1;
  }
  return 0;
}

int
pal_get_sensor_name(uint8_t fru, uint8_t sensor_num, char *name) {

  int ret = -1;

  switch(fru) {
    case FRU_SCM:
      ret = get_scm_sensor_name(sensor_num, name);
      break;
    case FRU_SMB:
      ret = get_smb_sensor_name(sensor_num, name);
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      ret = get_pim_sensor_name(sensor_num, name);
      break;
    case FRU_PSU1:
    case FRU_PSU2:
    case FRU_PSU3:
    case FRU_PSU4:
      ret = get_psu_sensor_name(sensor_num, name);
      break;
    default:
      return -1;
  }
  return ret;
}

static int
get_scm_sensor_units(uint8_t sensor_num, char *units) {

  switch(sensor_num) {
    case SCM_SENSOR_OUTLET_LOCAL_TEMP:
    case SCM_SENSOR_OUTLET_REMOTE_TEMP:
    case SCM_SENSOR_INLET_LOCAL_TEMP:
    case SCM_SENSOR_INLET_REMOTE_TEMP:
    case BIC_SENSOR_MB_OUTLET_TEMP:
    case BIC_SENSOR_MB_INLET_TEMP:
    case BIC_SENSOR_PCH_TEMP:
    case BIC_SENSOR_VCCIN_VR_TEMP:
    case BIC_SENSOR_1V05MIX_VR_TEMP:
    case BIC_SENSOR_SOC_TEMP:
    case BIC_SENSOR_SOC_THERM_MARGIN:
    case BIC_SENSOR_VDDR_VR_TEMP:
    case BIC_SENSOR_SOC_DIMMA0_TEMP:
    case BIC_SENSOR_SOC_DIMMB0_TEMP:
    case BIC_SENSOR_SOC_TJMAX:
      sprintf(units, "C");
      break;
    case SCM_SENSOR_HSC_VOLT:
    case BIC_SENSOR_P3V3_MB:
    case BIC_SENSOR_P12V_MB:
    case BIC_SENSOR_P1V05_PCH:
    case BIC_SENSOR_P3V3_STBY_MB:
    case BIC_SENSOR_P5V_STBY_MB:
    case BIC_SENSOR_PV_BAT:
    case BIC_SENSOR_PVDDR:
    case BIC_SENSOR_P1V05_MIX:
    case BIC_SENSOR_VCCIN_VR_VOL:
    case BIC_SENSOR_VDDR_VR_VOL:
    case BIC_SENSOR_P1V05MIX_VR_VOL:
    case BIC_SENSOR_INA230_VOL:
      sprintf(units, "Volts");
      break;
    case SCM_SENSOR_HSC_CURR:
    case BIC_SENSOR_1V05MIX_VR_CURR:
    case BIC_SENSOR_VDDR_VR_CURR:
    case BIC_SENSOR_VCCIN_VR_CURR:
      sprintf(units, "Amps");
      break;
    case SCM_SENSOR_HSC_POWER:
    case BIC_SENSOR_SOC_PACKAGE_PWR:
    case BIC_SENSOR_VCCIN_VR_POUT:
    case BIC_SENSOR_VDDR_VR_POUT:
    case BIC_SENSOR_P1V05MIX_VR_POUT:
    case BIC_SENSOR_INA230_POWER:
      sprintf(units, "Watts");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_smb_sensor_units(uint8_t sensor_num, char *units) {

  switch(sensor_num) {
    case SMB_SENSOR_TH3_SERDES_TEMP:
    case SMB_SENSOR_TH3_CORE_TEMP:
    case SMB_SENSOR_TEMP1:
    case SMB_SENSOR_TEMP2:
    case SMB_SENSOR_TEMP3:
    case SMB_SENSOR_TEMP4:
    case SMB_SENSOR_TEMP5:
    case SMB_SENSOR_TH3_DIE_TEMP1:
    case SMB_SENSOR_TH3_DIE_TEMP2:
    case SMB_SENSOR_PDB_L_TEMP1:
    case SMB_SENSOR_PDB_L_TEMP2:
    case SMB_SENSOR_PDB_R_TEMP1:
    case SMB_SENSOR_PDB_R_TEMP2:
    case SMB_SENSOR_FCM_T_TEMP1:
    case SMB_SENSOR_FCM_T_TEMP2:
    case SMB_SENSOR_FCM_B_TEMP1:
    case SMB_SENSOR_FCM_B_TEMP2:
      sprintf(units, "C");
      break;
    case SMB_SENSOR_1220_VMON1:
    case SMB_SENSOR_1220_VMON2:
    case SMB_SENSOR_1220_VMON3:
    case SMB_SENSOR_1220_VMON4:
    case SMB_SENSOR_1220_VMON5:
    case SMB_SENSOR_1220_VMON6:
    case SMB_SENSOR_1220_VMON7:
    case SMB_SENSOR_1220_VMON8:
    case SMB_SENSOR_1220_VMON9:
    case SMB_SENSOR_1220_VMON10:
    case SMB_SENSOR_1220_VMON11:
    case SMB_SENSOR_1220_VMON12:
    case SMB_SENSOR_1220_VCCA:
    case SMB_SENSOR_1220_VCCINP:
    case SMB_SENSOR_TH3_SERDES_VOLT:
    case SMB_SENSOR_TH3_CORE_VOLT:
    case SMB_SENSOR_FCM_T_HSC_VOLT:
    case SMB_SENSOR_FCM_B_HSC_VOLT:
      sprintf(units, "Volts");
      break;
    case SMB_SENSOR_TH3_SERDES_CURR:
    case SMB_SENSOR_TH3_CORE_CURR:
    case SMB_SENSOR_FCM_T_HSC_CURR:
    case SMB_SENSOR_FCM_B_HSC_CURR:
      sprintf(units, "Amps");
      break;
    case SMB_SENSOR_FCM_T_HSC_POWER:
    case SMB_SENSOR_FCM_B_HSC_POWER:
      sprintf(units, "Watts");
      break;
    case SMB_SENSOR_FAN1_FRONT_TACH:
    case SMB_SENSOR_FAN1_REAR_TACH:
    case SMB_SENSOR_FAN2_FRONT_TACH:
    case SMB_SENSOR_FAN2_REAR_TACH:
    case SMB_SENSOR_FAN3_FRONT_TACH:
    case SMB_SENSOR_FAN3_REAR_TACH:
    case SMB_SENSOR_FAN4_FRONT_TACH:
    case SMB_SENSOR_FAN4_REAR_TACH:
    case SMB_SENSOR_FAN5_FRONT_TACH:
    case SMB_SENSOR_FAN5_REAR_TACH:
    case SMB_SENSOR_FAN6_FRONT_TACH:
    case SMB_SENSOR_FAN6_REAR_TACH:
    case SMB_SENSOR_FAN7_FRONT_TACH:
    case SMB_SENSOR_FAN7_REAR_TACH:
    case SMB_SENSOR_FAN8_FRONT_TACH:
    case SMB_SENSOR_FAN8_REAR_TACH:
      sprintf(units, "RPM");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_pim_sensor_units(uint8_t sensor_num, char *units) {

  switch(sensor_num) {
    case PIM1_SENSOR_TEMP1:
    case PIM1_SENSOR_TEMP2:
    case PIM2_SENSOR_TEMP1:
    case PIM2_SENSOR_TEMP2:
    case PIM3_SENSOR_TEMP1:
    case PIM3_SENSOR_TEMP2:
    case PIM4_SENSOR_TEMP1:
    case PIM4_SENSOR_TEMP2:
    case PIM5_SENSOR_TEMP1:
    case PIM5_SENSOR_TEMP2:
    case PIM6_SENSOR_TEMP1:
    case PIM6_SENSOR_TEMP2:
    case PIM7_SENSOR_TEMP1:
    case PIM7_SENSOR_TEMP2:
    case PIM8_SENSOR_TEMP1:
    case PIM8_SENSOR_TEMP2:
    case PIM1_SENSOR_QSFP_TEMP:
    case PIM2_SENSOR_QSFP_TEMP:
    case PIM3_SENSOR_QSFP_TEMP:
    case PIM4_SENSOR_QSFP_TEMP:
    case PIM5_SENSOR_QSFP_TEMP:
    case PIM6_SENSOR_QSFP_TEMP:
    case PIM7_SENSOR_QSFP_TEMP:
    case PIM8_SENSOR_QSFP_TEMP:
      sprintf(units, "C");
      break;
    case PIM1_SENSOR_HSC_CURR:
    case PIM2_SENSOR_HSC_CURR:
    case PIM3_SENSOR_HSC_CURR:
    case PIM4_SENSOR_HSC_CURR:
    case PIM5_SENSOR_HSC_CURR:
    case PIM6_SENSOR_HSC_CURR:
    case PIM7_SENSOR_HSC_CURR:
    case PIM8_SENSOR_HSC_CURR:
      sprintf(units, "Amps");
      break;
    case PIM1_SENSOR_HSC_POWER:
    case PIM2_SENSOR_HSC_POWER:
    case PIM3_SENSOR_HSC_POWER:
    case PIM4_SENSOR_HSC_POWER:
    case PIM5_SENSOR_HSC_POWER:
    case PIM6_SENSOR_HSC_POWER:
    case PIM7_SENSOR_HSC_POWER:
    case PIM8_SENSOR_HSC_POWER:
      sprintf(units, "Watts");
      break;
    case PIM1_SENSOR_HSC_VOLT:
    case PIM2_SENSOR_HSC_VOLT:
    case PIM3_SENSOR_HSC_VOLT:
    case PIM4_SENSOR_HSC_VOLT:
    case PIM5_SENSOR_HSC_VOLT:
    case PIM6_SENSOR_HSC_VOLT:
    case PIM7_SENSOR_HSC_VOLT:
    case PIM8_SENSOR_HSC_VOLT:
    case PIM1_SENSOR_34461_VOLT1:
    case PIM1_SENSOR_34461_VOLT2:
    case PIM1_SENSOR_34461_VOLT3:
    case PIM1_SENSOR_34461_VOLT4:
    case PIM1_SENSOR_34461_VOLT5:
    case PIM1_SENSOR_34461_VOLT6:
    case PIM1_SENSOR_34461_VOLT7:
    case PIM1_SENSOR_34461_VOLT8:
    case PIM1_SENSOR_34461_VOLT9:
    case PIM1_SENSOR_34461_VOLT10:
    case PIM1_SENSOR_34461_VOLT11:
    case PIM1_SENSOR_34461_VOLT12:
    case PIM1_SENSOR_34461_VOLT13:
    case PIM1_SENSOR_34461_VOLT14:
    case PIM1_SENSOR_34461_VOLT15:
    case PIM1_SENSOR_34461_VOLT16:
    case PIM2_SENSOR_34461_VOLT1:
    case PIM2_SENSOR_34461_VOLT2:
    case PIM2_SENSOR_34461_VOLT3:
    case PIM2_SENSOR_34461_VOLT4:
    case PIM2_SENSOR_34461_VOLT5:
    case PIM2_SENSOR_34461_VOLT6:
    case PIM2_SENSOR_34461_VOLT7:
    case PIM2_SENSOR_34461_VOLT8:
    case PIM2_SENSOR_34461_VOLT9:
    case PIM2_SENSOR_34461_VOLT10:
    case PIM2_SENSOR_34461_VOLT11:
    case PIM2_SENSOR_34461_VOLT12:
    case PIM2_SENSOR_34461_VOLT13:
    case PIM2_SENSOR_34461_VOLT14:
    case PIM2_SENSOR_34461_VOLT15:
    case PIM2_SENSOR_34461_VOLT16:
    case PIM3_SENSOR_34461_VOLT1:
    case PIM3_SENSOR_34461_VOLT2:
    case PIM3_SENSOR_34461_VOLT3:
    case PIM3_SENSOR_34461_VOLT4:
    case PIM3_SENSOR_34461_VOLT5:
    case PIM3_SENSOR_34461_VOLT6:
    case PIM3_SENSOR_34461_VOLT7:
    case PIM3_SENSOR_34461_VOLT8:
    case PIM3_SENSOR_34461_VOLT9:
    case PIM3_SENSOR_34461_VOLT10:
    case PIM3_SENSOR_34461_VOLT11:
    case PIM3_SENSOR_34461_VOLT12:
    case PIM3_SENSOR_34461_VOLT13:
    case PIM3_SENSOR_34461_VOLT14:
    case PIM3_SENSOR_34461_VOLT15:
    case PIM3_SENSOR_34461_VOLT16:
    case PIM4_SENSOR_34461_VOLT1:
    case PIM4_SENSOR_34461_VOLT2:
    case PIM4_SENSOR_34461_VOLT3:
    case PIM4_SENSOR_34461_VOLT4:
    case PIM4_SENSOR_34461_VOLT5:
    case PIM4_SENSOR_34461_VOLT6:
    case PIM4_SENSOR_34461_VOLT7:
    case PIM4_SENSOR_34461_VOLT8:
    case PIM4_SENSOR_34461_VOLT9:
    case PIM4_SENSOR_34461_VOLT10:
    case PIM4_SENSOR_34461_VOLT11:
    case PIM4_SENSOR_34461_VOLT12:
    case PIM4_SENSOR_34461_VOLT13:
    case PIM4_SENSOR_34461_VOLT14:
    case PIM4_SENSOR_34461_VOLT15:
    case PIM4_SENSOR_34461_VOLT16:
    case PIM5_SENSOR_34461_VOLT1:
    case PIM5_SENSOR_34461_VOLT2:
    case PIM5_SENSOR_34461_VOLT3:
    case PIM5_SENSOR_34461_VOLT4:
    case PIM5_SENSOR_34461_VOLT5:
    case PIM5_SENSOR_34461_VOLT6:
    case PIM5_SENSOR_34461_VOLT7:
    case PIM5_SENSOR_34461_VOLT8:
    case PIM5_SENSOR_34461_VOLT9:
    case PIM5_SENSOR_34461_VOLT10:
    case PIM5_SENSOR_34461_VOLT11:
    case PIM5_SENSOR_34461_VOLT12:
    case PIM5_SENSOR_34461_VOLT13:
    case PIM5_SENSOR_34461_VOLT14:
    case PIM5_SENSOR_34461_VOLT15:
    case PIM5_SENSOR_34461_VOLT16:
    case PIM6_SENSOR_34461_VOLT1:
    case PIM6_SENSOR_34461_VOLT2:
    case PIM6_SENSOR_34461_VOLT3:
    case PIM6_SENSOR_34461_VOLT4:
    case PIM6_SENSOR_34461_VOLT5:
    case PIM6_SENSOR_34461_VOLT6:
    case PIM6_SENSOR_34461_VOLT7:
    case PIM6_SENSOR_34461_VOLT8:
    case PIM6_SENSOR_34461_VOLT9:
    case PIM6_SENSOR_34461_VOLT10:
    case PIM6_SENSOR_34461_VOLT11:
    case PIM6_SENSOR_34461_VOLT12:
    case PIM6_SENSOR_34461_VOLT13:
    case PIM6_SENSOR_34461_VOLT14:
    case PIM6_SENSOR_34461_VOLT15:
    case PIM6_SENSOR_34461_VOLT16:
    case PIM7_SENSOR_34461_VOLT1:
    case PIM7_SENSOR_34461_VOLT2:
    case PIM7_SENSOR_34461_VOLT3:
    case PIM7_SENSOR_34461_VOLT4:
    case PIM7_SENSOR_34461_VOLT5:
    case PIM7_SENSOR_34461_VOLT6:
    case PIM7_SENSOR_34461_VOLT7:
    case PIM7_SENSOR_34461_VOLT8:
    case PIM7_SENSOR_34461_VOLT9:
    case PIM7_SENSOR_34461_VOLT10:
    case PIM7_SENSOR_34461_VOLT11:
    case PIM7_SENSOR_34461_VOLT12:
    case PIM7_SENSOR_34461_VOLT13:
    case PIM7_SENSOR_34461_VOLT14:
    case PIM7_SENSOR_34461_VOLT15:
    case PIM7_SENSOR_34461_VOLT16:
    case PIM8_SENSOR_34461_VOLT1:
    case PIM8_SENSOR_34461_VOLT2:
    case PIM8_SENSOR_34461_VOLT3:
    case PIM8_SENSOR_34461_VOLT4:
    case PIM8_SENSOR_34461_VOLT5:
    case PIM8_SENSOR_34461_VOLT6:
    case PIM8_SENSOR_34461_VOLT7:
    case PIM8_SENSOR_34461_VOLT8:
    case PIM8_SENSOR_34461_VOLT9:
    case PIM8_SENSOR_34461_VOLT10:
    case PIM8_SENSOR_34461_VOLT11:
    case PIM8_SENSOR_34461_VOLT12:
    case PIM8_SENSOR_34461_VOLT13:
    case PIM8_SENSOR_34461_VOLT14:
    case PIM8_SENSOR_34461_VOLT15:
    case PIM8_SENSOR_34461_VOLT16:
      sprintf(units, "Volts");
      break;
    default:
      return -1;
  }
  return 0;
}

static int
get_psu_sensor_units(uint8_t sensor_num, char *units) {

  switch(sensor_num) {
    case PSU1_SENSOR_IN_VOLT:
    case PSU1_SENSOR_12V_VOLT:
    case PSU1_SENSOR_STBY_VOLT:
    case PSU2_SENSOR_IN_VOLT:
    case PSU2_SENSOR_12V_VOLT:
    case PSU2_SENSOR_STBY_VOLT:
    case PSU3_SENSOR_IN_VOLT:
    case PSU3_SENSOR_12V_VOLT:
    case PSU3_SENSOR_STBY_VOLT:
    case PSU4_SENSOR_IN_VOLT:
    case PSU4_SENSOR_12V_VOLT:
    case PSU4_SENSOR_STBY_VOLT:
      sprintf(units, "Volts");
      break;
    case PSU1_SENSOR_IN_CURR:
    case PSU1_SENSOR_12V_CURR:
    case PSU1_SENSOR_STBY_CURR:
    case PSU2_SENSOR_IN_CURR:
    case PSU2_SENSOR_12V_CURR:
    case PSU2_SENSOR_STBY_CURR:
    case PSU3_SENSOR_IN_CURR:
    case PSU3_SENSOR_12V_CURR:
    case PSU3_SENSOR_STBY_CURR:
    case PSU4_SENSOR_IN_CURR:
    case PSU4_SENSOR_12V_CURR:
    case PSU4_SENSOR_STBY_CURR:
      sprintf(units, "Amps");
      break;
    case PSU1_SENSOR_IN_POWER:
    case PSU1_SENSOR_12V_POWER:
    case PSU1_SENSOR_STBY_POWER:
    case PSU2_SENSOR_IN_POWER:
    case PSU2_SENSOR_12V_POWER:
    case PSU2_SENSOR_STBY_POWER:
    case PSU3_SENSOR_IN_POWER:
    case PSU3_SENSOR_12V_POWER:
    case PSU3_SENSOR_STBY_POWER:
    case PSU4_SENSOR_IN_POWER:
    case PSU4_SENSOR_12V_POWER:
    case PSU4_SENSOR_STBY_POWER:
      sprintf(units, "Watts");
      break;
    case PSU1_SENSOR_FAN_TACH:
    case PSU2_SENSOR_FAN_TACH:
    case PSU3_SENSOR_FAN_TACH:
    case PSU4_SENSOR_FAN_TACH:
      sprintf(units, "RPM");
      break;
    case PSU1_SENSOR_TEMP1:
    case PSU1_SENSOR_TEMP2:
    case PSU1_SENSOR_TEMP3:
    case PSU2_SENSOR_TEMP1:
    case PSU2_SENSOR_TEMP2:
    case PSU2_SENSOR_TEMP3:
    case PSU3_SENSOR_TEMP1:
    case PSU3_SENSOR_TEMP2:
    case PSU3_SENSOR_TEMP3:
    case PSU4_SENSOR_TEMP1:
    case PSU4_SENSOR_TEMP2:
    case PSU4_SENSOR_TEMP3:
      sprintf(units, "C");
      break;
     default:
      return -1;
  }
  return 0;
}

int
pal_get_sensor_units(uint8_t fru, uint8_t sensor_num, char *units) {
  int ret = -1;

  switch(fru) {
    case FRU_SCM:
      ret = get_scm_sensor_units(sensor_num, units);
      break;
    case FRU_SMB:
      ret = get_smb_sensor_units(sensor_num, units);
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      ret = get_pim_sensor_units(sensor_num, units);
      break;
    case FRU_PSU1:
    case FRU_PSU2:
    case FRU_PSU3:
    case FRU_PSU4:
      ret = get_psu_sensor_units(sensor_num, units);
      break;
    default:
      return -1;
  }
  return ret;
}

static void
sensor_thresh_array_init(uint8_t fru) {
  static bool init_done[MAX_NUM_FRUS] = {false};
  int i = 0, j;
  float fvalue;

  if (init_done[fru])
    return;

  switch (fru) {
    case FRU_SCM:
      scm_sensor_threshold[SCM_SENSOR_OUTLET_LOCAL_TEMP][UCR_THRESH] = 53;
      scm_sensor_threshold[SCM_SENSOR_OUTLET_REMOTE_TEMP][UCR_THRESH] = 53;
      scm_sensor_threshold[SCM_SENSOR_INLET_LOCAL_TEMP][UCR_THRESH] = 50;
      scm_sensor_threshold[SCM_SENSOR_INLET_REMOTE_TEMP][UCR_THRESH] = 50;
      scm_sensor_threshold[SCM_SENSOR_HSC_VOLT][UCR_THRESH] = 12.6;
      scm_sensor_threshold[SCM_SENSOR_HSC_VOLT][LCR_THRESH] = 11.4;
      scm_sensor_threshold[SCM_SENSOR_HSC_CURR][UCR_THRESH] = 5.8;
      scm_sensor_threshold[SCM_SENSOR_HSC_POWER][UCR_THRESH] = 70;
      for (i = scm_sensor_cnt; i < scm_all_sensor_cnt; i++) {
        for (j = 1; j <= MAX_SENSOR_THRESHOLD; j++) {
          if (!bic_get_sdr_thresh_val(fru, scm_all_sensor_list[i], j, &fvalue)){
            scm_sensor_threshold[scm_all_sensor_list[i]][j] = fvalue;
          } else {
            /* Error case, if get BIC data retry more than 30 times(30s),
             * it means BIC get wrong, skip init BIC threshold value */
            goto scm_thresh_done;
          }
        }
      }
scm_thresh_done:
      kv_set(SCM_INIT_THRESH_STATUS, "done", 0, 0);
      break;
    case FRU_SMB:
      smb_sensor_threshold[SMB_SENSOR_1220_VMON1][UCR_THRESH] = 4.32;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON1][LCR_THRESH] = 3.68;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON2][UCR_THRESH] = 3.564;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON2][LCR_THRESH] = 3.036;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON3][UCR_THRESH] = 5.4;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON3][LCR_THRESH] = 4.6;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON4][UCR_THRESH] = 3.564;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON4][LCR_THRESH] = 3.036;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON5][UCR_THRESH] = 2.7;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON5][LCR_THRESH] = 2.3;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON6][UCR_THRESH] = 1.296;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON6][LCR_THRESH] = 1.104;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON7][UCR_THRESH] = 1.296;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON7][LCR_THRESH] = 1.104;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON8][UCR_THRESH] = 3.564;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON8][LCR_THRESH] = 3.036;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON9][UCR_THRESH] = 0.927;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON9][LCR_THRESH] = 0.727;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON10][UCR_THRESH] = 0.927;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON10][LCR_THRESH] = 0.736;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON11][UCR_THRESH] = 1.944;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON11][LCR_THRESH] = 1.656;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON12][UCR_THRESH] = 1.296;
      smb_sensor_threshold[SMB_SENSOR_1220_VMON12][LCR_THRESH] = 1.104;
      smb_sensor_threshold[SMB_SENSOR_1220_VCCA][UCR_THRESH] = 3.564;
      smb_sensor_threshold[SMB_SENSOR_1220_VCCA][LCR_THRESH] = 3.036;
      smb_sensor_threshold[SMB_SENSOR_1220_VCCINP][UCR_THRESH] = 3.564;
      smb_sensor_threshold[SMB_SENSOR_1220_VCCINP][LCR_THRESH] = 3.036;
      smb_sensor_threshold[SMB_SENSOR_TH3_SERDES_VOLT][UCR_THRESH] = 0.927;
      smb_sensor_threshold[SMB_SENSOR_TH3_SERDES_VOLT][LCR_THRESH] = 0.736;
      smb_sensor_threshold[SMB_SENSOR_TH3_SERDES_CURR][UCR_THRESH] = 80;
      smb_sensor_threshold[SMB_SENSOR_TH3_SERDES_TEMP][UCR_THRESH] = 90;
      smb_sensor_threshold[SMB_SENSOR_TH3_CORE_VOLT][UCR_THRESH] = 0.927;
      smb_sensor_threshold[SMB_SENSOR_TH3_CORE_VOLT][LCR_THRESH] = 0.727;
      smb_sensor_threshold[SMB_SENSOR_TH3_CORE_CURR][UCR_THRESH] = 300;
      smb_sensor_threshold[SMB_SENSOR_TH3_CORE_TEMP][UCR_THRESH] = 90;
      smb_sensor_threshold[SMB_SENSOR_TEMP1][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_TEMP2][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_TEMP3][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_TEMP4][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_TEMP5][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_TH3_DIE_TEMP1][UCR_THRESH] = 105;
      smb_sensor_threshold[SMB_SENSOR_TH3_DIE_TEMP2][UCR_THRESH] = 105;
      smb_sensor_threshold[SMB_SENSOR_PDB_L_TEMP1][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_PDB_L_TEMP2][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_PDB_R_TEMP1][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_PDB_R_TEMP2][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_TEMP1][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_TEMP2][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_TEMP1][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_TEMP2][UCR_THRESH] = 70;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_HSC_VOLT][UCR_THRESH] = 12.6;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_HSC_VOLT][LCR_THRESH] = 11.4;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_HSC_CURR][UCR_THRESH] = 29;
      smb_sensor_threshold[SMB_SENSOR_FCM_T_HSC_POWER][UCR_THRESH] = 350;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_HSC_VOLT][UCR_THRESH] = 12.6;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_HSC_VOLT][LCR_THRESH] = 11.4;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_HSC_CURR][UCR_THRESH] = 29;
      smb_sensor_threshold[SMB_SENSOR_FCM_B_HSC_POWER][UCR_THRESH] = 350;
      smb_sensor_threshold[SMB_SENSOR_FAN1_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN1_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN1_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN1_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN2_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN2_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN2_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN2_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN3_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN3_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN3_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN3_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN4_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN4_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN4_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN4_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN5_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN5_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN5_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN5_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN6_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN6_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN6_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN6_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN7_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN7_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN7_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN7_REAR_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN8_FRONT_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN8_FRONT_TACH][LCR_THRESH] = 800;
      smb_sensor_threshold[SMB_SENSOR_FAN8_REAR_TACH][UCR_THRESH] = 12000;
      smb_sensor_threshold[SMB_SENSOR_FAN8_REAR_TACH][LCR_THRESH] = 800;
      break;
    case FRU_PSU1:
    case FRU_PSU2:
    case FRU_PSU3:
    case FRU_PSU4:
      i = fru - 11;
      psu_sensor_threshold[PSU1_SENSOR_IN_VOLT+(i*0x0d)][UCR_THRESH] = 310;
      psu_sensor_threshold[PSU1_SENSOR_IN_VOLT+(i*0x0d)][LCR_THRESH] = 92;
      psu_sensor_threshold[PSU1_SENSOR_12V_VOLT+(i*0x0d)][UCR_THRESH] = 13;
      psu_sensor_threshold[PSU1_SENSOR_12V_VOLT+(i*0x0d)][LCR_THRESH] = 11;
      psu_sensor_threshold[PSU1_SENSOR_STBY_VOLT+(i*0x0d)][UCR_THRESH] = 3.6;
      psu_sensor_threshold[PSU1_SENSOR_STBY_VOLT+(i*0x0d)][LCR_THRESH] = 3.0;
      psu_sensor_threshold[PSU1_SENSOR_IN_CURR+(i*0x0d)][UCR_THRESH] = 10;
      psu_sensor_threshold[PSU1_SENSOR_12V_CURR+(i*0x0d)][UCR_THRESH] = 125;
      psu_sensor_threshold[PSU1_SENSOR_STBY_CURR+(i*0x0d)][UCR_THRESH] = 5;
      psu_sensor_threshold[PSU1_SENSOR_IN_POWER+(i*0x0d)][UCR_THRESH] = 1500;
      psu_sensor_threshold[PSU1_SENSOR_12V_POWER+(i*0x0d)][UCR_THRESH] = 1500;
      psu_sensor_threshold[PSU1_SENSOR_STBY_POWER+(i*0x0d)][UCR_THRESH] = 15;
      psu_sensor_threshold[PSU1_SENSOR_FAN_TACH+(i*0x0d)][LCR_THRESH] = 500;
      psu_sensor_threshold[PSU1_SENSOR_TEMP1+(i*0x0d)][UCR_THRESH] = 60;
      psu_sensor_threshold[PSU1_SENSOR_TEMP2+(i*0x0d)][UCR_THRESH] = 80;
      psu_sensor_threshold[PSU1_SENSOR_TEMP3+(i*0x0d)][UCR_THRESH] = 95;
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      pim_thresh_array_init(fru);
      break;
  }
  init_done[fru] = true;
}

int
pal_get_sensor_threshold(uint8_t fru, uint8_t sensor_num,
                                      uint8_t thresh, void *value) {
  float *val = (float*) value;

  sensor_thresh_array_init(fru);

  switch(fru) {
  case FRU_SCM:
    *val = scm_sensor_threshold[sensor_num][thresh];
    break;
  case FRU_SMB:
    *val = smb_sensor_threshold[sensor_num][thresh];
    break;
  case FRU_PIM1:
  case FRU_PIM2:
  case FRU_PIM3:
  case FRU_PIM4:
  case FRU_PIM5:
  case FRU_PIM6:
  case FRU_PIM7:
  case FRU_PIM8:
    *val = pim_sensor_threshold[sensor_num][thresh];
    break;
  case FRU_PSU1:
  case FRU_PSU2:
  case FRU_PSU3:
  case FRU_PSU4:
    *val = psu_sensor_threshold[sensor_num][thresh];
    break;
  default:
    return -1;
  }
  return 0;
}

bool
pal_is_fw_update_ongoing(uint8_t fru) {

  char key[MAX_KEY_LEN];
  char value[MAX_VALUE_LEN] = {0};
  int ret;
  struct timespec ts;

  switch (fru) {
    case FRU_SCM:
      sprintf(key, "slot%d_fwupd", IPMB_BUS);
      break;
    default:
      return false;
  }

  ret = kv_get(key, value, NULL, 0);
  if (ret < 0) {
     return false;
  }

  clock_gettime(CLOCK_MONOTONIC, &ts);
  if (strtoul(value, NULL, 10) > ts.tv_sec)
     return true;

  return false;
}

int
pal_get_fw_info(uint8_t fru, unsigned char target,
                unsigned char* res, unsigned char* res_len) {
  return -1;
}

static sensor_desc_t *
get_sensor_desc(uint8_t fru, uint8_t snr_num) {

  if (fru < 1 || fru > MAX_NUM_FRUS) {
    syslog(LOG_WARNING, "get_sensor_desc: Wrong FRU ID %d\n", fru);
    return NULL;
  }

  return &m_snr_desc[fru-1][snr_num];
}

static int
_set_pim_sts_led(uint8_t fru, uint8_t color)
{
  char path[LARGEST_DEVICE_NAME];
  uint8_t bus = 80 + ((fru - 3) * 8);

  snprintf(path, LARGEST_DEVICE_NAME,
           I2C_SYSFS_DEVICES"/%d-0060/system_led", bus);

  if(color == FPGA_STS_CLR_BLUE)
    write_device(path, "1");
  else if(color == FPGA_STS_CLR_YELLOW)
    write_device(path, "0");

  return 0;
}

void
pal_set_pim_sts_led(uint8_t fru)
{
  int val;
  char tmp[LARGEST_DEVICE_NAME];
  char path[LARGEST_DEVICE_NAME + 1];
  snprintf(tmp, LARGEST_DEVICE_NAME, KV_PATH, KV_PIM_HEALTH);
  /* FRU_PIM1 = 3, FRU_PIM2 = 4, ...., FRU_PIM8 = 10 */
  /* KV_PIM1 = 1, KV_PIM2 = 2, ...., KV_PIM8 = 8 */
  snprintf(path, LARGEST_DEVICE_NAME, tmp, fru - 2);
  if(read_device(path, &val)) {
    syslog(LOG_ERR, "%s cannot get value from %s", __func__, path);
    return;
  }
  if(val)
    _set_pim_sts_led(fru, FPGA_STS_CLR_BLUE);
  else
    _set_pim_sts_led(fru, FPGA_STS_CLR_YELLOW);

  return;
}

void
pal_sensor_assert_handle(uint8_t fru, uint8_t snr_num,
                                      float val, uint8_t thresh) {
  char crisel[128];
  char thresh_name[10];
  sensor_desc_t *snr_desc;

  switch (thresh) {
    case UNR_THRESH:
        sprintf(thresh_name, "UNR");
      break;
    case UCR_THRESH:
        sprintf(thresh_name, "UCR");
      break;
    case UNC_THRESH:
        sprintf(thresh_name, "UNCR");
      break;
    case LNR_THRESH:
        sprintf(thresh_name, "LNR");
      break;
    case LCR_THRESH:
        sprintf(thresh_name, "LCR");
      break;
    case LNC_THRESH:
        sprintf(thresh_name, "LNCR");
      break;
    default:
      syslog(LOG_WARNING, "pal_sensor_assert_handle: wrong thresh enum value");
      exit(-1);
  }

  switch (fru) {
    case FRU_SCM:
      switch(snr_num) {
        case SCM_SENSOR_INLET_REMOTE_TEMP:
          snr_desc = get_sensor_desc(fru, snr_num);
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - ASSERT,FRU:%u",
                          snr_desc->name, thresh_name, val, fru);
          break;
        default:
          return;
      }
      break;
    case FRU_SMB:
      switch(snr_num) {
        case SMB_SENSOR_TH3_DIE_TEMP1:
        case SMB_SENSOR_TH3_DIE_TEMP2:
          snr_desc = get_sensor_desc(fru, snr_num);
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - ASSERT,FRU:%u",
                          snr_desc->name, thresh_name, val, fru);
          break;
        default:
          return;
      }
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      switch(snr_num) {
        case PIM1_SENSOR_QSFP_TEMP:
        case PIM2_SENSOR_QSFP_TEMP:
        case PIM3_SENSOR_QSFP_TEMP:
        case PIM4_SENSOR_QSFP_TEMP:
        case PIM5_SENSOR_QSFP_TEMP:
        case PIM6_SENSOR_QSFP_TEMP:
        case PIM7_SENSOR_QSFP_TEMP:
        case PIM8_SENSOR_QSFP_TEMP:
          snr_desc = get_sensor_desc(fru, snr_num);
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - ASSERT,FRU:%u",
                          snr_desc->name, thresh_name, val, fru);
          break;
        default:
          return;
      }
      break;
    default:
      return;
  }
  pal_add_cri_sel(crisel);
  return;
}

void
pal_sensor_deassert_handle(uint8_t fru, uint8_t snr_num,
                                        float val, uint8_t thresh) {
  char crisel[256];
  char thresh_name[8];
  sensor_desc_t *snr_desc;
  uint8_t max_sensor_len = 128;
  char safe_sensor_name[max_sensor_len];


  switch (thresh) {
    case UNR_THRESH:
      sprintf(thresh_name, "UNR");
      break;
    case UCR_THRESH:
      sprintf(thresh_name, "UCR");
      break;
    case UNC_THRESH:
      sprintf(thresh_name, "UNCR");
      break;
    case LNR_THRESH:
      sprintf(thresh_name, "LNR");
      break;
    case LCR_THRESH:
      sprintf(thresh_name, "LCR");
      break;
    case LNC_THRESH:
      sprintf(thresh_name, "LNCR");
      break;
    default:
      syslog(LOG_WARNING,
             "pal_sensor_deassert_handle: wrong thresh enum value");
      return;
  }
  switch (fru) {
    case FRU_SCM:
      switch (snr_num) {
        case SCM_SENSOR_INLET_REMOTE_TEMP:
          snr_desc = get_sensor_desc(FRU_SCM, snr_num);
          strncpy(safe_sensor_name, snr_desc->name, max_sensor_len - 1);
          safe_sensor_name[max_sensor_len - 1] = '\0';
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - DEASSERT,FRU:%u",
                          safe_sensor_name, thresh_name, val, fru);
          break;
        default:
          return;
      }
    case FRU_SMB:
      switch(snr_num) {
        case SMB_SENSOR_TH3_DIE_TEMP1:
        case SMB_SENSOR_TH3_DIE_TEMP2:
          snr_desc = get_sensor_desc(fru, snr_num);
          strncpy(safe_sensor_name, snr_desc->name, max_sensor_len - 1);
          safe_sensor_name[max_sensor_len - 1] = '\0';
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - DEASSERT,FRU:%u",
                          safe_sensor_name, thresh_name, val, fru);
          break;
        default:
          return;
      }
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      switch(snr_num) {
        case PIM1_SENSOR_QSFP_TEMP:
        case PIM2_SENSOR_QSFP_TEMP:
        case PIM3_SENSOR_QSFP_TEMP:
        case PIM4_SENSOR_QSFP_TEMP:
        case PIM5_SENSOR_QSFP_TEMP:
        case PIM6_SENSOR_QSFP_TEMP:
        case PIM7_SENSOR_QSFP_TEMP:
        case PIM8_SENSOR_QSFP_TEMP:
          snr_desc = get_sensor_desc(fru, snr_num);
          snprintf(crisel, sizeof(crisel), "%s %s %.2fV - ASSERT,FRU:%u",
                          snr_desc->name, thresh_name, val, fru);
          break;
        default:
          return;
      }
      break;
    default:
      return;
  }
  pal_add_cri_sel(crisel);
  return;
}

int
pal_sensor_threshold_flag(uint8_t fru, uint8_t snr_num, uint16_t *flag) {

  switch(fru) {
    case FRU_SCM:
      if (snr_num == BIC_SENSOR_SOC_THERM_MARGIN)
        *flag = GETMASK(SENSOR_VALID) | GETMASK(UCR_THRESH);
      else if (snr_num == BIC_SENSOR_SOC_PACKAGE_PWR)
        *flag = GETMASK(SENSOR_VALID);
      else if (snr_num == BIC_SENSOR_SOC_TJMAX)
        *flag = GETMASK(SENSOR_VALID);
      break;
    default:
      break;
  }
  return 0;
}

static void
scm_sensor_poll_interval(uint8_t sensor_num, uint32_t *value) {

  switch(sensor_num) {
    case SCM_SENSOR_OUTLET_LOCAL_TEMP:
    case SCM_SENSOR_OUTLET_REMOTE_TEMP:
    case SCM_SENSOR_INLET_LOCAL_TEMP:
      *value = 30;
      break;
    case SCM_SENSOR_INLET_REMOTE_TEMP:
      *value = 2;
      break;
    case SCM_SENSOR_HSC_VOLT:
    case SCM_SENSOR_HSC_CURR:
    case SCM_SENSOR_HSC_POWER:
      *value = 30;
      break;
    default:
      *value = 30;
      break;
  }
}

static void
smb_sensor_poll_interval(uint8_t sensor_num, uint32_t *value) {

  switch(sensor_num) {
    case SMB_SENSOR_TH3_SERDES_TEMP:
    case SMB_SENSOR_TH3_CORE_TEMP:
    case SMB_SENSOR_TEMP1:
    case SMB_SENSOR_TEMP2:
    case SMB_SENSOR_TEMP3:
    case SMB_SENSOR_TEMP4:
    case SMB_SENSOR_TEMP5:
    case SMB_SENSOR_PDB_L_TEMP1:
    case SMB_SENSOR_PDB_L_TEMP2:
    case SMB_SENSOR_PDB_R_TEMP1:
    case SMB_SENSOR_PDB_R_TEMP2:
    case SMB_SENSOR_FCM_T_TEMP1:
    case SMB_SENSOR_FCM_T_TEMP2:
    case SMB_SENSOR_FCM_B_TEMP1:
    case SMB_SENSOR_FCM_B_TEMP2:
      *value = 30;
      break;
    case SMB_SENSOR_TH3_DIE_TEMP1:
    case SMB_SENSOR_TH3_DIE_TEMP2:
      *value = 2;
      break;
    case SMB_SENSOR_1220_VMON1:
    case SMB_SENSOR_1220_VMON2:
    case SMB_SENSOR_1220_VMON3:
    case SMB_SENSOR_1220_VMON4:
    case SMB_SENSOR_1220_VMON5:
    case SMB_SENSOR_1220_VMON6:
    case SMB_SENSOR_1220_VMON7:
    case SMB_SENSOR_1220_VMON8:
    case SMB_SENSOR_1220_VMON9:
    case SMB_SENSOR_1220_VMON10:
    case SMB_SENSOR_1220_VMON11:
    case SMB_SENSOR_1220_VMON12:
    case SMB_SENSOR_1220_VCCA:
    case SMB_SENSOR_1220_VCCINP:
    case SMB_SENSOR_TH3_SERDES_VOLT:
    case SMB_SENSOR_TH3_CORE_VOLT:
    case SMB_SENSOR_FCM_T_HSC_VOLT:
    case SMB_SENSOR_FCM_B_HSC_VOLT:
    case SMB_SENSOR_TH3_SERDES_CURR:
    case SMB_SENSOR_TH3_CORE_CURR:
    case SMB_SENSOR_FCM_T_HSC_CURR:
    case SMB_SENSOR_FCM_B_HSC_CURR:
    case SMB_SENSOR_FCM_T_HSC_POWER:
    case SMB_SENSOR_FCM_B_HSC_POWER:
      *value = 30;
      break;
    case SMB_SENSOR_FAN1_FRONT_TACH:
    case SMB_SENSOR_FAN1_REAR_TACH:
    case SMB_SENSOR_FAN2_FRONT_TACH:
    case SMB_SENSOR_FAN2_REAR_TACH:
    case SMB_SENSOR_FAN3_FRONT_TACH:
    case SMB_SENSOR_FAN3_REAR_TACH:
    case SMB_SENSOR_FAN4_FRONT_TACH:
    case SMB_SENSOR_FAN4_REAR_TACH:
    case SMB_SENSOR_FAN5_FRONT_TACH:
    case SMB_SENSOR_FAN5_REAR_TACH:
    case SMB_SENSOR_FAN6_FRONT_TACH:
    case SMB_SENSOR_FAN6_REAR_TACH:
    case SMB_SENSOR_FAN7_FRONT_TACH:
    case SMB_SENSOR_FAN7_REAR_TACH:
    case SMB_SENSOR_FAN8_FRONT_TACH:
    case SMB_SENSOR_FAN8_REAR_TACH:
      *value = 2;
      break;
    default:
      *value = 10;
      break;
  }
}

static void
pim_sensor_poll_interval(uint8_t sensor_num, uint32_t *value) {

  switch(sensor_num) {
    case PIM1_SENSOR_TEMP1:
    case PIM1_SENSOR_TEMP2:
    case PIM1_SENSOR_HSC_VOLT:
    case PIM1_SENSOR_HSC_CURR:
    case PIM1_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM1_SENSOR_34461_VOLT1:
    case PIM1_SENSOR_34461_VOLT2:
    case PIM1_SENSOR_34461_VOLT3:
    case PIM1_SENSOR_34461_VOLT4:
    case PIM1_SENSOR_34461_VOLT5:
    case PIM1_SENSOR_34461_VOLT6:
    case PIM1_SENSOR_34461_VOLT7:
    case PIM1_SENSOR_34461_VOLT8:
    case PIM1_SENSOR_34461_VOLT9:
    case PIM1_SENSOR_34461_VOLT10:
    case PIM1_SENSOR_34461_VOLT11:
    case PIM1_SENSOR_34461_VOLT12:
    case PIM1_SENSOR_34461_VOLT13:
    case PIM1_SENSOR_34461_VOLT14:
    case PIM1_SENSOR_34461_VOLT15:
    case PIM1_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM2_SENSOR_TEMP1:
    case PIM2_SENSOR_TEMP2:
    case PIM2_SENSOR_HSC_VOLT:
    case PIM2_SENSOR_HSC_CURR:
    case PIM2_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM2_SENSOR_34461_VOLT1:
    case PIM2_SENSOR_34461_VOLT2:
    case PIM2_SENSOR_34461_VOLT3:
    case PIM2_SENSOR_34461_VOLT4:
    case PIM2_SENSOR_34461_VOLT5:
    case PIM2_SENSOR_34461_VOLT6:
    case PIM2_SENSOR_34461_VOLT7:
    case PIM2_SENSOR_34461_VOLT8:
    case PIM2_SENSOR_34461_VOLT9:
    case PIM2_SENSOR_34461_VOLT10:
    case PIM2_SENSOR_34461_VOLT11:
    case PIM2_SENSOR_34461_VOLT12:
    case PIM2_SENSOR_34461_VOLT13:
    case PIM2_SENSOR_34461_VOLT14:
    case PIM2_SENSOR_34461_VOLT15:
    case PIM2_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM3_SENSOR_TEMP1:
    case PIM3_SENSOR_TEMP2:
    case PIM3_SENSOR_HSC_VOLT:
    case PIM3_SENSOR_HSC_CURR:
    case PIM3_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM3_SENSOR_34461_VOLT1:
    case PIM3_SENSOR_34461_VOLT2:
    case PIM3_SENSOR_34461_VOLT3:
    case PIM3_SENSOR_34461_VOLT4:
    case PIM3_SENSOR_34461_VOLT5:
    case PIM3_SENSOR_34461_VOLT6:
    case PIM3_SENSOR_34461_VOLT7:
    case PIM3_SENSOR_34461_VOLT8:
    case PIM3_SENSOR_34461_VOLT9:
    case PIM3_SENSOR_34461_VOLT10:
    case PIM3_SENSOR_34461_VOLT11:
    case PIM3_SENSOR_34461_VOLT12:
    case PIM3_SENSOR_34461_VOLT13:
    case PIM3_SENSOR_34461_VOLT14:
    case PIM3_SENSOR_34461_VOLT15:
    case PIM3_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM4_SENSOR_TEMP1:
    case PIM4_SENSOR_TEMP2:
    case PIM4_SENSOR_HSC_VOLT:
    case PIM4_SENSOR_HSC_CURR:
    case PIM4_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM4_SENSOR_34461_VOLT1:
    case PIM4_SENSOR_34461_VOLT2:
    case PIM4_SENSOR_34461_VOLT3:
    case PIM4_SENSOR_34461_VOLT4:
    case PIM4_SENSOR_34461_VOLT5:
    case PIM4_SENSOR_34461_VOLT6:
    case PIM4_SENSOR_34461_VOLT7:
    case PIM4_SENSOR_34461_VOLT8:
    case PIM4_SENSOR_34461_VOLT9:
    case PIM4_SENSOR_34461_VOLT10:
    case PIM4_SENSOR_34461_VOLT11:
    case PIM4_SENSOR_34461_VOLT12:
    case PIM4_SENSOR_34461_VOLT13:
    case PIM4_SENSOR_34461_VOLT14:
    case PIM4_SENSOR_34461_VOLT15:
    case PIM4_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM5_SENSOR_TEMP1:
    case PIM5_SENSOR_TEMP2:
    case PIM5_SENSOR_HSC_VOLT:
    case PIM5_SENSOR_HSC_CURR:
    case PIM5_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM5_SENSOR_34461_VOLT1:
    case PIM5_SENSOR_34461_VOLT2:
    case PIM5_SENSOR_34461_VOLT3:
    case PIM5_SENSOR_34461_VOLT4:
    case PIM5_SENSOR_34461_VOLT5:
    case PIM5_SENSOR_34461_VOLT6:
    case PIM5_SENSOR_34461_VOLT7:
    case PIM5_SENSOR_34461_VOLT8:
    case PIM5_SENSOR_34461_VOLT9:
    case PIM5_SENSOR_34461_VOLT10:
    case PIM5_SENSOR_34461_VOLT11:
    case PIM5_SENSOR_34461_VOLT12:
    case PIM5_SENSOR_34461_VOLT13:
    case PIM5_SENSOR_34461_VOLT14:
    case PIM5_SENSOR_34461_VOLT15:
    case PIM5_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM6_SENSOR_TEMP1:
    case PIM6_SENSOR_TEMP2:
    case PIM6_SENSOR_HSC_VOLT:
    case PIM6_SENSOR_HSC_CURR:
    case PIM6_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM6_SENSOR_34461_VOLT1:
    case PIM6_SENSOR_34461_VOLT2:
    case PIM6_SENSOR_34461_VOLT3:
    case PIM6_SENSOR_34461_VOLT4:
    case PIM6_SENSOR_34461_VOLT5:
    case PIM6_SENSOR_34461_VOLT6:
    case PIM6_SENSOR_34461_VOLT7:
    case PIM6_SENSOR_34461_VOLT8:
    case PIM6_SENSOR_34461_VOLT9:
    case PIM6_SENSOR_34461_VOLT10:
    case PIM6_SENSOR_34461_VOLT11:
    case PIM6_SENSOR_34461_VOLT12:
    case PIM6_SENSOR_34461_VOLT13:
    case PIM6_SENSOR_34461_VOLT14:
    case PIM6_SENSOR_34461_VOLT15:
    case PIM6_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM7_SENSOR_TEMP1:
    case PIM7_SENSOR_TEMP2:
    case PIM7_SENSOR_HSC_VOLT:
    case PIM7_SENSOR_HSC_CURR:
    case PIM7_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM7_SENSOR_34461_VOLT1:
    case PIM7_SENSOR_34461_VOLT2:
    case PIM7_SENSOR_34461_VOLT3:
    case PIM7_SENSOR_34461_VOLT4:
    case PIM7_SENSOR_34461_VOLT5:
    case PIM7_SENSOR_34461_VOLT6:
    case PIM7_SENSOR_34461_VOLT7:
    case PIM7_SENSOR_34461_VOLT8:
    case PIM7_SENSOR_34461_VOLT9:
    case PIM7_SENSOR_34461_VOLT10:
    case PIM7_SENSOR_34461_VOLT11:
    case PIM7_SENSOR_34461_VOLT12:
    case PIM7_SENSOR_34461_VOLT13:
    case PIM7_SENSOR_34461_VOLT14:
    case PIM7_SENSOR_34461_VOLT15:
    case PIM7_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM8_SENSOR_TEMP1:
    case PIM8_SENSOR_TEMP2:
    case PIM8_SENSOR_HSC_VOLT:
    case PIM8_SENSOR_HSC_CURR:
    case PIM8_SENSOR_HSC_POWER:
      *value = 30;
      break;
    case PIM8_SENSOR_34461_VOLT1:
    case PIM8_SENSOR_34461_VOLT2:
    case PIM8_SENSOR_34461_VOLT3:
    case PIM8_SENSOR_34461_VOLT4:
    case PIM8_SENSOR_34461_VOLT5:
    case PIM8_SENSOR_34461_VOLT6:
    case PIM8_SENSOR_34461_VOLT7:
    case PIM8_SENSOR_34461_VOLT8:
    case PIM8_SENSOR_34461_VOLT9:
    case PIM8_SENSOR_34461_VOLT10:
    case PIM8_SENSOR_34461_VOLT11:
    case PIM8_SENSOR_34461_VOLT12:
    case PIM8_SENSOR_34461_VOLT13:
    case PIM8_SENSOR_34461_VOLT14:
    case PIM8_SENSOR_34461_VOLT15:
    case PIM8_SENSOR_34461_VOLT16:
      *value = 60;
      break;
    case PIM1_SENSOR_QSFP_TEMP:
    case PIM2_SENSOR_QSFP_TEMP:
    case PIM3_SENSOR_QSFP_TEMP:
    case PIM4_SENSOR_QSFP_TEMP:
    case PIM5_SENSOR_QSFP_TEMP:
    case PIM6_SENSOR_QSFP_TEMP:
    case PIM7_SENSOR_QSFP_TEMP:
    case PIM8_SENSOR_QSFP_TEMP:
      *value = 2;
      break;
    default:
      *value = 10;
      break;
  }
}

static void
psu_sensor_poll_interval(uint8_t sensor_num, uint32_t *value) {

  switch(sensor_num) {
    case PSU1_SENSOR_IN_VOLT:
    case PSU1_SENSOR_12V_VOLT:
    case PSU1_SENSOR_STBY_VOLT:
    case PSU1_SENSOR_IN_CURR:
    case PSU1_SENSOR_12V_CURR:
    case PSU1_SENSOR_STBY_CURR:
    case PSU1_SENSOR_IN_POWER:
    case PSU1_SENSOR_12V_POWER:
    case PSU1_SENSOR_STBY_POWER:
    case PSU1_SENSOR_FAN_TACH:
    case PSU1_SENSOR_TEMP1:
    case PSU1_SENSOR_TEMP2:
    case PSU1_SENSOR_TEMP3:
    case PSU2_SENSOR_IN_VOLT:
    case PSU2_SENSOR_12V_VOLT:
    case PSU2_SENSOR_STBY_VOLT:
    case PSU2_SENSOR_IN_CURR:
    case PSU2_SENSOR_12V_CURR:
    case PSU2_SENSOR_STBY_CURR:
    case PSU2_SENSOR_IN_POWER:
    case PSU2_SENSOR_12V_POWER:
    case PSU2_SENSOR_STBY_POWER:
    case PSU2_SENSOR_FAN_TACH:
    case PSU2_SENSOR_TEMP1:
    case PSU2_SENSOR_TEMP2:
    case PSU2_SENSOR_TEMP3:
    case PSU3_SENSOR_IN_VOLT:
    case PSU3_SENSOR_12V_VOLT:
    case PSU3_SENSOR_STBY_VOLT:
    case PSU3_SENSOR_IN_CURR:
    case PSU3_SENSOR_12V_CURR:
    case PSU3_SENSOR_STBY_CURR:
    case PSU3_SENSOR_IN_POWER:
    case PSU3_SENSOR_12V_POWER:
    case PSU3_SENSOR_STBY_POWER:
    case PSU3_SENSOR_FAN_TACH:
    case PSU3_SENSOR_TEMP1:
    case PSU3_SENSOR_TEMP2:
    case PSU3_SENSOR_TEMP3:
    case PSU4_SENSOR_IN_VOLT:
    case PSU4_SENSOR_12V_VOLT:
    case PSU4_SENSOR_STBY_VOLT:
    case PSU4_SENSOR_IN_CURR:
    case PSU4_SENSOR_12V_CURR:
    case PSU4_SENSOR_STBY_CURR:
    case PSU4_SENSOR_IN_POWER:
    case PSU4_SENSOR_12V_POWER:
    case PSU4_SENSOR_STBY_POWER:
    case PSU4_SENSOR_FAN_TACH:
    case PSU4_SENSOR_TEMP1:
    case PSU4_SENSOR_TEMP2:
    case PSU4_SENSOR_TEMP3:
      *value = 30;
      break;
    default:
      *value = 10;
      break;
  }
}

int
pal_get_sensor_poll_interval(uint8_t fru, uint8_t sensor_num, uint32_t *value) {

  switch(fru) {
    case FRU_SCM:
      scm_sensor_poll_interval(sensor_num, value);
      break;
    case FRU_SMB:
      smb_sensor_poll_interval(sensor_num, value);
      break;
    case FRU_PIM1:
    case FRU_PIM2:
    case FRU_PIM3:
    case FRU_PIM4:
    case FRU_PIM5:
    case FRU_PIM6:
    case FRU_PIM7:
    case FRU_PIM8:
      pim_sensor_poll_interval(sensor_num, value);
      break;
    case FRU_PSU1:
    case FRU_PSU2:
    case FRU_PSU3:
    case FRU_PSU4:
      psu_sensor_poll_interval(sensor_num, value);
      break;
    default:
      *value = 2;
      break;
  }
  return 0;
}

void
pal_get_chassis_status(uint8_t slot, uint8_t *req_data, uint8_t *res_data, uint8_t *res_len) {

  char key[MAX_KEY_LEN];
  char buff[MAX_VALUE_LEN];
  int policy = 3;
  uint8_t status, ret;
  unsigned char *data = res_data;

  /* Platform Power Policy */
  sprintf(key, "%s", "server_por_cfg");
  if (pal_get_key_value(key, buff) == 0)
  {
    if (!memcmp(buff, "off", strlen("off")))
      policy = 0;
    else if (!memcmp(buff, "lps", strlen("lps")))
      policy = 1;
    else if (!memcmp(buff, "on", strlen("on")))
      policy = 2;
    else
      policy = 3;
  }

  /* Current Power State */
  ret = pal_get_server_power(FRU_SCM, &status);
  if (ret >= 0) {
    *data++ = status | (policy << 5);
  } else {
    /* load default */
    syslog(LOG_WARNING, "ipmid: pal_get_server_power failed for server\n");
    *data++ = 0x00 | (policy << 5);
  }
  *data++ = 0x00;   /* Last Power Event */
  *data++ = 0x40;   /* Misc. Chassis Status */
  *data++ = 0x00;   /* Front Panel Button Disable */
  *res_len = data - res_data;
}

uint8_t
pal_set_power_restore_policy(uint8_t slot, uint8_t *pwr_policy, uint8_t *res_data) {

    uint8_t completion_code;
    char key[MAX_KEY_LEN];
    unsigned char policy = *pwr_policy & 0x07;  /* Power restore policy */

  completion_code = CC_SUCCESS;   /* Fill response with default values */
    sprintf(key, "%s", "server_por_cfg");
    switch (policy)
    {
      case 0:
        if (pal_set_key_value(key, "off") != 0)
          completion_code = CC_UNSPECIFIED_ERROR;
        break;
      case 1:
        if (pal_set_key_value(key, "lps") != 0)
          completion_code = CC_UNSPECIFIED_ERROR;
        break;
      case 2:
        if (pal_set_key_value(key, "on") != 0)
          completion_code = CC_UNSPECIFIED_ERROR;
        break;
      case 3:
        /* no change (just get present policy support) */
        break;
      default:
          completion_code = CC_PARAM_OUT_OF_RANGE;
        break;
    }
    return completion_code;
}

void *
generate_dump(void *arg) {

  uint8_t fru = *(uint8_t *) arg;
  char cmd[128];
  char fname[128];
  char fruname[16];

  // Usually the pthread cancel state are enable by default but
  // here we explicitly would like to enable them
  pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);
  pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);

  pal_get_fru_name(fru, fruname);//scm

  memset(fname, 0, sizeof(fname));
  snprintf(fname, 128, "/var/run/autodump%d.pid", fru);
  if (access(fname, F_OK) == 0) {
    memset(cmd, 0, sizeof(cmd));
    sprintf(cmd,"rm %s",fname);
    system(cmd);
  }

  // Execute automatic crashdump
  memset(cmd, 0, 128);
  sprintf(cmd, "%s %s", CRASHDUMP_BIN, fruname);
  system(cmd);

  syslog(LOG_CRIT, "Crashdump for FRU: %d is generated.", fru);

  t_dump[fru-1].is_running = 0;
  return 0;
}

static int
pal_store_crashdump(uint8_t fru) {

  int ret;
  char cmd[100];

  // Check if the crashdump script exist
  if (access(CRASHDUMP_BIN, F_OK) == -1) {
    syslog(LOG_CRIT, "Crashdump for FRU: %d failed : "
        "auto crashdump binary is not preset", fru);
    return 0;
  }

  // Check if a crashdump for that fru is already running.
  // If yes, kill that thread and start a new one.
  if (t_dump[fru-1].is_running) {
    ret = pthread_cancel(t_dump[fru-1].pt);
    if (ret == ESRCH) {
      syslog(LOG_INFO,
             "pal_store_crashdump: No Crashdump pthread exists");
    } else {
      pthread_join(t_dump[fru-1].pt, NULL);
      sprintf(cmd,
              "ps | grep '{dump.sh}' | grep 'scm' "
              "| awk '{print $1}'| xargs kill");
      system(cmd);
      sprintf(cmd,
              "ps | grep 'bic-util' | grep 'scm' "
              "| awk '{print $1}'| xargs kill");
      system(cmd);
#ifdef DEBUG
      syslog(LOG_INFO, "pal_store_crashdump:"
                       " Previous crashdump thread is cancelled");
#endif
    }
  }

  // Start a thread to generate the crashdump
  t_dump[fru-1].fru = fru;
  if (pthread_create(&(t_dump[fru-1].pt), NULL, generate_dump,
      (void*) &t_dump[fru-1].fru) < 0) {
    syslog(LOG_WARNING, "pal_store_crashdump: pthread_create for"
        " FRU %d failed\n", fru);
    return -1;
  }

  t_dump[fru-1].is_running = 1;

  syslog(LOG_INFO, "Crashdump for FRU: %d is being generated.", fru);

  return 0;
}

int
pal_sel_handler(uint8_t fru, uint8_t snr_num, uint8_t *event_data) {

  char key[MAX_KEY_LEN] = {0};
  char cvalue[MAX_VALUE_LEN] = {0};
  static int assert_cnt[MINIPACK_MAX_NUM_SLOTS] = {0};
  switch(fru) {
    case FRU_SCM:
      switch(snr_num) {
        case CATERR_B:
          pal_store_crashdump(fru);
          break;

        case 0x00:  // don't care sensor number 00h
          return 0;
      }
      sprintf(key, "server_sel_error");

      if ((event_data[2] & 0x80) == 0) {  // 0: Assertion,  1: Deassertion
         assert_cnt[fru-1]++;
      } else {
        if (--assert_cnt[fru-1] < 0)
           assert_cnt[fru-1] = 0;
      }
      sprintf(cvalue, "%s", (assert_cnt[fru-1] > 0) ? "0" : "1");
      break;

    default:
      return -1;
  }

  /* Write the value "0" which means FRU_STATUS_BAD */
  return pal_set_key_value(key, cvalue);

}

void
init_led(void)
{
  int dev, ret;
  dev = open("/dev/i2c-50", O_RDWR);
  if(dev < 0) {
    syslog(LOG_ERR, "%s: open() failed\n", __func__);
    return;
  }

  ret = ioctl(dev, I2C_SLAVE, I2C_ADDR_SIM_LED);
  if(ret < 0) {
    syslog(LOG_ERR, "%s: ioctl() assigned i2c addr failed\n", __func__);
    close(dev);
    return;
  }

  i2c_smbus_write_byte_data(dev, 0x06, 0x00);
  i2c_smbus_write_byte_data(dev, 0x07, 0x00);
  close(dev);

  return;
}

int
set_sled(int brd_rev, uint8_t color, int led_name)
{
  int dev, ret;
  uint8_t io0_reg = 0x02, io1_reg = 0x03;
  uint8_t clr_val, val_io0, val_io1;
  dev = open("/dev/i2c-50", O_RDWR);
  if(dev < 0) {
    syslog(LOG_ERR, "%s: open() failed\n", __func__);
    return -1;
  }

  ret = ioctl(dev, I2C_SLAVE, I2C_ADDR_SIM_LED);
  if(ret < 0) {
    syslog(LOG_ERR, "%s: ioctl() assigned i2c addr failed\n", __func__);
    close(dev);
    return -1;
  }
  val_io0 = i2c_smbus_read_byte_data(dev, 0x02);
  if(val_io0 < 0) {
    close(dev);
    syslog(LOG_ERR, "%s: i2c_smbus_read_byte_data failed\n", __func__);
    return -1;
  }

  val_io1 = i2c_smbus_read_byte_data(dev, 0x03);
  if(val_io1 < 0) {
    close(dev);
    syslog(LOG_ERR, "%s: i2c_smbus_read_byte_data failed\n", __func__);
    return -1;
  }

  clr_val = color;

  if(brd_rev == 0 || brd_rev == 4) {
    if(led_name == SLED_SMB || led_name == SLED_PSU) {
      clr_val = clr_val << 3;
      val_io0 = (val_io0 & 0x7) | clr_val;
      val_io1 = (val_io1 & 0x7) | clr_val;
    }
    else if(led_name == SLED_SYS || led_name == SLED_FAN) {
      val_io0 = (val_io0 & 0x38) | clr_val;
      val_io1 = (val_io1 & 0x38) | clr_val;
    }
    else
      syslog(LOG_WARNING, "%s: unknown led name\n", __func__);

    if(led_name == SLED_PSU || led_name == SLED_FAN) {
      i2c_smbus_write_byte_data(dev, io0_reg, val_io0);
    } else {
      i2c_smbus_write_byte_data(dev, io1_reg, val_io1);
    }
  }
  else {
    if(led_name == SLED_FAN || led_name == SLED_SMB) {
      clr_val = clr_val << 3;
      val_io0 = (val_io0 & 0x7) | clr_val;
      val_io1 = (val_io1 & 0x7) | clr_val;
    }
    else if(led_name == SLED_SYS || led_name == SLED_PSU) {
      val_io0 = (val_io0 & 0x38) | clr_val;
      val_io1 = (val_io1 & 0x38) | clr_val;
    }
    else {
      syslog(LOG_WARNING, "%s: unknown led name\n", __func__);
    }

    if(led_name == SLED_SYS || led_name == SLED_FAN) {
      i2c_smbus_write_byte_data(dev, io0_reg, val_io0);
    } else {
      i2c_smbus_write_byte_data(dev, io1_reg, val_io1);
    }
  }

  close(dev);
  return 0;
}


static void
upgrade_led_blink(int brd_rev,
                uint8_t sys_ug, uint8_t fan_ug, uint8_t psu_ug, uint8_t smb_ug)
{
  static uint8_t sys_alter = 0, fan_alter = 0, psu_alter = 0, smb_alter = 0;

  if(sys_ug) {
    if(sys_alter == 0) {
      set_sled(brd_rev, SLED_CLR_BLUE, SLED_SYS);
      sys_alter = 1;
    } else {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SYS);
      sys_alter = 0;
    }
  }
  if(fan_ug) {
    if(fan_alter == 0) {
      set_sled(brd_rev, SLED_CLR_BLUE, SLED_FAN);
      fan_alter = 1;
    } else {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_FAN);
      fan_alter = 0;
    }
  }
  if(psu_ug) {
    if(psu_alter == 0) {
      set_sled(brd_rev, SLED_CLR_BLUE, SLED_PSU);
      psu_alter = 1;
    } else {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      psu_alter = 0;
    }
  }
  if(smb_ug) {
    if(smb_alter == 0) {
      set_sled(brd_rev, SLED_CLR_BLUE, SLED_SMB);
      smb_alter = 1;
    } else {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SMB);
      smb_alter = 0;
    }
  }
}

int
pal_mon_fw_upgrade
(int brd_rev, uint8_t *sys_ug, uint8_t *fan_ug,
              uint8_t *psu_ug, uint8_t *smb_ug)
{
  char cmd[5];
  FILE *fp;
  int ret=-1;
  char *buf_ptr;
  int buf_size = 1000;
  int str_size = 200;
  int tmp_size;
  char str[200];
  snprintf(cmd, sizeof(cmd), "ps w");
  fp = popen(cmd, "r");
  if(NULL == fp)
     return -1;

  buf_ptr = (char *)malloc(buf_size * sizeof(char) + sizeof(char));
  memset(buf_ptr, 0, sizeof(char));
  tmp_size = str_size;
  while(fgets(str, str_size, fp) != NULL) {
    tmp_size = tmp_size + str_size;
    if(tmp_size + str_size >= buf_size) {
      buf_ptr = realloc(buf_ptr, sizeof(char) * buf_size * 2 + sizeof(char));
      buf_size *= 2;
    }
    if(!buf_ptr) {
      syslog(LOG_ERR,
             "%s realloc() fail, please check memory remaining", __func__);
      goto free_buf;
    }
    strncat(buf_ptr, str, str_size);
  }

  //check whether sys led need to blink
  *sys_ug = strstr(buf_ptr, "write spi2") != NULL ? 1 : 0;
  if(*sys_ug) goto fan_state;

  *sys_ug = strstr(buf_ptr, "write spi1 BACKUP_BIOS") != NULL ? 1 : 0;
  if(*sys_ug) goto fan_state;

  *sys_ug = (strstr(buf_ptr, "scmcpld_update") != NULL) ? 1 : 0;
  if(*sys_ug) goto fan_state;

  *sys_ug = (strstr(buf_ptr, "pimcpld_update") != NULL) ? 1 : 0;
  if(*sys_ug) goto fan_state;

  *sys_ug = (strstr(buf_ptr, "fw-util") != NULL) ?
          ((strstr(buf_ptr, "--update") != NULL) ? 1 : 0) : 0;
  if(*sys_ug) goto fan_state;

  //check whether fan led need to blink
fan_state:
  *fan_ug = (strstr(buf_ptr, "fcmcpld_update") != NULL) ? 1 : 0;

  //check whether fan led need to blink
  *psu_ug = (strstr(buf_ptr, "psu-util") != NULL) ?
          ((strstr(buf_ptr, "--update") != NULL) ? 1 : 0) : 0;

  //check whether smb led need to blink
  *smb_ug = (strstr(buf_ptr, "smbcpld_update") != NULL) ? 1 : 0;
  if(*smb_ug) goto close_fp;

  *smb_ug = (strstr(buf_ptr, "pdbcpld_update") != NULL) ? 1 : 0;
  if(*smb_ug) goto close_fp;

  *smb_ug = (strstr(buf_ptr, "flashcp") != NULL) ? 1 : 0;
  if(*smb_ug) goto close_fp;

  *smb_ug = strstr(buf_ptr, "write spi1 IOB_FPGA_FLASH") != NULL ? 1 : 0;
  if(*smb_ug) goto close_fp;

  *smb_ug = strstr(buf_ptr, "write spi1 TH3_FLASH") != NULL ? 1 : 0;
  if(*smb_ug) goto close_fp;

  *smb_ug = strstr(buf_ptr, "write spi1 BCM5396_EE") != NULL ? 1 : 0;
  if(*smb_ug) goto close_fp;

close_fp:
  ret = pclose(fp);
  if(-1 == ret)
     syslog(LOG_ERR, "%s pclose() fail ", __func__);

  upgrade_led_blink(brd_rev, *sys_ug, *fan_ug, *psu_ug, *smb_ug);

free_buf:
  free(buf_ptr);
  return 0;
}



void set_sys_led(int brd_rev)
{
  uint8_t fru;
  uint8_t ret = 0;
  uint8_t prsnt = 0;
  ret = pal_is_fru_prsnt(FRU_SCM, &prsnt);
  if (ret) {
    set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SYS);
    return;
  }
  if (!prsnt) {
    set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SYS);
    return;
  }

  for(fru = FRU_PIM1; fru <= FRU_PIM8; fru++){
    ret = pal_is_fru_prsnt(fru, &prsnt);
    if (ret) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SYS);
      return;
    }
    if (!prsnt) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_SYS);
      return;
    }
  }
  set_sled(brd_rev, SLED_CLR_BLUE, SLED_SYS);
  return;
}

void set_fan_led(int brd_rev)
{
  int i, val;
  uint8_t fan_num = 16;//rear:8 && front:8
  char path[LARGEST_DEVICE_NAME + 1];
  int sensor_num[] = {42, 43, 44, 45, 46, 47, 48, 49,
                             50, 51, 52, 53, 54, 55, 56, 57};

  for(i = 0; i < fan_num; i++) {
    snprintf(path, LARGEST_DEVICE_NAME, SENSORD_FILE_SMB, sensor_num[i]);
    if(read_device(path, &val)) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_FAN);
      return;
    }
    if(val <= 800) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_FAN);
      return;
    }
  }
  set_sled(brd_rev, SLED_CLR_BLUE, SLED_FAN);
  return;
}

void set_psu_led(int brd_rev)
{
  int i, val_in, val_out12;
  float val_out3;
  int vin_min = 92;
  int vin_max = 310;
  int vout_12_min = 11;
  int vout_12_max = 13;
  float vout_3_min = 3.00;
  float vout_3_max = 3.60;
  uint8_t psu_num = 4;
  uint8_t prsnt;
  int sensor_num[] = {1, 14, 27, 40};
  char path[LARGEST_DEVICE_NAME + 1];

  for(i = FRU_PSU1; i <= FRU_PSU4; i++) {
    pal_is_fru_prsnt(i, &prsnt);
    if(!prsnt) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }
  }

  for(i = 0; i < psu_num; i++) {

    snprintf(path, LARGEST_DEVICE_NAME, SENSORD_FILE_PSU, i+1, sensor_num[i]);
    if(read_device(path, &val_in)) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

    if(val_in > vin_max || val_in < vin_min) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

    snprintf(path, LARGEST_DEVICE_NAME, SENSORD_FILE_PSU,
             i+1, sensor_num[i] + 1);
    if(read_device(path, &val_out12)) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

    if(val_out12 > vout_12_max || val_out12 < vout_12_min) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

    snprintf(path, LARGEST_DEVICE_NAME, SENSORD_FILE_PSU,
             i+1, sensor_num[i] + 2);
    if(read_device_float(path, &val_out3)) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

    if(val_out3 > vout_3_max || val_out3 < vout_3_min) {
      set_sled(brd_rev, SLED_CLR_YELLOW, SLED_PSU);
      return;
    }

  }

  set_sled(brd_rev, SLED_CLR_BLUE, SLED_PSU);

  return;
}

void set_smb_led(int brd_rev)
{
  set_sled(brd_rev, SLED_CLR_BLUE, SLED_SMB);
  return;
}

int
pal_light_scm_led(uint8_t led_color)
{
  int ret;
  char *val;

  if(led_color == SCM_LED_BLUE)
    val = "0";
  else
    val = "1";
  ret = write_device(SCM_SYS_LED_COLOR, val);
  if (ret) {
#ifdef DEBUG
  syslog(LOG_WARNING, "write_device failed for %s\n", SCM_SYS_LED_COLOR);
#endif
    return -1;
  }

  return 0;
}

int
pal_set_def_key_value(void) {

  int i, ret;
  char path[LARGEST_DEVICE_NAME + 1];

  for (i = 0; strcmp(key_list[i], LAST_KEY) != 0; i++) {
    snprintf(path, LARGEST_DEVICE_NAME, KV_PATH, key_list[i]);
    if ((ret = kv_set(key_list[i], def_val_list[i],
	                  0, KV_FPERSIST | KV_FCREATE)) < 0) {
#ifdef DEBUG
      syslog(LOG_WARNING, "pal_set_def_key_value: kv_set failed. %d", ret);
#endif
    }
  }
  return 0;
 }

int
pal_init_sensor_check(uint8_t fru, uint8_t snr_num, void *snr) {
  pal_set_def_key_value();
  psu_init_acok_key(fru);
  return 0;
}

int
pal_get_fru_health(uint8_t fru, uint8_t *value) {

  char cvalue[MAX_VALUE_LEN] = {0};
  char key[MAX_KEY_LEN] = {0};
  int ret;

  switch(fru) {
    case FRU_SCM:
      sprintf(key, "scm_sensor_health");
      break;
    case FRU_SMB:
      sprintf(key, "smb_sensor_health");
      break;
	case FRU_PIM1:
      sprintf(key, "pim1_sensor_health");
      break;
	case FRU_PIM2:
      sprintf(key, "pim2_sensor_health");
      break;
	case FRU_PIM3:
      sprintf(key, "pim3_sensor_health");
      break;
	case FRU_PIM4:
      sprintf(key, "pim4_sensor_health");
      break;
	case FRU_PIM5:
      sprintf(key, "pim5_sensor_health");
      break;
	case FRU_PIM6:
      sprintf(key, "pim6_sensor_health");
      break;
	case FRU_PIM7:
      sprintf(key, "pim7_sensor_health");
      break;
	case FRU_PIM8:
      sprintf(key, "pim8_sensor_health");
      break;
	case FRU_PSU1:
      sprintf(key, "psu1_sensor_health");
      break;
	case FRU_PSU2:
      sprintf(key, "psu2_sensor_health");
      break;
	case FRU_PSU3:
      sprintf(key, "psu3_sensor_health");
      break;
	case FRU_PSU4:
      sprintf(key, "psu4_sensor_health");
      break;

    default:
      return -1;
  }

  ret = pal_get_key_value(key, cvalue);
  if (ret) {
    return ret;
  }

  *value = atoi(cvalue);

  *value = *value & atoi(cvalue);
  return 0;
}

int
pal_set_sensor_health(uint8_t fru, uint8_t value) {

  char key[MAX_KEY_LEN] = {0};
  char cvalue[MAX_VALUE_LEN] = {0};

  switch(fru) {
    case FRU_SCM:
      sprintf(key, "scm_sensor_health");
      break;
    case FRU_SMB:
      sprintf(key, "smb_sensor_health");
      break;
	case FRU_PIM1:
      sprintf(key, "pim1_sensor_health");
      break;
	case FRU_PIM2:
      sprintf(key, "pim2_sensor_health");
      break;
	case FRU_PIM3:
      sprintf(key, "pim3_sensor_health");
      break;
	case FRU_PIM4:
      sprintf(key, "pim4_sensor_health");
      break;
	case FRU_PIM5:
      sprintf(key, "pim5_sensor_health");
      break;
	case FRU_PIM6:
      sprintf(key, "pim6_sensor_health");
      break;
	case FRU_PIM7:
      sprintf(key, "pim7_sensor_health");
      break;
	case FRU_PIM8:
      sprintf(key, "pim8_sensor_health");
      break;
	case FRU_PSU1:
      sprintf(key, "psu1_sensor_health");
      break;
	case FRU_PSU2:
      sprintf(key, "psu2_sensor_health");
      break;
	case FRU_PSU3:
      sprintf(key, "psu3_sensor_health");
      break;
	case FRU_PSU4:
      sprintf(key, "psu4_sensor_health");
      break;

    default:
      return -1;
  }

  sprintf(cvalue, (value > 0) ? "1": "0");

  return pal_set_key_value(key, cvalue);
}

static void pal_sel_strncat_output(char* output, char* msg, int max_output_len) {
  int legal_len;

  legal_len = max_output_len - strlen(output);
  if (legal_len < 0) {
    legal_len = 0;
  }
  strncat(output, msg, legal_len);
  if (legal_len < strlen(msg)) {
    syslog(LOG_INFO, "pal_sel_strncat_output: truncation occurs, and orgn msg: \"%s\"", msg);
  }
}

static bool update_oem_data2_str(sensor_offset_str_table_t offset_table, uint8_t event_data) {
  return (offset_table.ed2_mask != 0x00 && \
    ((((offset_table.ed2_mask & event_data) | offset_table.ed2_or) == offset_table.ed2_val) ? true: false));
}

static bool update_oem_data3_str(sensor_offset_str_table_t offset_table, uint8_t event_data) {
  return (offset_table.ed3_mask != 0x00 && \
    ((((offset_table.ed3_mask & event_data) | offset_table.ed3_or) == offset_table.ed3_val) ? true: false));
}

int
pal_parse_sel(uint8_t fru, uint8_t *sel, char *error_log)
{
  char temp_log[512] = {0};
  uint8_t event_type;
  uint8_t sensor_type = sel[10];
  uint8_t event_data1 = sel[13];
  uint8_t event_data2 = sel[14];
  uint8_t event_data3 = sel[15];
  bool parsed = false;
  bool match_oem_data2 = false;
  bool match_oem_data3 = false;
  sensor_offset_str_table_t offset_table;
  sensor_type_val_to_desc_str_t desc_table;
  uint8_t sensor_type_index;
  uint8_t sensor_type_count;
  uint8_t offset_table_index;
  uint8_t sel_sensor_spec_offset;
  uint8_t no_of_left_shifts;
  uint8_t hex_val_to_be_printed;

  /*
   * Event Type: sel[12][6:0]
   * The parsed rule based on sensor type is only applicable
   * when the event type value is 0x6F, sensor-specific discrete
   */
  event_type = sel[12] & SEL_EVENT_TYPE_MASK;
  if (event_type != SEL_SENSOR_SPECIFIC) {
    pal_parse_sel_helper(fru, sel, error_log);
    return 0;
  }

  /* Init output message */
  strcpy(error_log, "");

  /* Loop through g_sensor_type_val_to_desc_str_table to MatchSensorType */
  sensor_type_count = sizeof(g_sensor_type_val_to_desc_str_table) / sizeof(sensor_type_val_to_desc_str_t);
  for (sensor_type_index = 0; sensor_type_index < sensor_type_count; sensor_type_index++) {
    desc_table = g_sensor_type_val_to_desc_str_table[sensor_type_index];
    /* Check for SelRecordData Sensor type match with Table entry. If it is matched go further, else continue. */
    if (desc_table.sensor_type_val != sensor_type) {
      continue;
    }

    /* Loop through DescTable to UpdatedEventDescription. */
    for (offset_table_index = 0; offset_table_index < desc_table.offset_table_size; offset_table_index++){
      offset_table = desc_table.sensor_offset_str_table[offset_table_index];
      sel_sensor_spec_offset = event_data1 & SEL_SENSOR_SPECIFIC_OFFSET_MASK;

      /* Check for SelRecordData Sensor specific offset match with Table entry. If it is matched go further, else continue. */
      if (offset_table.sensor_spec_offset != sel_sensor_spec_offset) {
        continue;
      }

      /* UpatedSensorSpecOffsetDescription */
      /* Check for parsed Flag. */
      if (parsed == false) {
        /* When entering for the first time, make parsed flag as TRUE and get Description. */
        parsed = true;
        pal_sel_strncat_output(error_log, offset_table.desc_str, SEL_PARSER_RET_MAX_LEGAL_LEN);

        /* If any one of match_oem_data2 and match_oem_data3 is TRUE, then continue else break the loop. */
        match_oem_data2 = (event_data1 & SEL_OEM_DATA2_VALID_MASK) ? true: false;
        match_oem_data3 = (event_data1 & SEL_OEM_DATA3_VALID_MASK) ? true: false;
        if (match_oem_data2 || match_oem_data3) {
          continue;
        } else {
          break;
        }
      } else {
        /*
         * If match_oem_data2 is TRUE then check for event_data2 match in table entry.
         * If matched, Update the string and Continue the loop.
         */
        if (match_oem_data2 && update_oem_data2_str(offset_table, event_data2)) {
          if (offset_table.ed2_or != 0x00) {
            /*
             * If ed2_or is not zero then print associated HEX value.
             * Get no_of_left_shifts value from MASK
             * Loop until BIT0 is 1.
             */
            no_of_left_shifts = 0;
            while (((offset_table.ed2_mask >> no_of_left_shifts) & SEL_OEM_DATA_BIT0_MASK) == 0x00) {
              no_of_left_shifts++;
            }

            /* Get the HEX value to be printed. */
            hex_val_to_be_printed = ((event_data2 & offset_table.ed2_mask) >> no_of_left_shifts);

            /* Update string along with HEX value. */
            sprintf(temp_log, ". %s0x%02X", offset_table.desc_str, hex_val_to_be_printed);
            pal_sel_strncat_output(error_log, temp_log, SEL_PARSER_RET_MAX_LEGAL_LEN);
          } else {
            /* Update string alone. */
            sprintf(temp_log, ". %s", offset_table.desc_str);
            pal_sel_strncat_output(error_log, temp_log, SEL_PARSER_RET_MAX_LEGAL_LEN);
          }
          /* Continue the loop. */
          continue;
        }

        /*
         * If match_oem_data3 is TRUE then check for event_data3 match in table entry.
         * If matched, Update the string and Continue the loop.
         */
        if (match_oem_data3 && update_oem_data3_str(offset_table, event_data3)) {
          if (offset_table.ed3_or != 0x00) {
            /*
             * If ed3_or is not zero then print associated HEX value.
             * Get no_of_left_shifts value from MASK
             * Loop until BIT0 is 1.
             */
            no_of_left_shifts = 0;
            while (((offset_table.ed3_mask >> no_of_left_shifts) & SEL_OEM_DATA_BIT0_MASK) == 0x00) {
              no_of_left_shifts++;
            }

            /* Get the HEX value to be printed. */
            hex_val_to_be_printed = ((event_data3 & offset_table.ed3_mask) >> no_of_left_shifts);

            /* Update string along with HEX value. */
            sprintf(temp_log, ". %s0x%02X", offset_table.desc_str, hex_val_to_be_printed);
            pal_sel_strncat_output(error_log, temp_log, SEL_PARSER_RET_MAX_LEGAL_LEN);
          } else {
            /* Update string alone. */
            sprintf(temp_log, ". %s", offset_table.desc_str);
            pal_sel_strncat_output(error_log, temp_log, SEL_PARSER_RET_MAX_LEGAL_LEN);
          }
          /* Continue the loop. */
          continue;
        }
      } /* End of if-else loop: UpdatedSensorSpecOffsetDescription */
    } /* End of for loop: UpdatedEventDescription */
    break;
  } /* End of for loop: MatchSensorType */

  if (parsed == true) {
    return 0;
  }

  pal_parse_sel_helper(fru, sel, error_log);

  return 0;
}

int
minipack_sensor_name(uint8_t fru, uint8_t sensor_num, char *name) {
  uint8_t sensor_num_count;
  uint8_t sensor_num_index;
  sensor_num_val_to_desc_str_t desc_table;

  sensor_num_count = sizeof(g_sensor_num_val_to_desc_str_table) / sizeof(sensor_num_val_to_desc_str_t);
   /* Loop through g_sensor_num_val_to_desc_str_table to get Description based on sensor number */
  for (sensor_num_index = 0; sensor_num_index < sensor_num_count; sensor_num_index++) {
    desc_table = g_sensor_num_val_to_desc_str_table[sensor_num_index];
    if (desc_table.sensor_num_val != sensor_num) {
      continue;
    }
    pal_sel_strncat_output(name, desc_table.sensor_num_desc_str, SEL_SENSOR_NAME_MAX_LEGAL_LEN);
    return 0;
  }
  return -1;
}

int
pal_get_event_sensor_name(uint8_t fru, uint8_t *sel, char *name) {
  uint8_t snr_type = sel[10];
  uint8_t snr_num = sel[11];
  uint8_t sensor_type_index;
  uint8_t sensor_type_count;
  sensor_type_val_to_desc_str_t desc_table;

  sensor_type_count = sizeof(g_sensor_type_val_to_desc_str_table) / sizeof(sensor_type_val_to_desc_str_t);
  /* Loop through g_sensor_type_val_to_desc_str_table to get Description based on sensor type */
  for (sensor_type_index = 0; sensor_type_index < sensor_type_count; sensor_type_index++) {
    desc_table = g_sensor_type_val_to_desc_str_table[sensor_type_index];
    if (desc_table.sensor_type_val != snr_type) {
      continue;
    }
    pal_sel_strncat_output(name, desc_table.sensor_type_desc_str, SEL_SENSOR_NAME_MAX_LEGAL_LEN);
    return 0;
  }

  /* Translate it based on snr_num */
  if (minipack_sensor_name(fru, snr_num, name) == 0) {
    return 0;
  }

  /* Otherwise, translate it based on snr_num in the way of x86 event */
  return pal_get_x86_event_sensor_name(fru, snr_num, name);
}

/* Read the Front Panel Hand Switch and return the position */
int
pal_get_hand_sw_physically(uint8_t *pos) {
  char path[LARGEST_DEVICE_NAME + 1];
  int loc;

  snprintf(path, sizeof(path), GPIO_BMC_UART_SEL5, "value");
  if (read_device(path, &loc)) {
    return -1;
  }
  *pos = loc;

  return 0;
}

int
pal_get_hand_sw(uint8_t *pos) {
  char value[MAX_VALUE_LEN];
  uint8_t loc;
  int ret;

  ret = kv_get("scm_hand_sw", value, NULL, 0);
  if (!ret) {
    loc = atoi(value);
    if (loc > HAND_SW_BMC) {
      return pal_get_hand_sw_physically(pos);
    }
    *pos = loc;

    return 0;
  }

  return pal_get_hand_sw_physically(pos);
}

/* Return the Front Panel Power Button */
int
pal_get_dbg_pwr_btn(uint8_t *status) {
  int val;

  if (read_device(SCM_DBG_PWR_BTN, &val)) {
    return -1;
  }

  if (val) {
    *status = 0;
  } else {
    *status = 1;
  }

  return 0;
}

/* Return the Debug Card Reset Button status */
int
pal_get_dbg_rst_btn(uint8_t *status) {
  int val;

  if (read_device(SCM_DBG_RST_BTN, &val)) {
    return -1;
  }

  if (val) {
    *status = 1; /* RST BTN status pressed */
  } else {
    *status = 0; /* RST BTN status clear */
  }

  return 0;
}

/* Clear Debug Card Reset Button status */
int
pal_clr_dbg_rst_btn() {
  if (write_device(SCM_DBG_RST_BTN_CLR, "0")) {
    syslog(LOG_ERR, "Reset button status not clear");
    return -1;
  }
  msleep(5);

  if (write_device(SCM_DBG_RST_BTN_CLR, "1")) {
    syslog(LOG_ERR, "Reset button status can't recover to normal");
    return -2;
  }

  return 0;
}

/* Update the Reset button input to the server at given slot */
int
pal_set_rst_btn(uint8_t slot, uint8_t status) {
  char *val;

  if (slot != FRU_SCM) {
    return -1;
  }

  if (status) {
    val = "1";
  } else {
    val = "0";
  }

  if (write_device(SCM_COM_RST_BTN, val)) {
    return -1;
  }

  return 0;
}

/* Return the Debug Card UART Sel Button status */
int
pal_get_dbg_uart_btn(uint8_t *status) {
  int val;

  if (read_device(SCM_DBG_UART_BTN, &val)) {
    return -1;
  }

  if (val) {
    *status = 1; /* UART BTN status pressed */
  } else {
    *status = 0; /* UART BTN status clear */
  }

  return 0;
}

/* Clear Debug Card UART Sel Button status */
int
pal_clr_dbg_uart_btn() {
  if (write_device(SCM_DBG_UART_BTN_CLR, "0")) {
    syslog(LOG_ERR, "UART Sel button status not clear");
    return -1;
  }
  msleep(5);

  if (write_device(SCM_DBG_UART_BTN_CLR, "1")) {
    syslog(LOG_ERR, "UART Sel button status can't recover to normal");
    return -2;
  }

  return 0;
}

/* Switch the UART mux to userver or BMC */
int
pal_switch_uart_mux(uint8_t slot) {
  char path[LARGEST_DEVICE_NAME + 1];
  char *val;
  uint8_t prsnt;

  if (pal_is_debug_card_prsnt(&prsnt)) {
    return -1;
  }

  /* Refer the UART select table in schematic */
  if (slot == HAND_SW_SERVER) {
    val = "0";
  } else {
    val = "1";
  }

  snprintf(path, sizeof(path), GPIO_BMC_UART_SEL5, "value");
  if (write_device(path, val)) {
#ifdef DEBUG
    syslog(LOG_WARNING, "pal_switch_uart_mux: write_device fail: %s\n", path);
#endif
    return -1;
  }

  return 0;
}

int
pal_get_boot_order(uint8_t slot, uint8_t *req_data,
                   uint8_t *boot, uint8_t *res_len) {
  int ret, msb, lsb, i, j = 0;
  char str[MAX_VALUE_LEN] = {0};
  char tstr[4];

  ret = pal_get_key_value("server_boot_order", str);
  if (ret) {
    *res_len = 0;
    return ret;
  }

  for (i = 0; i < 2*SIZE_BOOT_ORDER; i += 2) {
    snprintf(tstr, sizeof(tstr), "%c\n", str[i]);
    msb = strtol(tstr, NULL, 16);

    snprintf(tstr, sizeof(tstr), "%c\n", str[i+1]);
    lsb = strtol(tstr, NULL, 16);
    boot[j++] = (msb << 4) | lsb;
  }
  *res_len = SIZE_BOOT_ORDER;

  return 0;
}

int
pal_set_boot_order(uint8_t slot, uint8_t *boot,
                   uint8_t *res_data, uint8_t *res_len) {
  int i, j, network_dev = 0;
  char str[MAX_VALUE_LEN] = {0};
  char tstr[10];
  enum {
    BOOT_DEVICE_IPV4 = 0x1,
    BOOT_DEVICE_IPV6 = 0x9,
  };

  *res_len = 0;

  for (i = 0; i < SIZE_BOOT_ORDER; i++) {
    if (i > 0) {  // byte[0] is boot mode, byte[1:5] are boot order
      for (j = i+1; j < SIZE_BOOT_ORDER; j++) {
        if (boot[i] == boot[j])
          return CC_INVALID_PARAM;
      }

      // If bit[2:0] is 001b (Network), bit[3] is IPv4/IPv6 order
      // bit[3]=0b: IPv4 first
      // bit[3]=1b: IPv6 first
      if ((boot[i] == BOOT_DEVICE_IPV4) || (boot[i] == BOOT_DEVICE_IPV6))
        network_dev++;
    }

    snprintf(tstr, 3, "%02x", boot[i]);
    if (strlen(str) + strlen(tstr) < MAX_VALUE_LEN - 1) {
      strncat(str, tstr, sizeof(tstr) - 1);
    } else {
      return CC_INVALID_PARAM;
    }
  }

  // not allow having more than 1 network boot device in the boot order
  if (network_dev > 1)
    return CC_INVALID_PARAM;

  return pal_set_key_value("server_boot_order", str);
}

int
pal_get_restart_cause(uint8_t slot, uint8_t *restart_cause) {
  char value[MAX_VALUE_LEN] = {0};
  unsigned int cause;

  if (kv_get("server_restart_cause", value, NULL, KV_FPERSIST)) {
    return -1;
  }
  if(sscanf(value, "%u", &cause) != 1) {
    return -1;
  }
  *restart_cause = cause;

  return 0;
}

int
pal_set_restart_cause(uint8_t slot, uint8_t restart_cause) {
  char value[MAX_VALUE_LEN] = {0};

  sprintf(value, "%d", restart_cause);
  if (kv_set("server_restart_cause", value, 0, KV_FPERSIST)) {
    return -1;
  }
  return 0;
}

int
pal_set_ppin_info(uint8_t slot, uint8_t *req_data, uint8_t req_len,
                  uint8_t *res_data, uint8_t *res_len) {
  char str[MAX_VALUE_LEN] = {0};
  char tstr[10];
  int i;
  int completion_code = CC_UNSPECIFIED_ERROR;
  *res_len = 0;

  for (i = 0; i < SIZE_CPU_PPIN; i++) {
    snprintf(tstr, sizeof(tstr), "%02x", req_data[i]);
    strcat(str, tstr);
  }

  if (pal_set_key_value("server_cpu_ppin", str) != 0)
    return completion_code;

  completion_code = CC_SUCCESS;

  return completion_code;
}

int
pal_get_fruid_path(uint8_t fru, char *path) {
  if (fru != FRU_SCM)
    return -1;

  sprintf(path, MINIPACK_FRU_PATH, "scm");

  return 0;
}

int
pal_ipmb_processing(int bus, void *buf, uint16_t size) {
  char key[MAX_KEY_LEN];
  char value[MAX_VALUE_LEN];
  struct timespec ts;
  static time_t last_time = 0;

  if ((bus == 4) && (((uint8_t *)buf)[0] == 0x20)) {  // OCP LCD debug card
    clock_gettime(CLOCK_MONOTONIC, &ts);
    if (ts.tv_sec >= (last_time + 5)) {
      last_time = ts.tv_sec;
      ts.tv_sec += 30;

      snprintf(key, sizeof(key), "ocpdbg_lcd");
      snprintf(value, sizeof(value), "%lld", ts.tv_sec);
      if (kv_set(key, value, 0, 0) < 0) {
        return -1;
      }
    }
  }

  return 0;
}

bool
pal_is_mcu_working(void) {
  char key[MAX_KEY_LEN] = {0};
  char value[MAX_VALUE_LEN] = {0};
  struct timespec ts;

  snprintf(key, sizeof(key), "ocpdbg_lcd");
  if (kv_get(key, value, NULL, 0)) {
     return false;
  }

  clock_gettime(CLOCK_MONOTONIC, &ts);
  if (strtoul(value, NULL, 10) > ts.tv_sec) {
     return true;
  }

  return false;
}
