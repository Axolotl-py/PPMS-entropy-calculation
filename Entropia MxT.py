#Bibliotecas
import os
import pandas as pd
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline


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

def derivada_dM_dT(temperatura, magnetizacao, pontos=None):
    """Calcula dM/dT a campo constante"""
    spl = UnivariateSpline(temperatura, magnetizacao, s=len(temperatura)*1e-4)
    deriv_func = spl.derivative(n=1)
    
    if pontos is not None:
        return deriv_func(pontos)
    else:
        return deriv_func(temperatura)

def entropia_MxT(soma_total, dH):
    """Calcula ΔS(T) = 0.5 * [dM/dT|_H1 + dM/dT|_H2] * ΔH"""
    delta_S = 0.5 * (soma_total) * dH * 1e-3
    return delta_S

def arredondamento_inteiro(num,multiplo=500,torr=20):
    resto = num % multiplo
    if min(resto, multiplo - resto) <= torr:
        return round(num / multiplo) * multiplo
    return num

def arredondamento_array(arr, multiplo=500, torr=20):
    """Aplica arredondamento_inteiro em cada elemento do array"""
    return np.array([arredondamento_inteiro(x, multiplo, torr) for x in arr])

def separar_por_campo(arquivo,saida,nome_da_amostra,linhas_pular):
    controle = 0
    dados_por_campo = {}

    diferença = []
    caminho_arquivo = os.path.join(diretorio, arquivo)

    dados = pd.read_csv(caminho_arquivo, skiprows=linhas_pular)

    massa = np.mean(dados["Mass (grams)"]) * 1e-3
    print(f"Massa da amostra (g): {massa}")

    mag_norm = np.array(dados["Moment (emu)"])/massa #emu/g
    Temp = np.array(dados["Temperature (K)"])
    Campo = np.array(dados["Magnetic Field (Oe)"])

    Campo_round = arredondamento_array(np.round(Campo))
    campos_unicos = np.unique(Campo_round)

    print("Campos repetidos(Oe): ",campos_unicos)
    
    for i, H in enumerate(campos_unicos):

        if i < len(campos_unicos) - 1:

            diferença.append(campos_unicos[i+1] - campos_unicos[i])

        mask = Campo_round == H
        Temp_H = Temp[mask]
        mag_H = mag_norm[mask]
        
        #Filtrar somente o primeiro aquecimento
        dT = np.diff(Temp_H)

        idx = np.where(dT < 0)[0]

        if len(idx) > 0:
            corte = idx[0] + 1
            Temp_H = Temp_H[corte:]
            mag_H = mag_H[corte:]
        
        ponto_max_mag_H = np.argmax(mag_H)
        mag_H = mag_H[:ponto_max_mag_H+0]
        Temp_H = Temp_H[:ponto_max_mag_H+0]

        dados_por_campo[H] = (Temp_H, mag_H)
        if controle == 1:
            nome_arquivo_saida = f"{nome_da_amostra}_{int(H)}Oe.txt"
            caminho_saida = os.path.join(saida, nome_arquivo_saida)

            df_saida = pd.DataFrame({
                "Temperature (K)": Temp_H,
                "Magnetization (emu/g)": mag_H
            })
            df_saida.to_csv(caminho_saida, sep='\t', index=False)
            print(f"Arquivo salvo: {caminho_saida}")

    campos_ordenados = np.sort(list(dados_por_campo.keys()))

    return diferença, dados_por_campo, campos_ordenados
    
def plot_MxT(dados_por_campo,nome_da_amostra,saida):
    controle = 0
    #figura completa
    
    plt.figure()
    for H, (Temp_H, mag_H) in dados_por_campo.items():
        plt.plot(Temp_H, mag_H, "o", label=f'{int(H)} Oe')

    plt.xlabel('Temperatura (K)')
    plt.ylabel('Magnetização (emu/g)')
    plt.legend()
    plt.grid()
    if controle == 1:
        caminho_figura = os.path.join(saida, f"{nome_da_amostra}_MxT.png")
        plt.savefig(caminho_figura)
        plt.close()
        print(f"Figura salva: {caminho_figura}")
    plt.show()

