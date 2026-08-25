import socket


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
		self.head = head if head is not None else {}
		self.body = body


def parse_HTTP_message(http_message: bytes) -> Http_HL:
	http_hl = Http_HL()

	if b"\r\n\r\n" in http_message:
		head, body = http_message.split(b"\r\n\r\n", 1)
	else:
		head, body = http_message, b""
	http_hl.body = body.decode()

	lineas = head.split(b"\r\n")
	http_hl.start_line = lineas[0].decode()

	headers = lineas[1:]
	for line in headers:
		llave, _, valor = line.partition(b":")
		llave = llave.decode().strip()
		valor = valor.decode().strip()
		http_hl.head[llave] = valor

	return http_hl


def create_HTTP_message(parse_http: Http_HL) -> bytes:
	# Si hay body, se asume que es correcto y tiene el Content-Length apropiado
	head = parse_http.start_line + "\r\n"
	body = parse_http.body

	for llave, valor in parse_http.head.items():
		head += f"{llave}: {valor}\r\n"

	message = head + "\r\n" + body
	return message.encode()


def recive_message(socket: socket.socket, buff_size: int = 4) -> bytes:
	message = b""
	while b"\r\n\r\n" not in message:
		data = socket.recv(buff_size)
		if not data:
			break
		message += data

	head, _, _= message.partition(b"\r\n\r\n")
	content_length = _get_content_length(head)

	if content_length is not None:
		body = socket.recv(content_length)
		return head + b"\r\n\r\n" + body
	# else
	return head + b"\r\n\r\n"


def _get_content_length(head: bytes) -> int | None:
	for line in head.split(b"\r\n"):
		if line.lower().startswith(b"content-length:"):
			_, _, value = line.partition(b":")
			return int(value.strip())
	return None
