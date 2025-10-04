# Technical Requirements Document (TRD)

## 1) Objective
Build a small Python Flask web app that accepts a stock ticker and returns a “Cash Cow” fundamental report featuring:
- Piotroski F‑Score (0–9)
- Value Investor Score (0–100)
- Growth Investor Score (0–100)
- Brief company bio
- Links to company homepage and recent Reuters/AP articles

Use a local **Ollama** instance for selective LLM tasks and **CrewAI** agents to orchestrate data gathering, scoring, and summarization. The app must be simple to deploy on a single host.

---

## 2) Scope
**In scope**
- One-page input UI and results UI
- REST API to produce machine‑readable JSON
- Data collection from at least one fundamentals API provider and company metadata source
- News discovery from Reuters/AP (links only)
- CrewAI orchestration across agents
- Local LLM calls through Ollama HTTP API
- Caching, basic observability, tests
- **PDF export of the rendered report**

**Out of scope**
- User auth or multitenancy
- Portfolio storage
- Paid newsroom licensing or paywall bypassing

---

## 3) Key Outputs
### 3.1 Report JSON schema
```json
{
  "ticker": "string",
  "asOf": "YYYY-MM-DD",
  "company": {
    "name": "string",
    "exchange": "string",
    "industry": "string",
    "sector": "string",
    "homepage": "https://..."
  },
  "scores": {
    "piotroskiF": 0,
    "valueInvestor": 0,
    "growthInvestor": 0
  },
  "explain": {
    "piotroski": "string",
    "value": "string",
    "growth": "string",
    "cashCow": "string"
  },
  "fundamentals": {
    "period": "ttm|annual|quarterly",
    "currency": "USD",
    "ttm": { "revenue": 0, "netIncome": 0, "operatingCashFlow": 0, "freeCashFlow": 0, "capex": 0, "ebit": 0, "totalAssets": 0, "currentAssets": 0, "currentLiabilities": 0, "longTermDebt": 0, "sharesDiluted": 0 },
    "ratios": { "pe": 0, "pb": 0, "evEbit": 0, "fcfYield": 0, "roa": 0, "roe": 0, "grossMargin": 0, "operatingMargin": 0 }
  },
  "news": [ { "title": "string", "source": "Reuters|AP", "publishedAt": "ISO-8601", "url": "https://..." } ]
}
```

### 3.2 UI
- Single search box for ticker
- Result cards: F‑Score, Value Score, Growth Score, Cash Cow summary, company bio
- Small news list (top 5)

---

## 4) Scoring Specs
### 4.1 Piotroski F‑Score (0–9)
Annual data unless only TTM available. One point each:
1. **Profitability**: Positive ROA; Positive CFO; ΔROA > 0; Accruals = CFO > NI
2. **Leverage/Liquidity**: ΔLeverage (long‑term debt/total assets) ≤ 0; ΔCurrent Ratio > 0; No new shares issued (ΔShares ≤ 0)
3. **Operating Efficiency**: ΔGross Margin > 0; ΔAsset Turnover > 0
Fallbacks: Use latest year vs prior year. If prior year missing, mark metric as **unknown** and exclude from denominator, then scale score to 0–9.

### 4.2 Value Investor Score (0–100)
Weighted composite of normalized factors with guardrails:
- **Valuation** 55%: PE, PB, EV/EBIT, FCF Yield (higher is better)
- **Quality** 25%: ROE, ROA, Gross Margin stability, Piotroski F‑Score
- **Risk** 20%: Leverage (Debt/Assets), Interest coverage, Share issuance trend
Normalization: Winsorize by sector deciles. Transform to 0–100 via min‑max within sector.

### 4.3 Growth Investor Score (0–100)
- **Growth** 60%: 3Y CAGR of Revenue, 3Y CAGR of EPS (or NI/share), OCF CAGR
- **Quality of growth** 25%: Margin expansion (gross and operating), ROIC trend
- **Durability** 15%: Net retention proxy (if SaaS data present) or revenue dispersion, Share dilution penalty
Scaling: Same sector‑relative min‑max to 0–100. If 3Y data insufficient, use 2Y and flag lower confidence.

### 4.4 “Cash Cow” Summary
Derived bullets produced by LLM from: FCF level and yield, OCF coverage of NI, Capex intensity, Working capital efficiency, Debt service coverage, Dividend safety (if applicable).

