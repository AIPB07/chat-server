import socket
import selectors

HOST = '127.0.0.1'
PORT = 54321


def accept_connection(sock):
	"""Function to accept a new socket connection"""

	# Accept connection to new socket. Register socket to be waited on for
	# read AND write events
	conn, addr = sock.accept()
	print(f'Connected to by {addr}')
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
	events = selectors.EVENT_READ|selectors.EVENT_WRITE
	sel.register(conn, events, data)



def service_connection(key, events):
	"""Function to service an existing socket connection"""

	sock = key.fileobj
	data = key.data
	# Check for read events
	if events & selectors.EVENT_READ:
		data_recv = sock.recv(1024)
		if data_recv != None:
			data.outb += data_recv
		else:
			print(f'Closing connection to {data.addr}')
			sel.unregister(sock)
			sock.close()
	# Check for write events
	if events & selectors.EVENT_WRITE:
		if data.outb:
			data_sent = sock.sendall(data.outb)
			data.outb = data.outb[sent:]


if __name__ == '__main__':
	# Configure selector object, listening socket. Register socket to be waited on
	# for read events
	sel = selectors.DefaultSelector()
	lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	lsock.bind((HOST, PORT))
	lsock.listen()
	lsock.setblocking(False)
	sel.register(lsock, selectors.EVENT_READ, data=None)

	while True:
		events = sel.select()
		for key, mask, in events:
			if key.data is None:
				# Listening socket is ready, accept new connection
				accept_connection(key.fileobj)
			else:
				# Existing connection is ready, service it
				service_connection(key, mask)
