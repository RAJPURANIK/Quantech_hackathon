# QUANTECH — Quantitative Finance & Portfolio Risk Intelligence

**An AI-assisted portfolio analytics and risk research platform for Indian investors.**

QUANTECH helps users explore portfolio risk, evaluate asset allocations, compare investment strategies against the NIFTY 50 benchmark, and examine hypothetical market stress scenarios through an interactive web dashboard.

> **Disclaimer:** QUANTECH is an educational and research prototype, not financial advice. It does not claim SEBI registration or provide guaranteed investment outcomes.

## Overview

Traditional investment analysis often focuses on individual stocks rather than the combined risk of an entire portfolio. QUANTECH takes a portfolio-level approach by combining quantitative finance, statistical risk metrics, portfolio allocation methods, historical backtesting, and experimental risk assessment.

The application uses a React frontend connected to a Python REST API. Financial calculations are performed by the backend, while the frontend displays results and visualizations.

## Key Features

- **Portfolio Management:** Load a demo portfolio, enter holdings manually, or upload a CSV file containing instrument symbols and portfolio weights.
- **Risk Intelligence:** Calculate portfolio performance and risk measures, including returns, volatility, Sharpe ratio, drawdown, beta, Value at Risk (VaR), and Conditional Value at Risk (CVaR).
- **Smart Allocation:** Generate equal-weight and Hierarchical Risk Parity (HRP) allocations, with a minimum-variance optimization option and fallback handling.
- **Backtesting Lab:** Compare Original, Recommended, Equal-weight, and NIFTY 50 strategies using historical data, periodic rebalancing, and transaction-cost assumptions.
- **Monte Carlo Simulator:** Explore seeded simulations using normal and Student-t return assumptions, with simulated outcome distributions and risk summaries.
- **Explainable Insights:** Display deterministic portfolio observations and a guarded, experimental model-based risk assessment.
- **Stress Testing:** Examine selected historical replay data and hypothetical market shocks.
- **Governance & Methodology:** Check portfolio constraints and data-quality warnings, and review the calculation methodology.
- **Market Data Handling:** Retrieve historical prices through yfinance, use a local cache, validate data, and explicitly label demo-data results.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Routing and UI | React Router, CSS |
| Charts | Plotly.js, react-plotly.js |
| Backend | Python, FastAPI, Uvicorn |
| Data processing | pandas, NumPy, PyYAML |
| Market data | yfinance, local CSV cache |
| Portfolio allocation | PyPortfolioOpt, SciPy, cvxpy where supported |
| Testing | pytest, HTTPX TestClient |

## Architecture

```text
QUANTECH
├── backend/
│   ├── app/            # FastAPI application and schemas
│   ├── analytics/      # Financial and risk metrics
│   ├── data/           # Market data, cache and demo data
│   ├── portfolio/      # Allocation and optimization
│   ├── backtesting/    # Strategy backtesting
│   ├── simulation/     # Monte Carlo simulation
│   ├── stress/         # Stress scenarios
│   ├── governance/     # Policy checks
│   ├── models/         # Experimental risk assessment
│   ├── config/         # Instrument universe
│   └── tests/          # Backend tests
└── frontend/
    └── src/
        ├── api/        # Backend API client
        ├── components/ # Reusable UI and charts
        ├── pages/      # Dashboard pages
        └── types/      # TypeScript types
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Node.js 20 or newer
- npm
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/RAJPURANIK/Quantech_hackathon.git
cd Quantech_hackathon
```

### 2. Set up the backend

Open a terminal in the project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Set up the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

### 4. Verify the backend

Visit `http://127.0.0.1:8000/api/health`. A successful response should contain:

```json
{"status":"ok"}
```

### 5. Run backend tests

From the `backend` directory:

```powershell
py -m pytest -q
```

To verify the production frontend build, run `npm run build` from the `frontend` directory.

## Main API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Backend health check |
| `GET /api/universe` | Available instruments |
| `GET /api/demo-portfolio` | Illustrative portfolio |
| `POST /api/portfolio/validate` | Validate portfolio holdings or CSV |
| `POST /api/risk/metrics` | Calculate portfolio risk metrics |
| `POST /api/allocation/recommend` | Generate allocation recommendations |
| `POST /api/backtest` | Compare historical strategies |
| `POST /api/simulation/monte-carlo` | Simulate possible portfolio outcomes |
| `POST /api/insights` | Generate deterministic insights and model assessment |
| `POST /api/stress` | Evaluate stress scenarios |
| `POST /api/governance/check` | Check portfolio policies |

## Methodology

- Daily simple returns are used for return calculations.
- Annualized statistics use 252 trading days where applicable.
- Backtesting uses periodic rebalancing and configurable proportional transaction costs.
- VaR and CVaR are expressed as loss magnitudes.
- Monte Carlo simulation uses fixed seeds for reproducibility.
- Data availability, demo-data status, and experimental model limitations should be considered when interpreting results.

## Current Limitations

- Live market data depends on the availability and quality of the external data provider.
- Bundled demo data is illustrative and must not be treated as verified live market data.
- Risk-model output is experimental and is not a validated investment prediction.
- Historical backtests and simulations do not guarantee future performance.
- Advanced features described in the project guide, including full LightGBM/SHAP explanations, counterfactual rebalancing, purged walk-forward validation, block-bootstrap simulation, market-regime modelling, a news-based GenAI layer, and dynamic risk adjustment, are not all implemented in the current version.
- Deployment to a public hosting provider is not included in the local setup instructions.

## Responsible Use

QUANTECH is intended for educational exploration of quantitative finance, portfolio risk, allocation techniques, and financial data analysis. Validate inputs and independently review outputs before using them in any real-world financial decision.

## Project

- **Name:** QUANTECH
- **Domain:** FinTech, Quantitative Finance, Portfolio Analytics
- **Frontend:** React + TypeScript
- **Backend:** Python + FastAPI
- **Repository:** https://github.com/RAJPURANIK/Quantech_hackathon
