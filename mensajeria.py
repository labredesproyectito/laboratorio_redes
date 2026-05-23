# mensajeria.py
# Proyecto MINIMO y SIMPLE para el laboratorio de Redes
# Tecnólogo en Informática

import socket
import threading
import hashlib
import os
from datetime import datetime

MAX_LARGO_MENSAJE = 255


# =========================
# AUTENTICACION
# =========================
def autenticar(ip_auth, puerto_auth):
    usuario = input("Usuario: ")
    clave = input("Clave: ")

    md5 = hashlib.md5(clave.encode()).hexdigest()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_auth, puerto_auth))

    # banner
    print(sock.recv(1024).decode())

    mensaje = f"{usuario}-{md5}\r\n"
    sock.send(mensaje.encode())

    respuesta = sock.recv(1024).decode().strip()

    if respuesta == "SI":
        nombre = sock.recv(1024).decode().strip()
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

    puerto = int(input("Puerto local: "))
    ip_auth = input("IP auth: ")
    puerto_auth = int(input("Puerto auth: "))

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
