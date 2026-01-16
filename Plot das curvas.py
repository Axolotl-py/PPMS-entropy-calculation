import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt

diretorio = "/home/gabriel/Documentos/IC/Medidas/PPMS/S1/Concerto (cópia)"

arquivos = os.listdir(diretorio)
arquivos = [f for f in arquivos if f.endswith(".txt")]
print("Arquivos encontrados:", arquivos)

# Padrão mais flexível - aceita K ou k e números com ou sem zeros
arquivos.sort(key=lambda x: int(re.search(r'_(\d+)k?\.txt$', x, re.IGNORECASE).group(1)))

print("Arquivos ordenados:", arquivos)

# Extrair nome da amostra
nome_amostra = arquivos[0].split('_')[0]  # "S1"

fig, ax = plt.subplots(figsize=(15, 12))

for arquivo in arquivos:
    temp = int(re.search(r'_(\d+)k?\.txt$', arquivo, re.IGNORECASE).group(1))
    caminho = os.path.join(diretorio, arquivo)
    
    # Ler o arquivo manualmente e processar
    with open(caminho, 'r') as f:
        linhas = f.readlines()
    
    campos = []
    magnetizacoes = []
    
    for linha in linhas:
        # Dividir por qualquer quantidade de tabs ou espaços
        partes = re.split(r'\t+', linha.strip())
        # Filtrar partes vazias
        partes = [p for p in partes if p]
        
        if len(partes) >= 2:  # Pelo menos campo e magnetização
            try:
                campo_val = float(partes[0].replace(',', '.'))
                mag_val = float(partes[1].replace(',', '.'))
                campos.append(campo_val)
                magnetizacoes.append(mag_val)
            except ValueError:
                continue  # Pula linhas que não podem ser convertidas
    
    if len(campos) == 0:
        print(f"Arquivo {arquivo} não tem dados válidos")
        continue
    
    campo = np.array(campos)
    magnetizacao = np.array(magnetizacoes)
    
    print(f"\nArquivo: {arquivo}")
    print(f"Pontos: {len(campo)}")
    print(f"Campo range: {campo[0]:.1f} -> {campo[-1]:.1f}")
    print(f"Magnetização range: {magnetizacao[0]:.3f} -> {magnetizacao[-1]:.3f}")
    
    # Verificar se precisa inverter (se termina com campo baixo)
    if campo[-1] < campo[0]:
        campo = campo[::-1]
        magnetizacao = magnetizacao[::-1]
        print("Dados invertidos para ordem crescente")
    
    # Encontrar temperatura min e max para a colorbar
    if 'temps' not in locals():
        temps = [int(re.search(r'_(\d+)k?\.txt$', f, re.IGNORECASE).group(1)) for f in arquivos]
        temp_min, temp_max = min(temps), max(temps)
    
    # Cor baseada na temperatura
    cor = plt.cm.plasma((temp - temp_min) / (temp_max - temp_min))
    ax.plot(campo, magnetizacao, color=cor, alpha=0.7)

ax.set_xlabel('H (Oe)', fontsize=12)
ax.set_ylabel('M/g (emu/g)', fontsize=12)
ax.set_title(f'Amostra: {nome_amostra}', fontsize=14)
ax.grid(True, alpha=0.3)

# Criar colorbar corretamente
sm = plt.cm.ScalarMappable(cmap='plasma', norm=plt.Normalize(vmin=temp_min, vmax=temp_max))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, label='Temperatura (K)')

plt.tight_layout()
plt.savefig(os.path.join(diretorio, f'Plot_MxH_{nome_amostra}.png'), dpi=300)
plt.show()