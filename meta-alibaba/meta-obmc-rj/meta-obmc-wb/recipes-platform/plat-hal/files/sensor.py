#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# sensor.py
# Python implementation of the Class sensor
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase

class sensor(devicebase):

    __Value = None
    __Min = None
    __Max = None
    __ValueConfig = None
    __Unit = None
    __format = None

    __Min_config = None
    __Max_config = None

    @property
    def Min_config(self):
        return self.__Min_config

    @Min_config.setter
    def Min_config(self, val):
        self.__Min_config  = val

    @property
    def Max_config(self):
        return self.__Max_config

    @Max_config.setter
    def Max_config(self, val):
        self.__Max_config  = val

    @property
    def Unit(self):
        return self.__Unit

    @Unit.setter
    def Unit(self, val):
        self.__Unit  = val

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, val):
        self.__format  = val


    @property
    def ValueConfig(self):
        return self.__ValueConfig

    @ValueConfig.setter
    def ValueConfig(self, val):
        self.__ValueConfig  = val

    def get_formula_value(self, config):
        val_dict = []
        sensors = config.get('sensors')
        for i in sensors:
            val = sensor(i).Value
            val_dict.append(val)

        formula = config.get('calc_formula')
        if formula is None:
            print("calc_formula err")
            return False, "calc formula not found"

        formula_str = formula.format(*val_dict)
        value = eval(formula_str)

        return True, value

    @property
    def Value(self):
        try:
            config = self.ValueConfig
            way = config.get("way")
            if way == 'sysfs':
                loc_config = config.get("real_loc", None)
                if loc_config is None:
                    ret, ind = self.find_real_file_path(config.get("loc"))
                    loc_config = ind if (ret is True) else None
                    self.ValueConfig['real_loc'] = loc_config
                ret, val = self.read_real_sysfs(loc_config)
            elif way == 'sysfs_calc':
                ret, val = self.get_formula_value(config)
            else:
                ret, val  = self.get_value(config)
            if ret is False:
                raise Exception(str(val))
            if self.format is None:
                self.__Value = int(val)
            else:
                self.__Value = eval(self.format % val)
            if self.__Value <= -9999:
                raise Exception("value is illegal")
        except:
            self.__Value = None
            return None
        return self.__Value

    @Value.setter
    def Value(self, val):
        self.__Value  = val

    @property
    def Min(self):
        try:
            if self.format is None:
                self.__Min = self.Min_config
            else:
                self.__Min = eval(self.format % self.Min_config)
        except:
            return None
        return self.__Min

    @Min.setter
    def Min(self, val):
        self.__Min  = val

    @property
    def Max(self):
        try:
            if self.format is None:
                self.__Max = self.Max_config
            else:
                self.__Max = eval(self.format % self.Max_config)
        except:
            return None
        return self.__Max

    @Max.setter
    def Max(self, val):
        self.__Max  = val

    def __init__(self, conf=None):
        self.ValueConfig = conf.get("value", None)
        self.Min_config = conf.get("Min", None)
        self.Max_config = conf.get("Max", None)
        self.Unit = conf.get('Unit', None)
        self.format = conf.get('format', None)
        self.name = conf.get('name', None)
        self.prechk = conf.get('prechk', None)

    def __str__(self):
        formatstr =  \
            "ValueConfig:                : %s \n" \
            "Min :          %s \n" \
            "Max : %s \n" \
            "Unit  : %s \n" \
            "format:       : %s \n"

        tmpstr = formatstr % (self.ValueConfig, self.Min,
                                self.Max, self.Unit,
                                self.format)
        return tmpstr

