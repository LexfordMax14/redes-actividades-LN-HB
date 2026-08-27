import re
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

	head, _, body = message.partition(b"\r\n\r\n")
	content_length = _get_content_length(head)

	while content_length is not None and len(body) < content_length:

		data = socket.recv(buff_size)

		if not data:
			break

		body += data

	return head + b"\r\n\r\n" + body


def _get_content_length(head: bytes) -> int | None:
	for line in head.split(b"\r\n"):
		if line.lower().startswith(b"content-length:"):
			_, _, value = line.partition(b":")
			return int(value.strip())
	return None

def replace_forbidden_word(http_hl: Http_HL, reemplazos: list[dict[str, str]]) -> Http_HL:
	# TODO: solo se reemplaza el texto si se que tiene texto el HTTP
	texto = http_hl.body
	mapa: dict[str, str] = {}
	for d in reemplazos:
		mapa.update(d)

	if not mapa:
		http_hl.body = texto
		return http_hl

	claves_ordenadas = sorted(mapa.keys(), key=len, reverse=True)

	patron = r'\b(' + '|'.join(re.escape(clave) for clave in claves_ordenadas) + r')\b'
	regex = re.compile(patron, re.IGNORECASE)

	def _reemplazar(match: re.Match) -> str:
		palabra_encontrada = match.group(0)
		for clave in mapa:
			if clave.lower() == palabra_encontrada.lower():
				return mapa[clave]
		return palabra_encontrada  # fallback (no debería ocurrir)

	nuevo_body = regex.sub(_reemplazar, texto)
	http_hl.body = nuevo_body

	_actualizar_content_length(http_hl)

	return http_hl


def _actualizar_content_length(http_hl: Http_HL) -> None:
	nuevo_length = str(len(http_hl.body.encode("utf-8")))
	for key in http_hl.head:
		if key.lower() == "content-length":
			http_hl.head[key] = nuevo_length
	http_hl.head["Content-Length"] = nuevo_length
