#ifndef __PHYTOOL_H__
#define __PHYTOOL_H__

#include "mv88e6xxx.h"
#include "bcm5xxx.h"
#include "mdio_base.h"

#define NORMAL_MDIO             (0x00)
#define MARVELL_88E6XXX         (0x01)

#define ARG_BUFFER_LEN       (64)

struct smitool_ops {
    int switch_type;
    char *name;
    int (*read_phy)(int addr, int reg);
    int (*write_phy)(int addr, int reg, int value);
    int (*read_switch)(int sw_addr, int addr, int reg, unsigned int *value);
    int (*write_switch)(int sw_addr, int addr, int reg, unsigned int value);
};

typedef int (*smitool_func)(int argc, char* argv[],struct smitool_ops* p_ops);

struct smitool_function{
    char type_obj[ARG_BUFFER_LEN];
    char type_op[ARG_BUFFER_LEN];
    smitool_func func;
};

int smitool_phy_rd(int argc, char *argv[], struct smitool_ops *p_ops);
int smitool_phy_wr(int argc, char *argv[], struct smitool_ops *p_ops);
int smitool_switch_rd(int argc, char *argv[], struct smitool_ops *p_ops);
int smitool_switch_wr(int argc, char *argv[], struct smitool_ops *p_ops);

struct smitool_function phy_funcs[] = {
    { "phy", "rd", smitool_phy_rd, },
    { "phy", "wr", smitool_phy_wr, },
    { "switch", "rd", smitool_switch_rd, },
    { "switch", "wr", smitool_switch_wr, },
    {}
};

#endif /* End of __PHYTOOL_H__ */
