import threading
import socket
import sys
import getopt

# TODO: Validation for groupname / user id
# TODO: 

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
        self.num_conn = 0
        self.groups = []

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            # not sure if im gonna need that timeout
            client.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client,address)).start()
            ThreadedServer.num_conn += 1
            print('Server Listening to ', ThreadedServer.num_conn, 'clients')

    def listen_to_client(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)

                # here is where we build message / validate
                if data:
                    response = data
                    client.send(response)
                else:
                    raise socket.error('Client disconnected')
            except:
                client.close()
                ThreadedServer.num_conn -= 1
                print('Client disconnected listening to: ', ThreadedServer.num_conn, 'clients')
                return False

if __name__ == "__main__":
    ThreadedServer('', port).listen()


