#!/usr/bin/env python
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
import operator

try:
    from plat_utils.plat_common_util import *
    from plat_hal.interface import interface
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

def usage():
    print("usage:")
    print("    platformutil.py fan|psu|sensor|event num|status")
    exit()

def get_fan_all(int_case):
    fan_dict = {}
    fan_info = int_case.get_fan_info_all()
    fan_nr = fan_info.get("Number", 0)
    if fan_nr == 0:
        print("Number of fans is 0")
        return None
    for fan_idx in range(1, fan_nr+1):
        fan_name = "FAN%d" % fan_idx
        if not fan_name in fan_info:
            print("%s not in fan_info" % fan_name)
            continue
        fi = fan_info[fan_name]
        if "Rotors" not in fi:
            print("Rotors not found")
            continue
        rotor_nr = fi["Rotors"]
        for ridx in range(1, rotor_nr+1):
            sub_name = "%s_%d" % (fan_name, ridx)
            rname = "Rotor%d" % ridx
            sub_fan_info = {}
            if rname not in fi:
                print("%s not found" % rname)
                continue
            try:
                sub_fan_info["Present"] = True if fi["Present"] == "yes" else False
                sub_fan_info["Running"] = fi[rname]["Running"]
                sub_fan_info["Speed"] = fi[rname]["Speed"]
                sub_fan_info["LowThd"] = fi[rname]["SpeedMin"]
                sub_fan_info["HighThd"] = fi[rname]["SpeedMax"]
                sub_fan_info["PN"] = fi["PN"]
                sub_fan_info["SN"] = fi["SN"]
                sub_fan_info["AirFlow"] = fi["AirFlow"]
                sub_fan_info["Status"] = True if fi[rname]["HwAlarm"] == "no" else False

                fan_dict[sub_name] = sub_fan_info
            except Exception as e:
                print("GOT EXCEPTON: %s" % str(e))
                continue
    rotor_per_fan = fan_info["FAN1"]["Rotors"]
    fan_dict["Number"] = fan_nr * rotor_per_fan
    return fan_dict

def get_fan_status(int_case):
    formatstr = "%%-%ds %%-10s %%-8s %%-10s %%-10s %%-10s %%-20s %%-16s %%-10s"%(8)
    fan_dict = get_fan_all(int_case)
    if fan_dict == None:
        print('Error: get fan status failed')
        return

    fan_nr = fan_dict.get('Number')
    if fan_nr == None:
        print("Error: FAN get all format invalid, prop Number missing")
        return
    status_table = []
    status_table.append([formatstr%("FAN", "Presence", "Status", "Speed", "LowThd", "HighThd", "PN", "SN", "AirFlow")])
    status_table.append([formatstr%("-----", "--------", "------", "-----", "------", \
                        "-------", "----------------", "-------------", "-------")])
    fan_names = [ k for k in fan_dict.keys() if operator.eq('Number', k) == False and operator.eq('WatchdogStatus', k) == False ]
    fan_names.sort()
    for fan_name in fan_names:
        fan = fan_dict[fan_name]
        presence = fan.get('Present')
        speed = fan.get('Speed')
        low = fan.get('LowThd')
        high = fan.get('HighThd')
        pn = fan.get('PN')
        sn = fan.get('SN')
        status = fan.get('Status')
        airflow = fan.get('AirFlow')

        if presence == None:
            print('Error: FAN get all format invaid, prop "Present" missing.')
            continue
        elif presence == False:
            presence = 'NOT_PRESENT'
            status = 'N/A'
            speed = 'N/A'
            low = 'N/A'
            high = 'N/A'
            pn = 'N/A'
            sn = 'N/A'
            airflow = 'N/A'
        else:
            presence = 'PRESENT'
            if status == None:
                status = 'N/A'
            elif status == True:
                status = 'OK'
            else:
                status = 'NOT_OK'
            if airflow == None:
                airflow = 'N/A'
            if speed == None:
                speed = 'N/A'
            if low == None:
                low = 'N/A'
            if high == None:
                high = 'N/A'
            if pn == None:
                pn = 'N/A'
            if sn == None:
                sn = 'N/A'
        status_table.append([formatstr%(str(fan_name), str(presence), str(status), str(speed), str(low), str(high), str(pn), str(sn), str(airflow))])

    if len(status_table) - 2 != fan_nr:
        print('Error: FAN get all missing some FAN information.')

    if len(status_table) > 0:
        return status_table

