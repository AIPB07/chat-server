import socket
import selectors
import errno
import sys
import time

HEADER_LENGTH = 10
HOST = '127.0.0.1'
PORT = 54321

print('\nWelcome to the chat server!\n')
time.sleep(1)
print('Hit enter to send message or refresh message feed\n')
time.sleep(1)
print('Type "quit" to leave the chat\n')
time.sleep(1)
my_username = input('Enter username: ')

# Set up client socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.setblocking(False)

# Send username to server with a header
my_username_enc = my_username.encode("utf-8")
my_username_header = f'{len(my_username_enc):<{HEADER_LENGTH}}'.encode("utf-8")
sock.send(my_username_header + my_username_enc)

while True:
	msg = input(f'{my_username}> ')
	if msg.lower() == 'quit':
		sock.close()
		print('Connection closed')
		sys.exit()
	elif msg:
		# Send message
		msg_enc = msg.encode("utf-8")
		msg_header = f'{len(msg_enc):<{HEADER_LENGTH}}'.encode("utf-8")
		sock.send(msg_header + msg_enc)
	try:
		# Receive messages
		while True:
			user_header = sock.recv(HEADER_LENGTH)
			if not user_header:
				print('Connection closed by server')
				sys.exit()
			user_len = int(user_header.decode("utf-8").strip())
			user = sock.recv(user_len).decode("utf-8")
			msg_header = sock.recv(HEADER_LENGTH)
			msg_len = int(msg_header.decode("utf-8").strip())
			msg = sock.recv(msg_len).decode("utf-8")
			print(f'{user}> {msg}')
	except IOError as e:
		# EAGAIN and EWOULDBLOCK are standard errors when non-blocking socket 
		# operation cannot be performed immediately
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print(f'Reading error: {str(e)}')
		continue
	except Exception as e:
		# Any other exception
		print(f'Reading error: {str(e)}')
		sys.exit()


