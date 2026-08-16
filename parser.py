import socket

BODY = (
	"<!DOCTYPE html>\n"
	'<html lang="es">\n'
	"<head>\n"
	'    <meta charset="UTF-8">\n'
	"    <title>Server HL</title>\n"
	"</head>\n"
	"<body>\n"
	"    <h1>Has usado los servicios HL</h1>\n"
	"    <h3>Si puedes ver este mensaje, es que has logrado una respuesta de\n"
	"    nuestro server. Abre una botella de champagne.</h3>\n"
	"</body>\n"
	"</html>\n"
)

HTTP_RESPONSE = (
	"HTTP/1.1 200 OK\r\n"
	"Content-Type: text/html; charset=utf-8\r\n"
	f"Content-Length: {len(BODY.encode('utf-8'))}\r\n"
	"X-ElQuePregunta: HL\r\n"
	"Connection: close\r\n"
	"\r\n" + BODY
).encode("utf-8")


class Http_HL:
	"""Clase Http Hector-Lazaro.

	Para que el LSP te hintee mejor."""

	def __init__(
		self,
		head: dict[str, str] | None = None,
		start_line: str = "",
		body: str = "",
	):
		self.start_line = start_line
		empty_head: dict[str, str] = {}
		self.head = empty_head if not head else head
		self.body = body


def parse_HTTP_message(http_message: bytes) -> Http_HL:
	message = http_message.split(b"\r\n\r\n", 1)

	# TODO(Hector): puede ser que un mensaje HTTP llegue con BODY o no.
	# Si llega con BODY, hay que rescatar el HEADER `content-length` para saber
	# de cuantos bytes es el body, y pegarlo al Http_HL
	# `curl` no envia un content-length, pero un navegador puede.
	if len(message) < 2:
		head = message[0]
		body = b""
	else:
		head = message[0]
		body = message[1]

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

	# Convención de http
	while b"\r\n\r\n" not in message:
		data = socket.recv(buff_size)

		if not data:
			break

		message += data

	return message
