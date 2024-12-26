#ifndef __MV88E63XXX_H__
#define __MV88E63XXX_H__
#include "mdio_base.h"
/* Marvell SMI Parameters*/
#define MSD_OK                                  (0x00)   /* Operation succeeded                   */
#define MSD_FAIL                                (0x01)   /* Operation failed                    */
#define MSD_BAD_PARAM                           (0x04)   /* Illegal parameter in function called  */
#define MSD_BUSY                                (0x05)   /* Last operation busy */
#define MSD_NO_SUCH                             (0x0D)   /* No such item                    */
#define MSD_NOT_SUPPORTED                       (0x10)   /* This request is not support           */
#define MSD_ALREADY_EXIST                       (0x1B)   /* Tried to create existing item         */
#define MSD_BAD_CPU_PORT                        (0x20)   /* Input CPU Port is not valid physical port number */
#define MSD_FEATURE_NOT_ENABLE                  (0x40) /*The feature not been enabled when do operation*/

#define MSD_REG_SMI_COMMAND                     (0x0)
#define MSD_REG_SMI_DATA                        (0x1)
#define MSD_SMI_BUSY                            (0x8000)
#define MSD_SMI_MODE                            (0x1000)
#define MSD_SMI_MODE_BIT                        (12)
#define MSD_SMI_FUNC_BIT                        (13)
#define MSD_SMI_FUNC_SIZE                       (2)
#define MSD_SMI_OP_BIT                          (10)
#define MSD_SMI_OP_SIZE                         (2)
#define MSD_SMI_DEV_ADDR_BIT                    (5)
#define MSD_SMI_DEV_ADDR_SIZE                   (5)
#define MSD_SMI_REG_ADDR_BIT                    (0)
#define MSD_SMI_REG_ADDR_SIZE                   (5)
#define MSD_SMI_CLAUSE45                        (0)
#define MSD_SMI_CLAUSE22                        (1)
#define MSD_SMI_WRITE_ADDR                      (0x00)
#define MSD_SMI_WRITE                           (0x01)
#define MSD_SMI_READ_22                         (0x02)
#define MSD_SMI_READ_45                         (0x03)
#define MSD_SMI_READ_INC                        (0x02)
#define MSD_SMI_INTERNAL			            (0x0)
#define MSD_SMI_EXTERNAL			            (0x1)
#define MSD_SMI_SMISETUP			            (0x2)

/* Define Switch SMI Device Address */
#define AMETHYST_PORT_START_ADDR	            (0x0)    /* Start Port Address */
#define AMETHYST_GLOBAL1_DEV_ADDR	            (0x1B)	/* Global 1 Device Address */
#define AMETHYST_GLOBAL2_DEV_ADDR	            (0x1C)	/* Global 2 Device Address */
#define AMETHYST_TCAM_DEV_ADDR		            (0x1F)	/* TCAM Device Address */
#define AMETHYST_QD_REG_SMI_PHY_CMD       	    (0x18)	/* SMI PHY Command Register */	
#define AMETHYST_QD_REG_SMI_PHY_DATA      	    (0x19)	/* SMI PHY Data Register */
#define SMI_LOOP                                (100)	
#define SMI_ACCESS_LOOP                         (1000)

#define SW_ADDR                                 (0x1f)

int mv88e6xxx_phyred_read(int addr, int reg);
int mv88e6xxx_phyred_write(int addr, int reg, unsigned int value);
int mv88e6xxx_reg_read(int sw_addr, int addr, int reg, unsigned int *value);
int mv88e6xxx_reg_write(int sw_addr, int addr, int reg, unsigned int value);

#endif /* End of __MV88E63XXX_H__ */