clc; clear; close all;
rng(123); 

clc; clear; close all;
rng(123); 

% SCENARIO 1: impatto della dimensione dello storico dati sulla stima della domanda

% Parametri globali
media_vera = 500; % valore atteso reale della domanda
dev_std_vera = 120; % deviazione standard reale della domanda
costo_acquisto = 40; % costo unitario
prezzo_vendita = 90; % prezzo di vendita
valore_recupero = 15; % prezzo di svendita

% Calcolo dei costi marginali 
cu = prezzo_vendita - costo_acquisto; % costo underage
co = costo_acquisto - valore_recupero; % costo overage

z_vero = norminv(cu / (cu + co)); %quantile della normale standard
Q_ottima = media_vera + dev_std_vera * z_vero; %calcolo della quantità ottima da ordinare partendo da z
loss = normpdf(z_vero) - z_vero * (1 - normcdf(z_vero)); %funzione di perdita
profitto_teorico = cu * media_vera - co * (Q_ottima - media_vera) - (cu + co) * dev_std_vera * loss;

giorni_oss_vettore = 5:5:500; % sequenza dei giorni di osservazione da 5 a 500 con passo 5
giorni_vendita = 10000;
num_simulazioni = 1000;
errori_rapporto_p1 = zeros(length(giorni_oss_vettore), 1);

for i = 1:length(giorni_oss_vettore)
    rapporti_tmp = zeros(num_simulazioni, 1);
    
    for j = 1:num_simulazioni 
        % stima dei parametri della domanda basata sul campione storico
        [media_camp, dev_std_camp] = stima_parametri_domanda(giorni_oss_vettore(i), media_vera, dev_std_vera);
        
        % calcolo della quantità ottima campionaria
        Q_campionaria = media_camp + dev_std_camp * z_vero; 
        
        % calcolo dell'efficienza rispetto al profitto teorico
        rapporti_tmp(j) = simula_profitto_recupero_fisso(media_vera, dev_std_vera, cu, co, Q_campionaria, profitto_teorico, giorni_vendita);
    end
    errori_rapporto_p1(i) = mean(rapporti_tmp);
end

figure(1);
plot(giorni_oss_vettore, errori_rapporto_p1, 'b', 'LineWidth', 2);
title('Scenario 1: dimensione storico dati', 'FontWeight', 'bold');
xlabel('Giorni di osservazione');
ylabel('Efficienza profitto');
xlim([0 500]);
grid on;

% SCENARIO 2: incertezza sul prezzo di svendita 

prezzo_vendita_scen2 = 120; 
cu_scen2 = prezzo_vendita_scen2 - costo_acquisto; 
giorni_oss_fissi = 250; 
giorni_oss_recupero_vettore = 5:5:200; 

% definizione dei parametri reali per la distribuzione uniforme del recupero
limite_sup_vero = 0.9; 
limite_inf_vero = 0.3;
tasso_recupero_medio = (limite_sup_vero + limite_inf_vero) / 2;
co_medio = costo_acquisto - (costo_acquisto * tasso_recupero_medio);

% calcolo del profitto ottimo atteso con la funzione di perdita
z_vero_scen2 = norminv(cu_scen2 / (cu_scen2 + co_medio)); 
Q_ottima_scen2 = media_vera + dev_std_vera * z_vero_scen2; 
loss_scen2 = normpdf(z_vero_scen2) - z_vero_scen2 * (1 - normcdf(z_vero_scen2));
profitto_teorico_scen2 = cu_scen2 * media_vera - co_medio * (Q_ottima_scen2 - media_vera) - (cu_scen2 + co_medio) * dev_std_vera * loss_scen2;

errori_rapporto_p2 = zeros(length(giorni_oss_recupero_vettore), 1);

for i = 1:length(giorni_oss_recupero_vettore)
    rapporti_tmp = zeros(num_simulazioni, 1);
    
    for j = 1:num_simulazioni
        % stima della domanda e del tasso di recupero
        [media_camp, dev_std_camp] = stima_parametri_domanda(giorni_oss_fissi, media_vera, dev_std_vera);
        tasso_recupero_camp = stima_tasso_recupero(giorni_oss_recupero_vettore(i), limite_sup_vero, limite_inf_vero);
        
        % calcolo dei costi marginali campionari e della quantità ordinata
        co_camp = costo_acquisto - (costo_acquisto * tasso_recupero_camp); 
        z_camp = norminv(cu_scen2 / (cu_scen2 + co_camp));
        Q_campionaria = media_camp + dev_std_camp * z_camp; 
        
        % simulazione del profitto con recupero distribuito uniformemente
        rapporti_tmp(j) = simula_profitto_recupero_uniforme(costo_acquisto, prezzo_vendita_scen2, limite_sup_vero, limite_inf_vero, media_vera, dev_std_vera, Q_campionaria, profitto_teorico_scen2, giorni_vendita);
    end
    errori_rapporto_p2(i) = mean(rapporti_tmp);
end

