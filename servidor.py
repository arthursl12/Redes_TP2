#!/usr/bin/env python3

import argparse
import queue
import select
import socket
import sys
from threading import Thread
# from _thread import *

from common import (MAX_PAYLOAD_SIZE, WINDOW_SIZE, ack_encode,
                    connection_encode, fim_encode, info_file_decode, msgId,
                    ok_encode)
from fileassembler import FileAssembler


def logexit(err):
    print(err)
    sys.exit(1)


def multi_threaded_client(client, server):
    # connection.send(str.encode('Server is working:'))
    infoClient = client.getsockname()
    infoServer = server.getsockname()
    
    exit_loop = False
    def receive_file_thread(client, udtS):
        proximo_idx = 0
        while(True):
            
            data,_ = udtS.recvfrom(MAX_PAYLOAD_SIZE+20)
            if not data:
                print("[log] Conexão UDP encerrada precocemente")
                break
            data = bytearray(data)
            assert msgId(data) == 6
            (seq, _, _) = f.file_pkt_decode(data)
            print(f"[udp] Recebi o pacote {seq}, deveria ser entre {proximo_idx} e {proximo_idx + WINDOW_SIZE}")
            if (seq >= proximo_idx and seq <= proximo_idx+WINDOW_SIZE):
                print(f"[udp] Acknowledge do pacote {seq}")
                
                # Guarda o pacote na posição correspondente e envia o ACK
                # pkts.append(data) 
                pkts[seq] = data 
                client.sendall(ack_encode(seq))
                if (seq == proximo_idx):
                    # Avança início da janela
                    proximo_idx += 1
                    print(f"[udp] Próximo está entre {proximo_idx} e {proximo_idx + WINDOW_SIZE}")
    
    while True:
        print("[log] Aguardando mensagem do cliente")
        data = client.recv(2048)
        if (len(data) == 0):
            print(f"[log] Cliente {infoClient[0]}: {infoClient[1]} " +
                  "encerrou a conexão")
            break
        if data is not None:
            data = bytearray(data)
            print(f"[log] Mensagem recebida de {infoClient[0]}: {infoClient[1]}")
            # print(f"[log] Mensagem: {data}")
            print(f"[log] \tTipo da mensagem: {msgId(data)}")
            if (msgId(data) == 1):
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
                b_con = connection_encode(infoUdt[1])
                client.sendall(b_con)
            elif (msgId(data) == 3):
                # Recebeu mensagem Info_file
                nome, tam = info_file_decode(data)
                print(f"[udp] Informações do arquivo: {nome}: {tam}")

                # Alocar estruturas para janela deslizante do receptor
                
                qtd_pkts = tam//MAX_PAYLOAD_SIZE
                if (tam % MAX_PAYLOAD_SIZE != 0):
                    qtd_pkts += 1
                pkts = [None for _ in range(qtd_pkts)]
                f = FileAssembler(nome,qtd_pkts)
                print(f"[udp] Alocado um vetor de {len(pkts)} posições")

                # Envia o OK para o cliente
                print(f"[udp] Enviando OK")
                client.sendall(ok_encode())
                
                # Cria uma thread para receber os pacotes
                
                print(f"[udp] Aguardando pacotes")
                # start_new_thread(receive_file_thread, (client, udtS))
                proximo_idx = 0
                while(True and len(pkts) > 0):
                    data,_ = udtS.recvfrom(MAX_PAYLOAD_SIZE+20)
                    if not data:
                        print("[log] Conexão UDP encerrada precocemente")
                        break
                    data = bytearray(data)
                    assert msgId(data) == 6
                    (seq, _, _) = f.file_pkt_decode(data)
                    print(f"[udp] Recebi o pacote {seq}, deveria ser entre {proximo_idx} e {proximo_idx + WINDOW_SIZE}")
                    if (seq >= proximo_idx and seq <= proximo_idx+WINDOW_SIZE):
                        print(f"[udp] Acknowledge do pacote {seq}")
                        
                        # Guarda o pacote na posição correspondente e envia o ACK
                        # pkts.append(data) 
                        f.pkts[seq] = data
                        f.ack[seq] = True
                        f.assemblePacket(seq)
                        client.sendall(ack_encode(seq))
                        if (seq == proximo_idx):
                            # Avança início da janela
                            proximo_idx += 1
                            print(f"[udp] Próximo está entre {proximo_idx} e {proximo_idx + WINDOW_SIZE}")
                    print(f"[log] Recebeu todos? {all(p for p in f.ack)}")
                    i = 0
                    for p in f.ack:
                        if p is None:
                            print(f"[log] Pacote: {i} é None")
                        i += 1
                    if all(p for p in f.ack):
                        # Já recebeu todos
                        break
                # Edge-case: arquivo vazio
                if (len(pkts) == 0):
                    f.assemblePacket(None)
                # Terminou de receber o arquivo
                # f.pkts = pkts
                print("[log] Arquivo recebido por completo")
                print("[log] Enviando mensagem de fim")
                client.sendall(fim_encode())
                
                print(f"[log] Encerrando conexão UDP com o cliente "+
                      f"{infoClient[0]}: {infoClient[1]}")
                udtS.close()
                print(f"[log] Encerrando soquete TCP com o cliente "+
                      f"{infoClient[0]}: {infoClient[1]}")
                client.close()
                
                print(f"[log] Escrevendo arquivo {f.nome_arq} em disco")
                # f.pkts = pkts 
                # f.assembleFile()
                print(f"[log] Arquivo {f.nome_arq} disponível  em disco")
                break

            # elif (msgId(data) == 5):
                # # Recebeu mensagem de fim
                # print("[log] Arquivo recebido por completo")
                # f.pkts = pkts
                # exit_loop = True   
                # print(f"[log] Encerrando conexão UDP com o cliente "+
                #       f"{infoClient[0]}: {infoClient[1]}")
                # udtS.close()
                # print(f"[log] Encerrando soquete TCP com o cliente "+
                #       f"{infoClient[0]}: {infoClient[1]}")
                # print(f"[log] Escrevendo arquivo {f.nome_arq} em disco")
                # f.assembleFile()
                # print(f"[log] Arquivo {f.nome_arq} disponível  em disco")
                
                # break
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
        cltT = Thread(target=multi_threaded_client, args=(Client, server))
        cltT.start()
        # start_new_thread(multi_threaded_client, (Client, server))
        ThreadCount += 1
        print("Número da Thread: " + str(ThreadCount))
    print("[log] Finalizando servidor")
    server.close()


if __name__ == "__main__":
    main()
