import gurobipy as gp
from gurobipy import GRB
import numpy as np
import matplotlib.pyplot as plt
from dati import *

# in questo script calcoliamo VSS e EVPI confrontando i modelli stocastici e deterministici

np.random.seed(123)

N = 100 # numero di scenari per valutare le metriche stocastiche in modo stabile

# genero l'albero degli scenari su cui valutiamo tutti i modelli
domanda_S = genera_domanda(N, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)

# 1. RP: uso la funzione già pronta per trovare spesa ottima e profitto su tutti i 100 scenari
x_RP, val_RP = risolvi_modello(domanda_S)

# 2. WS: calcolo il profitto perfetto conoscendo la domanda in anticipo
val_WS_totale = 0
for s in range(N):
    m_WS = gp.Model(f"WS_{s}")
    m_WS.setParam('OutputFlag', 0) 
    x_WS = m_WS.addMVar(shape=len(costi), lb=0.0)
    y_WS = m_WS.addMVar(shape=len(prezzi), lb=0.0)
    
    m_WS.setObjective(-(costi @ x_WS) + (prezzi @ y_WS), GRB.MAXIMIZE)
    m_WS.addConstr(x_WS @ tempi_necessari <= disp_temp)
    m_WS.addConstr(y_WS <= domanda_S[:, s]) 
    m_WS.addConstr((gozinto @ y_WS) <= x_WS)
    
    m_WS.optimize()
    if m_WS.status == GRB.OPTIMAL:
        val_WS_totale += m_WS.ObjVal

val_WS = val_WS_totale / N # media degli scenari perfetti (il nostro tetto massimo)

# 3. EV: decido la spesa x basandomi solo sulla media matematica della domanda
domanda_media = np.mean(domanda_S, axis=1) 

m_EV = gp.Model("EV")
m_EV.setParam('OutputFlag', 0) 
x_EV = m_EV.addMVar(shape=len(costi), lb=0.0)
y_EV = m_EV.addMVar(shape=len(prezzi), lb=0.0)

m_EV.setObjective(-(costi @ x_EV) + (prezzi @ y_EV), GRB.MAXIMIZE)
m_EV.addConstr(x_EV @ tempi_necessari <= disp_temp)
m_EV.addConstr(y_EV <= domanda_media)
m_EV.addConstr((gozinto @ y_EV) <= x_EV)

m_EV.optimize()
x_ingenuo = x_EV.X # salvo la decisione presa usando solo la media

# 4. EEV: uso la funzione già pronta per valutare quanti soldi fa la spesa ingenua (x_ingenuo) sui 100 scenari
val_EEV = valuta_out_of_sample_sicuro(x_ingenuo, domanda_S)

# EVPI: valore dell'informazione perfetta (WS - RP)
EVPI = val_WS - val_RP

# VSS: valore della soluzione stocastica rispetto a quella media (RP - EEV)
VSS = val_RP - val_EEV

print(" RISULTATI METRICHE STOCASTICHE ")
print(f"Profitto EEV: {val_EEV:.2f} €")
print(f"Profitto RP: {val_RP:.2f} €")
print(f"Profitto WS: {val_WS:.2f} €")
print(f"EVPI: {EVPI:.2f} €")
print(f"VSS:  {VSS:.2f} €")

# grafico per confrontare EEV, RP e WS
plt.style.use('seaborn-v0_8-whitegrid')
valori_plot = [val_EEV, val_RP, val_WS]
etichette = ['EEV', 'RP', 'WS']

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(etichette, valori_plot, color=['#ff9896', '#2ca02c', '#aec7e8'], edgecolor='black')

for bar in bars:
    altezza = bar.get_height()
    ax.annotate(f'{altezza:.2f} €',
                xy=(bar.get_x() + bar.get_width() / 2, altezza),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold')

ax.annotate(f'VSS = {VSS:.2f} €', xy=(0.5, val_RP - (VSS/2)), xytext=(0.5, val_RP - (VSS/2)), ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", lw=2))
ax.annotate(f'EVPI = {EVPI:.2f} €', xy=(1.5, val_WS - (EVPI/2)), xytext=(1.5, val_WS - (EVPI/2)), ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="blue", lw=2))

plt.title('Analisi comparativa del profitto atteso: confronto tra i modelli EEV, RP e WS', fontsize=14, pad=15)
plt.ylabel('Profitto Medio (€)', fontsize=12)
plt.ylim(0, max(valori_plot) * 1.15) 
plt.tight_layout()
plt.show()