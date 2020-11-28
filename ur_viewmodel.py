import ur_controller
import urgui
import time
import sys
import os
import threading
import logging
import numpy as np
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QObject, QUrl # Signal, Slot
from PySide2.QtQuick import QQuickView
# from PySide2.QtCore import Property as QtProperty
import ur_visual

class RepeatingTimer(threading.Timer):
    # 循环定时器类
    # def __init__(self, interval, function, args=None, kwargs=None):  
    # 初始化的时候传参是延迟时间、调用的函数，函数的可变位置参数、函数的可变关键字参数
    def run(self):
        while (not self.finished.is_set()) and self.function(*self.args, **self.kwargs) :
            self.finished.wait(self.interval)
        else:
            # logging.warning('Function returns False, stop refresh')
            self.cancel()

class URControlViewModel:
    def __init__(self):
        self.controller = None
        self.gui = urgui.UIsignal()
        self.ip = '192.168.1.102'
        self.port = 30003
        self.payloadData = ''
        self.is_connected = False
        self.thread_joint = None
        self.thread_tcp = None
        self.event = threading.Event()
        self.lock = threading.Lock()

    def init_connect(self, root_obj):
        self.root_obj = root_obj
        self.swipeViewButton_obj = self.root_obj.findChildren(QObject, 'swipeView')[0]
        # self.init_setting_object()只连接一次，不加括号会一直连接
        self.swipeViewButton_obj.currentIndexChanged.connect(self.init_setting_object())
        self.ipAddress_obj = self.root_obj.findChildren(QObject, 'ipAddress')[0]
        self.ipAddress_obj.editingFinished.connect(
            lambda: self.getIPadress_fromUI(self.ipAddress_obj.property("text")))
        self.connectButton_obj = self.root_obj.findChildren(QObject, 'connectButton')[0]
        self.connectButton_obj.clicked.connect(self.connectUR)
        # self.init_button_object()
        # self.init_setting_object()
    
    def init_setting_object(self):
        # print("chushihua",self.swipeViewButton_obj.property("currentIndex"))
        # if self.swipeViewButton_obj.property("currentIndex") == 1:
        #     return
        # print("chushihua")
        self.init_button_object()
        self.payload_obj = self.root_obj.findChildren(QObject, 'payloadData')[0]
        self.payload_obj.editingFinished.connect(
            lambda: self.getPayloadData_fromUI(self.payload_obj.property("text")))
        # self.setting_obj_dic = dict([
        #     ('ctrlSpeedJ', self.setJSpeed), ('ctrlSpeedTCP', self.setTCPSpeed),
        # ])
        # for (key, value) in self.setting_obj_dic.items():
        #     temp_obj = self.root_obj.findChildren(QObject, key)[0]
        #     temp_obj.clicked.connect(value)
        #     self.setting_obj_dic[key] = temp_obj
        self.speedj_obj = self.root_obj.findChildren(QObject, 'ctrlSpeedJ')[0]
        self.speedTCP_obj = self.root_obj.findChildren(QObject, 'ctrlSpeedTCP')[0]
        # print(self.gui.jointSpeed,self.gui.tcpSpeed)
        self.speedj_obj.valueChanged.connect(self.setJSpeed)
        self.speedTCP_obj.valueChanged.connect(self.setTCPSpeed)
        
    # QML Object can't be in another thread than QMLApplicationEngine
    # Initialize all button and connect function 不能放到线程里面
    def init_button_object(self):
        # self.event.wait()
        self.button_obj_dic = dict([
            ('freedriveButton', self.freedriveMode), ('stopButton', self.stopMotion),
            ('moveTCPButton', self.moveTCP), ('moveJointButton', self.moveJoint),
            ('zeroButton', self.resetRobot), ('rB_poweron', self.send_power_on),
            ('rB_release', self.send_brake_release), ('rB_poweroff', self.send_power_off),
            ('rB_restart_safety', self.send_restart_safety), 
            ('rB_shutdown', self.send_shutdown),
            ('unlockButton', self.send_unlock_protective_stop), 
            # ('emergencyStopButton', self.), #待实现
            ('disconnectButton', self.disconnectRobot),
            ('xaddButton', self.axisX_add), ('xsubButton', self.axisX_sub),
            ('yaddButton', self.axisY_add), ('ysubButton', self.axisY_sub),
            ('zaddButton', self.axisZ_add), ('zsubButton', self.axisZ_sub),
            ('rxaddButton', self.rX_add), ('rxsubButton', self.rX_sub),
            ('ryaddButton', self.rY_add), ('rysubButton', self.rY_sub),
            ('rzaddButton', self.rZ_add), ('rzsubButton', self.rZ_sub),
            ('savePayloadData', self.save_payload),
            ('testbutton', self.moveto_target)
             ])
        # Sequence: pressed, checked changed, (released), clicked
        for (key, value) in self.button_obj_dic.items():
            temp_obj = self.root_obj.findChildren(QObject, key)[0]
            temp_obj.clicked.connect(value)
            self.button_obj_dic[key] = temp_obj
    
    def getIPadress_fromUI(self, ip):
        print("Setting IP address")
        if self.ip != ip:
            self.ip = ip

    def connectUR_task(self):
        # checked False: connect; checked True: Cancelling
        try:
            if self.connectButton_obj.property("checked"):
                self.connectButton_obj.setProperty("enabled", False)
                self.ipAddress_obj.setProperty("enabled", False)
                print("Start to connect, waiting ... ", end=' ')
                time.sleep(0.01)
                self.controller = ur_controller.URController(self.ip)
                time.sleep(0.5)
                if self.getConnectStatus():
