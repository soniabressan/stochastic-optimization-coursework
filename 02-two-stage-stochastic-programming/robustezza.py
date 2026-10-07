import gurobipy as gp
from gurobipy import GRB
import numpy as np
import matplotlib.pyplot as plt
from dati import *

# in questo script calcoliamo quanto perdiamo se stimiamo male la domanda (gestore pessimista)

np.random.seed(123)

N_opt = 200 # uso 200 scenari per calcolare la spesa (x) in modo stabile
big_N = 1000 # 1000 scenari veri indipendenti per il test sul mondo reale

print("1. Ottimizzazione con modello VERO...")
# genero gli scenari usando le probabilità corrette (p=0.20)
dom_vera_opt = genera_domanda(N_opt, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)

# calcolo la spesa perfetta
x_vera, _ = risolvi_modello(dom_vera_opt)

print("2. Ottimizzazione con modello ERRATO (Pessimista)...")
# genero scenari simulando l'errore del gestore che sottostima i picchi (p=0.05)
dom_errata_opt = genera_domanda(N_opt, p_errato, mu_err_succ, sig_err_succ, mu_vero_norm, sig_vero_norm)

# trovo la spesa "sbagliata" basata sulle stime errate
x_errata, _ = risolvi_modello(dom_errata_opt)

print(f"3. Valutazione sul Mondo Reale ({big_N} scenari veri)...")
# creo il mondo reale usando le probabilità VERE
domanda_reale = genera_domanda(big_N, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)

# testo entrambe le decisioni di spesa sui 1000 scenari reali per vedere quanti soldi fanno davvero
profitto_con_x_vera = valuta_out_of_sample_sicuro(x_vera, domanda_reale)
profitto_con_x_errata = valuta_out_of_sample_sicuro(x_errata, domanda_reale)

# la differenza è il costo dell'errore
differenza = profitto_con_x_vera - profitto_con_x_errata

print("\n--- RISULTATI ROBUSTEZZA ---")
print(f"Profitto ottenuto usando la distribuzione VERA:   {profitto_con_x_vera:.2f} €")
print(f"Profitto ottenuto usando la distribuzione ERRATA: {profitto_con_x_errata:.2f} €")
print(f"Costo dell'errore di stima (Soldi persi):         {differenza:.2f} €")

# grafico
plt.style.use('seaborn-v0_8-whitegrid')
valori_plot = [profitto_con_x_vera, profitto_con_x_errata]
etichette = [f'Distribuzione vera\n(p={p_vero})', f'Distribuzione errata\n(pessimista, p={p_errato})']

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(etichette, valori_plot, color=['#2ca02c', '#d62728'], edgecolor='black', width=0.6)

for bar in bars:
    altezza = bar.get_height()
    ax.annotate(f'{altezza:.2f} €',
                xy=(bar.get_x() + bar.get_width() / 2, altezza),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
plt.title('Test di robustezza: impatto dell\'errore di stima', fontsize=14, pad=15)
plt.ylabel('Profitto reale valutato (Out-of-Sample)', fontsize=12)

min_y = min(valori_plot) - (min(valori_plot) * 0.01)
max_y = max(valori_plot) + (max(valori_plot) * 0.01)
plt.ylim(min_y, max_y)

ax.text(0.5, min_y + ((max_y - min_y) / 2), f"Costo dell'errore:\n- {differenza:.2f} € / giorno", 
        ha='center', va='center', fontsize=12, color='red', fontweight='bold',
        bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.5'))

plt.tight_layout()
plt.show()