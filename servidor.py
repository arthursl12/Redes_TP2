#!/usr/bin/env python3

from common import msgId
import queue
import select
import socket
import sys
from _thread import *
import argparse

def logexit(err):
    print(err)
    sys.exit(1)

def multi_threaded_client(connection):
    # connection.send(str.encode('Server is working:'))
    infoClient = connection.getsockname()
    while True:
        data = connection.recv(2048)
        if (len(data) == 0):
            print(f"[log] Cliente {infoClient[0]}: {infoClient[1]} " +
                  "encerrou a conexão")
            break
        if data is not None:
            data = bytearray(data)
            print(f"[log] Mensagem recebida de {infoClient[0]}: {infoClient[1]}")
            # print(f"[log] Mensagem: {data}")
            print(f"[log] \tTipo da mensagem: {msgId(data)}")
            response = 'Server message: ' + data.decode('utf-8')
            connection.sendall(str.encode(response))
    connection.close()

def main():
    # Parse dos argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("porta", help="Porta do servidor", type=int)
    parser.add_argument("-v","--version", 
                        help="Versão do IP do servidor", default="v4")
    args = parser.parse_args()
    
    # Inicialização
    if (args.version == "v4"):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif (args.version == "v6"):
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        logexit("Protocolo desconhecido")
    print ("[log] Servidor iniciado")
    # server.setblocking(0)
    try:
        server.bind(('', args.porta))
    except socket.error as e:
        logexit(str(e))
    
    infoServer = server.getsockname()
    print (f"[log] Aguardando conexões em {infoServer[0]}, {infoServer[1]}")

    # Loop principal
    server.listen(5)
    ThreadCount = 0
    while True:
        Client, address = server.accept()
        print('[log] Conexão com sucesso: '+ address[0] 
              + ':' + str(address[1]))
        start_new_thread(multi_threaded_client, (Client, ))
        ThreadCount += 1
        print("Número da Thread: " + str(ThreadCount))
    print("[log] Finalizando servidor")
    server.close()


if __name__ == "__main__":
    main()
