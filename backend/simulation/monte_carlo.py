"""Seeded Monte Carlo is illustrative and reproducible; inputs are historical daily returns."""
import numpy as np
def simulate(returns, weights, model="normal", days=252, paths=500, goal=.10, seed=42):
    r=returns.dropna(); w=np.asarray(weights); mu=r.mean().values; cov=r.cov().values; rng=np.random.default_rng(seed)
    z=rng.multivariate_normal(mu,cov,(paths,days))
    if model=="student_t": z=mu+(z-mu)*rng.chisquare(6,(paths,1,1))**-.5*np.sqrt(6/4)
    p=(z@w); wealth=np.cumprod(1+p,axis=1); terminal=wealth[:,-1]-1
    fan=np.quantile(wealth,[.05,.25,.5,.75,.95],axis=0).tolist()
    q=np.quantile(terminal,.05); return {"fan":fan,"var_95":float(-q),"cvar_95":float(-terminal[terminal<=q].mean()),"goal_probability":float((terminal>=goal).mean()),"days":days,"paths":paths,"seed":seed,"model":model}
