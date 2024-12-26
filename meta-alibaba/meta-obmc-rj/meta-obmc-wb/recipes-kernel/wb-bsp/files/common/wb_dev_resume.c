/*
 * Copyright(C) 2022-2032 Ruijie Network. All rights reserved.
 *
 * wb_dev_resume.c
 * Original Author: xxx@ruijie.com.cn 2022-04-01
 *
 * The main function of the driver is to register the device exception recovery interface with 
 * the framework layer through the platform driver, enabling exception recovery for the device 
 * when an anomaly occurs.
 *
 * History
 *  [Version]        [Author]               [Date]            [Description]
 *    v1.0             xxx                 2022-04-01         Initial version
 */

#include <linux/platform_device.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/version.h>
#include <linux/delay.h>
#include <linux/init.h>
#include <linux/io.h>
#include <linux/of.h>
#include <asm/uaccess.h>
#include <linux/fs.h>
#include <linux/pci.h>
#include <linux/kallsyms.h>
#include <linux/synclink.h>
#include <linux/bug.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/kprobes.h>


#define DRV_NAME        "dev-resume-driver"

/* define of C3000 CPU */
#define C3000_PS2B_PCIE_DEV_VID     (0x8086)
#define C3000_PS2B_PCIE_DEV_DID     (0x19dd)
#define GPIO_RX_DIS_BITS            (BIT9)
#define PAD_MODE_BITS               (BIT10 | BIT11 | BIT12)
#define PAD_TERM_BITS               (BIT10 | BIT11 | BIT12 | BIT13)

#define RESUME_WAY_MAX_NUM          (8)


enum dev_type_e {
    DEV_TYPE_EUSB,
    DEV_TYPE_MMC,
    DEV_TYPE_SSD,
    DEV_TYPE_END,
};

enum dev_resume_way_e {
    /* Recovery method: Device exception recovery is performed by writing to registers. Different device types have different bound interfaces */
    DEV_RESUME_WAY1_WR_REG = 1,
    DEV_RESUME_WAY2_WR_REG = 2,

    /* Recovery method: Device exception recovery is performed by controlling the GPIO levels */
    DEV_RESUME_WAY2_CTL_GPIO,

    DEV_RESUME_WAYX_END,
};

enum reg_access_mode_e {
    ACCESS_MODE_DEV_FILE = 1,
    ACCESS_MODE_IO,
    ACCESS_MODE_MEM,
    ACCESS_MODE_END,
};

typedef struct reg_cfg_info_s {
    u32 reg_addr;
    u32 reg_width;
    u32 access_mode;
    u32 reset_val;
    u32 dereset_val;
    u32 reset_mask;
    u32 reset_delay;
    u32 dereset_delay;
    u32 is_dereset;
    
    const char *dev_file_path;
    u64 map_base_addr;
} reg_cfg_info_t;

typedef struct gpio_cfg_info_s {
    u32 gpio_num;
    u32 active_level;
    u32 reset_delay;
    u32 dereset_delay;
} gpio_cfg_info_t;

typedef struct mmc_cfg_info_s {
    u32 resume_way;

    union {
        reg_cfg_info_t  reg_info;
        gpio_cfg_info_t gpio_info;
    } info;
} mmc_cfg_info_t;

typedef struct ssd_cfg_info_s {
    u32 resume_way;
    
    union {
        reg_cfg_info_t  reg_info;
    } info;
} ssd_cfg_info_t;

typedef struct eusb_cfg_info_s {
    u32 resume_way;
    
    union {
        reg_cfg_info_t  reg_info;
    } info;
} eusb_cfg_info_t;

typedef int *(*dev_resume_func_t)(u32, u32);

typedef int (*reg_dev_resume_func_t)(dev_resume_func_t);

typedef int (*unreg_dev_resume_func_t)(void);

typedef struct dev_resume_info_s {
    struct list_head list;
    u32 dev_type;
    u32 slot_id;
    u32 resume_way_num;
    u32 bit_mask;

    const char *reg_intf_name;
    unsigned long reg_intf_addr;

    const char *unreg_intf_name;
    unsigned long unreg_intf_addr;

    union {
        mmc_cfg_info_t mmc_cfg_info[RESUME_WAY_MAX_NUM];
        ssd_cfg_info_t ssd_cfg_info[RESUME_WAY_MAX_NUM];
        eusb_cfg_info_t eusb_cfg_info[RESUME_WAY_MAX_NUM];
    } dev_cfg_info;
} dev_resume_info_t;

/* Manage all registered device recovery information through this linked list. */
static LIST_HEAD(dev_resume_info_list);

static DEFINE_SPINLOCK(dev_resume_info_list_lock);

