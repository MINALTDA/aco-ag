# algoritmos/distancia_tempo.py
import json
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida. Coloque sua chave no arquivo .env.")

# Caminhos dos arquivos
JSON_CIDADES = os.path.join("dados", "municipios.json")
ARQ_DIST = os.path.join("dados", "matriz_distancias.csv")
ARQ_TEMPO = os.path.join("dados", "matriz_tempos.csv")

with open(JSON_CIDADES, encoding='utf-8') as f:
    cidades = json.load(f)

nomes = [cidade['nome'] for cidade in cidades]
coordenadas = [f"{cidade['lat']},{cidade['lng']}" for cidade in cidades]

# Inicializar DataFrames
distancias = pd.DataFrame(index=nomes, columns=nomes)
tempos = pd.DataFrame(index=nomes, columns=nomes)

# Função para dividir destinos em blocos de até 25
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

LIMIT = 25  # Limite máximo de destinos por request

for i, origem in enumerate(coordenadas):
    nome_origem = nomes[i]
    for idx_chunk, destino_indices in enumerate(chunks(list(range(len(coordenadas))), LIMIT)):
        destinos_chunk = [coordenadas[j] for j in destino_indices]
        nomes_destino_chunk = [nomes[j] for j in destino_indices]
        destinos_str = "|".join(destinos_chunk)
        url = (
            "https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origem}"
            f"&destinations={destinos_str}"
            "&mode=driving"
            "&language=pt-BR"
            f"&key={GOOGLE_API_KEY}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro HTTP para {nome_origem}: {response.text}")
            continue
        data = response.json()
        if data.get('status') != "OK" or 'rows' not in data or not data['rows']:
            print(f"Erro inesperado para origem '{nome_origem}': {data}")
            continue
        elements = data['rows'][0]['elements']
        for dest_idx, elem in enumerate(elements):
            nome_destino = nomes_destino_chunk[dest_idx]
            if elem.get('status') == 'OK':
                dist_km = elem['distance']['value'] / 1000
                tempo_min = elem['duration']['value'] / 60
            else:
                dist_km = float('inf')
                tempo_min = float('inf')
            distancias.loc[nome_origem, nome_destino] = dist_km
            tempos.loc[nome_origem, nome_destino] = tempo_min
        print(f"Origem '{nome_origem}' - bloco {idx_chunk + 1} processado ({len(destinos_chunk)} destinos).")
        time.sleep(1)  # Boa prática

distancias.to_csv(ARQ_DIST, encoding='utf-8')
tempos.to_csv(ARQ_TEMPO, encoding='utf-8')

print("Matrizes de distâncias e tempos geradas com sucesso!")
