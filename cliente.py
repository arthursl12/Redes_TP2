#!/usr/bin/env python3

import socket
import argparse
import sys
import common

def logexit(err):
    print(err)
    sys.exit(1)
    

def validIPv4(addr):
    try:
        socket.inet_pton(socket.AF_INET, addr)
    except socket.error:
        return False
    return True

def validIPv6(addr):
    try:
        socket.inet_pton(socket.AF_INET6, addr)
    except socket.error:
        return False
    return True


"""
Mensagens e seus códigos:
Hello       1
Connection  2
Info file   3
OK          4
Fim         5
FILE        6
ACK         7
"""


def main():
    # Parse dos argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="IP do servidor {v4|v6}")
    parser.add_argument("porta", help="Porta do servidor", type=int)
    parser.add_argument("arquivo", help="Arquivo a ser enviado")
    args = parser.parse_args()
    
    # Valida IPv4 ou IPv6 passado e usa a mesma versão
    if validIPv4(args.ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif validIPv6(args.ip):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
       logexit("Protocolo desconhecido")
       
    # Conecta com o servidor
    s.connect((args.ip, args.porta))
    print("[log] Enviando mensagem")
    s.sendall(common.hello_encode())
    # s.sendall(b"Hello, world")
    data = s.recv(1024)
    s.close()
    print('Received', repr(data))

if __name__ == "__main__":
    main()