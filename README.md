# IFRS 9 Expected Credit Loss (ECL) Engine

An end-to-end credit risk pipeline that estimates Expected Credit Loss under IFRS 9, built on LendingClub's 2007–2018 loan data. This started as an M.Tech project but ended up being a full attempt at replicating how a bank's risk team would actually model, calibrate, and stress-test provisioning numbers — from raw loan tapes all the way to a dashboard a risk analyst could use day to day.

## What it does

Given a portfolio of loans, the engine predicts three components of credit loss and combines them:

**ECL = PD × LGD × EAD**

- **PD (Probability of Default)** — a calibrated Gradient Boosting model, trained with Weight-of-Evidence encoded features selected using Information Value
- **LGD (Loss Given Default)** — a regression model trained only on the ~26.7K loans that actually defaulted, then applied across the full portfolio
- **EAD (Exposure at Default)** — a hybrid approach: outstanding principal for active loans, an amortisation formula for closed ones, and zero for loans paid in full

The result gets staged under IFRS 9 (Stage 1/2/3 based on PD thresholds), stress-tested under macro scenarios, and backtested against four regulatory benchmarks.

## Results

| Metric | Value |
|---|---|
| PD model AUC | 0.7115 |
| Gini coefficient | 0.4230 |
| KS statistic | 0.3046 |
| Calibration gap (post Platt Scaling) | 23.80% → 0.07% |
| LGD model RMSE / R² | 0.2007 / 0.1914 |
| Portfolio EAD | $145.3M |
| Base case ECL | $23.7M |
| Adverse scenario ECL | $30.8M (+$7.1M uplift) |
| Optimistic scenario ECL | $19.0M |

Backtesting (NB06) — all four regulatory tests passed:
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
| `04_ead_model` | Hybrid amortisation logic across active/closed/paid-off loans |
| `05_ecl_calculation` | Combines PD × LGD × EAD, applies IFRS 9 staging and macro overlays |
| `06_backtesting` | Kupiec, Traffic Light, calibration, and PSI stability tests |

## Dashboard

A six-page Streamlit app for exploring the model outputs interactively:
- **Overview** — portfolio-level ECL summary
- **Loan Sandbox** — plug in a hypothetical loan and see its ECL and Basel Traffic Light status in real time
- **Portfolio** — segment-level breakdowns
- **Model Performance** — PD/LGD diagnostics, calibration curves
- **Backtesting** — the four regulatory tests, visualised
- **Export Report** — CSV export for offline review

Built with a dark fintech theme (Sora + DM Mono), custom CSS, and Plotly for charts.

## Tech stack

Python, scikit-learn (Gradient Boosting, WoE/IV pipelines), Platt Scaling for calibration, Streamlit + Plotly for the dashboard, joblib for model persistence, pandas for the data pipeline.

## Repo structure
ifrs9-ecl-engine/
├── notebooks/       # the six-notebook pipeline above
├── src/             # saved models (pd_model.pkl, lgd_model.pkl, scaler.pkl, etc.)
├── dashboard/        # Streamlit app (app.py + pages/)
├── reports/          # generated charts, summary CSVs
└── data/             # NOT tracked in git — see below

## Reproducing this

The raw dataset and all derived CSVs are excluded from this repo (they're large and fully regenerable). To reproduce:

1. Download the LendingClub 2007–2018 accepted loans dataset
2. Place it at `data/accepted_2007_to_2018q4.csv`
3. Run the notebooks in order, 01 through 06 — each one writes its outputs to `data/` for the next notebook to pick up
4. Launch the dashboard with `streamlit run dashboard/app.py`

## Known issues / next steps

A few things I've flagged in code review that are still pending:

- **NB01**: `credit_history_years` should be pinned to a fixed reference date (2018-12-31) rather than computed relative to run-time, for reproducibility
- **NB02**: an unused `FrozenEstimator` import needs removing
- **NB04**: the amortisation calculation currently loops row-by-row — should be vectorised for performance on larger portfolios
- **NB06**: `pd_bucket` assignment should use `pd.qcut` for cleaner quantile-based bucketing

None of these affect the current results, but they're the next things I'd clean up before treating this as production-ready.

## Why I built this

Targeting risk analyst roles, I wanted something that went past a Kaggle-style PD model and actually replicated the full IFRS 9 lifecycle a bank goes through — PD, LGD, EAD, staging, macro overlays, and the backtesting a regulator would actually check. It's also the reason the repo includes things like calibration diagnostics and PSI stability tests, not just a model with a good AUC
