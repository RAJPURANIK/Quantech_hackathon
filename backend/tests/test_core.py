import pandas as pd, numpy as np
from analytics.metrics import returns, max_drawdown, risk_metrics
from portfolio.allocations import validate_weights, equal_weight
from backtesting.engine import backtest
from fastapi.testclient import TestClient
from app.main import app
from simulation.monte_carlo import simulate
def test_returns_and_drawdown():
    p=pd.Series([100,110,99]); r=returns(p); assert round(r.iloc[0],2)==.10; assert round(max_drawdown(r),2)==.10
def test_risk_metrics_var_and_sharpe():
    r=pd.Series([.01,-.02,.01,-.01]); m=risk_metrics(r); assert m["historical_var_95"]>0 and "sharpe" in m and m["historical_cvar_95"]>=m["historical_var_95"]
def test_weights_and_equal():
    assert validate_weights([{"weight":.5},{"weight":.4}]); assert sum(equal_weight(["a","b","c"]).values())==1
def test_cost_accounting():
    i=pd.date_range("2024-01-30",periods=5); p=pd.DataFrame({"a":[100,110,100,120,118],"b":[100,90,110,100,105]},index=i); result=backtest(p,{"a":.5,"b":.5},"monthly",15); assert result["total_cost"]>=0 and len(result["wealth"])==4
def test_api_smoke_and_csv():
    c=TestClient(app); assert c.get("/api/health").status_code==200; assert len(c.get("/api/universe").json()["assets"])>=15
    h=c.get("/api/demo-portfolio").json()["holdings"]; assert c.post("/api/risk/metrics",json={"holdings":h}).status_code==200
    r=c.post("/api/portfolio/validate",files={"file":("x.csv",b"symbol,weight\nNIFTYBEES.NS,1\n","text/csv")}); assert r.status_code==200 and r.json()["valid"]
def test_seeded_simulation_and_stage2_endpoints():
    rs=pd.DataFrame({"a":np.linspace(-.01,.01,50),"b":np.linspace(.01,-.01,50)}); assert simulate(rs,[.5,.5],paths=10)["seed"]==42
    c=TestClient(app); h=c.get("/api/demo-portfolio").json()["holdings"]; assert c.post("/api/simulation/monte-carlo",json={"holdings":h}).status_code==200; assert c.post("/api/insights",json={"holdings":h}).status_code==200; assert c.post("/api/stress",json={"holdings":h}).status_code==200
