#!/usr/bin/env python3
import sys
import os
import time
import syslog
import glob
import click
from platform_config import MAC_DEFAULT_PARAM
from platform_util import write_sysfs, get_value, get_format_value, check_value


AVSCTROL_DEBUG_FILE = "/etc/.avscontrol_debug_flag"

AVSCTROLERROR = 1
AVSCTROLDEBUG = 2

debuglevel = 0

CONTEXT_SETTINGS = {"help_option_names": ['-h', '--help']}


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
        return None


def avscontrol_debug(s):
    if AVSCTROLDEBUG & debuglevel:
        syslog.openlog("AVSCONTROL", syslog.LOG_PID)
        syslog.syslog(syslog.LOG_DEBUG, s)


def avscontrol_error(s):
    if AVSCTROLERROR & debuglevel:
        syslog.openlog("AVSCONTROL", syslog.LOG_PID)
        syslog.syslog(syslog.LOG_ERR, s)


def avserror(s):
    # s = s.decode('utf-8').encode('gb2312')
    syslog.openlog("AVSCONTROL", syslog.LOG_PID)
    syslog.syslog(syslog.LOG_ERR, s)


def avsinfo(s):
    syslog.openlog("AVSCONTROL", syslog.LOG_PID)
    syslog.syslog(syslog.LOG_INFO, s)


def debug_init():
    global debuglevel
    if os.path.exists(AVSCTROL_DEBUG_FILE):
        debuglevel = debuglevel | AVSCTROLDEBUG | AVSCTROLERROR
    else:
        debuglevel = debuglevel & ~(AVSCTROLDEBUG | AVSCTROLERROR)


def set_avs_value_sysfs(conf, dcdc_value):
    msg = ""
    formula = conf.get("formula", None)
    loc = conf.get("loc")
    locations = glob.glob(loc)
    if len(locations) == 0:
        msg = "avs sysfs loc: %s not found" % loc
        avscontrol_error(msg)
        return False, msg
    sysfs_loc = locations[0]
    avscontrol_debug("set_avs_value_sysfs, loc: %s, origin dcdc value: %s, formula: %s" %
                     (sysfs_loc, dcdc_value, formula))
    if formula is not None:
        dcdc_value = get_format_value(formula % (dcdc_value))
    wr_val = str(dcdc_value)
    avscontrol_debug("set_avs_value_sysfs, write val: %s" % wr_val)
    ret, log = write_sysfs(sysfs_loc, wr_val)
    if ret is False:
        msg = "set_avs_value_sysfs failed, msg: %s" % log
        avscontrol_error(msg)
    return ret, msg


def set_avs_value(avs_conf, dcdc_value):
    set_avs_way = avs_conf.get("set_avs", {}).get("gettype")
    if set_avs_way != "sysfs":
        msg = "unsupport set avs value type: %s" % set_avs_way
        avscontrol_error(msg)
        return False, msg
    ret, msg = set_avs_value_sysfs(avs_conf["set_avs"], dcdc_value)
    return ret, msg


def get_dcdc_value(avs_conf, rov_value):
    msg = ""
    mac_avs_param = avs_conf.get("mac_avs_param", {})
    if rov_value not in mac_avs_param.keys():
        if avs_conf["type"] == 0:
            msg = "VID:0x%x out of range, voltage regulate stop" % rov_value
            avsinfo(msg)
            return False, msg
        dcdc_value = mac_avs_param[avs_conf["default"]]
        avsinfo("VID:0x%x out of range, use default VID:0x%x" % (rov_value, dcdc_value))
    else:
        dcdc_value = mac_avs_param[rov_value]
    return True, dcdc_value


def get_rov_value_cpld(avs_conf):
    cpld_avs_config = avs_conf["cpld_avs"]
    return get_value(cpld_avs_config)


