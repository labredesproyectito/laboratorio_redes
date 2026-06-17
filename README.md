# README - Laboratorio de Redes de Computadoras

## Descripción

Tarea obligatoria de redes.
Para enviar mensajes a hosts especificos se utiliza TCP y para enviar mensajes por broadcast se utiliza UDP.
Para enviar archivos se utiliza el protocolo TCP.
Para enviar archivos por broadcast primero se envia un mensaje a todos los hots de la red y luego estos le responden al emisor para que este ultimo les envie el archivo.

Hay 2 hilos, uno para el socket UDP y otro para el socket TCP.
El socket tcp siempre esta listo para aceptar nuevas conexiones

## Requisitos

- Python 3.8 o superior
- Conexión de red local
- Servidor de autenticación accesible

## Ejecución

```bash
python mensajeria.py <puerto_local> <ip_auth> <puerto_auth>
```

Ejemplo:

```bash
python mensajeria.py 25555 ti.esi.edu.uy 33
```

## Autenticación

Al iniciar el programa, solicita:

```text
Usuario
Clave
```

La clave se convierte a MD5 y se envía al servidor de autenticación. Si las credenciales son correctas, el servidor devuelve un mensaje de bienvenida.

Ejemplo:

```text
./mensajeria 25555 ti.esi.edu.uy 33
Usuario: aturing
Clave: aturing
Bienvenido Alan_Mathison_Turing
```

## Uso del cliente

### Enviar mensaje

```text
<IP|hostname> <mensaje>
```

Ejemplos:

```text
192.168.1.10 Hola
pc01 Buenas tardes
```

### Enviar broadcast

```text
* <mensaje>
```

Ejemplo:

```text
* Hola a todos
```

### Enviar archivo

```text
<IP|hostname> &file <ruta_archivo>
```

Ejemplo:

```text
192.168.1.10 &file foto.jpg
```

### Broadcast de archivo

```text
* &file foto.jpg
```

## Estado de implementación

- [x] Enviar mensaje (TCP)
- [x] Enviar broadcast (UDP)
- [x] Enviar archivo (TCP)
- [x] Broadcast de archivo (señalización por UDP y transferencia por TCP)
- [x] Autenticación con servidor (envío de MD5)
- [x] Recepción y guardado de archivos en directorio actual
- [x] Reintentos / confirmación de entrega
- [ ] Interfaz gráfica de usuario (GUI) (no lo pide la letra del oblitatorio)

## Formato de mensajes

El protocolo actual utiliza formatos simples:

- UDP broadcast texto: `BROADCAST|MENSAJE|usuario|mensaje`
- UDP broadcast archivo: `BROADCAST|ARCHIVO|usuario|ruta_archivo`
- TCP directo texto: `MENSAJE|usuario|mensaje`
- TCP directo archivo: `ARCHIVO|usuario|nombre_archivo|tamanio`
- Confirmación TCP: `ACK|OK` / `ACK|ERROR`

## Recepción de archivos

Los archivos recibidos se guardan en el directorio actual.

## Tecnologías usadas

- Python
- socket
- threading
- hashlib

## Estructura del programa

El archivo principal `mensajeria.py` contiene las siguientes partes principales:

