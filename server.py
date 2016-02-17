import threading
import socket
import sys
import getopt
import string

# TODO: Synchronize on num connections / groups
# TODO: Build and store messages

#defualt port
port = 55555

try:
    opts, args = getopt.getopt(sys.argv[1:],"p:")
# Wong command - exit
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

# get argument
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
        self.msg = ''


class ThreadedServer(object):
    num_conn = 0
    groups = []
    mutex_lock = threading.Lock()

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
        # Data local to the thread
        data = threading.local()
        data.msg_flag = False
        data.groupname = ''
        data.username = ''

        while True:
            try:
                incoming = client.recv(size)

                if incoming:
                    # Decode the bytes in the message
                    s = bytes.decode(incoming, 'utf-8')

                    # make it a switch with a function that checks for this stuff
                    if s[:5] == 'post ':
                        #consume post tag
                        data.groupname = s[5:]
                        print("group name:", data.groupname)

                        # validate groupname is printable and has no spaces
                        if ' ' not in data.groupname and set(data.groupname).issubset(string.printable):
                            data.msg_flag = True

                            # Check if it is a new group
                            if not self.group_exists(data.groupname):
                                self.mutex_lock.acquire()
                                self.groups.append(Group(data.groupname))
                                self.mutex_lock.release()
                            else:
                                print("Group already exists in memory")

                            client.send(bytes('Ok', 'utf-8'))
                        else:
                            client.send(bytes('Error: Invalid group name', 'UTF-8'))

                    # id requires the post flag to be true
                    elif s[:3] == 'id ':
                        #consume id tag
                        data.username = s[3:]
                        print("username: ", data.username)

                        # validate username is printable
                        if set(data.username).issubset(string.printable):
                            client.send(bytes('Ok', 'UTF-8'))
                        else:
                            data.msg_flag = False
                            client.send(bytes('Error: Invalid username', 'UTF-8'))

                    # Need mechanism for sending all the messages
                    elif s[:4] == 'get ':
                        #consume get tag
                        s = s[4:]
                        print("[get]group name: ", s)
                        print("Messages: ")
                        client.send(bytes('Ok', 'UTF-8'))

                    # Add the given message to the given group
                    else:
                        message = s
                        print("message:", message)
                        data.msg_flag = False
                else:
                    raise socket.error('Client disconnected')
            except:
                client.close()
                ThreadedServer.num_conn -= 1
                print('Client disconnected listening to: ', ThreadedServer.num_conn, 'clients')
                return False

    def group_exists(self, name):
        for g in self.groups:
            if g.name == name:
                return True
        return False

    # Might not need the timestamp can probably generate it here
    def construct_header(self, ip, port, uname, timestamp):
        header = "From " + uname + '/' + ip + ':' + port + ' ' + timestamp
        return True

if __name__ == "__main__":
    ThreadedServer('', port).listen()


