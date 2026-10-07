function [errore_relativo, errore_assoluto] = simula_profitto_recupero_variabile(costo_acquisto, prezzo_vendita, media_camp, dev_std_camp, media_vera, dev_std_vera, tasso_recupero_camp, num_simulazioni, k_sup, k_inf, limite_sup_max, limite_inf_max)
 % Calcola l'errore assoluto e relativo utilizzando parametri campionari per determinare la quantità ottima in uno scenario dove il prezzo di svendita dell'invenduto è stocastico e decresce esponenzialmente in base alla quantità avanzata.
   
    % calcolo costi marginali basati su campione
    cu_camp = prezzo_vendita - costo_acquisto;
    co_camp = costo_acquisto - (costo_acquisto * tasso_recupero_camp); 
    
    z_camp = norminv(cu_camp / (cu_camp + co_camp));
    quantita_ordinata = media_camp + dev_std_camp * z_camp; 
    
    %simulazione Monte Carlo
    domanda_effettiva = max(0, normrnd(media_vera, dev_std_vera, [num_simulazioni, 1])); 
    invenduto = max(0, quantita_ordinata - domanda_effettiva);
    
    r_sup = limite_sup_max * exp(-k_sup * invenduto);
    r_inf = limite_inf_max * exp(-k_inf * invenduto);
    r_sup = max(r_sup, r_inf + 0.01); 
    
    valore_recupero_simulato = r_inf + (r_sup - r_inf) .* rand(size(invenduto));
    vendite = min(quantita_ordinata, domanda_effettiva);
    
    % Calcolo profitti simulati
    profitti = prezzo_vendita .* vendite + valore_recupero_simulato .* invenduto - costo_acquisto .* quantita_ordinata;
    
    % Calcolo del valore di recupero teorico medio
    valore_recupero_teorico = (limite_sup_max + limite_inf_max) / 2;
    
    % Definizione dei costi marginali veri
    cu = prezzo_vendita - costo_acquisto; 
    co = costo_acquisto - valore_recupero_teorico; 
    
    % calcolo della Q ottima vera
    z_vero = norminv(cu / (cu + co));
    Q_ottima = media_vera + dev_std_vera * z_vero;
    
    % calcolo del profitto ottimo atteso tramite la funzione di perdita
    loss_function = normpdf(z_vero) - z_vero * (1 - normcdf(z_vero));
    profitto_ottimo = cu * media_vera - co * (Q_ottima - media_vera) - (cu + co) * dev_std_vera * loss_function;
    
    %calcolo errori
    errore_relativo = mean(profitti) / profitto_ottimo;
    errore_assoluto = abs(mean(profitti) - profitto_ottimo);
end