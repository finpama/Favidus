import os

def limparPastaExixtente(parent:str):
    childs = os.listdir(parent)

    for child in childs:
        child_path = os.path.join(parent, child)
        
        if os.path.isfile(child_path):
            os.remove(child_path)
        else:
            limparPastaExixtente(child_path)
            os.rmdir(child_path)

def define_vazia(parent):
    if not os.path.exists(parent):
        os.mkdir(parent)
    else:
        limparPastaExixtente(parent)