figure(2);
plot(giorni_oss_recupero_vettore, errori_rapporto_p2, 'r', 'LineWidth', 2);
title('Scenario 2: incertezza
sul prezzo di svendita', 'FontWeight', 'bold');
xlabel('Giorni osservazione svendite');
ylabel('Efficienza profitto');
xlim([0 200]);
grid on;


% SCENARIO 3: Bilanciamento tra costo di understocking Cu e overstocking Co

co_fisso = 50; 
rapporto_costi_vettore = logspace(log10(0.1), log10(20), 30); %scala logaritmica per garantire la stessa risoluzione grafica sia per Cu << Co che per Cu >> Co
errori_rapporto_p3 = zeros(length(rapporto_costi_vettore), 1);

for i = 1:length(rapporto_costi_vettore)
    rapporti_tmp = zeros(num_simulazioni, 1);
    cu_dinamico = rapporto_costi_vettore(i) * co_fisso; 
    
    % calcolo del profitto massimo possibile (se conoscessi il futuro)
    z_vero_scen3 = norminv(cu_dinamico / (cu_dinamico + co_fisso)); 
    Q_ottima_scen3 = media_vera + dev_std_vera * z_vero_scen3; 
    loss_scen3 = normpdf(z_vero_scen3) - z_vero_scen3 * (1 - normcdf(z_vero_scen3));
    profitto_teorico_scen3 = cu_dinamico * media_vera - co_fisso * (Q_ottima_scen3 - media_vera) - (cu_dinamico + co_fisso) * dev_std_vera * loss_scen3;
    
    for j = 1:num_simulazioni
        % stima su 30 gg e simulazione
        [media_camp, dev_std_camp] = stima_parametri_domanda(30, media_vera, dev_std_vera);
        Q_campionaria = media_camp + dev_std_camp * z_vero_scen3; 
        rapporti_tmp(j) = simula_profitto_recupero_fisso(media_vera, dev_std_vera, cu_dinamico, co_fisso, Q_campionaria, profitto_teorico_scen3, giorni_vendita);
    end
    errori_rapporto_p3(i) = mean(rapporti_tmp);
end

figure(3);
semilogx(rapporto_costi_vettore, errori_rapporto_p3, 'Color', [0 1 0], 'LineWidth', 2);
title('Scenario 3: bilanciamento costi', 'FontWeight', 'bold');
xlabel('Rapporto Cu / Co (log)');
ylabel('Efficienza profitto');
xlim([0.1 20]);
grid on;

% SCENARIO 4: rapporto Sigma/Mu

co_scen4 = 25; 
cu_scen4 = 50; 
sigma_su_mu_vettore = linspace(0.02, 0.28, 20); % crea 20 valori del rapporto sigma/mu equispaziati tra 0.02 e 0.28
z_vero_scen4 = norminv(cu_scen4 / (cu_scen4 + co_scen4)); 

errori_p4_pochi = zeros(length(sigma_su_mu_vettore), 1);
errori_p4_molti = zeros(length(sigma_su_mu_vettore), 1);

for i = 1:length(sigma_su_mu_vettore)
    dev_std_dinamica = media_vera * sigma_su_mu_vettore(i); 
   
    % calcolo del profitto massimo possibile con la deviazione standard aggiornata
    Q_ottima_scen4 = media_vera + dev_std_dinamica * z_vero_scen4; 
    loss_scen4 = normpdf(z_vero_scen4) - z_vero_scen4 * (1 - normcdf(z_vero_scen4));
    profitto_teorico_scen4 = cu_scen4 * media_vera - co_scen4 * (Q_ottima_scen4 - media_vera) - (cu_scen4 + co_scen4) * dev_std_dinamica * loss_scen4;
        
    rapporti_tmp_pochi = zeros(num_simulazioni, 1);
    rapporti_tmp_molti = zeros(num_simulazioni, 1);
    
    for j = 1:num_simulazioni
        % Simulazione con storico limitato (10 giorni)
        [m_camp_10, s_camp_10] = stima_parametri_domanda(10, media_vera, dev_std_dinamica);
        Q_camp_10 = m_camp_10 + s_camp_10 * z_vero_scen4; 
        rapporti_tmp_pochi(j) = simula_profitto_recupero_fisso(media_vera, dev_std_dinamica, cu_scen4, co_scen4, Q_camp_10, profitto_teorico_scen4, giorni_vendita);
        
        % Simulazione con storico ampio (250 giorni)
        [m_camp_250, s_camp_250] = stima_parametri_domanda(250, media_vera, dev_std_dinamica);
        Q_camp_250 = m_camp_250 + s_camp_250 * z_vero_scen4; 
        rapporti_tmp_molti(j) = simula_profitto_recupero_fisso(media_vera, dev_std_dinamica, cu_scen4, co_scen4, Q_camp_250, profitto_teorico_scen4, giorni_vendita);
    end
    
    errori_p4_pochi(i) = mean(rapporti_tmp_pochi);
    errori_p4_molti(i) = mean(rapporti_tmp_molti);
end

figure(4);
plot(sigma_su_mu_vettore, errori_p4_pochi, 'r', 'LineWidth', 2);
hold on;
plot(sigma_su_mu_vettore, errori_p4_molti, 'm', 'LineWidth', 2);
title('Scenario 4: variabilità della domanda', 'FontWeight', 'bold'); % Usato il termine "variabilità" che abbiamo scelto
xlabel('Rapporto \sigma / \mu');
ylabel('Efficienza profitto');
xlim([0 0.3]);
legend('pochi dati: 10 gg', 'molti dati: 250 gg', 'Location', 'southwest');
grid on;
hold off;
