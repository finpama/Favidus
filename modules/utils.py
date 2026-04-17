
import pymupdf
import os


def unir_pdfs(directory_path, output_filename):
    'Une os pdfs na pasta *directory_path* para o arquivo *output_filename*'
    
    doc = pymupdf.open()

    files = os.listdir(directory_path)

    for file in files:
        file_path = os.path.join(directory_path, file)

        if not os.path.exists(file_path):
            print(f"Aviso: arquivo não encontrado: {file}")

            continue
        
        try:
            doc.insert_file(file_path)  
            
        except Exception as e:
            print(f"Não foi possível ler o arquivo {file}: {e}")
            
    try:
        doc.save(output_filename)
        doc.close()
    except pymupdf.mupdf.FzErrorSystem:
        raise pymupdf.mupdf.FzErrorSystem(f'Não será possível alterar "{output_filename}" pois o arquivo está aberto')
    
    print(f"\nTodos os {len(files)} CT-Es foram mesclados e estão no arquivo {output_filename}")

