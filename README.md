# Actividad: construir un proxy — CC4303 Redes

**Integrantes:** Hector Bonilla V, Lázaro Narváez U

**Repositorio:** https://github.com/LexfordMax14/redes-actividades-LN-HB

---

## 1. Declaración de uso de IA

| Modelo | Integrante | Dónde se usó |
| --- | --- | --- |
| Gemini | Lázaro | Consultas puntuales de Python: `.items()`, `str.replace()`, sintaxis de diccionarios. Solo aprendizaje del lenguaje, no diseño. |
| Claude (Opus 5) | Lázaro | Código: diagnóstico de bugs en `recive_message`, cambio del body de `strings` a `bytes`. Pruebas: ejecución del proxy contra el servidor del curso. Redacción: estructura de este informe. |
| Claude (Sonnet) | Héctor | Consulta sobre el significado de `b""` en sockets, a raíz de un error durante el desarrollo. Revisión de código. |

---

## 2. Cómo ejecutar

```bash
python tcp_socket_server.py
```

- Requiere estar parado en la carpeta del repo (`rules.json` y `403.jpg` se leen con ruta relativa).
- El proxy escucha en el puerto 8000. La IP se cambia en la variable `IP_VM` de `tcp_socket_server.py`.
- Reglas configurables en `rules.json`: usuario, dominios bloqueados y palabras prohibidas.

Prueba rápida:

```bash
curl http://cc4303.bachmann.cl/ -x IP_VM:8000
```

**Entorno:** probado en máquina virtual (IP_VM) y en localhost (127.0.0.1).

---

## 3. Diagrama del proxy

![diagrama](diagrama.jpg)

**Sockets necesarios: 3.**

| Socket | Rol |
| --- | --- |
| `server_socket` | Portero. Solo hace `accept()`, no transfiere datos. |
| `new_socket` | Proxy actuando como **servidor** frente al cliente. Uno por conexión. |
| `proxy_socket` | Proxy actuando como **cliente** frente al servidor real. |

Idea central: un proxy es servidor y cliente a la vez. Recibe con `accept()` y pide con `connect()`.

---

## 4. Diseño

### 4.0 Arquitectura

**Separación en dos archivos.** Aplicamos separación de responsabilidades, criterio traído del ramo de Ingeniería de Software: `parser.py` concentra el manejo del protocolo HTTP (leer del socket, interpretar y armar mensajes), y `tcp_socket_server.py` la lógica del proxy (a quién conectarse, qué bloquear, qué censurar). El servidor no sabe cómo se parsea un header; el parser no sabe qué es un dominio bloqueado.

**Clase `Http_HL` en vez de diccionario o tupla.** Se eligió una clase para que el editor respetara las firmas y autocompletara los campos. Además entrega una estructura fija con la que trabajar: `start_line`, `head` y `body` siempre existen y siempre tienen el mismo tipo, lo que evita chequeos defensivos en el resto del código.

### 4.1 `parse_HTTP_message` — qué extrae

Separa el mensaje en tres partes, en `\r\n\r\n`:

| Campo | Tipo | Contenido |
| --- | --- | --- |
| `start_line` | `str` | `GET http://host/ruta HTTP/1.1` — método, path y versión |
| `head` | `dict[str, str]` | un par por header |
| `body` | `bytes` | contenido crudo |

Decisiones:

- **Headers como `str`, body como `bytes`.** Los headers son ASCII por especificación; el body puede ser binario (JPEG, gzip). Decodificarlo asumiendo UTF-8 rompe con imágenes.
- **`partition(b":")`** en vez de `split`: corta en el primer `:` nomás. Un header como `Date: Thu, 27 Aug 2026 17:07:08 GMT` tiene más de uno.

`create_HTTP_message` es la inversa exacta: rearma `start_line + headers + \r\n + body` y devuelve `bytes`.

### 4.2 Bloqueo de dominios

- Se compara la lista `blocked` del JSON contra el path de la start line.
- Al usar el proxy, el cliente manda la **URL completa** en la start line (`GET http://host/ruta`), no solo la ruta. Por eso una entrada como `cc4303.bachmann.cl/secret` calza.
- **Por qué contra el path y no contra el header `Host`.** La primera versión comparaba `Host` contra la lista, pero el `Host` trae solo el dominio (`cc4303.bachmann.cl`), nunca la ruta. Con esa lógica una entrada como `cc4303.bachmann.cl/secret` no podía calzar jamás, y la única forma de bloquear `/secret` era bloquear el dominio entero — lo que también dejaba fuera `/` y `/replace`. Comparar contra el path resuelve las dos cosas.
- **La comparación es por substring, no por igualdad** (`if url in path`). Esto es deliberado: si una página está bloqueada, las rutas colgadas de ella (`/secret/algo`) también deben estarlo. Como efecto lateral se bloquean rutas que solo comparten prefijo sin ser subrutas (`/secretos-publicos`); se aceptó porque en un control parental bloquear de más es preferible a bloquear de menos.
- Bloqueado → se responde `403 Forbidden` con un HTML que incluye `<img src="/403.jpg">`.
- **`/403.jpg` se intercepta ANTES del chequeo de bloqueo.** Es un recurso local, no del servidor remoto; si se chequeara después, el proxy iría a buscarlo afuera y devolvería 404.
- **La imagen se sirve con `200 OK`, no con `403`.** El recurso prohibido es la página, no la imagen. El 403 corresponde a la respuesta del HTML bloqueado; la petición posterior de `/403.jpg` es legítima y el proxy la satisface localmente.

