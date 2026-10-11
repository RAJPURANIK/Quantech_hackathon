# Quantech

FastAPI + React portfolio research prototype for Indian instruments. It is for research and education only, not financial advice, and makes no SEBI claims.

## Run

Backend (PowerShell):

```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

Frontend (a second PowerShell):

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. For a production compile, run `npm run build` in `frontend`. Test the backend with `cd backend; py -m pytest -q`.

## Delivered

- Stage 1: FastAPI endpoints, 18-instrument Indian universe, cached yfinance adapter with validation and explicit bundled demo-data fallback, portfolio validation/CSV upload, metrics, equal-weight/HRP allocation, no-look-ahead backtest, policy checks, React navigation and six working pages.
- Stage 2: seeded normal/Student-t Monte Carlo, Ledoit-Wolf/cvxpy minimum-variance allocation with fallback, experimental risk classifier safeguards, and Monte Carlo / Explainable Insights pages.
- Stage 3: backend stress endpoint with transparent hypothetical shocks. Dynamic risk adjustment and an optional LLM layer are intentionally not implemented.

## Assumptions and limitations

- The supplied `QUANTECH_SPEC.md` was not present, so the user message was used as the authoritative specification.
- Annualization is 252 trading days. Positive returns are gains; drawdown and VaR/CVaR are positive loss magnitudes.
- The bundled demo CSV is illustrative and always returned with `demo: true`; it is never presented as live data. Its short history is unsuitable for real decisions and keeps the ML assessment experimental.
- Live yfinance data can be delayed, incomplete, or unavailable. Cache files remain local in `backend/data/cache`; user-entered holdings are not persisted.
- The frontend renders API output only and does not calculate financial metrics. No database or external service is required beyond optional yfinance access.
