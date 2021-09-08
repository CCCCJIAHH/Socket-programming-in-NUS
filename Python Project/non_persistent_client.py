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
FILE_A = "GET /a.jpg HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: close\r\n\n"
FILE_B = "GET /b.mp3 HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: close\r\n\n"
FILE_C = "GET /c.txt HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: close\r\n\n"
files = [FILE_A, FILE_B, FILE_C]


def make_socket():

	try:
		sock = socket.socket()
		sock.settimeout(TIMEOUT)
	except socket.error:
		print('socket creation has failed.')
		sys.exit(1)
		
	return sock



def connect(hostname, port):

	t1 = datetime.datetime.now()

	try:
		sock.connect((hostname,port))
	except socket.error:
		print("connection has been refused..")
		sys.exit(1)

	send_data(sock, 'con'.encode())
	data = receive_data(sock)

	if data != 'con'.encode():
		print('connection to server not acknowledged. .')
		sys.exit(1)

	t2 = datetime.datetime.now()
	return (t2-t1)



def send_data(sock, msg):

	try:
		sock.sendall(msg)
	except socket.error:
		print("send message failed.\n")
		sys.exit(1)



def receive_data(sock):

	try:
		data = sock.recv(MAX_SIZE)
	except socket.error:
		print("error in receiving data.")
		sys.exit(1)

	return data



def retrieve_file(sock, raw_filename, extension):
	#Create a file to write to.
	filename='retrieve_non_persistent_' + raw_filename + extension
	file = open(filename, 'wb+')
	
	datum = True
	count = 0

	while datum:

		datum = receive_data(sock) #receive data from the socket
		if datum == 'fin'.encode() or not datum:
			break   #if data == 'fin' or data is an empty string, break
 
		file.write(datum)
		count += 1
		send_data(sock, 'ack'.encode())  #send an acknowledge to the server

	file.close()
	return count


	#main function
if __name__ == "__main__":

	total_time = 0
	number_of_packets = 0
	
	for file in files:

		filename = file.split()[1][1:]
		raw_filename, file_ext = os.path.splitext(filename)

		sock = make_socket()
		t0 = connect(HOSTNAME, PORT)

		t1 = datetime.datetime.now()
		# print('current time is {}.'.format(t1)) # Find the time prior to making the socket.

		send_data(sock, file.encode())
		pkt_recn = retrieve_file(sock, raw_filename, file_ext)

		sock.close() # Close socket. End connection.
		sock = None

		t2 = datetime.datetime.now()
		# print('current time is {}.'.format(t2)) # Find the time after making the socket.

		time_div = (t2-t1+t0).total_seconds()
		print('retrieval time is {} seconds.'.format(time_div)) # Calculated time difference.
		total_time += time_div

		print('number of packets received = {}\n'.format(pkt_recn)) # Find the number of packets received.
		number_of_packets += pkt_recn
	
	print('total transaction time = {:.6f} seconds.'.format(total_time))
	print('number_of_packets = {}'.format(number_of_packets))
