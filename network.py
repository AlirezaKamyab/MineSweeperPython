#!/usr/bin/env python3

import socket, json
from threading import Thread

class Network:
    def __init__(self, host='localhost', port=1234, buffer_size = 65536):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = buffer_size
        self.connections = []
        self.__conn_type = 0

    
    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)


    def connect(self):
        self.__conn_type = 1
        self.socket.connect((self.host, self.port))

    
    def send(self, msg, code=0):
        try:
            data = {'code':code, 'data':msg}
            data = json.dumps(data)
            self.socket.send(data.encode('utf-8'))
            print(f"Code {code}, {len(data)} Bytes sent!")
        except: return

    
    def sendall(self, msg, code=0):
        data = {'code':code, 'data':msg}
        if self.__conn_type == 0:
            for conn in self.connections:
                try:
                    conn.send(json.dumps(data).encode('utf-8'))
                    print(f"Code {code}, {len(data)} Bytes sent!")
                except: continue
            return 
        
        data = json.dumps(data)
        self.socket.sendall(data.encode('utf-8'))
        print(f"Code {code}, {len(data)} Bytes sent! To All")


    def recieve(self):
        data = socket.recv(self.buffer_size)
        data = json.loads(str(data, encoding='utf-8'))
        return data

    @staticmethod
    def sendwith(client, msg, code):
        data = {'code':code, 'data':msg}
        client.send(json.dumps(data).encode('utf-8'))
