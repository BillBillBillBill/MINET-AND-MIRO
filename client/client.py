#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import json

class TcpClient:
    HOST = "localhost"
    PORT = 12345
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def start_query(self):
        while True:
            data = raw_input(">")
            if not data:
                break
            self.client.send(data.encode('utf8'))
            data = self.client.recv(self.BUFSIZ)
            if not data:
                break
            print data.decode('utf8')


    def send_json(self, message):
        try:
            print "Send: {}".format(message)
            self.client.sendall(message)
            response = self.client.recv(self.BUFSIZ)
            jresp = json.loads(response)
            print "Recv: ",jresp
        except Exception as e:
            print e
        # finally:
        #     self.client.close()

    def __exit__(self):
        self.client.send("EXIT")
        self.client.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port

    msg1 = {'src':'hello', 'dst':"bar"}
    jmsg1 = json.dumps(msg1)
    client = TcpClient()
    client.send_json(jmsg1)
    client.start_query()
