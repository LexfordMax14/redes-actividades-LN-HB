import socket


def recive_message(socket: socket.socket, buff_size: int) -> bytes:
	message = b""

	while True:
		data = socket.recv(buff_size)

		if data == b"": break
		if b"\0" in data:
			message += data
			break

		message += data

	return message
