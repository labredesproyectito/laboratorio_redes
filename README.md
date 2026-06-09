# README - Laboratorio de Redes de Computadoras

## Descripción

Tarea obligatoria de redes.
Para enviar mensajes a hosts especificos o por broadcast se utiliza el protocolo UDP.
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

- [x] Enviar mensaje (UDP)
- [x] Enviar broadcast (UDP)
- [x] Enviar archivo (TCP)
- [x] Broadcast de archivo (señalización por UDP y transferencia por TCP)
- [x] Autenticación con servidor (envío de MD5)
- [x] Recepción y guardado de archivos en directorio actual
- [ ] Reintentos / confirmación de entrega (no implementado)

## Formato de mensajes

El protocolo actual utiliza formatos simples:

- Texto: `MSG|usuario|mensaje`
- Archivo: `FILE|usuario|nombre|tamanio`
- Enviar archivo broadcast mediante TCP: `GET_FILE|usuario|nombre|tamanio`

## Recepción de archivos

Los archivos recibidos se guardan en el directorio actual.

## Tecnologías usadas

- Python
- socket
- threading
- hashlib

## Limitaciones actuales

En la implementación actual se reconocen estas limitaciones:

- Los mensajes son enviados por UDP, por lo cual pueden perderse y no llegar correctamente. Es una desicion asumida para el programa

## Estructura del programa

El archivo principal `mensajeria.py` contiene las siguientes partes principales:

- `recibir_linea_crlf(buffer, sock)`: lee datos de un socket TCP hasta encontrar el delimitador `\r\n`, devuelve la línea completa y los bytes restantes.
- `autenticador()`: solicita usuario y clave, calcula el MD5, se conecta al servidor de autenticación y valida las credenciales.
- `conectar_tcp(ip, puerto)`: convierte hostname a dirección IP y abre una conexión TCP hacia el destino.
- `enviar_mensaje_udp_broadcast(sock, nombre_usuario, mensaje)`: envía un mensaje UDP broadcast usando el formato `BROADCAST|MENSAJE|...`.
- `enviar_archivo_udp_broadcast(sock, nombre_usuario, ruta_archivo)`: envía la señal de broadcast para pedir transferencia de archivo a todos los hosts.
- `enviar_mensaje_tcp(sock, nombre_usuario, mensaje)`: envía un mensaje directo por TCP al servidor/destino.
- `enviar_archivo_tcp(sock, nombre_usuario, path)`: envía la cabecera de archivo y a continuación los bytes del archivo por TCP.
- `recibir_mensaje_udp_broadcast(ip_origen, nombre_usuario, mensaje)`: muestra en pantalla un mensaje recibido por UDP broadcast.
- `recibir_mensaje_tcp(sock, nombre_usuario, mensaje)`: muestra en pantalla un mensaje recibido por TCP.
- `recibir_archivo_tcp(sock, usuario, nombre_archivo, tamanio_archivo, resto)`: recibe un archivo por TCP y lo guarda en disco, manejando bytes restantes que ya llegaron junto a la cabecera.
- `parsear(texto)`: interpreta la entrada del usuario y distingue destino, comando `&file` y ruta de archivo.
- `escucha_udp_broadcast(host, port, nombre_usuario)`: mantiene un hilo escuchando paquetes UDP en el puerto local.
- `escucha_tcp(host, port, nombre_usuario)`: mantiene un hilo escuchando conexiones TCP entrantes y delegando cada conexión a `manejar_tcp`.
- `manejar_udp(sock, nombre_usuario_local)`: procesa paquetes UDP recibidos y decide si son mensajes o solicitudes de transferencia de archivo.
- `manejar_tcp(sock)`: procesa la primera línea TCP recibida, identifica el tipo de operación (`MENSAJE`, `ARCHIVO`, `PEDIR_ARCHIVO`) y llama a la función apropiada.
- `manejar_cliente(nombre_usuario)`: lee la entrada del usuario desde teclado y envía mensajes o archivos según la sintaxis.
- `iniciar_servidor(host, tcp_port, udp_port, nombre_usuario)`: arranca los hilos de escucha TCP y UDP.
- `main()`: inicia la autenticación y luego ejecuta el bucle principal de lectura de comandos.

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
