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
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "../Stirrer/serial_labware"))) # path 설
from Log.Logging_Class import NodeLogger
import serial
import time
from pymodbus.client import ModbusSerialClient

class ParamterMotorController(object):
    def __init__(self):
        # serial settings
        self.info={
            "DeviceName":"MotorController",
            "Port":"/dev/ttyACM0",
            "BaudRate":115200
        }
  

class MotorController(ParamterMotorController):
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
    def __init__(self, logger_obj, device_name="MotorController"):
        ParamterMotorController.__init__(self,)
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

    def read_register(self, address, count=1):
        try:
            with self.lock:
                response = self.client.read_holding_registers(address=address, count=count, slave=self.device_id)
            if response and not response.isError():
                return response.registers[0] if count == 1 else response.registers
        except:
            pass
        return None

    def write_register(self, address, value):
        try:
            with self.lock:
                response = self.client.write_register(address=address, value=value, slave=self.device_id)
            if response and not response.isError():
                return True
        except:
            pass
        return False

    def set_speed(self, speed):
        print("..")
        if 0 <= speed <= 100:
            return self.write_register(0x0001, speed)
        return False

    def set_cw_ccw(self, direction):
        if direction in [0, 1]:
            return self.write_register(0x0002, direction)
        return False

    def set_enable(self, enable):
        if enable in [0, 1]:
            return self.write_register(0x0003, enable)
        return False

    def set_brake(self, brake):
        if brake in [0, 1]:
            return self.write_register(0x0004, brake)
        return False

    def get_current_RPM(self):
        return self.read_register(0x0015)
    
    # Action
    def startMotor(self, speed=50, direction=1, motor_id=1, mode_type="virtual"):
        device_name = "Motor {} ({})".format(motor_id, mode_type)
        if mode_type == "real":
            self.logger_obj.debug(device_name=device_name, debug_msg="Starting motor...")
            time.sleep(4)
            self.set_speed(speed)
            time.sleep(4)
            self.set_cw_ccw(direction)
            time.sleep(4)
            self.set_brake(0)
            time.sleep(4)
            self.set_enable(1)
            time.sleep(4)
            rpm = self.get_current_RPM()
            debug_msg = f"Motor started with speed: {speed}, direction: {direction}, current RPM: {rpm}"
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            return "[{}] : {}".format(device_name, debug_msg)
        else:
            debug_msg = f"(VIRTUAL) Motor started with speed={speed}, direction={direction}"
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            return "[{}] : {}".format(device_name, debug_msg)

    def stopMotor(self, motor_id=1, mode_type="virtual"):
        device_name = "Motor {} ({})".format(motor_id, mode_type)
        if mode_type == "real":
            self.logger_obj.debug(device_name=device_name, debug_msg="Stopping motor...")
            self.set_enable(0)
            self.set_brake(1)
            rpm = self.get_current_RPM()
            debug_msg = f"Motor stopped with current RPM: {rpm}"
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            return "[{}] : {}".format(device_name, debug_msg)
        else:
            debug_msg = "(VIRTUAL) Motor stopped"
            self.logger_obj.debug(device_name=device_name, debug_msg=debug_msg)
            return "[{}] : {}".format(device_name, debug_msg)
        

if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(platform_name="MotorController (test)", setLevel="DEBUG", SAVE_DIR_PATH="Log")
    MotorController_obj=MotorController(NodeLogger_obj, device_name="MotorController")
    MotorController_obj.set_speed(speed=10)
    MotorController_obj.startMotor(speed=70, direction=1, mode_type="real")
    # time.sleep(3)
    # MotorController_obj.stopMotor(mode_type="real")
