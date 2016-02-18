# Post client
import socket
import sys
import getopt
import getpass

# TODO: Make sure the

# Default values
host = '127.0.0.1'
port = 55555
group_name = ''

# Argument Parsing
try:
    arguments = sys.argv[1:]
    opts, args = getopt.getopt(arguments,"p:h:")
# Wong command - exit
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

# if we have arguments but they dont start with an option .. quit
if len(arguments) > 2 and not(arguments[0] == '-p' or arguments[0] == '-h'):
    print("Error: invalid command")
    exit(1)

else:
    # argv parsing
    for opt, arg in opts:
        if opt == '-p':
            port = int(arg)
        elif opt == '-h':
            host = arg
#check if exists then go
if( len(arguments) == len(opts)*2 + 1):
    group_name = arguments[len(opts) * 2]
else:
    if group_name == '':
        print("error: invalid command")
        exit(1)

# TODO: Surround with a Try/Catch Block
# Connect to server
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

# 1. SEND: post group_name
info = bytes("post " + group_name, 'UTF-8')
socket.send(info)

# 2. Check response - ok or error
response = socket.recv(1024).decode('UTF-8')
if not (response == 'Ok'):
    print(response) #error
    exit(1)

# 3. Send user name
info = bytes("id " + getpass.getuser(), 'UTF-8')
socket.send(info)

# 4. Check response
response = socket.recv(1024).decode('UTF-8')
if not (response == 'Ok'):
    print(response) #error
    exit(1)

# Typed message part ..  take everything up to the ! mark
tot = ''
data = input('Message: \n')

while not data == '<!':
    # Total message and newline when newline is pressed
    tot = tot + data + '\n'
    data = input()

socket.send(bytes(tot, 'UTF-8'))
socket.close()
exit(0)
