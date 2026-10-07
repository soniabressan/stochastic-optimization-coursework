function [errore_relativo] = simula_profitto_recupero_uniforme(costo_acquisto, prezzo_vendita, limite_sup_vero, limite_inf_vero, media_vera, dev_std_vera, quantita_ordinata, profitto_teorico, giorni_vendita)
    % Simula il profitto con tasso di recupero variabile uniformemente.
    
    % Simulazione della domanda
    domanda_effettiva = max(0, normrnd(media_vera, dev_std_vera, [giorni_vendita, 1])); 
    
    % Simulazione del tasso di recupero giornaliero
    tasso_recupero_simulato = limite_inf_vero + (limite_sup_vero - limite_inf_vero) * rand(giorni_vendita, 1);
    valore_recupero = costo_acquisto * tasso_recupero_simulato;
    
    % Calcolo vendite e invenduto
    vendite = min(quantita_ordinata, domanda_effettiva);
    invenduto = max(0, quantita_ordinata - domanda_effettiva);
    
    % Calcolo del profitto
    profitto_simulato = prezzo_vendita .* vendite + valore_recupero .* invenduto - costo_acquisto .* quantita_ordinata;
    
    % Rapporto di errore
    errore_relativo = mean(profitto_simulato) / profitto_teorico;
end