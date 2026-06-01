# README - Laboratorio de Redes de Computadoras

## Descripción

Proyecto desarrollado para el laboratorio de Redes de Computadoras. Esta aplicación de mensajería implementa comunicación UDP para intercambio de mensajes y archivos, y utiliza TCP para autenticación de usuarios.

El enfoque principal es presentar:

- Comunicación entre pares con UDP
- Broadcast en la red local
- Envío y recepción de archivos
- Autenticación centralizada con servidor TCP
- Código simple, claro y fácil de defender

## Características

- Mensajería unicast entre clientes
- Broadcast de texto y archivos
- Envío de archivos binarios
- Recepción de archivos en el directorio local
- Autenticación mediante servidor externo
- Soporte multiplataforma: Windows / Linux

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
python mensajeria.py 22764 ti.esi.edu.uy 33
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
Bienvenido Nombre_Apellido
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

## Comandos especiales

```text
/help
/exit
```

- `/help`: muestra instrucciones de uso.
- `/exit`: cierra la aplicación de forma controlada.

## Formato de mensajes

El protocolo actual utiliza formatos simples:

- Texto: `MSG|usuario|mensaje`
- Archivo: `FILE|usuario|nombre|contenido`

## Recepción de archivos

Los archivos recibidos se guardan en el directorio actual.

Para evitar sobrescribir archivos, el programa debería renombrar archivos duplicados como:

- `documento.pdf`
- `documento_1.pdf`
- `documento_2.pdf`

## Tecnologías usadas

- Python
- socket
- threading
- hashlib

## Limitaciones actuales

En la implementación actual se reconocen estas limitaciones:

- El archivo se envía en un solo paquete UDP
- No hay control de pérdida ni reenvío de paquetes
- No hay validación de integridad de archivos
- No hay fragmentación para archivos grandes
- El protocolo es muy básico
- No existe historial de conversaciones
- No se maneja una lista de usuarios conectados

## Mejora propuesta para nota 10/10

Para elevar el proyecto hacia una calificación excelente, se recomienda trabajar en los siguientes puntos:

- [ ] Transferencia de archivos robusta
  - Codificar archivos en Base64 para soportar datos binarios.
  - Decodificar y escribir contenido binario al recibir.

- [ ] Límite y fragmentación de archivos
  - Limitar el tamaño máximo de envío a un valor seguro (por ejemplo 50 KB).
  - O implementar fragmentación para permitir archivos más grandes.

- [ ] Validación de mensajes
  - Verificar el formato de los paquetes antes de procesarlos.
  - Evitar errores por paquetes malformados.

- [ ] Comandos de ayuda y salida
  - Agregar `/help` para mostrar uso y ejemplos.
  - Agregar `/exit` para una salida ordenada.

- [ ] Evitar sobrescritura de archivos
  - Generar nombres alternativos cuando un archivo ya exista.

- [ ] Manejo de errores en autenticación
  - Detectar fallos de conexión, timeout y respuestas inválidas.
  - Mostrar mensajes claros al usuario.

- [ ] Validación de longitud de mensajes en recepción
  - No solo validar al enviar, también al recibir.

- [ ] Manejo de excepciones específico
  - Reemplazar `except:` con excepciones concretas.
  - Facilitar la detección de problemas.

- [x] Documentación y comentarios
  - Documentar el flujo de trabajo y las funciones clave.
  - Añadir comentarios que expliquen decisiones de diseño.

- [ ] Pruebas completas
  - Mensajes unicast y broadcast.
  - Envío y recepción de archivos.
  - Autenticación correcta e incorrecta.
  - Uso simultáneo por varios usuarios.

## Estructura del programa

El archivo principal `mensajeria.py` contiene:

- `autenticar()`: maneja la conexión y validación de credenciales con el servidor TCP.
- `receptor()`: escucha paquetes UDP en un hilo independiente.
- `enviar_mensaje()`: envía mensajes de texto a un destino UDP.
- `enviar_archivo()`: envía archivos al destino UDP.
- `main()`: controla el bucle principal y el flujo del cliente.

## Decisiones de diseño

- Separar autenticación (TCP) y mensajería (UDP) facilita control y depuración.
- Preferir un protocolo simple reduce la complejidad para un laboratorio.
- Usar hilos permite recibir mensajes mientras el usuario escribe.
- Evitar dependencias externas mantiene el proyecto portable.

## Pruebas recomendadas

- Autenticación exitosa con usuario y clave válidos.
- Autenticación fallida con credenciales inválidas.
- Mensajes unicast entre dos instancias del cliente.
- Broadcast de texto y archivo a múltiples receptores.
- Recepción de un archivo con el mismo nombre varias veces.

## Integrantes

```text
Nombre - CI
Nombre - CI
Nombre - CI
```

## Observaciones

El proyecto fue desarrollado intentando priorizar simplicidad y claridad del código por encima de optimizaciones o arquitecturas complejas.

## Conclusión

Este proyecto es una base sólida para el laboratorio de redes. Con las mejoras propuestas se puede lograr un sistema más robusto, seguro y fácil de defender, acercándolo mucho a una nota 10/10.
