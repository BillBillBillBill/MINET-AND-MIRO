#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import threading
import SocketServer
import json, types,string
import functools
import time
import datetime
import traceback
from conn import r

connections = []

def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.isLogin:
            print "用户没有登录，操作失败"
            return {"code": "AUTH_NEED", "message": "You need to login first"}
        else:
            print "已登录 操作成功"
            return method(self, *args, **kwargs)
    return wrapper

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):


    def setup(self):
        self.isLogin = False
        self.user = None
        self.allow_action = {
            "handshake": self.handshake_handler,
            "register": self.register_handler,
            "login": self.login_handler,
            "show_info": self.show_info,
            "broadcast": self.broadcast_handler
        }
        connections.append(self)

    def finish(self):
        connections.remove(self)

    def get_user(self):
        return self.user

    def get_all_user(self):
        return [conn.get_user() for conn in connections]

    # 重载其基类BaseHTTPRequestHandler的成员函数handle_one_reques
    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            #没有判断 wfile 是否已经 close 就直接调用 flush()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return


    def handle(self):
        try:
            while 1:
                print connections
                if self.isLogin:
                    print "用户[{}]发来消息".format(self.user)
                data = self.request.recv(1024)
                if not data:
                    print "用户退出"
                    break
                try:
                    # 读取发来的json
                    self.jdata = json.loads(data)
                    action_type = self.jdata.get("action")
                    # 根据请求由不同handler处理
                    response = self.handle_action(action_type)
                    response = json.dumps(response)
                    print "Receive json :%r"% (response)
                except Exception as e:
                    print "Error:{} / Receive data:{} / traceback:{}".format(e.message, data, traceback.format_exc())
                    response = '{"code":"JSON_REQUIRE","message":"Please send json format"}'
                self.request.sendall(response)
        except Exception as e:
            print "Error:{} / traceback:{}".format(e.message, traceback.format_exc())


    def handle_action(self, action_type):
        print "Receive action:[%s]" % action_type

        if action_type not in self.allow_action.keys():
            return {"code": "UNKNOWN_METHOD", "message": "The action is unknown"}
        else:
            return self.allow_action[action_type]()

    def show_info(self):
        return {"code": "CURRENT_THREADS", "message": "The current threads are {}, current users ars {}".format(connections, self.get_all_user())}

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
                print "Error:",e.message,traceback.format_exc()
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
                    self.user = username
                    self.isLogin = True
                    return {"code":"LOGIN_SUCCESS","message":"success"}
                else:
                    return {"code":"LOGIN_FAIL","message":"Username and password not match"}
            except Exception, e:
                print "Error:",e.message,traceback.format_exc()
                return {"code":"SERVER_ERROR","message":"Server Error"}

    @authenticated
    def broadcast_handler(self):
        content = self.jdata.get("content")
        now_time = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        if not content:
            return {"code":"BROADCAST_FAIL","message":"content length must > 0"}
        broadcast_msg = {
            "time": now_time,
            "content": content,
            "user": self.current_user,
            "nickname": r.get("user:" + self.current_user +":nickname")
        }
        print "新消息：", broadcast_msg
        # 向所有在线用户发送该消息
        for conn in connections:
            if conn.get_user() != self.user:
                print "向{}发送消息".format(conn.get_user())
                conn.request.sendall(json.dumps(broadcast_msg))
        return {"code":"BROADCAST_SUCCESS","message":""}



           
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
    # ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    # print "Server loop running in thread:", server_thread.name
    #print "等待连接"


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()