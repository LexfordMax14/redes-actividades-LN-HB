import socket


def parse_HTTP_message(socket: socket.socket, buff_size: int) -> str:

	data = socket.recv(buff_size)

	message = ""
	while True:
		if not data: break
		message += data.decode()
		if message.endswith("\r\n\r\n"): break

	return message
