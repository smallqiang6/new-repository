#include "bcm5xxx.h"
/* Broadcom SMI Phy Register Read-Write */
int bcm5xxx_phyreg_read(int addr, int reg)
{
    return ast_mdiobus_read(addr, reg);
}

int bcm5xxx_phyreg_write(int addr, int reg, int value)
{
    return ast_mdiobus_write(addr, reg, value);
}