def reconstruir_MxH(dados_por_campo, campos_ordenados, temperaturas):
    plt.figure(figsize=(6,5))

    for Tfix in temperaturas:
        M_vs_H = []

        for H in campos_ordenados:
            T, M = dados_por_campo[H]
            if Tfix < T.min() or Tfix > T.max():
                M_vs_H.append(np.nan)
            else:
                M_vs_H.append(np.interp(Tfix, T, M))

        plt.plot(campos_ordenados, M_vs_H, 'o-', label=f"{Tfix:.0f} K")

    plt.xlabel("Campo Magnético (Oe)")
    plt.ylabel("Magnetização (emu/g)")
    plt.title("Isotherms M × H (reconstruídas de M × T)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def calculo_da_entropia(dados_por_campo,campos_ordenados,diferença):
    delta_S_total = {}
    
    T_min = max(dados_por_campo[H][0].min() for H in campos_ordenados)
    T_max = min(dados_por_campo[H][0].max() for H in campos_ordenados)

    temp_comum = np.arange(T_min, T_max, 0.5)
    dS = np.zeros_like(temp_comum)

    for i in range(len(campos_ordenados) - 1):
        H1 = campos_ordenados[i]
        H2 = campos_ordenados[i + 1]
        dH = diferença[i]

        Temp_H1, mag_H1 = dados_por_campo[H1]
        Temp_H2, mag_H2 = dados_por_campo[H2]

        mag_interp_H1 = np.interp(temp_comum,Temp_H1, mag_H1)
        mag_interp_H2 = np.interp(temp_comum,Temp_H2, mag_H2)

        dM_dT_H1 = derivada_dM_dT(temp_comum,mag_interp_H1)
        dM_dT_H2 = derivada_dM_dT(temp_comum,mag_interp_H2)
        soma_total = dM_dT_H1 + dM_dT_H2

        delta_S = entropia_MxT(soma_total, dH)
        dS += delta_S 
        delta_S_total[f"{int(H1)}Oe_to_{int(H2)}Oe"] = (delta_S)

    return temp_comum,delta_S_total,dS

def plot_deltaS(temp_comum,delta_S_total):
    controle = 0
    plt.figure()
    for chave, delta_S in delta_S_total.items():
        plt.plot(temp_comum,delta_S, "o")

    plt.xlabel('Índice de Temperatura')
    plt.ylabel('ΔS (J/kg·K)')
    #plt.legend()
    plt.grid()
    if controle == 1:
        caminho_figura = os.path.join(saida, f"{nome_da_amostra}_DeltaS.png")
        plt.savefig(caminho_figura)
        plt.close()
        print(f"Figura salva: {caminho_figura}")
    plt.show()

#inputs
diretorio = "/home/gabriel/Documentos/IC/Medidas"
nome_da_amostra = r"Sn15" #melhor que o usuario defina
linhas_pular = 34  #ajustar conforme o arquivo
saida = os.path.join(diretorio,"separados_por_campo")

arquivos = [f for f in os.listdir(diretorio) if f.endswith(".txt") or f.endswith(".dat") or f.endswith(".DAT")]
print(arquivos)

os.makedirs(saida, exist_ok=True)

for arquivo in arquivos:
    #print(f"Processando arquivo: {arquivo}")
    
    diferença, dados_por_campo, campos_ordenados = separar_por_campo(arquivo,saida,nome_da_amostra,linhas_pular)

    #print(f"ΔH entre campos (Oe): {diferença}")
    #print(f"Campos ordenados (Oe): {campos_ordenados}")
    
    #Temp_4000, mag_4000 = dados_por_campo[4000]
    #print(f"Temperaturas: {Temp_4000}")
    
    plot_MxT(dados_por_campo,nome_da_amostra,saida)
    
    temp_comum,delta_S_total,dS = calculo_da_entropia(dados_por_campo,campos_ordenados,diferença)
    print(f"ΔS total calculada: {delta_S_total}")
    
    plot_deltaS(temp_comum,delta_S_total)
    
    plt.plot(temp_comum,-dS, "o")
    plt.xlabel("temperatura (K)")
    plt.ylabel(r"-$\Delta$S (J $Kg^{-1}$ $K^{-1}$)")
    plt.show()
    
    #reconstruir_MxH(dados_por_campo,campos_ordenados,temp_comum)