#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import click
import os
from platform_config import *
from platform_util import *


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def getPid(name):
    ret = []
    for dirname in os.listdir('/proc'):
        if dirname == 'curproc':
            continue
        try:
            with open('/proc/{}/cmdline'.format(dirname), mode='r') as fd:
                content = fd.read()
        except Exception:
            continue
        if name in content:
            ret.append(dirname)
    return ret


def startDevmonitor():
    if STARTMODULE.get('dev_monitor', 0) == 1:
        cmd = "nohup dev_monitor.py start >/dev/null 2>&1 &"
        rets = getPid("dev_monitor.py")
        if len(rets) == 0:
            os.system(cmd)

def startdfx_xdpe_monitor():
    if STARTMODULE.get('dfx_xdpe_monitor', 0) == 1:
        cmd = "nohup dfx_xdpe_monitor.py >/dev/null 2>&1 &"
        rets = getPid("dfx_xdpe_monitor.py")
        if len(rets) == 0:
            os.system(cmd)

def starthal_fanctrl():
    if STARTMODULE.get('hal_fanctrl', 0) == 1:
        cmd = "nohup hal_fanctrl.py start >/dev/null 2>&1 &"
        rets = getPid("hal_fanctrl.py")
        if len(rets) == 0:
            os.system(cmd)


def starthal_ledctrl():
    if STARTMODULE.get('hal_ledctrl', 0) == 1:
        cmd = "nohup hal_ledctrl.py start >/dev/null 2>&1 &"
        rets = getPid("hal_ledctrl.py")
        if len(rets) == 0:
            os.system(cmd)


def startAvscontrol():
    if STARTMODULE.get('avscontrol', 0) == 1:
        cmd = "nohup avscontrol.py start >/dev/null 2>&1 &"
        rets = getPid("avscontrol.py")
        if len(rets) == 0:
            os.system(cmd)


def Generate_mgmt_version():
    cmd = "nohup platform_manufacturer.py -u > /dev/null 2>&1 &"
    rets = getPid("platform_manufacturer.py")
    if len(rets) == 0:
        os.system(cmd)


def startGenerate_mgmt_version():
    if STARTMODULE.get('generate_mgmt_version', 1) == 1: #default value 1 to generate
        for i in range(10):
            Generate_mgmt_version()
            if os.path.exists(MGMT_VERSION_PATH):
                #click.echo("%%WB_PLATFORM_PROCESS: generate mgmt_version success")
                return
            time.sleep(1)
        click.echo("%%WB_PLATFORM_PROCESS: generate mgmt_version,failed, %s not exits" % MGMT_VERSION_PATH)
    return


def startGenerate_sw_config():
    if STARTMODULE.get('gen_sw_config', 1) == 1:
        cmd = "nohup gen_sw_config.py > /dev/null 2>&1 &"
        rets = getPid("gen_sw_config.py")
        if len(rets) == 0:
            os.system(cmd)

def stopDevmonitor():
    if STARTMODULE.get('dev_monitor', 0) == 1:
        rets = getPid("dev_monitor.py")  #
        for ret in rets:
            cmd = "kill " + ret
            os.system(cmd)


def stopdfx_xdpe_monitor():
    if STARTMODULE.get('dfx_xdpe_monitor', 0) == 1:
        rets = getPid("dfx_xdpe_monitor.py")
        for ret in rets:
            cmd = "kill " + ret
            os.system(cmd)


def stophal_fanctrl():
    if STARTMODULE.get('hal_fanctrl', 0) == 1:
        rets = getPid("hal_fanctrl.py")
        for ret in rets:
            cmd = "kill " + ret
            os.system(cmd)


def stophal_ledctrl():
    if STARTMODULE.get('hal_ledctrl', 0) == 1:
        rets = getPid("hal_ledctrl.py")
        for ret in rets:
            cmd = "kill " + ret
            os.system(cmd)


def stopAvscontrol():
    if STARTMODULE.get('avscontrol', 0) == 1:
        rets = getPid("avscontrol.py")
        for ret in rets:
            cmd = "kill " + ret
            os.system(cmd)


def otherinit():
    for conf in GLOBALINITPARAM:
        set_value(conf)


def otherinit_pre():
    for conf in GLOBALINITPARAM_PRE:
        set_value(conf)


def unload_apps():
    stopdfx_xdpe_monitor()
    stopAvscontrol()
    stophal_ledctrl()
    stophal_fanctrl()
    stopDevmonitor()


def load_apps():
    otherinit_pre()
    startDevmonitor()
    starthal_fanctrl()
    starthal_ledctrl()
    startAvscontrol()
    startdfx_xdpe_monitor()
    startGenerate_mgmt_version()
    startGenerate_sw_config()
    otherinit()


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def main():
    '''device operator'''
    pass


@main.command()
def start():
    '''load process '''
    load_apps()


@main.command()
def stop():
    '''stop process '''
    unload_apps()


@main.command()
def restart():
    '''restart process'''
    unload_apps()
    load_apps()


if __name__ == '__main__':
    u'''process init operation'''
    main()
