import streamlit as st
import pandas as pd
from algoritmos.ga import run_ga
import folium
from streamlit_folium import st_folium
import json
import plotly.graph_objects as go
import time

def render():
    st.header("Algoritmo genético (GA)")

    matriz_custos = pd.read_csv("dados/matriz_custos.csv", index_col=0)
    cidades = matriz_custos.index.tolist()

    # Patrocínio por padrão
    idx_patrocinio = cidades.index("Patrocínio") if "Patrocínio" in cidades else 0
    cidade_inicio = st.selectbox("Cidade inicial/final", cidades, index=idx_patrocinio, key="ga_cidade_inicio")

    st.subheader("Parâmetros do GA")
    n_pop = st.number_input("Tamanho da população", 2, 200, 50)
    n_iter = st.number_input("Número de iterações", 10, 10000, st.session_state.get("max_iter", 300), step=10)
    p_crossover = st.slider("Probabilidade de crossover", 0.0, 1.0, 0.9, 0.05)
    p_mutacao = st.slider("Probabilidade de mutação", 0.0, 1.0, 0.2, 0.05)
    elite_frac = st.slider("Fração de elite", 0.0, 0.5, 0.2, 0.05)

    if st.button("Executar GA"):
        idx_inicio = cidades.index(cidade_inicio)
        t0 = time.time()
        resultado = run_ga(
            matriz_custos,
            n_pop=int(n_pop),
            n_iter=int(n_iter),
            p_crossover=p_crossover,
            p_mutacao=p_mutacao,
            elite_frac=elite_frac,
            cidade_inicio=idx_inicio
        )
        t1 = time.time()
        resultado["tempo_execucao"] = t1 - t0
        st.session_state["ga_resultado"] = resultado

    if "ga_resultado" in st.session_state:
        resultado = st.session_state["ga_resultado"]
        st.success(f"Melhor rota encontrada: {' → '.join(resultado['rota'])}")
        st.write(f"Custo total: R$ {resultado['custo']:.2f}")

        # Visualização no mapa
        with open("dados/municipios.json", encoding="utf-8") as f:
            dados_cidades = json.load(f)
        coords_dict = {d["nome"]: (d["lat"], d["lng"]) for d in dados_cidades}
        coordenadas = [coords_dict[nome] for nome in resultado["rota"]]

        lat_c, lng_c = coordenadas[0]
        m = folium.Map(location=[lat_c, lng_c], zoom_start=8)
        folium.Marker([lat_c, lng_c], tooltip="Início", icon=folium.Icon(color="green")).add_to(m)
        for (lat, lng), nome in zip(coordenadas[1:], resultado["rota"][1:]):
            folium.Marker([lat, lng], tooltip=nome).add_to(m)
        folium.PolyLine(locations=coordenadas, color="purple", weight=4).add_to(m)
        st_folium(m, width=800, height=500)

        # Gráfico de evolução do custo (Plotly, com títulos)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=resultado["historico"],
            x=list(range(1, len(resultado["historico"]) + 1)),
            mode='lines+markers'
        ))
        fig.update_layout(
            title="Evolução do custo ao longo das iterações",
            xaxis_title="Iteração",
            yaxis_title="Custo (R$)",
            template="simple_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tempo de execução
        tempo_exec = resultado.get("tempo_execucao", None)
        if tempo_exec is not None:
            st.info(f"Tempo de execução do algoritmo: {tempo_exec:.2f} segundos")
    else:
        st.info("Configure os parâmetros e clique em 'Executar GA' para visualizar o resultado.")