def get_psu_all(int_case):
    psu_dict = {}
    psu_info = int_case.get_psu_info_all()

    if "Number" not in psu_info:
        return psu_dict

    psu_nr = psu_info["Number"]
    psu_dict["Number"] = psu_nr
    for idx in range(1, psu_nr+1):
        psu_name = "PSU%d" % idx
        if not psu_name in psu_info:
            print("%s not in psu_info" % psu_name)
            continue

        pi = psu_info[psu_name]
        pinfo = {}
        try:
            pinfo["Present"] = True if pi["Present"] == "yes" else False
            pinfo["AirFlow"] = pi["AirFlow"]
            pinfo["PN"] = pi["PN"]
            pinfo["SN"] = pi["SN"]
        except Exception as e:
            print("%s not in psu_info, exception 1" % psu_name)
            continue

        if "Inputs" in pi:
            pii = pi["Inputs"]
            if "Status" in pii:
                try:
                    pinfo["InputStatus"] = pii["Status"]
                    pinfo["InputType"] = pii["Type"]
                except Exception as e:
                    pinfo["InputType"] = "N/AA"

        if "Outputs" in pi:
            pio = pi["Outputs"]
            if "Status" in pio:
                try:
                    pinfo["OutputStatus"] = pio["Status"]
                except Exception as e:
                    pinfo["OutputStatus"] = False

        if "FanSpeed" in pi:
            pif = pi["FanSpeed"]
            try:
                pinfo["Speed"] = pif["Value"]
                pinfo["LowThd"] = pif["Min"]
                pinfo["HighThd"] = pif["Max"]
            except Exception as e:
                pinfo["Speed"] = 0
                pinfo["LowThd"] = 0
                pinfo["HighThd"] = 0

        psu_dict[psu_name] = pinfo

    return psu_dict

def get_psu_status(int_case):
    formatstr = "%%-%ds %%-10s %%-15s %%-15s %%-15s %%-20s %%-20s %%-10s"%(8)
    psu_dict = get_psu_all(int_case)
    if psu_dict == None:
        print("Error: get_pus_all failed")
        return

    psu_nr = psu_dict.get('Number')
    if psu_nr == None:
        print('Error: PSU get all format invalid, prop "Number" missing.')
        return

    psu_names = [ k for k in psu_dict.keys() if operator.eq('Number', k) == False ]
    psu_names.sort()
    status_table = []
    status_table.append([formatstr%("PSU", "Presence", "InputStatus", "InputType", "OutputStatus", "PN", "SN", "AirFlow")])
    status_table.append([formatstr%("----", "--------", "-----------", "----------", \
                                    "------------", "--------------", "--------------", "--------")])
    for psu_name in psu_names:
        psu = psu_dict[psu_name]
        presence = psu.get('Present')
        pn = psu.get('PN')
        sn = psu.get('SN')
        in_status = psu.get('InputStatus')
        out_status = psu.get('OutputStatus')
        in_type = psu.get('InputType')
        airflow = psu.get('AirFlow')

        if presence == None:
            print('Error: PSU get all format invaid, prop "Present" is missing.')
            continue
        elif presence == False:
            presence = 'NOT_PRESENT'
            in_status = 'N/A'
            out_status = 'N/A'
            in_type = 'N/A'
            pn = 'N/A'
            sn = 'N/A'
        else:
            presence = 'PRESENT'
            if in_status == None:
                in_status = 'N/A'
            elif in_status == True:
                in_status = 'OK'
            else:
                in_status = 'NOT_OK'

            if in_type == None:
                in_type = 'N/A'

            if out_status == None:
                out_status = 'N/A'
            elif out_status == True:
                out_status = 'OK'
            else:
                out_status = 'NOT_OK'

            if pn == None:
                pn = 'N/A'
            if sn == None:
                sn = 'N/A'
            if airflow == None:
                airflow = 'N/A'
        status_table.append([formatstr%(str(psu_name), str(presence), str(in_status),\
                                 str(in_type), str(out_status), str(pn), str(sn), str(airflow))])

    if len(status_table) - 2 != psu_nr:
        print('Error: PSU get all missing some PSU information.')

    if len(status_table) > 0:
        return status_table

