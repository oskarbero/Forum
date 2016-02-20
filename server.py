import threading
import socket
import sys
import getopt
import string
import time, datetime

# TODO: Better error descriptions etc...
# TODO: Better Get client - find a way to just recieve all info back to back
# TODO: Clean up clean up .. everybody cleanup!
# TODO: Got a job fuck yeahhhh!!!!! 

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
    def __init__(self, header, message):
        self.header = header
        self.msg = message
        self.total = "{}\n{}".format(header,message)


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

    #post client ?
    def listen_to_client(self, client, address):
        size = 1024
        # Data local to the thread
        data = threading.local()
        # msg_flag is for avoiding confusion if for example the message starts with the word post
        data.msg_flag = False
        data.get_flag = False

        while True:
            try:
                incoming = client.recv(size)
                if incoming:
                    # Decode the bytes in the message
                    s = bytes.decode(incoming, 'utf-8')

                    # $POST GROUP_NAME
                    if s[:5] == 'post ':
                        data.groupname = s[5:]

                        # validate groupname is printable and has no spaces
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

                            client.send(bytes('Ok', 'utf-8'))
                        else:
                            client.send(bytes('Error: Invalid group name', 'UTF-8'))
                            raise socket.error('Client disconnected')

                    # $ID USERNAME
                    elif s[:3] == 'id ' and data.msg_flag:
                        data.username = s[3:]

                        if set(data.username).issubset(string.printable):
                            client.send(bytes('Ok', 'UTF-8'))
                        else:
                            client.send(bytes('Error: Invalid username', 'UTF-8'))
                            raise socket.error('Client disconnected')

                    # $GET GROUP_NAME
                    elif s[:4] == 'get ':
                        data.groupname = s[4:]

                        if self.valid_group(data.groupname):
                            data.get_flag = True
                            exists, data.group = self.get_group(data.groupname)
                            # Check if it is a new group
                            if exists:
                                client.send(bytes('Ok', 'UTF-8'))
                                continue
                            else:
                                # Group You're getting from does not exist
                                client.send(bytes('Error: Invalid group name', 'UTF-8'))
                                raise socket.error('Client disconnected')

                    # SAVE MESSAGE FROM USER
                    elif data.msg_flag:
                        #synchronize to not overwrite anything
                        self.mutex_lock.acquire()
                        data.group.messages.append(self.build_message(address, data.username, s))
                        self.mutex_lock.release()

                        client.close()
                        return True

                    # TRANSMIT MESSAGE TO USER
                    elif data.get_flag:
                        total = "Messages: %s\n\n"%len(data.group.messages)

                        for msg in data.group.messages:
                               total += msg.total + '\n'
                        print(total)
                        client.send(bytes(total, 'UTF-8'))

                        # Done with Get Client
                        client.close()
                        return True
                    else:
                        client.send(bytes('Error: Invalid Command', 'UTF-8'))
                        raise socket.error('Client disconnected')

                else:
                    raise socket.error('Client disconnected')
            except:
                client.close()
                ThreadedServer.num_conn -= 1
                #print('Client disconnected listening to: ', ThreadedServer.num_conn, 'clients') #not really needed
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

    # TODO: Make sure it's compliant with the spec for Assignment 3
    def build_message(self, address, uname, message):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%a %b %d %H:%M:%S %Z %Y')
        header = "{}/{}:{} {}\n".format(uname, address[0],address[1] , timestamp)
        return Message(header, message)

if __name__ == "__main__":
    ThreadedServer('', port).listen()


