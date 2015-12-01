#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import json
import time

class TcpClient:
    HOST = "localhost"
    PORT = 12345
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    def __init__(self):
        self.isMIRO = False
        self.isLogin = False
        self.jdata = {}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        print self.client.getpeername()
        print self.client.getsockname()
        self.handshake()
        self.allow_action = ["handshake", "register", "login", "broadcast"]


    def handshake(self):
        ack_msg ='{"action": "handshake", "agent": "MINET"}'
        self.send_json(ack_msg)
        if self.jdata.get("server") != "MIRO":
            print "Server is not MIRO"
            self.client.close()
        else:
            self.isMIRO = True
            print "Connect to MIRO"

    def register(self, username, password, nickname):
        register_msg = '{"action": "register", "username": "%s", "password": "%s", "nickname": "%s"}' % (username, password, nickname)
        self.send_json(register_msg)
        if self.jdata.get("code") == "REGISTER_SUCCESS":
            print "Register success"
        else:
            print "Register fail, reason:", self.jdata.get("message")


    def login(self, username, password):
        register_msg = '{"action": "login", "username": "%s", "password": "%s"}' % (username, password)
        self.send_json(register_msg)
        if self.jdata.get("code") == "LOGIN_SUCCESS":
            self.isLogin = True
            print "Login success"
        else:
            print "Login fail, reason:", self.jdata.get("message")

    def broadcast(self, content=""):
        broadcast_msg = '{"action": "broadcast", "content": "%s"}' % content
        self.send_json(broadcast_msg)
        if self.jdata.get("code") == "BROADCAST_SUCCESS":
            print "Broadcast success"
        else:
            print "Broadcast fail, reason:", self.jdata.get("message")

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

            # self.client.send(data.encode('utf8'))
            # data = self.client.recv(self.BUFSIZ)
            # if not data:
            #     break
            # print data.decode('utf8')


    def start_receive_msg(self):
        """
        仅用于测试
        """
        while True:
            data = self.client.recv(self.BUFSIZ)
            print "收到信息：", data
            time.sleep(0.5)


    def send_json(self, message):
        try:
            print "Send: {}".format(message)
            self.client.sendall(message)
            response = self.client.recv(self.BUFSIZ)
            self.jdata = json.loads(response)
            print "Recv: ", self.jdata
        except Exception as e:
            print e


    def finish(self):
        self.client.send("EXIT")
        self.client.close()

if __name__ == "__main__":
    # msg1 = {'src':'hello', 'dst':"bar"}
    # jmsg1 = json.dumps(msg1)
    client = TcpClient()
    client.start_query()

    # client.register('user111111','user111111','user111111')
    # client.login('user111111','user111111')
    #
    # # 测试发送广播
    # client.broadcast("")
    # client.broadcast("hehe")
    #
    # # 测试接收信息
    # client.start_receive_msg()

    #
    # while 1:
    #     client.send_json('{"action": "show_info"}')
    #     time.sleep(1)

    # client.send_json(jmsg1)
    # client.start_query()
