import socket

from parser import parse_HTTP_message

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

		recv_message = parse_HTTP_message(new_socket, buff_size)

		print(f' -> Se ha recibido el siguiente mensaje: {recv_message}')
		response_message = f"Se ha sido recibido con éxito el mensaje:{recv_message}\r\n\r\nignorar"
		new_socket.send(response_message.encode())

		new_socket.close()
		print(f"conexión con {new_socket_address} ha sido cerrada")