import pytest
from file import FileManager
import filecmp

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

class TestFileDivider:
    def setup_method(self):
        self.f = FileManager("ttAuto.txt")
        self.f.divideFile()
    
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
        self.f = FileManager("ttAuto.txt")
        self.f.divideFile()
        
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
        
    
    ### TODO: função/classe para remontar e testar se a divisão tá certa
"""
class TestFileAssembler:
    def setup_method(self):
        self.f = FileManager("ttAuto.txt", 1000)
        self.f.divideFile()
    
    def test_assembler(self):
        lst = []
        for i in range(self.f.getQtdPacotes()):
            lst.append(self.f[i])
        filename = assemblePackets(lst)
        assert filecmp(filename, "ttAuto.txt", shallow=False) == True

"""

class TestFileFlags:
    def setup_method(self):
        self.f = FileManager("ttLong.txt")
        self.f.divideFile()
    
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

"""
class TestThrowsGetters:
    def setup_method(self):
        self.f = FileManager("ttAuto.txt", 1000)
    
    def test_nothrow_get_item(self):
        for i in range(self.f.getQtdPacotes()):
            pkt = self.f[i]
        
        for i in range(self.f.getQtdPacotes()):
            self.f.setAck(i, False)
            
        for i in range(self.f.getQtdPacotes()):
            self.f.isAck(i)
                
        for i in range(self.f.getQtdPacotes()):
            self.f.sendFlag(i)
            
        for i in range(self.f.getQtdPacotes()):
            self.f.isAck(i)
            
        for i in range(self.f.getQtdPacotes()):
            self.f.isSentFlag(i)
    
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
            self.f.sendFlag(-1)
        with pytest.raises(Exception) as e_info:
            self.f.sendFlag(100000000000000000)
        
        # isSentFlag
        with pytest.raises(Exception) as e_info:
            self.f.isSentFlag(-1)
        with pytest.raises(Exception) as e_info:
            self.f.isSentFlag(100000000000000000)
"""