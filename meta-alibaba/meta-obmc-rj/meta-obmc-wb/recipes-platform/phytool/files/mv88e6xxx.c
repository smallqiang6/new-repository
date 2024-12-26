#include "mv88e6xxx.h"
/* Marvell SMI Register Read-Write Multi-Chip */
static int mv88e6xxx_reg_wait_ready(int sw_addr)
{
    int timeout, ret;

    timeout = SMI_LOOP;
    do
    {
        ret = ast_mdiobus_read(sw_addr, MSD_REG_SMI_COMMAND);
        if (ret < 0){
            MSD_DBG_ERROR("read AMETHYST_QD_REG_SMI_PHY_CMD register returned: %d.\n", ret);
            continue;
        }
        if (timeout-- < 1){
            MSD_DBG_INFO("read AMETHYST_QD_REG_SMI_PHY_CMD register Timed Out\n");
            return -MSD_BUSY;
        }
    } while (ret & MSD_SMI_BUSY);

    return MSD_OK;
}

int mv88e6xxx_reg_write(int sw_addr, int addr, int reg, unsigned int value)
{
    int ret;
    unsigned int smiReg;

    /* Single-Chip Mode */
    if (sw_addr == 0) {
        return ast_mdiobus_write(addr, reg, value);
    }

    /* Wait for the bus to become free. */
    ret = mv88e6xxx_reg_wait_ready(sw_addr);
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_reg_wait_ready timeout %d\n", ret);
        return ret;
    }
    /* Transmit the data to write. */
    ret = ast_mdiobus_write(sw_addr, MSD_REG_SMI_DATA, value);
    if (ret < 0) {
        MSD_DBG_ERROR("ast_mdiobus_write failed %d\n", ret);
        return ret;
    }
    /* Transmit the write command. */
    smiReg = MSD_SMI_BUSY | (addr << MSD_SMI_DEV_ADDR_BIT) | (MSD_SMI_WRITE << MSD_SMI_OP_BIT) | 
            (reg << MSD_SMI_REG_ADDR_BIT) | (MSD_SMI_CLAUSE22 << MSD_SMI_MODE_BIT);
    ret = ast_mdiobus_write(sw_addr, MSD_REG_SMI_COMMAND, smiReg);
    if (ret < 0) {
        MSD_DBG_ERROR("ast_mdiobus_write failed %d\n", ret);
        return ret;
    }
    /* Wait for the write command to complete. */
    ret = mv88e6xxx_reg_wait_ready(sw_addr);
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_reg_wait_ready timeout %d\n", ret);
        return ret;
    }

    return 0;
}

