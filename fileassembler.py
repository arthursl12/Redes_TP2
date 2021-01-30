### TODO: função/classe para remontar e testar se a divisão tá certa
from common import MAX_PAYLOAD_SIZE, msgId

class FileAssembler:
    def __init__(self, nome_arq, pkts):
        self.nome_arq = nome_arq
        self.pkts = pkts
    
    def file_pkt_decode(self, msg):
        """
        Decodifica uma mensagem em binário do tipo File.
        Retorna uma tupla com o índice desse pacote (inteiro), o tamanho do 
        payload (inteiro) e o payload em um bytearray
        """
        assert msgId(msg) == 6
        assert len(msg) <= MAX_PAYLOAD_SIZE + 8
        
        b_seq = msg[2:6]
        seq = int.from_bytes(b_seq, "big")
        
        b_size = msg[6:8]
        size = int.from_bytes(b_size, "big")
        
        assert size == len(msg) - 8
        assert size <= MAX_PAYLOAD_SIZE
        
        payload = msg[8:size+8]
        
        return (seq, size, payload)
    
    def assembleFile(self):
        with open(self.nome_arq,'wb') as file:
            for i in range(len(self.pkts)):
                msg = self.pkts[i]
                (seq, size, pl) = self.file_pkt_decode(msg)
                
                assert seq == i
                file.write(pl)
        #     pl = file.read(MAX_PAYLOAD_SIZE)
        #     seq = 0
        #     while pl:
        #         pl = bytearray(pl)
        #         pkt = self.file_pkt_encode(seq, pl)
        #         self.pkts.append(pkt)
        #         self.sent.append(False)
        #         self.ack.append(False)
                
        #         seq += 1
        #         pl = file.read(MAX_PAYLOAD_SIZE)

