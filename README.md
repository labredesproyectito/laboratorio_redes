# README - Laboratorio Redes de Computadoras

Proyecto realizado para el obligatorio de Redes de Computadoras.  
Aplicación de mensajería simple utilizando sockets UDP y autenticación TCP en Python.

El programa permite:

- Enviar mensajes entre pares
- Recibir mensajes
- Enviar archivos
- Recibir archivos
- Broadcast a toda la red
- Autenticación mediante servidor externo

---

# Requisitos

- Python 3
- Linux / Windows
- Conexión de red

---

# Ejecución

```bash
python mensajeria.py
```

Luego ingresar:

```text
Puerto local
IP servidor autenticación
Puerto servidor autenticación
```

Ejemplo:

```text
Puerto local: 22764
IP auth: ti.esi.edu.uy
Puerto auth: 33
```

---

# Autenticación

El programa solicita:

```text
Usuario
Clave
```

La clave se convierte a MD5 y se envía al servidor de autenticación.

Si la autenticación es correcta:

```text
Bienvenido Nombre_Apellido
```

---

# Enviar mensajes

Formato:

```text
IP mensaje
```

Ejemplo:

```text
192.168.1.10 Hola
```

También se puede usar hostname:

```text
pc01 Hola
```

---

# Broadcast

Enviar a todos:

```text
* Hola a todos
```

---

# Enviar archivos

Formato:

```text
IP &file ruta_archivo
```

Ejemplo:

```text
192.168.1.10 &file foto.jpg
```

Broadcast de archivos:

```text
* &file foto.jpg
```

---

# Recepción de archivos

Los archivos recibidos se guardan en el directorio actual.

---

# Tecnologías usadas

- Python
- socket
- threading
- hashlib

---

# Estructura del programa

```text
mensajeria.py
├── autenticar()
├── receptor()
├── enviar_mensaje()
├── enviar_archivo()
└── main()
```

---

# Decisiones tomadas

Se buscó realizar una implementación:

- Simple
- Fácil de entender
- Fácil de defender
- Con pocas dependencias
- Sin programación compleja

Se utilizó:

- UDP para mensajes y archivos
- Threads para recepción simultánea
- TCP para autenticación

---

# Limitaciones actuales

- No verifica pérdida de paquetes UDP
- No divide archivos grandes
- No controla archivos duplicados
- No valida integridad de archivos
- No posee interfaz gráfica
- No maneja múltiples conversaciones
- El protocolo es muy simple

---

# Posibles mejoras

## 1. Mejor protocolo

Actualmente:

```text
MSG|usuario|mensaje
```

Podría implementarse:

- JSON
- Headers
- Tamaño de paquete
- Checksum

---

## 2. Envío confiable de archivos

Actualmente UDP puede perder paquetes.

Mejoras:

- ACK
- Reenvío automático
- División en fragmentos

---

## 3. Interfaz gráfica

Crear GUI con:

- Tkinter
- PyQt

---

## 4. Cifrado

Agregar:

- TLS
- AES
- Encriptación de mensajes

---

## 5. Manejo de usuarios conectados

Agregar:

- Lista de usuarios online
- Estados
- Historial

---

## 6. Mejor manejo de errores

Actualmente los errores son básicos.

Se podría agregar:

- Logs
- Excepciones específicas
- Reintentos automáticos

---

# Integrantes

```text
Nombre - CI
Nombre - CI
Nombre - CI
```

---

# Observaciones

El proyecto fue desarrollado intentando priorizar simplicidad y claridad del código por encima de optimizaciones o arquitecturas complejas.
