import socket

def parse_HTTP_message(socket: socket.socket, buff_sizeL: int, end_sequence: str):

	# recibimos la primera parte del mensaje
	data = socket.recv(pkg_size)
	recv_message = connection_socket.recv(buff_size)
	full_message = recv_message

	# verificamos si llegó el mensaje completo o si aún faltan partes del mensaje

	# entramos a un while para recibir el resto y seguimos esperando información
	# mientras el buffer no contenga secuencia de fin de mensaje
	while not is_end_of_message:
		# recibimos un nuevo trozo del mensaje
		recv_message = connection_socket.recv(buff_size)

		# lo añadimos al mensaje "completo"
		full_message += recv_message

		# verificamos si es la última parte del mensaje
		is_end_of_message = contains_end_of_message(full_message.decode(), end_sequence)

	# removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
	full_message = remove_end_of_message(full_message.decode(), end_sequence)

	# finalmente retornamos el mensaje
	return full_message


def recieve_file(socket: socket.socket):
	# Se puede hacer lo mismo con un mensaje, con la diferencia de no estar
	# escribiendo lo recibido a un archivo

	pkg_size = 4 # bytes

	data = socket.recvfrom(pkg_size)[0]

	file = open("output.txt", "wb")
	while True:
		# Un paquete vacio es el fin de la comunicación
		if data == b"" : break
		else:
			file.write(data)
			data = socket.recvfrom(pkg_size)[0]
			print(f"[TRANSFER] Recieving pkg... ({len(data)})")
	file.close()

	print("[STATUS] file recieve")
	socket.close()

print('Creando socket - Cliente')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ('localhost', 5000)
client_socket.connect(address)

message = "hola mundo"
end_of_message = b""

client_socket.send(message.encode())


buffer_size = 1024
recv_message = client_socket.recv(buffer_size)

decoded_message = recv_message.decode()
print(f' -> Respuesta del servidor: {decoded_message}')


client_socket.close()
