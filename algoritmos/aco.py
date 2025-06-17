# algoritmos/aco.py
import numpy as np
import random

def run_aco(
    matriz_custos,
    n_formigas=20,
    n_iter=300,
    alfa=1.0,
    beta=5.0,
    evaporacao=0.5,
    feromonio_inicial=1.0,
    cidade_inicio=0,
    seed=None
):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    n_cidades = matriz_custos.shape[0]
    cidades = list(matriz_custos.index)
    custos = matriz_custos.values

    feromonio = np.ones((n_cidades, n_cidades)) * feromonio_inicial
    visibilidade = 1 / (custos + 1e-10)
    np.fill_diagonal(visibilidade, 0)

    melhor_rota = None
    melhor_custo = float("inf")
    historico = []

    for iteracao in range(n_iter):
        rotas = []
        custos_rotas = []

        for _ in range(n_formigas):
            visitado = [False] * n_cidades
            atual = cidade_inicio
            caminho = [atual]
            visitado[atual] = True

            for _ in range(n_cidades - 1):
                probas = []
                for j in range(n_cidades):
                    if not visitado[j]:
                        prob = (feromonio[atual, j] ** alfa) * (visibilidade[atual, j] ** beta)
                        probas.append(prob)
                    else:
                        probas.append(0)
                soma = sum(probas)
                if soma == 0:
                    # Nenhum caminho viável por probabilidade: escolha determinística do próximo não visitado
                    # (com custo altíssimo, mas força uma solução completa)
                    prox = [j for j, v in enumerate(visitado) if not v][0]
                else:
                    probas = [p / soma for p in probas]
                    prox = np.random.choice(range(n_cidades), p=probas)
                caminho.append(prox)
                visitado[prox] = True
                atual = prox

            caminho.append(cidade_inicio)  # Retorna ao início

            # Agora SEMPRE rota completa!
            custo_total = sum(
                custos[caminho[i], caminho[i + 1]]
                for i in range(len(caminho) - 1)
            )
            rotas.append(caminho)
            custos_rotas.append(custo_total)

            if custo_total < melhor_custo:
                melhor_custo = custo_total
                melhor_rota = caminho[:]

        # Atualiza feromônio apenas para rotas completas
        feromonio = feromonio * (1 - evaporacao)
        for rota, custo in zip(rotas, custos_rotas):
            for i in range(len(rota) - 1):
                feromonio[rota[i], rota[i + 1]] += 1.0 / (custo + 1e-10)

        historico.append(melhor_custo)

    # Garante que sempre retorna rota válida
    rota_cidades = [cidades[i] for i in melhor_rota]
    return {
        "rota": rota_cidades,
        "custo": melhor_custo,
        "historico": historico
    }
