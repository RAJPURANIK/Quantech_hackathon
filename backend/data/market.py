"""Market data adapter. Demo data is a bundled illustrative sample and always labelled."""
from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parent
CACHE=ROOT / "cache"; CACHE.mkdir(exist_ok=True)
DEMO=ROOT / "demo" / "demo_prices.csv"

def validate_prices(prices: pd.DataFrame) -> list[str]:
    issues=[]
    if prices.index.duplicated().any(): issues.append("duplicate dates")
    if prices.isna().any().any(): issues.append("missing prices")
    rets=prices.pct_change()
    if (rets.abs()>0.25).any().any(): issues.append("daily outlier above 25%")
    if len(prices) and (pd.Timestamp.now().tz_localize(None)-pd.Timestamp(prices.index.max()).tz_localize(None)).days>7: issues.append("stale prices")
    return issues

def _demo(symbols):
    df=pd.read_csv(DEMO,parse_dates=["date"]).set_index("date")
    # Use benchmark proxy only when a requested instrument is unavailable in the intentionally small bundled sample.
    for s in symbols:
        if s not in df: df[s]=df["^NSEI"] * (1 + (abs(hash(s)) % 7) / 1000)
    return df[symbols], True, ["Bundled DEMO DATA: illustrative, not live market prices"]

def get_prices(symbols:list[str], period="2y"):
    symbols=list(dict.fromkeys(symbols)); key="_".join(s.replace("^", "IDX") for s in symbols)+".csv"; cached=CACHE/key
    if cached.exists():
        try:
            df=pd.read_csv(cached,parse_dates=["date"]).set_index("date")
            if not validate_prices(df): return df, False, []
        except Exception: pass
    try:
        import yfinance as yf
        raw=yf.download(symbols, period=period, auto_adjust=True, progress=False, threads=True)
        prices=(raw["Close"] if isinstance(raw.columns,pd.MultiIndex) else raw[["Close"]].rename(columns={"Close":symbols[0]})).dropna(how="all")
        prices=prices.reindex(columns=symbols).ffill(limit=3).dropna()
        issues=validate_prices(prices)
        if len(prices)<30 or issues: raise ValueError(", ".join(issues) or "insufficient price history")
        prices.reset_index(names="date").to_csv(cached,index=False)
        return prices, False, []
    except Exception as exc:
        df,demo,warnings=_demo(symbols); return df,demo,warnings+[f"Live data unavailable ({type(exc).__name__}); using DEMO DATA."]
