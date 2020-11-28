# This Python file uses the following encoding: utf-8

#from PySide2.QtGui import QGuiApplication
#from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtCore import Property as QtProperty
# from PyQt5.QtCore import QObject
# from PyQt5.QtGui import QGuiApplication
# from PyQt5.QtQml import QQmlApplicationEngine
import time
import numpy as np
import random
import logging
import threading

class UIsignal(QObject):
    
    def __init__(self):
        super().__init__()
        self.__joint_pose = []
        self.__tcp_pose = []
        self.__tcp_speed = 0
        self.__joint_speed = 0
        self.__tcp_switch = True
        self.__joint_switch = True
        self.__rvRpy_index = 1

    # PyQt5:   list可以被识别
    # PySide2: list不可以被识别, 需定义为QVariantList
    #          或者定义为QVariant，然后toVariant转换为<class 'list'>
    # Signal()定义信号。@Slot定义槽函数
    # 正常来讲，@Slot不是必须的，当参数类型或返回值不是python里面标准的类型，比如是qml里的类型，是必须的
    # @Slot('QVariant', result=list) .toVariant()
    # @Slot(result='QVariant')  
    # def returnDict(self, ):
    #     return {"a": 1, "b": 2} # 键必须是字符串
    
    # Property: tcpPose; 6 dimemsion vector/list [mm, degree]
    # the numbers in list must be in float type, can not be numpy.float64
    tcpPoseRevised = Signal('QVariantList')
    def __set_tcppose(self, val):
        if self.__tcp_pose != val:
            self.__tcp_pose = val
            self.tcpPoseRevised.emit(self.__tcp_pose)
    def __get_tcppose(self):
        return self.__tcp_pose
    tcpPose = QtProperty('QVariantList', __get_tcppose, __set_tcppose, notify=tcpPoseRevised)
    
    # Property: jointPose; 6 dimemsion vector/list [degree]
    jointPoseRevised = Signal('QVariantList')
    def __set_jointpose(self, val):
        if self.__joint_pose != val:
            self.__joint_pose = val
            self.jointPoseRevised.emit(self.__joint_pose)
    def __get_jointpose(self):
        return self.__joint_pose
    jointPose = QtProperty('QVariantList', __get_jointpose, __set_jointpose, notify=jointPoseRevised)
    
    # Property: jointSpeed  unit: percent
    jointSpeedRevised = Signal(int)
    def __set_jointspeed(self, val):
        if self.__joint_speed != val:
            self.__joint_speed = val
            self.jointSpeedRevised.emit(self.__joint_speed)
            # print('python in set_jointspeed',self.__joint_speed)
    def __get_jointspeed(self):
#         print('python in ',self.__joint_speed)
         return self.__joint_speed
    jointSpeed = QtProperty(int, __get_jointspeed, __set_jointspeed, notify=jointSpeedRevised)
    
    # Property: tcpSpeed    unit: percent
    tcpSpeedRevised = Signal(int)
    def __set_tcpspeed(self, val):
        if self.__tcp_speed != val:
            self.__tcp_speed = val
            self.tcpSpeedRevised.emit(self.__tcp_speed)
    def __get_tcpspeed(self):
        return self.__tcp_speed
    tcpSpeed = QtProperty(int, __get_tcpspeed, __set_tcpspeed, notify=tcpSpeedRevised)
    
    # Property: tcpSwitch         # switch_tcp_checked   
    tcpSwitchChecked = Signal(bool)
    def __set_switch_tcp(self, val):
        if self.__tcp_switch != val:
            self.__tcp_switch = val
            self.tcpSwitchChecked.emit(self.__tcp_switch)
    def __get_switch_tcp(self):
        return self.__tcp_switch
    tcpSwitch = QtProperty(bool, __get_switch_tcp, __set_switch_tcp, notify=tcpSwitchChecked)
    
    # Property: jointSwitch
    jointSwitchChecked = Signal(bool)
    def __set_switch_joint(self, val):
        if self.__joint_switch != val:
            self.__joint_switch = val
            self.jointSwitchChecked.emit(self.__joint_switch)
    def __get_switch_joint(self):
        return self.__joint_switch
    jointSwitch = QtProperty(bool, __get_switch_joint, __set_switch_joint, notify=jointSwitchChecked)
    
    # Property: jointSwitch
    rvRpyIndexActivated = Signal(int)
    def __set_rvRpy_index(self, val):
        if self.__rvRpy_index != val:
            self.__rvRpy_index = val
            self.rvRpyIndexActivated.emit(self.__rvRpy_index)
    def __get_rvRpy_index(self):
        return self.__rvRpy_index
    rvRpyIndex = QtProperty(int, __get_rvRpy_index, __set_rvRpy_index, notify=rvRpyIndexActivated)
    
    setRobotMode = Signal(int)
    def set_robot_mode(self, index: int):
        self.setRobotMode.emit(index)
        
    setSafeMode = Signal(int)
    def set_safe_mode(self, index: int):
        self.setSafeMode.emit(index)


