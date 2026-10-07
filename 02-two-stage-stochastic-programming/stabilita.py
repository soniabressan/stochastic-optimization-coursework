import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math
import matplotlib.pyplot as plt
from dati import *

# in questo script analizziamo la stabilità In-Sample e Out-of-Sample della soluzione al variare di N

np.random.seed(123)

N_sim = 100 # numero di repliche indipendenti per costruire l'intervallo di confidenza 
big_N = 1000 # numero di scenari per simulare il mondo reale (out-of-sample)

# genero l'albero oos del mondo reale una volta sola
domanda_E = genera_domanda(big_N, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)

lista_n_scenario = [5, 10, 20, 50]
plot_scenari, plot_medie_is, plot_errori_is, plot_medie_oos, plot_errori_oos = [], [], [], [], []

for n_scenario in lista_n_scenario:
    differenze_is = np.zeros(N_sim)
    differenze_oos = np.zeros(N_sim)
    print(f"\n Testando N = {n_scenario} scenari")

    for i in range(N_sim): 
        # risolvo due alberi diversi (S e S') con stesso N per vedere se il profitto è instabile
        dom_S = genera_domanda(n_scenario, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)
        x_S, prof_IS_S = risolvi_modello(dom_S)
        
        dom_S_prime = genera_domanda(n_scenario, p_vero, mu_vero_succ, sig_vero_succ, mu_vero_norm, sig_vero_norm)
        x_S_prime, prof_IS_S_prime = risolvi_modello(dom_S_prime)
        
        # diff IS: confronto i profitti stimati internamente dalle due funzioni obiettivo
        differenze_is[i] = prof_IS_S - prof_IS_S_prime
        
        # diff OOS: testo le scorte calcolate (x) nel mondo reale indipendente
        profitto_vero_S = valuta_out_of_sample_sicuro(x_S, domanda_E)
        profitto_vero_S_prime = valuta_out_of_sample_sicuro(x_S_prime, domanda_E)
        differenze_oos[i] = profitto_vero_S - profitto_vero_S_prime

    # statistiche in-sample 
    mu_is = np.mean(differenze_is)
    err_is = 1.96 * np.std(differenze_is, ddof=1) / math.sqrt(N_sim)
    
    # statistiche out-of-sample 
    mu_oos = np.mean(differenze_oos)
    err_oos = 1.96 * np.std(differenze_oos, ddof=1) / math.sqrt(N_sim)
    
    plot_scenari.append(n_scenario)
    plot_medie_is.append(mu_is)
    plot_errori_is.append(err_is)
    plot_medie_oos.append(mu_oos)
    plot_errori_oos.append(err_oos)
    
    print(f"IS  - Media diff: {mu_is:.2f}, Intervallo: [{mu_is - err_is:.2f}, {mu_is + err_is:.2f}]")
    print(f"OOS - Media diff: {mu_oos:.2f}, Intervallo: [{mu_oos - err_oos:.2f}, {mu_oos + err_oos:.2f}]")

# grafico a barre di errore
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(9, 6))
plt.errorbar(plot_scenari, plot_medie_is, yerr=plot_errori_is, fmt='-s', color='#2ca02c', label='Diff. In-Sample', alpha=0.9)
plt.errorbar([x + 0.5 for x in plot_scenari], plot_medie_oos, yerr=plot_errori_oos, fmt='-o', color='#1f77b4', label='Diff. Out-of-Sample', alpha=0.9)
plt.axhline(0, color='black', linestyle='--', alpha=0.7)
plt.title('Stabilità In-Sample e Out-of-Sample al variare degli scenari', fontsize=14, pad=15)
plt.xlabel('Numero di scenari (N)', fontsize=12)
plt.ylabel("Differenza di profitto tra alberi (€)", fontsize=12)
plt.xticks(plot_scenari)
plt.legend()
plt.tight_layout()
plt.show()