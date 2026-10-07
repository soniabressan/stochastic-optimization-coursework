function [media_camp, dev_std_camp] = stima_parametri_domanda(num_osservazioni, media_vera, dev_std_vera)
    % Simula lo storico della domanda.
    
    % Generazione del campione di domanda
    campione_domanda = normrnd(media_vera, dev_std_vera, [num_osservazioni, 1]);
    
    % Calcolo delle statistiche campionarie
    media_camp = mean(campione_domanda);
    dev_std_camp = std(campione_domanda);
end