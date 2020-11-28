import numpy as np
# from ur_control import ur_trans_matrix, ur_socket
import ur_trans_matrix
import ur_socket
import time
import logging
import threading
import re


# control API
class URController:
    TCP_A = 'Tool vector actual'
    JOINT_A = 'q actual'
    MODE = ['Robot Mode', 'Joint Modes', 'Safety Mode']
    TCP_X, TCP_Y, TCP_Z, TCP_Roll, TCP_Pitch, TCP_Yaw = 0, 1, 2, 3, 4, 5
    Joint1, Joint2, Joint3, Joint4, Joint5, Joint6 = 0, 1, 2, 3, 4, 5

    def __init__(self, host):
        self.URSocSimple = ur_socket.URSocketSimple(host, 29999)
        self.URSoc = ur_socket.URSocket(host, 30003)
        self.connectState =self.URSoc.get_connected_state()
        if self.connectState:
            # print("开始线程")
            self.URSoc.start()
            # self.URSocket.daemon = True #是否设置为守护线程，主线程结束会kill此线程。不设置
            # self.URSocket.join() #是否设置阻塞主线程。不设置
        self.transMatrix = ur_trans_matrix.Util()
        self.tcp_vel = 0.05  # m/s
        self.tcp_acc = 0.05  # m/s
        # self.joint_vel = 25 * np.pi / 180  # Safe: 0.2rad/s
        # self.joint_acc = 50 * np.pi / 180
        self.joint_vel = 0.45
        self.joint_acc = 0.9
        self.is_stop = False

    # \n is necessary!!!!!
    def sendCommand(self, command):
        return self.URSocSimple.send(command+"\n")

    def get_TCPJoint_data(self, TCP=False, VTCP=False, Joint=False, Vjoint=False):
        return self.URSoc.get_current_data(TCP, VTCP, Joint, Vjoint)

    # ["R vector/rad", "R vector/degree", "RPY/rad", "RPY/degree"] rxRpyIndex = 0,1,2,3
    def get_tcp_pose(self, rvRpyIndex=0):
        tcp = self.URSoc.get_current_data(TCP=True)[0]  #返回的是rv，旋转矢量 transto_rpy=False
        if rvRpyIndex == 1:
            tcp[3:6] = [i* 180 / np.pi for i in tcp[3:6]]
        if rvRpyIndex == 2:
            tcp[3:6] = self.transMatrix.rv2rpy(tcp[3], tcp[4], tcp[5])
        if rvRpyIndex == 3:
            rpy_rad = self.transMatrix.rv2rpy(tcp[3], tcp[4], tcp[5])
            tcp[3:6] = [i* 180 / np.pi for i in rpy_rad]
        return tcp

    def get_tcp_speed(self):
        return self.URSoc.get_current_data(VTCP=True)[0]

    def get_joint_pose(self, transto_degree=False):
        data = self.URSoc.get_current_data(Joint=True)[0]
        if transto_degree:
            data = [(i*180 / np.pi) for i in data]
        return data

    def get_joint_speed(self, transto_degree=False):
        data = self.URSoc.get_current_data(Vjoint=True)[0]
        if transto_degree:
            data = [(i*180 / np.pi) for i in data]
        return data

    def set_tcp_speed(self, factor):
        self.tcp_vel = 0.05 * factor
        self.tcp_acc = 0.05 * factor

    def set_joint_speed(self, factor):
        self.joint_vel = 0.45 * factor
        self.joint_acc = 0.9 * factor

    def set_payload(self, text):
        it = re.sub(r'[^0-9.]', " ", text)
        it = it.split()
        it = list(map(float, it))
        '''
        m: mass in kilograms
        cog: Center of Gravity, a vector [CoGx, CoGy, CoGz] (in meters)
        '''
        msg = "set_payload(%f, [%f,%f,%f])\n" % (it[0], it[1],it[2], it[3])
        self.URSoc.send(msg)
        

    def add_line_to_program(self, program, new_line):
        return "{}\n\t{}".format(program, new_line)

    def move_to_tcp(self, target_tcp: list):
        '''
        Move to position (linear in tool-space)
        :param target_tcp: a 6 dimension vector list, unit: [m, rad]
        :return:
        '''
        # tool_acc = 0.05  # Safe: 0.5 #m^2/s
        if self.is_stop:
            self.is_stop = False
        tool_time = 0
        tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
        command_check_tcp = "if is_within_safety_limits(p[%f,%f,%f,%f,%f,%f]):" % (
            target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4], target_tcp[5])
        command_tcp = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
            target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4], target_tcp[5],
            self.tcp_acc, self.tcp_vel)
        msg = self.add_line_to_program(command_check_tcp,command_tcp)
        self.URSoc.send(msg)
        # 确保已达到目标点，就可以紧接着发送下一条指令
        actual_pos = self.get_tcp_pose()
        target_rpy = self.transMatrix.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
        rpy = self.transMatrix.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
                   and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j + 3] for j in range(3)]))\
                and not self.is_stop:
            actual_pos = self.get_tcp_pose()
            rpy = self.transMatrix.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
            time.sleep(0.1)
        # logging.info('Arrive target position successfully')

    def move_by_joint(self, target_joint,is_degree=False):
        '''
        Move to position (linear in joint-space)
        :param target_joint: [0,1.57,-1.57,3.14,-1.57,1.57] in radian
        :param is_degree: is in degree or not
        :return:
        '''
        if self.is_stop:
            self.is_stop = False
        tool_time = 0
        joint_pos_tolerance = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
        if is_degree:
            target_joint = np.asarray(target_joint) * np.pi / 180
        for i in range(len(target_joint)):
            if abs(target_joint[i]) > np.pi:
                logging.error("except: input target joint error")
                return
        joint_command = "movej([%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=%f,r=0)\n" % (
            target_joint[0], target_joint[1], target_joint[2], target_joint[3], target_joint[4], target_joint[5],
            self.joint_acc, self.joint_vel, tool_time)
        self.URSoc.send(joint_command)
        # time.sleep(2)
        # self.URSoc.send("stopj(1)\n")
        # 确保已达到目标点，就可以紧接着发送下一条指令
        actual_pos = self.get_joint_pose()
        while not (all([(np.abs(actual_pos[j] - target_joint[j])*180 / np.pi) < joint_pos_tolerance[j] for j in range(6)]))\
                and not self.is_stop:
            actual_pos = self.get_joint_pose()
            time.sleep(0.1)
        logging.info('Arrive target joint angle successfully')

    def move_servoj(self, target_joint, is_tcp=False, is_degree = False):
        '''
        :param target_joint: [0,1.57,-1.57,3.14,-1.57,1.57] in radian
        :param is_degree: is in degree or not
        :return:
        '''
        joint_acc = 0  # not used in current version
        joint_vel = 0  # not used in current version
        '''
        – t = 0.002 !           time where the command is controlling the robot. The function is blocking for time t [S].
        – lookahead time = .1 ! time [S], range [0.03,0.2] smoothens the trajectory with this lookahead time
        – gain = 300 !          proportional gain for following target position, range [100,2000]
        '''
        defult_t, lookahead_t, gain =  0.002, 0.1, 300
        if is_tcp:
            joint_command = "q = get_inverse_kin((p[%f,%f,%f,%f,%f,%f])\nservoj(q,%f,%f,%f,%f,%f)\n" % (
            target_joint[0], target_joint[1], target_joint[2], target_joint[3], target_joint[4], target_joint[5],
            joint_acc, joint_vel,defult_t, lookahead_t, gain)
        else:
            if is_degree:
                target_joint = np.asarray(target_joint) * np.pi / 180
            joint_command = "servoj([%f,%f,%f,%f,%f,%f],%f,%f,%f,%f,%f)\n" % (
            target_joint[0], target_joint[1], target_joint[2], target_joint[3], target_joint[4], target_joint[5],
            joint_acc, joint_vel,defult_t, lookahead_t, gain)
        self.URSoc.send(joint_command)
        logging.info('Arrive target servo angle successfully')

    def increase_move_TCP(self, key, direction="+", delta=0.005):
        self.dic_add_sub = {"+": 1, "-": -1}
        tcp_pos = self.get_tcp_pose()
        tcp_pos[key] += self.dic_add_sub[direction]*delta
        print(list(round(i,3) for i in tcp_pos))
        command_check_tcp = "if is_within_safety_limits(p[%f,%f,%f,%f,%f,%f]):" % (
            tcp_pos[0], tcp_pos[1], tcp_pos[2], tcp_pos[3], tcp_pos[4], tcp_pos[5])
        command_tcp = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=%f,r=0)\n" % (
            tcp_pos[0], tcp_pos[1], tcp_pos[2], tcp_pos[3], tcp_pos[4], tcp_pos[5],
            self.tcp_acc, self.tcp_vel,0.5)
        msg = self.add_line_to_program(command_check_tcp, command_tcp)
        self.URSoc.send(msg)
        time.sleep(0.5)

    def increase_move_joint(self, key, direction="+", delta = 2):
        joint_pos = self.get_joint_pose(transto_degree=True)
        joint_pos[key] += self.dic_add_sub[direction]*delta
        if joint_pos[key] > 180:
            logging.error('Joint %i angle exceed 180' % (key+1))
            return
        self.move_by_joint(joint_pos, is_degree=True)

    def moveto_target_pose(self):
        target_pose = [0.491, -0.073, 0.456, 0.071, -3.065, -0.177]
        target_joint = [3.091, -90.798, -84.936, -98.164, 97.092, 90.214]
        # self.move_to_tcp(target_pose)
        thread_target = threading.Thread(target=lambda: self.move_to_tcp(target_pose))
        thread_target.setDaemon(True)
        thread_target.start()

    def moveto_zero_pose(self):
        box_pose = [0.04265, -0.0268, 0.21068, 0.0004, 2.2310, 2.2113]
        box_joint = [0.00, 0.00, -162.00, -108.00, 180.00, 90.00]
        # self.move_by_joint(box_joint, is_degree=True)
        thread_zero = threading.Thread(target=lambda: self.move_by_joint(box_joint, is_degree=True))
        thread_zero.setDaemon(True)
        thread_zero.start()

    def set_freedrive(self, val, timeout=60):
        """
        set robot in freedrive/backdrive mode where an operator can jog
        the robot to wished pose.
        Freedrive will timeout at 60 seconds.
        """
        if val:
            self.URSoc.send("def myProg():\n\tfreedrive_mode()\n\tsleep({})\nend".format(timeout))
        else:
            # This is a non-existant program, but running it will stop freedrive
            self.URSoc.send("def myProg():\n\tend_freedrive_mode()\nend")
        # if val:
        #     self.URSoc.send("teach_mode()\n")
        # else:
        #     # This is a non-existant program, but running it will stop freedrive
        #     self.URSoc.send("end_teach_mode()\n")
    
    def stop(self, acc=1):
        self.is_stop = True
        self.URSoc.send("stopj(%s)\n" % acc)
    def close(self):
        self.URSocSimple.close()
        self.URSoc.close()
        self.sendCommand("quit")
    
