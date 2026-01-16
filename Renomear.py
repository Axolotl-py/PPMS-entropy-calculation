import os
diretorio = "/home/gabriel/Documentos/IC/Medidas/PPMS/S1/Concerto (cópia)"
arquivos = os.listdir(diretorio)

for arquivo in arquivos:
    if "_corrigido.txt" in arquivo:
        nome_novo = arquivo.replace("_corrigido.txt", ".txt")
        caminho_antigo = os.path.join(diretorio, arquivo)
        caminho_novo = os.path.join(diretorio, nome_novo)
        os.rename(caminho_antigo, caminho_novo)
        print(f"Renomeado: {arquivo} -> {nome_novo}")