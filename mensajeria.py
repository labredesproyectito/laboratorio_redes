# mensajeria.py
# Proyecto MINIMO y SIMPLE para el laboratorio de Redes
# Tecnólogo en Informática

import socket
import threading
import hashlib
import os
import sys
from datetime import datetime

MAX_LARGO_MENSAJE = 255

# =========================
# RECIBIR TCP
# =========================
def recibir(sock):
# Recibe datos via sock hasta recibir el delimitador "\r\n"
# Reensambla el mensaje y lo retorna
    buf = ""

    while True:
        data = sock.recv(1024)
        buf += data.decode('utf-8')
        if "\r\n" in buf:     # espera el mensaje "entero"
            break

    return buf.removesuffix("\r\n")
# Fin recibir

# =========================
#  ENVIAR TCP
# =========================
def enviar(sock, msg):
    sock.send(msg.encode('utf-8'))

# =========================
# AUTENTICACION
# =========================
def autenticar(ip_auth, puerto_auth):
    usuario = input("Usuario: ")
    clave = input("Clave: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_auth, puerto_auth))

    respuesta = recibir(sock)
    if respuesta != "Redes 2026 - Laboratorio - Autenticacion de Usuarios":
        print("ERROR: Protocolo de autenticacion incorrecto.\n")
        sys.exit(1)

    md5 = hashlib.md5(clave.encode('utf-8')).hexdigest()
    enviar(sock, f"{usuario}-{md5}\r\n")

    respuesta = recibir(sock)
    if respuesta == "SI":
        nombre = recibir(sock)
        print(f"Bienvenido {nombre}")
        sock.close()
        return usuario
    else:
        print("Usuario o clave incorrectos")
        sock.close()
        exit()

# =========================
# RECEPTOR
# =========================
def receptor(puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", puerto))

    while True:
        datos, addr = sock.recvfrom(65535)

        try:
            mensaje = datos.decode()

            fecha = datetime.now().strftime("%Y.%m.%d %H:%M")

            # MENSAJE NORMAL
            if mensaje.startswith("MSG|"):
                partes = mensaje.split("|", 2)

                usuario = partes[1]
                texto = partes[2]

                print(f"\n[{fecha}] {addr[0]} {usuario} dice: {texto}")

            # ARCHIVO
            elif mensaje.startswith("FILE|"):
                partes = mensaje.split("|", 3)

                usuario = partes[1]
                nombre = partes[2]
                contenido = partes[3].encode("latin1")

                with open(nombre, "wb") as f:
                    f.write(contenido)

                print(f"\n[{fecha}] {addr[0]} <Recibido {nombre} de {usuario}>")

        except:
            print("Error recibiendo datos")

# =========================
# ENVIAR MENSAJE
# =========================
def enviar_mensaje(sock, usuario, destino, puerto, texto):

    mensaje = f"MSG|{usuario}|{texto}"

    sock.sendto(mensaje.encode(), (destino, puerto))

# =========================
# ENVIAR ARCHIVO
# =========================
def enviar_archivo(sock, usuario, destino, puerto, path):

    if not os.path.exists(path):
        print("Archivo no encontrado")
        return

    nombre = os.path.basename(path)

    with open(path, "rb") as f:
        contenido = f.read()

    mensaje = f"FILE|{usuario}|{nombre}|".encode() + contenido

    sock.sendto(mensaje, (destino, puerto))

    print("Archivo enviado")

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

    # socket emisor UDP
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # broadcast
    sock_envio.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # hilo receptor
    hilo = threading.Thread(target=receptor, args=(puerto,))
    hilo.daemon = True
    hilo.start()

    print("Mensajeria iniciada")

    while True:

        entrada = input()

        if " " not in entrada:
            continue

        destino, contenido = entrada.split(" ", 1)

        # broadcast
        if destino == "*":
            destino = "255.255.255.255"

        # archivo
        if contenido.startswith("&file"):

            partes = contenido.split(" ", 1)

            if len(partes) < 2:
                print("Falta path")
                continue

            path = partes[1]

            enviar_archivo(
                sock_envio,
                usuario,
                destino,
                puerto,
                path
            )

        # mensaje normal
        else:

            if len(contenido) > MAX_LARGO_MENSAJE:
                print("Mensaje demasiado largo")
                continue

            enviar_mensaje(
                sock_envio,
                usuario,
                destino,
                puerto,
                contenido
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCerrando sesión...")