import threading
import socket
import sys
import getopt
import string
import time, datetime

# TODO: Add more Try/Except blocks
# TODO: Test on Ilabs for python 2.6/2.7 test for non local hosts and hosts by name
# TODO: Test all argvs

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

# Data structure
class Group:
    def __init__(self, name):
        self.name = name
        self.msg_cnt = 0
        self.messages = []


class Message:
    def __init__(self, header, message):
        self.header = header
        self.msg = message


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

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client,address)).start()
            ThreadedServer.num_conn += 1

    def listen_to_client(self, client, address):
        size = 1024
        # Data local to the thread
        data = threading.local()
        # msg_flag is for avoiding confusion if for example the message starts with the word post
        data.msg_flag = False

        while True:
            try:
                incoming = client.recv(size)
                if incoming:
                    # Decode the bytes in the message
                    recv_str = bytes.decode(incoming, 'utf-8')

                    # POST GROUP_NAME
                    if recv_str[:5] == 'post ':
                        data.groupname = recv_str[5:]

                        # 1. Validate Groupname
                        if self.valid_group(data.groupname):
                            data.msg_flag = True
                            exists, data.group = self.get_group(data.groupname)

                            # Check if it is a new group
                            if not exists:
                                data.group = Group(data.groupname)
                                # Prevent race conditions on adding a group
                                self.mutex_lock.acquire()
                                self.groups.append(data.group)
                                self.mutex_lock.release()
                        # 2. Send Ok or error
                            client.send(bytes('Ok', 'utf-8'))
                        else:
                            client.send(bytes('Error: Invalid group name', 'UTF-8'))
                            raise socket.error('Client disconnected')

                    # $ID USERNAME
                    elif recv_str[:3] == 'id ' and data.msg_flag:
                        data.username = recv_str[3:]
                        # 3. Validate username
                        if set(data.username).issubset(string.printable):

                        # 4. Send Ok or error
                            client.send(bytes('Ok', 'UTF-8'))
                        else:
                            client.send(bytes('Error: Invalid username', 'UTF-8'))
                            raise socket.error('Client disconnected')

                    # SAVE MESSAGE FROM USER
                    elif data.msg_flag:
                        # 5. Get and store the new message
                        self.mutex_lock.acquire()       # Prevent race conditions of any kind
                        data.group.messages.append(self.build_message(address, data.username, recv_str))
                        data.group.msg_cnt += 1
                        self.mutex_lock.release()

                        return True

                    # GET GROUP_NAME
                    elif recv_str[:4] == 'get ':
                        data.groupname = recv_str[4:]

                        # 1. Validate group name
                        if self.valid_group(data.groupname):
                            exists, data.group = self.get_group(data.groupname)

                        # 2. Send Ok or error
                            if exists:
                                client.send(bytes('Ok', 'UTF-8'))
                        # 3. Send # of messages
                                client.send(bytes("Messages: %s\n"%data.group.msg_cnt, 'UTF-8'))

                        # 4. Send header then message loop
                                for msg in data.group.messages:
                                    client.send(bytes(msg.header, 'UTF-8'))
                                    client.send(bytes(msg.msg + '\n', 'UTF-8'))

                                client.shutdown()
                                client.close()
                                return True
                            else:
                                # Group you're getting from does not exist
                                client.send(bytes('Error: Invalid group name', 'UTF-8'))
                                raise socket.error('Client disconnected')
                    else:
                        client.send(bytes('Error: Invalid Command', 'UTF-8'))
                        raise socket.error('Client disconnected')

                else:
                    raise socket.error('Client disconnected')
            except:
                client.close()
                ThreadedServer.num_conn -= 1    # No mutex here the race condition not very important
                print('Client disconnected listening to: ', ThreadedServer.num_conn, 'clients')
                return False

    # Validate group name
    def valid_group(self, groupname):
        if ' ' not in groupname and set(groupname).issubset(string.printable):
            return True
        return False

    # Find group in our array
    def get_group(self, name):
        for g in self.groups:
            if g.name == name:
                return True, g
        return False, False

    def build_message(self, address, uname, message):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%a %b %d %H:%M:%S %Z %Y')
        header = "{}/{}:{} {}\n".format(uname, address[0],address[1] , timestamp)
        return Message(header, message)

if __name__ == "__main__":
    ThreadedServer('', port).listen()


