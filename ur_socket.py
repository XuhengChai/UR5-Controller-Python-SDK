import socket
import struct
import time
import logging
import threading
import queue
import numpy as np
import os
import re
# import cv2

class URSocketSimple():
    is_connect = False
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        try:
            # Ipv4 SOCK_STREAM: 面向连接的流套接字，默认值，tcp协议  SOCK_DGRAM
            self.dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dashboard_socket.settimeout(3)
            self.dashboard_socket.connect((self.host, self.port))
            print(self.dashboard_socket.recv(1024).decode(),end='')
            URSocketSimple.is_connect = True
        except socket.timeout:
            logging.error("except: socket timed out error, can not connect_robot within 3 seconds")
            self.dashboard_socket.close()
            URSocketSimple.is_connect = False
        except Exception as e:
            logging.error("except: " + format(str(e)) + " in connecting %s : %s" % (self.host, self.port))
            self.dashboard_socket.close()
            URSocketSimple.is_connect = False
        finally:
            return URSocketSimple.is_connect

    def send(self, command):
        '''
        :param command: str, include \n!!!
        :return: str
        '''
        try:
            if URSocketSimple.is_connect:
                self.dashboard_socket.send(str.encode(command))
                msg = self.dashboard_socket.recv(1024).decode()
                # print(msg, type(msg))
                return msg
        except Exception as e:
            print(e)
            self.close()
            return

    def close(self):
        self.dashboard_socket.close()
        URSocketSimple.is_connect = False# 关闭连接
        print("Disconnected: Universal Robots Dashboard Server")