int mv88e6xxx_reg_read(int sw_addr, int addr, int reg, unsigned int *value)
{
    int ret;
    unsigned int smiReg;

    /* Single-Chip Mode */
    if (sw_addr == 0) {
        return ast_mdiobus_read(addr, reg);
    }
    /* Wait for the bus to become free. */
    ret = mv88e6xxx_reg_wait_ready(sw_addr);
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_reg_wait_ready timeout %d\n", ret);
        return ret;
    }
    /* Transmit the read command. */
    smiReg = MSD_SMI_BUSY | (addr << MSD_SMI_DEV_ADDR_BIT) | (MSD_SMI_READ_22 << MSD_SMI_OP_BIT) | 
            (reg << MSD_SMI_REG_ADDR_BIT) | (MSD_SMI_CLAUSE22 << MSD_SMI_MODE_BIT);
    ret = ast_mdiobus_write(sw_addr, MSD_REG_SMI_COMMAND, smiReg);
    if (ret < 0) {
        MSD_DBG_ERROR("ast_mdiobus_write failed %d\n", ret);
        return ret;
    }
    /* Wait for the read command to complete. */
    ret = mv88e6xxx_reg_wait_ready(sw_addr);
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_reg_wait_ready timeout %d\n", ret);
        return ret;
    }
    /* Read the data. */
    ret = ast_mdiobus_read(sw_addr, MSD_REG_SMI_DATA);
    if (ret < 0) {
        MSD_DBG_ERROR("ast_mdiobus_read failed %d\n", ret);
        return ret;
    }
    *value = ret & 0xffff;
    return MSD_OK;
}
/* Marvell SMI Phy Register Read-Write */
static int mv88e6xxx_smi_wait_ready(void)
{
    int smiReg, timeout, ret;

    timeout = SMI_ACCESS_LOOP;
    do
    {
        ret = mv88e6xxx_reg_read(SW_ADDR, AMETHYST_GLOBAL2_DEV_ADDR, AMETHYST_QD_REG_SMI_PHY_CMD, &smiReg);
        if (ret != MSD_OK){
            MSD_DBG_ERROR("read AMETHYST_QD_REG_SMI_PHY_CMD register returned: %d.\n", ret);
            continue;
        }
        if (timeout-- < 1){
            MSD_DBG_INFO("read AMETHYST_QD_REG_SMI_PHY_CMD register Timed Out\n");
            return -MSD_BUSY;
        }
    } while (smiReg & MSD_SMI_BUSY);

    return MSD_OK;
}
int mv88e6xxx_phyred_read(int addr, int reg)
{
    int ret;
    unsigned int smiReg;

    ret = mv88e6xxx_smi_wait_ready();
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_smi_wait_ready timeout %d\n", ret);
        return ret;
    }

    smiReg =  MSD_SMI_BUSY | (addr << MSD_SMI_DEV_ADDR_BIT) | (MSD_SMI_READ_22 << MSD_SMI_OP_BIT) | 
            (reg << MSD_SMI_REG_ADDR_BIT) | (MSD_SMI_CLAUSE22 << MSD_SMI_MODE_BIT);
    ret = mv88e6xxx_reg_write(SW_ADDR, AMETHYST_GLOBAL2_DEV_ADDR,AMETHYST_QD_REG_SMI_PHY_CMD, smiReg);
    if (ret < 0) {
        MSD_DBG_ERROR("read AMETHYST_QD_REG_SMI_PHY_CMD register returned: %d.\n", ret);
        return ret;
    }

    ret = mv88e6xxx_smi_wait_ready();
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_smi_wait_ready timeout %d\n", ret);
        return ret;
    }

    ret = mv88e6xxx_reg_read(SW_ADDR, AMETHYST_GLOBAL2_DEV_ADDR, AMETHYST_QD_REG_SMI_PHY_DATA, &smiReg);
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_reg_read failed %d\n", ret);
        return ret;
    }
    return smiReg;
}

int mv88e6xxx_phyred_write(int addr, int reg, unsigned int value)
{
    int ret;
    unsigned int smiReg;

    ret = mv88e6xxx_smi_wait_ready();
    if (ret < 0) {
        MSD_DBG_ERROR("mv88e6xxx_smi_wait_ready timeout %d\n", ret);
        return ret;
    }

    ret = mv88e6xxx_reg_write(SW_ADDR, AMETHYST_GLOBAL2_DEV_ADDR, AMETHYST_QD_REG_SMI_PHY_DATA, value);
    if (ret < 0) {
        MSD_DBG_ERROR("write AMETHYST_QD_REG_SMI_PHY_DATA register returned: %d.\n", ret);
        return ret;
    }

    smiReg = MSD_SMI_BUSY | (addr << MSD_SMI_DEV_ADDR_BIT) | (MSD_SMI_WRITE << MSD_SMI_OP_BIT) | 
            (reg << MSD_SMI_REG_ADDR_BIT) | (MSD_SMI_CLAUSE22 << MSD_SMI_MODE_BIT);

    ret = mv88e6xxx_reg_write(SW_ADDR, AMETHYST_GLOBAL2_DEV_ADDR, AMETHYST_QD_REG_SMI_PHY_CMD, smiReg);
    if (ret < 0) {
        MSD_DBG_ERROR("write AMETHYST_QD_REG_SMI_PHY_CMD register returned: %d.\n", ret);
        return ret;
    }

    return MSD_OK;
}