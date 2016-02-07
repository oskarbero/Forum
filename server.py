import threading
import socket
import sys
import string

class Group: 
    def __init__(self, name):
        self.name = name
        self.messages = []

class Message:
    def __init__(self, ip, port, u_name, timestamp):
        self.ip = ip
        self.port = port
        self.u_name = u_name
        self.timestamp = timestamp
        self.msg = []


#temporary server thing
class AsyncServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = []

    def run(self):
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        print('Connected by', addr)
        while 1:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)
        conn.close()


server = AsyncServer()
server.data = ['hello', 'world']
server.start()
print('The main program continues to run in foreground.')

server.join()                     # Wait for the background task to finish
print('Main program waited until background was done.')
