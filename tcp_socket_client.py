import socket

from parser import parse_HTTP_message

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ('localhost', 5000)
client_socket.connect(address)


message = "hola mundo desde el cliente\r\n\r\nignorar"
client_socket.send(message.encode())


# recv_message = parse_HTTP_message(client_socket, 4)
# print(f' -> Respuesta del servidor: {recv_message}')

client_socket.close()
