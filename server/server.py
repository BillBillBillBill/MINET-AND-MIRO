#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import threading
import SocketServer
import json
import functools
import time
import traceback
from conn import r


# 检测端口是否被占用
def isPortOpen(port):
    import telnetlib
    try:
        test = telnetlib.Telnet('localhost', port)
        test.close()
        return True
    except:
        return False


connections = []
recv_connections = []

# 检查用户是否登录
def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.isLogin:
            # print "用户没有登录，操作失败"
            return {"code": "AUTH_NEED", "message": "You need to login first"}
        else:
            # print "已登录 操作成功"
            return method(self, *args, **kwargs)
    return wrapper

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.isLogin = False
        self.user = None
        self.p2p_server_host = None
        self.p2p_server_port = None
        self.is_recv_boardcast = False
        self.allow_action = {
            "handshake": self.handshake_handler,
            "register": self.register_handler,
            "login": self.login_handler,
            "logout": self.logout_handler,
            "show_info": self.show_info,
            "broadcast": self.broadcast_handler,
            "get_online_user": self.get_user_info,
        }

    def finish(self):
        if self in connections:
            connections.remove(self)
        if self in recv_connections:
            recv_connections.remove(self)

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
            # 没有判断 wfile 是否已经 close 就直接调用 flush()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    # 处理用户发来的消息
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
                    print "Receive json :%r" % (response)
                except Exception as e:
                    print "Error:{} / Receive data:{} / traceback:{}".format(e.message, data, traceback.format_exc())
                    response = '{"code":"JSON_REQUIRE","message":"Please send json format"}'
                self.request.sendall(response)
        except Exception as e:
            print "Error:{} / traceback:{}".format(e.message, traceback.format_exc())


    # 根据不同action交给不同的handler处理
    def handle_action(self, action_type):
        print "Receive action:[%s]" % action_type

        if action_type not in self.allow_action.keys():
            return {"code": "UNKNOWN_METHOD", "message": "The action is unknown"}
        else:
            return self.allow_action[action_type]()

    # 显示信息
    def show_info(self):
        return {"code": "CURRENT_THREADS", "message": "The current threads are {}, current users ars {}".format(connections, self.get_all_user())}

    # 获取在线用户信息
    def get_user_info(self):
        user_info = []
        for conn in connections:
            user_info.append([conn.get_user(), r.get("user:" + conn.get_user() + ":nickname"), conn.p2p_server_host, conn.p2p_server_port])
        return user_info

    # 握手
    def handshake_handler(self):
        self.p2p_server_port = self.jdata.get("self_p2p_server_port", "")
        self.p2p_server_host = self.jdata.get("self_p2p_server_host", "")
        if self.jdata.get("is_recv_boardcast", "") == "yes":
            self.is_recv_boardcast = True
        if self.jdata.get("agent") == "MINET":
            return {"server": "MIRO"}
        else:
            return {"code": "UNKNOWN_AGENT", "message": "Your agent is rejected."}

    # 用户注册
    def register_handler(self):
        username = self.jdata.get("username")
        password = self.jdata.get("password")
        nickname = self.jdata.get("nickname")
        if not all([username, password, nickname]):
            return {"code": "REGISTER_FAIL", "message": "You need send username, password and nickname"}
        else:
            try:
                if r.exists("user:" + username + ":password"):
                    return {"code":"REGISTER_FAIL", "message": "Username is registered"}
                r.set("user:" + username + ":password", password)
                r.set("user:" + username + ":nickname", nickname)
                return {"code": "REGISTER_SUCCESS", "message": "success"}
            except Exception, e:
                print "Error:",e.message,traceback.format_exc()
                return {"code": "SERVER_ERROR", "message": "Server Error"}

    # 用户登录
    def login_handler(self):
        username = self.jdata.get("username")
        password = self.jdata.get("password")
        if not all([username, password]):
            return {"code": "LOGIN_FAIL", "message": "You need send username and password"}
        else:
            try:
                if not r.exists("user:" + username + ":password"):
                    return {"code": "LOGIN_FAIL", "message": "Username is not existed"}
                if password == r.get("user:" + username + ":password"):
                    if self.is_recv_boardcast:
                        recv_connections.append(self)
                    else:
                        connections.append(self)

                    self.user = username
                    self.isLogin = True
                    if not self.is_recv_boardcast:
                        self.broadcast_login()
                        r.sadd("online_user", username)
                    #self.broadcast({"action": "login", "user": self.get_user(), "nickname": r.get("user:" + username +":nickname")})
                    return {"code": "LOGIN_SUCCESS", "message": "success", "nickname": r.get("user:" + self.get_user() + ":nickname")}
                else:
                    return {"code": "LOGIN_FAIL", "message": "Username and password not match"}
            except Exception, e:
                print "Error:", e.message,traceback.format_exc()
                return {"code": "SERVER_ERROR", "message": "Server Error"}


    # 用户登出
    @authenticated
    def logout_handler(self):
        try:
            self.broadcast_logout()
            r.srem("online_user", self.user)
            self.isLogin = False
            # self.broadcast({"action": "logout", "user": self.get_user(), "nickname": r.get("user:" + self.get_user() +":nickname")})
        except Exception, e:
            print e
        return {"code": "LOGOUT_SUCCESS", "message": "success"}

    # 处理广播事件
    @authenticated
    def broadcast_handler(self, content=None):
        if not content:
            content = self.jdata.get("content")
        if not content:
            return {"code": "BROADCAST_FAIL", "message": "content length must > 0"}
        now_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        broadcast_msg = {
            "time": now_time,
            "content": content,
            "user": self.user,
            "nickname": r.get("user:" + self.user + ":nickname")
        }
        self.broadcast(broadcast_msg)
        return {"code": "BROADCAST_SUCCESS", "message": ""}


    def broadcast_login(self):
        now_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        broadcast_msg = {
            "time": now_time,
            "content": u"用户%s进入聊天室\n" % r.get("user:" + self.user + ":nickname"),
            "user": self.user,
            "nickname": "【系统消息】"
        }
        self.broadcast(broadcast_msg)


    def broadcast_logout(self):
        now_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        broadcast_msg = {
            "time": now_time,
            "content": u"用户%s退出聊天室\n" % r.get("user:" + self.user + ":nickname"),
            "user": self.user,
            "nickname": "【系统消息】"
        }
        self.broadcast(broadcast_msg)

    # 进行广播
    def broadcast(self, content=None):
        # 向所有在线用户发送该消息
        for conn in recv_connections:
            if conn.get_user() != self.user:
                print "向{}发送消息".format(conn.get_user())
                conn.request.sendall(json.dumps(content))

           
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# 启动服务器
def start_MIRO():
    # Port 0 means to select an arbitrary unused port
    HOST = "localhost"
    PORT = 12345
    # 寻找可用端口
    while isPortOpen(PORT):
        PORT += 1
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    SocketServer.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(ADDR, ThreadedTCPRequestHandler)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True

    print u"MIRO 开启，监听端口：", PORT
    server_thread.start()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

if __name__ == "__main__":
    start_MIRO()