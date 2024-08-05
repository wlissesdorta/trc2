# Importação das bibliotecas
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd  # Importando pandas para criar tabelas de dados

# Título do aplicativo Streamlit
st.title("Trocador de Calor")

# Seção no painel lateral para as entradas do fluido frio
st.sidebar.header("Fluido Frio")
Tf_e = st.sidebar.number_input("Temperatura de Entrada (°C)", value=30.0, key="Tf_e")
mf = st.sidebar.number_input("Vazão Mássica (kg/s)", value=0.2, key="mf")
Cp_f = st.sidebar.number_input("Capacidade Térmica Específica (kJ/kg.K)", value=4.171, format="%.3f", key="Cp_f")

# Seção no painel lateral para as entradas do fluido quente
st.sidebar.header("Fluido Quente")
Tq_e = st.sidebar.number_input("Temperatura de Entrada (°C)", value=100.0, key="Tq_e")
mq = st.sidebar.number_input("Vazão Mássica (kg/s)", value=0.1, key="mq")
Cp_q = st.sidebar.number_input("Capacidade Térmica Específica (kJ/kg.K)", value=2.131, format="%.3f", key="Cp_q")

# Seção no painel lateral para as configurações do trocador de calor
st.sidebar.header("Configurações do Trocador")
L = st.sidebar.number_input("Comprimento (m)", value=65.90, format="%.3f", key="L")
D = st.sidebar.number_input("Diâmetro (mm)", value=25.00, key="D")
N = st.sidebar.number_input("Número de Elementos", value=30, key="N")
U = st.sidebar.number_input("U (W/m².K)", value=38.10, key="U")

try:
    # Verificar se algum dos valores é zero para evitar divisão por zero
    if N == 0 or mq == 0 or mf == 0:
        raise ZeroDivisionError("Valor inválido, verifique!")

    # Cálculos preliminares
    D = D / 1000  # Conversão do diâmetro de milímetros para metros
    Cp_f *= 1000  # Conversão da capacidade térmica específica de kJ/kg.K para J/kg.K
    Cp_q *= 1000  # Conversão da capacidade térmica específica de kJ/kg.K para J/kg.K
    dx = L / N  # Comprimento de cada segmento

    # Inicialização das temperaturas ao longo do trocador
    Tq = np.zeros(N + 1)  # Temperaturas do fluido quente
    Tf = np.zeros(N + 1)  # Temperaturas do fluido frio

    # Condições de contorno
    Tq[0] = Tq_e  # Temperatura de entrada do fluido quente
    Tf[N] = Tf_e  # Temperatura de entrada do fluido frio

    # Cálculo dos fatores de troca de calor
    Aq = U * np.pi * D * dx / (Cp_q * mq)  # Fator para o fluido quente
    Af = U * np.pi * D * dx / (Cp_f * mf)  # Fator para o fluido frio

    # Loop para calcular as temperaturas em cada segmento do trocador
    for i in range(N):
        # Cálculo das novas temperaturas usando diferenças finitas
        Tq_new = (Tq[i] + Aq * Tf[N - i]) / (1 + Aq)
        Tf_new = (Tf[N - i] + Af * Tq[i]) / (1 + Af)
        Tq[i + 1] = Tq_new
        Tf[N - i - 1] = Tf_new

    # Ajustando o array x para ter o mesmo tamanho que Tq e Tf
    x = np.linspace(0, L, N + 1)

    # Criação do gráfico interativo usando Plotly
    fig = go.Figure()

    # Adicionando a curva de temperatura do fluido quente ao gráfico
    fig.add_trace(go.Scatter(
        x=x,
        y=Tq,
        mode='lines+markers',
        name='Fluido Quente',
        line=dict(color='red'),
        hovertemplate='Comprimento: %{x:.2f} m<br>Temperatura: %{y:.2f} °C'
    ))

    # Adicionando a curva de temperatura do fluido frio ao gráfico
    fig.add_trace(go.Scatter(
        x=x,
        y=Tf,
        mode='lines+markers',
        name='Fluido Frio',
        line=dict(color='blue'),
        hovertemplate='Comprimento: %{x:.2f} m<br>Temperatura: %{y:.2f} °C'
    ))

    # Configuração do layout do gráfico
    fig.update_layout(
        title='Distribuição de Temperatura ao Longo do Trocador de Calor',
        xaxis_title='Comprimento do Trocador (m)',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        template='plotly_white'
    )

    # Exibindo o gráfico no aplicativo Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Criando uma tabela para os valores de entrada
    input_data = {
        "Parâmetro": [
            "Temperatura de Entrada Fluido Frio (°C)",
            "Vazão Mássica Fluido Frio (kg/s)",
            "Capacidade Térmica Específica Fluido Frio (kJ/kg.K)",
            "Temperatura de Entrada Fluido Quente (°C)",
            "Vazão Mássica Fluido Quente (kg/s)",
            "Capacidade Térmica Específica Fluido Quente (kJ/kg.K)",
            "Comprimento do Trocador (m)",
            "Diâmetro do Trocador (mm)",
            "Número de Elementos",
            "Coeficiente Global de Transferência de Calor (U, W/m².K)"
        ],
        "Valor": [
            Tf_e,
            mf,
            Cp_f / 1000,  # Convertendo de J/kg.K para kJ/kg.K
            Tq_e,
            mq,
            Cp_q / 1000,  # Convertendo de J/kg.K para kJ/kg.K
            L,
            D * 1000,  # Convertendo de metros para milímetros
            N,
            U
        ]
    }

    # Exibindo a tabela de valores de entrada
    st.subheader("Valores de Entrada")
    st.table(pd.DataFrame(input_data))

    # Criando uma tabela para os arrays de temperaturas
    temp_data = {
        "Posição (m)": x,
        "Temperatura Fluido Quente (°C)": Tq,
        "Temperatura Fluido Frio (°C)": Tf
    }

    # Exibindo a tabela dos arrays de temperaturas
    st.subheader("Distribuição de Temperaturas ao Longo do Trocador")
    st.table(pd.DataFrame(temp_data))

# Tratamento de exceção para divisão por zero
except ZeroDivisionError as e:
    st.error(str(e))
