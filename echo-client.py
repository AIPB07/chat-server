import socket

HOST = '127.0.0.1'
PORT = 54321
HEADER_SIZE = 10


def send_recv():	
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		# prompt user for message
		msg = input('Enter message: ')
		while True:
			# send message
			print('Sending message...')
			msg = f'{len(msg):<{HEADER_SIZE}}' + msg
			s.sendall(msg.encode())

			# receive message
			new_msg = True
			full_msg = ''
			while True:
				print('Receiving message...')
				recv_msg = s.recv(16)
				if new_msg:
					len_msg = int(msg[:HEADER_SIZE])
					new_msg = False
				
				full_msg += recv_msg.decode("utf-8")

				if len(full_msg)-HEADER_SIZE == len_msg:
					print('Full message received!')
					print(f'{full_msg[HEADER_SIZE:]}')
					send_recv()


if __name__ == '__main__':
	send_recv()