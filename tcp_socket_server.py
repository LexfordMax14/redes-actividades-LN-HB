import socket

from parser import recive_message

if __name__ == "__main__":

	buff_size = 4
	address = ('localhost', 5000)

	print('Creando socket - Servidor')

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(address)
	server_socket.listen(3)

	# nos quedamos esperando a que llegue una petición de conexión
	print('... Esperando clientes')

	while True:
		new_socket, new_socket_address = server_socket.accept()

		recv_message = recive_message(new_socket, buff_size)
		print(f' -> Se ha recibido el siguiente mensaje: {recv_message.decode()}')

		response_message = f"echo: {recv_message.decode()}"
		new_socket.send(response_message.encode())
		new_socket.send(b"\0")

		new_socket.close()
		print(f"conexión con {new_socket_address} ha sido cerrada")