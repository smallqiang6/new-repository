// SPDX-License-Identifier: GPL-2.0-only
/*
 * Aspeed FMC(Firmware SPI Memory Controller)
 *
 * Copyright (C) 2017 Google, Inc.
 * Copyright (C) 2021 Aspeed Technology Inc.
 *
 */

#include <linux/clk.h>
#include <linux/clk-provider.h>
#include <linux/err.h>
#include <linux/errno.h>
#include <linux/io.h>
#include <linux/module.h>
#include <linux/of_platform.h>
#include <linux/platform_device.h>
#include <linux/regulator/consumer.h>
#include <linux/reset.h>
#include <linux/spinlock.h>
#include <linux/types.h>

enum chips {
    AST2500 = 1,
    AST2600 = 2,
};
static int g_debug_info = 0;
static int g_debug_err = 0;
static int g_model = AST2500;

#define AST2600_FMC_WDT2_CTRL_STATUS   (0x1E620064)
#define AST2600_FMC_WDT2_TIMER_VALUE   (0x1E620068)
#define AST2600_FMC_WDT2_TIMER_REST    (0x1E62006C)

#define AST2520_FMC_CE_CTRL               (0x1E620004)
#define AST2520_FMC_WDT2_RESET_MASK       (0x1E78503C)
#define AST2520_FMC_WDT2_COUNTER_RELOAD   (0x1E785024)
#define AST2520_FMC_WDT2_COUNTER_RESTART  (0x1E785028)
#define AST2520_FMC_WDT2_CTRL             (0x1E78502C)
#define AST2520_FMC_WDT2_TIMEOUT_STATUS   (0x1E785030)

module_param(g_debug_info, int, S_IRUGO | S_IWUSR);
module_param(g_debug_err, int, S_IRUGO | S_IWUSR);

#define WB_ASPEED_COMMON_DEBUG(fmt, args...) do {                                        \
    if (g_debug_info) { \
        printk(KERN_INFO "[wb_aspeed_common][VER][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define WB_ASPEED_COMMON_DEBUG_ERR(fmt, args...) do {                                        \
    if (g_debug_err) { \
        printk(KERN_ERR "[wb_aspeed_common][ERR][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)


static ssize_t wb_aspeed_bmc_view_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    uint32_t tmp_val;
    char __iomem *addr_after_map;

    switch(g_model){
    case AST2500:
        addr_after_map = ioremap(AST2520_FMC_WDT2_TIMEOUT_STATUS, 4);
        tmp_val = readl(addr_after_map);
        iounmap(addr_after_map);
        WB_ASPEED_COMMON_DEBUG("get bmc view orign value %d success\n", tmp_val);
        if ((tmp_val & 0x2) != 0) {
            tmp_val = 1;
        } else {
            tmp_val = 0;
        }

        return (ssize_t)snprintf(buf, PAGE_SIZE, "%d\n", tmp_val);
    case AST2600:
        addr_after_map = ioremap(AST2600_FMC_WDT2_CTRL_STATUS, 4);
        tmp_val = readl(addr_after_map);
        iounmap(addr_after_map);
        WB_ASPEED_COMMON_DEBUG("get bmc view orign value %d success\n", tmp_val);
        tmp_val = (tmp_val & 0x10) >> 4;

        return (ssize_t)snprintf(buf, PAGE_SIZE, "%d\n", tmp_val);
    default:
        WB_ASPEED_COMMON_DEBUG_ERR("unsupport model %d\n", g_model);
        return -EINVAL;
    }

    WB_ASPEED_COMMON_DEBUG_ERR("unsupport model %d\n", g_model);
    return -EINVAL;
}

static ssize_t wb_aspeed_bmc_switch_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    uint32_t tmp, timer_value;
    char __iomem *addr_after_map;
    int ret;

    ret = kstrtoint(buf, 0, &timer_value);
    if (ret != 0) {
        WB_ASPEED_COMMON_DEBUG_ERR("invaild timer_value ret: %d, buf: %s.\n", ret, buf);
        return -EINVAL;
    }

    if (timer_value > 10*60) {
        WB_ASPEED_COMMON_DEBUG_ERR("Timer Reload Value, not more than 600(s): %d.\n", timer_value);
        return -EINVAL;
    }

    switch(g_model){
    case AST2500:
        /* set FMC 0 */
        tmp = 0x00;
        addr_after_map = ioremap(AST2520_FMC_CE_CTRL, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);
        /* reset WDT2 reset mask */
        tmp = 0x033FFFF3;
        addr_after_map = ioremap(AST2520_FMC_WDT2_RESET_MASK, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);
        /* set timer value */
        timer_value = timer_value * 1000 * 1000; /* The time unit is 1 us second.*/
        addr_after_map = ioremap(AST2520_FMC_WDT2_COUNTER_RELOAD, 4);
        writel(timer_value, addr_after_map);
        iounmap(addr_after_map);
        WB_ASPEED_COMMON_DEBUG("set timer value 0x%x success\n", timer_value);

        /* load Timer Reload Value */
        tmp = 0x4755;
        addr_after_map = ioremap(AST2520_FMC_WDT2_COUNTER_RESTART, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);

        /* enable fmc wdt2 */
        tmp = 0xB3;
        addr_after_map = ioremap(AST2520_FMC_WDT2_CTRL, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);

        return count;
    case AST2600:
        /* set timer value */
        timer_value = timer_value * 10; /* The time unit is 0.1 second.*/
        addr_after_map = ioremap(AST2600_FMC_WDT2_TIMER_VALUE, 4);
        writel(timer_value, addr_after_map);
        iounmap(addr_after_map);
        WB_ASPEED_COMMON_DEBUG("set timer value 0x%x success\n", timer_value);

        /* load Timer Reload Value */
        tmp = 0x4755;
        addr_after_map = ioremap(AST2600_FMC_WDT2_TIMER_REST, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);

        /* enable fmc wdt2 */
        tmp = 1;
        addr_after_map = ioremap(AST2600_FMC_WDT2_CTRL_STATUS, 4);
        writel(tmp, addr_after_map);
        iounmap(addr_after_map);

        return count;
    default:
        WB_ASPEED_COMMON_DEBUG_ERR("unsupport model %d\n", g_model);
        return -EINVAL;
    }

    WB_ASPEED_COMMON_DEBUG_ERR("unsupport model %d\n", g_model);
    return -EINVAL;
}

