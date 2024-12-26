#ifndef __BCM5XXX_H__
#define __BCM5XXX_H__
#include "mdio_base.h"
int bcm5xxx_phyreg_read(int addr, int reg);
int bcm5xxx_phyreg_write(int addr, int reg, int value);
#endif /* End of __BCM5XXX_H__ */