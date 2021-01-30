### TODO: função/classe para remontar e testar se a divisão tá certa
from common import MAX_PAYLOAD_SIZE

class FileManager:
    def __init__(self, nome_arq):
        self.nome_arq = nome_arq
        self.pkt_max_size = MAX_PAYLOAD_SIZE
        self.pkts = []
        self.sent = []
        self.ack = []
    
    def file_pkt_encode(self, seq, payload):
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
    
    def divideFile(self):
        with open(self.nome_arq,'rb') as file:
            pl = file.read(MAX_PAYLOAD_SIZE)
            seq = 0
            while pl:
                pl = bytearray(pl)
                pkt = self.file_pkt_encode(seq, pl)
                self.pkts.append(pkt)
                self.sent.append(False)
                self.ack.append(False)
                
                seq += 1
                pl = file.read(MAX_PAYLOAD_SIZE)

    def getQtdPacotes(self):
        return len(self.pkts)

    def __getitem__(self, key):
        return self.pkts[key]
    
    # Getters/Setters de Flags
    def isAck(self, idx):
        return self.ack[idx]
    def setAck(self, idx, status):
        assert type(status) == bool
        self.ack[idx] = status
    def isSent(self, idx):
        return self.sent[idx]
    def setSent(self, idx, status):
        assert type(status) == bool
        self.sent[idx] = status