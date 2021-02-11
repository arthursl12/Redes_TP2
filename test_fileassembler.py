import pytest
from filedivider import FileDivider
from fileassembler import FileAssembler

"""
Construtor: nome do arquivo, tamanho máximo do payload
            cria uma lista de pacotes
getQtdPacotes
Operador[]: acessa os pedaços (pacotes prontos)
Ack: dizer que recebeu o ack
isAck: dizer SE recebeu o ack
SendFlag: dizer que mandou 
isSentFlag: dizer SE mandou
"""
class TestPacketDecoder:
    def setup_method(self):
        self.div = FileDivider("ttLong.txt")
        self.div.loadPackets()
        self.f = FileAssembler("resLong.txt", pkts=self.div.pkts)
        # self.f.assembleFile()
        
    def test_decoder(self):
        # Syntethic payload
        pl = bytearray()
        for k in range(1000):
            if (k < 300):
                i = 1
                pl.extend(i.to_bytes(length=1, byteorder='big'))
            else:
                i = 0
                pl.extend(i.to_bytes(length=1, byteorder='big'))
        assert len(pl) == 1000
        pkt0 = self.div.file_pkt_encode(0,pl)
        pkt1 = self.div.file_pkt_encode(1,pl)
        pkt2 = self.div.file_pkt_encode(2,pl)
        
        assert (0,1000,pl) == self.f.file_pkt_decode(pkt0)
        assert (1,1000,pl) == self.f.file_pkt_decode(pkt1)
        assert (2,1000,pl) == self.f.file_pkt_decode(pkt2)
        
        pl = bytearray()
        for k in range(359):
            if (k < 300):
                i = 1
                pl.extend(i.to_bytes(length=1, byteorder='big'))
            else:
                i = 0
                pl.extend(i.to_bytes(length=1, byteorder='big'))
        assert len(pl) == 359
        pkt3 = self.div.file_pkt_encode(3,pl)
        assert (3,359,pl) == self.f.file_pkt_decode(pkt3)
        
        
        
        

