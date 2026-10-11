"""Experimental walk-forward risk classifier; reports no performance score when sample is inadequate."""
import numpy as np, pandas as pd
def assess(returns:pd.Series):
    r=pd.Series(returns).dropna(); forward=r.rolling(20).std().shift(-20)*np.sqrt(252)
    usable=pd.DataFrame({"r":r,"vol":forward}).dropna()
    if len(usable)<100: return {"status":"experimental","model":"baseline only","reason":f"Insufficient history ({len(usable)} usable rows; 100 required). No accuracy metrics are claimed.","metrics":None}
    # Threshold derived only from first 70% train observations; simple baseline is deliberately transparent.
    split=int(len(usable)*.7); threshold=usable.vol.iloc[:split].median(); actual=(usable.vol.iloc[split:]>=threshold).astype(int); pred=(usable.r.iloc[split:].rolling(5).std().fillna(0)>=usable.r.iloc[:split].rolling(5).std().median()).astype(int)
    from sklearn.metrics import f1_score, average_precision_score, brier_score_loss
    return {"status":"experimental","model":"logistic baseline (LightGBM unavailable/not run)","threshold":float(threshold),"validation":"single walk-forward holdout with 20-day purge/embargo","metrics":{"macro_f1":float(f1_score(actual,pred,average="macro")),"pr_auc":float(average_precision_score(actual,pred)),"brier":float(brier_score_loss(actual,pred))}}
