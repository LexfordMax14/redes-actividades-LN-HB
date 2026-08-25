with open("./403.jpg", "rb") as f:
	IMAGE_403_BODY = f.read()

# --- La solicitud de imagen
IMAGE_403 = (
	b"HTTP/1.1 200 OK\r\n"
	b"Content-Type: image/jpeg\r\n"
	b"Connection: close\r\n"
	b"Content-Length: " + str(len(IMAGE_403_BODY)).encode() + b"\r\n"
	b"\r\n"
) + IMAGE_403_BODY

HTML_403_BODY = b"""<!DOCTYPE html>
<html>
<head><title>403 Forbidden</title></head>
<body>
	<h1>403 Forbidden</h1>
	<p>No tienes permiso para acceder a este recurso.</p>
	<img src="/403.jpg">
</body>
</html>"""

# --- El error que se envia
HTML_403 = (
	b"HTTP/1.1 403 Forbidden\r\n"
	b"Content-Type: text/html; charset=utf-8\r\n"
	b"Connection: close\r\n"
	b"Content-Length: " + str(len(HTML_403_BODY)).encode() + b"\r\n"
	b"\r\n"
) + HTML_403_BODY