def doAvsCtrol_single(avs_conf):
    try:
        avs_name = avs_conf.get("name")
        rov_source = avs_conf["rov_source"]
        if rov_source != 0:
            msg = "Unsupport rov_source: %s" % rov_source
            avscontrol_error(msg)
            return False, msg
        ret, rov_value = get_rov_value_cpld(avs_conf)  # get rov from cpld reg
        if ret is False:
            msg = "%s get rov_value failed, msg: %s" % (avs_name, rov_value)
            avscontrol_error(msg)
            return False, msg
        avscontrol_debug("%s rov_value:  0x%x" % (avs_name, rov_value))
        ret, dcdc_value = get_dcdc_value(avs_conf, rov_value)
        if ret is False:
            msg = "%s get output voltage value failed, msg: %s" % (avs_name, dcdc_value)
            avscontrol_error(msg)
            return False, msg
        ret, msg = set_avs_value(avs_conf, dcdc_value)
        return ret, msg
    except Exception as e:
        msg = "%s avscontrol raise exception, msg: %s" % (avs_name, str(e))
        avscontrol_error(msg)
        return False, msg


def check_avs_ready(avs_ready_check_list):
    '''
    avs_ready_check_list is a secondary list.
    avs_ready_conf_list is a primary list.
    If any condition in the primary list within the secondary list is true, the final result is true.
    If all conditions in a primary list are true, the final result for that primary list is true.
    '''
    avs_ready = False
    for avs_ready_conf_list in avs_ready_check_list:
        for avs_ready_conf in avs_ready_conf_list:
            ret, msg = check_value(avs_ready_conf)
            if ret is False:
                avs_ready = False
                msg = "avs_ready_conf: %s check_value failed, msg: %s" % (avs_ready_conf, msg)
                avscontrol_debug(msg)
                break
            avs_ready = True
            msg = "avs_ready_conf: %s check_value success, msg: %s" % (avs_ready_conf, msg)
            avscontrol_debug(msg)
        if avs_ready is True:
            avscontrol_debug("check_avs_ready ok, avs_ready is True")
            return True
    return False


def check_avs_status(avs_conf):
    avs_name = avs_conf.get("name")
    check_avs_ready_conf = avs_conf.get("check_avs_ready")
    if check_avs_ready_conf is None: # don't need to check avs ready
        msg = "%s check_avs_ready_conf is None, don't need to check avs ready" % avs_name
        avscontrol_debug(msg)
        return True, msg

    retrytime = check_avs_ready_conf.get("retry", 1)
    sleep_time = check_avs_ready_conf.get("sleep_time")
    avs_ready_check_list = check_avs_ready_conf.get("avs_ready_check_list", [])

    loop = 0
    while True:
        loop += 1
        debug_init()
        ret = check_avs_ready(avs_ready_check_list)
        if ret is True:
            msg = "%s check_avs_ready ok, retrytime: %d, loop: %d" % (avs_name, retrytime, loop)
            avscontrol_debug(msg)
            return True, msg
        avscontrol_debug("%s check_avs_ready not ok, retrytime: %d, loop: %d" % (avs_name, retrytime, loop))
        if retrytime > 0 and loop >= retrytime:
            msg = "%s check_avs_ready timeout, retrytime: %d, loop: %d" % (avs_name, retrytime, loop)
            avscontrol_debug(msg)
            return False, msg
        if sleep_time is not None and sleep_time > 0:
            time.sleep(sleep_time)
    return False, "%s check_avs_ready error" % avs_name


def doAvsCtrol(avs_conf):
    debug_init()
    ret, log = check_avs_status(avs_conf)
    if ret is False:
        return False, log

    avs_ctrl_pre_sleep = avs_conf.get("avs_ctrl_pre_sleep")
    if avs_ctrl_pre_sleep is not None and avs_ctrl_pre_sleep > 0:
        time.sleep(avs_ctrl_pre_sleep)

    retry_time = avs_conf.get("retry", 10)
    for i in range(retry_time):
        debug_init()
        ret, log = doAvsCtrol_single(avs_conf)
        if ret is True:
            return True, log
        time.sleep(1)
    return False, log


def run():
    errcnt = 0
    msg = ""
    for item in MAC_DEFAULT_PARAM:
        status, log = doAvsCtrol(item)
        if status is False:
            errcnt += 1
            msg += log

    if errcnt == 0:
        avsinfo("%%AVSCONTROL success")
        sys.exit(0)
    avserror("%%DEV_MONITOR-AVS: MAC Voltage adjust failed.")
    avserror("%%DEV_MONITOR-AVS: errmsg: %s" % msg)
    sys.exit(1)


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def main():
    '''device operator'''


@main.command()
def start():
    '''start AVS control'''
    avsinfo("%%AVSCONTROL start")
    run()


if __name__ == '__main__':
    main()
