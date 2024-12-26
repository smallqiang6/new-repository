/*
 *
 * wb_wdt.c
 * ko for watchdog function
 * Original Author: support 2020-09-28
 */

#include <linux/err.h>
#include <linux/delay.h>
#include <linux/module.h>
#include <linux/of_gpio.h>
#include <linux/platform_device.h>
#include <linux/watchdog.h>
#include <linux/hrtimer.h>
#include <asm/uaccess.h>
#include <linux/kthread.h>
#include <linux/mutex.h>
#include <linux/hwmon-sysfs.h>

#define GPIO_FEED_WDT_MODE   (1)
#define LOGIC_FEED_WDT_MODE  (2)

#define SYMBOL_I2C_DEV_MODE          (1)
#define SYMBOL_PCIE_DEV_MODE         (2)
#define SYMBOL_IO_DEV_MODE           (3)
#define FILE_MODE                    (4)
#define SYMBOL_PLATFORM_I2C_DEV_MODE (5)  /* Use the wb_platform_i2c_dev driver to export the logical device */

#define ONE_BYTE             (1)

#define WDT_OFF              (0)
#define WDT_ON               (1)
#define SYSFS_NO_CFG         (0xff)

#define MS_TO_S              (1000)
#define MS_TO_NS             (1000 * 1000)

#define MAX_REG_VAL          (255)

#define INVALID_REG_ADDR     (0xffffffff)
#define WB_RV_UNSUPPORT      999

extern int platform_i2c_device_func_read(const char *path, uint32_t offset, uint8_t *buf, size_t count);
extern int platform_i2c_device_func_write(const char *path, uint32_t offset, uint8_t *buf, size_t count);
extern int i2c_device_func_write(const char *path, uint32_t offset, uint8_t *buf, size_t count);
extern int i2c_device_func_read(const char *path, uint32_t offset, uint8_t *buf, size_t count);

int g_wb_wdt_debug = 0;
int g_wb_wdt_error = 0;

module_param(g_wb_wdt_debug, int, S_IRUGO | S_IWUSR);
module_param(g_wb_wdt_error, int, S_IRUGO | S_IWUSR);