---

## 5) Data Sources
- **Fundamentals & Prices**: Pluggable adapter interface. Primary options: Financial Modeling Prep (FMP), Alpha Vantage, Polygon, or SEC EDGAR parsing. Start with FMP due to breadth.
- **Company profile**: Same provider or Clearbit/Crunchbase fallback (optional).
- **News Links**: Reuters and AP public RSS or search endpoints. Only link titles and URLs. No scraping behind paywalls.

Environment keys: `DATA_PROVIDER=fmp|alphavantage|polygon|edgar`, plus provider‑specific API keys.

---

## 6) Architecture
### 6.1 Overview
- Flask app provides Web + JSON API
- CrewAI manages **ResearchAgent**, **DataAgent**, **ScoringAgent**, **WriterAgent**
- Ollama runs local model(s) for summarization, explanation, and fallback reasoning
- Redis for cache; optional Celery for background jobs

### 6.2 Components
- **Flask**: routes, request validation, response serialization
- **Service layer**: `DataService`, `ScoreService`, `NewsService`, `LLMService`
- **Agents (CrewAI)**:
  - **ResearchAgent**: validates ticker, fetches profile, resolves homepage
  - **DataAgent**: pulls statements and ratios, computes derived fields
  - **ScoringAgent**: computes Piotroski and composite scores
  - **WriterAgent**: drafts bio and cash‑cow summary with strict token limits
- **Ollama**: `llama3` or `mistral` models
- **Cache**: `ticker+asOf` key, TTL 24h

### 6.3 Sequence (per request)
1. Flask receives ticker → validates format
2. CrewAI kickoff with shared memory
3. DataAgent gets fundamentals and price; NewsService gathers links
4. ScoringAgent computes F‑Score and investor scores
5. WriterAgent calls Ollama to produce short bio and explanations
6. Persist to cache → return JSON and render UI

---

## 7) Interfaces
### 7.1 HTTP Endpoints
- `GET /` → search UI
- `POST /analyze` body `{ "ticker": "AAPL" }` → HTML
- `GET /api/report/<ticker>` → JSON matching schema
- `GET /report/<ticker>.pdf` → PDF download of the same report
- `GET /health` → `{status: "ok"}`

### 7.2 Data Adapter Protocol
```python
class FundamentalsAdapter:
    def get_profile(self, ticker): ...  # name, exchange, sector, industry, homepage
    def get_prices(self, ticker): ...   # latest price, shares
    def get_financials(self, ticker): ...  # IS, BS, CF for last 5 years
    def get_ratios(self, ticker): ...  # pe, pb, ev_ebit, margins, leverage
```

### 7.3 Ollama Integration
- Host: `http://localhost:11434`
- Generate: `POST /api/generate` with `{"model":"llama3","prompt":"..."}`
- Use short prompts; temperature 0.2; max tokens 256 for summaries
- All prompts must be **deterministic** when `seed` is set

### 7.4 CrewAI Setup
- Define agents with tools bound to services
- Tasks: `collect_profile`, `collect_financials`, `compute_scores`, `write_bio_and_cash_cow`
- Use a single crew `TickerCrew` with shared context
- Hard timeout per request: 8s data, 2s LLM, overall 12s; return partial results if timeouts fire

---

## 8) Algorithms
### 8.1 Derived metrics
- **FCF** = OCF − Capex
- **FCF Yield** = FCF / MarketCap
- **Asset Turnover** = Revenue / Avg Total Assets
- **Leverage** = LT Debt / Total Assets
- **Current Ratio** = Current Assets / Current Liabilities
- **Accruals** test: CFO > NI → 1 else 0
- Year‑over‑year deltas computed on matching fiscal calendars

### 8.2 Missing Data Policy
- Per‑metric availability flags
- Scale Piotroski score by available metrics
- Mark Value/Growth confidence as `high|medium|low` based on data coverage

---

## 9) Validation & Testing
- Unit tests for: adapter math, Piotroski logic, normalization and scoring, prompt determinism
- Contract tests for `/api/report/:ticker` against schema
- Mock provider responses for CI

---

## 10) Performance & Reliability
- Cache all successful reports for 24h
- Circuit breaker and retries on provider calls
- Request time budget as in §7.4
- Log structured events; add `/health` and `/metrics` (Prometheus optional)

---

