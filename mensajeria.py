# mensajeria.py
# Tecnólogo en Informática

import socket
import threading
import hashlib
import os
import sys
from getpass import getpass
from datetime import datetime

MAX_LARGO_MENSAJE = 255

archivos_broadcast = {}

# =========================
# RECIBIR LINEA CRLF
# Recibe datos via sock hasta recibir el delimitador "\r\n"
# Reensambla el mensaje y lo retorna
# =========================
def recibir_linea_crlf(sock):
    buf = ""

    while True:
        data = sock.recv(1024)
        buf += data.decode('utf-8')
        if "\r\n" in buf:     # espera el mensaje "entero"
            break

    return buf.removesuffix("\r\n")


# =========================
# RECIBIR CABECERA ARCHIVO
# Recibe datos via sock hasta encontrar el delimitador "\r\n"
# Reensambla la cabecera del archivo y devuelve también los bytes restantes
# que ya pueden pertenecer al contenido del archivo
# =========================
def recibir_cabecera_archivo(sock):
    data = b""

    while b"\r\n" not in data:
        data += sock.recv(4096)

    linea, resto = data.split(b"\r\n", 1)
    return linea.decode('utf-8'), resto


# =========================
# AUTENTICACION
# =========================
def autenticar(ip_auth, puerto_auth):
    usuario = input("Usuario: ")
    clave = getpass("Clave: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_auth, puerto_auth))

    respuesta = recibir_linea_crlf(sock)
    if respuesta != "Redes 2026 - Laboratorio - Autenticacion de Usuarios":
        print("ERROR: Protocolo de autenticacion incorrecto.\n")
        sys.exit(1)

    md5 = hashlib.md5(clave.encode('utf-8')).hexdigest()
    sock.send(f"{usuario}-{md5}\r\n".encode('utf-8'))

    respuesta = recibir_linea_crlf(sock)
    if respuesta == "SI":
        nombre = recibir_linea_crlf(sock)
        print(f"Bienvenido {nombre}")
        sock.close()
        return usuario
    else:
        print("Usuario o clave incorrectos")
        sock.close()
        exit()


# =========================
# RECEPTOR UDP
# =========================
def receptor_udp(sock, usuario, puerto):
    while True:
        datos, addr = sock.recvfrom(65535)

        try:
            mensaje = datos.decode('utf-8').strip()

            fecha = datetime.now().strftime("%Y.%m.%d %H:%M")

            # MENSAJE NORMAL
            if mensaje.startswith("MSG|"):
                partes = mensaje.split("|", 2)

                usuario_remitente  = partes[1]
                texto = partes[2]

                print(f"[{fecha}] {addr[0]} {usuario_remitente } dice: {texto}")
            elif mensaje.startswith("FILE|"):
                partes = mensaje.split("|", 3)

                usuario_remitente = partes[1]
                if usuario_remitente == usuario:
                        continue

                nombre = partes[2]
                tamanio = int(partes[3])

                ip_origen = addr[0]
                puerto_origen = addr[1]

                sock.sendto(f"GET_FILE|{usuario_remitente }|{nombre}|{tamanio}".encode('utf-8'), (ip_origen, puerto))
            elif mensaje.startswith("GET_FILE|"):
                partes = mensaje.split("|", 3)

                usuario_remitente  = partes[1]
                if usuario_remitente == usuario:
                    nombre = partes[2]
                    tamanio = int(partes[3])

                    ip_origen = addr[0]
                    puerto_origen = addr[1]

                    path = archivos_broadcast.get(nombre)
                    if path:
                        enviar_archivo(usuario, ip_origen, puerto, path, tamanio)

        except:
            print("Error recibiendo datos")


# =========================
# RECEPTOR TCP
# =========================
def receptor_tcp(sock):
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=recibir_archivo, args=(conn, addr), daemon=True).start()



# =========================
# RECIBIR ARCHIVO
# =========================
def recibir_archivo(conn, addr):
    cabereca, resto = recibir_cabecera_archivo(conn)

    usuario, nombre, tamanio = cabereca.split("|")
    tamanio = int(tamanio)
    origen = addr[0]

    bytes_recibidos = 0
    with open(nombre, "wb") as f:
        if resto:
            f.write(resto)
            bytes_recibidos = len(resto)

        while bytes_recibidos < tamanio:
            datos = conn.recv(4096)
            if not datos:
                break

            f.write(datos)
            bytes_recibidos += len(datos)

    conn.close()

    fecha = datetime.now().strftime("%Y.%m.%d %H:%M")

    if bytes_recibidos == tamanio:
        print(f"[{fecha}] {origen} <Recibido {nombre} de {usuario}>")
    else:
        print(f"[{fecha}] {origen} <Error Recibiendo Archivo de {usuario}>")


# =========================
# ENVIAR ARCHIVO
# =========================
def enviar_archivo(usuario, destino, puerto, path, tamanio):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((destino, puerto))

    nombre = os.path.basename(path)

    sock.send(f"{usuario}|{nombre}|{tamanio}\r\n".encode('utf-8'))


    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            
            sock.sendall(chunk)

    sock.close()


# =========================
# MAIN
# =========================
def main():
    if len(sys.argv) < 4:
        print(" Error: faltan argumentos. Uso: mensajeria.py port ipAuth portAuth)")
        sys.exit(1)

    puerto = int(sys.argv[1])
    ip_auth = sys.argv[2]
    puerto_auth = int(sys.argv[3])

    usuario = autenticar(ip_auth, puerto_auth)

    # socket receptor UDP
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp.bind(("", puerto))
    socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # socket receptor TCP
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_tcp.bind(("0.0.0.0", puerto))
    socket_tcp.listen()

    # hilos receptores
    threading.Thread(target=receptor_udp, args=(socket_udp, usuario, puerto), daemon=True).start()
    threading.Thread(target=receptor_tcp, args=(socket_tcp,), daemon=True).start()

    while True:
        entrada = input()

        if " " not in entrada:
            continue

        destino, contenido = entrada.split(" ", 1)

        broadcast = destino == "*"

        # broadcast
        if broadcast:
            destino = "255.255.255.255"
        else:
            try:
                destino = socket.gethostbyname(destino)
            except socket.gaierror:
                print(" Error: Host no encontrado")
                continue


        # archivo
        if contenido.startswith("&file"):
            partes = contenido.split(" ", 1)

            if len(partes) < 2:
                print("Falta path")
                continue

            path = partes[1]
            if not os.path.exists(path):
                print("Archivo no encontrado")
                continue

            nombre = os.path.basename(path)
            tamanio = os.path.getsize(path)

            if broadcast:
                archivos_broadcast[nombre] = path
                socket_udp.sendto(f"FILE|{usuario}|{nombre}|{tamanio}".encode('utf-8'), (destino, puerto))
            else:
                enviar_archivo(usuario, destino, puerto, path, tamanio)
        # mensaje normal
        else:
            if len(contenido) > MAX_LARGO_MENSAJE:
                print("Mensaje demasiado largo")
                continue

            socket_udp.sendto(f"MSG|{usuario}|{contenido}".encode('utf-8'), (destino, puerto))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cerrando sesión...")