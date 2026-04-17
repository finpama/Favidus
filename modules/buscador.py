import re
from dataclasses import dataclass
from typing import Any


@dataclass
class DadosCTE:
    isCartaCorrecao: bool
    processo: Any = 'NA'
    cte: Any = 'NA'
    fornecedor: Any = 'NA'
    valor: Any = 'NA'
    emissao: Any = 'NA'
    codServ: Any = 'NA'
    filialTomador: Any = 'NA'
    nomeRecebedorDestinatario: Any = 'NA'


def coletarDadosCTE(pageText: str) -> DadosCTE:
    
    padrao_cartaCorreção = r"\b(Carta de Correção Eletrônica)\b"
    match_cartaCorreção = re.search(padrao_cartaCorreção, pageText)
    
    if match_cartaCorreção != None:
        return DadosCTE(isCartaCorrecao=True)
    
    padroes_processo = [
            r"\b(\d{5}[\/-]\d{2}[a-zA-Z])\b",
            r"\b(C\d{3}[\/-]\d{2}[a-zA-Z])\b",
            r"\b(\d{5}[\/-]\d{2})\b",
            r"\b(C\d{3}[\/-]\d{2})\b",
        ]
    
    padrao_cte = r"NÚMERO[^\d]*?(\d{4,7})"
    padrao_valor = r"VALOR TOTAL DO SERVIÇO\n.*?([\d,.]{4,})\n"
    padrao_emissao = r"EMISSÃO[\w\W]*?(\d{2}/\d{2}/\d{4})"
    padrao_filialTomador = r"TOMADOR[\w\W]*?85\.070\.068\/(\d{4}-\d{2})"
    padrao_nomeRecebedor = r"RECEBEDOR.*?(\w+)"
    padrao_nomeDestinatario = r"DESTINATÁRIO.*?(\w+)"
    
    match_processo = None
    for padrao in padroes_processo:
        match_processo = re.search(padrao, pageText)
        if match_processo != None: break
    
    match_cte = re.search(padrao_cte, pageText)
    match_valor = re.search(padrao_valor, pageText)
    match_emissao = re.search(padrao_emissao, pageText)
    match_filialTomador = re.search(padrao_filialTomador, pageText)
    match_nomeRecebedor = re.search(padrao_nomeRecebedor, pageText)
    match_nomeDestinatario = re.search(padrao_nomeDestinatario, pageText)
    
    
    processo = match_processo.group(1) if match_processo != None else 'NA'
    cte = match_cte.group(1) if match_cte != None else 'NA'
    valor = match_valor.group(1) if match_valor != None else 'NA'
    emissao = match_emissao.group(1) if match_emissao != None else 'NA'
    filialTomador = match_filialTomador.group(1) if match_filialTomador != None else 'NA'
    nomeRecebedor = match_nomeRecebedor.group(1) if match_nomeRecebedor != None else 'NA'
    nomeDestinatario = match_nomeDestinatario.group(1) if match_nomeDestinatario != None else 'NA'
    
    if nomeRecebedor != "NA":
        recebedorDestinatario = nomeRecebedor
    else:
        recebedorDestinatario = nomeDestinatario
    
    if recebedorDestinatario == "GONCALVES":
        codServ = 'SERV000326'
    else:
        codServ = 'SERV000358'
    
    dados = DadosCTE(
        False,
        processo.replace('/', '-'),
        cte,
        'Avidus',
        valor,
        emissao,
        codServ,
        filialTomador,
        recebedorDestinatario
    )
    
    return dados