static DEVICE_ATTR(bmc_switch, S_IRUGO | S_IWUSR, wb_aspeed_bmc_view_show, wb_aspeed_bmc_switch_store);
static DEVICE_ATTR(bmc_view, S_IRUGO, wb_aspeed_bmc_view_show, NULL);

static struct attribute * wb_aspeed_attrs[] = {
    &dev_attr_bmc_switch.attr,
    &dev_attr_bmc_view.attr,
    NULL,
};
static struct attribute_group wb_aspeed_attr_group = {
    .attrs = wb_aspeed_attrs,
};

static int wb_aspeed_common_probe(struct platform_device *pdev)
{
    int chip_id, status;

    if (pdev->dev.of_node) {
        chip_id = (enum chips)of_device_get_match_data(&pdev->dev);
    } else {
        WB_ASPEED_COMMON_DEBUG_ERR("currently not support!\n");
        return -ENODEV;
    }

    switch (chip_id) {
    case AST2500:
        g_model = AST2500;
        break;
    case AST2600:
        g_model = AST2600;
        break;
    default:
        WB_ASPEED_COMMON_DEBUG_ERR("chip type %d is not suppredted!\n", chip_id);
        return -ENODEV;
    }

    status = sysfs_create_group(&pdev->dev.kobj, &wb_aspeed_attr_group);
    if (status != 0) {
        WB_ASPEED_COMMON_DEBUG_ERR("create bmc attr error!\n");
        return -EBADRQC;
    }

	return status;
}

static int wb_aspeed_common_remove(struct platform_device *pdev)
{
    sysfs_remove_group(&pdev->dev.kobj, &wb_aspeed_attr_group);

    return 0;
}


static const struct of_device_id wb_aspeed_common_matches[] = {
    { .compatible = "aspeed,ast2500-wb-common", .data = (void *)AST2500},
    { .compatible = "aspeed,ast2600-wb-common", .data = (void *)AST2600},
    {},
};

MODULE_DEVICE_TABLE(of, wb_aspeed_common_matches);

static struct platform_driver wb_aspeed_common_driver = {
	.probe = wb_aspeed_common_probe,
	.driver = {
		.name = "wb_aspeed_common",
		.of_match_table = wb_aspeed_common_matches,
	},
	.remove     = wb_aspeed_common_remove,
};

module_platform_driver(wb_aspeed_common_driver);

MODULE_AUTHOR("support");
MODULE_DESCRIPTION("wb aspeed common Driver");
MODULE_LICENSE("GPL");
