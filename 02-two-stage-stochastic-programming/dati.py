import numpy as np
import gurobipy as gp
from gurobipy import GRB

# questo script contiene i dati di input per la simulazione e i parametri di configurazione e le funzioni per generare la domanda e risolvere il modello

# componenti per le piadine: 0=Base, 1=Crudo, 2=Cotto, 3=Formaggi, 4=Verdure
costi = np.array([0.50, 1.50, 1.00, 1.20, 0.50]) 

# tipologie di piadine: 0=Leggenda, 1=Semplice, 2=Sobrietà, 3=Emilia
prezzi = np.array([6.40, 5.90, 4.90, 6.50]) 

# risorse [Piastra, Personale] in minuti (15 ore = 900 min, piastra 600 min effettivi)
disp_temp = np.array([600, 900]) 

# tempi necessari (Componenti x Risorse) in minuti
tempi_necessari = np.array([
    [2.0, 1.0], 
    [0.0, 2.0], 
    [0.0, 1.5], 
    [0.0, 1.0], 
    [0.0, 1.5]  
]) 

# righe (Componenti): [Base, Crudo, Cotto, Formaggi, Verdure]
# colonne (Prodotti): [Leggenda, Semplice, Sobrietà, Emilia]
gozinto = np.array([
    [1, 1, 1, 1], 
    [1, 0, 0, 1], 
    [0, 1, 1, 0], 
    [1, 1, 1, 1], 
    [1, 1, 0, 1]  
]) 

# scenario di riferimento: rappresenta la distribuzione reale osservata sul mercato
p_vero = 0.20 
mu_vero_succ = [80, 100, 50, 70]   
sig_vero_succ = [15, 20, 10, 15] 
mu_vero_norm = [30, 40, 20, 30]    
sig_vero_norm = [5, 8, 4, 5]   

# scenario di stima distorta: rappresenta una previsione basata su parametri sottostimati
p_errato = 0.05 
mu_err_succ = [45, 55, 30, 40]  
sig_err_succ = [10, 12, 6, 8]

def genera_domanda(n_scenari, p, mu_succ, sig_succ, mu_norm, sig_norm):
    # matrice per salvare le domande (righe = prodotti, colonne = scenari)
    dom = np.zeros((len(prezzi), n_scenari))
    for s in range(n_scenari):
        # se esce < p (es. 0.20) sono in una serata di picco, altrimenti serata normale
        if np.random.rand() < p:
            for j in range(len(prezzi)):
                dom[j, s] = max(0, np.random.normal(mu_succ[j], sig_succ[j]))
        else:
            for j in range(len(prezzi)):
                dom[j, s] = max(0, np.random.normal(mu_norm[j], sig_norm[j]))
    return dom

#funzione per risolvere il modello data una matrice di domanda
def risolvi_modello(domanda_matrix):
    n_scen = domanda_matrix.shape[1]
    
    # Creiamo un ambiente per silenziare i log della console
    env = gp.Env(empty=True)
    env.setParam('OutputFlag', 0)
    env.start()
    
    m = gp.Model("ato", env=env)
    
    # variabili decisionali:
    # x = quanti componenti preparo ORA (1° stadio, uguali per ogni scenario)
    # y = quante piadine assemblo DOPO (2° stadio, cambiano per ogni scenario)
    x = m.addMVar(shape=len(costi), lb=0.0)
    y = m.addMVar(shape=(len(prezzi), n_scen), lb=0.0)
    
    # funzione obiettivo: massimizzo differenza tra ricavo medio atteso su tutti gli scenari e costo certo dei componenti comprati oggi
    m.setObjective(-(costi @ x) + (1/n_scen)*((prezzi @ y).sum()), GRB.MAXIMIZE)
    
    # Vincolo 1: non posso superare il tempo a disposizione (piastra e personale)
    m.addConstr(x @ tempi_necessari <= disp_temp)
    
    # Vincolo 2: Non assemblo più piadine di quelle che mi chiedono
    m.addConstr(y <= domanda_matrix)
    
    # Vincolo 3: per ogni scenario gli ingredienti che uso (gozinto * y) non possono superare quelli che ho comprato (x)
    for s in range(n_scen):
        m.addConstr((gozinto @ y[:, s]) <= x)
        
    m.optimize()
    if m.status == GRB.OPTIMAL:
        # Copiamo i valori prima di distruggere il modello
        ris_x = x.X.copy()
        ris_obj = m.ObjVal
        m.dispose()
        env.dispose()
        return ris_x, ris_obj 
    
    m.dispose()
    env.dispose()
    return np.zeros(len(costi)), 0

# funzione per valutare la soluzione out-of-sample su big_N scenari reali
def valuta_out_of_sample_sicuro(x_fissato, domanda_E):
    # qui la x è FISSA: l'ho già decisa al primo stadio e valuto come si comporta su big_N scenari
    n_E = domanda_E.shape[1]
    costo_primo_stadio = np.sum(costi * x_fissato) 
    ricavo_totale_scenari = 0
    
    #per non stampare le 1000 iterazioni
    env = gp.Env(empty=True)
    env.setParam('OutputFlag', 0)
    env.start()
    
    for s in range(n_E):
        m_eval = gp.Model(f"eval_{s}", env=env)
        
        # ora la variabile è solo la y (quante piadine fare)
        y_s = m_eval.addMVar(shape=len(prezzi), lb=0.0)
        
        m_eval.setObjective((prezzi @ y_s), GRB.MAXIMIZE)
        m_eval.addConstr(y_s <= domanda_E[:, s])
        
        # uso la x passata come parametro
        m_eval.addConstr((gozinto @ y_s) <= x_fissato) 
            
        m_eval.optimize()
        if m_eval.status == GRB.OPTIMAL:
            ricavo_totale_scenari += m_eval.ObjVal
            
        # distruggo il modello prima di passare al prossimo scenario 
        m_eval.dispose() 
        
    env.dispose()
    return -costo_primo_stadio + (ricavo_totale_scenari / n_E) 
    # restituisco il profitto medio atteso su big_N scenari reali dato un primo stadio fissato (x_fissato)