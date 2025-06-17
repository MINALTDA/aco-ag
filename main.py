import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Adiciona a pasta menu ao path para importação fácil
sys.path.append(os.path.join(os.path.dirname(__file__), "menu"))

# Importa cada página
import parametros
import aco
import ga
import comparacao
import sobre

st.set_page_config(page_title="Otimização de rotas", layout="wide", page_icon="🚚")

menu_options = [
    "Início",
    "Parâmetros",
    "ACO",
    "Algoritmo genético",
    "Comparação",
    "Sobre"
]
menu_icons = [
    "house", "gear", "bug", "diagram-3", "bar-chart", "info-circle"
]
# "bug" = inseto (alternativa para formiga), "diagram-3" para genética (substituto para DNA)
MENU_KEY = "menu_selected_option"

if MENU_KEY not in st.session_state:
    st.session_state[MENU_KEY] = menu_options[0]
active_page = st.session_state[MENU_KEY]

with st.sidebar:
    st.title("🚚 Otimização de rotas")
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        menu_icon="cast",
        default_index=menu_options.index(active_page),
        key=MENU_KEY,
        orientation="vertical"
    )

if selected == "Início":
    st.header("Bem-vindo ao otimizador de rotas")
    st.write("""
        Este sistema compara algoritmos de Colônia de Formigas (ACO) e Algoritmo Genético (GA)
        para roteamento eficiente de veículos. Use o menu ao lado para acessar as funcionalidades.
    """)

elif selected == "Parâmetros":
    parametros.render()

elif selected == "ACO":
    aco.render()

elif selected == "Algoritmo genético":
    ga.render()

elif selected == "Comparação":
    comparacao.render()

elif selected == "Sobre":
    sobre.render()

else:
    st.error("Página não reconhecida.")
