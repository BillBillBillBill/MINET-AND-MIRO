#!/usr/bin/env python
#coding:utf-8

import socket
import json
import time
from threading import Thread


class TcpClient:
    HOST = "localhost"
    PORT = 12345
    BUFSIZ = 1024
    ADDR = (HOST, PORT)


    def __init__(self, UI=None, is_recv_boardcast=False):
        self.isMIRO = False
        self.isLogin = False
        self.UI = UI
        self.is_recv_boardcast = is_recv_boardcast
        self.jdata = {}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        print self.client.getpeername()
        print self.client.getsockname()
        self.handshake()
        self.allow_action = ["handshake", "register", "login", "logout", "broadcast", "get_online_user"]


    def handshake(self):
        if self.is_recv_boardcast:
            ack_msg = '{"action": "handshake", "agent": "MINET", "is_recv_boardcast": "yes"}'
        else:
            ack_msg = '{"action": "handshake", "agent": "MINET"}'
        self.send_json_and_recv(ack_msg)
        if self.jdata.get("server") != "MIRO":
            print "Server is not MIRO"
            self.client.close()
        else:
            self.isMIRO = True
            print "Connect to MIRO"


    def register(self, username, password, nickname):
        register_msg = '{"action": "register", "username": "%s", "password": "%s", "nickname": "%s"}'\
                       % (username, password, nickname)
        self.send_json_and_recv(register_msg)
        if self.jdata.get("code") == "REGISTER_SUCCESS":
            print "Register success"
            return True
        else:
            print "Register fail, reason:", self.jdata.get("message")
            return False


    def login(self, username, password):
        register_msg = '{"action": "login", "username": "%s", "password": "%s"}' % (username, password)
        self.send_json_and_recv(register_msg)
        if self.jdata.get("code") == "LOGIN_SUCCESS":
            self.isLogin = True
            print "Login success"
            return True
        else:
            print "Login fail, reason:", self.jdata.get("message")
            return False


    def logout(self):
        logout_msg = '{"action": "logout"}'
        self.send_json_and_recv(logout_msg)
        self.isLogin = False
        if self.jdata.get("code") == "LOGOUT_SUCCESS":
            print "Logout success"
        else:
            print "Logout fail:", self.jdata.get("message")


    def broadcast(self, content=""):
        broadcast_msg = '{"action": "broadcast", "content": "%s"}' % content
        try:
            self.send_json(broadcast_msg)
            print "Broadcast success"
            return True
        except Exception, e:
            print e
            print "Broadcast fail, reason:", self.jdata.get("message")
            return False


    def get_online_user(self):
        get_msg = '{"action": "get_online_user"}'
        self.send_json_and_recv(get_msg)
        if self.jdata.get("user"):
            print self.jdata.get("user")


    def start_query(self):

        while True:
            action = raw_input("action:")

            if not action:
                break

            if action not in self.allow_action:
                print "action not allowed"
                continue

            if action == "broadcast":
                content = raw_input("content:")
                self.broadcast(content)

            if action == "handshake":
                self.handshake()

            if action == "register":
                username = raw_input("username:")
                password = raw_input("password:")
                nickname = raw_input("nickname:")
                self.register(username, password, nickname)

            if action == "login":
                username = raw_input("username:")
                password = raw_input("password:")
                self.login(username, password)

            if action == "logout":
                self.logout()

            if action == "get_online_user":
                self.get_online_user()
            # self.client.send(data.encode('utf8'))
            # data = self.client.recv(self.BUFSIZ)
            # if not data:
            #     break
            # print data.decode('utf8')

    def receive_one_msg(self):
        """
        接收一条信息 并返回
        """
        data = self.client.recv(self.BUFSIZ)
        print "收到信息：", data
        jdata = json.loads(data)
        return jdata


    def send_json(self, message):
        """
        发送信息
        """
        try:
            print u"Send: {}".format(message)
            self.client.sendall(message.encode("utf-8"))
        except Exception as e:
            print "send_json:", e


    def send_json_and_recv(self, message):
        try:
            #  print "Send: {}".format(message)
            self.client.sendall(message.encode("utf-8"))
            response = self.client.recv(self.BUFSIZ)
            self.jdata = json.loads(response)
            print "Recv: ", self.jdata
        except Exception as e:
            print "send_json_and_recv:", e


    def finish(self):
        if self.isLogin and not self.is_recv_boardcast:
            self.logout()
        self.client.close()

if __name__ == "__main__":
    # msg1 = {'src':'hello', 'dst':"bar"}
    # jmsg1 = json.dumps(msg1)
    client = TcpClient()
    #client.start_query()

    # client.register('user111111','user111111','user111111')
    client.login('1','1')
    #
    # # 测试发送广播
    client.broadcast("")
    client.broadcast("hehe")
    client.broadcast("hehehhhhh")
    #
    # # 测试接收信息
    # client.start_receive_msg()

    #
    # while 1:
    #     client.send_json('{"action": "show_info"}')
    #     time.sleep(1)

    # client.send_json(jmsg1)
    # client.start_query()
