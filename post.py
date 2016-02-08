# Echo client program - basis for the GET and POST 
import socket
import sys
import getopt

# defualt values
host = '127.0.0.1'
port = 50505
group_name = ''

try:
    opts, args = getopt.getopt(sys.argv[1:],"p:h:")
# Wong command - exit
except getopt.GetoptError:
    print("error: invalid command")
    exit(1)

# argv parsing
for opt, arg in opts:
    if opt == '-p':
        port = int(arg)
    elif opt == '-h':
        host = arg

# get last argv (should always be group name otherwise its wrong
group_name = sys.argv.pop()
if group_name == '':
    print("error: invalid command")
    exit(1)

print('port ', port , '\nhost: ' , host , '\ngroupname: ', group_name)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))


# Typed message part ..  take everything up to the ! mark
while True:
    data = input('message: ')
    # check EOL - my own !
    if data == '<!':
        exit(1)

    # encode as byte stream
    socket.send(bytes(data, 'UTF-8'))

    # decode bytestream to plaintext
    response = (socket.recv(1024)).decode('utf-8')
    print("response: ", response)

