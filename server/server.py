#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import threading
import SocketServer
import json, types,string
import os, datetime
from conn import r

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            while 1:
                data = self.request.recv(1024)
                try:
                    self.jdata = json.loads(data)
                    action_type = self.jdata.get("action")
                    # 根据请求由不同handler处理
                    response = self.handle_action(action_type)
                    response = json.dumps(response)
                    # cur_thread = threading.current_thread()
                    # self.jdata.update({'thread':cur_thread.name})
                    print "Receive json :%r"% (response)
                except Exception as e:
                    print "Error:",e.message
                    print "Receive data:%r"% (data)
                    response = '{"code":"JSON_REQUIRE","message":"Please send json format"}'
                self.request.sendall(response)
        except Exception as e:
            print e


    def handle_action(self, action_type):
        print "Receive action:", action_type
        allow_action = {
            "handshake": self.handshake_handler,
            "register": self.register_handler,
            "login": self.login_handler,
        }
        if action_type not in allow_action.keys():
            return {"code": "UNKNOWN METHOD", "message": "The action is unknown"}
        else:
            return allow_action[action_type]()

    def handshake_handler(self):
        if self.jdata.get("agent") == "MINET":
            return {"server": "MIRO"}
        else:
            return {"code": "UNKNOWN_AGENT", "message": "Your agent is rejected."}


    def register_handler(self):
        username = self.jdata.get("username")
        password = self.jdata.get("password")
        nickname = self.jdata.get("nickname")
        if not all([username, password, nickname]):
            return {"code":"REGISTER_FAIL","message":"You need send username, password and nickname"}
        else:
            try:
                if r.exists("user:" + username +":password"):
                    return {"code":"REGISTER_FAIL","message":"Username is registered"}
                r.set("user:" + username +":password", password)
                r.set("user:" + username +":nickname", nickname)
                return {"code":"REGISTER_SUCCESS","message":"success"}
            except Exception, e:
                print "Error:",e.message
                return {"code":"SERVER_ERROR","message":"Server Error"}

    def login_handler(self):
        username = self.jdata.get("username")
        password = self.jdata.get("password")
        if not all([username, password]):
            return {"code":"LOGIN_FAIL","message":"You need send username and password"}
        else:
            try:
                if not r.exists("user:" + username +":password"):
                    return {"code":"LOGIN_FAIL","message":"Username is not existed"}
                if password == r.get("user:" + username +":password"):
                    self.current_user = username
                    r.sadd("online_user", username)
                    return {"code":"LOGIN_SUCCESS","message":"success"}
                else:
                    return {"code":"LOGIN_FAIL","message":"Username and password not match"}
            except Exception, e:
                print "Error:",e.message
                return {"code":"SERVER_ERROR","message":"Server Error"}



           
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST = "localhost"
    PORT = 12345
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    
    SocketServer.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(ADDR, ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    print " .... waiting for connection"

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()