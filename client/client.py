#!/usr/bin/env python
#coding:utf-8

import socket
import json
import time

import threading
import SocketServer
import traceback
import uuid

from PyQt5.QtWidgets import QTextBrowser


# 检测端口是否被占用
def isPortOpen(port):
    import telnetlib
    try:
        test = telnetlib.Telnet('localhost', port)
        test.close()
        return True
    except:
        return False


# 生成一个secrect id
def generate_secrect_id():
    return uuid.uuid4().hex


class TcpClient:
    HOST = "localhost"
    PORT = 12345
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    def __init__(self, UI=None, is_recv_boardcast=False):
        self.isMIRO = False
        self.isLogin = False
        self.nickname = None
        self.UI = UI
        self.is_recv_boardcast = is_recv_boardcast
        self.jdata = {}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        # print self.client.getpeername()
        # print self.client.getsockname()
        # self.handshake()
        self.allow_action = ["handshake", "register", "login", "logout", "broadcast", "get_online_user"]

    def handshake(self, self_p2p_server_host=None, self_p2p_server_port=None):
        if self.is_recv_boardcast:
            ack_msg = {"action": "handshake", "agent": "MINET", "is_recv_boardcast": "yes"}
        else:
            ack_msg = {"action": "handshake", "agent": "MINET"}
        if self_p2p_server_host:
            ack_msg["self_p2p_server_host"] = self_p2p_server_host
        if self_p2p_server_port:
            ack_msg["self_p2p_server_port"] = self_p2p_server_port
        ack_msg = json.dumps(ack_msg)
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
            if self.jdata.get("nickname"):
                self.nickname = self.jdata.get("nickname")
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
            self.send_json_and_recv(broadcast_msg)
            print "Broadcast success"
            return True
        except Exception, e:
            print e
            print "Broadcast fail, reason:", self.jdata.get("message")
            return False

    def get_online_user(self):
        get_msg = '{"action": "get_online_user"}'
        self.send_json_and_recv(get_msg)
        # 防黏包
        # if isinstance(self.jdata, dict):
        #     self.receive_one_msg()
        return self.jdata

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


############ P2P聊天部分 ############

class P2P_chat_manager(object):
    P2P_chat_objects = {}
    main_window = None


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.allow_action = {
            "handshake": self.handshake_handler,
            "chat": self.show_msg,
        }

    def finish(self):
        # 断开连接
        pass

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
                data = self.request.recv(1024)
                if not data:
                    break
                try:
                    # 读取发来的json
                    self.jdata = json.loads(data)
                    action_type = self.jdata.get("action")
                    # 根据请求由不同handler处理
                    self.handle_action(action_type)
                except Exception as e:
                    print "Error:{} / Receive data:{} / traceback:{}".format(e.message, data, traceback.format_exc())

        except Exception as e:
            print "Error:{} / traceback:{}".format(e.message, traceback.format_exc())

    # 根据不同action交给不同的handler处理
    def handle_action(self, action_type):
        print "Receive action:[%s]" % action_type

        if action_type not in self.allow_action.keys():
            self.request.sendall(json.dumps({"code": "UNKNOWN_METHOD", "message": "The action is unknown"}))
        else:
            self.allow_action[action_type]()

    # 握手
    def handshake_handler(self):
        print u"开始建立连接"
        host = self.jdata.get("host")
        port = self.jdata.get("port")
        nickname = self.jdata.get("nickname")
        secret_id = self.jdata.get("secret_id")
        if not all([host, port, nickname, secret_id]):
            self.request.sendall(json.dumps({"code": "MORE_DATA_NEEDED", "message": "You must send host, port, nickname, secret_id"}))
        else:
            try:
                if not P2P_chat_manager.P2P_chat_objects.get(secret_id):
                    # 建立对话
                    P2P_chat_manager.main_window.addTab_to_tabView_signal.emit(self.jdata)
                    print "建立连接完成"
                self.request.sendall(json.dumps({"message": "success"}))
            except Exception, e:
                print e
                self.request.sendall(json.dumps({"message": "fail"}))

    # 收取信息并显示
    def show_msg(self):
        content = self.jdata.get("content")
        secret_id = self.jdata.get("secret_id")
        P2P_chat_object = P2P_chat_manager.P2P_chat_objects.get(secret_id)
        if P2P_chat_object:
            QTextBrowserObject = P2P_chat_object.get("chat_tab")
            jdata = {"content": content, "nickname": P2P_chat_object.get("nickname")}
            P2P_chat_manager.main_window.add_format_text_to_QTextBrowser_signal.emit(jdata, QTextBrowserObject)
        else:
            print u"找不到该聊天"

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# 启动服务器
def start_P2P_chat_TCP_server(HOST="localhost", PORT=54321, UI=None):

    ADDR = (HOST, PORT)

    print "start P2P chat server at port:", PORT

    SocketServer.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(ADDR, ThreadedTCPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    server.serve_forever()


class P2PChatClient:

    def __init__(self, host, port, receiver_nickname, self_nickname, UI=None, chat_tab=None, secret_id=None):
        self.host = host
        self.port = int(port)
        self.receiver_nickname = receiver_nickname
        self.self_nickname = self_nickname
        self.UI = UI
        self.chat_tab = chat_tab
        self.secret_id = generate_secrect_id() if not secret_id else secret_id
        self.ADDR = (host, self.port)
        self.jdata = {}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.allow_action = ["handshake", "chat"]
        P2P_chat_manager.P2P_chat_objects[self.secret_id] = {}
        P2P_chat_manager.P2P_chat_objects[self.secret_id]['sender'] = self
        P2P_chat_manager.P2P_chat_objects[self.secret_id]['nickname'] = receiver_nickname

    def handshake(self, self_host, self_port):
        handshake_msg = u'{"action": "handshake", "host": "%s", "port": "%s", "nickname": "%s", "secret_id": "%s"}' % (self_host, self_port, self.self_nickname, self.secret_id)
        self.send_json_and_recv(handshake_msg)
        if self.jdata.get("message") != "success":
            print "Handshake fail"
            self.client.close()
        else:
            print "Handshake success"

    def chat(self, content=""):
        broadcast_msg = '{"action": "chat", "content": "%s", "secret_id": "%s"}' % (content, self.secret_id)
        try:
            self.send_json(broadcast_msg)
            print "Send message success"
            return True
        except Exception, e:
            print e
            print "Send message fail, reason:", self.jdata.get("message")
            return False

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
            response = self.client.recv(1024)
            self.jdata = json.loads(response)
            print "Recv: ", self.jdata
        except Exception as e:
            print "send_json_and_recv:", e

    def finish(self):
        # 断开连接
        self.client.close()

#####################################

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