def get_type(unit_str):
    unit2type = {"C": "temperature", "A": "amp", "V": "voltage",
                    "RPM": "RPM", "W": "power", "mOHM": "resistance"}

    if unit_str in unit2type:
        return unit2type[unit_str]
    return None

def get_sensors_info(int_case):
    sensor_dict = {}
    sensor_info = int_case.get_sensor_info()
    sname_temp_cl = ["Cpu", "Inlet", "Switch"]
    sname_temp_rj = ["CPU_TEMP", "INLET_TEMP", "SWITCH_TEMP"]
    for si_name, si_val in sensor_info.items():
        if si_name.startswith("PSU"):
            sname = si_name.split("_")[0]
            if si_name.find("Temperature") != -1:
                new_si_name = "%s_TEMP" % sname
                si_name = new_si_name
        elif si_name in sname_temp_cl:
            sname = "TEMPERATURE"
            new_si_name = "%s_temp" % si_name
            si_name = new_si_name.upper()
        elif si_name in sname_temp_rj:
            sname = "TEMPERATURE"
        elif si_name.startswith("CPU"):
            sname = "CPU"
        elif si_name.startswith("FAN"):
            sname = "FAN"
        elif si_name.startswith("Switch") or \
                si_name.startswith("SWITCH") or \
                si_name.find("_LC_") != -1:
                sname = "SWITCH"
        elif si_name.startswith("SYS") or \
                si_name.startswith("Baseboard"):
            sname = "SYSTEM"
        else:
            sname = "OTHER"

        si_info = {}
        si_info["LowThd"] = si_val["Min"]
        si_info["HighThd"] = si_val["Max"]
        si_info["Value"] = si_val["Value"]
        type = get_type(si_val["Unit"])
        if not type:
            continue
        si_info["Type"] = type

        if sname not in sensor_dict:
            sensor_dict[sname] = {}
        sensor_dict[sname][si_name] = si_info
    return sensor_dict

def get_sensors_num(int_case):
    sensor_dict = get_sensors_info(int_case)
    sum = 0
    for sensor_name, sensor_obj in sensor_dict.items():
        if operator.eq(sensor_name, 'Number') == True:
            continue
        sum += len(sensor_obj.keys())
    return sum

def get_sensors_status(int_case):
    formatstr = "%%-%ds %%-25s %%-10s %%-18s %%-18s %%-18s"%(15)
    sensor_dict = get_sensors_info(int_case)
    if sensor_dict == None:
        print('Error: get_sensors_all failed')
        return

    status_table = []
    status_table.append([formatstr%("Sensor", "InputName", "State", "Value", "LowThd", "HighThd")])
    status_table.append([formatstr%("-----------", "----------------", "---------", \
                                    "--------------", "---------------", "---------------")])
    type2unit = { 'temperature' : ' C', 'voltage' : ' V', 'RPM' : ' RPM', 'amp' : ' A', \
                    'power' : ' W', 'resistance' : ' mOHM'}
    type_keys = type2unit.keys()
    for sensor_name, sensor_obj in sensor_dict.items():
        if operator.eq(sensor_name, 'Number') == True:
            continue

        si_names = [ k for k in sensor_obj.keys() ]
        si_names.sort()
        for si_name in si_names:
            si = sensor_obj[si_name]
            #print si_name, ":", si
            if si_name == "Sys_AirFlow":
                status = 'OK'
                airflow = si
                status_table.append([formatstr%(sensor_name, si_name, status,\
                                 str(airflow), str(airflow), str(airflow))])
                continue

            stype = si.get('Type')
            sval = si.get('Value')
            slow = si.get('LowThd')
            shigh = si.get('HighThd')
            sunit = ' '
            fault = False
            if stype != None:
                sunit = type2unit.get(stype)
                if sunit == None:
                    sunit = ' '
            try:
                sval = '%.3f'%float(sval)
            except:
                sval = 0.0
                fault = True

            try:
                slow = '%.3f'%float(slow)
            except:
                slow = 0.0
                fault = True

            try:
                shigh = '%.3f'%float(shigh)
            except:
                shigh = 0.0
                fault = True

            status = 'NOT_OK'
            if fault == False and float(sval) > float(slow) and float(sval) < float(shigh):
                status = 'OK'
            status_table.append([formatstr%(sensor_name, si_name, status,\
                                 (str(sval)+sunit), (str(slow)+sunit), (str(shigh)+sunit))])
    if len(status_table) > 0:
        return status_table

