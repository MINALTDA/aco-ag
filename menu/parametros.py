import streamlit as st
from algoritmos.matriz_custos import calcular_matriz_custos
import pandas as pd
import os

def render():
    st.header("Configuração de parâmetros globais")
    st.write("Defina aqui os custos e parâmetros dos algoritmos. As alterações só terão efeito ao clicar em 'Atualizar parâmetros e matriz de custos'.")

    # Parâmetros globais de custo (inputs temporários)
    custo_km = st.number_input("Custo por quilômetro (R$)", min_value=0.0, max_value=100.0, value=st.session_state.get("custo_km", 2.5), step=0.1)
    custo_min = st.number_input("Custo por minuto (R$)", min_value=0.0, max_value=100.0, value=st.session_state.get("custo_min", 0.5), step=0.1)

    # Parâmetros dos algoritmos
    max_iter = st.number_input("Máximo de iterações", min_value=10, max_value=5000, value=st.session_state.get("max_iter", 1000), step=10)
    tempo_limite = st.number_input("Tempo máximo de execução (segundos)", min_value=10, max_value=3600, value=st.session_state.get("tempo_limite", 300), step=10)

    if st.button("Atualizar parâmetros e matriz de custos"):
        # Atualiza sessão
        st.session_state["custo_km"] = custo_km
        st.session_state["custo_min"] = custo_min
        st.session_state["max_iter"] = int(max_iter)
        st.session_state["tempo_limite"] = int(tempo_limite)

        # Calcula e salva matriz de custos
        custos = calcular_matriz_custos(
            custo_km=custo_km,
            custo_min=custo_min
        )
        st.success("Parâmetros atualizados e matriz de custos recalculada com sucesso!")
        st.dataframe(custos)
        st.download_button(
            "Baixar matriz de custos (CSV)",
            data=custos.to_csv().encode("utf-8"),
            file_name="matriz_custos.csv",
            mime="text/csv"
        )
    else:
        # Mostra última matriz de custos, se existir
        path_custos = "dados/matriz_custos.csv"
        if os.path.exists(path_custos):
            custos = pd.read_csv(path_custos, index_col=0)
            st.info("Última matriz de custos calculada:")
            st.dataframe(custos)
            st.download_button(
                "Baixar matriz de custos (CSV)",
                data=custos.to_csv().encode("utf-8"),
                file_name="matriz_custos.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhuma matriz de custos foi gerada ainda.")
