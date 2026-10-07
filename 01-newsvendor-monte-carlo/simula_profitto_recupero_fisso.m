function [errore_relativo] = simula_profitto_recupero_fisso(media_vera, dev_std_vera, cu, co, quantita_ordinata, profitto_teorico, giorni_vendita)
    % Calcola il rapporto tra profitto simulato e teorico
    
    % Generazione della domanda effettiva
    domanda_effettiva = max(0, normrnd(media_vera, dev_std_vera, [giorni_vendita, 1])); 
    
    % Calcolo del profitto
    vendite = min(quantita_ordinata, domanda_effettiva);
    invenduto = max(0, quantita_ordinata - domanda_effettiva);
    
    profitto_simulato = cu .* vendite - co .* invenduto; 
    
    % Calcolo dell'errore relativo
    errore_relativo = mean(profitto_simulato) / profitto_teorico;
end