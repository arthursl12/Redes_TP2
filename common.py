
'''
Mensagens e seus códigos:
Hello       1
Connection  2
Info file   3
OK          4
Fim         5
FILE        6
ACK         7
'''
MAX_FILENAME_SIZE = 15
WINDOW_SIZE = 5
MAX_PAYLOAD_SIZE = 1000

def msgId(b_msg):
    """
    Dada uma mensagem em bytes 'b_msg', retorna o inteiro referente à qual tipo 
    de mensagem ela é. 

    Isso é representado pelos dois primeiros bytes da mensagem.
    O código correspondente da cada mensagem está na especificação
    """
    assert type(b_msg) == bytearray
    assert len(b_msg) >= 2
    
    id = b_msg[:2]
    return int.from_bytes(id, "big")  

def hello_encode():
    """
    Cria uma mensagem do tipo Hello: apenas 2 bytes, representando o 1
    """
    ba = bytearray()
    i = 1
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    return ba

def hello_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo Hello.
    Verifica seu tamanho e id, levanta uma exceção se houver algo errado
    """
    assert msgId(msg) == 1
    assert len(msg) == 2

def connection_encode(porta):
    """
    Cria uma mensagem do tipo Connection: 
        2 bytes: representando o 2
        4 bytes: representando a porta UDP (número inteiro)
    """
    assert porta >= 0
    
    ba = bytearray()
    i = 2
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    ba.extend(porta.to_bytes(length=4, byteorder='big'))
    return ba

def connection_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo Connection, ou seja retorna o 
    inteiro referente à porta UDP na mensagem (4 bytes)
    """
    assert msgId(msg) == 2
    assert len(msg) == 6
    
    b_porta = msg[2:6]
    return int.from_bytes(b_porta, "big")  

def info_file_encode(nome_arq, size):
    """
    Cria uma mensagem do tipo Info File: 
        2 bytes : representando o 3
        15 bytes: nome do arquivo, incluindo extensão (string)
        8 bytes : tamanho do arquivo, em bytes (número inteiro)
    Nome com mais de 15 bytes levanta uma exceção
    """
    assert size >= 0
    
    # Id da mensagem
    ba = bytearray()
    i = 3
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    
    # Nome do arquivo (máximo 15 bytes)
    b_str = nome_arq.encode("ascii")
    print (len(b_str))
    
    # Completa com zeros até 15 bytes
    # Se o nome tiver mais de 15, levantará uma exceção
    filler = bytearray(MAX_FILENAME_SIZE - len(b_str))
    ba.extend(filler)
    ba.extend(b_str)
    
    # Coloca o tamanho do arquivo
    ba.extend(size.to_bytes(length=8, byteorder='big'))
    return ba

def info_file_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo Info File.
    Retorna uma tupla com o nome do arquivo (string) e o seu tamanho em bytes 
    (inteiro)
    """
    assert msgId(msg) == 3
    assert len(msg) == 25
    
    
    b_nome = msg[2:17]
    b_size = msg[17:25]
    
    nome = b_nome.decode("ascii")
    nome = nome.strip('\x00')       # Remove possíveis zeros à esquerda 
    tam = int.from_bytes(b_size, "big")
    return (nome, tam) 

def ok_encode():
    """
    Cria uma mensagem do tipo OK: apenas 2 bytes, representando o 4
    """
    ba = bytearray()
    i = 4
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    return ba

def ok_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo OK.
    Verifica seu tamanho e id, levanta uma exceção se houver algo errado
    """
    assert msgId(msg) == 4
    assert len(msg) == 2

def fim_encode():
    """
    Cria uma mensagem do tipo FIM: apenas 2 bytes, representando o 5
    """
    ba = bytearray()
    i = 5
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    return ba

def fim_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo FIM.
    Verifica seu tamanho e id, levanta uma exceção se houver algo errado
    """
    assert msgId(msg) == 5
    assert len(msg) == 2

def file_encode():
    pass
def file_decode():
    pass

def ack_encode():
    """
    Cria uma mensagem do tipo ACK: apenas 2 bytes, representando o 7
    """
    ba = bytearray()
    i = 7
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    return ba

def ack_decode(msg):
    """
    Decodifica uma mensagem em binário do tipo ACK.
    Verifica seu tamanho e id, levanta uma exceção se houver algo errado
    """
    assert msgId(msg) == 7
    assert len(msg) == 2