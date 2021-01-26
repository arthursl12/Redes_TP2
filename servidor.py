#!/usr/bin/env python3

import common 
import queue
import select
import socket
import sys
from _thread import *
import argparse

def logexit(err):
    print(err)
    sys.exit(1)

def multi_threaded_client(client, server):
    # connection.send(str.encode('Server is working:'))
    infoClient = client.getsockname()
    infoServer = server.getsockname()
    
    while True:
        data = client.recv(2048)
        if (len(data) == 0):
            print(f"[log] Cliente {infoClient[0]}: {infoClient[1]} " +
                  "encerrou a conexão")
            break
        if data is not None:
            data = bytearray(data)
            print(f"[log] Mensagem recebida de {infoClient[0]}: {infoClient[1]}")
            # print(f"[log] Mensagem: {data}")
            print(f"[log] \tTipo da mensagem: {common.msgId(data)}")
            if (common.msgId(data) == 1):
                # Recebeu mensagem Hello
                # Cria o socket UDP
                udtS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print(f"[udp] Socket UDP criado")
                
                # Usa o mesmo IP, mas uma porta dada pelo sistema
                udtS.bind((infoServer[0],0))
                infoUdt = udtS.getsockname()
                print(f"[udp] Socket com endereço: {infoUdt[0]}: {infoUdt[1]}")
                
                # Manda a mensagem Connection com o número da porta para 
                # o cliente
                b_con = common.connection_encode(infoUdt[1])
                client.sendall(b_con)
            elif (common.msgId(data) == 3):
                # Recebeu mensagem Info_file
                
                
                
                
                
                # print(f"[udp] Aguardando udp: {infoUdt[0]}: {infoUdt[1]}")
                # data, addr = udtS.recvfrom(1024)
                # print(f"[udp] Recebido: {data}")
                
                
            # response = 'Server message: ' + data.decode('utf-8')
            # client.sendall(str.encode(response))
    client.close()

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
        start_new_thread(multi_threaded_client, (Client, server))
        ThreadCount += 1
        print("Número da Thread: " + str(ThreadCount))
    print("[log] Finalizando servidor")
    server.close()


if __name__ == "__main__":
    main()
