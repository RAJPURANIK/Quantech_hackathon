import yaml
from pathlib import Path
def check_policy(holdings, data_warnings=None, max_single=.30, max_sector=.45):
    assets=yaml.safe_load((Path(__file__).parents[1]/"config"/"assets.yaml").read_text())["assets"]; lookup={a["symbol"]:a for a in assets}; warnings=[]; total=sum(h["weight"] for h in holdings)
    if abs(total-1)>.0001: warnings.append({"level":"error","message":f"Weights total {total:.2%}; rebalance to 100%."})
    sectors={}
    for h in holdings:
        if h["weight"]<0: warnings.append({"level":"error","message":f"{h['symbol']} is short; only long positions are permitted."})
        if h["weight"]>max_single: warnings.append({"level":"warning","message":f"{h['symbol']} is {h['weight']:.1%}; reduce below {max_single:.0%}."})
        sector=lookup.get(h["symbol"],{}).get("sector","Unknown"); sectors[sector]=sectors.get(sector,0)+h["weight"]
    for sec,w in sectors.items():
        if w>max_sector: warnings.append({"level":"warning","message":f"{sec} is {w:.1%}; diversify below {max_sector:.0%}."})
    for issue in data_warnings or []:
        if "stale" in issue.lower(): warnings.append({"level":"warning","message":"Price data is stale; refresh before acting."})
    return {"pass":not any(x["level"]=="error" for x in warnings),"warnings":warnings,"sector_weights":sectors}
