# Autor: João Carlos Menescal (U3KP)
# Data: Março/2026
# Versão: JocaMohr v8.0 - Critério de Tração Parabólico (Griffith Style)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches

# --- Configurações Iniciais ---
DEFAULTS = {
    's1': 120, 's3': 40, 'pp': 20, 'alpha': 1.0,
    'c': 15, 'phi': 30, 'ang': 60, 'giro': 45,
    'ts': 10, 'pc': 180
}
regime_atual = 'Normal'

# --- Função de Ajuda (Texto Original Integrado) ---
def abrir_ajuda(event):
    help_fig = plt.figure('JocaMohr - Manual Técnico', figsize=(11, 9), facecolor='#fdfdfd')
    txt = (
        "MANUAL TÉCNICO JOCAMOHR\n\n"
        "Autor: João Carlos Menescal (U3KP)\n"
        "Data: Março/2026\n\n"
        "1. TENSÕES PRINCIPAIS:\n"
        "   - Sigma 1 (s1): Tensão principal máxima (maior compressão).\n"
        "   - Sigma 2 (s2): Tensão principal intermediária (assumida s2 = s3 no modelo 2D).\n"
        "   - Sigma 3 (s3): Tensão principal mínima.\n"
        "   No gráfico de Mohr, o círculo é definido pelo diâmetro entre s3 e s1.\n\n"
        "2. TENSÃO EFETIVA E COEFICIENTE DE BIOT (alpha):\n"
        "   A falha da rocha é controlada pela tensão efetiva (sigma'):\n"
        "   Cálculo: sigma' = sigma_total - (alpha * Pp)\n"
        "   - alpha (Biot): Define a eficiência da pressão de poros (Pp). Se alpha=1.0,\n"
        "     a Pp neutraliza a tensão normal integralmente. Se alpha=0, a Pp não afeta.\n\n"
        "3. CRITÉRIO DE RESISTÊNCIA (Mohr-Coulomb):\n"
        "   A resistência da rocha (tau_res) é dada por:\n"
        "   tau_res = c + sigma_n' * tan(phi)\n"
        "   Onde 'c' é a Coesão e 'phi' é o Ângulo de Atrito Interno.\n\n"
        "4. CÁLCULO DO FATOR DE SEGURANÇA (FS):\n"
        "   O FS é a razão entre a capacidade de carga da rocha e o esforço aplicado.\n"
        "   Fórmula: FS = tau_res / tau_atuante\n"
        "   - tau_res: Ponto no envelope de ruptura para a mesma sigma_n' do plano.\n"
        "   - tau_atuante: Tensão de cisalhamento calculada no plano da fratura.\n"
        "   Interpretacão: FS > 1.0 (Estável) | FS <= 1.0 (Falha/Ruptura).\n\n"
        "5. GEOMETRIA DO PLANO:\n"
        "   - Mergulho: Inclinação da fratura em relação à horizontal.\n"
        "   - Regime Normal: s1 é Vertical (Gravidade). S3 é Horizontal.\n"
        "   - Regime Reverso: s1 é Horizontal (Compressão). S3 é Vertical.\n\n"
        "6. LIMITES DE TRAÇÃO E COLAPSO:\n"
        "   - Tração (Ts): Define a resistência à tração da rocha. A falha ocorre de forma\n"
        "     parabólica (Griffith modificado) conectando a coesão ao limite negativo.\n"
        "   - Colapso (Pc): Define o limite de esmagamento de poros (Cap Yield).\n\n"
        "7. COMPORTAMENTO DO CÍRCULO:\n"
        "   O círculo de Mohr deforma-se fisicamente (colapso) ao tocar as envoltorias:\n"
        "   - AZUL: Ruptura por Tração (Sigma' < 0).\n"
        "   - VERMELHO: Ruptura por Cisalhamento (Mohr-Coulomb).\n"
        "   - VERDE: Colapso de Poros (Sigma' > Pc)."
    )
    plt.text(0.05, 0.95, txt, transform=help_fig.transFigure, fontsize=10, 
             verticalalignment='top', family='monospace', linespacing=1.4,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.15))
    plt.axis('off')
    plt.show()

# --- Setup da Interface ---
fig = plt.figure(figsize=(15, 9), facecolor='#f0f2f5')
plt.subplots_adjust(left=0.05, bottom=0.18, right=0.95, top=0.88)
fig.suptitle('JocaMohr', fontsize=22, fontweight='bold', color='#2c3e50', y=0.96)

ax_help = plt.axes([0.90, 0.93, 0.05, 0.03])
btn_help = Button(ax_help, 'AJUDA ?', color='#d1d8e0')
btn_help.on_clicked(abrir_ajuda)

