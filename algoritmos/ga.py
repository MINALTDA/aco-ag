# algoritmos/ga.py
import numpy as np
import random

def run_ga(
    matriz_custos,
    n_pop=50,
    n_iter=300,
    p_crossover=0.9,
    p_mutacao=0.2,
    elite_frac=0.2,
    cidade_inicio=0,
    seed=None
):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    n_cidades = matriz_custos.shape[0]
    cidades = list(matriz_custos.index)
    custos = matriz_custos.values

    # Função para avaliar rota
    def calc_custo(rota):
        return sum(custos[rota[i], rota[i + 1]] for i in range(n_cidades)) + custos[rota[-1], rota[0]]

    # Gerar população inicial
    pop = []
    for _ in range(n_pop):
        rota = list(range(n_cidades))
        rota.remove(cidade_inicio)
        random.shuffle(rota)
        rota = [cidade_inicio] + rota + [cidade_inicio]
        pop.append(rota)
    pop = np.array(pop)

    historico = []
    melhor_rota = None
    melhor_custo = float("inf")

    n_elite = max(1, int(elite_frac * n_pop))

    for it in range(n_iter):
        custos_pop = np.array([calc_custo(ind) for ind in pop])
        idx_sorted = np.argsort(custos_pop)
        pop = pop[idx_sorted]

        # Salvar melhor da geração
        if custos_pop[idx_sorted[0]] < melhor_custo:
            melhor_custo = custos_pop[idx_sorted[0]]
            melhor_rota = pop[0].tolist()
        historico.append(melhor_custo)

        # Elitismo
        nova_pop = [pop[i].tolist() for i in range(n_elite)]

        # Cruzamento
        while len(nova_pop) < n_pop:
            pais = random.sample(list(pop[:20]), 2)
            if random.random() < p_crossover:
                filho = order_crossover(pais[0], pais[1], cidade_inicio)
            else:
                filho = pais[0].tolist()
            if random.random() < p_mutacao:
                filho = mutation(filho, cidade_inicio)
            nova_pop.append(filho)

        pop = np.array(nova_pop)

    rota_cidades = [cidades[i] for i in melhor_rota]
    return {
        "rota": rota_cidades,
        "custo": melhor_custo,
        "historico": historico
    }

def order_crossover(parent1, parent2, cidade_inicio):
    # OX para TSP
    n = len(parent1)
    start, end = sorted(random.sample(range(1, n-1), 2))  # evita inicio/fim
    child = [None] * n
    child[start:end] = parent1[start:end]
    pos = end
    for gene in parent2[1:-1]:
        if gene not in child:
            if pos == n-1:
                pos = 1
            child[pos] = gene
            pos += 1
    child[0] = parent1[0]
    child[-1] = parent1[-1]
    # Fill None if any left
    for i in range(1, n-1):
        if child[i] is None:
            child[i] = parent2[i]
    return child

def mutation(rota, cidade_inicio):
    # 2-opt swap simples, exceto início/fim
    n = len(rota)
    i, j = sorted(random.sample(range(1, n-1), 2))
    rota[i:j] = reversed(rota[i:j])
    return rota
