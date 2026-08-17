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
		start_line: str = "",
		head: dict[str, str] | None = None,
		body: str | None = None,
	):
		self.start_line = start_line
		empty_head: dict[str, str] = {}
		self.head = empty_head if head == None else head
		self.body = body


def parse_HTTP_message(socket: socket.socket, buff_size: int = 4) -> Http_HL:
	http_hl = Http_HL()
	message = b""
	# Convención de http
	while b"\r\n\r\n" not in message:
		data = socket.recv(buff_size)
		if not data:
			break
		message += data
	message = message.split(b"\r\n\r\n", 1)
	# Como el buff_size es 4, siempre va a ser una lista de tamaño 1

	head = message[0]
	lineas = head.split(b"\r\n")
	http_hl.start_line = lineas[0].decode()

	headers = lineas[1:]
	for line in headers:
		# Cuidado con el separador ": ", yo usaria ":" y luego strip()
		llave, valor = line.split(b": ", 1)
		http_hl.head[llave.decode()] = valor.decode()

	if "Content-Length" in http_hl.head:
		data = socket.recv(int(http_hl.head["Content-Length"]))
		http_hl.body = data.decode()

	return http_hl


def create_HTTP_message(parse_http: Http_HL) -> bytes:
	head = parse_http.start_line + "\r\n"
	body = "" if parse_http.body == None else parse_http.body

	for llave, valor in parse_http.head.items():
		head += f"{llave}: {valor}\r\n"

	return (head + "\r\n" + body).encode()
