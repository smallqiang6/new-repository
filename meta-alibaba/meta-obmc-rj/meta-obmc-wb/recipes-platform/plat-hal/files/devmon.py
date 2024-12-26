#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# devmon.py
# Python implementation of the Class devmon
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase

class devmon(devicebase):
    __Value = None
    __Name = None
    __Expects = None
    __RW = None
    __Decoder = None
    __Descr = None

    def __init__(self, conf=None):
        self.ValueConfig = conf.get("value", None)
        self.__Name = conf.get('name', None)
        self.__Descr = conf.get('Descr', None)
        self.__Decoder = conf.get('Decoder', None)
        self.__Default = conf.get('Default', None)
        self.__RW = conf.get('RW', None)
        self.__Expects = conf.get('Expects', None)
        self.format = conf.get('format', None)
        self.intbase = conf.get('intbase', None)
        self.prechk = conf.get('prechk', None)

    @property
    def Value(self):
        try:
            config = self.ValueConfig
            way = config.get("way")
            mask = config.get("mask")
            if way == 'sysfs':
                loc_config = config.get("real_loc", None)
                if loc_config is None:
                    ret, ind = self.find_real_file_path(config.get("loc"))
                    loc_config = ind if (ret is True) else None
                    self.ValueConfig['real_loc'] = loc_config
                ret, val = self.read_real_sysfs(loc_config)
            else:
                ret, val  = self.get_value(config)
            if ret is False:
                raise Exception(str(val))
            if self.format is None:
                if isinstance(val, str):
                    self.__Value = int(val, self.intbase)
                elif isinstance(val, int):
                    self.__Value = val
                else:
                    self.__Value = None
                    return None
            else:
                self.__Value = eval(self.format % val)
        except:
            self.__Value = None
            return None
        return self.__Value & mask

    def reset(self):
        try:
            if self.__RW == "RO":
                return -1
            config = self.ValueConfig
            way = config.get("way")
            mask = config.get("mask")
            if way == 'sysfs':
                loc_config = config.get("real_loc", None)
                if loc_config is None:
                    ret, ind = self.find_real_file_path(config.get("loc"))
                    loc_config = ind if (ret is True) else None
                    self.ValueConfig['real_loc'] = loc_config
                ret, val = self.write_real_sysfs(loc_config, self.__Default)
            else:
                ret, val  = self.set_value(config, self.__Default)
            if ret is False:
                raise Exception(str(val))
        except:
            return -1
        return 0

    @Value.setter
    def Value(self, val):
        self.__Value  = val

    @property
    def devmonInit(self):
        pass

    @property
    def Name(self):
        return self.__Name

    @Name.setter
    def Name(self, val):
        self.__Name  = val

    @property
    def Descr(self):
        return self.__Descr

    @Descr.setter
    def Descr(self, val):
        self.__Descr  = val

    @property
    def Expects(self):
        return self.__Expects

    @Expects.setter
    def Expects(self, val):
        self.__Expects  = val

    @property
    def Decoder(self):
        return self.__Decoder

    @Decoder.setter
    def Decoder(self, val):
        self.__Decoder  = val

    @property
    def RW(self):
        return self.__RW

    @RW.setter
    def RW(self, val):
        self.__RW  = val
