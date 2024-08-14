
import streamlit as st
import math
from sympy import symbols, Eq, solve
import pandas as pd
import plotly.graph_objects as go

# Título do aplicativo
st.title("Simulação de Trocador de Calor")

# Seção para entrada de dados
st.sidebar.header("Parâmetros do Fluido Externo (Anel) - Etilenoglicol")
m_a = st.sidebar.number_input("Vazão mássica (kg/s)", value=3.78, format="%.2f")
T_a = st.sidebar.number_input("Temperatura de entrada (°C)", value=32.0, format="%.2f")
rho_a = st.sidebar.number_input("Densidade (kg/m³)", value=1084.0, format="%.2f")
cp_a = st.sidebar.number_input("Capacidade calorífica específica (J/kg.K)", value=2583.0, format="%.2f")
k_a = st.sidebar.number_input("Condutividade térmica (W/m.K)", value=0.26, format="%.4f")
v_a = st.sidebar.number_input("Viscosidade cinemática (m²/s)", value=4.32e-6, format="%.11f")
Pr_a = st.sidebar.number_input("Número de Prandtl", value=46.52, format="%.2f")

st.sidebar.header("Parâmetros do Fluido Interno (Tubo) - Água")
m_t = st.sidebar.number_input("Vazão mássica (kg/s)", value=0.6, format="%.2f")
T_t = st.sidebar.number_input("Temperatura de entrada (°C)", value=80.0, format="%.2f")
rho_t = st.sidebar.number_input("Densidade (kg/m³)", value=995.0, format="%.2f")
cp_t = st.sidebar.number_input("Capacidade calorífica específica (J/kg.K)", value=4178.6, format="%.2f")
k_t = st.sidebar.number_input("Condutividade térmica (W/m.K)", value=0.622, format="%.4f")
v_t = st.sidebar.number_input("Viscosidade cinemática (m²/s)", value=7.276e-7, format="%.11f")
Pr_t = st.sidebar.number_input("Número de Prandtl", value=4.87, format="%.2f")

st.sidebar.header("Parâmetros do Trocador de Calor")
Di_a = (st.sidebar.number_input("Diâmetro interno do anel Externo (mm)", value=51.00, format="%.2f"))/1000
Di_t = (st.sidebar.number_input("Diâmetro interno do tubo Interno (mm)", value=32.80, format="%.2f"))/1000
De_t = (st.sidebar.number_input("Diâmetro externo do tubo Interno (mm)", value=32.80, format="%.2f"))/1000
L = st.sidebar.number_input("Comprimento do trocador (m)", value=20.0, format="%.2f")
N = st.sidebar.number_input("Número de segmentos", value=10)

# O restante do código permanece inalterado...


# Cálculos
A_t = (math.pi * Di_t**2) / 4
A_a = (math.pi * (Di_a**2 - De_t**2)) / 4
V_t = m_t / (rho_t * A_t)
V_a = m_a / (rho_a * A_a)
D_h = Di_a - De_t
D_eq = (Di_a**2 - De_t**2) / De_t
Re_t = V_t * Di_t / v_t
Re_a = V_a * D_eq / v_a
Nu_t = 0.023 * Re_t**(4/5) * Pr_t**0.3
Nu_a = 0.023 * Re_a**(4/5) * Pr_a**0.4
h_t = Nu_t * k_t / Di_t
h_a = Nu_a * k_a / D_eq
U = 1 / ((1 / h_t) + (1 / h_a))
dx = L / N
A = math.pi * Di_t * dx
C_q = m_t * cp_t
C_f = m_a * cp_a

# Criação de equações para resolver o sistema
T_quente = symbols('T_quente0:%d' % (N + 1))
T_frio = symbols('T_frio0:%d' % (N + 1))
Equacoes_Quente = []
Equacoes_Frio = []

for i in range(N):
    eq_q = Eq(C_q * (T_quente[i] - T_quente[i + 1]), 
              ((U * A) / 2) * (T_quente[i] + T_quente[i + 1] - T_frio[i] - T_frio[i + 1]))
    eq_f = Eq(-C_f * (T_frio[i + 1] - T_frio[i]), 
              ((U * A) / 2) * (T_quente[i] + T_quente[i + 1] - T_frio[i] - T_frio[i + 1]))
    Equacoes_Quente.append(eq_q)
    Equacoes_Frio.append(eq_f)

Equacoes_Quente = [eq.subs({T_quente[0]: T_t, T_frio[N]: T_a}) for eq in Equacoes_Quente]
Equacoes_Frio = [eq.subs({T_quente[0]: T_t, T_frio[N]: T_a}) for eq in Equacoes_Frio]

solucao = solve(Equacoes_Quente + Equacoes_Frio, T_quente + T_frio)

temperaturas_quente = [T_t] + [solucao[T_quente[i]] for i in range(1, N + 1)]
temperaturas_frio = [solucao[T_frio[i]] for i in range(N)] + [T_a]

# Convertendo os valores simbólicos para floats
temperaturas_quente = [float(T_t)] + [float(solucao[T_quente[i]]) for i in range(1, N + 1)]
temperaturas_frio = [float(solucao[T_frio[i]]) for i in range(N)] + [float(T_a)]

# Criação do DataFrame
df = pd.DataFrame({
    'Segmento': range(N + 1),
    'Temperatura Quente (°C)': temperaturas_quente,
    'Temperatura Frio (°C)': temperaturas_frio
})
df['L (m)'] = df['Segmento'] * L / N



# Criação do gráfico
fig = go.Figure()

# Trace para Temperatura Quente
fig.add_trace(go.Scatter(
    x=df['L (m)'], 
    y=df['Temperatura Quente (°C)'], 
    mode='lines+markers', 
    name='Temperatura Quente (°C)',
    line=dict(color='red'),
    hovertemplate='%{x:.2f} m<br> %{y:.2f} °C'
))

# Trace para Temperatura Frio
fig.add_trace(go.Scatter(
    x=df['L (m)'], 
    y=df['Temperatura Frio (°C)'], 
    mode='lines+markers', 
    name='Temperatura Frio (°C)',
    line=dict(color='blue'),
    hovertemplate='%{x:.2f} m<br>%{y:.2f} °C'
))

fig.update_layout(
    title='Temperaturas ao Longo do Trocador de Calor',
    xaxis_title='Distância (m)',
    yaxis_title='Temperatura (°C)',
    hovermode="x"  # Isso permite que ambos os valores sejam exibidos simultaneamente ao passar o mouse
)

st.plotly_chart(fig)