**¿Cuántos ciclos HTTP para mostrar una imagen en un navegador?**

Dos: uno para el HTML y otro para la imagen. El navegador no puede saber que hay una imagen hasta recibir y parsear el HTML, así que las peticiones son necesariamente secuenciales y no se pueden juntar en una sola.

### 4.3 Reemplazo de palabras

- Se recorre `forbidden_words` (una **lista de diccionarios** de un par cada uno) y se aplica `bytes.replace()` por cada par.
- Los reemplazos son acumulativos: cada vuelta trabaja sobre el resultado de la anterior.
- **Sin regex**: el enunciado solo permite `socket`, `json` y `sys`. `str.replace()` basta porque las claves del JSON no se solapan entre sí y coinciden en mayúsculas con el contenido de las páginas del curso. Un enfoque case-insensitive habría requerido `re`.
- Tras reemplazar se **recalcula `Content-Length`**: el body cambia de tamaño (`proxy` = 5 bytes, `[REDACTED]` = 10). Con el body en `bytes` es `len(body)` directo — importa que sea el largo en bytes y no en caracteres, porque las páginas tienen tildes.

### 4.4 Modificación de headers

Se agrega `X-ElQuePregunta` con el nombre (tomado de `rules.json`) a la request que va del proxy al servidor.

### 4.5 Mensajes más grandes que el buffer

`recive_message` lee en dos fases:

**¿Cómo sé que el HEAD llegó completo?**
Por el delimitador `\r\n\r\n`. Se acumula en un buffer hasta encontrarlo.

**¿Qué pasa si los headers no caben en mi buffer?**
Nada: no se lee "un buffer", se acumula en un `while` hasta ver el delimitador. Funciona incluso con `buff_size=1`.

**¿Y el BODY?**
Por `Content-Length`. Se lee hasta que `len(body)` alcance ese valor.

**¿Cómo sé si llegó el mensaje completo?**
Dos criterios combinados: delimitador para el head, `Content-Length` para el body.

Detalle clave: un mismo `recv` puede traer el final del head **y** el inicio del body. Ese sobrante se conserva y se cuenta en `len(body)`; descartarlo hace que el proxy pida bytes de más y se cuelgue.

**Por qué `buff_size = 4` por defecto** (y no el 50 que sugiere el enunciado): para forzar el peor caso en cada ejecución. Con buffers grandes los errores de lectura no se manifiestan. Durante el desarrollo nos encontramos justamente con el caso descrito arriba —un `recv` que traía head más un pedazo de body, y ese sobrante se perdía—, y con 50 ese efecto podría no haber aparecido nunca.

---

## 5. Pruebas

### 5.1 Con curl

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Bloqueo | `curl http://cc4303.bachmann.cl/secret -x IP_VM:8000` | `403` |
| Imagen | `curl http://cc4303.bachmann.cl/403.jpg -x IP_VM:8000` | `200`, `image/jpeg`, 20134 bytes |
| Header | `curl http://cc4303.bachmann.cl/ -x IP_VM:8000` | `<h1>Bienvenide HL!</h1>` (valor tomado de `rules.json`) |
| Reemplazo | `curl http://cc4303.bachmann.cl/replace -x IP_VM:8000` | 9 `[REDACTED]`, 5 `[FORBIDDEN]`, 3 `[???]`; ninguna palabra sin censurar |
| Content-Length | `curl -i .../replace -x IP_VM:8000` | header 1225 = body 1225 bytes |

### 5.2 Tamaño de buffer

Head del servidor: 192 bytes. Start line: 17 bytes. Mensaje total: 1351 bytes.

| `buff_size` | Caso | Resultado |
| --- | --- | --- |
| 200 | menor que el mensaje, mayor que los headers | OK |
| 50 | menor que los headers, mayor que la start line | OK |
| 4 | menor que la start line | OK |
| 1 | mínimo posible | OK |

En los 4 casos el body llega completo y coincide con `Content-Length`.

### 5.3 Con el navegador

- `http://cc4303.bachmann.cl/secret` — ya no se ve el contenido del sitio: el proxy responde 403 y el navegador muestra la imagen alojada localmente. Se observan dos ciclos HTTP en el log: uno por el HTML, otro por la imagen.

![/secret](secret.png)

- `http://cc4303.bachmann.cl/` — el título muestra `Bienvenide HL!`, valor que el servidor toma del header `X-ElQuePregunta` agregado por el proxy. El enlace también aparece censurado.

![/root](root.png)

- `http://cc4303.bachmann.cl/replace` — el texto es el mismo que sin proxy, solo con las palabras prohibidas reemplazadas. No hay cortes ni caracteres rotos: las tildes se conservan porque el `Content-Length` se recalcula en bytes. El `<title>` de la pestaña también queda censurado.

![/replace](replace.png)
