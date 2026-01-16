import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import smplotlib

def integral_trapezio(x, y):
    """Calcula a integral filtrando NaNs."""
    # Filtrar NaNs
    mask = ~np.isnan(y)
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 2:
        return 0.0
    
    # Calcular integral
    n = len(x_clean)
    integral = 0.0
    for i in range(n - 1):
        h = x_clean[i + 1] - x_clean[i]
        area = (y_clean[i] + y_clean[i + 1]) * h / 2.0
        integral += area
    
    return integral

def entropia_por_pares(integral1, integral2, delta_T):
    """Calcula ΔS com conversão correta de Oe para Tesla."""
    # μ₀ = 4π × 10⁻⁷ N/A²
    mu0 = 4 * np.pi * 1e-7
    
    # Converter Oe para Tesla: 1 Oe = 1e-4 T
    # E considerar que M está em emu/g = 1 A·m²/kg
    # Então ∫M dH (emu-Oe/g) = ∫M dH × 1e-4 (J/kg)
    
    delta_integral = (integral2 - integral1) * 1e-4  # Oe para Tesla
    delta_S = delta_integral / delta_T
    
    # As integrais individuais devem ser POSITIVAS
    # mas ΔS pode ser negativa se integral2 < integral1
    print(f"T1: {temp1}K, Integral: {integral1:.1f}")
    print(f"T2: {temp2}K, Integral: {integral2:.1f}") 
    print(f"ΔS = ({integral2:.1f} - {integral1:.1f}) / {delta_T} = {delta_S:.1f}")

    return delta_S

diretorio = "/home/gabriel/Documentos/IC/Medidas/PPMS/S1/Concerto (cópia)"

arquivos = os.listdir(diretorio)

arquivos = [f for f in arquivos if f.endswith(".txt")]
print(arquivos)

arquivos.sort(key=lambda x: int(re.search(r'_(\d+)k?\.txt$', x).group(1)))

print(arquivos)

entropias = []
temperaturas = []

for i in range(len(arquivos) - 1):
    arquivo1 = os.path.join(diretorio, arquivos[i])
    arquivo2 = os.path.join(diretorio, arquivos[i + 1])
    
    dados1 = pd.read_csv(arquivo1, sep='\t', header=None)
    dados2 = pd.read_csv(arquivo2, sep='\t', header=None)

    # Campo 1
    campo1 = dados1.iloc[:, 0].values
    magnetizacao1 = dados1.iloc[:, 1].values

    # Prevenção: inverter se estiver em ordem decrescente
    if campo1[-1] < campo1[0]:
        campo1 = campo1[::-1]
        magnetizacao1 = magnetizacao1[::-1]
        print(f"  Dados {arquivos[i]} invertidos para ordem crescente")

        # Agora fazer o corte normalmente
        idx_max1 = np.argmax(campo1)
        campo1 = campo1[6:idx_max1+1]
        magnetizacao1 = magnetizacao1[6:idx_max1+1]

        # Campo 2 (mesma lógica)
        campo2 = dados2.iloc[:, 0].values
        magnetizacao2 = dados2.iloc[:, 1].values

        if campo2[-1] < campo2[0]:
            campo2 = campo2[::-1]
            magnetizacao2 = magnetizacao2[::-1]
            print(f"  Dados {arquivos[i+1]} invertidos para ordem crescente")

        idx_max2 = np.argmax(campo2)
        campo2 = campo2[6:idx_max2+1]
        magnetizacao2 = magnetizacao2[6:idx_max2+1]

    integral1 = integral_trapezio(campo1, magnetizacao1)
    integral2 = integral_trapezio(campo2, magnetizacao2)
    
    temp1 = int(re.search(r'_(\d+)k?\.txt$', arquivos[i]).group(1))
    temp2 = int(re.search(r'_(\d+)k?\.txt$', arquivos[i + 1]).group(1))
    delta_T = temp2 - temp1

    print(f"\nCalculando ΔS entre {temp1}K e {temp2}K:")
    print("========================================")
    print(delta_T)

    delta_S = entropia_por_pares(integral1, integral2, delta_T)
    temperaturas.append(temp1)
    entropias.append(delta_S)

#entropias = -np.array(entropias)
print("Temperaturas (K):", temperaturas)
print("Entropias (J/kg·K):", entropias)
print(sum(entropias))

# Extrair o nome da amostra do primeiro arquivo
nome_amostra = arquivos[0].split('_')[0]  # Pega "Ni50Mn36Ni14" do arquivo "Ni50Mn36Ni14_229K.txt"

plt.figure(figsize=(15, 15))
plt.plot(temperaturas, entropias, marker='o', label=f'{nome_amostra}\nΔS total = {sum(entropias):.1f} J/kg·K')
plt.axhline(y=0, color='k', linestyle='--', linewidth=0.8)
plt.legend(fontsize=20)
plt.xlabel('Temperatura (K)', fontsize=20)
plt.ylabel(r"$ΔS_{M} (J·kg^{-1}·K^{-1})$", fontsize=20)
plt.savefig(os.path.join(diretorio, f'Entropia_{nome_amostra}.png'), dpi=300)
plt.show()
