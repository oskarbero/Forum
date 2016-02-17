# Post client
import socket
import sys
import getopt
import getpass
import string
# defualt values
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

#print('port ', port , '\nhost: ' , host , '\ngroupname: ', group_name)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

info = bytes("post " + group_name, 'UTF-8')
# 1. SEND: post group_name
socket.send(info)

# 2. Check response - ok or error
response = socket.recv(1024).decode('UTF-8')
if not (response == 'Ok'):
    #print(response) #error
    exit(1)

# 3. Send user name
info = bytes("id " + getpass.getuser(), 'UTF-8')
socket.send(info)

# 4. Check response
response = socket.recv(1024)
#.decode('UTF-8')
if not (response.decode('UTF-8') == 'Ok'):
    print(response) #error
    exit(1)

# Typed message part ..  take everything up to the ! mark
while True:
    data = input('message: ')
    # check EOL - my own !
    if data == '<!':
        exit(1)
    # encode as byte stream
    socket.send(bytes(data, 'UTF-8'))

    # decode bytestream to plaintext
    #response = (socket.recv(1024)).decode('utf-8')
    #print("response: ", response)