#define WDT_VERBOSE(fmt, args...) do {                                        \
    if (g_wb_wdt_debug) { \
        printk(KERN_INFO "[WDT][VER][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

#define WDT_ERROR(fmt, args...) do {                                        \
    if (g_wb_wdt_error) { \
        printk(KERN_ERR "[WDT][ERR][func:%s line:%d]\n"fmt, __func__, __LINE__, ## args); \
    } \
} while (0)

enum {
    HW_ALGO_TOGGLE,
    HW_ALGO_LEVEL,
    HW_ALGO_EIGENVALUES,
};

enum {
    WATCHDOG_DEVICE_TYPE    = 0,
    HRTIMER_TYPE,
    THREAD_TYPE,
};

    /* Logic device to the dog */
typedef struct logic_wdt_info_s {
    const char  *feed_dev_name;  /* Name of the dog feeding logic device */
    uint8_t     logic_func_mode; /* 1:i2c, 2:pcie, 3:io, 4 Device file, 5:platform i2c */
    uint32_t    feed_reg;        /* Feed the dog register address */
    uint8_t     active_val;      /* 1: Write 1 to feed the dog, 0: write 0 to feed the dog */
    uint8_t     state_val;       /* Save feed dog valid value */
}logic_wdt_info_t;

/* GPIO feeds the dog */
typedef struct gpio_wdt_info_s {
    int       gpio;
    bool      active_low;
    bool      state;
}gpio_wdt_info_t;

typedef struct wb_wdt_priv_s {
    /* GPIO feeding dog and logic device feeding dog common variables */
    struct task_struct *thread;
    struct hrtimer hrtimer;
    ktime_t   m_kt;
    const char  *config_dev_name;   /* Configure the logical device name, including the enable and set time  */
    uint8_t     config_mode;        /* 1:gpio feed the dog, 2: logic device feed the dog */
    uint8_t     hw_algo;            /* 1:Flip feed dog, 2: level feed dog, 3: feature value feed dog */
    uint8_t     enable_val;         /* The valid value is enabled */
    uint8_t     disable_val;        /* The valid value is disabled */
    uint8_t     enable_mask;        /* Enable the mask */
    uint8_t     priv_func_mode;     /* 1:i2c, 2:pcie, 3:io, 4:device Files, 5:platform i2c */
    uint8_t     feed_wdt_type;      /* 0: does not feed the dog, 1:hrtimer feeds the dog, 2: threads feed the dog */
    uint32_t    enable_reg;         /* Enable register address */
    uint32_t    timeout_cfg_reg;    /* Timeout Sets the register address */
    uint32_t    hw_margin;          /* Timeout period */
    uint32_t    feed_time;          /* Dog feeding time */
    uint32_t    timer_accuracy;     /* Timer accuracy (time when cpld is configured with 1) */
    gpio_wdt_info_t     gpio_wdt;   /* gpio feeds the dog */
    logic_wdt_info_t    logic_wdt;  /* Logic device to the dog */
    struct device *dev;
    const struct attribute_group *sysfs_group;
    uint8_t sysfs_index;
    struct mutex update_lock;
    struct watchdog_device  wdd;
    uint32_t wdt_ready;
}wb_wdt_priv_t;

static int wdt_file_read(const char *path, uint32_t pos, uint8_t *val, size_t size)
{
    int ret;
    struct file *filp;
    loff_t tmp_pos;

    filp = filp_open(path, O_RDONLY, 0);
    if (IS_ERR(filp)) {
        WDT_ERROR("read open failed errno = %ld\n", -PTR_ERR(filp));
        filp = NULL;
        goto exit;
    }

    tmp_pos = (loff_t)pos;
    ret = kernel_read(filp, val, size, &tmp_pos);
    if (ret < 0) {
        WDT_ERROR("kernel_read failed, path=%s, addr=0x%x, size=%u, ret=%d\n", path, pos, size, ret);
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

static int wdt_file_write(const char *path, uint32_t pos, uint8_t *val, size_t size)
{
    int ret;
    struct file *filp;
    loff_t tmp_pos;

    filp = filp_open(path, O_RDWR, 777);
    if (IS_ERR(filp)) {
        WDT_ERROR("write open failed errno = %ld\n", -PTR_ERR(filp));
        filp = NULL;
        goto exit;
    }

    tmp_pos = (loff_t)pos;
    ret = kernel_write(filp, val, size, &tmp_pos);
    if (ret < 0) {
        WDT_ERROR("kernel_write failed, path=%s, addr=0x%x, size=%u, ret=%d\n", path, pos, size, ret);
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

static int wb_wdt_read(uint8_t mode, const char *path,
                uint32_t offset, uint8_t *buf, size_t count)
{
    int ret;

    switch (mode) {
    case SYMBOL_I2C_DEV_MODE:        /* Use i2c device driver mode */
        ret = i2c_device_func_read(path, offset, buf, count);
        break;
    case FILE_MODE:                  /* File access mode */
        ret = wdt_file_read(path, offset, buf, count);
        break;
    case SYMBOL_PLATFORM_I2C_DEV_MODE:
        ret = platform_i2c_device_func_read(path, offset, buf, count);
        break;
    default:
        WDT_ERROR("mode %u error, wdt func read failed.\n", mode);
        return -EINVAL;
    }

    WDT_VERBOSE("wdt func read mode:%u,dev_nam:%s, offset:0x%x, read_val:0x%x, size:%u.\n",
        mode, path, offset, *buf, count);

    return ret;
}

static int wb_wdt_write(uint8_t mode, const char *path,
                uint32_t offset, uint8_t *buf, size_t count)
{
    int ret;

    switch (mode) {
    case SYMBOL_I2C_DEV_MODE:        /* Use i2c device driver mode */
        ret = i2c_device_func_write(path, offset, buf, count);
        break;
    case FILE_MODE:                  /* File access mode */
        ret = wdt_file_write(path, offset, buf, count);
        break;
    case SYMBOL_PLATFORM_I2C_DEV_MODE:
        ret = platform_i2c_device_func_write(path, offset, buf, count);
        break;
    default:
        WDT_ERROR("mode %u error, wdt func write failed.\n", mode);
        return -EINVAL;
    }

    WDT_VERBOSE("wdt func write mode:%u, dev_nam:%s, offset:0x%x, write_val:0x%x, size:%u.\n",
        mode, path, offset, *buf, count);

    return ret;
}

static int wb_wdt_enable_ctrl(wb_wdt_priv_t *priv, uint8_t flag)
{
    int ret;
    uint8_t val;
    uint8_t ctrl_val;

    /* case: Can't not enable/disable WDT */
    if(priv->enable_reg == INVALID_REG_ADDR) {
        dev_dbg(priv->dev, "Can't not enable/disable WDT.\n");
        return 0;
    }

    /* Enable bit judgment and setting */
    switch (flag) {
    case WDT_ON:
        ctrl_val = priv->enable_val;
        break;
    case WDT_OFF:
        ctrl_val = priv->disable_val;
        break;
    default:
        WDT_ERROR("unsupport wdt enable ctrl:%u.\n", flag);
        return -EINVAL;
    }

    /* If wdt is enabled, read before write does not change the value of other bits */
    ret = wb_wdt_read(priv->priv_func_mode, priv->config_dev_name,
                priv->enable_reg, &val, ONE_BYTE);
    if (ret < 0) {
        dev_err(priv->dev, "read wdt control reg error.\n");
        return ret;
    }

    /* If wdt is enabled, read before write does not change the value of other bits */
    val &= ~priv->enable_mask;

    val |= ctrl_val & priv->enable_mask;

    ret = wb_wdt_write(priv->priv_func_mode, priv->config_dev_name,
                priv->enable_reg, &val, ONE_BYTE);
    if (ret < 0) {
        dev_err(priv->dev, "write wdt control reg error.\n");
        return ret;
    }

    return 0;
}

static void wdt_hwping(wb_wdt_priv_t *priv)
{
    gpio_wdt_info_t *gpio_wdt;
    logic_wdt_info_t *logic_wdt;
    uint8_t tmp_val;
    int ret;

    if (priv->wdt_ready == 0) {
        WDT_VERBOSE("wdt not ready, do nothing\n");
        return;
    }

    if (priv->config_mode == GPIO_FEED_WDT_MODE) {
        gpio_wdt = &priv->gpio_wdt;
        switch (priv->hw_algo) {
        case HW_ALGO_TOGGLE:
            gpio_wdt = &priv->gpio_wdt;
            gpio_wdt->state = !gpio_wdt->state;
            gpio_set_value_cansleep(gpio_wdt->gpio, gpio_wdt->state);
            WDT_VERBOSE("gpio toggle wdt work. val:%u\n", gpio_wdt->state);
            break;
        case HW_ALGO_LEVEL:
            gpio_wdt = &priv->gpio_wdt;
            /* Pulse */
            gpio_set_value_cansleep(gpio_wdt->gpio, !gpio_wdt->active_low);
            udelay(1);
            gpio_set_value_cansleep(gpio_wdt->gpio, gpio_wdt->active_low);
            WDT_VERBOSE("gpio level wdt work.\n");
            break;
        }
    } else {
        logic_wdt = &priv->logic_wdt;
        switch (priv->hw_algo) {
        case HW_ALGO_TOGGLE:
            logic_wdt->active_val = !logic_wdt->active_val;
            ret = wb_wdt_write(logic_wdt->logic_func_mode, logic_wdt->feed_dev_name,
                        logic_wdt->feed_reg, &logic_wdt->active_val, ONE_BYTE);
            if (ret < 0) {
                WDT_ERROR("logic toggle wdt write failed.ret = %d\n", ret);
            }
            WDT_VERBOSE("logic toggle wdt work.\n");
            break;
        case HW_ALGO_LEVEL:
            tmp_val = !logic_wdt->active_val;
            ret = wb_wdt_write(logic_wdt->logic_func_mode, logic_wdt->feed_dev_name,
                        logic_wdt->feed_reg, &tmp_val, ONE_BYTE);
            if (ret < 0) {
                WDT_ERROR("logic level wdt write first failed.ret = %d\n", ret);
            }
            udelay(1);
            ret = wb_wdt_write(logic_wdt->logic_func_mode, logic_wdt->feed_dev_name,
                        logic_wdt->feed_reg, &logic_wdt->active_val, ONE_BYTE);
            if (ret < 0) {
                WDT_ERROR("logic level wdt write second failed.ret = %d\n", ret);
            }
            WDT_VERBOSE("logic level wdt work.\n");
            break;
        case HW_ALGO_EIGENVALUES:
            ret = wb_wdt_write(logic_wdt->logic_func_mode, logic_wdt->feed_dev_name,
                        logic_wdt->feed_reg, &logic_wdt->active_val, ONE_BYTE);
            if (ret < 0) {
                WDT_ERROR("logic eigenvalues wdt write failed, path: %s, mode: %d, reg: 0x%x, val: 0x%x, ret: %d\n",
                    logic_wdt->feed_dev_name, logic_wdt->logic_func_mode, logic_wdt->feed_reg,
                    logic_wdt->active_val, ret);
            }
            WDT_VERBOSE("logic eigenvalues wdt work, path: %s, mode: %d, reg: 0x%x, val: 0x%x\n",
                logic_wdt->feed_dev_name, logic_wdt->logic_func_mode, logic_wdt->feed_reg, logic_wdt->active_val);
            break;
        }
    }
    return;
}

static enum hrtimer_restart hrtimer_hwping(struct hrtimer *timer)
{
    wb_wdt_priv_t *priv = container_of(timer, wb_wdt_priv_t, hrtimer);

    wdt_hwping(priv);
    hrtimer_forward(timer, timer->base->get_time(), priv->m_kt);
    return HRTIMER_RESTART;
}

/* The cpld timeout period is configured */
static int wb_wdt_set_timeout_cfg_reg(wb_wdt_priv_t *priv, uint8_t *buf, size_t count)
{
    int ret;
    struct device *dev;

    dev = priv->dev;
    if(priv->timeout_cfg_reg == INVALID_REG_ADDR) {
        dev_dbg(priv->dev, "Can't not set timeout cfg reg.\n");
        return -WB_RV_UNSUPPORT;
    }
    ret = wb_wdt_write(priv->priv_func_mode, priv->config_dev_name,
                priv->timeout_cfg_reg, buf, count);
    if (ret < 0) {
        dev_err(dev, "set timeout cfg reg error.\n");
        return ret;
    }

    return 0;
}

static int thread_timer_cfg(wb_wdt_priv_t *priv)
{
    struct device *dev;
    uint32_t hw_margin;
    uint32_t feed_time;
    uint32_t accuracy;
    uint8_t set_time_val;
    int ret;

    dev = priv->dev;

    ret = 0;
    ret += of_property_read_u32(dev->of_node, "feed_time", &priv->feed_time);
    if (ret != 0) {
        dev_err(dev, "thread Failed to priv dts.\n");
        return -ENXIO;
    }
    WDT_VERBOSE("thread priv->feed_time: %u.\n", priv->feed_time);

    hw_margin = priv->hw_margin;
    feed_time = priv->feed_time;
    accuracy = priv->timer_accuracy;

    if (feed_time > (hw_margin / 2)) {
        dev_err(dev, "thread timer feed_time should be less than half hw_margin.\n");
        return -EINVAL;
    }

    /* The set value is written to the logic device */
    set_time_val = hw_margin / accuracy;
    ret = wb_wdt_set_timeout_cfg_reg(priv, &set_time_val, ONE_BYTE);
    if (ret < 0) {
        if(ret != -WB_RV_UNSUPPORT) {
            dev_err(dev, "set wdt thread timer reg error.\n");
            return ret;
        }
    }
    return 0;
}

static int wdt_thread_timer(void *data)
{
    wb_wdt_priv_t *priv = data;

    while (!kthread_should_stop()) {
        schedule_timeout_uninterruptible(msecs_to_jiffies(priv->feed_time));
        wdt_hwping(priv);
    }
    return 0;
}

static int thread_timer_create(wb_wdt_priv_t *priv)
{
    struct task_struct *p;
    int ret;

    /* Timeout configuration */
    ret = thread_timer_cfg(priv);
    if (ret < 0) {
        dev_err(priv->dev, "set wdt thread timer failed.\n");
        return ret;
    }

    /* Create a dog feed thread */
    p = kthread_create(wdt_thread_timer, (void *)priv, "%s", "wb_wdt");
    if (IS_ERR(p)) {
        dev_err(priv->dev, "timer thread create failed.\n");
        return PTR_ERR(p);
    }
    WDT_VERBOSE("timer thread create success.\n");

    /* Enable the watchdog */
    ret = wb_wdt_enable_ctrl(priv, WDT_ON);
    if (ret < 0) {
        dev_err(priv->dev, "thread enable wdt failed.\n");
        kthread_stop(p);
        return -ENXIO;
    }

    /* Feed the dog once after enabling the watchdog */
    wdt_hwping(priv);

    /* Call thread */
    priv->thread = p;
    wake_up_process(p);
    return 0;
}

static int hrtimer_cfg(wb_wdt_priv_t *priv)
{
    struct device *dev;
    struct hrtimer *hrtimer;
    uint8_t set_time_val;
    uint8_t hrtimer_s;
    uint32_t hrtimer_ns;
    int ret;
    uint32_t hw_margin;
    uint32_t feed_time;
    uint32_t accuracy;
    uint32_t max_timeout;

    dev = priv->dev;

    ret = 0;
    ret += of_property_read_u32(dev->of_node, "feed_time", &priv->feed_time);
    if (ret != 0) {
        dev_err(dev, "hrtimer Failed to priv dts.\n");
        return -ENXIO;
    }
    WDT_VERBOSE("hrtimer priv->feed_time: %u.\n", priv->feed_time);

    hrtimer = &priv->hrtimer;
    hw_margin = priv->hw_margin;
    feed_time = priv->feed_time;
    accuracy = priv->timer_accuracy;
    max_timeout = accuracy * 255;

    if (hw_margin < accuracy || hw_margin > max_timeout) {
        dev_err(dev, "hrtimer_hw_margin should be between %u and %u.\n",
            accuracy, max_timeout);
        return -EINVAL;
    }
    if (feed_time > (hw_margin / 2)) {
        dev_err(dev, "feed_time should be less than half hw_margin.\n");
        return -EINVAL;
    }

    hrtimer_s = feed_time / MS_TO_S;                /* The second portion of the time it takes to safely feed your dog */
    hrtimer_ns = (feed_time % MS_TO_S) * MS_TO_NS;  /* The nanosecond portion of safe dog feeding time */
    set_time_val = hw_margin / accuracy;            /* Values written to the logic device */

    /* Configuring the timeout period */
    ret = wb_wdt_set_timeout_cfg_reg(priv, &set_time_val, ONE_BYTE);
    if (ret < 0) {
        if(ret != -WB_RV_UNSUPPORT) {
            dev_err(dev, "set wdt time reg error.\n");
            return ret;
        }
    }

    /* Enable the watchdog */
    ret = wb_wdt_enable_ctrl(priv, WDT_ON);
    if (ret < 0) {
        dev_err(dev, "hrtimer enable wdt failed.\n");
        return -ENXIO;
    }

    /* Feed the dog once after enabling the watchdog */
    wdt_hwping(priv);

    /* Example Initialize the hrtimer and enable the hrtimer to feed the dog */
    priv->m_kt = ktime_set(hrtimer_s, hrtimer_ns);
    hrtimer_init(hrtimer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
    hrtimer->function = hrtimer_hwping;
    hrtimer_start(hrtimer, priv->m_kt, HRTIMER_MODE_REL);

    return 0;
}

static int wb_wdt_ping(struct watchdog_device *wdd)
{
    wb_wdt_priv_t *priv = watchdog_get_drvdata(wdd);

    wdt_hwping(priv);
    return 0;
}

static int wb_wdt_start(struct watchdog_device *wdd)
{
    wb_wdt_priv_t *priv = watchdog_get_drvdata(wdd);
    int ret;

    ret = wb_wdt_enable_ctrl(priv, WDT_ON);
    if (ret < 0) {
        WDT_ERROR("start wdt enable failed.\n");
        return -ENXIO;
    }
    set_bit(WDOG_HW_RUNNING, &wdd->status);
    return 0;
}

static int wb_wdt_stop(struct watchdog_device *wdd)
{
    wb_wdt_priv_t *priv = watchdog_get_drvdata(wdd);
    int ret;

    ret = wb_wdt_enable_ctrl(priv, WDT_OFF);
    if (ret < 0) {
        WDT_ERROR("stop wdt enable failed.\n");
        return -ENXIO;
    }
    clear_bit(WDOG_HW_RUNNING, &wdd->status);
    return 0;
}

static int wb_wdt_set_timeout(struct watchdog_device *wdd, unsigned int t)
{
    wb_wdt_priv_t *priv = watchdog_get_drvdata(wdd);
    uint32_t timeout_ms;
    uint32_t accuracy;
    uint8_t set_time_val;
    int ret;

    accuracy = priv->timer_accuracy;
    timeout_ms = t * 1000;

    /* The set value is written to the logic device */
    set_time_val = timeout_ms / accuracy;
    ret = wb_wdt_set_timeout_cfg_reg(priv, &set_time_val, ONE_BYTE);
    if (ret < 0) {
        if(ret == -WB_RV_UNSUPPORT) {
            /* No support set timeout cfg. Here, sysfs case */
            ret = -EOPNOTSUPP;
        }
        WDT_ERROR("set wdt timeout reg error.set_time_val:%u\n", set_time_val);
        return ret;
    }
    wdd->timeout = t;

    return 0;
}

static const struct watchdog_info wb_wdt_ident = {
    .options    = WDIOF_MAGICCLOSE | WDIOF_KEEPALIVEPING | WDIOF_SETTIMEOUT,
    .firmware_version = 0,
    .identity   = "CPLD Watchdog",
};

static const struct watchdog_ops wb_wdt_ops = {
    .owner        = THIS_MODULE,
    .start        = wb_wdt_start,
    .stop         = wb_wdt_stop,
    .ping         = wb_wdt_ping,
    .set_timeout  = wb_wdt_set_timeout,
};

static int watchdog_device_cfg(wb_wdt_priv_t *priv)
{
    int ret;
    uint8_t set_time_val;

    /* Verify that the watchdog is disabled by default */
    ret = wb_wdt_enable_ctrl(priv, WDT_OFF);
    if (ret < 0) {
        dev_err(priv->dev, "probe disable wdt failed.\n");
        return -ENXIO;
    }

    /* The default timeout period is set */
    set_time_val = priv->hw_margin / priv->timer_accuracy; /* Values written to the logic device */
    ret = wb_wdt_set_timeout_cfg_reg(priv, &set_time_val, ONE_BYTE);
    if (ret < 0) {
        if(ret != -WB_RV_UNSUPPORT) {
            dev_err(priv->dev, "set wdt time reg error.\n");
            return ret;
        }
    }

    /* Register the wdd device with the kernel watchdog framework */
    watchdog_set_drvdata(&priv->wdd, priv);

    priv->wdd.info         = &wb_wdt_ident;
    priv->wdd.ops          = &wb_wdt_ops;
    priv->wdd.bootstatus   = 0;
    priv->wdd.timeout      = priv->hw_margin / MS_TO_S;
    priv->wdd.min_timeout  = priv->timer_accuracy / MS_TO_S;
    priv->wdd.max_timeout  = priv->timer_accuracy * MAX_REG_VAL / MS_TO_S;
    priv->wdd.parent       = priv->dev;

    watchdog_stop_on_reboot(&priv->wdd);

    ret = devm_watchdog_register_device(priv->dev, &priv->wdd);
    if (ret != 0) {
        dev_err(priv->dev, "cannot register watchdog device (err=%d)\n", ret);
        return -ENXIO;
    }

    return 0;
}

static int logic_wdt_init(wb_wdt_priv_t *priv)
{
    struct device *dev;
    logic_wdt_info_t *logic_wdt;
    int ret;

    dev = priv->dev;
    logic_wdt = &priv->logic_wdt;

    ret = 0;
    ret += of_property_read_string(dev->of_node, "feed_dev_name", &logic_wdt->feed_dev_name);
    ret += of_property_read_u32(dev->of_node, "feed_reg", &logic_wdt->feed_reg);
    ret += of_property_read_u8(dev->of_node, "active_val", &logic_wdt->active_val);
    ret += of_property_read_u8(dev->of_node, "logic_func_mode", &logic_wdt->logic_func_mode);
    if (ret != 0) {
        dev_err(dev, "Failed to logic_wdt dts.\n");
        return -ENXIO;
    }

    logic_wdt->state_val = logic_wdt->active_val;

    WDT_VERBOSE("feed_dev_name:%s, feed_reg:0x%x, active_val:%u, logic_func_mode:%u\n",
        logic_wdt->feed_dev_name, logic_wdt->feed_reg,
        logic_wdt->active_val, logic_wdt->logic_func_mode);

    return 0;
}

static int gpio_wdt_init(wb_wdt_priv_t *priv)
{
    struct device *dev;
    gpio_wdt_info_t *gpio_wdt;
    enum of_gpio_flags flags;
    uint32_t f = 0;
    int ret;

    dev = priv->dev;
    gpio_wdt = &priv->gpio_wdt;

    gpio_wdt->gpio = of_get_gpio_flags(dev->of_node, 0, &flags);
    if (!gpio_is_valid(gpio_wdt->gpio)) {
        dev_err(dev, "gpio is invalid.\n");
        return gpio_wdt->gpio;
    }

    gpio_wdt->active_low = flags & OF_GPIO_ACTIVE_LOW;

    if(priv->hw_algo == HW_ALGO_TOGGLE) {
        f = GPIOF_IN;
    } else if (priv->hw_algo == HW_ALGO_LEVEL) {
        f = gpio_wdt->active_low ? GPIOF_OUT_INIT_HIGH : GPIOF_OUT_INIT_LOW;
    } else {
        dev_err(dev, "gpio not support hw_algo type: %d.\n", priv->hw_algo);
        return -EINVAL;
    }

    ret = devm_gpio_request_one(dev, gpio_wdt->gpio, f,
                dev_name(dev));
    if (ret) {
        dev_err(dev, "devm_gpio_request_one failed.\n");
        return ret;
    }

    gpio_wdt->state = gpio_wdt->active_low;
    gpio_direction_output(gpio_wdt->gpio, gpio_wdt->state);

    WDT_VERBOSE("active_low:%d\n", gpio_wdt->active_low);
    return 0;
}

static ssize_t set_wdt_sysfs_value(struct device *dev, struct device_attribute *da,
                        const char *buf, size_t count)
{
    wb_wdt_priv_t *priv = dev_get_drvdata(dev);
    int ret, val;

    val = 0;
    sscanf(buf, "%d", &val);
    WDT_VERBOSE("set wdt, val:%d.\n", val);

    if (val < 0 || val > 255) {
        WDT_ERROR("set wdt val %d failed.\n", val);
        return -EINVAL;
    }

    mutex_lock(&priv->update_lock);

    ret = wb_wdt_enable_ctrl(priv, val);
    if (ret < 0) {
        WDT_ERROR("set wdt sysfs value:%u failed.\n", val);
        goto fail;
    }

    WDT_VERBOSE("set wdt sysfs value:%u successed.\n", val);
    mutex_unlock(&priv->update_lock);
    return count;

fail:
    mutex_unlock(&priv->update_lock);
    return ret;
}

static ssize_t show_wdt_sysfs_value(struct device *dev,
                        struct device_attribute *da, char *buf)
{
    wb_wdt_priv_t *priv = dev_get_drvdata(dev);
    uint8_t val, status;
    int ret;

    /* case: Can't not enable/disable WDT */
    if(priv->enable_reg == INVALID_REG_ADDR) {
        /* default is ON */
        status = WDT_ON;
        dev_dbg(priv->dev, "Can't not enable/disable WDT, default is ON. status:%d.\n", status);
        return sprintf(buf, "%u\n", status);
    }

    mutex_lock(&priv->update_lock);

    /* First read the value val of the enable register */
    ret = wb_wdt_read(priv->priv_func_mode, priv->config_dev_name,
                priv->enable_reg, &val, ONE_BYTE);
    if (ret < 0) {
        dev_err(priv->dev, "read wdt enable reg val error.\n");
        goto fail;
    }

    val &= priv->enable_mask;
    if (val == priv->enable_val) {
        status = WDT_ON;
    } else if(val == priv->disable_val) {
        status = WDT_OFF;
    } else {
        WDT_ERROR("enable reg read val not match set val, read val:%u, mask:%u, enable_val:%u, disable_val:%u",
            val, priv->enable_mask, priv->enable_val, priv->disable_val);
        ret = -EIO;
        goto fail;
    }

    WDT_VERBOSE("read_val:%u, mask:%u, enable_val:%u, disable_val:%u, status:%u",
        val, priv->enable_mask, priv->enable_val, priv->disable_val, status);

    mutex_unlock(&priv->update_lock);
    return sprintf(buf, "%u\n", status);

fail:
    mutex_unlock(&priv->update_lock);
    return ret;
}

static ssize_t set_wdt_ready_sysfs_value(struct device *dev, struct device_attribute *da,
                   const char *buf, size_t count)
{
    wb_wdt_priv_t *priv;
    int err;
    uint32_t val;

    priv = dev_get_drvdata(dev);
    err = kstrtouint(buf, 0, &val);
    if (err) {
        dev_err(priv->dev, "invalid value: %s, can't set wdt ready status\n", buf);
        return err;
    }

    WDT_VERBOSE("set wdt ready status value: %u\n", val);

    priv->wdt_ready = val;

    return count;
}

static ssize_t show_wdt_ready_sysfs_value(struct device *dev, struct device_attribute *da,
                   char *buf)
{
    wb_wdt_priv_t *priv;

    priv = dev_get_drvdata(dev);
    return sprintf(buf, "%u\n", priv->wdt_ready);
}

static SENSOR_DEVICE_ATTR(wdt_status, S_IRUGO | S_IWUSR, show_wdt_sysfs_value, set_wdt_sysfs_value, 0);
static SENSOR_DEVICE_ATTR(wdt_ready, S_IRUGO | S_IWUSR, show_wdt_ready_sysfs_value, set_wdt_ready_sysfs_value, 0);

static struct attribute *wdt_sysfs_attrs[] = {
    &sensor_dev_attr_wdt_status.dev_attr.attr,
    NULL
};

static struct attribute *wdt_ready_sysfs_attrs[] = {
    &sensor_dev_attr_wdt_ready.dev_attr.attr,
    NULL
};

static const struct attribute_group wdt_sysfs_group = {
    .attrs = wdt_sysfs_attrs,
};

static const struct attribute_group wdt_ready_sysfs_group = {
    .attrs = wdt_ready_sysfs_attrs,
};

struct wdt_attr_match_group {
    uint8_t index;                                /* ID */
    const struct attribute_group *attr_group_ptr; /* SYS attribute pointer */
};

static struct wdt_attr_match_group g_wdt_attr_match[] = {
    {0, &wdt_sysfs_group},
    {1, &wdt_ready_sysfs_group},
};

static const struct attribute_group *wdt_get_attr_group(uint32_t index)
{
    int i;
    struct wdt_attr_match_group *group;

    for (i = 0; i < ARRAY_SIZE(g_wdt_attr_match); i++) {
        group = &g_wdt_attr_match[i];
        if (index == group->index) {
            WDT_VERBOSE("get wdt attr, index:%u.\n", index);
            return group->attr_group_ptr;
        }
    }

    return NULL;
}

static int wb_wdt_probe(struct platform_device *pdev)
{
    wb_wdt_priv_t *priv;
    int ret;
    const char *algo;

    priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
    if (!priv) {
        dev_err(&pdev->dev, "devm_kzalloc failed.\n");
        return -ENOMEM;
    }

    platform_set_drvdata(pdev, priv);

#ifdef CONFIG_OF
    ret = 0;
    ret += of_property_read_string(pdev->dev.of_node, "config_dev_name", &priv->config_dev_name);
    ret += of_property_read_string(pdev->dev.of_node, "hw_algo", &algo);
    ret += of_property_read_u8(pdev->dev.of_node, "config_mode", &priv->config_mode);
    ret += of_property_read_u8(pdev->dev.of_node, "priv_func_mode", &priv->priv_func_mode);
    ret += of_property_read_u32(pdev->dev.of_node,"hw_margin_ms", &priv->hw_margin);
    ret += of_property_read_u8(pdev->dev.of_node,"feed_wdt_type", &priv->feed_wdt_type);
    ret += of_property_read_u32(pdev->dev.of_node,"timer_accuracy", &priv->timer_accuracy);
    if (ret != 0) {
        dev_err(&pdev->dev, "Failed to priv dts.\n");
        return -ENXIO;
    }

    ret = of_property_read_u32(pdev->dev.of_node, "enable_reg", &priv->enable_reg);
    if (ret < 0) {
        /* case: Can't not enable/disable WDT */
        dev_dbg(&pdev->dev, "Failed to get property in dts: enable_reg.\n");
        priv->enable_reg = INVALID_REG_ADDR; /* no enable register */
    } else {
        ret = 0;
        ret += of_property_read_u8(pdev->dev.of_node, "enable_val", &priv->enable_val);
        ret += of_property_read_u8(pdev->dev.of_node, "disable_val", &priv->disable_val);
        ret += of_property_read_u8(pdev->dev.of_node, "enable_mask", &priv->enable_mask);
        if (ret != 0) {
            dev_err(&pdev->dev, "Failed to priv dts.\n");
            return -ENXIO;
        }
    }

    ret = of_property_read_u32(pdev->dev.of_node, "timeout_cfg_reg", &priv->timeout_cfg_reg);
    if (ret < 0) {
        /* case: Can't not set timeout cfg reg */
        dev_dbg(&pdev->dev, "Failed to get property in dts: timeout_cfg_reg.\n");
        priv->timeout_cfg_reg = INVALID_REG_ADDR; /* no timeout cfg register */
    }

    /* Whether sysfs is generated is optional */
    priv->sysfs_index = SYSFS_NO_CFG;
    of_property_read_u8(pdev->dev.of_node,"sysfs_index", &priv->sysfs_index);

    /* wdt_ready is configurable. If the value is not configured, the value is 1 by default */
    ret = of_property_read_u32(pdev->dev.of_node,"wdt_ready", &priv->wdt_ready);
    if (ret != 0) {
        priv->wdt_ready = 1;
    }

    if (!strcmp(algo, "toggle")) {
        priv->hw_algo = HW_ALGO_TOGGLE;
    } else if (!strcmp(algo, "level")) {
        priv->hw_algo = HW_ALGO_LEVEL;
    } else if (!strcmp(algo, "eigenvalues")) {
        priv->hw_algo = HW_ALGO_EIGENVALUES;
    } else {
        dev_err(&pdev->dev, "hw_algo config error.must be toggle or level.\n");
        return -EINVAL;
    }

    dev_info(&pdev->dev, "config_dev_name:%s, config_mode:%u, priv_func_mode:%u, enable_reg:0x%x, timeout_cfg_reg:0x%x\n",
        priv->config_dev_name, priv->config_mode, priv->priv_func_mode, priv->enable_reg, priv->timeout_cfg_reg);
    dev_info(&pdev->dev, "enable_val:%u, disable_val:%u, enable_mask:%u, hw_margin:%u, feed_wdt_type:%u\n",
        priv->enable_val, priv->disable_val, priv->enable_mask,   priv->hw_margin, priv->feed_wdt_type);

#else
    dev_err(&pdev->dev, "Error: CONFIG_OF must be defined.\n");
    return -ENXIO;
#endif

    priv->dev = &pdev->dev;
    if (priv->config_mode == GPIO_FEED_WDT_MODE) {
        ret = gpio_wdt_init(priv);
        if (ret < 0) {
            dev_err(&pdev->dev, "init gpio mode wdt failed.\n");
            return -ENXIO;
        }
    } else if (priv->config_mode == LOGIC_FEED_WDT_MODE) {
        ret = logic_wdt_init(priv);
        if (ret < 0) {
            dev_err(&pdev->dev, "init func mode wdt failed.\n");
            return -ENXIO;
        }
    } else {
        dev_err(&pdev->dev, "unsupport %u config_mode, dts configure error.\n",
            priv->config_mode);
        return -ENXIO;
    }

    switch (priv->feed_wdt_type) {
    case WATCHDOG_DEVICE_TYPE:
        ret = watchdog_device_cfg(priv);
        break;
    case HRTIMER_TYPE:
        ret = hrtimer_cfg(priv);
        break;
    case THREAD_TYPE:
        ret = thread_timer_create(priv);
        break;
    default:
        dev_err(&pdev->dev, "timer type %u unsupport.\n", priv->feed_wdt_type);
        return -EINVAL;
    }
    if (ret < 0) {
        dev_err(&pdev->dev, "init timer feed_wdt_type %u failed.\n", priv->feed_wdt_type);
        return -ENXIO;
    }

    dev_info(&pdev->dev, "register %s mode, config_mode %u, func_mode %u, %u ms overtime wdt success\n",
        algo, priv->config_mode, priv->priv_func_mode, priv->hw_margin);

    if (priv->sysfs_index != SYSFS_NO_CFG) {
        /* Creating sysfs */
        priv->sysfs_group = wdt_get_attr_group(priv->sysfs_index);
        if (priv->sysfs_group) {
            ret = sysfs_create_group(&pdev->dev.kobj, priv->sysfs_group);
            if (ret != 0) {
                dev_err(&pdev->dev, "sysfs_create_group failed. ret:%d.\n", ret);
                return -ENOMEM;
            }
            dev_err(&pdev->dev, "sysfs create group success\n");
        } else {
            dev_err(&pdev->dev, "failed to find %u index wdt, return NULL.\n", priv->sysfs_index);
            return -ENOMEM;
        }

        mutex_init(&priv->update_lock);

        dev_info(&pdev->dev, "register %u index wdt sysfs success." ,priv->sysfs_index);
    }

    return 0;
}

static void unregister_action(struct platform_device *pdev)
{
    wb_wdt_priv_t *priv = platform_get_drvdata(pdev);
    int ret;

    /* Feed the dog one last time before logging off */
    wdt_hwping(priv);

    ret = wb_wdt_enable_ctrl(priv, WDT_OFF);
    if (ret < 0) {
        dev_err(&pdev->dev, "remove disable wdt failed.\n");
    }

    if (priv->sysfs_index != SYSFS_NO_CFG) {
       sysfs_remove_group(&pdev->dev.kobj, priv->sysfs_group);
    }

    if (priv->feed_wdt_type == HRTIMER_TYPE) {
        hrtimer_cancel(&priv->hrtimer);
    } else if (priv->feed_wdt_type == THREAD_TYPE) {
        kthread_stop(priv->thread);
        priv->thread = NULL;
    } else {
        WDT_VERBOSE("wdd type, do nothing.\n");
    }
#if 0
    if (priv->config_mode == GPIO_FEED_WDT_MODE) {
        gpio_wdt = &priv->gpio_wdt;
        gpio_set_value_cansleep(gpio_wdt->gpio, !gpio_wdt->active_low);

        if (priv->hw_algo == HW_ALGO_TOGGLE) {
            gpio_direction_input(gpio_wdt->gpio);
        }
    } else {
        logic_wdt = &priv->logic_wdt;
        logic_wdt->state_val = !logic_wdt->state_val;
        ret = wb_wdt_write(logic_wdt->logic_func_mode, logic_wdt->feed_dev_name,
                    logic_wdt->feed_reg, &logic_wdt->state_val, ONE_BYTE);
        if (ret < 0) {
            dev_err(&pdev->dev, "set wdt control reg error.\n");
        }
    }
#endif

    return;
}

static int wb_wdt_remove(struct platform_device *pdev)
{
    WDT_VERBOSE("enter remove wdt.\n");
    unregister_action(pdev);
    dev_info(&pdev->dev, "remove wdt finish.\n");

    return 0;
}

static void wb_wdt_shutdown(struct platform_device *pdev)
{
    WDT_VERBOSE("enter shutdown wdt.\n");
    unregister_action(pdev);
    dev_info(&pdev->dev, "shutdown wdt finish.\n");

    return;
}

static const struct of_device_id wb_wdt_dt_ids[] = {
    { .compatible = "wb_wdt", },
    { }
};
MODULE_DEVICE_TABLE(of, wb_wdt_dt_ids);

static struct platform_driver wb_wdt_driver = {
    .driver = {
        .name       = "wb_wdt",
        .of_match_table = wb_wdt_dt_ids,
    },
    .probe  = wb_wdt_probe,
    .remove = wb_wdt_remove,
    .shutdown = wb_wdt_shutdown,
};

#ifdef CONFIG_GPIO_WATCHDOG_ARCH_INITCALL
static int __init wb_wdt_init(void)
{
    return platform_driver_register(&wb_wdt_driver);
}
arch_initcall(wb_wdt_init);
#else
module_platform_driver(wb_wdt_driver);
#endif

MODULE_AUTHOR("support");
MODULE_DESCRIPTION("watchdog driver");
MODULE_LICENSE("GPL");
