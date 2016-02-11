import threading
import socket
import sys
import getopt
import string

# TODO: Add more loops based on the request comming in
# TODO: Build and store messages

#defualt port
port = 50505

try:
    opts, args = getopt.getopt(sys.argv[1:],"p:")
# Wong command - exit
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

#get argument
for opt, arg in opts:
    if opt == '-p':
        port = int(arg)
    else:
        print("error: invalid command")
        exit(1)

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


class ThreadedServer(object):
    num_conn = 0
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.groups = []

#TODO: Separate threads for get and post .. so that we can have a good protocol convo
    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client,address)).start()
            ThreadedServer.num_conn += 1

    #post client ?
    def listen_to_client(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    #SPLIT FOR GET / POST
                    s = bytes.decode(data, 'utf-8')
                       #check for meta data
                    if s[1] == 'g' or s[1] == 'u':
                        if self.validate_header(s):
                            client.send(bytes('Ok', 'utf-8'))
                            if s[1] == 'g':# choose groupname
                                print("group name: ", s)
                            elif s[1] == 'u': #chose username
                                print("username: ", s)
                                s = s[3:] #consume the [meta] header
                            else:
                                client.send(bytes('Error: Invalid group name', 'utf-8'))
                    else:
                        message = s
                        print("message: ", message)
                else:
                    raise socket.error('Client disconnected')
            except:
                client.close()
                ThreadedServer.num_conn -= 1
                print('Client disconnected listening to: ', ThreadedServer.num_conn, 'clients')
                return False

    def validate_header(self, info):
        p_chars = set(string.printable)
        if "[g]" not in info[0:3]:
            if "[u]" not in info:
                return False
        if (' ' not in info) and set(info).issubset(p_chars):
            return True
        return False

if __name__ == "__main__":
    ThreadedServer('', port).listen()


