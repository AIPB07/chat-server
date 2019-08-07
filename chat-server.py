import socket
import selectors

HEADER_LENGTH = 10
HOST = '127.0.0.1'
PORT = 54321
clients = []  # List for storing client information


def accept_connection(sock):
	"""Function to accept a new connection"""

	global clients
	conn, addr = sock.accept()
	print(f'Connected to by {addr}')
	conn.setblocking(False)

	# Receive first message. This will contain username
	user_header = conn.recv(HEADER_LENGTH)
	username_length = int(user_header.decode("utf-8").strip())
	username = conn.recv(username_length).decode("utf-8")

	# Register socket with sel 
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	data = {"addr": addr, "username": username, "socket": conn}
	sel.register(conn, events, data=data)
	clients.append(data)


def service_connection(key, mask):
	"""Function to service an existing connection"""

	global clients
	sock = key.fileobj
	data = key.data
	# Check for read events
	if mask & selectors.EVENT_READ:
		# Receive message from socket
		msg_header = sock.recv(HEADER_LENGTH)
		if not msg_header:
			print(f'Closing connection to {data["addr"]}')
			sel.unregister(sock)
			sock.close()
			clients = [client for client in clients if client["addr"]!=data["addr"]]
			return None
		msg_length = int(msg_header.decode("utf-8").strip())
		msg = sock.recv(msg_length).decode("utf-8")
		print(f'Message received: {msg}')

		# Create username header
		username_enc = data["username"].encode("utf-8")
		user_header = f'{len(username_enc):<{HEADER_LENGTH}}'.encode("utf-8")

		# Distribute message to all other connected clients
		for client in clients:
			if client["addr"] == data["addr"]:
				continue
			print(f'Sending message to {client["username"]}...')
			client["socket"].send(user_header + username_enc + msg_header + msg.encode())
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
		else:
			# Existing socket is ready. Service it
			service_connection(key, mask)

