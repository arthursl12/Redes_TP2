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
QTD_MAX_TIMEOUTS = 5
f = FileDivider()
recebeu_Tudo = False
exc_timeouts = False

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

def argParse():
    """ Parse dos argumentos """
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="IP do servidor {v4|v6}")
    parser.add_argument("porta", help="Porta do servidor", type=int)
    parser.add_argument("arquivo", help="Arquivo a ser enviado")
    return parser.parse_args()

def connectTCP(ip, port):
    """ Conecta ao socket TCP do servidor """
    # Valida IPv4 ou IPv6 passado e usa a mesma versão
    if validIPv4(ip):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif validIPv6(ip):
        tcp_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
       logexit("Protocolo desconhecido")
       
    # Conecta com o servidor
    tcp_socket.connect((ip, port))
    infoServer = tcp_socket.getsockname()
    return tcp_socket, infoServer

def connectUDP(ip, serverIP):
    """ Conecta ao socket UDP do servidor """
    # Cria socket UDP
    if validIPv4(ip):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif validIPv6(ip):
        udp_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    else:
        logexit("Protocolo desconhecido")
    
    # Conecta ao socket UDP do servidor
    udp_socket.bind((serverIP,0)) 
    return udp_socket

def getPortUDP(tcp_socket):
    """ 
    Usa o protocolo definido na especificação para conseguir a porta UDP do 
    servidor, trocando mensagens de Hello e Connection
    """
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
    
    return porta

def infoFile(arquivo, tcp_socket):
    """ 
    Envia informações do arquivo ao servidor e aguarda confirmação dele para
    começar o processo de envio do arquivo.
    """
    # Envia a mensagem Info_file ao servidor, com o nome e tamanho do arquivo
    print("[log] Enviando info_file")
    filename = arquivo
    size = os.path.getsize(arquivo)
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

def prepareFile(arquivo):
    """
    Divide o arquivo em pacotes, usando o gerenciador 'FileDivider'. Essa classe
    auxiliará a janela deslizante
    """
    print(f"[log] Criando o gerenciador de pacotes do arquivo {arquivo}")
    f.loadFile(arquivo)
    f.loadPackets()
    print(f"[log] Serão criados {f.getQtdPacotes()} pacotes")
    print(f"[log] Os primeiros {WINDOW_SIZE} já foram criados")

def ack_thread(server):
    """
    Thread auxiliar para receber as mensagens de controle do servidor enquanto
    a janela deslizante é executada
    """
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
            break
        else:
            logexit("Mensagem inválida!")
    print("[log] Fim da thread de recebimento")

def slidingWindowRemaining(udp_socket, n_pkts, ip, porta, win_base):
    """
    Caso haja pacotes restantes a serem enviados, usa a janela deslizante para
    terminar de enviá-los
    """
    global exc_timeouts
    
    idx_enviar = n_pkts - WINDOW_SIZE + 1 
    if n_pkts < WINDOW_SIZE: 
        idx_enviar = 0      # Se a janela for muito grande, comece a enviar do 0         
    time_start = time.time()
    qtd_tos = 0             # Contar quantos timeouts numa mesma janela
    while idx_enviar < n_pkts:
        # Enquanto não enviar todos 
        print(f"[log][rem] Enviando pacotes de {idx_enviar} até {n_pkts-1}")
        
        # Envie todos pelo socket UDP
        for j in range(idx_enviar, n_pkts):
            # Manda os pacotes dentro da janela para o servidor, via UDP
            udp_socket.sendto(f[j], (ip, porta))
            f.setSent(j, True)      # Marca cada um como enviado

        print(f"[log][rem] Aguardando resposta ou timeout")
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
            # e resetar o timer e o contador de timeouts
            idx_enviar += 1
            time_start = time.time()
            qtd_tos = 0             
        elif (agora - time_start > TIMEOUT_MAX):
            # Timeout: servidor não confirmou os pacotes a tempo
            print("[log][rem] TIMEOUT: resetando timer e enviando novamente")
            for j in range(idx_enviar, n_pkts):
                f.setSent(j, False)      # Reseta status de enviado
            time_start = time.time()
            qtd_tos += 1
            continue
        elif (qtd_tos > QTD_MAX_TIMEOUTS):
            print("[log][rem] Tempo de timeouts excedido. Desconectando.")
            exc_timeouts = True
            

def slidingWindow(tcp_socket, udp_socket, ip, porta):
    """
    Faz a janela deslizante para enviar o arquivo ao servidor via o soquete UDP,
    cria uma thread para gerenciar as mensagens de controle que chegam pelo 
    soquete TCP
    """
    global recebeu_Tudo
    global exc_timeouts

    # Cria a thread para receber os Acks do servidor
    ackT = Thread(target=ack_thread, args=(tcp_socket, ))
    ackT.start()
    
    # Janela deslizante pode começar
    win_base = 0
    n_pkts = f.getQtdPacotes()
    qtd_tos = 0             # Contar quantos timeouts numa mesma janela
    
    while ((win_base+WINDOW_SIZE-1) < n_pkts):
        f.loadPackets(win_base)
        # Enquanto houver pacotes a enviar
        print(f"[log] Enviando pacotes de {win_base} até {win_base+WINDOW_SIZE-1}")
        # Manda os pacotes dentro da janela para o servidor, via UDP
        for j in range(win_base, win_base+WINDOW_SIZE):
            udp_socket.sendto(f[j], (ip, porta))
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
            qtd_tos = 0             
        
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
            qtd_tos += 1
            continue
        elif (qtd_tos > QTD_MAX_TIMEOUTS):
            print("[log][rem] Tempo de timeouts excedido. Desconectando.")
            exc_timeouts = True

    if (not recebeu_Tudo and not exc_timeouts):
        slidingWindowRemaining(udp_socket, n_pkts, ip, porta, win_base)
    elif (exc_timeouts):
        udp_socket.close()
        tcp_socket.close()
        print("[log] ERRO: Cliente encerrado. Arquivo não pôde ser enviado.")
        exit()
        
    # Aguarda a mensagem Fim chegar na outra thread e ela encerrar
    ackT.join()
    
    # Confere se realmente recebeu tudo
    if (n_pkts > 0):
    	assert recebeu_Tudo
    print(f"[log] Fim do loop de envio")

def main():
    args = argParse()
    
    tcp_socket, infoServer = connectTCP(args.ip, args.porta)
    porta = getPortUDP(tcp_socket)
    udp_socket = connectUDP(args.ip, infoServer[0])
    infoFile(arquivo=args.arquivo, tcp_socket=tcp_socket)
    prepareFile(arquivo=args.arquivo)
    slidingWindow(tcp_socket=tcp_socket, 
                  udp_socket=udp_socket, 
                  ip=args.ip, porta=porta)
    
    udp_socket.close()
    tcp_socket.close()
    print("[log] Cliente encerrado. Arquivo enviado.")
    

if __name__ == "__main__":
    main()
    
