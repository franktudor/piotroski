from pydantic import BaseModel, Field
from typing import List, Optional

class Company(BaseModel):
    name: str
    exchange: str
    industry: str
    sector: str
    homepage: str

class Scores(BaseModel):
    piotroskiF: int
    valueInvestor: int
    growthInvestor: int

class Explain(BaseModel):
    piotroski: str
    value: str
    growth: str
    cashCow: str

class FundamentalsTTM(BaseModel):
    revenue: float
    netIncome: float
    operatingCashFlow: float
    freeCashFlow: float
    capex: float
    ebit: float
    totalAssets: float
    currentAssets: float
    currentLiabilities: float
    longTermDebt: float
    sharesDiluted: float

class Ratios(BaseModel):
    pe: float
    pb: float
    evEbit: float
    fcfYield: float
    roa: float
    roe: float
    grossMargin: float
    operatingMargin: float

class Fundamentals(BaseModel):
    period: str
    currency: str
    ttm: FundamentalsTTM
    ratios: Ratios

class News(BaseModel):
    title: str
    source: str
    publishedAt: str
    url: str

class Report(BaseModel):
    ticker: str
    asOf: str
    company: Company
    scores: Scores
    explain: Explain
    fundamentals: Fundamentals
    news: List[News]