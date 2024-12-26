#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# temp.py
# Python implementation of the Class temp
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase
from .sensor import sensor

class temp(sensor):
    def __init__(self, conf = None):
        super(temp, self).__init__(conf.get('Temperature', None))
        self.name =  conf.get("name", None)

    def __str__(self):
        super(temp, self).__str__()

    def get_max_value(self, conf):
        try:
            ret, val = self.get_value(conf)
            return val
        except:
            return None

    @property
    def Value(self):
        try:
            if isinstance(self.ValueConfig, list):
                max = None
                for i in self.ValueConfig:
                    tmp = self.get_max_value(i)
                    if tmp is None:
                        continue
                    if max is None or max < tmp:
                        max = tmp
                if max is None:
                    return None
                if self.format is None:
                    self.__Value = int(max)
                else:
                    self.__Value = eval(self.format % max)
            else:
                ret, val = self.get_value(self.ValueConfig)
                if self.format is None:
                    self.__Value = int(val)
                else:
                    self.__Value = eval(self.format % val)
        except:
            return None
        return self.__Value

    @Value.setter
    def Value(self, val):
        self.__Value  = val
