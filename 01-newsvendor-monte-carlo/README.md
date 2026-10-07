# Newsvendor under uncertainty – Monte Carlo study

How much profit is lost when the order quantity of a newsvendor model is computed from *estimated* parameters instead of the true ones?

- The optimal order is Q* = μ + σ·z, with z = Φ⁻¹(cu / (cu + co)); its expected profit is the 100 % efficiency reference.
- The parameters are estimated from a limited history of observations, and the resulting order is tested on 10,000 simulated selling days, repeated 1,000 times.
- Four scenarios: uncertain demand, uncertain salvage value, unbalanced over/under-stocking costs, and increasing demand volatility.

Main finding: efficiency is low and unstable with fewer than ~50 days of data and approaches 100 % after about 100–150 days.

**Report (Italian):** [report.pdf](report.pdf)

## Run

Open MATLAB in this folder and run `main.m`. It produces the four figures of the report.
