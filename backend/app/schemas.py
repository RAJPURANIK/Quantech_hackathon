from pydantic import BaseModel, Field, field_validator
from typing import Literal

class Holding(BaseModel):
    symbol: str = Field(min_length=1, max_length=30)
    weight: float = Field(ge=0, le=1)

class PortfolioRequest(BaseModel):
    holdings: list[Holding] = Field(min_length=1, max_length=30)
    frequency: Literal["monthly", "quarterly"] = "monthly"
    cost_bps: float = Field(default=15, ge=0, le=500)
    @field_validator("holdings")
    @classmethod
    def unique_symbols(cls, v):
        if len({h.symbol.upper() for h in v}) != len(v): raise ValueError("Duplicate symbols are not allowed")
        return v

class AllocationRequest(PortfolioRequest):
    method: Literal["equal_weight", "hrp", "min_variance"] = "hrp"
    profile: Literal["Conservative", "Balanced", "Growth"] = "Balanced"

class BacktestRequest(PortfolioRequest):
    recommended: list[Holding] | None = None