## 11) Security & Compliance
- Do not store API keys in repo
- Respect provider ToS; link to articles rather than scraping content
- Input sanitation for ticker and HTTP params
- CORS disabled by default

---

## 12) Deployment
- Python 3.11, Flask 3.x
- `pip install flask pydantic requests cachetools redis crewai pydantic-settings tenacity weasyprint`
- System packages for WeasyPrint (Dockerfile): `apt-get install -y libpango-1.0-0 libcairo2 libjpeg-turbo8 libpng16-16 libffi8` (package names may vary by distro)
- Optional: Dockerfile and docker‑compose with `ollama`, `web`, `redis`

### 12.1 Env Vars
```
FLASK_ENV=production
DATA_PROVIDER=fmp
FMP_API_KEY=...
OLLAMA_HOST=http://localhost:11434
CACHE_URL=redis://redis:6379/0
NEWS_SOURCES=reuters,ap
MODEL_NAME=llama3
SECTOR_NORMALIZATION=true
```

---

## 13) Prompts (LLM via Ollama)
**Company bio** (keep to 70–90 words):
```
Write a neutral 80‑word company bio for {ticker} using this structured data:
{name}, {exchange}, {industry}, {sector}, founded {founded?}, HQ {hq?}.
Do not speculate. If data missing, omit it. No adjectives. Return plain text only.
```

**Cash Cow bullets** (4–6 bullets max):
```
Summarize free‑cash‑flow strength for {ticker} using:
FCF {fcf}, FCF Yield {fcf_yield}%, OCF {ocf}, Capex {capex},
NI {ni}, Debt/Assets {lev}, Interest coverage {icov}, Dividend {div?}.
Use terse bullets. No hype. No forward guidance.
```

---

## 14) UI Notes
- Minimal responsive Bootstrap or Tailwind
- Cards for scores; badges for confidence
- Table for key ratios; small news list with source and time
- **Download PDF** button that links to `/report/<ticker>.pdf`

---

## 15) Skeleton Project Layout
```
app/
  __init__.py
  main.py                # Flask factory
  routes.py              # /, /analyze, /api/report, /report/<ticker>.pdf
  services/
    data_adapter.py
    data_service.py
    news_service.py
    score_service.py
    llm_service.py
  agents/
    crew.py
    research_agent.py
    data_agent.py
    scoring_agent.py
    writer_agent.py
  models/
    report.py            # Pydantic schema
  templates/
    index.html
    report.html          # screen view
    report_pdf.html      # print-optimized HTML for PDF
  static/
    styles.css

tests/
  test_piotroski.py
  test_scores.py
  test_api_contract.py

Dockerfile
docker-compose.yml
README.md
```

---

## 16) Acceptance Criteria
- For a valid ticker, `/api/report/<ticker>` returns JSON within 2–5 seconds under warm cache
- F‑Score matches manual calculation for test fixtures
- Value and Growth scores compute on at least 70% of S&P 500 tickers with medium+ confidence
- UI shows scores, bio, cash‑cow bullets, and ≥3 Reuters/AP links when available
- **`/report/<ticker>.pdf` generates a PDF matching the HTML content layout within 3 seconds under warm cache**

---

## 17) Risks
- API coverage gaps for smaller tickers
- Sector normalization limited by provider universes
- Reuters/AP feed availability variability

---

## 18) Future Work
- Multi‑ticker compare view
- CSV export
- Alternative models via Ollama registry
- Optional auth and user notes
- Branded PDF header/footer themes

---

## 19) PDF Export Design
**Renderer**: WeasyPrint renders `report_pdf.html` to PDF. Use print CSS for pagination and page headers.

**Route**: `/report/<ticker>.pdf` resolves the cached JSON. It renders `report_pdf.html` with the same data used by `report.html` and streams the PDF with `application/pdf` and `Content-Disposition: attachment`.

**Print CSS**:
- `@page` to set margins and footer page numbers
- Avoid heavy color blocks; prefer monochrome tables
- Ensure links show full URLs via `a[href]::after{ content: " (" attr(href) ")"; }` for print clarity

**Error handling**:
- If report not cached, build synchronously using the same path as HTML
- On data gaps, include a "Data coverage" appendix page

**Testing**:
- Golden-file snapshot of a known ticker PDF
- Content presence checks: titles, all three scores, bio, top 3 news items, timestamp