ax1 = fig.add_subplot(121, projection='3d', proj_type='ortho') 
ax2 = fig.add_subplot(122)                   

# Linhas do Círculo
mohr_stable, = ax2.plot([], [], color='#1f77b4', lw=2, zorder=5) 
mohr_shear,  = ax2.plot([], [], color='red', lw=3.5, zorder=6)   
mohr_tens,   = ax2.plot([], [], color='blue', lw=3.5, zorder=6)  
mohr_coll,   = ax2.plot([], [], color='green', lw=3.5, zorder=6) 

mohr_env,    = ax2.plot([], [], color='#d62728', ls='--', lw=1.5, zorder=4)
mohr_point,  = ax2.plot([], [], 'o', color='#2ca02c', markersize=8, zorder=7)
status_text  = ax2.text(0.05, 0.92, '', transform=ax2.transAxes, fontsize=12, fontweight='bold')

# Rótulos
txt_tens  = ax2.text(-48, 5, 'Ruptura por tração', color='blue', fontsize=8, fontweight='bold', ha='left')
txt_shear = ax2.text(0, 0, 'Ruptura por cisalhamento', color='red', fontsize=8, fontweight='bold', ha='center')
txt_coll  = ax2.text(0, 0, 'Colapso de poros', color='green', fontsize=8, fontweight='bold', ha='left')

ax2.set_xlim(-50, 200); ax2.set_ylim(0, 100); ax2.set_aspect('equal')
ax2.set_xlabel(r'$\sigma_n$ (MPa)'); ax2.set_ylabel(r'$\tau$ (MPa)')
ax2.grid(True, linestyle=':', alpha=0.4); ax2.axvline(0, color='black', lw=1.5, alpha=0.6, zorder=2)

# Janelas
for label, xpos in [('TENSÕES', 0.12), ('PROPRIEDADES DA ROCHA', 0.31), ('PROPRIEDADES DO PLANO', 0.62)]:
    fig.text(xpos, 0.13, label, fontsize=9, fontweight='bold', color='#2c3e50')
rect_t = patches.Rectangle((0.05, 0.02), 0.22, 0.13, lw=1, edgecolor='#bdc3c7', facecolor='#ffffff', transform=fig.transFigure, zorder=-1)
rect_r = patches.Rectangle((0.30, 0.02), 0.28, 0.13, lw=1, edgecolor='#bdc3c7', facecolor='#ffffff', transform=fig.transFigure, zorder=-1)
rect_p = patches.Rectangle((0.61, 0.02), 0.28, 0.13, lw=1, edgecolor='#bdc3c7', facecolor='#ffffff', transform=fig.transFigure, zorder=-1)
fig.patches.extend([rect_t, rect_r, rect_p])