/********************************** start：debug print ***********************************/
static int debug = 0;
module_param(debug, int, S_IRUGO | S_IWUSR);
MODULE_PARM_DESC(debug, "control print info level. 0: none; 1: err; 2: err + warn; 3: err + warn +info; >3: all");
#define DEBUG_ERROR(fmt, args...)                                                           \
    do {                                                                                    \
        if (debug > 0) {                                                                    \
            printk(KERN_ERR "[func:%s line:%d]  "fmt, __func__, __LINE__, ## args);         \
        } else {                                                                            \
            pr_debug(fmt, ## args);                                                         \
        }                                                                                   \
    } while(0)

#define DEBUG_WARN(fmt, args...)                                                            \
        do {                                                                                \
            if (debug > 1) {                                                                \
                printk(KERN_WARNING "[func:%s line:%d]  "fmt, __func__, __LINE__, ## args); \
            } else {                                                                        \
                pr_debug(fmt, ## args);                                                     \
            }                                                                               \
        } while(0)

#define DEBUG_INFO(fmt, args...)                                                            \
    do {                                                                                    \
        if (debug > 2) {                                                                    \
            printk(KERN_INFO "[func:%s line:%d]  "fmt, __func__, __LINE__, ## args);        \
        } else {                                                                            \
            pr_debug(fmt, ## args);                                                         \
        }                                                                                   \
    } while(0)

#define DEBUG_VERBOSE(fmt, args...)                                                         \
    do {                                                                                    \
        if (debug > 3) {                                                                    \
            printk(KERN_DEBUG "[func:%s line:%d]  "fmt, __func__, __LINE__, ## args);       \
        } else {                                                                            \
            pr_debug(fmt, ## args);                                                         \
        }                                                                                   \
    } while(0)
/********************************** end：debug print ***********************************/

/********************************** start：defaul print ***********************************/
#define DEBUG(fmt, args...)                                                                 \
    do {                                                                                    \
        printk(KERN_DEBUG "[func:%s line:%d]  "fmt, __func__, __LINE__, ## args);           \
    } while(0)
/********************************** end：defaul print ***********************************/

static int noop_pre(struct kprobe *p, struct pt_regs *regs) { return 0; }
static struct kprobe kp = {   
	.symbol_name = "kallsyms_lookup_name",  
};
unsigned long (*kallsyms_lookup_name_fun)(const char *name) = NULL;

/* Call kprobe to find the address location of kallsyms_lookup_name */
static int find_kallsyms_lookup_name(void)
{ 
    int ret = -1;

	kp.pre_handler = noop_pre;
	ret = register_kprobe(&kp);
    if (ret < 0) {  
	    DEBUG_ERROR("register_kprobe failed, error:%d\n", ret); 
        return ret; 
	}
	DEBUG_INFO("kallsyms_lookup_name addr: %p\n", kp.addr); 
	kallsyms_lookup_name_fun = (void*)kp.addr; 
	unregister_kprobe(&kp);
    
	return ret;
}

static int file_read_in_kernel(const char *path, uint32_t pos, uint8_t *val, size_t size)
{
    int ret;
    struct file *filp;
    loff_t tmp_pos;

    filp = filp_open(path, O_RDONLY, 0);
    if (IS_ERR(filp)) {
        DEBUG_ERROR("read open failed errno = %ld\r\n", -PTR_ERR(filp));
        filp = NULL;
        goto exit;
    }
    ret = 0;
    tmp_pos = (loff_t)pos;

    ret = kernel_read(filp, val, size, &tmp_pos);
    if (ret < 0) {
        DEBUG_ERROR("read kernel_read failed, ret=%d\r\n", ret);
        goto exit;
    }
    filp_close(filp, NULL);

    return ret;

exit:
    if (filp != NULL) {
        filp_close(filp, NULL);
    }

    return -1;
}

static int file_write_in_kernel(const char *path, uint32_t pos, uint8_t *val, size_t size)
{
    int ret;
    struct file *filp;
    loff_t tmp_pos;

    filp = filp_open(path, O_RDWR, 777);
    if (IS_ERR(filp)) {
        DEBUG_ERROR("write open failed errno = %ld\r\n", -PTR_ERR(filp));
        filp = NULL;
        goto exit;
    }
    ret = 0;
    tmp_pos = (loff_t)pos;

    ret = kernel_write(filp, val, size, &tmp_pos);
    if (ret < 0) {
        DEBUG_ERROR("write kernel_write failed, ret=%d\r\n", ret);
        goto exit;
    }
    vfs_fsync(filp, 1);
    filp_close(filp, NULL);

    return ret;

exit:
    if (filp != NULL) {
        filp_close(filp, NULL);
    }

    return -1;
}

static int write_reg_accord_to_access_mode(reg_cfg_info_t *p_reg_info, u32 addr, u8 *pval, size_t size)
{
    int ret;
    u32 ui_reg_val;
    u16 us_reg_val;
    u8  uc_reg_val;
    u8 __iomem *membase;

    if ((p_reg_info == NULL) || (pval == NULL)) {
        DEBUG_ERROR("invalid para\n");
        return -EINVAL;
    }

    DEBUG_INFO("mode: %u, addr: 0x%x, size: 0x%zx, val: 0x%x\n", \
                p_reg_info->access_mode, addr, size, *(u32*)pval);

    switch (p_reg_info->access_mode) {
    case ACCESS_MODE_DEV_FILE:
        if (p_reg_info->dev_file_path == NULL) {
            DEBUG_ERROR("invalid para dev_file_name\n");
            return -EINVAL;
        }

        DEBUG_INFO("path: %s\n", p_reg_info->dev_file_path);
        ret = file_write_in_kernel(p_reg_info->dev_file_path, addr, pval, size);
        if (ret < 0) {
            DEBUG_ERROR("wr %s fail, ret: %d, addr: 0x%x, size: 0x%zx\n", p_reg_info->dev_file_path, \
                         ret, addr, size);
            return -EIO;
        }

        break;
    case ACCESS_MODE_IO:
        if (size == 4) {
            ui_reg_val = *(u32*)pval;
            outl(ui_reg_val, (unsigned long)(addr));
        } else if (size == 2) {
            us_reg_val = *(u16*)pval;
            outw(us_reg_val, (unsigned long)(addr));
        } else {
            uc_reg_val = *pval;
            outb(uc_reg_val, (unsigned long)(addr));
        }

        break;
    case ACCESS_MODE_MEM:
        membase = ioremap(p_reg_info->map_base_addr, size);
        DEBUG_INFO("base_addr: 0x%llx, membase: 0x%p\n", p_reg_info->map_base_addr, membase);
        if (membase == NULL) {
            DEBUG_ERROR("ioremap fail\n");
            return -ENOMEM;
        }

        if (size == 4) {
            ui_reg_val = *(u32*)pval;
            writel(ui_reg_val, (membase + addr));
        } else if (size == 2) {
            us_reg_val = *(u16*)pval;
            writew(us_reg_val, (membase + addr));
        } else {
            uc_reg_val = *pval;
            writeb(uc_reg_val, (membase + addr));
        }
        iounmap(membase);

        break;
    default:
        DEBUG_ERROR("invalid access mode: %u\n", p_reg_info->access_mode);
        return -EFAULT;
    }

    return 0;
}

static int read_reg_accord_to_access_mode(reg_cfg_info_t *p_reg_info, u32 addr, u8 *pval, size_t size)
{
    int ret;
    u8 __iomem *membase;

    if ((p_reg_info == NULL) || (pval == NULL)) {
        DEBUG_ERROR("invalid para reg_info\n");
        return -EINVAL;
    }

    DEBUG_INFO("mode: %u, addr: 0x%x, size: 0x%zx\n", p_reg_info->access_mode, addr, size);

    switch (p_reg_info->access_mode) {
    case ACCESS_MODE_DEV_FILE:
        if (p_reg_info->dev_file_path == NULL) {
            DEBUG_ERROR("invalid para dev_file_name\n");
            return -EINVAL;
        }
        
        DEBUG_INFO("path: %s\n", p_reg_info->dev_file_path);
        ret = file_read_in_kernel(p_reg_info->dev_file_path, addr, pval, size);
        if (ret < 0) {
            DEBUG_ERROR("rd %s fail, ret: %d, addr: 0x%x, size: 0x%zx\n", p_reg_info->dev_file_path, \
                         ret, addr, size);
            return -EIO;
        }

        break;
    case ACCESS_MODE_IO:
        if (size == 4) {
            *(u32*)pval = inl((unsigned long)addr);
        } else if (size == 2) {
            *(u16*)pval = inw((unsigned long)addr);
        } else {
            *pval = inb((unsigned long)addr);
        }

        break;
    case ACCESS_MODE_MEM:
        membase = ioremap(p_reg_info->map_base_addr, size);
        if (membase == NULL) {
            DEBUG_ERROR("ioremap fail\n");
            return -ENOMEM;
        }
        
        if (size == 4) {
            *(u32*)pval = readl(membase + addr);
        } else if (size == 2) {
            *(u16*)pval = readw(membase + addr);
        } else {
            *pval = readb(membase + addr);
        }
        
        iounmap(membase);

        break;
    default:
        DEBUG_ERROR("invalid access mode: %u\n", p_reg_info->access_mode);
        return -EFAULT;
    }

    DEBUG_INFO("rd val: 0x%x", *(u32*)pval);
    return 0;
}

static int do_resume_by_op_reg(reg_cfg_info_t *p_reg_info)
{
    int ret;
    u32 addr;
    u8 *pval;
    size_t size;
    u32 buf;
    u32 save_buf;

    /* 1. read reg raw value first */
    buf = 0;
    pval = (u8 *)&buf;
    addr = p_reg_info->reg_addr;
    size = p_reg_info->reg_width;
    ret = read_reg_accord_to_access_mode(p_reg_info, addr, pval, size);
    if (ret != 0) {
        DEBUG_ERROR("rd fail, ret: %d\n", ret);
        return -EFAULT;
    }
    DEBUG_INFO("read: addr: 0x%x, width: 0x%zx, rd_val: 0x%x\n", addr, size, buf);
    save_buf = buf;

    /* 2. write reg to recovery */
    buf &= ~(p_reg_info->reset_mask);
    buf |= p_reg_info->reset_val;
    ret = write_reg_accord_to_access_mode(p_reg_info, addr, pval, size);
    if (ret != 0) {
        DEBUG_ERROR("wr fail, ret: %d\n", ret);
        return -EFAULT;
    }
    DEBUG_INFO("write: addr: 0x%x, width: 0x%zx, wr_val: 0x%x\n", addr, size, buf);

    /* 3. reset delay */
    DEBUG_INFO("reset delay time: %u us\n", p_reg_info->reset_delay);
    usleep_range(p_reg_info->reset_delay + 1, p_reg_info->reset_delay + 2);

    if (p_reg_info->is_dereset) {
        /* 4. write reg to unreset */
        buf = save_buf;
        buf &= ~(p_reg_info->reset_mask);
        buf |= p_reg_info->dereset_val;
        ret = write_reg_accord_to_access_mode(p_reg_info, addr, pval, size);
        if (ret != 0) {
            DEBUG_ERROR("wr fail, ret: %d\n", ret);
            return -EFAULT;
        }
        DEBUG_INFO("write: addr: 0x%x, width: 0x%zx, wr_val: 0x%x\n", addr, size, buf);

        /* 5. unreset delay */
        DEBUG_INFO("dereset delay time: %u us\n", p_reg_info->dereset_delay);
        usleep_range(p_reg_info->dereset_delay + 1, p_reg_info->dereset_delay + 2);
    }

    return 0;
}

static int do_resume_by_op_gpio(gpio_cfg_info_t *p_gpio_info)
{
    int ret;

    DEBUG_INFO("rst: gpio%u output %u level\n", p_gpio_info->gpio_num, p_gpio_info->active_level);
    ret = gpio_direction_output(p_gpio_info->gpio_num, p_gpio_info->active_level);
    if (ret != 0) {
        DEBUG_ERROR("gpio%u output %u fail, ret = %d\n", p_gpio_info->gpio_num, \
                     p_gpio_info->active_level, ret);
        return -EFAULT;
    }

    DEBUG_INFO("reset delay time: %u us\n", p_gpio_info->reset_delay);
    usleep_range(p_gpio_info->reset_delay + 1, p_gpio_info->reset_delay + 2);

    DEBUG_INFO("derst: gpio%u output %u level\n", p_gpio_info->gpio_num, !p_gpio_info->active_level);
    ret = gpio_direction_output(p_gpio_info->gpio_num, !p_gpio_info->active_level);
    if (ret != 0) {
        DEBUG_ERROR("gpio%u output %u fail, ret = %d\n", p_gpio_info->gpio_num, \
                     !p_gpio_info->active_level, ret);
        return -EFAULT;
    }

    DEBUG_INFO("dereset delay time: %u us\n", p_gpio_info->dereset_delay);
    usleep_range(p_gpio_info->reset_delay + 1, p_gpio_info->reset_delay + 2);

    return 0;
}

static dev_resume_info_t* get_dev_resume_info(u32 dev_type, u32 slot_id)
{
    struct list_head *n, *pos;
    dev_resume_info_t *p_dev_resume_info;
    
    spin_lock(&dev_resume_info_list_lock);
    list_for_each_safe(pos, n, &dev_resume_info_list) {
        p_dev_resume_info = list_entry(pos, dev_resume_info_t, list);
        DEBUG_INFO("dev_type: %u, slot_id: %u\n", p_dev_resume_info->dev_type, p_dev_resume_info->slot_id); 
        if ((p_dev_resume_info->dev_type == dev_type) && (p_dev_resume_info->slot_id == slot_id)) {
            spin_unlock(&dev_resume_info_list_lock);
            return p_dev_resume_info;
        }
    }
    spin_unlock(&dev_resume_info_list_lock);

    return NULL;
}

static int c3000_mmc_pwr_resume_by_op_reg(reg_cfg_info_t *p_reg_info)
{
    struct pci_dev *pcidev;
    void __iomem *mmio_addr;
    unsigned long len;
    u32 vid, did;
    int i, ret;
    u32 *saved_reg_info;
    volatile void __iomem *addr;
    u32 reg_num, reg_val;
    static struct mutex lock;
    u32 reg_addr_arr[] = {0xc50728, 0xc5072c, 0xc50738, 0xc5073c,    /* reg：pad_cfg_dw0/1_emmc_cmd/clk */
                          0xc50740, 0xc50744, 0xc50748, 0xc5074c,    /* reg：pad_cfg_dw0/1_emmc_d0-d7 */
                          0xc50750, 0xc50754, 0xc50758, 0xc5075c,
                          0xc50760, 0xc50764, 0xc50768, 0xc5076c,
                          0xc50770, 0xc50774, 0xc50778, 0xc5077c, };

    DEBUG_VERBOSE("start\n");

    vid = C3000_PS2B_PCIE_DEV_VID;
    did = C3000_PS2B_PCIE_DEV_DID;
    pcidev = pci_get_device(vid, did, NULL);
    if (pcidev == NULL) {
        DEBUG_ERROR("get pci dev fail, vid 0x%x, did 0x%x\n", vid, did);
        return -ENODEV;
    }

    len = pci_resource_len(pcidev, 0);
    mmio_addr = pcim_iomap(pcidev, 0, len);
    DEBUG_INFO("mmio_addr = 0x%p, len = 0x%lx\n", mmio_addr, len);
    if (mmio_addr == NULL) {
        DEBUG_ERROR("remap fail, bar0, len: 0x%lx\n", len);
        return -ENOMEM;
    }

    saved_reg_info = kzalloc(sizeof(reg_addr_arr), GFP_KERNEL);
    if (saved_reg_info == NULL) {
        DEBUG_ERROR("kzmalloc fail, size: 0x%zx\n", sizeof(reg_addr_arr));
        pcim_iounmap(pcidev, mmio_addr);
        return -ENOMEM;
    }

    mutex_init(&lock);
    mutex_lock(&lock);

    reg_num = ARRAY_SIZE(reg_addr_arr);
    for (i = 0; i < reg_num; i++) {
        addr = mmio_addr + reg_addr_arr[i];
        saved_reg_info[i] = readl(addr);
        DEBUG_INFO("r addr: 0x%p, info[0]= 0x%x\n", addr, saved_reg_info[i]);
    }

    for (i = 0; i < reg_num; i++) {
        if (i % 2 == 0) {
            reg_val = saved_reg_info[i] & (~(GPIO_RX_DIS_BITS | PAD_MODE_BITS));
        } else {
            reg_val = saved_reg_info[i] & (~PAD_TERM_BITS);
        }
        addr = mmio_addr + reg_addr_arr[i];
        writel(reg_val, addr);
        DEBUG_INFO("w addr: 0x%p, val: [%d]= 0x%x\n", addr, i, reg_val);
    }

    ret = do_resume_by_op_reg(p_reg_info);
    if (ret != 0) {
        DEBUG_ERROR("resume by operate reg fail, ret: %d\n", ret);
        ret = -EIO;
    }

    for (i = 0; i < reg_num; i++) {
        addr = mmio_addr + reg_addr_arr[i];
        reg_val = saved_reg_info[i];
        writel(reg_val, addr);
        DEBUG_INFO("w addr: 0x%p, val: [%d]= 0x%x\n", addr, i, reg_val);
    }

    mutex_unlock(&lock);

    kfree(saved_reg_info);
    pcim_iounmap(pcidev, mmio_addr);

    DEBUG_VERBOSE("end\n");
    return ret;
}

static int dev_resume_only_by_op_reg(reg_cfg_info_t *p_reg_info)
{
    int ret;

    DEBUG_VERBOSE("start\n");

    ret = do_resume_by_op_reg(p_reg_info);
    if (ret != 0) {
        DEBUG_ERROR("resume by operate reg fail, ret: %d\n", ret);
        return -EIO;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}

static int dev_resume_only_by_op_gpio(gpio_cfg_info_t *p_gpio_info)
{
    int ret;

    DEBUG_VERBOSE("start\n");

    ret = do_resume_by_op_gpio(p_gpio_info);
    if (ret != 0) {
        DEBUG_ERROR("resume by operate gpio fail, ret: %d\n", ret);
        return -EIO;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}


/************************** start： Externally registered interface **********************************/
static int mmc_resume(u32 dev_type, u32 slot_id)
{
    dev_resume_info_t *p_dev_resume_info;
    mmc_cfg_info_t *p_mmc_cfg_info;
    int i, ret;
    ulong bit_mask;

    DEBUG("start\n");
    DEBUG("dev_type: %u, slot_id: %u\n", dev_type, slot_id); 

    /* 1. Interrupt context stack trace alert notification. */
    WARN(in_interrupt(), "should not used in interrupt context\n");

    /* 2. Obtain device recovery information. */
    p_dev_resume_info = get_dev_resume_info(dev_type, slot_id);
    if (p_dev_resume_info == NULL) {
        DEBUG_ERROR("dev info is not existed\n");
        return -EEXIST;
    }

    /* 3. Traverse the bitmask of recovery methods to determine which recovery methods need to be executed, and bind the recovery methods to specific recovery interfaces. */
    bit_mask = p_dev_resume_info->bit_mask;
    for_each_set_bit(i, &bit_mask, RESUME_WAY_MAX_NUM) {
        DEBUG_INFO("i = %d\n", i);
        p_mmc_cfg_info = &p_dev_resume_info->dev_cfg_info.mmc_cfg_info[i];

        DEBUG_INFO("resume way = %u\n", p_mmc_cfg_info->resume_way);
        switch (p_mmc_cfg_info->resume_way) {
        case DEV_RESUME_WAY1_WR_REG:
            ret = c3000_mmc_pwr_resume_by_op_reg(&p_mmc_cfg_info->info.reg_info);
            if (ret != 0) {
                DEBUG_ERROR("mmc pwr resume fail, ret = %d\n", ret);
                return -EIO;
            }
            DEBUG_INFO("mmc pwr resume complete\n");
            
            break;
        case DEV_RESUME_WAY2_WR_REG:
            ret = dev_resume_only_by_op_reg(&p_mmc_cfg_info->info.reg_info);
            if (ret != 0) {
                DEBUG_ERROR("mmc rst resume fail, ret = %d\n", ret);
                return -EIO;
            }
            DEBUG_INFO("mmc rst resume complete\n");
            
            break;

        case DEV_RESUME_WAY2_CTL_GPIO:
            ret = dev_resume_only_by_op_gpio(&p_mmc_cfg_info->info.gpio_info);
            if (ret != 0) {
                DEBUG_ERROR("mmc gpio rst resume fail, ret = %d\n", ret);
                return -EIO;
            }
            DEBUG_INFO("mmc gpio resume complete\n");

            break;
            
        default:
            DEBUG_INFO("unachieved resume way: %u\n", p_mmc_cfg_info->resume_way);
        }
    }

    DEBUG("end\n");
    return 0;
}

static int ssd_resume(u32 dev_type, u32 slot_id)
{
    dev_resume_info_t *p_dev_resume_info;
    ssd_cfg_info_t *p_ssd_cfg_info;
    int i, ret;
    ulong bit_mask;

    DEBUG("start\n");
    DEBUG("dev_type: %u, slot_id: %u\n", dev_type, slot_id); 

    /* 1. Interrupt context stack trace alert notification. */
    WARN(in_interrupt(), "should not used in interrupt context\n");

    /* 2. Obtain device recovery information. */
    p_dev_resume_info = get_dev_resume_info(dev_type, slot_id);
    if (p_dev_resume_info == NULL) {
        DEBUG_ERROR("dev info is not existed\n");
        return -EEXIST;
    }

     /* 3. Traverse the bitmask of recovery methods to determine which recovery methods need to be executed, and bind the recovery methods to specific recovery interfaces. */
    bit_mask = p_dev_resume_info->bit_mask;
    for_each_set_bit(i, &bit_mask, RESUME_WAY_MAX_NUM) {
        DEBUG_INFO("i = %d\n", i);
        p_ssd_cfg_info = &p_dev_resume_info->dev_cfg_info.ssd_cfg_info[i];

        DEBUG_INFO("resume way = %u\n", p_ssd_cfg_info->resume_way);
        switch (p_ssd_cfg_info->resume_way) {
        case DEV_RESUME_WAY2_WR_REG:
            ret = dev_resume_only_by_op_reg(&p_ssd_cfg_info->info.reg_info);
            if (ret != 0) {
                DEBUG_ERROR("ssd reg power reset resume fail, ret = %d\n", ret);
                return -EIO;
            }
            DEBUG_INFO("ssd reg power reset complete\n");
            
            break;

        default:
            DEBUG_INFO("unachieved resume way: %u\n", p_ssd_cfg_info->resume_way);
        }
    }

    DEBUG("end\n");
    return 0;
}

static int eusb_resume(u32 dev_type, u32 slot_id)
{
    dev_resume_info_t *p_dev_resume_info;
    eusb_cfg_info_t *p_eusb_cfg_info;
    int i, ret;
    ulong bit_mask;

    DEBUG("start\n");
    DEBUG("dev_type: %u, slot_id: %u\n", dev_type, slot_id); 

    /* 1. Interrupt context stack trace alert notification. */
    WARN(in_interrupt(), "should not used in interrupt context\n");

    /* 2. Obtain device recovery information. */
    p_dev_resume_info = get_dev_resume_info(dev_type, slot_id);
    if (p_dev_resume_info == NULL) {
        DEBUG_ERROR("dev info is not existed\n");
        return -EEXIST;
    }

     /* 3. Traverse the bitmask of recovery methods to determine which recovery methods need to be executed, and bind the recovery methods to specific recovery interfaces. */
    bit_mask = p_dev_resume_info->bit_mask;
    for_each_set_bit(i, &bit_mask, RESUME_WAY_MAX_NUM) {
        DEBUG_INFO("i = %d\n", i);
        p_eusb_cfg_info = &p_dev_resume_info->dev_cfg_info.eusb_cfg_info[i];

        DEBUG_INFO("resume way = %u\n", p_eusb_cfg_info->resume_way);
        switch (p_eusb_cfg_info->resume_way) {
        case DEV_RESUME_WAY2_WR_REG:
            ret = dev_resume_only_by_op_reg(&p_eusb_cfg_info->info.reg_info);
            if (ret != 0) {
                DEBUG_ERROR("eusb reg power reset resume fail, ret = %d\n", ret);
                return -EIO;
            }
            DEBUG_INFO("eusb reg power reset complete\n");
            
            break;

        default:
            DEBUG_INFO("unachieved resume way: %u\n", p_eusb_cfg_info->resume_way);
        }
    }

    DEBUG("end\n");
    return 0;
}
/************************** end： Externally registered interface **********************************/

static int mmc_resume_info_init(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    struct device_node *child;
    int i, ret;
    reg_cfg_info_t *p_reg_info;
    gpio_cfg_info_t *p_gpio_info;
    mmc_cfg_info_t *p_mmc_cfg_info;
    u32 resume_way;
    u32 width;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);

    /* 1. Traverse all recovery methods of the device and initialize the corresponding device recovery configuration information. */
    i = 0;
    for_each_child_of_node(pdev->dev.of_node, child) {
        /* 1.1 Obtain the recovery methods of the device and assess their validity. */
        resume_way = 0;
        ret = of_property_read_u32(child, "resume_way", &resume_way);
        DEBUG_INFO("i:%d, resume_way: %u\n", i, resume_way);
        if (ret != 0) {
            dev_err(&pdev->dev, "parse resume_way fail\n");
            return -EINVAL;
        }

        if (resume_way >= DEV_RESUME_WAYX_END) {
            dev_err(&pdev->dev, "resume_way: %u is invalid\n", resume_way);
            return -EINVAL;
        }

        /* 1.2 Obtain the MMC configuration information and initialize it */
        p_mmc_cfg_info = &p_dev_resume_info->dev_cfg_info.mmc_cfg_info[i];
        p_mmc_cfg_info->resume_way = resume_way;
        
        /* 1.3 Based on the recovery methods, fill in the necessary configuration information for the corresponding MMC recovery methods. */
        switch (resume_way) {
        case DEV_RESUME_WAY1_WR_REG:
        case DEV_RESUME_WAY2_WR_REG:
            /* 1.3.1 Parse the essential information */
            p_reg_info = &p_mmc_cfg_info->info.reg_info;
            ret  = of_property_read_u32(child, "reg_addr",      &p_reg_info->reg_addr);
            ret |= of_property_read_u32(child, "reg_width",     &p_reg_info->reg_width);
            ret |= of_property_read_u32(child, "access_mode",   &p_reg_info->access_mode);
            DEBUG_INFO("access_mode: %u, addr: 0x%x, width: %u", p_reg_info->access_mode, 
                        p_reg_info->reg_addr, p_reg_info->reg_width);

            ret |= of_property_read_u32(child, "reset_val",     &p_reg_info->reset_val);
            ret |= of_property_read_u32(child, "dereset_val",   &p_reg_info->dereset_val);
            ret |= of_property_read_u32(child, "reset_mask",    &p_reg_info->reset_mask);
            ret |= of_property_read_u32(child, "reset_delay",   &p_reg_info->reset_delay);
            ret |= of_property_read_u32(child, "dereset_delay", &p_reg_info->dereset_delay);
            DEBUG_INFO("rst_val: 0x%x, derst_val: 0x%x, mask: 0x%x, rst_delay: %u, " \
                       "derst_delay: %u, ret: %d\n", 
                        p_reg_info->reset_val, p_reg_info->dereset_val, p_reg_info->reset_mask, 
                        p_reg_info->reset_delay, p_reg_info->dereset_delay,  ret);

            if (ret != 0) {
                dev_err(&pdev->dev, "parse dts prop fail, ret = %d\n", ret);
                return -EFAULT;
            }

            /* 1.3.2 Parse the optional information */
            p_reg_info->dev_file_path = NULL;
            p_reg_info->map_base_addr = 0;
            p_reg_info->is_dereset = 1;
            (void)of_property_read_string(child, "dev_file_path", &p_reg_info->dev_file_path);
            (void)of_property_read_u64(child,    "map_base_addr", &p_reg_info->map_base_addr);
            (void)of_property_read_u32(child,    "is_dereset",    &p_reg_info->is_dereset);

            /* 1.3.2 Validity check */
            if (p_reg_info->access_mode >= ACCESS_MODE_END) {
                dev_err(&pdev->dev, "access_mode: %u is invalid\n", p_reg_info->access_mode);
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_DEV_FILE) && 
                (p_reg_info->dev_file_path == NULL)) {
                dev_err(&pdev->dev, "invalid dev file name\n");
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_MEM) && 
                (p_reg_info->map_base_addr == 0)) {
                dev_err(&pdev->dev, "invalid map base addr\n");
                return -EFAULT;
            }

            width = p_reg_info->reg_width;
            if ((width != 4) && (width != 2) && (width != 1)) {
                DEBUG_ERROR("invalid reg width: %u\n", width);
                return -EFAULT;
            }

            break;
        case DEV_RESUME_WAY2_CTL_GPIO:
            p_gpio_info = &p_mmc_cfg_info->info.gpio_info;
            ret  = of_property_read_u32(child, "gpio_num",      &p_gpio_info->gpio_num);
            ret |= of_property_read_u32(child, "active_level",  &p_gpio_info->active_level);
            ret |= of_property_read_u32(child, "reset_delay",   &p_gpio_info->reset_delay);
            ret |= of_property_read_u32(child, "dereset_delay", &p_gpio_info->dereset_delay);
            DEBUG_INFO("gpio_num: %u, active_level: %u, reset_delay: %u, dereset_delay: %u\n",      \
                        p_gpio_info->gpio_num, p_gpio_info->active_level, p_gpio_info->reset_delay, \
                        p_gpio_info->dereset_delay);
            if (ret != 0) {
                dev_err(&pdev->dev, "@ parse dts prop fail, ret = %d\n", ret);
                return -EFAULT;
            }

            ret= gpio_request(p_gpio_info->gpio_num, "mmc_rst_gpio");
            if (ret != 0) {
                dev_err(&pdev->dev, "gpio%u request fail, ret = %d\n", p_gpio_info->gpio_num, ret);
                return -EFAULT;
            }
            
            ret = gpio_direction_output(p_gpio_info->gpio_num, !p_gpio_info->active_level);
            if (ret != 0) {
                gpio_free(p_gpio_info->gpio_num);
                dev_err(&pdev->dev, "gpio%u output %u fail, ret = %d\n", p_gpio_info->gpio_num, \
                        !p_gpio_info->active_level, ret);
                return -EFAULT;
            }

            break;
        default:
            dev_err(&pdev->dev, "unknown mmc resume type: %u\n", resume_way);
            return -EFAULT;
        }

        i++;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}

static void mmc_resume_info_deinit(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    gpio_cfg_info_t *p_gpio_info;
    mmc_cfg_info_t *p_mmc_cfg_info;
    u32 resume_way;
    int i;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);

    DEBUG_INFO("resume_way_num: %u\n", p_dev_resume_info->resume_way_num);
    for (i = 0; i < p_dev_resume_info->resume_way_num; i++) {
        p_mmc_cfg_info = &p_dev_resume_info->dev_cfg_info.mmc_cfg_info[i];
        p_gpio_info = &p_mmc_cfg_info->info.gpio_info;
        resume_way =  p_mmc_cfg_info->resume_way;
        DEBUG_INFO("i: %d, resume_way: %u, gpio_num: %u\n", i, resume_way, p_gpio_info->gpio_num);
        switch (resume_way) {
        case DEV_RESUME_WAY2_CTL_GPIO:
            gpio_free(p_gpio_info->gpio_num);
            break;

        default:
            DEBUG_INFO("no need deinit's resume way: %u\n", resume_way);
        }
    }

    DEBUG_VERBOSE("end\n");
    return;
}


static int ssd_resume_info_init(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    struct device_node *child;
    int i, ret;
    reg_cfg_info_t *p_reg_info;
    ssd_cfg_info_t *p_ssd_cfg_info;
    u32 resume_way;
    u32 width;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);

     /* 1. Traverse all recovery methods of the device and initialize the corresponding device recovery configuration information. */
    i = 0;
    for_each_child_of_node(pdev->dev.of_node, child) {
        /* 1.1 Obtain the recovery methods of the device and assess their validity. */
        resume_way = 0;
        ret = of_property_read_u32(child, "resume_way", &resume_way);
        DEBUG_INFO("i:%d, resume_way: %u\n", i, resume_way);
        if (ret != 0) {
            dev_err(&pdev->dev, "parse resume_way fail\n");
            return -EINVAL;
        }

        if (resume_way >= DEV_RESUME_WAYX_END) {
            dev_err(&pdev->dev, "resume_way: %u is invalid\n", resume_way);
            return -EINVAL;
        }

       /* 1.2 Obtain the SSD configuration information and initialize it */
        p_ssd_cfg_info = &p_dev_resume_info->dev_cfg_info.ssd_cfg_info[i];
        p_ssd_cfg_info->resume_way = resume_way;
        
         /* 1.3 Based on the recovery methods, fill in the necessary configuration information for the corresponding SSD recovery methods. */
        switch (resume_way) {
        case DEV_RESUME_WAY1_WR_REG:
        case DEV_RESUME_WAY2_WR_REG:
            /* 1.3.1 Parse the essential information */
            p_reg_info = &p_ssd_cfg_info->info.reg_info;
            ret  = of_property_read_u32(child, "reg_addr",      &p_reg_info->reg_addr);
            ret |= of_property_read_u32(child, "reg_width",     &p_reg_info->reg_width);
            ret |= of_property_read_u32(child, "access_mode",   &p_reg_info->access_mode);
            DEBUG_INFO("access_mode: %u, addr: 0x%x, width: %u", p_reg_info->access_mode, 
                        p_reg_info->reg_addr, p_reg_info->reg_width);

            ret |= of_property_read_u32(child, "reset_val",     &p_reg_info->reset_val);
            ret |= of_property_read_u32(child, "dereset_val",   &p_reg_info->dereset_val);
            ret |= of_property_read_u32(child, "reset_mask",    &p_reg_info->reset_mask);
            ret |= of_property_read_u32(child, "reset_delay",   &p_reg_info->reset_delay);
            ret |= of_property_read_u32(child, "dereset_delay", &p_reg_info->dereset_delay);
            DEBUG_INFO("rst_val: 0x%x, derst_val: 0x%x, mask: 0x%x, rst_delay: %u, " \
                       "derst_delay: %u, ret: %d\n", 
                        p_reg_info->reset_val, p_reg_info->dereset_val, p_reg_info->reset_mask, 
                        p_reg_info->reset_delay, p_reg_info->dereset_delay,  ret);

            if (ret != 0) {
                dev_err(&pdev->dev, "parse dts prop fail, ret = %d\n", ret);
                return -EFAULT;
            }

            /* 1.3.2 Parse the optional information */
            p_reg_info->dev_file_path = NULL;
            p_reg_info->map_base_addr = 0;
            p_reg_info->is_dereset = 1;
            (void)of_property_read_string(child, "dev_file_path", &p_reg_info->dev_file_path);
            (void)of_property_read_u64(child,    "map_base_addr", &p_reg_info->map_base_addr);
            (void)of_property_read_u32(child,    "is_dereset",    &p_reg_info->is_dereset);

            /* 1.3.2 Validity check */
            if (p_reg_info->access_mode >= ACCESS_MODE_END) {
                dev_err(&pdev->dev, "access_mode: %u is invalid\n", p_reg_info->access_mode);
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_DEV_FILE) && 
                (p_reg_info->dev_file_path == NULL)) {
                dev_err(&pdev->dev, "invalid dev file name\n");
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_MEM) && 
                (p_reg_info->map_base_addr == 0)) {
                dev_err(&pdev->dev, "invalid map base addr\n");
                return -EFAULT;
            }

            width = p_reg_info->reg_width;
            if ((width != 4) && (width != 2) && (width != 1)) {
                DEBUG_ERROR("invalid reg width: %u\n", width);
                return -EFAULT;
            }

            break;
        case DEV_RESUME_WAY2_CTL_GPIO:
            /* reserve for future */
            break;
        default:
            dev_err(&pdev->dev, "unknown ssd resume type: %u\n", resume_way);
            return -EFAULT;
        }

        i++;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}

static int eusb_resume_info_init(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    struct device_node *child;
    int i, ret;
    reg_cfg_info_t *p_reg_info;
    eusb_cfg_info_t *p_eusb_cfg_info;
    u32 resume_way;
    u32 width;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);

    /* 1. Traverse all recovery methods of the device and initialize the corresponding device recovery configuration information. */
    i = 0;
    for_each_child_of_node(pdev->dev.of_node, child) {
        /* 1.1 Obtain the recovery methods of the device and assess their validity. */
        resume_way = 0;
        ret = of_property_read_u32(child, "resume_way", &resume_way);
        DEBUG_INFO("i:%d, resume_way: %u\n", i, resume_way);
        if (ret != 0) {
            dev_err(&pdev->dev, "parse resume_way fail\n");
            return -EINVAL;
        }

        if (resume_way >= DEV_RESUME_WAYX_END) {
            dev_err(&pdev->dev, "resume_way: %u is invalid\n", resume_way);
            return -EINVAL;
        }

        /* 1.2 Obtain the eusb configuration information and initialize it */
        p_eusb_cfg_info = &p_dev_resume_info->dev_cfg_info.eusb_cfg_info[i];
        p_eusb_cfg_info->resume_way = resume_way;
        
        /* 1.3 Based on the recovery methods, fill in the necessary configuration information for the corresponding eusb recovery methods. */
        switch (resume_way) {
        case DEV_RESUME_WAY1_WR_REG:
        case DEV_RESUME_WAY2_WR_REG:
            /* 1.3.1 Parse the essential information */
            p_reg_info = &p_eusb_cfg_info->info.reg_info;
            ret  = of_property_read_u32(child, "reg_addr",      &p_reg_info->reg_addr);
            ret |= of_property_read_u32(child, "reg_width",     &p_reg_info->reg_width);
            ret |= of_property_read_u32(child, "access_mode",   &p_reg_info->access_mode);
            DEBUG_INFO("access_mode: %u, addr: 0x%x, width: %u", p_reg_info->access_mode, 
                        p_reg_info->reg_addr, p_reg_info->reg_width);

            ret |= of_property_read_u32(child, "reset_val",     &p_reg_info->reset_val);
            ret |= of_property_read_u32(child, "dereset_val",   &p_reg_info->dereset_val);
            ret |= of_property_read_u32(child, "reset_mask",    &p_reg_info->reset_mask);
            ret |= of_property_read_u32(child, "reset_delay",   &p_reg_info->reset_delay);
            ret |= of_property_read_u32(child, "dereset_delay", &p_reg_info->dereset_delay);
            DEBUG_INFO("rst_val: 0x%x, derst_val: 0x%x, mask: 0x%x, rst_delay: %u, " \
                       "derst_delay: %u, ret: %d\n", 
                        p_reg_info->reset_val, p_reg_info->dereset_val, p_reg_info->reset_mask, 
                        p_reg_info->reset_delay, p_reg_info->dereset_delay,  ret);

            if (ret != 0) {
                dev_err(&pdev->dev, "parse dts prop fail, ret = %d\n", ret);
                return -EFAULT;
            }

            /* 1.3.2 Parse the optional information */
            p_reg_info->dev_file_path = NULL;
            p_reg_info->map_base_addr = 0;
            p_reg_info->is_dereset = 1;
            (void)of_property_read_string(child, "dev_file_path", &p_reg_info->dev_file_path);
            (void)of_property_read_u64(child,    "map_base_addr", &p_reg_info->map_base_addr);
            (void)of_property_read_u32(child,    "is_dereset",    &p_reg_info->is_dereset);

            /* 1.3.2 Validity check */
            if (p_reg_info->access_mode >= ACCESS_MODE_END) {
                dev_err(&pdev->dev, "access_mode: %u is invalid\n", p_reg_info->access_mode);
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_DEV_FILE) && 
                (p_reg_info->dev_file_path == NULL)) {
                dev_err(&pdev->dev, "invalid dev file name\n");
                return -EFAULT;
            }

            if ((p_reg_info->access_mode == ACCESS_MODE_MEM) && 
                (p_reg_info->map_base_addr == 0)) {
                dev_err(&pdev->dev, "invalid map base addr\n");
                return -EFAULT;
            }

            width = p_reg_info->reg_width;
            if ((width != 4) && (width != 2) && (width != 1)) {
                DEBUG_ERROR("invalid reg width: %u\n", width);
                return -EFAULT;
            }

            break;
        case DEV_RESUME_WAY2_CTL_GPIO:
            /* reserve for future */
            break;
        default:
            dev_err(&pdev->dev, "unknown eusb resume type: %u\n", resume_way);
            return -EFAULT;
        }

        i++;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}

static void ssd_resume_info_deinit(struct platform_device *pdev)
{
    /* reserve for future */
    return;
}

static void eusb_resume_info_deinit(struct platform_device *pdev)
{
    /* reserve for future */
    return;
}

static int dev_resume_info_init(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    int ret;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);
    DEBUG_INFO("dev_type: %u\n", p_dev_resume_info->dev_type);

    switch (p_dev_resume_info->dev_type) {
    case DEV_TYPE_MMC:
        ret = mmc_resume_info_init(pdev);
        if (ret != 0) {
            dev_err(&pdev->dev, "mmc resume info init fail, ret = %d\n", ret);
            return -EFAULT;
        }
        break;
    case DEV_TYPE_SSD:
        ret = ssd_resume_info_init(pdev);
        if (ret != 0) {
            dev_err(&pdev->dev, "ssd resume info init fail, ret = %d\n", ret);
            return -EFAULT;
        }

        break;
    case DEV_TYPE_EUSB:
        ret = eusb_resume_info_init(pdev);
        if (ret != 0) {
            dev_err(&pdev->dev, "eusb resume info init fail, ret = %d\n", ret);
            return -EFAULT;
        }

        break;
    default:
        dev_err(&pdev->dev, "unknown dev type: %u\n", p_dev_resume_info->dev_type);
        return -EFAULT;
    }

    DEBUG_VERBOSE("end\n");
    return 0;
}

static void dev_resume_info_deinit(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);
    DEBUG_INFO("dev_type: %u\n", p_dev_resume_info->dev_type);

    switch (p_dev_resume_info->dev_type) {
    case DEV_TYPE_MMC:
        mmc_resume_info_deinit(pdev);
        break;

    case DEV_TYPE_SSD:
        ssd_resume_info_deinit(pdev);
        break;
    
    case DEV_TYPE_EUSB:
        eusb_resume_info_deinit(pdev);
        break;
    default:
        dev_err(&pdev->dev, "@ unknown dev type: %u\n", p_dev_resume_info->dev_type);
    }

    DEBUG_VERBOSE("end\n");
    return;
}


static int reg_intf_accord_to_dev_type(struct platform_device *pdev)
{
    int ret;
    dev_resume_info_t *p_dev_resume_info;
    reg_dev_resume_func_t pfunc;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);
    DEBUG_INFO("dev_type: %u, reg_func: %s\n", \
                p_dev_resume_info->dev_type, p_dev_resume_info->reg_intf_name);

    pfunc = (reg_dev_resume_func_t)p_dev_resume_info->reg_intf_addr;
    switch (p_dev_resume_info->dev_type) {
    case DEV_TYPE_MMC:
        ret = pfunc((dev_resume_func_t)mmc_resume);
        if (ret != 0) {
            dev_err(&pdev->dev, "reg mmc resume intf fail, ret: %d, \n", ret);
            return -EFAULT;
        }
        
        break;
    case DEV_TYPE_SSD:
        ret = pfunc((dev_resume_func_t)ssd_resume);
        if (ret != 0) {
            dev_err(&pdev->dev, "reg ssd resume intf fail, ret: %d, \n", ret);
            return -EFAULT;
        }

        break;
    case DEV_TYPE_EUSB:
        ret = pfunc((dev_resume_func_t)eusb_resume);
        if (ret != 0) {
            dev_err(&pdev->dev, "reg eusb resume intf fail, ret: %d, \n", ret);
            return -EFAULT;
        }

        break;
    default:
        dev_err(&pdev->dev, "unknown dev type: %u\n", p_dev_resume_info->dev_type);
        return -EFAULT;
    }


    DEBUG_VERBOSE("end\n");
    return 0;
}

static int unreg_intf(struct platform_device *pdev)
{
    int ret;
    dev_resume_info_t *p_dev_resume_info;
    unreg_dev_resume_func_t pfunc;

    p_dev_resume_info = platform_get_drvdata(pdev);
    DEBUG_INFO("unreg_func: %s\n", p_dev_resume_info->unreg_intf_name);

    pfunc = (unreg_dev_resume_func_t)p_dev_resume_info->unreg_intf_addr;
    ret = pfunc();
    if (ret != 0) {
        dev_err(&pdev->dev, "unreg intf: %s fail, ret: %d, \n", p_dev_resume_info->unreg_intf_name, ret);
        return -EFAULT;
    }

    return 0;
}

/********************************* start: sysfs-test ****************************************/
static ssize_t wb_show_resume_bit_mask(struct device *dev, struct device_attribute *attr, char *buf)
{
    dev_resume_info_t *p_info;
    ssize_t size;

    p_info = (dev_resume_info_t *)dev_get_drvdata(dev);
    DEBUG_INFO("p_info: 0x%p, dev_type: %u, slot_id: %u\n", p_info, p_info->dev_type, p_info->slot_id);

    size = snprintf(buf, PAGE_SIZE, "dev_type: %u, slot_id: %u, bit_mask: 0x%x\n", \
                                     p_info->dev_type, p_info->slot_id, p_info->bit_mask);

    return size;
}

static ssize_t wb_set_resume_bit_mask(struct device *dev, struct device_attribute *attr,
                                             const char *buf, size_t count)
{
    dev_resume_info_t *p_info;

    if (count == 0) {
        DEBUG_ERROR("input is null\n");
        return -EINVAL;
    }

    p_info = (dev_resume_info_t *)dev_get_drvdata(dev);
    DEBUG_INFO("p_info: 0x%p, dev_type: %u, slot_id: %u\n", p_info, p_info->dev_type, p_info->slot_id);

    DEBUG_INFO("current bit_mask: 0x%x\n", p_info->bit_mask);
    p_info->bit_mask = (u32)simple_strtoul(buf, NULL, 0);
    DEBUG_INFO("setted bit_mask: 0x%x\n", p_info->bit_mask);
    
    return count;
}

/* Used to test the external exception recovery interface */
static ssize_t wb_resume_intf_test(struct device *dev, struct device_attribute *attr, char *buf)
{
    dev_resume_info_t *p_info;
    ssize_t size;
    int ret;

    p_info = (dev_resume_info_t *)dev_get_drvdata(dev);
    DEBUG_INFO("p_info: 0x%p, dev_type: %u, slot_id: %u\n", p_info, p_info->dev_type, p_info->slot_id);

    switch(p_info->dev_type) {
    case DEV_TYPE_MMC:
        ret = mmc_resume(p_info->dev_type, p_info->slot_id);
        if (ret != 0) {
            DEBUG_ERROR("mmc_resume test fail, ret = %d\n", ret);
            size = snprintf(buf, PAGE_SIZE, "emmc interface test ........ fail\n");
            return size;
        }
        
        size = snprintf(buf, PAGE_SIZE, "emmc interface test ........ ok\n");
        return size;

    case DEV_TYPE_SSD:
        ret = ssd_resume(p_info->dev_type, p_info->slot_id);
        if (ret != 0) {
            DEBUG_ERROR("ssd_resume test fail, ret = %d\n", ret);
            size = snprintf(buf, PAGE_SIZE, "ssd interface test ........ fail\n");
            return size;
        }
        
        size = snprintf(buf, PAGE_SIZE, "ssd interface test ........ ok\n");
        return size;

    case DEV_TYPE_EUSB:
        ret = eusb_resume(p_info->dev_type, p_info->slot_id);
        if (ret != 0) {
            DEBUG_ERROR("eusb_resume test fail, ret = %d\n", ret);
            size = snprintf(buf, PAGE_SIZE, "eusb interface test ........ fail\n");
            return size;
        }
        
        size = snprintf(buf, PAGE_SIZE, "eusb interface test ........ ok\n");
        return size;

    default:
        DEBUG_ERROR("unknown dev type: %u\n", p_info->dev_type);
    }

    return 0;
}

static struct device_attribute dev_attr_resume_bit_mask;
static struct device_attribute dev_attr_resume_intf_test;

static DEVICE_ATTR(resume_bit_mask, S_IWUSR | S_IRUSR | S_IRGRP, \
                      wb_show_resume_bit_mask, wb_set_resume_bit_mask);
static DEVICE_ATTR(resume_intf_test, S_IWUSR | S_IRUSR | S_IRGRP, \
                      wb_resume_intf_test, NULL);

static struct attribute *dev_attrs[] = {
    &dev_attr_resume_bit_mask.attr,
    &dev_attr_resume_intf_test.attr,
    NULL,
};

static struct attribute_group dev_attr_group = {
    .attrs = dev_attrs,
};
/********************************* end： sysfs-test ****************************************/


static int dev_resume_probe(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info, *p_info;
    u32 dev_type, slot_id, resume_way_num, bit_mask;
    const char *reg_intf_name, *unreg_intf_name;
    unsigned long reg_intf_addr, unreg_intf_addr;
    int ret;

    DEBUG_VERBOSE("start\n");

    if (of_have_populated_dt() == 0) {
        dev_err(&pdev->dev, "unsupport dts parse\n");
        return -EFAULT;
    }

    dev_type = 0;
    slot_id  = 0;
    bit_mask = 0;
    reg_intf_name   = NULL;
	unreg_intf_name = NULL;
    ret  = of_property_read_u32(pdev->dev.of_node, "dev_type", &dev_type);
    ret |= of_property_read_u32(pdev->dev.of_node, "slot_id",  &slot_id);
    ret |= of_property_read_u32(pdev->dev.of_node, "bit_mask", &bit_mask);
    ret |= of_property_read_string(pdev->dev.of_node, "reg_intf_name", &reg_intf_name);
    ret |= of_property_read_string(pdev->dev.of_node, "unreg_intf_name", &unreg_intf_name);
    DEBUG_INFO("dev_type: %u, slot_id: %u, bit_mask: 0x%x, reg_intf_name: %s, "     \
               "unreg_intf_name: %s, ret = %d\n",                                   \
               dev_type, slot_id, bit_mask, reg_intf_name ? reg_intf_name : "null", \
               unreg_intf_name ? unreg_intf_name : "null", ret); 
    if (ret != 0) {
        dev_err(&pdev->dev, "read dts propert fail, ret = %d\n", ret);
        return -EFAULT;
    }

    if (dev_type >= DEV_TYPE_END) {
        dev_err(&pdev->dev, "dev_type is invalid, %u\n", dev_type);
        return -EINVAL;
    }

    if ((bit_mask == 0) || (bit_mask >= (1 << RESUME_WAY_MAX_NUM))) {
        dev_err(&pdev->dev, "bit_mask is invalid, %u\n", bit_mask);
        return -EINVAL;
    }

    reg_intf_addr = (unsigned long)kallsyms_lookup_name_fun(reg_intf_name);
    if (reg_intf_addr == 0) {
        dev_err(&pdev->dev, "reg_intf %s is not exist\n", reg_intf_name);
        return -EFAULT;
    }

    unreg_intf_addr = (unsigned long)kallsyms_lookup_name_fun(unreg_intf_name);
    if (unreg_intf_addr == 0) {
        dev_err(&pdev->dev, "unreg_intf %s is not exist\n", unreg_intf_name);
        return -EFAULT;
    }

    /* Confirm how many recovery methods are available for this device */
    resume_way_num = of_get_child_count(pdev->dev.of_node);
    DEBUG_INFO("resume_way_num: %u\n", resume_way_num);
    if ((resume_way_num == 0) || (resume_way_num >= RESUME_WAY_MAX_NUM)) {
        dev_err(&pdev->dev, "resume_way_num: %u is invalid\n", resume_way_num);
        return -EFAULT;
    }

    /* serach resume_info_list check if the device information already exists */
    spin_lock(&dev_resume_info_list_lock);
    list_for_each_entry(p_info, &dev_resume_info_list, list) {
        if ((p_info->dev_type == dev_type) && (p_info->slot_id == slot_id)) {
            dev_warn(&pdev->dev, "dev_type%u slot_id%u has already existed\n", dev_type, slot_id);
            spin_unlock(&dev_resume_info_list_lock);
            return -EFAULT;
        }
    }
    spin_unlock(&dev_resume_info_list_lock);

    p_dev_resume_info = devm_kzalloc(&pdev->dev, sizeof(dev_resume_info_t), GFP_KERNEL);
    if (!p_dev_resume_info) {
        dev_err(&pdev->dev, "alloc mem fail\n");
        return -ENOMEM;
    }
    DEBUG_INFO("p_dev_resume_info: 0x%p \n", p_dev_resume_info);

    platform_set_drvdata(pdev, p_dev_resume_info);
    p_dev_resume_info->dev_type   = dev_type;
    p_dev_resume_info->slot_id    = slot_id;
    p_dev_resume_info->bit_mask   = bit_mask;
    p_dev_resume_info->resume_way_num = resume_way_num;
    
    p_dev_resume_info->reg_intf_name   = reg_intf_name;
    p_dev_resume_info->reg_intf_addr   = reg_intf_addr;
    p_dev_resume_info->unreg_intf_name = unreg_intf_name;
    p_dev_resume_info->unreg_intf_addr = unreg_intf_addr;

    ret = dev_resume_info_init(pdev);
    if (ret != 0) {
        dev_err(&pdev->dev, "dev resume info init fail, ret = %d\n", ret);
        return -ENODEV;
    }

    ret = reg_intf_accord_to_dev_type(pdev);
    if (ret != 0) {
        dev_err(&pdev->dev, "reg intf fail, ret = %d\n", ret);
        return -ENODEV;
    }

    ret = sysfs_create_group(&pdev->dev.kobj, &dev_attr_group);
    if (ret != 0) {
        dev_err(&pdev->dev, "add sysfs prop fail, ret = %d\n", ret);
        return -ENODEV;
    }

    spin_lock(&dev_resume_info_list_lock);
    list_add_tail(&p_dev_resume_info->list, &dev_resume_info_list);
    spin_unlock(&dev_resume_info_list_lock);

    DEBUG_VERBOSE("end\n");
    return 0;
}

static int dev_resume_remove(struct platform_device *pdev)
{
    dev_resume_info_t *p_dev_resume_info;
    int ret;

    DEBUG_VERBOSE("start\n");

    p_dev_resume_info = platform_get_drvdata(pdev);

    spin_lock(&dev_resume_info_list_lock);
    list_del(&p_dev_resume_info->list);
    spin_unlock(&dev_resume_info_list_lock);

    sysfs_remove_group(&pdev->dev.kobj, &dev_attr_group);

    ret = unreg_intf(pdev);
    if (ret != 0) {
        dev_err(&pdev->dev, "unreg intf fail, ret = %d\n", ret);
        return -ENODEV;
    }

    dev_resume_info_deinit(pdev);

    DEBUG_VERBOSE("end\n");
    return 0;
}

static struct of_device_id dev_resume_of_match[] = {
    { .compatible = "dev_resume_drv", },
    { /* Sentinel */ }
};

static struct platform_driver dev_resume_pdrv = {
    .driver = {
        .name  = DRV_NAME,
        .owner = THIS_MODULE,
        .of_match_table = dev_resume_of_match,
    },
    .probe  = dev_resume_probe,
    .remove = dev_resume_remove,
};

static int __init wb_dev_resume_init(void)
{
    int ret;

    ret = find_kallsyms_lookup_name();
    if (ret < 0) {
        DEBUG_ERROR("find kallsyms_lookup_name failed\n");
        return -ENXIO;
    }
    DEBUG_INFO("find kallsyms_lookup_name ok\n");
    return platform_driver_register(&dev_resume_pdrv);
}

static void __exit wb_dev_resume_exit(void)
{
    platform_driver_unregister(&dev_resume_pdrv);
}

module_init(wb_dev_resume_init);
module_exit(wb_dev_resume_exit);

MODULE_AUTHOR("xxx");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("register a dev resumed interface to let dev escape from unexpected exceptions");


