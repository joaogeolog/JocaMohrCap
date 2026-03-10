import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Configuração da Página ---
st.set_page_config(page_title="JocaMohr Web", layout="wide")

# Título Principal
st.write("# JocaMohr - Simulador Geomecânico")
st.write("### Autor: João Carlos Menescal (U3KP)")

# --- Sliders na Barra Lateral ---
with st.sidebar:
    st.header("TENSÕES (MPa)")
    s1 = st.slider("Sigma 1 (s1)", 0, 400, 120)
    s3 = st.slider("Sigma 3 (s3)", 0, 400, 40)
    pp = st.slider("Pressão de Poros", 0, 200, 20)

    st.header("PROPRIEDADES DA ROCHA")
    alpha = st.slider("Biot (alpha)", 0.0, 1.0, 1.0)
    c = st.slider("Coesão (MPa)", 0, 50, 15)
    phi = st.slider("Atrito (graus)", 0, 60, 30)
    ts = st.slider("Tração - Ts (MPa)", 0, 50, 10)
    pc = st.slider("Colapso - Pc (MPa)", 50, 400, 180)

    st.header("PLANO E VISUALIZAÇÃO")
    mergulho = st.slider("Mergulho (graus)", 0, 90, 60)
    giro = st.slider("Giro Horizontal 3D", 0, 360, 45)
    regime = st.radio("Regime", ["Normal", "Reverso"])

# --- Cálculos Geomecânicos ---
if s1 < s3: s1 = s3
s1_eff, s3_eff = s1 - (alpha * pp), s3 - (alpha * pp)
centro_m, raio_m = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2

# Construção da Envoltória
x_env = np.linspace(-ts if ts > 0 else -0.01, pc, 500)
tan_phi = np.tan(np.radians(phi))
xt_coll = (pc + (c / tan_phi)) / 2
y_env = np.zeros_like(x_env)

for i, x in enumerate(x_env):
    if x < 0:
        k = (c**2) / (ts if ts > 0 else 0.001)
        y_env[i] = np.sqrt(max(0, k * (x + ts)))
    elif x < xt_coll:
        y_env[i] = c + x * tan_phi
    else:
        a_c, b_c = pc - xt_coll, c + xt_coll * tan_phi
        y_env[i] = b_c * np.sqrt(max(0, 1 - ((x - xt_coll)**2 / a_c**2)))

# --- Plotagem (Modo Web) ---
# Usamos plt.subplots para criar a figura e os eixos de forma limpa
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': '3d'} if False else None)

# Ajuste manual para o ax1 ser 3D
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122)

# Círculo de Mohr
t_c = np.linspace(0, np.pi, 500)
x_circ = centro_m + raio_m * np.cos(t_c)
y_circ = raio_m * np.sin(t_c)
res_interp = np.interp(x_circ, x_env, y_env, left=0, right=0)
x_f, y_f = np.clip(x_circ, -ts, pc), np.minimum(y_circ, res_interp)

ax2.plot(x_f, y_f, color='#1f77b4', lw=2, label="Círculo de Mohr")
ax2.plot(x_env, y_env, color='#d62728', ls='--', label="Envoltória")

# Ponto no Plano
theta_rel = mergulho if regime == 'Normal' else 90 - mergulho
sn = centro_m + raio_m * np.cos(np.radians(2 * theta_rel))
tn_te = abs(raio_m * np.sin(np.radians(2 * theta_rel)))
sn_clamped = np.clip(sn, -ts, pc)
tn_re = min(tn_te, np.interp(sn_clamped, x_env, y_env))
ax2.plot([sn_clamped], [tn_re], 'o', color='#2ca02c', markersize=10)

ax2.set_xlim(-50, 250); ax2.set_ylim(0, 120); ax2.set_aspect('equal')
ax2.set_xlabel("sigma_n' (MPa)"); ax2.set_ylabel("tau (MPa)")
ax2.grid(alpha=0.3)

# 3D Render
ax1.view_init(elev=20, azim=giro)
ax1.set_axis_off()
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
x_3d = 0.5 * np.cos(u) * np.sin(v)
y_3d = 0.5 * np.sin(u) * np.sin(v)
z_3d = 0.8 * np.cos(v)
ax1.plot_wireframe(x_3d, y_3d, z_3d, color="lightgray", alpha=0.3)

# EXIBIÇÃO FINAL
st.pyplot(fig)

# Métricas abaixo do gráfico
col1, col2 = st.columns(2)
fs = np.interp(sn_clamped, x_env, y_env) / tn_te if tn_te > 0.1 else 10.0
col1.metric("Fator de Segurança (FS)", f"{fs:.2f}")
col2.metric("Regime Atual", regime)
