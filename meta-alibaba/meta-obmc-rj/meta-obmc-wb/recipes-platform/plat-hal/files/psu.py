#######################################################
#
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
# psu.py
# Python implementation of the Class psu
# Original author: rd@ruijie.com.cn
#
#######################################################
from .devicebase import devicebase
from eepromutil.fru import *
from .sensor import sensor

class psu(devicebase):
    __pmbus = None
    __e2loc = None
    __present = None
    __productManufacturer = None #: ARTESYN
    __productName         = None #: CRPS550W
    __productPartModelName= None #: CSU550AP-3-300
    __productVersion      = None #: AB
    __productSerialNumber = None #: M623UZ00JYABL
    __AirFlow             = None # 'N/A'
    __AirFlowconfig       = None
    __InputStatus_config   = None
    __OutputStatus_config  = None
    __FanSpeed_config      = None
    __Temperature_config   = None
    __InputStatus   = None
    __OutputStatus  = None
    __FanSpeed      = None
    __Temperature   = None
    __FanSpeedMin   = None
    __FanSpeedMax   = None
    __InputsVoltage_config    = None
    __InputsCurrent_config     = None
    __InputsPower_config       = None
    __OutputsVoltage_config   = None
    __OutputsCurrent_config   = None
    __OutputsPower_config     = None
    __InputsVoltage   = {}
    __InputsCurrent    = None
    __InputsPower      = None
    __OutputsVoltage  = None
    __OutputsCurrent  = None
    __OutputsPower    = None
    __InputsType_config = None
    __InputsType = None

    def __init__(self, conf = None):
        self.fake = conf.get("fake", None)
        self.pmbus = conf.get("pmbusloc", None)
        self.e2loc = conf.get("e2loc", None)
        self.__presentconfig = conf.get("present", None)
        self.name =  conf.get("name", None)
        self.AirFlowconfig =  conf.get("airflow", None)
        self.FanSpeed_config = conf.get("FanSpeed", None)
        if self.FanSpeed_config is not None:
            self.FanSpeed   = self.judge_psu_sensor_fake(self.FanSpeed_config)
        self.Temperature_config = conf.get("Temperature", None)
        self.Temperature   = self.judge_psu_sensor_fake(self.Temperature_config)
        self.__InputsVoltage_config  = conf.get("InputsVoltage",None)
        self.generate_psu_input_vol(self.__InputsVoltage_config)
        self.__InputsCurrent_config   = conf.get("InputsCurrent",None)
        self.generate_psu_input_cur(self.__InputsCurrent_config)
        self.__InputsPower_config     = conf.get("InputsPower",None)
        self.InputsPower = self.judge_psu_sensor_fake(self.__InputsPower_config)
        self.__OutputsVoltage_config = conf.get("OutputsVoltage",None)
        self.OutputsVoltage = sensor(self.__OutputsVoltage_config)
        self.__OutputsCurrent_config = conf.get("OutputsCurrent",None)
        self.OutputsCurrent = sensor(self.__OutputsCurrent_config)
        self.__OutputsPower_config   = conf.get("OutputsPower",None)
        self.OutputsPower = sensor(self.__OutputsPower_config)

        self.__InputStatus_config = conf.get("InputsStatus", None)
        self.__OutputStatus_config = conf.get("OutputsStatus", None)
        self.__InputsType_config = conf.get('InputsType', None)

    def judge_psu_sensor_fake(self, sensor_item):
        if sensor_item.get("fake", None) == 1:
            return "fake"
        else:
            return sensor(sensor_item)

    def generate_psu_input_vol(self, config):
        if config.get("fake", None) == 1:
            self.__InputsVoltage = "fake"
            return
        tmp = {}
        for (key, item) in config.items():
            tmp.setdefault(key, sensor(item))
        self.__InputsVoltage  = tmp

    def get_psu_sensor_by_name(self, psutype):
        if self.__InputsVoltage == "fake":
            return self.__InputsVoltage
        return self.__InputsVoltage.get(psutype) or self.__InputsVoltage.get('other')

    @property
    def InputsVoltage(self):
        psutype = self.InputsType
        input_sensor = self.get_psu_sensor_by_name(psutype)
        if input_sensor  is None:
            return None
        else:
            return input_sensor

    @InputsVoltage.setter
    def InputsVoltage(self, val):
        self.__InputsVoltage  = val

    def generate_psu_input_cur(self, config):
        if config.get("fake", None) == 1:
            self.__InputsCurrent = "fake"
            return
        tmp = {}
        for (key, item) in config.items():
            tmp.setdefault(key, sensor(item))
        self.__InputsCurrent  = tmp

    def get_psu_sensor_by_name_cur(self, psutype):
        if self.__InputsCurrent == "fake":
            return self.__InputsCurrent
        return self.__InputsCurrent.get(psutype) or self.__InputsCurrent.get('other')

    @property
    def InputsCurrent(self):
        psutype = self.InputsType
        input_sensor = self.get_psu_sensor_by_name_cur(psutype)
        if input_sensor  is None:
            return None
        else:
            return input_sensor

    @InputsCurrent.setter
    def InputsCurrent(self, val):
        self.__InputsCurrent  = val

    @property
    def InputsPower(self):
        return self.__InputsPower

    @InputsPower.setter
    def InputsPower(self, val):
        self.__InputsPower  = val

    @property
    def OutputsVoltage(self):
        return self.__OutputsVoltage

    @OutputsVoltage.setter
    def OutputsVoltage(self, val):
        self.__OutputsVoltage  = val

    @property
    def OutputsCurrent(self):
        return self.__OutputsCurrent

    @OutputsCurrent.setter
    def OutputsCurrent(self, val):
        self.__OutputsCurrent  = val

    @property
    def OutputsPower(self):
        return self.__OutputsPower

    @OutputsPower.setter
    def OutputsPower(self, val):
        self.__OutputsPower  = val

    @property
    def InputStatus(self):
        if self.present == False:
            self.__InputStatus = False
        else:
            ret, val = self.get_value(self.__InputStatus_config)
            mask = self.__InputStatus_config.get("mask")
            target = self.__InputStatus_config.get("target", None)
            try:
                ttt = val & mask
                if ttt == 0 and self.fake != 1:
                    self.__InputStatus  = True
                elif self.fake == 1 and ttt == target:
                    self.__InputStatus  = True
                else:
                    self.__InputStatus  = False
            except Exception as e:
                self.__InputStatus  = False
        return self.__InputStatus

    @InputStatus.setter
    def InputStatus(self, val):
        self.__InputStatus  = val


    @property
    def InputsType(self):
        if self.fake == 1 and self.OutputStatus:
            self.__InputsType = self.__InputsType_config.get("type", "AC/DC")
            return self.__InputsType
        elif self.fake == 1 and not self.OutputStatus:
            self.__InputsType = "N/A"
            return self.__InputsType
        psutypedecode = self.__InputsType_config.get('psutypedecode', None)
        if self.present == False:
            self.__InputsType = psutypedecode.get(0x00)
        else:
            ret, val = self.get_value(self.__InputsType_config)
            self.__InputsType = self.__InputsType_config.get(val,None)
            if self.__InputsType is not None:
                return self.__InputsType
            if ret == True and val in psutypedecode:
                self.__InputsType = psutypedecode.get(val)
            else:
                self.__InputsType = psutypedecode.get(0x00)
        return self.__InputsType

    @InputsType.setter
    def InputsType(self, val):
        self.__InputsType  = val

    @property
    def FanSpeedMin(self):
        return self.__FanSpeedMin

    @FanSpeedMin.setter
    def FanSpeedMin(self, val):
        self.__FanSpeedMin  = val

    @property
    def FanSpeedMax(self):
        return self.__FanSpeedMax

    @FanSpeedMax.setter
    def FanSpeedMax(self, val):
        self.__FanSpeedMax  = val

    @property
    def OutputStatus(self):
        if self.present == False:
            self.__OutputStatus = False
        else:
            ret, val = self.get_value(self.__OutputStatus_config)
            mask = self.__OutputStatus_config.get("mask")
            target = self.__OutputStatus_config.get("target", None)
            try:
                ttt = val & mask
                if ttt == 0 and self.fake != 1:
                    self.__OutputStatus  = True
                elif self.fake == 1 and ttt == target:
                    self.__OutputStatus  = True
                else:
                    self.__OutputStatus  = False
            except Exception as e:
                self.__OutputStatus  = False
        return self.__OutputStatus

    @OutputStatus.setter
    def OutputStatus(self, val):
        self.__OutputStatus  = val

    @property
    def FanSpeed(self):
        return self.__FanSpeed

    @FanSpeed.setter
    def FanSpeed(self, val):
        self.__FanSpeed  = val

    @property
    def Temperature(self):
        return self.__Temperature

    @Temperature.setter
    def Temperature(self, val):
        self.__Temperature  = val

    @property
    def Temperature_config(self):
        return self.__Temperature_config

    @Temperature_config.setter
    def Temperature_config(self, val):
        self.__Temperature_config = val

    @property
    def AirFlowconfig(self):
        return self.__AirFlowconfig

    @AirFlowconfig.setter
    def AirFlowconfig(self, val):
        self.__AirFlowconfig = val

    @property
    def pmbus(self):
        return self.__pmbus

    @pmbus.setter
    def pmbus(self, val):
        self.__pmbus = val

    @property
    def e2loc(self):
        return self.__e2loc

    @e2loc.setter
    def e2loc(self, val):
        self.__e2loc = val

    @property
    def AirFlow(self):
        return self.__AirFlow

    @AirFlow.setter
    def AirFlow(self, val):
        self.__AirFlow = val

    @property
    def present(self):
        if self.fake == 1:
            return True
        ret , val = self.get_value(self.__presentconfig)
        mask = self.__presentconfig.get("mask")
        okval = self.__presentconfig.get("okval")
        try:
            if mask:
                val = val & mask
            if okval:
                return True if val == okval else False
            if val == 0:
                return True
            else:
                return False
        except Exception as e:
            return False

    @present.setter
    def present(self, val):
        self.__present = val

    @property
    def productManufacturer(self):
        return self.__productManufacturer

    @productManufacturer.setter
    def productManufacturer(self, val):
        self.__productManufacturer = val

    @property
    def productName(self):
        return self.__productName

    @productName.setter
    def productName(self, val):
        self.__productName = val

    @property
    def productPartModelName(self):
        return self.__productPartModelName

    @productPartModelName.setter
    def productPartModelName(self, val):
        self.__productPartModelName = val

    @property
    def productVersion(self):
        return self.__productVersion

    @productVersion.setter
    def productVersion(self, val):
        self.__productVersion = val

    @property
    def productSerialNumber(self):
        return self.__productSerialNumber

    @productSerialNumber.setter
    def productSerialNumber(self, val):
        self.__productSerialNumber = val

    @property
    def psu_temp_dict(self):
        self.__psu_temp_dict = {}
        try:
            self.__psu_temp_dict = {}
            self.__psu_temp_dict['Min'] = self.Temperature.Min
            self.__psu_temp_dict['Max'] = self.Temperature.Max
            self.__psu_temp_dict['Value'] = self.Temperature.Value
        except Exception as e:
            self.__psu_temp_dict = None
        return self.__psu_temp_dict

    @psu_temp_dict.setter
    def psu_temp_dict(self, val):
        self.__psu_temp_dict = val

    @property
    def psu_temp_sensor_dict(self):
        self.__psu_temp_sensor_dict = {}
        try:
            self.__psu_temp_sensor_dict = {}
            self.__psu_temp_sensor_dict['Min'] = self.Temperature.Min
            self.__psu_temp_sensor_dict['Max'] = self.Temperature.Max
            self.__psu_temp_sensor_dict['Value'] = self.Temperature.Value
            self.__psu_temp_sensor_dict['Unit'] = self.Temperature.Unit
        except Exception as e:
            self.__psu_temp_sensor_dict = None
        return self.__psu_temp_sensor_dict

    @psu_temp_sensor_dict.setter
    def psu_temp_sensor_dict(self, val):
        self.__psu_temp_sensor_dict = val

    @property
    def psu_fanspeed_dict(self):
        self.__psu_fanspeed_dict = {}
        try:
            self.__psu_fanspeed_dict = {}
            self.__psu_fanspeed_dict['Min'] = self.FanSpeed.Min
            self.__psu_fanspeed_dict['Max'] = self.FanSpeed.Max
            self.__psu_fanspeed_dict['Value'] = self.FanSpeed.Value
        except Exception as e:
            self.__psu_fanspeed_dict = None
        return self.__psu_fanspeed_dict

    @psu_fanspeed_dict.setter
    def psu_fanspeed_dict(self, val):
        self.__psu_fanspeed_dict = val

    @property
    def psu_fanspeed_sensor_dict(self):
        self.__psu_fanspeed_sensor_dict = {}
        try:
            self.__psu_fanspeed_sensor_dict = {}
            self.__psu_fanspeed_sensor_dict['Min'] = self.FanSpeed.Min
            self.__psu_fanspeed_sensor_dict['Max'] = self.FanSpeed.Max
            self.__psu_fanspeed_sensor_dict['Value'] = self.FanSpeed.Value
            self.__psu_fanspeed_sensor_dict['Unit'] = self.FanSpeed.Unit
        except Exception as e:
            self.__psu_fanspeed_sensor_dict = None
        return self.__psu_fanspeed_sensor_dict

    @psu_fanspeed_sensor_dict.setter
    def psu_fanspeed_sensor_dict(self, val):
        self.__psu_fanspeed_sensor_dict = val

    @property
    def psu_input_voltage_dict(self):
        self.__psu_input_voltage_dict = {}
        try:
            self.__psu_input_voltage_dict["Value"] = self.InputsVoltage.Value
            self.__psu_input_voltage_dict["LowAlarm"] = self.InputsVoltage.Min
            self.__psu_input_voltage_dict["HighAlarm"] = self.InputsVoltage.Max
            self.__psu_input_voltage_dict["Unit"] = self.InputsVoltage.Unit
        except Exception as e:
            self.__psu_input_voltage_dict = None
        return self.__psu_input_voltage_dict

    @psu_input_voltage_dict.setter
    def psu_input_voltage_dict(self, val):
        self.__psu_input_voltage_dict = val

    @property
    def psu_input_voltage_sensor_dict(self):
        self.__psu_input_voltage_sensor_dict = {}
        try:
            self.__psu_input_voltage_sensor_dict["Value"] = self.InputsVoltage.Value
            self.__psu_input_voltage_sensor_dict["Min"] = self.InputsVoltage.Min
            self.__psu_input_voltage_sensor_dict["Max"] = self.InputsVoltage.Max
            self.__psu_input_voltage_sensor_dict["Unit"] = self.InputsVoltage.Unit
        except Exception as e:
            self.__psu_input_voltage_sensor_dict = None
        return self.__psu_input_voltage_sensor_dict

    @psu_input_voltage_sensor_dict.setter
    def psu_input_voltage_sensor_dict(self, val):
        self.__psu_input_voltage_sensor_dict = val

    @property
    def psu_input_current_dict(self):
        self.__psu_input_current_dict = {}
        try:
            self.__psu_input_current_dict["Value"] = self.InputsCurrent.Value
            self.__psu_input_current_dict["LowAlarm"] = self.InputsCurrent.Min
            self.__psu_input_current_dict["HighAlarm"] = self.InputsCurrent.Max
            self.__psu_input_current_dict["Unit"] = self.InputsCurrent.Unit
        except Exception as e:
            self.__psu_input_current_dict = None
        return self.__psu_input_current_dict

    @psu_input_current_dict.setter
    def psu_input_current_dict(self, val):
        self.__psu_input_current_dict = val

    @property
    def psu_input_current_sensor_dict(self):
        self.__psu_input_current_sensor_dict = {}
        try:
            self.__psu_input_current_sensor_dict["Value"] = self.InputsCurrent.Value
            self.__psu_input_current_sensor_dict["Min"] = self.InputsCurrent.Min
            self.__psu_input_current_sensor_dict["Max"] = self.InputsCurrent.Max
            self.__psu_input_current_sensor_dict["Unit"] = self.InputsCurrent.Unit
        except Exception as e:
            self.__psu_input_current_sensor_dict = None
        return self.__psu_input_current_sensor_dict

    @psu_input_current_sensor_dict.setter
    def psu_input_current_sensor_dict(self, val):
        self.__psu_input_current_sensor_dict = val

    @property
    def psu_input_power_dict(self):
        self.__psu_input_power_dict = {}
        try:
            self.__psu_input_power_dict["Value"] = self.InputsPower.Value
            self.__psu_input_power_dict["LowAlarm"] = self.InputsPower.Min
            self.__psu_input_power_dict["HighAlarm"] = self.InputsPower.Max
            self.__psu_input_power_dict["Unit"] = self.InputsPower.Unit
        except Exception as e:
            self.__psu_input_power_dict = None
        return self.__psu_input_power_dict

    @psu_input_power_dict.setter
    def psu_input_power_dict(self, val):
        self.__psu_input_power_dict = val

    @property
    def psu_input_power_sensor_dict(self):
        self.__psu_input_power_sensor_dict = {}
        try:
            self.__psu_input_power_sensor_dict["Value"] = self.InputsPower.Value
            self.__psu_input_power_sensor_dict["Min"] = self.InputsPower.Min
            self.__psu_input_power_sensor_dict["Max"] = self.InputsPower.Max
            self.__psu_input_power_sensor_dict["Unit"] = self.InputsPower.Unit
        except Exception as e:
            self.__psu_input_power_sensor_dict = None
        return self.__psu_input_power_sensor_dict

    @psu_input_power_sensor_dict.setter
    def psu_input_power_sensor_dict(self, val):
        self.__psu_input_power_sensor_dict = val

    @property
    def psu_output_voltage_dict(self):
        self.__psu_output_voltage_dict = {}
        try:
            self.__psu_output_voltage_dict["Value"] = self.OutputsVoltage.Value
            self.__psu_output_voltage_dict["LowAlarm"] = self.OutputsVoltage.Min
            self.__psu_output_voltage_dict["HighAlarm"] = self.OutputsVoltage.Max
            self.__psu_output_voltage_dict["Unit"] = self.OutputsVoltage.Unit
        except Exception as e:
            self.__psu_output_voltage_dict = None
        return self.__psu_output_voltage_dict

    @psu_output_voltage_dict.setter
    def psu_output_voltage_dict(self, val):
        self.__psu_output_voltage_dict = val

    @property
    def psu_output_voltage_sensor_dict(self):
        self.__psu_output_voltage_sensor_dict = {}
        try:
            self.__psu_output_voltage_sensor_dict["Value"] = self.OutputsVoltage.Value
            self.__psu_output_voltage_sensor_dict["Min"] = self.OutputsVoltage.Min
            self.__psu_output_voltage_sensor_dict["Max"] = self.OutputsVoltage.Max
            self.__psu_output_voltage_sensor_dict["Unit"] = self.OutputsVoltage.Unit
        except Exception as e:
            self.__psu_output_voltage_sensor_dict = None
        return self.__psu_output_voltage_sensor_dict

    @psu_output_voltage_sensor_dict.setter
    def psu_output_voltage_sensor_dict(self, val):
        self.__psu_output_voltage_sensor_dict = val

    @property
    def psu_output_current_dict(self):
        self.__psu_output_current_dict = {}
        try:
            self.__psu_output_current_dict["Value"] = self.OutputsCurrent.Value
            self.__psu_output_current_dict["LowAlarm"] = self.OutputsCurrent.Min
            self.__psu_output_current_dict["HighAlarm"] = self.OutputsCurrent.Max
            self.__psu_output_current_dict["Unit"] = self.OutputsCurrent.Unit
        except Exception as e:
            self.__psu_output_current_dict = None
        return self.__psu_output_current_dict

    @psu_output_current_dict.setter
    def psu_output_current_dict(self, val):
        self.__psu_output_current_dict = val

    @property
    def psu_output_current_sensor_dict(self):
        self.__psu_output_current_sensor_dict = {}
        try:
            self.__psu_output_current_sensor_dict["Value"] = self.OutputsCurrent.Value
            self.__psu_output_current_sensor_dict["Min"] = self.OutputsCurrent.Min
            self.__psu_output_current_sensor_dict["Max"] = self.OutputsCurrent.Max
            self.__psu_output_current_sensor_dict["Unit"] = self.OutputsCurrent.Unit
        except Exception as e:
            self.__psu_output_current_sensor_dict = None
        return self.__psu_output_current_sensor_dict

    @psu_output_current_sensor_dict.setter
    def psu_output_current_sensor_dict(self, val):
        self.__psu_output_current_sensor_dict = val

    @property
    def psu_output_power_dict(self):
        self.__psu_output_power_dict = {}
        try:
            if self.fake != 1:
                self.__psu_output_power_dict["Value"] = self.OutputsPower.Value
            elif self.fake == 1:
                self.__psu_output_power_dict["Value"] = self.OutputsCurrent.Value * self.OutputsVoltage.Value
            self.__psu_output_power_dict["LowAlarm"] = self.OutputsPower.Min
            self.__psu_output_power_dict["HighAlarm"] = self.OutputsPower.Max
            self.__psu_output_power_dict["Unit"] = self.OutputsPower.Unit
        except Exception as e:
            self.__psu_output_power_dict = None
        return self.__psu_output_power_dict

    @psu_output_power_dict.setter
    def psu_output_power_dict(self, val):
        self.__psu_output_power_dict = val

    @property
    def psu_output_power_sensor_dict(self):
        self.__psu_output_power_sensor_dict = {}
        try:
            if self.fake != 1:
                self.__psu_output_power_sensor_dict["Value"] = self.OutputsPower.Value
            elif self.fake == 1:
                self.__psu_output_power_sensor_dict["Value"] = self.OutputsCurrent.Value * self.OutputsVoltage.Value
            self.__psu_output_power_sensor_dict["Min"] = self.OutputsPower.Min
            self.__psu_output_power_sensor_dict["Max"] = self.OutputsPower.Max
            self.__psu_output_power_sensor_dict["Unit"] = self.OutputsPower.Unit
        except Exception as e:
            self.__psu_output_power_sensor_dict = None
        return self.__psu_output_power_sensor_dict

    @psu_output_power_sensor_dict.setter
    def psu_output_power_sensor_dict(self, val):
        self.__psu_output_power_sensor_dict = val

    @property
    def psu_power_status_dict(self):
        dic = {}
        inputdic ={}
        Outputsdic = {}
        dic["Name"] = self.name
        inputdic["Type"] = self.InputsType
        inputdic["Status"] = self.InputStatus
        if self.__InputsVoltage != "fake":
            inputdic["Voltage"] = self.psu_input_voltage_dict
        if self.__InputsCurrent != "fake":
            inputdic["Current"] = self.psu_input_current_dict
        if self.InputsPower != "fake":
            inputdic["Power"] = self.psu_input_power_dict

        Outputsdic["Status"] = self.OutputStatus
        Outputsdic["Voltage"]  = self.psu_output_voltage_dict
        Outputsdic["Current"]  = self.psu_output_current_dict
        Outputsdic["Power"]  = self.psu_output_power_dict
        
        dic["Inputs"] = inputdic
        dic["Outputs"] = Outputsdic
        self.__psu_power_status_dict = dic
        return self.__psu_power_status_dict

    @psu_power_status_dict.setter
    def psu_power_status_dict(self, val):
        self.__psu_power_status_dict = val
    
    @property
    def psu_status_dict(self):
        dic = {}
        dic["Name"] = self.name
        dic["InputType"] = self.InputsType
        if self.Temperature != "fake":
            dic["Temperature"] = self.psu_temp_dict
        if self.FanSpeed is not None and self.FanSpeed != "fake":
            dic["FanSpeed"] = self.psu_fanspeed_dict

        dic["InputStatus"] = self.InputStatus
        dic["OutputStatus"] = self.OutputStatus
        self.__psu_status_dict = dic
        return self.__psu_status_dict

    @psu_status_dict.setter
    def psu_status_dict(self, val):
        self.__psu_status_dict = val

    @property
    def psu_sensor_info_dict(self):
        dic = {}
        if self.Temperature != "fake":
            dic["%s_%s" % (self.name, "TEMP")] = self.psu_temp_sensor_dict
        if self.FanSpeed is not None and self.FanSpeed != "fake":
            dic["%s_%s" % (self.name, "FAN")] = self.psu_fanspeed_sensor_dict
        if self.__InputsVoltage != "fake":
            dic["%s_%s"%(self.name,"Input_V" )] = self.psu_input_voltage_sensor_dict
        if self.__InputsCurrent != "fake":
            dic["%s_%s"%(self.name,"Input_C" )] = self.psu_input_current_sensor_dict
        if self.InputsPower != "fake":
            dic["%s_%s"%(self.name,"Input_P" )] = self.psu_input_power_sensor_dict

        dic["%s_%s"%(self.name,"Output_V" )] = self.psu_output_voltage_sensor_dict
        dic["%s_%s"%(self.name,"Output_C" )] = self.psu_output_current_sensor_dict
        dic["%s_%s"%(self.name,"Output_P" )] = self.psu_output_power_sensor_dict   
        self.__psu_sensor_info_dict = dic
        return self.__psu_sensor_info_dict

    @psu_sensor_info_dict.setter
    def psu_sensor_info_dict(self, val):
        self.__psu_sensor_info_dict = val

    def __str__(self):
        formatstr =  \
                "name                : %s \n" \
                "productManufacturer : %s \n" \
                "productName         : %s \n" \
                "productPartModelName: %s \n" \
                "productVersion      : %s \n" \
                "productSerialNumber : %s \n" \
                "AirFlow             : %s \n" \

        tmpstr = formatstr % (self.name, self.productManufacturer,
                                self.productName, self.productPartModelName,
                                self.productVersion, self.productSerialNumber, self.AirFlow)
        return tmpstr

    def get_fan_speed_pwm(self):

        if self.fake == 1:
            return 0
        selfconfig = {}
        selfconfig['bus'] = self.pmbus['bus']
        selfconfig['addr'] = self.pmbus['addr']
        selfconfig['way'] = 'i2cword'
        selfconfig['offset'] = 0x3b
        ret, val = self.get_value(selfconfig)
        if ret == True:
            return val
        else:
            return None

    def set_fan_speed_pwm(self, pwm):
        '''
            pmbus
                if duty:
                 i2cset -f -y 0x3b 0x0064  wp
        '''
        if self.fake == 1:
            return True
        if 0 <= pwm <= 100:
            '''enable duty first '''
            selfconfig = {}

            selfconfig['bus'] = self.pmbus['bus']
            selfconfig['addr'] = self.pmbus['addr']
            selfconfig['way'] = 'i2cpec'
            selfconfig['offset'] = 0x3a
            ret , val = self.set_value(selfconfig, 0x80)

            selfconfig['way'] = 'i2cwordpec'
            selfconfig['offset'] = 0x3b
            bytetmp = pwm
            ret , val = self.set_value(selfconfig, bytetmp)
            if ret == True:
                return True
            else:
                return None
        else:
            raise Exception("pwm not in range [0,100]")

    def isnumberorletter(self, asciinum):
        if asciinum >= ord('0') and asciinum <= ord('9'):
            return True
        elif asciinum >=ord('a') and asciinum <= ord('z'):
            return True
        elif asciinum >=ord('A') and asciinum <= ord('Z'):
            return True
        elif asciinum == ord('-') or asciinum == ord(' '):
            return True
        return False

    def list2str(self, block_data):
        res = ""
        for i in range(len(block_data)):
            if self.isnumberorletter(block_data[i]):
                res += chr(block_data[i])
        return res.strip()

    def get_digital_label(self, offset):
        bus = self.pmbus.get('bus')
        addr = self.pmbus.get("addr")
        ret, res = self.get_i2cblock(bus, addr, offset)
        target = self.list2str(res)
        return target

    def get_product_info_pmbus(self):
        self.productManufacturer = self.get_digital_label(0x99)
        self.productPartModelName = self.get_digital_label(0x9a)
        self.productSerialNumber = self.get_digital_label(0x9e)
        self.productVersion = self.get_digital_label(0x9b)

    def change_psu_info_way(self):
        self.e2loc["way"] = "pmbus"
        self.get_product_info_pmbus()

    def get_product_info_eeprom(self):
        eeprom = self.get_eeprom_info(self.e2loc)
        if eeprom is None:
            self.change_psu_info_way()
            return
        fru = ipmifru()
        fru.decodeBin(eeprom)
        if fru.productInfoArea is not None:
            self.productManufacturer = fru.productInfoArea.productManufacturer.strip()
            self.productName         = fru.productInfoArea.productName.strip()
            self.productPartModelName= fru.productInfoArea.productPartModelName.strip()
            self.productVersion      = fru.productInfoArea.productVersion.strip()
            self.productSerialNumber = fru.productInfoArea.productSerialNumber.strip().replace(chr(0),"")
        # AS13-32H, AS13-48F8H, AS23-128H, AS14-128H PSU JUDGE METHOD
        if self.productPartModelName is None:
            self.change_psu_info_way()
            return
        else:
            for i in self.AirFlowconfig:
                if self.productPartModelName in self.AirFlowconfig[i]:
                    return
            self.change_psu_info_way()

    def get_fru_info(self):
        try:
            if self.present == False:
                raise Exception("%s: not present" % self.name)
            if self.fake == 1:
                self.productManufacturer = "Builtin"
                self.productName         = "Builtin"
                self.productPartModelName= "Builtin"
                self.productVersion      = "Builtin"
                self.productSerialNumber = "Builtin"
                return True
            if self.e2loc.get('way') == 'pmbus':
                self.get_product_info_pmbus()
            else:
                self.get_product_info_eeprom()
        except Exception as e:
            self.productManufacturer = None
            self.productName         = None
            self.productPartModelName= None
            self.productVersion      = None
            self.productSerialNumber = None
            return False
        return True

    def get_d2_airflow(self, res):
        return ((res >> 3) & 0b11)

    def get_airflow_pmbus(self):
        bus = self.pmbus.get('bus')
        addr = self.pmbus.get("addr")
        ret, res = self.geti2c(bus, addr, 0xd2)
        res = self.get_d2_airflow(res)
        if res == 0b01:
            self.AirFlow = "F2B"
        elif res == 0b10:
            self.AirFlow = "B2F"
        else:
            if self.AirFlowconfig == None:
                self.AirFlow = None
                return False
            else:
                for i in self.AirFlowconfig:
                    if self.productPartModelName in self.AirFlowconfig[i]:
                        self.AirFlow = i
                        return True
            self.AirFlow = "LIQUID"
        if self.AirFlow == None:
            return False
        else:
            return True

    def get_airflow_eeprom(self):
        if self.productPartModelName  == None:
            ret = self.get_fru_info()
            if ret is False:
                self.AirFlow = None
                return False
        if self.AirFlowconfig == None:
            self.AirFlow = None
            return False
        else:
            for i in self.AirFlowconfig:
                if self.productPartModelName in self.AirFlowconfig[i]:
                    self.AirFlow = i
                    return True
            self.get_airflow_pmbus()
        if self.AirFlow == None:
            return False
        else:
            return True

    def get_AirFlow(self):
        try:
            if self.present == False:
                raise Exception("%s: not present" % self.name)
            if self.fake == 1:
                self.AirFlow = self.AirFlowconfig.get("type","F2B")
                return True
            if self.e2loc.get('way') == 'pmbus':
                self.get_airflow_pmbus()
            else:
                self.get_airflow_eeprom()
        except Exception as e:
            self.AirFlow = None
            return False
        return True
