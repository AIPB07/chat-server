import socket
import selectors

HEADER_LENGTH = 10
HOST = '0.0.0.0'
PORT = 54321
clients = []  # List for storing client information


def send_msg(sock, msg):
	"""Function for sending message to client"""

	totalsent = 0
	while totalsent < len(msg):
		try:
			sent = sock.send(msg[totalsent:])
		except OSError:
			print('Message failed to send')
			return
		if sent == 0:
			print('Socket connection broken')
			return
		totalsent += sent


def recv_msg(sock, msg_len):
	"""Function for receiving fixed-length message from client"""

	msg = b''
	while len(msg) < msg_len:
		try:
			chunk = sock.recv(min(msg_len, msg_len - len(msg)))
		except BlockingIOError:
			print('Failed to receive message (BlockingIOError)')
			return
		except OSError:
			print('Failed to receive message (OSError)')
		if chunk == b'':
			return
		msg += chunk
	return msg


def accept_connection(sock):
	"""Function to accept a new connection"""

	global clients
	conn, addr = sock.accept()
	print(f'Connected to by {addr}')
	conn.setblocking(False)

	# Receive first message. This will contain username
	user_header = recv_msg(conn, HEADER_LENGTH)
	if not user_header:
		print(f'Error receiving user header. Closing connection to {addr}')
		conn.close()
		return
	try:
		username_length = int(user_header.decode("utf-8").strip())
		username = recv_msg(conn, username_length).decode("utf-8")
	except AttributeError:
		print(f'Error receiving username. Closing connection to {addr}')
		conn.close()
		return
	except UnicodeDecodeError:
		print(f'Error decoding username. Closing connection to {addr}')
		conn.close()
		return
	except ValueError:
		print(f'Invalid username length received. Closing connection to {addr}')
		conn.close()
		return

	# Register socket with sel 
	events = selectors.EVENT_READ
	data = {"addr": addr, "username": username, "socket": conn}
	sel.register(conn, events, data=data)
	clients.append(data)


def service_connection(key):
	"""Function to service an existing connection"""

	global clients
	sock = key.fileobj
	data = key.data
	# Receive message from socket
	msg_header = recv_msg(sock, HEADER_LENGTH)
	if not msg_header:
		print(f'Closing connection to {data["addr"]}')
		sel.unregister(sock)
		sock.close()
		clients = [client for client in clients if client["addr"]!=data["addr"]]
		return
	try:
		msg_length = int(msg_header.decode("utf-8").strip())
		msg = recv_msg(sock, msg_length).decode("utf-8")
		print(f'Message received: {msg}')
	except AttributeError:
		print(f'Error receiving message. Closing connection to {data["addr"]}')
		sel.unregister(sock)
		sock.close()
		clients = [client for client in clients if client["addr"]!=data["addr"]]
		return
	except UnicodeDecodeError:
		print(f'Error decoding message. Closing connection to {data["addr"]}')
		sel.unregister(sock)
		conn.close()
		return
	except ValueError:
		print(f'Invalid message length received. Closing connection to {data["addr"]}')
		sel.unregister(sock)
		conn.close()
		return

	# Create username header
	username_enc = data["username"].encode("utf-8")
	user_header = f'{len(username_enc):<{HEADER_LENGTH}}'.encode("utf-8")

	# Distribute message to all other connected clients
	for client in clients:
		if client["addr"] != data["addr"]:
			print(f'Sending message to {client["username"]}...')
			send_msg(client["socket"], user_header + username_enc + msg_header + msg.encode())
			print('Message sent!')


# Configure listening socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((HOST, PORT))
lsock.listen()
lsock.setblocking(False)

# Configure selector object
sel = selectors.DefaultSelector()
sel.register(lsock, selectors.EVENT_READ, data=None)

# Loop over blocking calls to select
while True:
	events = sel.select()
	for key, mask in events:
		if key.data is None:
			# Listening socket is ready. Accept new connection
			accept_connection(key.fileobj)
		elif mask & selectors.EVENT_READ:
			# Existing socket is ready. Service it
			service_connection(key)

