import socket


class Http_HL:
	"""Clase Http Hector-Lazaro.

	Para que el LSP te hintee mejor."""

	def __init__(
		self,
		head: dict[str, str] = {},
		start_line: str = "",
		body: str = "",
	):
		self.start_line = start_line
		self.head = head
		self.body = body


def parse_HTTP_message(http_message: bytes) -> Http_HL:
	head, body = http_message.split(b"\r\n\r\n", 1)

	http_hl = Http_HL()
	http_hl.body = body.decode()

	lineas = head.split(b"\r\n")
	http_hl.start_line = lineas[0].decode()

	headers = lineas[1:]
	for line in headers:
		# Cuidado con el separador ": ", yo usaria ":" y luego strip()
		llave, valor = line.split(b": ", 1)
		http_hl.head[llave.decode()] = valor.decode()

	return http_hl


def create_HTTP_message(parse_http: Http_HL) -> bytes:
	head = parse_http.start_line + "\r\n"
	body = parse_http.body

	for llave, valor in parse_http.head.items():
		head += f"{llave}: {valor}\r\n"

	message = head + "\r\n" + body
	return message.encode()


def recive_message(socket: socket.socket, buff_size: int) -> bytes:
	message = b""

	while True:
		data = socket.recv(buff_size)

		if data == b"":
			break
		# Nuestra convención para el final de un mensaje.
		if b"\0" in data:
			message += data
			break

		message += data

	return message