def update(val):
    global regime_atual
    s1, s3, pp, alpha, c, phi, mergulho = s_s1.val, s_s3.val, s_pp.val, s_alpha.val, s_c.val, s_phi.val, s_ang.val
    ts, pc = s_ts.val, s_pc.val
    if s1 < s3: s1 = s3 
    
    s1_eff, s3_eff = s1 - (alpha * pp), s3 - (alpha * pp)
    centro_m, raio_m = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2
    
    # --- Geometria da Envoltória (Parábola na Tração) ---
    x_env = np.linspace(-ts, pc, 1000)
    tan_phi = np.tan(np.radians(phi))
    xt_coll = (pc + (c / tan_phi)) / 2
    
    y_env = np.zeros_like(x_env)
    for i, x in enumerate(x_env):
        if x < 0:
            # PARÁBOLA DE GRIFFITH (tau^2 = k * (sigma + Ts))
            # Ajustamos k para que a parábola passe por (0, c)
            k = (c**2) / (ts if ts > 0 else 0.001)
            y_env[i] = np.sqrt(max(0, k * (x + ts)))
        elif x < xt_coll:
            y_env[i] = c + x * tan_phi
        else:
            a_c, b_c = pc - xt_coll, c + xt_coll * tan_phi
            y_env[i] = b_c * np.sqrt(np.maximum(0, 1 - ((x - xt_coll)**2 / a_c**2)))
    
    txt_shear.set_position((xt_coll/2, (c + (xt_coll/2)*tan_phi) + 2.5)); txt_shear.set_rotation(phi)
    txt_coll.set_position((pc - 45, (c + xt_coll * tan_phi) + 12))

    t_c = np.linspace(0, np.pi, 1000); x_circ = centro_m + raio_m * np.cos(t_c); y_circ = raio_m * np.sin(t_c)
    res_interp = np.interp(x_circ, x_env, y_env, left=0, right=0)
    x_final, y_final = np.clip(x_circ, -ts, pc), np.minimum(y_circ, res_interp)
    
    m_fail = y_circ > res_interp
    m_t_p, m_c_p = x_circ < -ts, x_circ > pc
    m_tens, m_coll = m_t_p | (m_fail & (x_circ < 0)), m_c_p | (m_fail & (x_circ > xt_coll))
    m_shear, m_stable = m_fail & (~m_tens) & (~m_coll), (~m_fail) & (~m_t_p) & (~m_c_p)

    mohr_stable.set_data(np.where(m_stable, x_final, np.nan), np.where(m_stable, y_final, np.nan))
    mohr_shear.set_data(np.where(m_shear, x_final, np.nan), np.where(m_shear, y_final, np.nan))
    mohr_tens.set_data(np.where(m_tens, x_final, np.nan), np.where(m_tens, y_final, np.nan))
    mohr_coll.set_data(np.where(m_coll, x_final, np.nan), np.where(m_coll, y_final, np.nan))
    mohr_env.set_data(x_env, y_env)
    
    theta_rel = mergulho if regime_atual == 'Normal' else 90 - mergulho
    sn = centro_m + raio_m * np.cos(np.radians(2 * theta_rel))
    tn_te = abs(raio_m * np.sin(np.radians(2 * theta_rel)))
    sn_clamped = np.clip(sn, -ts, pc)
    tn_re = min(tn_te, np.interp(sn_clamped, x_env, y_env))
    mohr_point.set_data([sn_clamped], [tn_re])

    # --- Render 3D Original ---
    ax1.clear(); ax1.set_axis_off(); ax1.view_init(elev=20, azim=s_giro.val)
    R, H_lim = 0.5, 0.8; m_vis = 89.99 if mergulho >= 90 else (0.01 if mergulho <= 0 else mergulho)
    m_rad = np.radians(m_vis)
    u_surf, h_surf = np.meshgrid(np.linspace(0, 2*np.pi, 50), np.linspace(-H_lim, H_lim, 2))
    grid = np.linspace(-1.2, 1.2, 35); u_f, v_f = np.meshgrid(grid, grid); u_f, v_f = u_f.flatten(), v_f.flatten()

    if regime_atual == 'Normal':
        xp, yp, zp = u_f * np.cos(m_rad), v_f, u_f * np.sin(m_rad)
        mask = (xp**2 + yp**2 <= R**2) & (np.abs(zp) <= H_lim)
        v_s1, v_s2, v_s3 = [0,0,1], [0,1,0], [1,0,0]
        ax1.plot_surface(R*np.cos(u_surf), R*np.sin(u_surf), h_surf, color='gray', alpha=0.05, shade=False)
        n, t_vec = np.array([-np.sin(m_rad), 0, np.cos(m_rad)]), np.array([np.cos(m_rad), 0, np.sin(m_rad)])
    else:
        xp, yp, zp = u_f * np.cos(m_rad), v_f, -u_f * np.sin(m_rad)
        mask = (yp**2 + zp**2 <= R**2) & (np.abs(xp) <= H_lim)
        v_s1, v_s2, v_s3 = [1,0,0], [0,1,0], [0,0,1]
        ax1.plot_surface(h_surf, R*np.cos(u_surf), R*np.sin(u_surf), color='gray', alpha=0.05, shade=False)
        n, t_vec = np.array([np.cos(m_rad), 0, -np.sin(m_rad)]), np.array([-np.sin(m_rad), 0, -np.cos(m_rad)])

    if np.any(mask): ax1.plot_trisurf(xp[mask], yp[mask], zp[mask], color='#ff7f0e', alpha=0.8, shade=True)
    for vec, col, lbl in zip([v_s1, v_s2, v_s3], ['#d32f2f', '#388e3c', '#1976d2'], [r"$\sigma_1$", r"$\sigma_2$", r"$\sigma_3$"]):
        ax1.quiver(vec[0]*1.1, vec[1]*1.1, vec[2]*1.1, -vec[0]*0.2, -vec[1]*0.2, -vec[2]*0.2, color=col, lw=2)
        ax1.text(vec[0]*1.3, vec[1]*1.3, vec[2]*1.3, lbl, color=col, ha='center')

    s_sc, t_sc = 0.5 * (sn/200), 0.5 * (tn_re/100)
    ax1.quiver(0,0,0, n[0]*s_sc, n[1]*s_sc, n[2]*s_sc, color='black', lw=3)
    ax1.text(n[0]*s_sc*1.2, n[1]*s_sc*1.2, n[2]*s_sc*1.2, r"$\sigma_n$", color='black', fontsize=11, ha='center')
    ax1.quiver(0,0,0, t_vec[0]*t_sc, t_vec[1]*t_sc, t_vec[2]*t_sc, color='blue', lw=3)
    ax1.text(t_vec[0]*t_sc*1.2, t_vec[1]*t_sc*1.2, t_vec[2]*t_sc*1.2, r"$\tau$", color='blue', fontsize=11, ha='center')

    ax1.set_xlim(-1, 1); ax1.set_ylim(-1, 1); ax1.set_zlim(-1, 1); ax1.set_box_aspect([1, 1, 1])
    fs = np.interp(sn_clamped, x_env, y_env) / tn_te if tn_te > 0.1 else 10.0
    status_text.set_text(f"FS: {fs:.2f} | {regime_atual}"); status_text.set_color('red' if (fs <= 1.0 or sn < -ts or sn > pc) else 'darkgreen')
    fig.canvas.draw_idle()

