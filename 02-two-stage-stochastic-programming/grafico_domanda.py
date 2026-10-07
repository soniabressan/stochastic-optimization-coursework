import numpy as np
import matplotlib.pyplot as plt
from dati import *

# in questo script generiamo la distribuzione bimodale della domanda per la piadina "La leggenda" e la plottiamo
np.random.seed(42)

giorni = 1000
domanda_leggenda = []

# uso i dati reali importati per la Piadina "Leggenda" = prodotto index 0
for s in range(giorni):
    if np.random.rand() < p_vero: 
        domanda_leggenda.append(max(0, np.random.normal(mu_vero_succ[0], sig_vero_succ[0])))
    else: 
        domanda_leggenda.append(max(0, np.random.normal(mu_vero_norm[0], sig_vero_norm[0])))

# plottiamo
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(8, 5))
plt.hist(domanda_leggenda, bins=40, color='#ff7f0e', edgecolor='black', alpha=0.7)

plt.title('Distribuzione bimodale della domanda per la piadina "La leggenda" ', fontsize=14, pad=15)
plt.xlabel('Quantità domandata', fontsize=12)
plt.ylabel('Frequenza (giorni)', fontsize=12)

plt.annotate(f'Giornate normali\n({int((1-p_vero)*100)}% dei casi)', 
             xy=(mu_vero_norm[0], 70), xytext=(mu_vero_norm[0], 90),
             arrowprops=dict(facecolor='black', shrink=0.05), ha='center', fontweight='bold')
plt.annotate(f'Giornate di picco\n({int(p_vero*100)}% dei casi)', 
             xy=(mu_vero_succ[0], 15), xytext=(mu_vero_succ[0], 40),
             arrowprops=dict(facecolor='black', shrink=0.05), ha='center', fontweight='bold')

plt.tight_layout()
plt.show()