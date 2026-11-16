# IFRS 9 Expected Credit Loss (ECL) Engine

[![Live Demo](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B)](https://ifrs9-ecl-engine-sahilmehta.streamlit.app)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

An end-to-end credit risk pipeline that estimates Expected Credit Loss under IFRS 9, built on LendingClub's 2007–2018 loan data. This started as an M.Tech project at NMIMS but ended up being a full attempt at replicating how a bank's risk team would actually model, calibrate, and stress-test provisioning numbers from raw loan tapes all the way to a dashboard a risk analyst could use day to day.

## What it does

Given a portfolio of loans, the engine predicts three components of credit loss and combines them:

**ECL = PD × LGD × EAD**

- **PD (Probability of Default)** - a calibrated Gradient Boosting model, trained with Weight-of-Evidence encoded features selected using Information Value
- **LGD (Loss Given Default)** - a regression model trained only on the ~26.7K loans that actually defaulted, then applied across the full portfolio
- **EAD (Exposure at Default)** - an exposure-at-default model: EAD observed on defaulted loans (funded amount minus principal repaid), averaged by term x grade and applied to every loan, so no loan's own outcome sets its exposure

The result gets staged under IFRS 9 (Stage 1/2/3 based on PD thresholds), stress-tested under macro scenarios, and backtested against four regulatory benchmarks.

## Results

| Metric | Value |
|---|---|
| PD model AUC | 0.7101 |
| Gini coefficient | 0.4202 |
| KS statistic | 0.3072 |
| Calibration gap (post Platt Scaling) | 23.80% → 0.07% |
| LGD model RMSE / R² | 0.2007 / 0.1914 |
| Portfolio EAD | $1,178.7M |
| Base case ECL | $73.4M (6.22% of EAD) |
| Adverse scenario ECL | $95.6M (+$22.3M uplift) |
| Optimistic scenario ECL | $60.3M |
| Stage mix (1 / 2 / 3) | 97.1% / 1.3% / 1.5% |

Backtesting (NB06) - all four regulatory tests passed:
- Kupiec test: p = 0.7935
- Basel Traffic Light: GREEN (0.32% deviation)
- Calibration error: 0.0080
- Out-of-time PSI (2007–2016 train vs 2017–2018 test): 0.0466 (stable)

## Pipeline

| Notebook | What it does |
|---|---|
| `01_eda_and_cleaning` | Stratified sampling by year down to 122,216 loans, drops "Current" loans, engineers `debt_burden` and `log_annual_inc` |
| `02_pd_model` | WoE encoding, IV-based feature selection, Gradient Boosting + Platt Scaling calibration |
| `03_lgd_model` | GB regression trained on defaulted loans only, applied portfolio-wide |
| `04_ead_model` | EAD-at-default model: observed on defaulters, segmented by term x grade (99.5% of observed EAD reproduced) |
| `05_ecl_calculation` | Combines PD × LGD × EAD, applies IFRS 9 staging and macro overlays |
| `06_backtesting` | Kupiec, Traffic Light, calibration, and PSI stability tests |

## Live Dashboard

The engine outputs are deployed as a live six-page Streamlit app hosted on Streamlit Community Cloud: **[View the live dashboard here](https://ifrs9-ecl-engine-sahilmehta.streamlit.app)** _(if it's been idle, give it ~30 seconds to wake up)_

- **Overview** - portfolio-level ECL summary
- **Loan Sandbox** - plug in a hypothetical loan and see its ECL, IFRS 9 stage and risk flag in real time
- **Portfolio** - segment-level breakdowns
- **Model Performance** - PD/LGD diagnostics, calibration curves
- **Backtesting** - the four regulatory tests, visualised
- **Export Report** - CSV export for offline review

Built with a dark fintech theme (Sora + DM Mono), custom CSS, and Plotly for charts.

## Tech stack

Python, scikit-learn (Gradient Boosting, WoE/IV pipelines), Platt Scaling for calibration, Streamlit + Plotly for the dashboard, joblib for model persistence, pandas for the data pipeline.

## Repo structure
```text
ifrs9-ecl-engine/
├── notebooks/        # the six-notebook pipeline above
├── src/              # saved models (pd_model.pkl, lgd_model.pkl, scaler.pkl, etc.)
├── dashboard/        # Streamlit app (app.py + pages/)
├── reports/          # generated charts, summary CSVs
└── data/             # processed prediction CSVs for the live app

## Limitations & next steps

- **Staging is a proxy.** True SICR compares PD at the reporting date with PD at origination; this resolved-loan sample only has origination PD. Stage 2 uses a relative test (lifetime PD at least 2x the grade average), and Stage 3 uses a days-past-due backstop (31-120 days late or in default at the 31-Dec-2018 snapshot). Stage 1 uses 12-month PD derived from lifetime PD under a constant-hazard assumption.
- **The Loan Sandbox is a simplified calculator.** It uses grade-level PD/LGD lookups rather than the trained models.
- **v2 (planned):** apply the PD, LGD and EAD models to the live book (loans still outstanding at 31-Dec-2018), with staging from days past due and EAD from the actual outstanding balance.