- `recibir_linea_crlf(buffer, sock)`: lee datos de un socket TCP hasta encontrar el delimitador `\r\n`, devuelve la línea completa y los bytes restantes.
- `autenticador()`: solicita usuario y clave, calcula el hash MD5 de la contraseña, se conecta al servidor de autenticación y valida las credenciales.
- `conectar_tcp(ip, puerto)`: resuelve el hostname a dirección IP y abre una conexión TCP hacia el destino.
- `enviar_mensaje_udp_broadcast(sock, nombre_usuario, mensaje)`: envía un mensaje UDP broadcast usando el formato `BROADCAST|MENSAJE|...`.
- `recibir_mensaje_udp_broadcast(ip_origen, nombre_usuario, mensaje)`: muestra en pantalla un mensaje recibido por UDP broadcast.
- `enviar_archivo_udp_broadcast(sock, nombre_usuario, ruta_archivo)`: envía una señal UDP broadcast notificando que un archivo está disponible para ser solicitado.
- `enviar_mensaje_tcp(sock, nombre_usuario, mensaje)`: envía un mensaje directo por TCP utilizando el formato `MENSAJE|...`.
- `enviar_archivo_tcp(sock, nombre_usuario, path)`: envía la cabecera del archivo y posteriormente los bytes del archivo por TCP en bloques de 4096 bytes.
- `enviar_ack_tcp(sock, exito=True)`: envía una confirmación de recepción (`ACK|OK` o `ACK|ERROR`) a través de TCP.
- `recibir_ack_tcp(sock)`: espera una confirmación TCP durante un tiempo limitado y devuelve si fue recibida correctamente.
- `enviar_mensaje_tcp_con_reintentos(ip, puerto, nombre_usuario, mensaje)`: intenta enviar un mensaje TCP varias veces hasta recibir confirmación de entrega o agotar los reintentos.
- `enviar_archivo_tcp_con_reintentos(ip, puerto, nombre_usuario, path)`: intenta enviar un archivo TCP varias veces hasta recibir confirmación de entrega o agotar los reintentos.
- `recibir_mensaje_tcp(sock, nombre_usuario, mensaje)`: muestra en pantalla un mensaje recibido por TCP y envía una confirmación de recepción.
- `recibir_archivo_tcp(sock, usuario, nombre_archivo, tamanio_archivo, resto)`: recibe un archivo por TCP, lo guarda en disco, verifica que se haya recibido completo y envía una confirmación.
- `parsear(texto)`: interpreta la entrada del usuario y distingue destino, mensajes, comando `&file` y ruta de archivo.
- `escucha_udp_broadcast(host, port, nombre_usuario)`: mantiene un hilo escuchando paquetes UDP en el puerto local.
- `escucha_tcp(host, port, nombre_usuario)`: mantiene un hilo escuchando conexiones TCP entrantes y delega cada conexión a `manejar_tcp`.
- `manejar_udp(sock, nombre_usuario_local)`: procesa paquetes UDP recibidos y decide si corresponden a mensajes broadcast o solicitudes de transferencia de archivo.
- `manejar_tcp(sock)`: procesa la primera línea TCP recibida, identifica el tipo de operación (`MENSAJE`, `ARCHIVO`, `PEDIR_ARCHIVO`) y llama a la función apropiada.
- `manejar_cliente(nombre_usuario)`: lee la entrada del usuario desde teclado y envía mensajes o archivos según la sintaxis utilizada.
- `iniciar_servidor(host, tcp_port, udp_port, nombre_usuario)`: inicia los hilos de escucha TCP y UDP para atender conexiones y mensajes entrantes simultáneamente.
- `main()`: realiza la autenticación, inicia los servicios de red y ejecuta el ciclo principal de atención al usuario.

### Constantes principales

- `MAX_LARGO_MENSAJE`: longitud máxima permitida para un mensaje.
- `MAX_REINTENTOS_TCP`: cantidad máxima de reintentos para envíos TCP que requieren confirmación.
- `ACK_OK`: confirmación de recepción exitosa.
- `ACK_ERROR`: confirmación de recepción con error.
- `ACK_TIMEOUT`: tiempo máximo de espera de una confirmación TCP.

## Decisiones de diseño

- Separar autenticación/archivos (TCP) y mensajería (UDP) facilita control y depuración.
- Preferir un protocolo simple reduce la complejidad para un laboratorio.
- Usar hilos permite recibir mensajes mientras el usuario escribe.
- Evitar dependencias externas mantiene el proyecto portable.

## Integrantes

```text
Cristian Barreiro
Rafael Padrón
Mateo Araújo
```

## Observaciones

El proyecto fue desarrollado intentando priorizar simplicidad y claridad del código por encima de optimizaciones o arquitecturas complejas.
