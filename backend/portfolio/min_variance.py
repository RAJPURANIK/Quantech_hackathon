import numpy as np, pandas as pd
from portfolio.allocations import equal_weight
def min_variance(returns:pd.DataFrame, current:dict, profile="Balanced"):
    """Ledoit-Wolf covariance, long-only cvxpy objective with a modest turnover penalty."""
    try:
        from sklearn.covariance import LedoitWolf
        import cvxpy as cp
        cols=list(returns.columns); cov=LedoitWolf().fit(returns).covariance_; n=len(cols); w=cp.Variable(n); old=np.array([current.get(c,0) for c in cols]); cap={"Conservative":.35,"Balanced":.5,"Growth":.7}[profile]
        prob=cp.Problem(cp.Minimize(cp.quad_form(w,cov)+.01*cp.norm1(w-old)),[cp.sum(w)==1,w>=0,w<=cap]); prob.solve(solver="CLARABEL")
        if w.value is None: raise ValueError(prob.status)
        return {"weights":dict(zip(cols,[float(x) for x in w.value])),"fallback":False,"status":prob.status}
    except Exception as exc: return {"weights":equal_weight(returns.columns),"fallback":True,"status":f"fallback: {type(exc).__name__}"}
