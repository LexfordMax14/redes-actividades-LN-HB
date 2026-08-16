import socket

from parser import recive_message

#Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_VM = '10.0.2.15' # IP de la máquina virtual
# IP_VM = 'localhost' # si falla la MV

#Dirección del servidor al que nos queremos conectar
address = (IP_VM, 5000)
#Conexión
client_socket.connect(address)

#Enviar mensaje
message = "hola mundo desde el cliente"
client_socket.send(message.encode())
client_socket.send(b"\0") #esto para que? si ya se envia en bits? con el encode()

print ("mensaje enviado")

#Recibir respuesta
recv_message = recive_message(client_socket, 4)
print(f' -> response: {recv_message.decode()}')

#cerrar socket
client_socket.close()
