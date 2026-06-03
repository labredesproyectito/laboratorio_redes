import socket
import threading
import hashlib
import os
import sys
from datetime import datetime
import argparse
import base64

parser = argparse.ArgumentParser()
parser.add_argument("puerto", type=int)
parser.add_argument("ipAuth")
parser.add_argument("portAuth", type=int)
args = parser.parse_args()

MAX_LARGO_MENSAJE = 255


def autenticador():

    while True:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((args.ipAuth, args.portAuth))

        data = sock.recv(1024)
        print(data.decode())

        nombre = input("Escribe tu nombre: ")
        contraseña = input("Escribe tu contraseña: ")

        mensaje = f"{nombre}-{contraseña}"

        sock.sendall((mensaje + "\r\n").encode("utf-8"))

        print(mensaje)

        data = sock.recv(1024).decode().strip()

        print(data)

        if data == "SI":
            print(f"Bienvenido {nombre}")
            sock.close()
            return nombre

        print("Usuario o clave incorrectos")
        sock.close()


def parsear(texto):

    partes = texto.split()

    ip = partes[0]

    if len(partes) < 2:
        return ip, None, None

    if partes[1].startswith("&"):

        menj = partes[1]
        path = partes[2] if len(partes) > 2 else None

    else:

        menj = " ".join(partes[1:])
        path = None

    return ip, menj, path


def conectar_tcp(ip, puerto):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, puerto))
        return sock

    except:
        print(f"No fue posible conectar con {ip}:{puerto}")
        sock.close()
        return False


def envio(mensaje, ip):

    datos = mensaje.encode("utf-8")

    if ip == "*":

        broad_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broad_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    else:

        sock = conectar_tcp(ip, args.puerto)

        if not sock:
            return

    i = 0

    while i < len(datos):

        bloque = datos[i:i + 255]

        if ip == "*":
            broad_sock.sendto(bloque,("255.255.255.255", args.puerto))
        else:
            sock.sendall(bloque)

        i += 255

    print(f"enviado a {ip}")

    if ip == "*":
        broad_sock.close()
    else:
        sock.close()


def enviar_mensaje(nombre):

    mensaje = input("introduzeca mensaje: ")

    (ip, menj, path) = parsear(mensaje)

    if path is not None:
        
        with open(path, "r", encoding="utf-8") as f:
            path = f.read()
            nombre_archivo = os.path.basename(nombre_archivo)
            path = base64.b64encode(path).decode("utf-8")
            menj = menj + nombre_archivo + " " + path

    if menj is None:
        return

    menj = ip + " " + nombre + " " + menj + "\r\n"

    envio(menj, ip)




def manejar(data_bytes: bytes):
    print("manejando....")

    try:
        data = data_bytes.decode("utf-8")
    except:
        print("error no se puede decodear?")
        return False

    try:
        ip, nombre, resto = data.split(" ", 2)
    except ValueError:
        print("mensaje incompleto")
        return False

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    automatico = fecha + " " + ip + " "

    if resto.startswith("&file "):

        try:
             nombre_archivo, b64_data = resto.split(" ", 2)
        except ValueError:
            print(automatico + "<Error Recibiendo Archivo de " + nombre)
            return False

        

        try:
            archivo_bytes = base64.b64decode(b64_data)
        except Exception as e:
            print(automatico + "<Error Recibiendo Archivo de " + nombre)
            print(e)
            return False

        

        with open(nombre_archivo, "wb") as f:
            f.write(archivo_bytes)

        print(
            automatico +
            "Recibiendo " +
            nombre_archivo +
            " de " +
            nombre
        )

        return True

    else:

        mensaje = resto

        nombre_log = f"{ip}.txt"

        with open(nombre_log, "a", encoding="utf-8") as f:
            f.write(data + "\n")

        print(automatico + nombre + " dice: " + mensaje)

        return True
def handler(data_bytes):
    print("RECIBIDO:", data_bytes)
    manejar(data_bytes)



def broadcast_udp(host, port, handler):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    while True:
        data = s.recv(255)
        handler(data)
def escucha_tcp(host, port, handler):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()

    while True:
        print("Esperando conexión...")
        conn, addr = s.accept()
        print(f"Cliente conectado desde {addr}")


        threading.Thread(
            target=manejar_cliente,args=(conn, handler),daemon=True).start()

def manejar_cliente(conn, handler):
    buffer = b""
    print("reciviendo mensaje")

    DELIM = b"\r\n"
    
    while True:
        try:
            chunk = conn.recv(255)
            if not chunk:
                print("no es un chunk, rompiendo")
                break

            buffer += chunk
            

           
            while DELIM in buffer:
                mensaje, buffer = buffer.split(DELIM, 1)
                print("mensaje recibido... procesando")
                print("LONGITUD MENSAJE RECIBIDO:", len(mensaje))
                handler(mensaje)

        except Exception as e:
            print("conexion fallo")
            print(e)
            break
    
    conn.close()


def iniciar_servidor(host, tcp_port, udp_port, handler):
    threading.Thread(
        target=escucha_tcp,args=(host, tcp_port, handler),daemon=True).start()

    threading.Thread(
        target=broadcast_udp,args=(host, udp_port, handler),daemon=True).start()

def main():

    nombre = autenticador()
    print(f"Usuario autenticado: {nombre}")
    host = "0.0.0.0"

   

    threading.Thread(
        target=iniciar_servidor,args=(host, args.puerto, args.puerto, manejar),daemon=True).start()

    print("Servidor de escucha iniciado")

   
    while True:
        enviar_mensaje(nombre)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCerrando sesión...")