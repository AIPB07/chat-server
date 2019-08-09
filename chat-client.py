import socket
import selectors
import errno
import sys
import time
import ipaddress
import msvcrt
import signal

HEADER_LENGTH = 10
PORT = 54321


def send_msg(sock, msg):
	"""Function for sending message to server"""

	totalsent = 0
	while totalsent < len(msg):
		try:
			sent = sock.send(msg[totalsent:])
		except:
			print('Message failed to send')
			return
		if sent == 0:
			print('Socket connection broken')
			return
		totalsent += sent


def recv_msg(sock, msg_len):
	"""Function for receiving fixed-length message from server"""

	msg = b''
	while len(msg) < msg_len:
		#try:
		chunk = sock.recv(min(msg_len, msg_len - len(msg)))
		#except:
			#print('Failed to receive message')
			#return
		if chunk == b'':
			return
		msg += chunk
	return msg


def signal_handler(sig, frame):
	"""Signal handler to detect Ctrl+C"""

	print('You pressed Ctrl+C! Connection closed')
	sock.close()
	sys.exit()


# Ensure correct usage
if len(sys.argv) != 2:
	print('Usage: python chat-client.py IPv4')
	sys.exit()

# Validate IP address
try:
	server_ip = ipaddress.IPv4Address(sys.argv[1])
except ipaddress.AddressValueError:
	print('Please provide a valid IPv4 address')
	sys.exit()

HOST = sys.argv[1]

print('\nWelcome to the chat server!\n')
time.sleep(1)
print('Hit "Ctrl+C" to leave the chat\n')
time.sleep(1)
while True:
	my_username = input('Enter username: ')
	if my_username:
		try:
			my_username_enc = my_username.encode("utf-8")
		except UnicodeEncodeError:
			print('Invalid username. Please try another')
			continue
		break
	print('Please enter a username')

# Configure client socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	sock.connect((HOST, PORT))
except:
	print('Failed to connect to server')
	sys.exit()
sock.setblocking(False)

# Send username to server with a header
my_username_header = f'{len(my_username_enc):<{HEADER_LENGTH}}'.encode("utf-8")
send_msg(sock, my_username_header + my_username_enc)

while True:
	signal.signal(signal.SIGINT, signal_handler)
	if msvcrt.kbhit():
		while True:
			msg = input(f'{my_username}> ')
			if msg:
				try:
					msg_enc = msg.encode("utf-8")
				except UnicodeEncodeError:
					print('Invalid message. Please try another')
					continue
				break
		# Send message
		msg_enc = msg.encode("utf-8")
		msg_header = f'{len(msg_enc):<{HEADER_LENGTH}}'.encode("utf-8")
		send_msg(sock, msg_header + msg_enc)
	try:
		# Receive messages
		while True:
			user_header = recv_msg(sock, HEADER_LENGTH)
			if not user_header:
				print('Connection closed by server')
				sock.close()
				sys.exit()
				break
			user_len = int(user_header.decode("utf-8").strip())
			user = sock.recv(user_len).decode("utf-8")
			msg_header = recv_msg(sock, HEADER_LENGTH)
			msg_len = int(msg_header.decode("utf-8").strip())
			msg = recv_msg(sock, msg_len).decode("utf-8")
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
		break


