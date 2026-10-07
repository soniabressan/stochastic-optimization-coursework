function [tasso_recupero_campionario] = stima_tasso_recupero(num_osservazioni, limite_sup_vero, limite_inf_vero)
    % Simula lo storico del prezzo di svendita.
    
    % Generazione dei campioni da una distribuzione uniforme
    campioni_recupero = limite_inf_vero + (limite_sup_vero - limite_inf_vero) * rand(num_osservazioni, 1);
    
    % Restituisce il valore medio osservato
    tasso_recupero_campionario = mean(campioni_recupero);
end