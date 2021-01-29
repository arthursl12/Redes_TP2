### TODO: função/classe para remontar e testar se a divisão tá certa


class FileManager:
    
    
    def __init__(self, nome_arq, pkt_max_size):
        self.nome_arq = nome_arq
        self.pkt_max_size = pkt_max_size
        self.pkts = []
        self.sent = []
        self.ack = []
    
