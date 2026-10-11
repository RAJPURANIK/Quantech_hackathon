import numpy as np, pandas as pd
def validate_weights(holdings, tolerance=.0001):
    total=sum(h["weight"] if isinstance(h,dict) else h.weight for h in holdings); problems=[]
    if abs(total-1)>tolerance: problems.append(f"Weights sum to {total:.4f}, not 1.0000")
    if any((h["weight"] if isinstance(h,dict) else h.weight)<0 for h in holdings): problems.append("Long-only portfolio cannot include negative weights")
    return problems
def equal_weight(symbols): return {s:1/len(symbols) for s in symbols}
def hrp(returns:pd.DataFrame):
    try:
        from pypfopt.hierarchical_portfolio import HRPOpt
        return {k:float(v) for k,v in HRPOpt(returns=returns.dropna()).optimize().items()}
    except Exception:
        # inverse-volatility is an explicit transparent fallback when HRP dependency/data fails
        iv=1/returns.std().replace(0,np.nan); w=iv/iv.sum(); return {k:float(v) for k,v in w.fillna(1/len(w)).items()}
