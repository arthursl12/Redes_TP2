import pytest
import binascii
import common

class Test01:
    # def test_msgId(self):
    #     ba = bytearray()
    #     i = 332005
    #     ba.extend(i.to_bytes(length=5, byteorder='big'))
    #     msg1 = bytearray(2)
    #     print (binascii.hexlify(ba,sep=","))
    #     print (len(ba))
    #     print (binascii.hexlify(ba[:3],sep=","))
        
    #     assert common.msgId(ba) == 1
        
    def test_hello_msg(self):
        ba = bytearray()
        i = 1
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        assert ba == common.hello()
    
    def test_connection_msg(self):
        ba = bytearray()
        i = 2
        ba.extend(i.to_bytes(length=2, byteorder='big'))
        i = 40214
        ba.extend(i.to_bytes(length=4, byteorder='big'))
        assert ba == common.connection(40214)
    
    def test_connection_msg_error(self):
        with pytest.raises(Exception) as e_info:
            common.connection(-20)