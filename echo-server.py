import socket

HOST = '127.0.0.1'
PORT = 54321
HEADER_SIZE = 10


def recv_send():
	while True:
		conn, addr = s.accept()
		with conn:
			print(f'Connected by {addr}')
			new_msg = True
			full_msg = ''
			# loop over blocking calls to recv()
			while True:
				msg = conn.recv(16)
				if new_msg:
					len_msg = int(msg[:HEADER_SIZE])
					new_msg = False

				full_msg += msg.decode("utf-8")
				
				if len(full_msg)-HEADER_SIZE == len_msg:
					print('Full message received!')
					conn.sendall(full_msg.encode("utf-8"))
					recv_send()


if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	recv_send()








