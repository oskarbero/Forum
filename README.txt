==============================================================================
Post Client 
================================================================================

Goal: Allows to post a message to a specific groupp on the server

Call: $ post [-h hostname] [-p port] groupname

Defaults:
	host: localhost  // 127.0.0.1
	port: 50505		// hardcoded

Prtocol:
	1. User call: $post groupname
		-> client parses and validates input
		-> send "post groupname" to specified (or local) server

	2. Server Responds:
		-> *Ralidate groupname to be only printable characters and no white space
		-> If string starts with "error" client prints error message and exits
		-> If string is "OK" silently continue

[Test: valid groupname] 

	3. Client gets 'Ok' sends user's login name 
		-> send "id username" to server
		-> getting the name in py is: 

	4. Server Response:
		-> * Validate syntax of the command and user name to ensure that string is printable 
		-> If not send error to client -> print error
		-> Otherwise send OK
[Test: valid username ] 

	5. Client gets 'Ok'
		-> Read everything from std input and write to socket
		-> once end of file on the input stream - close socket 

[Q: What do you mean by end-of-file chosen ? Not sure what you mean here /// PICK MY OWN ?]


Functions of note:
------------------------------------------
import string
import getpass 

#get user name
getpass.getuser() 

#check if printable
def printable(str):	
	printset = set(string.printable)
	isprintable = set(str).issubset(printset)

#check if sring contains no whitespace
if (str.strip() == ' ')
		
Test Case Equivalence Classes:
-----------------------------------------------------------

1. ERROR: Invalid command:

Ex:
	$python pots group							// typo in post
	$python post -h groupname					// host not found				 
	$python post -h 127.0.0.1 -p 3311 testgrp   // host not found / wrong socket

Output:
	server $: error: invalid command
	exit(1)
	
2. Groupname doesnt exist 

Output:
	server $: error: invalid groupname 
	exit(1)



==============================================================================
Post Client 
================================================================================

Goal: Retrieve all messages from a specific group on the server 

Call: $ get [-h hostname] [-p port] groupname

Defaults:
	host: localhost  // 127.0.0.1
	port: 50505		// hardcoded

Prtocol:
	1. User sends "$get groupname"
	
	2. Server Validates
		-> Validate groupname printable/whitespace
		-> Send error if something went wrong
		-> Send silent "ok" + number of messages

	3. Client reads stream of bytes until server sends end-of-file


==============================================================================
SERVER Client 
================================================================================
Goal: Server side of protocols for Get and Post

Call: $ server [-p port]

Default:
	port: 50505		//hardcoded

Protocol:
	- server waits to accept connections
	- it is multithreaded so it can get multiple connections at once 
	- Returns error string if the command recieved is not a get or post
		and closes connection for that client
	- Validates the group name to ensure that the name contains only printable tex
		otherwise send error

Group Management:
	- No persistance
	- Need to keep track of any number of groups and any number of messages within a group
	- each message will be identified by the creator's IP address, port number, user name and timestamp

Post Requests:
	- If groupname is valid but doesn't exist create it with msg count of 0
	- Then read id and validate command and username

	- When recieving the message store source IP addr and port, username and timestamp
	- read data from the socket every byte read becomes part of the message
EOF on socket closes the connection

GET REQ:
	- Validate syntax / grpname

Response format:
	1. Header of the format
		"From Username host:port timestamp"
	2. blank line
	3. The message (spanning any num of lines)
	4. A blank line IFF there is another message


========================================================================================
NOTES:

1. Need to find synchronization primitves in python
2. Need to make the asynchronous server model
3. Need to write the basic validations on client side - argv 
4. Timestamp in python should be easy











