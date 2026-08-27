import json
import socket

from code_errors import HTML_403, IMAGE_403
from parser import (
	create_HTTP_message,
	parse_HTTP_message,
	recive_message,
	replace_forbidden_word,
)

RULES = None
with open("rules.json") as file:
	RULES = json.load(file)
USER: str = RULES["user"]
BLOCKED_DOMAINS: list[str] = RULES["blocked"]
FORBIDDEN_WORDS: list[dict[str, str]] = RULES["forbidden_words"]

if __name__ == "__main__":
	#IP_VM = '10.166.246.129' # IP de la máquina virtual
	IP_VM = "127.0.0.1" # si falla la MV
	address = (IP_VM, 8000)

	print("Creando socket - Servidor")
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(address)
	server_socket.listen(3)

	print("... Esperando clientes")

	while True:
		new_socket, addr = server_socket.accept()

		recv_message: bytes = recive_message(new_socket)
		if not recv_message.strip():
			new_socket.close()
			continue

		http_hl = parse_HTTP_message(recv_message)
		hostname = http_hl.head.get("Host")
		if not hostname:
			new_socket.close()
			continue

		# Aqui es donde se intenta prohibir el acceso
		start_line = http_hl.start_line.split(" ")
		path = start_line[1] if len(start_line) > 1 else ""

		if "/403.jpg" in path:
			new_socket.send(IMAGE_403)
			new_socket.close()
			continue

		blocked_domain = False
		for url in BLOCKED_DOMAINS:
			if url in path:
				blocked_domain = True
				break

		if blocked_domain:
			new_socket.send(HTML_403)
			new_socket.close()
			print(f"conexión con {addr} bloqueada ({hostname}) y cerrada")
			continue


		http_hl.head["X-ElQuePregunta"] = USER

		proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		proxy_socket.connect((hostname, 80))
		proxy_socket.send(create_HTTP_message(http_hl))

		response = recive_message(proxy_socket)
		proxy_socket.close()

		response = replace_forbidden_word(parse_HTTP_message(response),  FORBIDDEN_WORDS)
		new_socket.send(create_HTTP_message(response))
		new_socket.close()
		print(f"conexión con {addr} ha sido cerrada")
