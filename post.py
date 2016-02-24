# Post client
import socket
import sys
import getopt
import getpass

# TODO: Add Try/Except blocks to this on thursday
# TODO: Test on ilabs adapt to python 2.6 and 2.7

# Default values
host = '127.0.0.1'
port = 55555
group_name = ''

try:
    arguments = sys.argv[1:]
    opts, args = getopt.getopt(arguments,"p:h:")
# Wong command - exit
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

# Check for valid input format
if len(arguments) > 2 and not(arguments[0] == '-p' or arguments[0] == '-h'):
    print("Error: invalid command")
    exit(1)

else:
    for opt, arg in opts:             # Parse arguments
        if opt == '-p':
            port = int(arg)
        elif opt == '-h':
            host = socket.gethostbyname(arg) #Just in case it's a name address like vi.cs.rutgers.edu

# Get group name from arguments
if len(arguments) == len(opts)*2 + 1:
    group_name = arguments[len(opts) * 2]
else:
    if group_name == '':
        print("error: invalid command")
        exit(1)

# TODO: Surround with a Try/Catch Block
# Connect to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, port))

# 1. SEND: post group_name
info = bytes("post %s"%group_name,'UTF-8')
server.send(info)

# 2. Check response - ok or error
response = server.recv(1024).decode('UTF-8')
if not (response == 'Ok'):
    print(response) #error
    server.close()
    exit(1)

# 3. Send user name
info = bytes("id %s"%getpass.getuser(), 'UTF-8')
server.send(info)

# 4. Check response
response = server.recv(1024).decode('UTF-8')
if not (response == 'Ok'):
    print(response) #error
    server.close()
    exit(1)

# 5. Post message to the server
total = ''
data = input('Message: \n')
while not data == '!>':
    # Total message and newline when newline is pressed
    total = total + data
    data = input()
    if data != '!>':
        total += '\n'

server.send(bytes(total, 'UTF-8'))

server.close()
exit(0)
