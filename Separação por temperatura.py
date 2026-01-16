import os
import pandas as pd
import re
import numpy as np

######INPUTS######
diretorio = "/home/gabriel/Documentos/IC/Medidas/PPMS"
massa = 0.01372  # massa em gramas

#possiveis padrões:
#padrão = r"^[A-Z]\d[A-Z]{5}\.DAT$"
padrão = r"^S\d_MH\.DAT$" #S2_MH.DAT
#padrão = r"^[A-Z0-9]+MAGNET\d+\.DAT$"
##################

arquivos = [f for f in os.listdir(diretorio) if re.match(padrão, f)]

for nome_arquivo in arquivos:
    nome_diretorio = nome_arquivo[:-4]  # Remove .DAT
    saida = os.path.join(diretorio, nome_diretorio)
    os.makedirs(saida, exist_ok=True)

    caminho_completo = os.path.join(diretorio, nome_arquivo)
    dados = pd.read_csv(caminho_completo, header=None, sep=",", skiprows=6)

    magnetização = dados.iloc[:,4].values.astype(float)
    temperatura = np.round(dados.iloc[:,2].values.astype(float))
    campo = dados.iloc[:,3].values.astype(float)

    temperaturas_unicas = np.unique(temperatura)

    print(temperaturas_unicas)

    for temp in temperaturas_unicas:
        indices_temp = np.where(temperatura == temp)[0]
        magnetização_temp = magnetização[indices_temp]
        ################################
        magnetização_temp = magnetização_temp/massa # Dividir pela massa em gramas
        ################################
        campo_temp = campo[indices_temp]

        # Usar nome da pasta no arquivo de saída
        nome_saida = f"{nome_arquivo[:-4]}_{int(temp)}K.txt"
        caminho_saida = os.path.join(saida, nome_saida)

        np.savetxt(caminho_saida, np.column_stack((campo_temp, magnetização_temp)), 
        fmt='%.6f', delimiter='\t', header='Campo\tMagnetizacao')