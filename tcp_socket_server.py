import socket

from parser import recive_message

if __name__ == "__main__":

	IP_VM = '10.0.2.15' # IP de la máquina virtual
	# IP_VM = '127.0.0.1' # si falla la MV

	buff_size = 4 # tamaño del buffer para recibir el mensaje
	address = (IP_VM, 5000) # dirección del servidor al que nos queremos conectar

	print('Creando socket - Servidor')

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creación del socket TCP del servidor
	server_socket.bind(address)	#asociación del socket a la dirección y puerto especificados
	server_socket.listen(3) #máximo de conexiones en cola que puede tener el servidor

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