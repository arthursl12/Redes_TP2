#!/usr/bin/env python3

import argparse
import os
import socket
import sys
import time
from threading import Thread

from common import (WINDOW_SIZE, ack_decode, connection_decode, fim_encode,
                    hello_encode, info_file_encode, msgId)
from filedivider import FileDivider

TIMEOUT_MAX = 0.5

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
f = FileDivider()
recebeu_Tudo = False

        
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
    tcp_socket.sendall(hello_encode())
    
    # Recebe a mensagem Connection do servidor, com o número da porta
    data = tcp_socket.recv(1024)
    data = bytearray(data)
    tipo = msgId(data)
    print(f"[log] \tTipo da mensagem: {tipo}")
    if (tipo != 2):
        logexit("Mensagem de Connection inválida")
    porta = connection_decode(data)
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
    filename = args.arquivo
    size = os.path.getsize(args.arquivo)
    try:
        tcp_socket.sendall(info_file_encode(filename,size))
    except Exception:
        logexit("Nome não permitido")
        
    
    # Recebe a mensagem de OK do servidor
    print("[log] Aguardando ok do servidor")
    data = tcp_socket.recv(1024)
    data = bytearray(data)
    tipo = msgId(data)
    print(f"[log] \tTipo da mensagem: {tipo}")
    if (tipo != 4):
        logexit("Mensagem de OK inválida")
    print("[log] Ok recebido")
    
    # Divide o arquivo em pacotes
    print(f"[log] Criando os pacotes do arquivo {args.arquivo}")
    f.loadFile(args.arquivo)
    f.loadPackets()
    print(f"[log] Foram criados {f.getQtdPacotes()} pacotes")
    
    global recebeu_Tudo
    def ack_thread(server):
        global recebeu_Tudo
        print("[log] Entrando na thread para receber ACK's")
        while(1):
            data = server.recv(6)
            if (len(data) == 0):
            	print("[log] Servidor encerrou a conexão")
            	break
            data = bytearray(data)
            tipo = msgId(data)
            if (tipo == 7):
                seq = ack_decode(data)
                print(f"[udp] Ack de {seq} recebido")
                f.setAck(seq, True)
                print(f"[udp] Status do pacote {seq} é recebido")
            elif (tipo == 5):
                print(f"[log] Mensagem de fim recebida")
                recebeu_Tudo = True
                print(f"[log] Recebeu tudo (thread)? {recebeu_Tudo}")
                break
            else:
                logexit("Mensagem inválida!")
        print("[log] Fim da thread de recebimento")

    
    # Cria a thread para receber os Acks do servidor
    ackT = Thread(target=ack_thread, args=(tcp_socket, ))
    ackT.start()
    
    # Janela deslizante pode começar
    win_base = 0
    n_pkts = f.getQtdPacotes()
    
    while ((win_base+WINDOW_SIZE-1) < n_pkts):
        f.loadPackets(win_base)
        # Enquanto houver pacotes a enviar
        print(f"[log] Enviando pacotes de {win_base} até {win_base+WINDOW_SIZE-1}")
        # Manda os pacotes dentro da janela para o servidor, via UDP
        for j in range(win_base, win_base+WINDOW_SIZE):
            udp_socket.sendto(f[j], (args.ip, porta))
            f.setSent(j, True)      # Marca cada um como enviado
        
        print(f"[log] Aguardando resposta ou timeout")
        time_start = time.time()
        agora = time.time()
        while(agora - time_start < TIMEOUT_MAX):
            # Enquanto não deu timeout
            time.sleep(1)
            if f.isAck(win_base):
                break
            agora = time.time()
        
        if f.isAck(win_base):
            # Servidor já confirmou o primeiro, podemos avançar a janela
            # e resetar o timer
            win_base += 1
            time_start = time.time()
        elif (agora - time_start > TIMEOUT_MAX):
            # Timeout: servidor não confirmou os pacotes a tempo
            print("[log] TIMEOUT: resetando timer e enviando novamente")
            for j in range(win_base, win_base+WINDOW_SIZE):
                f.setSent(j, False)      # Reseta status de enviado
            time_start = time.time()
            continue

    # enviouTudo = True
    # for k in range(f.getQtdPacotes()):
    #     enviouTudo = enviouTudo and f.isAck(k)
    
    if (not recebeu_Tudo):
        # Tratamento dos pacotes restantes (para os quais a janela é muito grande)
        idx_enviar = n_pkts - WINDOW_SIZE + 1 
        if n_pkts < WINDOW_SIZE: 
            idx_enviar = 0      # Se a janela for muito grande, comece a enviar do 0         
        time_start = time.time()
        while idx_enviar < n_pkts:
            # Enquanto não enviar todos 
            print(f"[log] Enviando pacotes de {idx_enviar} até {n_pkts-1}")
            
            # Envie todos pelo socket UDP
            for j in range(idx_enviar, n_pkts):
                # Manda os pacotes dentro da janela para o servidor, via UDP
                udp_socket.sendto(f[j], (args.ip, porta))
                f.setSent(j, True)      # Marca cada um como enviado

            print(f"[log] Aguardando resposta ou timeout")
            time_start = time.time()
            agora = time.time()
            while(agora - time_start < TIMEOUT_MAX):
                # Enquanto não deu timeout
                time.sleep(1)
                if f.isAck(win_base):
                    break
                agora = time.time()

            if f.isAck(idx_enviar):
                # Servidor já confirmou o primeiro, podemos "avançar a janela"
                # e resetar o timer
                idx_enviar += 1
                time_start = time.time()
            elif (agora - time_start > TIMEOUT_MAX):
                # Timeout: servidor não confirmou os pacotes a tempo
                print("[log] TIMEOUT: resetando timer e enviando novamente")
                for j in range(idx_enviar, n_pkts):
                    f.setSent(j, False)      # Reseta status de enviado
                time_start = time.time()
                continue
    ackT.join()
    if (n_pkts > 0):
    	assert recebeu_Tudo
    # print(f"[log] Recebeu tudo (fim)? {recebeu_Tudo}")
    print(f"[log] Fim do loop de envio")
    udp_socket.close()
    # print("[log] Enviando confirmação de fim")
    # tcp_socket.sendall(fim_encode())
    tcp_socket.close()
    

if __name__ == "__main__":
    main()
    print("[log] Cliente encerrado. Arquivo enviado.")
    
