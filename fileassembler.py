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
        """
        Remonta o arquivo que está dividido em pacotes do tipo File, passados
        para o construtor. O arquivo de saída tem nome passado para o construtor
        """
        with open(self.nome_arq,'wb') as file:
            for i in range(len(self.pkts)):
                msg = self.pkts[i]
                (seq, size, pl) = self.file_pkt_decode(msg)
                
                assert seq == i
                file.write(pl)
