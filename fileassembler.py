import os
from pathlib import Path

from common import MAX_PAYLOAD_SIZE, WINDOW_SIZE, msgId


class FileAssembler:
    def __init__(self, nome_arq, qtd_pkts=0, pkts=None):
        self.nome_arq = nome_arq
        self.outputFolder = "output"
        self.pkts = [None for _ in range(qtd_pkts)] or pkts
        self.sent = [False for _ in range(qtd_pkts)]
        self.ack = [False for _ in range(qtd_pkts)]
        
    
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
    
    def assemblePacket(self, idx):
        """
        Remonta pacote de índice 'idx' do arquivo. O arquivo de saída tem nome 
        passado para o construtor e estará dentro da pasta 'output'.
        """
        Path(self.outputFolder).mkdir(exist_ok=True)
        if (idx == None):
            #Edge-case: arquivo vazio
            with open(self.outputFolder + "/" + self.nome_arq,'ab') as file:
                pass
            return
        if (idx > 0):
            size = os.path.getsize(self.outputFolder + "/" + self.nome_arq)
            print(f"[log] Arquivo possui {size}, sendo que deveria ter {idx*MAX_PAYLOAD_SIZE}")
            assert size == idx*MAX_PAYLOAD_SIZE
        with open(self.outputFolder + "/" + self.nome_arq,'ab') as file:
            print(f"[log] Remontando arquivo com pacote de índice {idx}")
            msg = self.pkts[idx]
            (seq, size, pl) = self.file_pkt_decode(msg)
            assert seq == idx
            file.write(pl)
            
        
    def assembleFile(self, idx=0):
        """
        Remonta o arquivo que está dividido em pacotes do tipo File, a partir
        do índice 'idx' (default 0). O arquivo de saída tem nome passado para o 
        construtor e estará dentro da pasta 'output'.
        
        """
        Path(self.outputFolder).mkdir(exist_ok=True)
        i = 0
        with open(self.outputFolder + "/" + self.nome_arq,'wb') as file:
            while (i < idx):
                file.seek(MAX_PAYLOAD_SIZE, 1)
                i += 1
            print(f"[log] Remontando arquivo a partir do índice {idx}")
            # i = idx
            while (i < idx+WINDOW_SIZE and i < len(self.pkts)):
                msg = self.pkts[i]
                (seq, size, pl) = self.file_pkt_decode(msg)
                assert seq == i
                file.write(pl)
                i += 1
                
