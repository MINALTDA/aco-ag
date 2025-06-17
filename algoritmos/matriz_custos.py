import pandas as pd
import os

def calcular_matriz_custos(
    path_dist="dados/matriz_distancias.csv",
    path_temp="dados/matriz_tempos.csv",
    custo_km=1.0,
    custo_min=0.0,
    path_saida="dados/matriz_custos.csv"
):
    # Ler matrizes
    dist = pd.read_csv(path_dist, index_col=0)
    temp = pd.read_csv(path_temp, index_col=0)
    # Converter para float e tratar valores ausentes
    dist = dist.apply(pd.to_numeric, errors='coerce').fillna(float('inf'))
    temp = temp.apply(pd.to_numeric, errors='coerce').fillna(float('inf'))

    # Calcular custos
    custos = dist * custo_km + temp * custo_min
    custos.to_csv(path_saida)
    return custos
