import os
import re

def concerto(arquivo):
    print(f"Processando {arquivo}")
    saida = arquivo.replace(".txt", "_corrigido.txt")

    with open(arquivo, "r") as f:
        linhas = f.readlines()

    linhas_corrigidas = []
    #linhas_corrigidas.append("Campo(Oe)\tMagnetizacao(emu/g)")
    for linha in linhas:
        linha = linha.strip()
        
        quebrado = linha.split("\t")
        
        parte1 = quebrado[0].replace(",", ".")
        parte3 = quebrado[2].replace(",", ".")
        try:
            p1_float = float(parte1)
            p3_float = float(parte3)
            
            linha_corrigida = f"{float(parte1):.6f}\t{float(parte3):.6f}"
            linhas_corrigidas.append(linha_corrigida)
        except ValueError as e:
            print("Deu não")

    print(linhas_corrigidas)

    with open(saida, "w") as f:
        f.write("\n".join(linhas_corrigidas))

diretorio = "/home/gabriel/Documentos/IC/Medidas/PPMS/S1"
arquivos = os.listdir(diretorio)
arquivos = [f for f in arquivos if f.endswith(".txt")]
arquivos_filtrados = [
    f for f in arquivos 
    if re.search(r'^s1_\d+k\.txt$', f, re.IGNORECASE) and 'corrigido' not in f.lower()
]
print("Arquivos encontrados:", arquivos_filtrados)

# Padrão mais flexível - aceita K ou k e números com ou sem zeros
arquivos_filtrados.sort(key=lambda x: int(re.search(r'_(\d+)k?\.txt$', x, re.IGNORECASE).group(1)))

print("Arquivos ordenados:", arquivos_filtrados)

for arquivo in arquivos_filtrados:
    try:
        concerto(os.path.join(diretorio, arquivo))
    except:
        print("Num deu não")
