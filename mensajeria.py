import argparse
import hashlib
import os
import socket
import sys
import threading
from datetime import datetime
from getpass import getpass

parser = argparse.ArgumentParser()
parser.add_argument("puerto", type=int)
parser.add_argument("ipAuth")
parser.add_argument("portAuth", type=int)
args = parser.parse_args()

MAX_LARGO_MENSAJE = 255


def recibir_linea_crlf(buffer, sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break

        buffer += data

        if b"\r\n" in buffer:
            break

    linea, resto = buffer.split(b"\r\n", 1)
    return linea.decode('utf-8'), resto


def autenticador():
    nombre = input("Usuario: ")
    contrasenia = getpass("Clave: ")

    buffer = b""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.ipAuth, args.portAuth))

    respuesta, buffer = recibir_linea_crlf(buffer, sock)
    if respuesta != "Redes 2026 - Laboratorio - Autenticacion de Usuarios":
        print("ERROR: Protocolo de autenticacion incorrecto.\n")
        sys.exit(1)

    md5 = hashlib.md5(contrasenia.encode('utf-8')).hexdigest()
    mensaje = f"{nombre}-{md5}"
    sock.sendall((mensaje + "\r\n").encode("utf-8"))

    respuesta, buffer = recibir_linea_crlf(buffer, sock)
    if respuesta == "SI":
        nombre_completo, buffer = recibir_linea_crlf(buffer, sock)
        print(f"Bienvenido {nombre_completo}")
        sock.close()
        return nombre
    else:
        print("Usuario o clave incorrectos")
        sock.close()
        exit()


def conectar_tcp(ip, puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        ip = socket.gethostbyname(ip)
        sock.connect((ip, puerto))
        return sock

    except:
        print(f"No fue posible conectar con {ip}:{puerto}")  # debug
        sock.close()
        return False


def enviar_mensaje_udp_broadcast(sock, nombre_usuario, mensaje):
    sock.sendto(f"BROADCAST|MENSAJE|{nombre_usuario}|{mensaje}\r\n".encode('utf-8'), ("255.255.255.255", args.puerto))
    sock.close()


def recibir_mensaje_udp_broadcast(ip_origen, nombre_usuario, mensaje):
    fecha = datetime.now().strftime("%Y.%m.%d %H:%M")
    print(f"[{fecha}] {ip_origen} {nombre_usuario} dice: {mensaje}")


def enviar_archivo_udp_broadcast(sock, nombre_usuario, ruta_archivo):
    sock.sendto(f"BROADCAST|ARCHIVO|{nombre_usuario}|{ruta_archivo}\r\n".encode('utf-8'), ("255.255.255.255", args.puerto))
    sock.close()


def enviar_mensaje_tcp(sock, nombre_usuario, mensaje):
    sock.sendall(f"MENSAJE|{nombre_usuario}|{mensaje}\r\n".encode('utf-8'))
    sock.close()


def recibir_mensaje_tcp(sock, nombre_usuario, mensaje):
    ip_origen, puerto = sock.getpeername()
    fecha = datetime.now().strftime("%Y.%m.%d %H:%M")
    print(f"[{fecha}] {ip_origen} {nombre_usuario} dice: {mensaje}")
    sock.close()


def enviar_archivo_tcp(sock, nombre_usuario, path):
    nombre_archivo = os.path.basename(path)
    tamanio_archivo = os.path.getsize(path)

    sock.sendall(f"ARCHIVO|{nombre_usuario}|{nombre_archivo}|{tamanio_archivo}\r\n".encode('utf-8'))

    with open(path, "rb") as f:
        while True:
            chunk = f.read(4096)  # Manda los bytes del archivo en chunks de 4kib
            if not chunk:
                break

            sock.sendall(chunk)

    sock.close()


def recibir_archivo_tcp(sock, usuario, nombre_archivo, tamanio_archivo, resto):
    ip_origen, puerto = sock.getpeername()

    bytes_recibidos = 0
    with open(nombre_archivo, "wb") as f:
        if resto:
            bytes_recibidos += len(resto)
            f.write(resto)

        while bytes_recibidos < tamanio_archivo:
            faltan = tamanio_archivo - bytes_recibidos
            datos = sock.recv(min(4096, faltan))
            if not datos:
                break

            f.write(datos)
            bytes_recibidos += len(datos)

    sock.close()

    fecha = datetime.now().strftime("%Y.%m.%d %H:%M")

    if bytes_recibidos == tamanio_archivo:
        print(f"[{fecha}] {ip_origen} <Recibido ./{nombre_archivo} de {usuario}>")
    else:
        print(f"[{fecha}] {ip_origen} <Error Recibiendo Archivo de {usuario}>")


def parsear(texto):
    partes = texto.split(" ", 1)

    if len(partes) < 2:
        return None, None, None

    destino = partes[0]
    resto = partes[1]

    if resto.startswith("&file"):
        file_partes = resto.split(" ", 2)

        if len(file_partes) < 2:
            return destino, None, None

        path = file_partes[1]
        return destino, "&file", path

    return destino, resto, None


def escucha_udp_broadcast(host, port, nombre_usuario):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        manejar_udp(sock, nombre_usuario)


def escucha_tcp(host, port, nombre_usuario):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=manejar_tcp, args=(conn,), daemon=True).start()


