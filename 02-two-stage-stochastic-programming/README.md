# Two-stage stochastic programming – assembly-to-order

Production planning for a small food chain: components are prepared in the morning (first stage) before the demand for the four final products is known (second stage), under oven and staff time limits.

- Demand is a mixture of two normal regimes: a standard day (80 %) and a peak day (20 %).
- **Stability:** in-sample and out-of-sample comparison as the number of scenarios grows (stable from about 20 scenarios).
- **Value of the stochastic solution:** RP, WS and EEV give VSS ≈ 39 € and EVPI ≈ 60 € per day.
- **Robustness:** cost of planning with an underestimated peak probability (5 % instead of 20 %), evaluated on 1,000 out-of-sample scenarios.

**Report (Italian):** [report.pdf](report.pdf)

## Files

| File | Content |
| --- | --- |
| `dati.py` | data, demand scenario generator, model solved with Gurobi |
| `grafico_domanda.py` | plot of the bimodal demand |
| `stabilita.py` | in-sample / out-of-sample stability |
| `metriche.py` | RP, WS, EEV, VSS, EVPI |
| `robustezza.py` | robustness to a biased estimate |

## Run

Requires Python 3 with `numpy`, `matplotlib` and `gurobipy` (a free academic Gurobi licence is needed for full-size models).

```
pip install -r requirements.txt
python stabilita.py
```
