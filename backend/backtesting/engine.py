"""Rebalances at close using weights known before the next period; costs are deducted proportionally to turnover."""
import pandas as pd, numpy as np
def backtest(prices, weights, frequency="monthly", cost_bps=15):
    r=prices.pct_change().dropna(); w=pd.Series(weights).reindex(r.columns).fillna(0.); w=w/w.sum(); current=w.copy(); costs=[]; daily=[]
    periods=r.index.to_period("M" if frequency=="monthly" else "Q")
    for i,(date,row) in enumerate(r.iterrows()):
        # terminal date of each rebalance period: reset after that day's return, never before it
        gross=float((current*row).sum()); cost=0.
        if i>0 and periods[i]!=periods[i-1]:
            drifted=current*(1+row); drifted=drifted/drifted.sum(); turnover=float((drifted-w).abs().sum()/2); cost=turnover*cost_bps/10000; current=w.copy()
        else:
            current=current*(1+row); current=current/current.sum()
        daily.append(gross-cost); costs.append(cost)
    series=pd.Series(daily,index=r.index); return {"returns":series,"wealth":(1+series).cumprod(),"total_cost":float(sum(costs)),"costs":costs}
