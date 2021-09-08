import socket
import datetime
import sys
import os

HOSTNAME = "127.0.0.1"
PORT = 8000
PROTOCOL = 0
TIMEOUT = 15
MAX_SIZE = 1024
QUEUE_SIZE = 5
PERSISTENT ="keep-alive"
NON_PERSISTENT = "close"


def setup_server(hostname, port):

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, PROTOCOL) # TCP connection
	except socket.error:
		print("socket setup has failed.")
		sys.exit(1)

	sock.settimeout(TIMEOUT)
	sock.bind((hostname, port))

	try:
		sock.listen(QUEUE_SIZE)
	except socket.error:
		print("setting up socket queue failed.")
		sys.exit(1)

	return sock



def create_conn(sock):

	try:
		conn, acc = sock.accept()
	except socket.timeout:
		print("no connections established after {} seconds. terminating connection.".format(TIMEOUT))
		sys.exit(1)

	if (conn.fileno() < 0):
		print("no connections established. terminating server.")
		sys.exit(1)

	test = receive_data(conn)

	if test != 'con'.encode():
		print("acknowledge from client failed. shutting down server.")
		sys.exit(1)

	send_data(conn, 'con'.encode())
	

	return conn


def send_data(sock, data):

	try:
		sock.sendall(data)
	except socket.error:
		print("error sending data.")
		sys.exit(1)



def receive_data(sock):

	try:
		data = sock.recv(MAX_SIZE)
	except socket.error:
		print("error receiving data.")
		sys.exit(1)
	return data



def send_file(sock, data):

	file = open(data[1][1:], 'rb')  #open file 
	
	while True:

		line = file.read(MAX_SIZE)
		if not line: #if line is empty: send 'fin' to indicate end of file and break
			print('[server]: reached end of file.')
			send_data(sock, 'fin'.encode())
			break

		send_data(sock, line)
		ack = receive_data(sock) #receive ack from client.
		if not ack == 'ack'.encode():
			print('[server]: ack not received, end file sending.')
			break

	file.close()


	#main function
if __name__ == "__main__":

	sock = setup_server(HOSTNAME, PORT)
	conn = create_conn(sock)

	while True:
		print('receiving request from client now.\n')
		data = receive_data(conn)

		if data:
			print('request obtained - {}'.format(data.decode()))
			data = data.split()
			filename = data[1][1:]
			conn_type = data[6]

			if conn_type == NON_PERSISTENT.encode():

				send_file(conn, data)
				print("{} sent. closing file and shutting down connection.".format(filename.decode()))
				conn.close()
				print("socket has been closed.\n")
				conn = None
				conn = create_conn(sock)

			elif (conn_type == PERSISTENT.encode()):
				send_file(conn, data)

		else:
			print('no more requests from client.')
			break

	if conn.fileno() >0:
		print("all files requested, now closing socket.")
		sock.close()
		print("socket has been closed. \n")
		sock = None
