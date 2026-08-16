import socket

from parser import (
	HTTP_RESPONSE,
	create_HTTP_message,
	parse_HTTP_message,
	recive_message,
)

if __name__ == "__main__":
	# IP_VM = '10.0.2.15' # IP de la máquina virtual
	IP_VM = "127.0.0.1" # si falla la MV
	buff_size = 4
	address = (IP_VM, 5000)

	print("Creando socket - Servidor")
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(address)
	server_socket.listen(3)

	print("... Esperando clientes")

	while True:
		new_socket, new_socket_address = server_socket.accept()

		recv_message = recive_message(new_socket, buff_size)
		http_hl = parse_HTTP_message(recv_message)
		print(
			" -> Se ha recibido el siguiente mensaje:\n"
			f"{create_HTTP_message(http_hl).decode()}\n"
			"---"
		)

		new_socket.send(HTTP_RESPONSE)

		new_socket.close()
		print(f"conexión con {new_socket_address} ha sido cerrada")
