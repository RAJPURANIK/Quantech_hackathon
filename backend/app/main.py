from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PortfolioRequest, AllocationRequest, BacktestRequest
from data.market import get_prices
from analytics.metrics import returns, risk_metrics
from portfolio.allocations import validate_weights, equal_weight, hrp
from backtesting.engine import backtest
from governance.policy import check_policy
from simulation.monte_carlo import simulate
from portfolio.min_variance import min_variance
from models.risk import assess
from stress.scenarios import stress
from pathlib import Path
import pandas as pd, yaml, io

app=FastAPI(title="Quantech API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])
ASSETS=yaml.safe_load((Path(__file__).parents[1]/"config"/"assets.yaml").read_text())["assets"]
DEMO=[{"symbol":"NIFTYBEES.NS","weight":.25},{"symbol":"HDFCBANK.NS","weight":.2},{"symbol":"RELIANCE.NS","weight":.2},{"symbol":"TCS.NS","weight":.15},{"symbol":"GOLDBEES.NS","weight":.1},{"symbol":"LIQUIDBEES.NS","weight":.1}]
def payload_data(symbols):
    prices,demo,warnings=get_prices(list(dict.fromkeys(symbols+["^NSEI"])))
    return prices,demo,warnings
def clean(obj):
    if isinstance(obj,dict): return {str(k):clean(v) for k,v in obj.items()}
    if isinstance(obj,list): return [clean(v) for v in obj]
    if hasattr(obj,"item"): return obj.item()
    return obj
def portfolio_returns(prices, holdings):
    w=pd.Series({h["symbol"]:h["weight"] for h in holdings}); p=prices.reindex(columns=w.index).ffill().dropna(); return returns(p).mul(w,axis=1).sum(axis=1), returns(p),w
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.get("/api/universe")
def universe(): return {"assets":ASSETS}
@app.get("/api/demo-portfolio")
def demo_portfolio(): return {"holdings":DEMO,"demo":True,"message":"Bundled illustrative demo portfolio"}
@app.post("/api/portfolio/validate")
async def validate(request:Request):
    content_type=request.headers.get("content-type","")
    try:
        if "multipart/form-data" in content_type:
            form=await request.form(); file=form.get("file")
            if not file: raise ValueError("Provide CSV file under 'file'")
            raw=await file.read()
            if len(raw)>1_000_000: raise ValueError("CSV is too large")
            df=pd.read_csv(io.BytesIO(raw))
            if set(df.columns)!={"symbol","weight"}: raise ValueError("CSV must contain exactly symbol,weight columns")
            df["symbol"]=df.symbol.astype(str).str.strip(); df["weight"]=pd.to_numeric(df.weight,errors="raise")
            holdings=df.to_dict("records")
        else: holdings=(await request.json()).get("holdings",[])
        req=PortfolioRequest(holdings=holdings); hs=[x.model_dump() for x in req.holdings]; issues=validate_weights(hs)
        known={a["symbol"] for a in ASSETS}; unknown=[h["symbol"] for h in hs if h["symbol"] not in known]
        return {"valid":not issues and not unknown,"holdings":hs,"issues":issues+([f"Unknown instruments: {', '.join(unknown)}"] if unknown else [])}
    except Exception as e: raise HTTPException(422,detail=str(e))
@app.post("/api/risk/metrics")
def risk(req:PortfolioRequest):
    hs=[h.model_dump() for h in req.holdings]; prices,demo,warnings=payload_data([h["symbol"] for h in hs]); pr,ar,w=portfolio_returns(prices,hs); benchmark=returns(prices["^NSEI"]).reindex(pr.index)
    return clean({"metrics":risk_metrics(pr,benchmark,w.values,ar),"demo":demo,"warnings":warnings,"dates":[str(x.date()) for x in pr.index]})
@app.post("/api/allocation/recommend")
def recommend(req:AllocationRequest):
    hs=[h.model_dump() for h in req.holdings]; prices,demo,warnings=payload_data([h["symbol"] for h in hs]); ar=returns(prices[[h["symbol"] for h in hs]]).dropna()
    if req.method=="min_variance":
        result=min_variance(ar,{h["symbol"]:h["weight"] for h in hs},req.profile); weights=result["weights"]
        return {"method":req.method,"weights":weights,"demo":demo,"warnings":warnings,"fallback":result["fallback"],"status":result["status"]}
    weights=equal_weight(ar.columns) if req.method=="equal_weight" else hrp(ar)
    return {"method":req.method,"weights":weights,"demo":demo,"warnings":warnings,"fallback":False}
@app.post("/api/simulation/monte-carlo")
def monte_carlo(req:PortfolioRequest, model:str="normal", goal:float=.10):
    hs=[h.model_dump() for h in req.holdings]; prices,demo,warnings=payload_data([h["symbol"] for h in hs]); _,ar,w=portfolio_returns(prices,hs)
    return {**simulate(ar,w.values,model=model,goal=goal),"demo":demo,"warnings":warnings}
@app.post("/api/insights")
def insights(req:PortfolioRequest):
    hs=[h.model_dump() for h in req.holdings]; prices,demo,warnings=payload_data([h["symbol"] for h in hs]); pr,ar,w=portfolio_returns(prices,hs); m=risk_metrics(pr,returns(prices["^NSEI"]),w.values,ar)
    text=[]
    if m["max_drawdown"]>.1:text.append(f"Historical maximum drawdown is {m['max_drawdown']:.1%}, which warrants liquidity planning.")
    if m["hhi"]>.25:text.append("Concentration is elevated (HHI above 0.25); diversification may reduce single-name risk.")
    if not text:text.append("Current concentration and historical drawdown do not trigger this prototype's deterministic flags.")
    return {"insights":text,"model_assessment":assess(pr),"demo":demo,"warnings":warnings}
@app.post("/api/stress")
def stress_test(req:PortfolioRequest):
    hs=[h.model_dump() for h in req.holdings]; prices,demo,warnings=payload_data([h["symbol"] for h in hs]); pr,_,_=portfolio_returns(prices,hs); return {**stress({h["symbol"]:h["weight"] for h in hs},pr),"demo":demo,"warnings":warnings}
@app.post("/api/backtest")
def do_backtest(req:BacktestRequest):
    hs=[h.model_dump() for h in req.holdings]; recommended=[h.model_dump() for h in req.recommended] if req.recommended else None
    symbols=[h["symbol"] for h in hs]+([h["symbol"] for h in recommended] if recommended else [])
    prices,demo,warnings=payload_data(symbols); p=prices.drop(columns="^NSEI"); original={h["symbol"]:h["weight"] for h in hs}; ew=equal_weight(original.keys()); rec={h["symbol"]:h["weight"] for h in recommended} if recommended else hrp(returns(p[list(original)]).dropna())
    outputs={"Original":backtest(p,original,req.frequency,req.cost_bps),"Recommended":backtest(p,rec,req.frequency,req.cost_bps),"Equal-weight":backtest(p,ew,req.frequency,req.cost_bps),"NIFTY 50":backtest(prices[["^NSEI"]],{"^NSEI":1},req.frequency,0)}
    return clean({"demo":demo,"warnings":warnings,"series":{n:{"dates":[str(x.date()) for x in x["wealth"].index],"wealth":x["wealth"].tolist(),"returns":x["returns"].tolist(),"total_cost":x["total_cost"]} for n,x in outputs.items()}})
@app.post("/api/governance/check")
def governance(req:PortfolioRequest):
    hs=[h.model_dump() for h in req.holdings]; _,demo,warnings=payload_data([h["symbol"] for h in hs]); result=check_policy(hs,warnings); return {**result,"demo":demo,"data_warnings":warnings}
