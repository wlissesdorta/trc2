import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Configuração do Trocador de Calor")

st.sidebar.header("Fluido Frio")
Tf_in = st.sidebar.number_input("Temperatura de Entrada (°C)", value=25.0, key="Tf_in")
mf = st.sidebar.number_input("Vazão Mássica (kg/s)", value=1.0, key="mf")
Cp_f = st.sidebar.number_input("Capacidade Térmica Específica (kJ/kg.K)", value=4.18, key="Cp_f")

st.sidebar.header("Fluido Quente")
Tq_in = st.sidebar.number_input("Temperatura de Entrada (°C)", value=75.0, key="Tq_in")
mq = st.sidebar.number_input("Vazão Mássica (kg/s)", value=1.0, key="mq")
Cp_q = st.sidebar.number_input("Capacidade Térmica Específica (kJ/kg.K)", value=4.18, key="Cp_q")

st.sidebar.header("Configurações do Trocador")
L = st.sidebar.number_input("Comprimento (m)", value=10.0, key="L")
D = st.sidebar.number_input("Diâmetro (mm)", value=50.0, key="D")
N = st.sidebar.number_input("Número de Elementos", value=10, key="N")
U = st.sidebar.number_input("U (W/m².K)", value=500.0, key="U")

try:
    # Verificar se algum dos valores é zero que causaria divisão por zero
    if N == 0 or mq == 0 or mf == 0:
        raise ZeroDivisionError("Valor inválido, verifique!")

    # Cálculo
    D = D / 1000  # Conversão para metros
    Cp_f *= 1000  # Conversão para J/kg.K
    Cp_q *= 1000  # Conversão para J/kg.K
    dx = L / N

    Tq = np.zeros(N + 1)
    Tf = np.zeros(N + 1)

    Tq[0] = Tq_in
    Tf[N] = Tf_in

    Aq = U * np.pi * D * dx / (Cp_q * mq)
    Af = U * np.pi * D * dx / (Cp_f * mf)

    for i in range(N):
        Tq_new = (Tq[i] + Aq * Tf[N - i]) / (1 + Aq)
        Tf_new = (Tf[N - i] + Af * Tq[i]) / (1 + Af)
        Tq[i + 1] = Tq_new
        Tf[N - i - 1] = Tf_new

    x = np.arange(0, L + dx, dx)

    # Gráfico Interativo com Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=Tq,
        mode='lines+markers',
        name='Fluido Quente',
        line=dict(color='red'),
        hovertemplate='Comprimento: %{x:.2f} m<br>Temperatura: %{y:.2f} °C'
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=Tf,
        mode='lines+markers',
        name='Fluido Frio',
        line=dict(color='blue'),
        hovertemplate='Comprimento: %{x:.2f} m<br>Temperatura: %{y:.2f} °C'
    ))

    fig.update_layout(
        title='Distribuição de Temperatura ao Longo do Trocador de Calor',
        xaxis_title='Comprimento do Trocador (m)',
        yaxis_title='Temperatura (°C)',
        hovermode='x unified',
        template='plotly_white'
    )

    st.plotly_chart(fig)

except ZeroDivisionError as e:
    st.error(str(e))