def get_event_num(int_case):
    event_dict = int_case.get_evst_info_all()
    return event_dict["Number"]

def get_event_status(int_case):
    event_dict = int_case.get_evst_info_all()
    status_table = []
    if event_dict == None:
        print('Error: get event status failed')
        return status_table
    event_nr = event_dict.get('Number')
    if event_nr == None:
        print("Error: Event get all format invalid, prop Number missing")
        return status_table
    if event_nr == 0:
        print("Number of events is 0")
        return status_table
    status_table = []
    status_table.append(["Name", "Description", "Status", "Value", "RW"])
    event_names = [ k for k in event_dict.keys() if operator.eq('Number', k) == False ]
    event_names.sort()
    for event_name in event_names:
        event_info = event_dict[event_name]
        desc = event_info["Descr"]
        value = event_info["Decoder"].get(event_info["Value"], "UnDecoder")
        rw = event_info["RW"]
        status = "NORMAL" if event_info["Value"] in event_info["Expects"] else "ALARM"
        status_table.append([str(event_name), str(desc), str(status), str(value), str(rw)])
    if len(status_table) - 1 != event_nr:
        print('Error: Event get all missing some Event information.')
    return status_table

def formatted_table_output(status_table):
    if len(status_table) == 0:
        return
    max_widths = [max(len(str(item)) for item in column) for column in zip(*status_table)]
    row_separator = "-"
    column_separator = "    "
    for rindex, row in enumerate(status_table):
        formatted_row = column_separator.join("{:<{}}".format(column, max_widths[cindex]) \
            for cindex, column in enumerate(row))
        print(formatted_row)
        if rindex == 0:
            separator_row = column_separator.join(row_separator * width for width in max_widths)
            print(separator_row)
    return

def str_format_adjust(status_table):
    name = []
    if status_table == None:
        return None
    for table in status_table[0:2]:
        print("".join(table))
    for table in status_table[2:]:
        name.append("".join(table).split(" ")[0])
    name = list(set(name))
    name.sort()
    for k in name:
        for table in status_table[2:]:
            name_table = "".join(table)
            if k in name_table.split(" ")[0]:
                print(name_table)
    return None

if __name__ == "__main__":
    platutil = PlatCommonUtil()
    int_case = interface()
    try:
        args = platutil.Argparser(['name', 'type'],
                              [str, str],
                              ['Name : fan|psu|sensor',
                               'Type : num|status'],
                              [False, True])
        if args.name == "fan":
            if args.type == "num":
                print(int_case.get_fan_total_number())
            elif args.type == "status":
                status_table = get_fan_status(int_case)
                str_format_adjust(status_table)
            else:
                usage()
        elif args.name == "psu":
            if args.type == "num":
                print(int_case.get_psu_total_number())
            elif args.type == "status":
                status_table = get_psu_status(int_case)
                str_format_adjust(status_table)
            else:
                usage()
        elif args.name == "sensor":
            if args.type == "num":
                print(get_sensors_num(int_case))
            elif args.type == "status":
                status_table = get_sensors_status(int_case)
                str_format_adjust(status_table)
            else:
                usage()
        elif args.name == "event":
            if args.type == "num":
                print(get_event_num(int_case))
            elif args.type == "status":
                status_table = get_event_status(int_case)
                formatted_table_output(status_table)
            else:
                usage()
        else:
            usage()
    except Exception as e:
        print("Error returned: " + str(e))
