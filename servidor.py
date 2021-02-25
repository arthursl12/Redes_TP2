#!/usr/bin/env python3

import argparse
import socket
import sys
from threading import Thread

from common import (MAX_PAYLOAD_SIZE, WINDOW_SIZE, ack_encode,
                    connection_encode, fim_encode, info_file_decode, msgId,
                    ok_encode)
from fileassembler import FileAssembler


def logexit(err):
    print(err)
    sys.exit(1)

def establishUDP(client, infoServer):
    """
    Cria o soquete UDP e envia a informação da porta para o cliente
    """
    # Cria o socket UDP
    udtS = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    udtS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udtS.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY, 0)
    print(f"[udp] Socket UDP criado")
    
    # Usa o mesmo IP, mas uma porta dada pelo sistema
    udtS.bind((infoServer[0],0))
    infoUdt = udtS.getsockname()
    print(f"[udp] Socket com endereço: {infoUdt[0]}: {infoUdt[1]}")
    
    # Manda a mensagem Connection com o número da porta para o cliente
    b_con = connection_encode(infoUdt[1])
    client.sendall(b_con)
    
    return udtS

def slidingWindow(client, udtS, pkts, fAssembler):
    """
    Implementa a janela deslizante do receptor. Se um pacote foi recebido e a 
    janela já avançou de sua posição, esse pacote é escrito no arquivo
    """
    print(f"[udp] Aguardando pacotes")
    proximo_idx = 0
    while(True and len(pkts) > 0):
        # Recebe exatamente um pacote FILE do soquete UDP
        data,_ = udtS.recvfrom(MAX_PAYLOAD_SIZE+20)
        if not data:
            print("[log] Conexão UDP encerrada precocemente")
            break
            
        # Verifica validade do pacote e o decodifica
        data = bytearray(data)
        assert msgId(data) == 6
        (seq, _, _) = fAssembler.file_pkt_decode(data)
        print(f"[udp] Recebi o pacote {seq}, "  +
              f"deveria ser entre {proximo_idx} "+
              f"e {proximo_idx + WINDOW_SIZE}")
        
        # Se o pacote estiver dentro da janela, aceitá-lo
        if (seq >= proximo_idx and seq <= proximo_idx+WINDOW_SIZE):
            # Guarda o pacote na posição correspondente e envia o ACK
            fAssembler.pkts[seq] = data
            fAssembler.ack[seq] = True
            print(f"[udp] Acknowledge do pacote {seq}")
            client.sendall(ack_encode(seq))
            if (seq == proximo_idx):
                # Escreve esse pacote e avança início da janela
                print(f"[udp] Janela avança uma posição")
                fAssembler.assemblePacket(seq)
                proximo_idx += 1
        
        # Verifica se todos os pacotes já chegaram
        print(f"[log] Recebeu todos? {all(p for p in fAssembler.ack)}")
        if all(p for p in fAssembler.ack):
            # Já recebeu todos, podemos sair do loop
            break
    
    # Tratamento de casos especiais finais
    if (len(pkts) == 0):
        # Edge-case: arquivo vazio
        fAssembler.assemblePacket(None)
    else:
        # Remontar pacotes restantes, caso haja
        fAssembler.assembleRemaining()

def handleFile(infoFileMsg, client, infoClient, udtS):
    """
    Consegue informações do arquivo a ser recebido, aloca estruturas necessárias
    para isso, recebe o arquivo via janela deslizante e finaliza a conexão
    """
    # Decodifica info_file
    nome, tam = info_file_decode(infoFileMsg)
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
    
    # Janela deslizante para receber os pacotes
    slidingWindow(client, udtS, pkts, f)
    print("[log] Arquivo recebido por completo")
    print(f"[log] Arquivo {f.nome_arq} disponível em disco")

    # Encerrar conexão com cliente
    print("[log] Enviando mensagem de fim")
    client.sendall(fim_encode())
    
    print(f"[log] Encerrando conexões com {infoClient[0]}: {infoClient[1]}")
    udtS.close()
    client.close()

def multi_threaded_client(client, server):
    """
    Thread de um cliente
    """
    infoClient = client.getsockname()
    infoServer = server.getsockname()
    
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
            print(f"[log] \tTipo da mensagem: {msgId(data)}")
            if (msgId(data) == 1):
                # Recebeu mensagem Hello, vamos estabelecer conexão UDP
                udtS = establishUDP(client, infoServer)
            elif (msgId(data) == 3):
                # Recebeu mensagem info_file, temos que confirmar e começar a 
                # receber o arquivo
                handleFile(infoFileMsg=data, 
                           client=client, 
                           infoClient=infoClient, 
                           udtS=udtS)
                # Recebido o arquivo, podemos parar de receber mensagens
                break
            else:
                logexit("Mensagem Inválida!")
    # Recebido o arquivo, podemos encerrar a conexão desse cliente
    client.close()

def main():
    # Parse dos argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("porta", help="Porta do servidor", type=int)
    parser.add_argument("-v","--version", 
                        help="Versão do IP do servidor", default="v6")
    args = parser.parse_args()
    
    # Inicialização do Servidor
    if (args.version == "v4"):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif (args.version == "v6"):
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY, 0)
        
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
        # Conecta com cliente
        Client, address = server.accept()
        print('[log] Conexão com sucesso: '+ address[0] 
              + ':' + str(address[1]))
        cltT = Thread(target=multi_threaded_client, args=(Client, server))
        cltT.start()
        ThreadCount += 1
    print("[log] Finalizando servidor")
    server.close()


if __name__ == "__main__":
    main()
