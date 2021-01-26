
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

def msgId(b_msg):
    '''
    Dada uma mensagem em bytes 'b_msg', retorna o inteiro referente à qual tipo 
    de mensagem ela é. 

    Isso é representado pelos dois primeiros bytes da mensagem.
    O código correspondente da cada mensagem está na especificação
    '''
    pass

def hello():
    """
    Cria uma mensagem do tipo Hello: apenas 2 bytes, representando o 1
    """
    ba = bytearray()
    i = 1
    ba.extend(i.to_bytes(length=2, byteorder='big'))
    return ba


def connection(porta):
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