import pytest
import binascii
import common

class Test01:
    def test_msgId(self):
        assert common.msgId(common.hello_encode()) == 1
        assert common.msgId(common.connection_encode(40532)) == 2

class TestHello:
    def test_hello_msg(self):
        ba = bytearray()
        i = 1
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        assert ba == common.hello_encode()
    
    def test_hello_decode(self):
        common.hello_decode(common.hello_encode())
        with pytest.raises(Exception) as e_info:
            ba = bytearray()
            i = 80
            ba.extend(i.to_bytes(length=2, byteorder='big'))
            common.hello_decode(ba)
    
class TestConnection:
    def test_connection_msg(self):
        ba = bytearray()
        i = 2
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        i = 40214
        ba.extend(i.to_bytes(length=4, byteorder='big'))
        assert ba == common.connection_encode(40214)
    
    def test_connection_msg_error(self):
        with pytest.raises(Exception) as e_info:
            common.connection_encode(-20)
    
    def test_connection_decode(self):
        msg = common.connection_encode(40214)
        assert common.connection_decode(msg) == 40214

class TestInfoFile:
    def test_info_file_encode(self):
        # Id da mensagem
        ba = bytearray()
        i = 3
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        
        # Nome do arquivo (máximo 15 bytes)
        string = "teste1.txt"
        b_str = string.encode("ascii")
        print (len(b_str))
        
        # Completa com zeros até 15 bytes
        filler = bytearray(common.MAX_FILENAME_SIZE - len(b_str))
        ba.extend(filler)
        ba.extend(b_str)
        
        # Coloca o tamanho do arquivo
        tam = 135
        ba.extend(tam.to_bytes(length=8, byteorder='big'))
        
        # print(len(ba))
        # print(binascii.hexlify(ba,","))
        assert ba == common.info_file_encode("teste1.txt",135)
    
    def test_info_file_encode_without_filler(self):
        # Id da mensagem
        ba = bytearray()
        i = 3
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        
        # Nome do arquivo (máximo 15 bytes)
        string = "nomemtlongo.txt"
        b_str = string.encode("ascii")
        print (len(b_str))
        
        # Completa com zeros até 15 bytes
        # filler = bytearray(common.MAX_FILENAME_SIZE - len(b_str))
        # ba.extend(filler)
        ba.extend(b_str)
        
        # Coloca o tamanho do arquivo
        tam = 2200
        ba.extend(tam.to_bytes(length=8, byteorder='big'))
                
        # print(len(ba))
        # print(binascii.hexlify(ba,","))
        assert ba == common.info_file_encode("nomemtlongo.txt",2200)
    
    def test_info_file_encode_name_too_big(self):
        with pytest.raises(Exception) as e_info:
            common.info_file_encode("nomemtlongo1.txt",2200)
    
    def test_info_file_decode(self):
        assert common.info_file_decode(
                    common.info_file_encode("teste1.txt",135)
                ) \
                == ("teste1.txt",135)
        assert common.info_file_decode(
                    common.info_file_encode("nomemtlongo.txt",2200)
                ) \
                == ("nomemtlongo.txt",2200)
        