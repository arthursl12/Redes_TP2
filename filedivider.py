import os

from common import MAX_PAYLOAD_SIZE, WINDOW_SIZE


class FileDivider:
    def __init__(self, nome_arq=None):
        if nome_arq is None:
            self.nome_arq = nome_arq
            self.pkts = []
            self.sent = []
            self.ack = []
        else:
            self.loadFile(nome_arq)

        
    def loadFile(self, nome_arq):
        self.nome_arq = nome_arq
        tam = os.path.getsize(nome_arq)
        qtd_pkts = tam//MAX_PAYLOAD_SIZE
        if (tam % MAX_PAYLOAD_SIZE != 0):
            qtd_pkts += 1
        self.pkts = [None for _ in range(qtd_pkts)]
        self.sent = [False for _ in range(qtd_pkts)]
        self.ack = [False for _ in range(qtd_pkts)]
    
    def file_pkt_encode(self, seq, payload):
        """
        Cria uma mensagem do tipo File: 
            2 bytes : representando o 6
            4 bytes: ordem do pacote na sequência (inteiro): (parâmetro passado)
            2 bytes : tamanho do payload a seguir, em bytes (número inteiro)
            Até 1000bytes: payload (parâmetro passado) 
        """
        ba = bytearray()
        i = 6
        ba.extend(i.to_bytes(length=2, byteorder='big'))    # Código pkt
        ba.extend(seq.to_bytes(length=4, byteorder='big'))  # Num. sequência
        
        pl_size = len(payload)
        assert pl_size <= MAX_PAYLOAD_SIZE
        assert type(payload) == bytearray
        ba.extend(pl_size.to_bytes(length=2, byteorder='big'))  # Size payload
        
        ba += payload       # Adiciona o payload
        return ba
    
    def loadPackets(self, idx=0):
        """
        Divide o arquivo com nome passado para o construtor em pacotes do tipo
        File. A lista de pacotes gerados, em ordem a partir de 'idx' (default 0)
        fica no atributo 'pkts' da classe.
        Gera pacotes a partir do índice 'idx' até 'idx'+tamanho da janela, os
        outros índices permanecem em 'None'
        """
        i = 0
        self.pkts = [None for _ in range(len(self.ack))]
        with open(self.nome_arq,'rb') as file:
            pl = file.read(MAX_PAYLOAD_SIZE)
            while (i != idx):
                pl = file.read(MAX_PAYLOAD_SIZE)
                i += 1
            
            if (pl is None):
                raise IndexError
            
            while (i <= idx+WINDOW_SIZE and i < len(self.ack)):
                pl = bytearray(pl)
                pkt = self.file_pkt_encode(i, pl)
                self.pkts[i] = pkt

                pl = file.read(MAX_PAYLOAD_SIZE)
                i += 1

    def getQtdPacotes(self):
        return len(self.ack)

    def __getitem__(self, key):
        if (key < 0):
            raise IndexError
        return self.pkts[key]
    
    # Getters/Setters de Flags
    def isAck(self, idx):
        if (idx < 0):
            raise IndexError
        return self.ack[idx]
    def setAck(self, idx, status):
        if (idx < 0):
            raise IndexError
        assert type(status) == bool
        self.ack[idx] = status
    def isSent(self, idx):
        if (idx < 0):
            raise IndexError
        return self.sent[idx]
    def setSent(self, idx, status):
        if (idx < 0):
            raise IndexError
        assert type(status) == bool
        self.sent[idx] = status

