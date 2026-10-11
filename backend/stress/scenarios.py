def stress(weights, portfolio_returns=None):
    """Transparent hypothetical shocks; not forecasts."""
    w=dict(weights); equity=sum(v for k,v in w.items() if "GOLD" not in k and "LIQUID" not in k); gold=sum(v for k,v in w.items() if "GOLD" in k); debt=sum(v for k,v in w.items() if "LIQUID" in k)
    historical={"note":"Insufficient return history for a robust replay."}
    if portfolio_returns is not None and len(portfolio_returns)>=5:
        historical={"worst_5_day_return":float((1+portfolio_returns).rolling(5).apply(lambda x:x.prod()-1,raw=True).min()),"observations":len(portfolio_returns),"note":"Worst observed rolling five-trading-day return; descriptive, not a forecast."}
    return {"historical_replay":historical,"hypothetical":{"equity_-20%":-.20*equity+.08*gold+.01*debt,"rates_up_100bp":-.06*equity-.03*gold-.01*debt},"stressed_monte_carlo_note":"Student-t simulation is the fat-tail stressed Monte Carlo method; results remain illustrative."}
