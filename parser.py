import socket

# request real capturada desde el navegador, para testear
REQ = (
	b"GET / HTTP/1.1\r\n"
	b"Host: 10.166.246.129:8000\r\n"
	b"Connection: keep-alive\r\n"
	b"Upgrade-Insecure-Requests: 1\r\n"
	b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0\r\n"
	b"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\n"
	b"Accept-Encoding: gzip, deflate\r\n"
	b"Accept-Language: es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,es-CL;q=0.4\r\n"
	b"dnt: 1\r\n"
	b"sec-gpc: 1\r\n"
	b"Cache-Control: max-age=0\r\n"
	b"\r\n"   # linea vacia: fin de headers, sin body
)


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

	# Convención de http
	while b"\r\n\r\n" not in message:
		data = socket.recv(buff_size)

		if not data:
			break

		message += data

	return message