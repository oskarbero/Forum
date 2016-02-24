import socket
import sys
import getopt


# Defualt values
host = '127.0.0.1'
port = 55555
group_name = ''

try:
    arguments = sys.argv[1:]
    opts, args = getopt.getopt(arguments,"p:h:")
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

# Check that given arguments start with the options
if len(arguments) > 2 and not(arguments[0] == '-p' or arguments[0] == '-h'):
    print("Error: invalid command")
    exit(1)
else:
    for opt, arg in opts:      # Parse arguments
        if opt == '-p':
            port = int(arg)
        elif opt == '-h':
            host = socket.gethostbyname(arg)    # In case the host is a name not an IP addr

# Get group name
if len(arguments) == len(opts)*2 + 1:
    group_name = arguments[len(opts) * 2]
elif group_name == '':
    print("error: invalid command")
    exit(1)

# Set up client socket and connect to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, port))

# 1. SEND: post group_name
info = bytes("get %s"%group_name)
info.encode('UTF-8')
server.send(info)

# 2. RECV: response or error
response = server.recv(1024).decode('UTF-8')
if response == 'Ok':

# 3. RECV: all messages from the server
    while response:
        response = server.recv(1024).decode('UTF-8')
        print(response)
else:
    print(response)
    exit(1)

# End
exit(0)

