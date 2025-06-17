import streamlit as st
import pandas as pd
from algoritmos.aco import run_aco
import folium
from streamlit_folium import st_folium
import json
import os
import plotly.graph_objects as go
import time

def render():
    st.header("Algoritmo de colônia de formigas (ACO)")

    matriz_custos = pd.read_csv("dados/matriz_custos.csv", index_col=0)
    cidades = matriz_custos.index.tolist()

    # Patrocínio por padrão
    idx_patrocinio = cidades.index("Patrocínio") if "Patrocínio" in cidades else 0
    cidade_inicio = st.selectbox("Cidade inicial/final", cidades, index=idx_patrocinio)

    st.subheader("Parâmetros do ACO")
    n_formigas = st.number_input("Número de formigas", 1, 100, 20)
    n_iter = st.number_input("Número de iterações", 10, 10000, st.session_state.get("max_iter", 300), step=10)
    alfa = st.slider("Alfa (peso do feromônio)", 0.1, 5.0, 1.0, 0.1)
    beta = st.slider("Beta (peso da heurística)", 0.1, 10.0, 5.0, 0.1)
    evaporacao = st.slider("Taxa de evaporação", 0.01, 1.0, 0.5, 0.01)

    if st.button("Executar ACO"):
        idx_inicio = cidades.index(cidade_inicio)
        t0 = time.time()
        resultado = run_aco(
            matriz_custos,
            n_formigas=n_formigas,
            n_iter=n_iter,
            alfa=alfa,
            beta=beta,
            evaporacao=evaporacao,
            cidade_inicio=idx_inicio
        )
        t1 = time.time()
        resultado["tempo_execucao"] = t1 - t0
        st.session_state["aco_resultado"] = resultado

    if "aco_resultado" in st.session_state:
        resultado = st.session_state["aco_resultado"]
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
        folium.PolyLine(locations=coordenadas, color="blue", weight=4).add_to(m)
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
        st.info("Configure os parâmetros e clique em 'Executar ACO' para visualizar o resultado.")
