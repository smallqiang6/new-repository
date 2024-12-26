/*
 * smitool.c
 * Original Author:  ruijie@ruijie.com.cn, 2021-09-10
 *
 * Mdio Interface
 *
 */
 /* 
 smitool phy rd|wr 5387|6321|8367 addr reg value 
 smitool switch rd|wr 5387|6321|8367 sw_addr addr reg value 
 */
#include "smitool.h"

static void smitool_help_info(void)
{
    printf("smitool usage:\n");
    printf("\tsmitool phy rd [SWITCH_TYPE]|general addr reg (read phy register)\n");
    printf("\tsmitool phy wr [SWITCH_TYPE]|general addr reg value (write phy register)\n");
    printf("\tsmitool switch rd [SWITCH_TYPE]|general sw_addr addr reg (read switch register)\n");
    printf("\tsmitool switch wr [SWITCH_TYPE]|general sw_addr addr reg value (write switch register)\n");
}

struct smitool_ops phy_ops[] = {
    {
        NORMAL_MDIO,
        "bcm5387",
        bcm5xxx_phyreg_read,
        bcm5xxx_phyreg_write,
        NULL,
        NULL,
    },
    {
        MARVELL_88E6XXX,
        "88e6321",
        mv88e6xxx_phyred_read,
        mv88e6xxx_phyred_write,
        mv88e6xxx_reg_read,
        mv88e6xxx_reg_write,
    },
    {
        NORMAL_MDIO,
        "general",
        ast_mdiobus_read,
        ast_mdiobus_write,
        NULL,
        NULL,
    },
    {
        NORMAL_MDIO,
        "bcm53134",
        ast_mdiobus_read,
        ast_mdiobus_write,
        NULL,
        NULL,
    },
    {}
};

struct smitool_ops* get_phy_ops(char *name)
{
    int index, size;

    size = sizeof(phy_ops) / sizeof(phy_ops[0]) - 1;
    for (index = 0; index < size; index++) {
        if (strncmp(name, phy_ops[index].name, strlen(phy_ops[index].name)) == 0) {
            return &phy_ops[index];
        }
    }

    return NULL;
}

int smitool_phy_rd(int argc, char *argv[], struct smitool_ops *p_ops)
{
    int addr, reg, ret;

    ret = -1;
    if (argc < 6) {
        smitool_help_info();
        return ret;
    }
    if (p_ops->read_phy == NULL) {
        printf("%s not support phy read\n", p_ops->name);
        return ret;
    }

    addr = strtoul(argv[4], 0, 0);
    reg = strtoul(argv[5], 0, 0);
    ret = p_ops->read_phy(addr, reg);
    if (ret < 0) {
        printf("read_phy failed\n");
        return ret;
    } else {
        printf("0x%4x\n", ret);
    }

    return 0;
}

int smitool_phy_wr(int argc, char *argv[], struct smitool_ops *p_ops)
{
    int addr, reg, value, ret;

    ret = -1;
    if (argc < 7) {
        smitool_help_info();
        return ret;
    }

    if (p_ops->write_phy == NULL) {
        printf("%s not support phy write\n", p_ops->name);
        return ret;
    }

    addr = strtoul(argv[4], 0, 0);
    reg = strtoul(argv[5], 0, 0);
    value = strtoul(argv[6], 0, 0);
    ret = p_ops->write_phy(addr, reg, value);
    if (ret) {
        printf("write_phy failed\n");
    }

    return ret;
}

int smitool_switch_rd(int argc, char *argv[], struct smitool_ops *p_ops)
{
    int sw_addr, addr, reg, value, ret;

    ret = -1;
    if (argc < 7) {
        smitool_help_info();
        return -1;
    }

    if (p_ops->read_switch == NULL) {
        printf("%s not support switch read\n", p_ops->name);
        return ret;
    }

    sw_addr = strtoul(argv[4], 0, 0);
    addr = strtoul(argv[5], 0, 0);
    reg = strtoul(argv[6], 0, 0);
    ret = p_ops->read_switch(sw_addr, addr, reg, &value);
    if (ret == 0) {
        printf("0x%4x\n", value);
    } else {
        printf("read_switch failed\n");
    }

    return ret;
}

int smitool_switch_wr(int argc, char *argv[], struct smitool_ops *p_ops)
{
    int sw_addr, addr, reg, value, ret;

    ret = -1;
    if (argc < 8) {
        smitool_help_info();
        return ret;
    }

    if (p_ops->write_switch == NULL) {
        printf("%s not support switch write\n", p_ops->name);
        return ret;
    }

    sw_addr = strtoul(argv[4], 0, 0);
    addr = strtoul(argv[5], 0, 0);
    reg = strtoul(argv[6], 0, 0);
    value = strtoul(argv[7], 0, 0);
    ret = p_ops->write_switch(sw_addr, addr, reg, value);
    if (ret) {
        printf("write_switch failed\n");
    }

    return ret;
}

smitool_func get_current_func(char *type_obj, char *type_op)
{
    int size, i;

    size = sizeof(phy_funcs) / sizeof(phy_funcs[0]) - 1;
    for(i = 0; i < size; i++) {
        if (strncmp(type_obj, phy_funcs[i].type_obj, strlen(phy_funcs[i].type_obj)) == 0
                && strncmp(type_op, phy_funcs[i].type_op, strlen(phy_funcs[i].type_op)) == 0) {
            return phy_funcs[i].func;
        }
    }

    return NULL;
}

int main(int argc, char *argv[])
{
    int ret;
    smitool_func cfunc;
    struct smitool_ops *p_ops;

    mdio_debug();

    ret = open_fd();
    if (ret < 0) {
        printf("open fd failed\n");
        return ret;
    }
    if (argc < 6) {
        smitool_help_info();
        return ret;
    }
    cfunc = get_current_func(argv[1], argv[2]);
    if (cfunc == NULL) {
        printf("get_current_func failed\n");
        smitool_help_info();
        close_fd();
        return 0;
    }

    p_ops = get_phy_ops(argv[3]);
    if (p_ops == NULL) {
        printf("get_phy_ops failed\n");
        smitool_help_info();
        close_fd();
        return 0;
    }

    ret = cfunc(argc, argv, p_ops);
    close_fd();

    return ret;
}
