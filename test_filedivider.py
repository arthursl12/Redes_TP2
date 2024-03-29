import pytest
from filedivider import FileDivider
import filecmp

"""
Construtor: nome do arquivo,
dividefile: cria uma lista de pacotes
getQtdPacotes
Operador[]: acessa os pedaços (pacotes prontos)
setAck: setar o ack
isAck: dizer SE recebeu o ack
setSent: dizer que mandou (ou não)
isSent: dizer SE mandou
"""

class TestFileDivider:
    def setup_method(self):
        self.f = FileDivider("ttAuto.txt")
        self.f.loadPackets()
    
    def test_packet_size(self):
        for i in range(self.f.getQtdPacotes()-1):
            assert len(self.f[0] == 1008)
        i = self.f.getQtdPacotes()-1
        assert len(self.f[i]) <= 1008
    
    def test_packet_header(self):
        for k in range(self.f.getQtdPacotes()):
            ba = bytearray()
            i = 6
            ba.extend(i.to_bytes(length=2, byteorder='big'))
            i = k
            ba.extend(i.to_bytes(length=4, byteorder='big'))
            
            pkt = self.f[i]
            i = len(pkt) - 8
            ba.extend(i.to_bytes(length=2, byteorder='big'))
            assert ba == pkt[:8]
            
    def test_packet_maker(self):
        self.f = FileDivider("ttAuto.txt")
        self.f.loadPackets()
        
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
        pkt = self.f.file_pkt_encode(4,pl)
        
        # Pkt manual
        ba = bytearray()
        i = 6
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        i = 4
        ba.extend(i.to_bytes(length=4, byteorder='big'))
        pl_size = len(pl)
        ba.extend(pl_size.to_bytes(length=2, byteorder='big'))
        ba += pl
        assert len(ba) == 1008
        assert len(ba) == len(pkt)
        assert ba == pkt

class TestFileFlags:
    def setup_method(self):
        self.f = FileDivider("ttLong.txt")
        self.f.loadPackets()
    
    def test_is_ack(self):
        for i in range(self.f.getQtdPacotes()):
            assert self.f.isAck(i) == False
    
    def test_ack(self):
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                self.f.setAck(i, True)
            
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                assert self.f.isAck(i) == True
            else:
                assert self.f.isAck(i) == False
            
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                self.f.setAck(i, False)

        for i in range(self.f.getQtdPacotes()):
            assert self.f.isAck(i) == False
    def test_is_sent(self):
        for i in range(self.f.getQtdPacotes()):
            assert self.f.isSent(i) == False
    
    def test_sent(self):
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                self.f.setSent(i, True)
            
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                assert self.f.isSent(i) == True
            else:
                assert self.f.isSent(i) == False
            
        for i in range(self.f.getQtdPacotes()):
            if (i % 2 == 0):
                self.f.setSent(i, False)

        for i in range(self.f.getQtdPacotes()):
            assert self.f.isSent(i) == False


class TestThrowsGetters:
    def setup_method(self):
        self.f = FileDivider("ttAuto.txt")
        self.f.loadPackets()
    
    def test_nothrow_get_item(self):
        for i in range(self.f.getQtdPacotes()):
            pkt = self.f[i]
        
        for i in range(self.f.getQtdPacotes()):
            self.f.setAck(i, False)
            
        for i in range(self.f.getQtdPacotes()):
            self.f.isAck(i)
                
        for i in range(self.f.getQtdPacotes()):
            self.f.isSent(i)
            
        for i in range(self.f.getQtdPacotes()):
            self.f.setSent(i,False)
    
    def test_throws_gets(self):    
        # Operador []
        with pytest.raises(Exception) as e_info:
            self.f[-1]
        with pytest.raises(Exception) as e_info:
            self.f[100000000000000000]
        
        # setAck
        with pytest.raises(Exception) as e_info:
            self.f.setAck(-1, True)
        with pytest.raises(Exception) as e_info:
            self.f.setAck(100000000000000000, True)
        
        # isAck
        with pytest.raises(Exception) as e_info:
            self.f.isAck(-1)
        with pytest.raises(Exception) as e_info:
            self.f.isAck(100000000000000000)
        
        # SendFlag
        with pytest.raises(Exception) as e_info:
            self.f.isSent(-1)
        with pytest.raises(Exception) as e_info:
            self.f.isSent(100000000000000000)
        
        # isSentFlag
        with pytest.raises(Exception) as e_info:
            self.f.setSent(-1, False)
        with pytest.raises(Exception) as e_info:
            self.f.setSent(100000000000000000, True)