# --- Callbacks ---
def reiniciar_tensao(event): s_s1.set_val(DEFAULTS['s1']); s_s3.set_val(DEFAULTS['s3']); s_pp.set_val(DEFAULTS['pp'])
def reiniciar_rocha(event): s_alpha.set_val(DEFAULTS['alpha']); s_c.set_val(DEFAULTS['c']); s_phi.set_val(DEFAULTS['phi']); s_ts.set_val(DEFAULTS['ts']); s_pc.set_val(DEFAULTS['pc'])
def reiniciar_plano(event): s_ang.set_val(60 if regime_atual == 'Normal' else 30)

# Sliders
s_s1 = Slider(plt.axes([0.10, 0.09, 0.14, 0.02]), r'$\sigma_1$', 0, 220, valinit=DEFAULTS['s1'], valfmt='%1.0f')
s_s3 = Slider(plt.axes([0.10, 0.06, 0.14, 0.02]), r'$\sigma_3$', 0, 200, valinit=DEFAULTS['s3'], valfmt='%1.0f')
s_pp = Slider(plt.axes([0.10, 0.03, 0.14, 0.02]), 'P.Poros', 0, 100, valinit=DEFAULTS['pp'], valfmt='%1.0f')
btn_rst_t = Button(plt.axes([0.22, 0.125, 0.045, 0.02]), 'Reiniciar', color='#f0f0f0'); btn_rst_t.on_clicked(reiniciar_tensao)

s_alpha = Slider(plt.axes([0.38, 0.11, 0.14, 0.015]), 'Biot α', 0, 1.0, valinit=DEFAULTS['alpha'])
s_c     = Slider(plt.axes([0.38, 0.09, 0.14, 0.015]), 'Coesão', 0, 50, valinit=DEFAULTS['c'], valfmt='%1.0f')
s_phi   = Slider(plt.axes([0.38, 0.07, 0.14, 0.015]), 'Atrito', 0, 60, valinit=DEFAULTS['phi'], valfmt='%1.0f')
s_ts    = Slider(plt.axes([0.38, 0.05, 0.14, 0.015]), 'Tração', 1, 50, valinit=DEFAULTS['ts'], valfmt='%1.0f')
s_pc    = Slider(plt.axes([0.38, 0.03, 0.14, 0.015]), 'Colapso', 50, 220, valinit=DEFAULTS['pc'], valfmt='%1.0f')
btn_rst_r = Button(plt.axes([0.53, 0.125, 0.045, 0.02]), 'Reiniciar', color='#f0f0f0'); btn_rst_r.on_clicked(reiniciar_rocha)

s_ang   = Slider(plt.axes([0.70, 0.08, 0.14, 0.02]), 'Mergulho', 0, 90, valinit=DEFAULTS['ang'], valfmt='%1.0f')
btn_rst_p = Button(plt.axes([0.84, 0.125, 0.045, 0.02]), 'Reiniciar', color='#f0f0f0'); btn_rst_p.on_clicked(reiniciar_plano)

s_giro = Slider(plt.axes([0.15, 0.19, 0.24, 0.025]), 'Giro Horizontal', 0, 360, valinit=DEFAULTS['giro'], valfmt='%1.0f')
btn_norm = Button(plt.axes([0.15, 0.23, 0.11, 0.03]), 'Normal', color='#add8e6')
btn_rev  = Button(plt.axes([0.28, 0.23, 0.11, 0.03]), 'Reverso', color='#f0f0f0')

def change_reg(r): 
    global regime_atual; regime_atual = r; s_giro.set_val(45)
    btn_norm.color, btn_rev.color = ('#add8e6', '#f0f0f0') if r == 'Normal' else ('#f0f0f0', '#ffcccb')
    update(None)

btn_norm.on_clicked(lambda x: change_reg('Normal')); btn_rev.on_clicked(lambda x: change_reg('Reverso'))
for s in [s_s1, s_s3, s_pp, s_alpha, s_c, s_phi, s_ang, s_giro, s_ts, s_pc]: s.on_changed(update)

update(None)
plt.show()
