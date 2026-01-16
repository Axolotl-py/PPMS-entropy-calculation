import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt

diretorio = "/home/gabriel/Documentos/IC/Medidas/dadosdasmedidasmxt/MAR7MTMAGNET1_00001"

#padrão = r"^dadosdasmedidasmxt_[A-Z]{3}\d[A-Z]{2}MAGNET\d_(\d+)_Oe\.txt$"
padrão = r"^dadosdasmedidasmxt_[A-Z]{3}\d[A-Z]{2}MAGNET\d_\d{5}_\d+_Oe\.txt$"
arquivos = [f for f in os.listdir(diretorio) if re.match(padrão, f)]
arquivos.sort(key=lambda x: int(re.search(r'_(\d+)_Oe\.txt$', x).group(1)))

print(arquivos)

nome_amostra = arquivos[0].split('_')[1]

# Estilos mais distintos
estilos = [
    '-',           # Sólida
    '--',          # Tracejada
    '-.',          # Traço-ponto
    ':',           # Pontilhada
    (0, (5, 5)),   # Espaçada
    (0, (3, 1, 1, 1)),  # Traço-duplo
    (0, (1, 5)),   # Pontos espaçados
    (0, (5, 1)),   # Traços longos
]

# Paleta de cores mais distinta
cores = [
    '#1f77b4',  # Azul
    '#ff7f0e',  # Laranja  
    '#2ca02c',  # Verde
    '#d62728',  # Vermelho
    '#9467bd',  # Roxo
    '#8c564b',  # Marrom
    '#e377c2',  # Rosa
    '#7f7f7f',  # Cinza
]

plt.figure(figsize=(13, 8))

for i, arquivo in enumerate(arquivos):
    campo_val = int(re.search(r'_(\d+)_Oe\.txt$', arquivo).group(1))
    caminho = os.path.join(diretorio, arquivo)
    dados = pd.read_csv(caminho, sep='\t', header=None, skiprows=1)
    
    temperatura = dados.iloc[:, 0].values
    magnetizacao = dados.iloc[:, 1].values
    
    # Garantir ordem crescente
    if temperatura[-1] < temperatura[0]:
        temperatura = temperatura[::-1]
        magnetizacao = magnetizacao[::-1]
    
    plt.plot(temperatura, magnetizacao, 
             label=f'{campo_val} Oe', 
             color=cores[i % len(cores)],
             linestyle=estilos[i % len(estilos)],
             linewidth=2.5,
             alpha=0.9)

plt.xlabel('Temperatura (K)', fontsize=14, fontweight='bold')
plt.ylabel('Magnetização (emu/g)', fontsize=14, fontweight='bold')
plt.title(f'Curvas M vs T - {nome_amostra}', fontsize=16, fontweight='bold', pad=20)

# Legenda organizada
plt.legend(bbox_to_anchor=(1.05, 1), 
           loc='upper left', 
           fontsize=11, 
           title='Campo Aplicado (Oe)', 
           title_fontsize=12,
           frameon=True,
           fancybox=True,
           shadow=True,
           ncol=1 if len(arquivos) <= 8 else 2)

plt.grid(True, alpha=0.2, linestyle='--')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(diretorio, f'Plot_MxT_estilos_{nome_amostra}.png'), 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()