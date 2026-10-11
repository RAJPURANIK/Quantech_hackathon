"""Risk metrics use 252 trading days/year. Returns are positive for gains; drawdowns/VaR losses are reported as positive magnitudes."""
import numpy as np, pandas as pd
ANNUALIZATION=252
def returns(prices): return prices.pct_change().dropna(how="all")
def max_drawdown(r):
    wealth=(1+r).cumprod(); return float((-((wealth/wealth.cummax())-1).min()))
def _cvar(r, q=.05):
    var=float(-np.quantile(r,q)); return float(-r[r<=np.quantile(r,q)].mean()) if (r<=np.quantile(r,q)).any() else var
def risk_metrics(portfolio_returns, benchmark_returns=None, weights=None, asset_returns=None):
    r=pd.Series(portfolio_returns).dropna(); ann_ret=float((1+r).prod()**(ANNUALIZATION/len(r))-1) if len(r) else 0.; vol=float(r.std(ddof=1)*np.sqrt(ANNUALIZATION)) if len(r)>1 else 0.
    downside=r[r<0].std(ddof=1)*np.sqrt(ANNUALIZATION) if (r<0).sum()>1 else 0
    mdd=max_drawdown(r); out={"annual_return":ann_ret,"annual_volatility":vol,"sharpe":ann_ret/vol if vol else 0.,"sortino":ann_ret/downside if downside else 0.,"calmar":ann_ret/mdd if mdd else 0.,"max_drawdown":mdd,"historical_var_95":float(-np.quantile(r,.05)) if len(r) else 0.,"historical_cvar_95":_cvar(r),"parametric_var_95":float(-(r.mean()-1.645*r.std(ddof=1))) if len(r)>1 else 0.,"parametric_cvar_95":float(-(r.mean()-2.063*r.std(ddof=1))) if len(r)>1 else 0.}
    if benchmark_returns is not None:
        b=pd.Series(benchmark_returns).reindex(r.index).dropna(); rr=r.reindex(b.index)
        beta=float(np.cov(rr,b,ddof=1)[0,1]/np.var(b,ddof=1)) if len(b)>1 and np.var(b)>0 else 0.; active=rr-b
        out.update(beta=beta,alpha=float((rr.mean()-beta*b.mean())*ANNUALIZATION),tracking_error=float(active.std(ddof=1)*np.sqrt(ANNUALIZATION)) if len(active)>1 else 0.,information_ratio=float(active.mean()*ANNUALIZATION/(active.std(ddof=1)*np.sqrt(ANNUALIZATION))) if active.std(ddof=1)>0 else 0.,up_capture=float(rr[b>0].mean()/b[b>0].mean()) if (b>0).any() else 0.,down_capture=float(rr[b<0].mean()/b[b<0].mean()) if (b<0).any() else 0.)
    if weights is not None:
        w=np.asarray(weights); out["hhi"] = float(np.square(w).sum())
    if asset_returns is not None and weights is not None:
        cov=asset_returns.cov().values*ANNUALIZATION; w=np.asarray(weights); total=float(np.sqrt(w@cov@w)); out["risk_contributions"]=(w*(cov@w)/total).tolist() if total else [0.]*len(w); out["correlation"]=asset_returns.corr().round(4).to_dict()
    return out
