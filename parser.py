import socket

def parse_HTTP_message(http_message: bytes): 

	# separo head de body 
	head, body = http_message.split(b"\r\n\r\n", 1) # puede haber un doble salto en el body se asume eso

	dict_http = {}
	dict_head = {}

	dict_http["body"] = body.decode() # el body se guarda en string
	dict_http["head"] = dict_head # para mejor acceso a los headers

	lineas = head.split(b"\r\n") #separar lineas del head

	dict_head["start_line"] = lineas[0].decode() #la primera linea es la start line

	headers = lineas[1:] # el resto son headers

	for line in headers:
		llave,valor = line.split(b": ",1) #par llave valor
		dict_head[llave.decode()] = valor.decode()

	return dict_http

def create_HTTP_message(parse_http: dict):

	#reconstruir la head
	head = parse_http["head"]["start_line"] + "\r\n" # start line

	for llave, valor in parse_http["head"].items():
		if llave == "content-length" or llave == "content-type" : # tomo lo importante (la start line esta arriba esto es para los headers)
			head += f"{llave}: {valor}\r\n"

	#reconstruir el body
	body = parse_http["body"]

	#reconstruir el mensaje completo
	message  = head + "\r\n" + body # unir head y body

	return message.encode() #retornar en bytes


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
