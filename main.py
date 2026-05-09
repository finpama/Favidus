
import os

from modules.reset import define_vazia
from modules.pdf import gerar_pdf_e_relatorio


define_vazia("cache")

pasta_leitor = './Leitor_NFs'
arquivo_final = 'arquivo_unificado.pdf'
relatorio = 'relatorio.xlsx'

if not os.path.exists(pasta_leitor):
    os.mkdir(pasta_leitor)

print('\nInsira o assinante... (OBS: Antes de seguir, certifique-se que todos os PDFs estão na pasta "Leitor")')
print('M: Michelle')
print('G: Gustavo')
print('K: Kendi')
print('Qualquer outro: Vazio')

assinante = input('\n> ')

files = os.listdir(pasta_leitor)
pdfs = [file for file in files if file.upper().endswith('.PDF')]
pdf_paths = [os.path.join(pasta_leitor, pdf) for pdf in pdfs]

df = gerar_pdf_e_relatorio(pdf_paths, assinante, arquivo_final)
    
try:
    df.drop('isCartaCorrecao', axis=1, inplace=True)
    df.to_excel(relatorio, index=False)
    print('O Relatório das CT-Es foi salvo com sucesso no arquivo "relatorio.xlsx"')
except PermissionError:
    raise PermissionError('Não foi possível alterar o relatório já existente pois o arquivo está aberto')