#                if True:
                    self.is_connected = True
                    self.swipeViewButton_obj.setProperty("currentIndex", 1)
                    # self.event.set()
                    self.refresh_data_toGui()
                else:
                    print("Connect error: Invalid connection")
                    self.connectButton_obj.setProperty("checked", False)
                self.connectButton_obj.setProperty("enabled", True)
                self.ipAddress_obj.setProperty("enabled", True)
            else:
                print("取消连接")
        except Exception as e:
            logging.error("Error: Timeout and ",e)
            self.disconnectRobot()

    # connectUR thread
    def connectUR(self):
        tCon = threading.Thread(target=lambda: self.connectUR_task())
        tCon.setDaemon(True) #一定要设置为守护线程
        tCon.start()
    
    def getConnectStatus(self):
        return self.controller.connectState

    def send_power_on(self):
        return self.controller.sendCommand("power on")  # Return "Powering on"
    
    def send_brake_release(self):
        self.controller.sendCommand("brake release")  # Return "Brake releasing"
    
    def send_power_off(self):
        return self.controller.sendCommand("power off")  # Return "Powering off"
    
    def send_restart_safety(self):
        return self.controller.sendCommand("restart safety")  # Return Restarting safety
    
    def send_shutdown(self):
        self.controller.sendCommand("shutdown") # Return "Shutting down"
        self.disconnectRobot()
    
    # def send_quit(self):
    #     return self.controller.sendCommand("quit")  # Return "Disconnected"
    
    def send_unlock_protective_stop(self):
        self.controller.sendCommand("close safety popup")
        if self.controller.sendCommand("unlock protective stop") == "Protective stop releasing":
            return True
        return False

    def getPayloadData_fromUI(self, data):
        if self.payloadData != data:
            self.payloadData = data
        print("Setting payloadData", self.payloadData)
    
    def save_payload(self):
        if self.payloadData != self.payload_obj.property("text"):
            self.payloadData = self.payload_obj.property("text")
        self.controller.set_payload(self.payloadData)
        print("Save payloadData", self.payloadData)
    
    # 得到当前的关节参数
    def getJpose_fromGui(self):
        print("从Gui获得当前机器人关节的参数")
        return self.gui.jointPose

    def getTCPpose_fromGui(self):
        print("从Gui获得TCP的位置参数")
        return self.gui.tcpPose

    def getJpose_fromUR(self):
        a_jpose = list(self.controller.get_joint_pose())
        print("从机械臂获得关节参数:",a_jpose)
        return a_jpose  #返回6个关节的数值

    def gettcpfromUR(self):
        tcp_pose = [round(a,4) for a in (self.controller.get_tcp_pose(self.gui.rvRpyIndex).tolist())]
        print("从机械臂获得TCP参数:",tcp_pose)
        return tcp_pose

    def refresh_data_toGui(self, hz=0.5):
        if self.gui.jointSwitch:
            print("Joint state: 刷新",end=', ')
        else:
            print("Joint state: 停止刷新",end=', ')
        if self.gui.tcpSwitch:
            print("TCP state:刷新")
        else:
            print("TCP state: 停止刷新")
        MODE = ['q actual', 'Tool vector actual', 'Robot Mode', 'Joint Modes', 'Safety Mode']
        def setJvalue_toGui_task():
            # self.lock.acquire()
            if self.is_connected:
                temp_dic = self.controller.URSoc.read(MODE)
                if temp_dic == -1:
                    self.disconnectRobot()
                    return 0
                jPose_fromUR, tcpfromUR, robotM, jointM, SafetyM = \
                    temp_dic[MODE[0]], temp_dic[MODE[1]], temp_dic[MODE[2]], temp_dic[MODE[3]], temp_dic[MODE[4]]
                self.gui.set_robot_mode(robotM[0])
                self.gui.set_safe_mode(SafetyM[0])
                if self.gui.jointSwitch:
                    jPose_fromUR = [round((i*180 / np.pi),2) for i in jPose_fromUR]
                    self.gui.jointPose = jPose_fromUR
                if self.gui.tcpSwitch:
                    # tcpfromUR = list(tcpfromUR)  # 元组转换为列表
                    tcpfromUR[0:3] = [round(1000*i,2) for i in tcpfromUR[0:3]]
                    if self.gui.rvRpyIndex == 0:
                        tcpfromUR[3:6] = [round(i, 4) for i in tcpfromUR[3:6]]
                    if self.gui.rvRpyIndex == 1:
                        tcpfromUR[3:6] = [round(i* 180 / np.pi, 2) for i in tcpfromUR[3:6]]
                    # np.float(i):  numpy.float64 trans to python.float, so that the data can transfer to qml
                    if self.gui.rvRpyIndex == 2:
                        rpy_rad2 = self.controller.transMatrix.rv2rpy(tcpfromUR[3], tcpfromUR[4], tcpfromUR[5])
                        tcpfromUR[3:6] = [round(np.float(i), 4) for i in rpy_rad2]
                    if self.gui.rvRpyIndex == 3:
                        rpy_rad3 = self.controller.transMatrix.rv2rpy(tcpfromUR[3], tcpfromUR[4], tcpfromUR[5])
                        tcpfromUR[3:6] = [round(np.float(i* 180 / np.pi), 2) for i in rpy_rad3]
                    self.gui.tcpPose = tcpfromUR
                    # print(self.gui.tcpPose)
            # self.lock.release()
            return self.is_connected  # and (self.gui.jointSwitch or self.gui.tcpSwitch)
        tjoint = RepeatingTimer(hz, setJvalue_toGui_task)
        tjoint.setDaemon(True)
        tjoint.start()


    def setspeed_toGui(self):
        #  90 percent
        self.gui.jointSpeed, self.gui.tcpSpeed = 90, 90

    # 设置机器人运动速度
    def setTCPSpeed(self): # tag = 'speedJ'
        self.controller.set_tcp_speed(self.gui.tcpSpeed/100)
        print("设置机器人的TCP速度", self.controller.tcp_vel)
        
    def setJSpeed(self): # tag = 'speedJ'
        # print("设置机器人的关节速度", self.gui.jointSpeed,self.gui.jointSpeed/100)
        self.controller.set_joint_speed(self.gui.jointSpeed/100)
        print("设置机器人的关节速度", self.controller.joint_vel)

    # 开始执行关节的调节设置
    def moveJoint(self):
        print("Move joint")
        if self.gui.jointSwitch:
            logging.warning('Should stop refresh joint')
            self.gui.jointSwitch = False
        if self.thread_tcp:
            if self.thread_tcp.isAlive():
                logging.warning('Please wait until moveTCP task is done, then try again')
                return
        # in degree or radian
        self.thread_joint = threading.Thread(target=lambda: self.controller.move_by_joint(
            self.gui.jointPose, is_degree=True))
        self.thread_joint.setDaemon(True)
        self.thread_joint.start()


    def moveTCP(self):
        print("Move TCP")
        if self.gui.tcpSwitch:
            logging.warning('Should stop refresh TCP')
            self.gui.tcpSwitch = False
        if self.thread_joint:
            if self.thread_joint.isAlive():
                logging.warning('Please wait until moveJoint task is done, then try again')
                return
        self.gui.rvRpyIndex = 0
        temp_pose = [i/1000 for i in self.gui.tcpPose[0:3]]
        temp_pose.extend(self.gui.tcpPose[3:6])
        self.thread_tcp = threading.Thread(target=lambda: self.controller.move_to_tcp(temp_pose))
        self.thread_tcp.setDaemon(True)
        self.thread_tcp.start()

    #机器人零点位置
    def resetRobot(self):
        if self.thread_joint:
            if self.thread_joint.isAlive():
                logging.warning('Please wait until moveJoint task is done, then try again')
                return
        if self.thread_tcp:
            if self.thread_tcp.isAlive():
                logging.warning('Please wait until moveTCP task is done, then try again')
                return
        self.controller.moveto_zero_pose()
        print("机器人位置归0")

    def moveto_target(self):
        self.controller.moveto_target_pose()

    # 手动控制机器人
    def freedriveMode(self):
        if self.button_obj_dic["freedriveButton"].property("checked"):
            print("Set robot in freedrive mode.")
            self.controller.set_freedrive(True)
        else:
            print("Set robot in normal mode.")
            self.controller.set_freedrive(False)

    #停止机器人运动
    def stopMotion(self):
        print("停止机器人运动")
        self.controller.stop()

    def disconnectRobot(self):
        if self.is_connected:
            print("Stop connection, waiting ... ")
            self.is_connected = False
            self.controller.close()
            self.swipeViewButton_obj.setProperty("currentIndex", 0)
            self.connectButton_obj.setProperty("checked", False)

    # 对末端执行器进行微调
    def axisX_add(self):
        print("末端执行器位置x+ 5mm")
        self.controller.increase_move_TCP(0)
    def axisY_add(self):
        print("末端执行器位置Y+ 5mm")
        self.controller.increase_move_TCP(1)
    def axisZ_add(self):
        print("末端执行器位置Z+ 5mm")
        self.controller.increase_move_TCP(2)
    def axisX_sub(self):
        print("末端执行器位置x- 5mm")
        self.controller.increase_move_TCP(0, "-")
    def axisY_sub(self):
        print("末端执行器位置Y- 5mm")
        self.controller.increase_move_TCP(1, "-")
    def axisZ_sub(self):
        print("末端执行器位置Z- 5mm")
        self.controller.increase_move_TCP(2, "-")
    def rX_add(self):
        print("末端执行器Roll+ 0.005rad")
        self.controller.increase_move_TCP(3)
    def rY_add(self):
        print("末端执行器Pitch+ 0.005rad")
        self.controller.increase_move_TCP(4)
    def rZ_add(self):
        print("末端执行器Yaw+ 0.005rad")
        self.controller.increase_move_TCP(5)
    def rX_sub(self):
        print("末端执行器Roll-  0.005rad")
        self.controller.increase_move_TCP(3, "-")
    def rY_sub(self):
        print("末端执行器Pitch- 0.005rad")
        self.controller.increase_move_TCP(4, "-")
    def rZ_sub(self):
        print("末端执行器Yaw- 0.005rad")
        self.controller.increase_move_TCP(5, "-")