class URSocket(threading.Thread):

    def __init__(self,host,port):
        super().__init__()
        # threading.Thread.__init__(self)
        # self.HOST = "192.168.1.102"    # The remote host
        # self.PORT = 30003        # The same port as used by the server
        self.robot_socket = None
        self.write_lock = threading.Lock()
        self.priority_queue = queue.Queue(10)
        self.priority_queue_dict = {}
        self._is_connection = False
        self.connect_robot(host,port)
        self.recv_dic = {'MessageSize': 'i', 'Time': 'd', 'q target': '6d', 'qd target': '6d', 'qdd target': '6d',
                         'I target': '6d', 'M target': '6d', 'q actual': '6d', 'qd actual': '6d', 'I actual': '6d',
                         'I control': '6d', 'Tool vector actual': '6d', 'TCP speed actual': '6d', 'TCP force': '6d',
                         'Tool vector target': '6d', 'TCP speed target': '6d', 'Digital input bits': 'd',
                         'Motor temperatures': '6d', 'Controller Timer': 'd', 'Test value': 'd', 'Robot Mode': 'd',
                         'Joint Modes': '6d', 'Safety Mode': 'd', 'empty1': '6d',
                         'Tool Accelerometer values': '3d', 'empty2': '6d', 'Speed scaling': 'd',
                         'Linear momentum norm': 'd', 'SoftwareOnly': 'd', 'softwareOnly2': 'd', 'V main': 'd',
                         'V robot': 'd', 'I robot': 'd', 'V actual': '6d', 'Digital outputs': 'd', 'Program state': 'd',
                         'Elbow position': '3d', 'Elbow velocity': '3d'}

    def get_connected_state(self):
        return self._is_connection

    def set_is_connection(self,flag):
        self._is_connection = flag

    def send(self, data):
        if not self._is_connection:
            return -1
        try:
            with self.write_lock:
                self.robot_socket.send(str.encode(data))
        except Exception as e:
            self.set_is_connection(False)
            return -1

    def read(self, name:list, if_print=False):
        '''
        :param name: unpack data name; example: ['q target','q actual','Tool vector actual','Tool vector target']
        :param if_print: print the unpack data or not
        :return:
        '''
        if not self._is_connection:
            return -1
        if not isinstance(name, list):
            logging.error('type error, the input arg must be a list!')
            return -1
        if self.priority_queue.empty():
            logging.warning('The buffer is empty once! ignore...')
            time.sleep(1)
            if self.priority_queue.empty():
                logging.error('The buffer is empty twice, closing the connection!')
                return -1
        buffer = self.priority_queue.get()
        # buffer = self.robot_socket.recv(1108)
        buffer_dict = {}
        ans_dic = {}
        ii = range(len(self.recv_dic))
        # zip 会取字典的第一个元素key和ii构成一个元组
        for key, i in zip(self.recv_dic, ii):
            fmtsize = struct.calcsize(self.recv_dic[key])  # 返回字节大小
            data_extracted, buffer = buffer[0:fmtsize], buffer[fmtsize:]
            fmt = "!" + self.recv_dic[key]
            buffer_dict[key] = struct.unpack(fmt, data_extracted) #返回一个tuple
        for i in range(len(name)):
            if not isinstance(name[i], str):
                logging.warning("type error, {} is not str, please check the input!".format(name[i]))
                break
            if name[i] not in self.recv_dic.keys():
                logging.warning("name error, please check name '{}' is correct or not!".format(name[i]))
                break
            # if 'q' in name[i]:  # for joint angles in radian
            #     ans_dic[name[i]] = np.array(buffer_dict[name[i]]) * 180 / np.pi
            # else:
            #     ans_dic[name[i]] = np.array(buffer_dict[name[i]])
            ans_dic[name[i]] = list(buffer_dict[name[i]])
            if if_print:
                print(name[i], end=':')
                self.print_array(ans_dic[name[i]])
        return ans_dic

    def print_array(self, data):
        for i in range(len(data)-1):
            print(round(data[i],3),end=',')
        print(round(data[-1],3))

    def flush(self):
        if not self._is_connection:
            return -1
        while not (self.priority_queue.empty()):
            self.priority_queue.queue.clear()
        return 0
    def connect_robot(self,host, port):
        """
        :param host: The remote host
        :param port: The same port as used by the server
        :return:
        """
        try:
            # -w 超时时间，这里应该是1s -n 发送 count 指定的 ECHO 数据包数
            # print("before ping", end=',')
            # with os.popen('ping -w 1 %s -n 1'% host) as popen:
            #     print("ping sucess!" if re.search("TTL",popen.read()) else 'ping falied',end='')
            # print("After ping      ", end=',')
            self.robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.robot_socket.settimeout(3)
            self.robot_socket.connect((host, port))
            print('Connected {}:{} success'.format(host, port))
            self.set_is_connection(True)
        except socket.timeout:
            logging.error("except: socket timed out error, can not connect_robot within 3 seconds")
            self.robot_socket.close()
            self.set_is_connection(False)

        except Exception as e:
            logging.error("except: " + format(str(e)) + " in connecting robot" )
            self.robot_socket.close()
            self.set_is_connection(False)
        finally:
            return self._is_connection
    def run(self):
        """
        A threading to receive data from socket
        """
        try:
            self.recv_all_buffer()
            # t_recv = threading.Thread(target=self.recv_all_buffer, args=(True,))
            # t_recv.start()
            # t_recv.join()
        finally:
            self.robot_socket.close()  # success: return 0，error: return -1，error code: errno
            print("Disconnected: Universal Robots!")

    def close(self):
        self.set_is_connection(False)
        time.sleep(0.3)
        # SHUT_RD 关闭接收消息通道，SHUT_WR 关闭发送消息通道，SHUT_RDWR 两个通道都关闭
        # 一般来讲run函数里面已经close了，此处检查一遍确定close
        try:
            if self.robot_socket.recv(1108):
                self.robot_socket.shutdown(2)
                self.robot_socket.close()
                logging.warning("Reclosed robot")
        except Exception as e:
            logging.info("Successfully closed!")

        # self.join()

    def recv_all_buffer(self):
        """
        parse a packet from the UR socket and return a dictionary with the data
        """
        timeout_count = 0
        failed_read_count = 0
        while self._is_connection:
            try:
                recv_data = self.robot_socket.recv(1108)
            except socket.timeout:
                timeout_count +=1
                if timeout_count > 3:
                    logging.error('except: socket timeout error!')
                    self.close()
                    break
                continue
            if len(recv_data) == 0:
                failed_read_count += 1
                if failed_read_count > 5:
                    logging.error('except: Received data with empty length !')
                    self.close()
                    break
                time.sleep(0.1)
                continue
            else:
                timeout_count = 0
                failed_read_count = 0
                if len(recv_data) == 1108:
                    if self.priority_queue.full():
                        self.priority_queue.get()
                    self.priority_queue.put(recv_data)

    # unit: m and radian
    def get_current_data(self, TCP=False, VTCP=False, Joint=False, Vjoint=False):
        buffer = self.priority_queue.get()
        ans_list = []
        if TCP:
            position_tcp = list(struct.unpack('!6d', buffer[444:492]))  # unit: [m,m,m,旋转矢量rad,rad,rad]
            ans_list.append(position_tcp)
        if VTCP:
            velocity_tcp = list(struct.unpack('!6d', buffer[492:540]))
            ans_list.append(velocity_tcp)
        if Joint:
            position_joint = list(struct.unpack('!6d', buffer[252:300]))  # unit:[rad]*6
            ans_list.append(position_joint)
        if Vjoint:
            velocity_joint = list(struct.unpack('!6d', buffer[300:348]))
            ans_list.append(velocity_joint)
        return ans_list