def manejar_udp(sock, nombre_usuario_local):
    datos, addr = sock.recvfrom(1024)
    texto = datos.decode("utf-8").removesuffix("\r\n")

    if not texto.startswith("BROADCAST|"):
        return

    texto = texto.removeprefix("BROADCAST|")
    partes = texto.split("|")
    tipo = partes[0]
    if tipo == "MENSAJE":
        nombre_usuario = partes[1]
        mensaje = partes[2]
        recibir_mensaje_udp_broadcast(addr[0], nombre_usuario, mensaje)
    elif tipo == "ARCHIVO":
        nombre_usuario = partes[1]
        ruta_archivo = partes[2]

        if (nombre_usuario_local == nombre_usuario):
            return

        tcp_sock = conectar_tcp(addr[0], args.puerto)
        if not tcp_sock:
            return

        tcp_sock.sendall(f"PEDIR_ARCHIVO|{nombre_usuario}|{ruta_archivo}\r\n".encode('utf-8'))
        manejar_tcp(tcp_sock)


def manejar_tcp(sock):
    buffer = b""

    respuesta, buffer = recibir_linea_crlf(buffer, sock)

    partes = respuesta.split("|")
    tipo = partes[0]
    if tipo == "MENSAJE":
        nombre_usuario = partes[1]
        mensaje = partes[2]
        recibir_mensaje_tcp(sock, nombre_usuario, mensaje)
    elif tipo == "ARCHIVO":
        nombre_usuario = partes[1]
        nombre_archivo = partes[2]
        tamanio_archivo = int(partes[3])
        recibir_archivo_tcp(sock, nombre_usuario, nombre_archivo, tamanio_archivo, buffer)
    elif tipo == "PEDIR_ARCHIVO":
        nombre_usuario = partes[1]
        ruta_archivo = partes[2]
        enviar_archivo_tcp(sock, nombre_usuario, ruta_archivo)


def manejar_cliente(nombre_usuario):
    entrada = input()

    ip_destino, contenido, ruta_archivo = parsear(entrada)

    if not ip_destino or not contenido:
        return

    if contenido.startswith("&file"):
        if not ruta_archivo:
            print("Error: Falta path")
            return

        if not os.path.exists(ruta_archivo):
            print("Error: Archivo no encontrado")
            return

        if ip_destino == "*":
            broad_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broad_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            enviar_archivo_udp_broadcast(broad_sock, nombre_usuario, ruta_archivo)
            return

        sock = conectar_tcp(ip_destino, args.puerto)
        if not sock:
            return

        enviar_archivo_tcp(sock, nombre_usuario, ruta_archivo)
    else:
        if len(contenido) > MAX_LARGO_MENSAJE:
            print("Error: Mensaje demasiado largo")
            return

        if ip_destino == "*":
            broad_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broad_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            enviar_mensaje_udp_broadcast(broad_sock, nombre_usuario, contenido)
            return

        sock = conectar_tcp(ip_destino, args.puerto)
        if not sock:
            return

        enviar_mensaje_tcp(sock, nombre_usuario, contenido)


def iniciar_servidor(host, tcp_port, udp_port, nombre_usuario):
    threading.Thread(target=escucha_tcp, args=(host, tcp_port, nombre_usuario), daemon=True).start()
    threading.Thread(target=escucha_udp_broadcast, args=(host, udp_port, nombre_usuario), daemon=True).start()


def main():
    nombre_usuario = autenticador()
    host = "0.0.0.0"

    iniciar_servidor(host, args.puerto, args.puerto, nombre_usuario)

    while True:
        manejar_cliente(nombre_usuario)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCerrando sesión...")