def abs_path(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

def viewload():
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view_model = URControlViewModel()
    ur_singal = view_model.gui
    view.rootContext().setContextProperty("urSingal", ur_singal)
    # qmlRegisterType(UIsignal, 'PySignal', 1, 0, 'PySignal') # implicit error when using slot and singal
    qmlRegisterType(ur_visual.FboItem, "QmlVTK", 1, 0, "VtkFboItem")

    view.setSource(QUrl.fromLocalFile(abs_path("qmlRobotGui\main.qml")))
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setTitle ("UR Controller")
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    root_obj = view.rootObject()
    view_model.init_connect(root_obj)
    root_obj.destroyed.connect(view_model.disconnectRobot)

    app.exec_()
    # Deleting the view before it goes out of scope is required to make
    # sure all child QML instances are destroyed in the correct order.
    del view

def appload():
    '''
    When using QmlApplicationEngine() to load qml-vtk window, in the unlikely event,
    you will encounter the following problems: the QML window is stuck.

    Please check if you: import pyside2, and use QmlApplicationEngine().load to load only one qml-vtk window
    (such as main.qml in here containing custom qmlRegisterType 【import QmlVTK 1.0】) .
    If you have to do this, plus self.createRenderer () to __ init__ function, fboitem class.
    Then it works but an error window, vtkoutputwindow, will be displayed.
    Then try to close the vtkoutputwindow (maybe call the Win32 API findwindow?)

    Recommended solution: import PyQt5 instead of pyside2;
    Or using QQuickView().setSource to load qml window;
    Or load another independent general qml window before load the qml-vtk window.
    '''
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    view_model = URControlViewModel()
    ur_singal = view_model.gui  # 这样在urgui里面定义的变量可以用self，否则只能定义全局变量
    engine.rootContext().setContextProperty("urSingal", ur_singal)
    qmlRegisterType(ur_visual.FboItem, "QmlVTK", 1, 0, "VtkFboItem")
    # qmlRegisterType(UIsignal, 'PySignal', 1, 0, 'PySignal') # implicit error when using slot and singal
    engine.load(os.path.join(os.path.dirname(__file__), "qmlRobotGui\main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    root_obj = engine.rootObjects()[0]
    view_model.init_connect(root_obj)
#    print(type(root_obj))
    root_obj.destroyed.connect(view_model.disconnectRobot)
    sys.exit(app.exec_())

if __name__ == "__main__":
    viewload()
