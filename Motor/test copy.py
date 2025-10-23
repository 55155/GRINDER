#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Hardware] Vial Storage file
# @author   Hyuk Jun Yoo (yoohj9475@kist.re.kr)   
# @version  1_1   
# TEST 2021-09-11
import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Stirrer/serial_labware")))
from Log.Logging_Class import NodeLogger
import serial
import time

class ParamterVialStorage(object):
    def __init__(self):
        # serial settings
        self.info={
            "DeviceName":"VialStorage",
            "Port":"COM3",
            "BaudRate":9600
        }
  

class VialStorage(ParamterVialStorage):
    """
    [VialStorage] VialStorage Class for controlling in another computer (windows)

    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name="Vial_Storage" (string): set Storage model name (log name)
    :param PORT="COM9" (str): set LA model name (log name)
    :param BaudRate=9600 (int) 
    :param mode_type="virtual" (str): set virtual or real mode

    # function
    1. vial_Entrance(entrance_num, mode_type="virtual")
    """
    def __init__(self, logger_obj, device_name="VialStorage"):
        ParamterVialStorage.__init__(self,)
        self.logger_obj=logger_obj
        self.device_name=device_name
        self.arduinoData = serial.Serial(self.info["Port"], self.info["BaudRate"])

    def heartbeat(self):
        self.arduinoData.write("5".encode())
        time.sleep(2)
        self.arduinoData.write("-5".encode())
        debug_msg="Hello World!! Succeed to connection to main computer!"
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)

        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg

    def openEntrance(self, action_type, entrance_num, mode_type="virtual"):
        """
        control vial storage's Entrance (1,2,3,4,5 : Bottom Site (Empty Vial)) (6,7,8,9,10 : Top Site (Full Vial))

        :param action_type="open" (str): set action type
        :param entrance_num (int): Entrance Number
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: return_res_msg => [Vial Storage ({mode_type})] : ~~
        """
        device_name="{} ({})".format(self.device_name, mode_type)
        if mode_type=="real":
            debug_msg="open {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)

            time.sleep(2)
            value = entrance_num
            # self.send_message(message=str(value))
            self.arduinoData.write(value.encode())
            if int(entrance_num) <=5:
                time.sleep(3)
            else:
                time.sleep(5)
            # value = "-"+entrance_num
            # self.arduinoData.write(value.encode())
            # # self.send_message(message=str(value))
            # time.sleep(3)
            # # self.arduinoData.close()

            debug_msg="Finished to open {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            
            return_res_msg="[{}] : {}".format(device_name, debug_msg)
            return return_res_msg

        elif mode_type=="virtual":
            debug_msg="{} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            debug_msg="Finished to open {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)

            return_res_msg="[{}] : {}".format(device_name, debug_msg)
            return return_res_msg
        
    def closeEntrance(self, action_type, entrance_num, mode_type="virtual"):
        """
        control vial storage's Entrance (1,2,3,4,5 : Bottom Site (Empty Vial)) (6,7,8,9,10 : Top Site (Full Vial))

        :param action_type="open" (str): set action type
        :param entrance_num (int): Entrance Number
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: return_res_msg => [Vial Storage ({mode_type})] : ~~
        """
        device_name="{} ({})".format(self.device_name, mode_type)
        if mode_type=="real":
            debug_msg="close {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)

            time.sleep(3)
            value = "-"+entrance_num
            self.arduinoData.write(value.encode())
            # self.send_message(message=str(value))
            # self.arduinoData.close()

            debug_msg="Finished to close {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            
            return_res_msg="[{}] : {}".format(device_name, debug_msg)
            return return_res_msg

        elif mode_type=="virtual":
            debug_msg="{} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            debug_msg="Finished to close {} {} entrance".format(action_type, entrance_num)
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)

            return_res_msg="[{}] : {}".format(device_name, debug_msg)
            return return_res_msg

if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(platform_name="Vial Storage (test)", setLevel="DEBUG", SAVE_DIR_PATH="Log")
    vialstorage_obj=VialStorage(NodeLogger_obj, device_name="Vial Storage")
    for i in range(0,5):
        i = str(i)
    # vialstorage_obj.heartbeat()
        # vialstorage_obj.openEntrance(action_type="open",entrance_num=i, mode_type="real")
    # vialstorage_obj.closeEntrance("close", "0", mode_type="real")
    time.sleep(2)
    # vialstorage_obj.closeEntrance("close", "1", mode_type="real")
    # vialstorage_obj.openEntrance("2", mode_type="real")
    # vialstorage_obj.openEntrance("3", mode_type="real")
    # vialstorage_obj.openEntrance("4", mode_type="real")
    # vialstorage_obj.openEntrance("open", "0", mode_type="real")
    # vialstorage_obj.openEntrance("open", "1", mode_type="real")
    # vialstorage_obj.openEntrance("open", "2", mode_type="real")
    # vialstorage_obj.openEntrance("open", "3", mode_type="real")
    # vialstorage_obj.openEntrance("open", "4", mode_type="real")
    vialstorage_obj.openEntrance("open", "5", mode_type="real")
    vialstorage_obj.openEntrance("open", "6", mode_type="real")
    vialstorage_obj.openEntrance("open", "7", mode_type="real")
    vialstorage_obj.openEntrance("open", "8", mode_type="real")
    vialstorage_obj.openEntrance("open", "9", mode_type="real")

    # vialstorage_obj.closeEntrance("close", "0", mode_type="real")
    # vialstorage_obj.closeEntrance("close", "1", mode_type="real")
    # vialstorage_obj.closeEntrance("close", "2", mode_type="real")
    # vialstorage_obj.closeEntrance("close", "3", mode_type="real")
    # vialstorage_obj.closeEntrance("close", "4", mode_type="real")
    vialstorage_obj.closeEntrance("close", "5", mode_type="real")
    vialstorage_obj.closeEntrance("close", "6", mode_type="real")
    vialstorage_obj.closeEntrance("close", "7", mode_type="real")
    vialstorage_obj.closeEntrance("close", "8", mode_type="real")
    vialstorage_obj.closeEntrance("close", "9", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("1", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("2", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("3", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("4", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("5", mode_type="real")
    # for _ in range(0,16):
    #     vialstorage_obj.openEntrance("6", mode_type="real")
    # vialstorage_obj.openEntrance("7", mode_type="real")
    # vialstorage_obj.openEntrance("8", mode_type="real")
    # vialstorage_obj.openEntrance("9", mode_type="real")
    # vialstorage_obj.openEntrance("10", mode_type="real")