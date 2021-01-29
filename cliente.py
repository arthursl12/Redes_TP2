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
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif validIPv6(args.ip):
        tcp_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
       logexit("Protocolo desconhecido")
       
    # Conecta com o servidor
    tcp_socket.connect((args.ip, args.porta))
    infoCliente = tcp_socket.getsockname()
    
    # Envia a mensagem Hello
    print("[log] Enviando hello")
    tcp_socket.sendall(common.hello_encode())
    
    # Recebe a mensagem Connection do servidor, com o número da porta
    data = tcp_socket.recv(1024)
    # print(f"[log] Mensagem: {data}")
    data = bytearray(data)
    tipo = common.msgId(data)
    print(f"[log] \tTipo da mensagem: {tipo}")
    if (tipo != 2):
        logexit("Mensagem de Connection inválida")
    porta = common.connection_decode(data)
    print(f"[log] Recebido a porta UDP {porta}")
    
    # Cria socket UDP
    if validIPv4(args.ip):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif validIPv6(args.ip):
        udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    else:
        logexit("Protocolo desconhecido")
    
    # Conecta ao socket UDP do servidor
    udp_socket.bind((infoCliente[0],0)) 
    
    # Envia a mensagem Info_file ao servidor, com o nome e tamanho do arquivo
    print("[log] Enviando info_file")
    filename = "teste1.txt"
    size = 2043
    tcp_socket.sendall(common.info_file_encode(filename,size))
    
    # Recebe a mensagem de OK do servidor
    print("[log] Aguardando ok do servidor")
    data = tcp_socket.recv(1024)
    # print(f"[log] Mensagem: {data}")
    data = bytearray(data)
    tipo = common.msgId(data)
    print(f"[log] \tTipo da mensagem: {tipo}")
    if (tipo != 4):
        logexit("Mensagem de OK inválida")
    print("[log] Ok recebido")
    
    # Janela deslizante pode começar
        
    # udp_socket.sendto(b"teste",(args.ip, porta))
    # print(f"[udp] Enviando arquivo pelo socket UDP, com porta {porta}")
    
    # s.sendall(b"Hello, world")
    data = tcp_socket.recv(1024)
    tcp_socket.close()
    print('Received', repr(data))

if __name__ == "__main__":
    main()