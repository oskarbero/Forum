import socket
import sys
import getopt
import getpass
import string

# Defualt values
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

# 1. SEND: post group_name
info = bytes("get " + group_name, 'UTF-8')
socket.send(info)

# TODO: find a better way to do get client
response = socket.recv(1024).decode('UTF-8')

if not response == 'Ok':
    print(response)
    exit(1)

socket.send(bytes(' ', 'UTF-8'))
response = socket.recv(1024).decode('UTF-8')
print(response)

exit(0)

