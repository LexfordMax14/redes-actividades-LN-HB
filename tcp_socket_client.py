import socket

from parser import recive_message

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = ('localhost', 5000)
client_socket.connect(address)


message = "hola mundo desde el cliente"
client_socket.send(message.encode())
client_socket.send(b"\0")

recv_message = recive_message(client_socket, 4)
print(f' -> response: {recv_message.decode()}')

client_socket.close()
