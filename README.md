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

El archivo principal `mensajeria.py` contiene:

- `recibir_linea_crlf()`: Recibe datos via sock hasta recibir el delimitador "\r\n", lo reensambla y lo retorna.
- `recibir_cabecera_archivo()`: Recibe datos via sock hasta encontrar el delimitador "\r\n", reensambla la cabecera del archivo y devuelve también los bytes restantes que ya pueden pertenecer al contenido del archivo.
- `autenticar()`: Maneja la conexión y validación de credenciales con el servidor TCP.
- `receptor_udp()`: escucha paquetes UDP en un hilo independiente.
- `receptor_tcp()`: escucha paquetes TCP en un hilo independiente.
- `recibir_archivo()`: recibe archivos mediante socket TCP y revisa que los bytes recibidos sean iguales a los bytes esperados del archivo
- `enviar_archivo()`: envía archivos al destino mediante TCP, lee el archivo en chunks de 64 KiB y los envia por partes.
- `main()`: controla el bucle principal y el flujo del cliente.

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
