#!/usr/bin/env python
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
#

import json
import argparse
import sys
import logging
from logging.handlers import *
import os
import subprocess

import logging.handlers
import shutil
import gzip

class CompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d.gz" % (self.baseFilename, i)
                dfn = "%s.%d.gz" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1.gz"
            if os.path.exists(dfn):
                os.remove(dfn)
            # These two lines below are the only new lines. I commented out the os.rename(self.baseFilename, dfn) and
            #  replaced it with these two lines.
            with open(self.baseFilename, 'rb') as f_in, gzip.open(dfn, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        self.mode = 'w'
        self.stream = self._open()


class PlatCommonUtil:

    def JSONparser(self, file):
        """
        Get a json file and create a dictionary
        """
        with open(file) as data_file:
            data = json.load(data_file)
        return data

    def JSONparserFile(self, file, div=':'):
        """
        Get a json file and create a dictionary
        """
        data = {}
        with open(file) as data_file:
            for line in data_file.readlines():
                if div in line:
                    line_list = line.split(div, 1)
                    data[line_list[0].strip()] = line_list[1].strip() 
        return data

    def Argparser(self, names, platformTypes, helps, optional=None):
        parser = argparse.ArgumentParser()
        for i in range(len(names)):
            if platformTypes[i] is None:
                parser.add_argument(names[i], help=helps[i])
            elif optional and optional[i]:
                parser.add_argument(
                    names[i],
                    metavar=names[i],
                    type=platformTypes[i],
                    help=helps[i],
                    nargs='?')
            else:
                parser.add_argument(
                    names[i],
                    metavar=names[i],
                    type=platformTypes[i],
                    help=helps[i])
        return parser.parse_args()

    def run_shell_cmd(self, cmd):
        """Run the supplied command.
        """
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        
        out = proc.wait()
        stdout,stderr = proc.communicate()
        if not stderr:
            stderr = stdout
        if out != 0:
            return stderr.decode('utf-8'),out
        else:
            return stdout.decode('utf-8'),out
