from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import date, timedelta
import pdfplumber
from pdfplumber.page import Page
import os
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd

from modules.buscador import coletarDadosCTE, DadosCTE
from modules.utils import unir_pdfs


PAGE_MAX_X = 595
PAGE_MAX_Y = 841

LABELSIZE_X = 217
LABELSIZE_Y = 78

prazoVencimento = 11


def whitespaceFinder(page: Page) -> tuple[int, int, int, int] | None:
        
    for y in range(int(PAGE_MAX_Y) - LABELSIZE_Y - 45, 5, -10):
        for x in range(30, int(PAGE_MAX_X), 10):
            
            x2 = x + LABELSIZE_X
            y2 = y + LABELSIZE_Y
            
            if x2 <= PAGE_MAX_X - 5 and y2 <= PAGE_MAX_Y - 6:
                
                cropped_page = page.crop((x, y, x2, y2))

                cropped_text = cropped_page.extract_text()
                
                if cropped_text == "":
                    return x, y, x2, y2


def transposeOrigin_bottom(x:int, y:int) -> tuple[int, int]:
    return x, PAGE_MAX_Y - y

def overlayPdfs(path_pdfBase, indexBase, path_pdfSecundario, indexSecundario, path_saida):
    
    output = PdfWriter()

    with open(path_pdfBase, 'rb') as file:
        pdf = PdfReader(file)

        with open(path_pdfSecundario, 'rb') as labelFile:
            text_pdf = PdfReader(labelFile)

            pag_pdf = pdf.pages[indexBase]
            pag_labelfile = text_pdf.pages[indexSecundario]

            pag_pdf.merge_page(pag_labelfile)
            output.add_page(pag_pdf)

            with open(path_saida, "wb") as out_pdf:
                output.write(out_pdf)

def gerar_labelPdf(x:int, y:int, signer:str, processo:str, emissao:str, final_cnpj, codServ, output_path):
    
    labelWidth = LABELSIZE_X
    
    if not signer.upper() in ['M', 'G', 'K']:
        labelWidth = 115
    
    if emissao != "NA":  
        emissaoDate = date.strptime(emissao, '%d/%m/%Y')
    else:
        emissaoDate = "NA"
    
    x, y = transposeOrigin_bottom(x, y)
    
    c = canvas.Canvas(output_path, pagesize=A4)
    
    
    c.setFillColorRGB(0.90, 0.90, 0.90)
    c.roundRect(x, y, labelWidth, -LABELSIZE_Y, radius=5, stroke=0, fill=1)
    
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica', 8)
    
    def cria_linha(lateral, altura, txt, linha=1):
        if linha > 0: 
            linha-= 1 # linha--
            
        cord_altura = altura - 10 * linha

        c.drawString(lateral + 5, cord_altura - 10, txt)
    
    data_vencimento = "__/__/____"
    
    if emissaoDate != "NA":
        vencimento = emissaoDate + timedelta(days=prazoVencimento)
        data_vencimento = vencimento.strftime('%d/%m/%Y')
    
    ic = "_____"
    if final_cnpj != "NA":
        match final_cnpj:
            case "0001-08":
                ic = 10501

            case "0002-80":
                ic = 10401

            case "0043-59":
                ic = 11401

            case "0045-10":
                ic = 11403

            case "0044-30":
                ic = 11404
                
    if processo == "NA":
        processo = "________"
    
    cria_linha(x, y, f'Processo: {processo}', 1)
    cria_linha(x, y, 'CC: 231219', 2)
    cria_linha(x, y, 'Nat: 202004', 3)
    cria_linha(x, y, 'Ct. Contábil: 3310102099', 4)
    cria_linha(x, y, f'IC: {ic}', 5)
    cria_linha(x, y, f'Cód.: {codServ}', 6)
    cria_linha(x, y, f'Pagamento após: {data_vencimento}', 7)
    

    if signer.upper() == 'G':
        cria_linha(x+110, y, 'Gustavo Carvalho Daquano', 6)
        cria_linha(x+110, y, '       Export Supervisor', 7)

    elif signer.upper() == 'M':
        cria_linha(x+110, y, 'Michelle Corrêa Lisboa', 6)
        cria_linha(x+110, y, '      Export Manager', 7)
        
    elif signer.upper() == 'K':
        cria_linha(x+110, y, 'Kendi Leal Okumura', 6)
        cria_linha(x+110, y, '    Export Manager', 7)
    
    
    c.save()


def gerar_labelledPdf(file_path:str, assinante:str, pasta_etiquetas:str, pasta_nfs:str):
    filename = os.path.basename(file_path)
    
    with pdfplumber.open(file_path) as file:
        
        listaDadosCTEs:list[DadosCTE] = []
        
        dadosCTE = None
        for pageIndex, pag in enumerate(file.pages):
            txt = pag.extract_text()
            
            dadosCTE = coletarDadosCTE(txt)
            
            if dadosCTE.isCartaCorrecao:
                continue
            
            listaDadosCTEs.append(dadosCTE)
            
            if dadosCTE.processo == "NA":
                print(f'{filename}: página "{pageIndex+1}" faltando processo')
                dadosCTE.processo = input(f'Insira o processo (sempre com "-" e sem "/"): ')
            
            if dadosCTE.filialTomador == "NA":
                print(f'{filename}: página "{pageIndex+1}" faltando CNPJ GTF')
                dadosCTE.filialTomador = input(f'Insira o final do CNPJ (Após a "/") do arquivo "{filename}" na página "{pageIndex+1}": ')
            
            if dadosCTE.emissao == "NA":
                print(f'{filename}: página "{pageIndex+1}" faltando data emissão')
                dadosCTE.filialTomador = input(f'Insira a data de emissão (formato: dd/mm/aaaa): ')
            
            
            
            whitespaceCoordinates = whitespaceFinder(pag)
            
            if whitespaceCoordinates != None:
                x, y, x2, y2 = whitespaceCoordinates
                
                path_labelfile = f"{pasta_etiquetas}/Etiqueta ({filename[:-4]}) pag{pageIndex+1}.pdf"
                
                if not os.path.exists(path_labelfile):
                    gerar_labelPdf(x, y, assinante, dadosCTE.processo, dadosCTE.emissao, dadosCTE.filialTomador, dadosCTE.codServ, path_labelfile)
                
                path_labelledFile = f'{pasta_nfs}/{dadosCTE.processo}_DACTE-{dadosCTE.cte}.pdf'
                
                overlayPdfs(file_path, pageIndex, path_labelfile, 0, path_labelledFile)
                
                
            else:
                print(f'Não encontrado espaço no arquivo: {file_path}')
            
            
        
        return listaDadosCTEs


def gerar_pdf_e_relatorio(pdf_paths, assinante, arquivo_final):
    cacheDir = 'cache'
    pasta_etiquetas = f'{cacheDir}/etiquetas'
    pasta_nfs = f'{cacheDir}/pdfs_etiquetados'
    
    os.mkdir(cacheDir)
    os.mkdir(f'{cacheDir}/etiquetas')
    os.mkdir(f'{cacheDir}/pdfs_etiquetados')
    
    dadosDF = []
    
    for pdf in pdf_paths:
        dadosCTEs = gerar_labelledPdf(pdf, assinante, pasta_etiquetas, pasta_nfs)
        
        if dadosCTEs != []:
            for dado in dadosCTEs: dadosDF.append(dado) 
    
    unir_pdfs(pasta_nfs, arquivo_final)
    
    return pd.DataFrame(dadosDF)

