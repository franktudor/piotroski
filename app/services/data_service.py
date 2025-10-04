import datetime
from app.services.data_adapter import FundamentalsAdapter
from app.models.report import Report, Company, Scores, Explain, Fundamentals, FundamentalsTTM, Ratios, News

class DataService:
    def __init__(self, adapter: FundamentalsAdapter):
        self.adapter = adapter

    def get_full_report_data(self, ticker: str) -> dict:
        """
        Orchestrates calls to the adapter to fetch all necessary data
        and assemble it into a dictionary matching the Report model structure.
        """
        profile = self.adapter.get_profile(ticker)
        if not profile:
            return None # Ticker not found or error

        financials = self.adapter.get_financials(ticker)
        ratios = self.adapter.get_ratios(ticker)
        price_data = self.adapter.get_prices(ticker)

        # For now, we will use placeholder data for scores and explanations,
        # as the ScoreService and LLMService will fill these in later.

        # This is a simplified mapping. A more robust implementation
        # would handle missing data more gracefully.
        latest_is = financials.get('income_statement', [{}])[0]
        latest_bs = financials.get('balance_sheet', [{}])[0]
        latest_cf = financials.get('cash_flow_statement', [{}])[0]

        # Derived FCF for simplicity, real logic will be in ScoreService
        ocf = latest_cf.get('operatingCashFlow', 0)
        capex = latest_cf.get('capitalExpenditure', 0)
        fcf = ocf - capex

        market_cap = price_data.get('marketCap', 0)
        fcf_yield = (fcf / market_cap) * 100 if market_cap else 0

        report_data = {
            "ticker": ticker.upper(),
            "asOf": datetime.date.today().isoformat(),
            "company": {
                "name": profile.get("name"),
                "exchange": profile.get("exchange"),
                "industry": profile.get("industry"),
                "sector": profile.get("sector"),
                "homepage": profile.get("homepage"),
            },
            "scores": { # Placeholder
                "piotroskiF": 0,
                "valueInvestor": 0,
                "growthInvestor": 0,
            },
            "explain": { # Placeholder
                "piotroski": "",
                "value": "",
                "growth": "",
                "cashCow": "",
            },
            "fundamentals": {
                "period": "ttm",
                "currency": "USD", # Assuming USD for now
                "ttm": {
                    "revenue": latest_is.get('revenue', 0),
                    "netIncome": latest_is.get('netIncome', 0),
                    "operatingCashFlow": ocf,
                    "freeCashFlow": fcf,
                    "capex": capex,
                    "ebit": latest_is.get('ebitda', 0) - latest_is.get('depreciationAndAmortization', 0), # EBIT approx.
                    "totalAssets": latest_bs.get('totalAssets', 0),
                    "currentAssets": latest_bs.get('totalCurrentAssets', 0),
                    "currentLiabilities": latest_bs.get('totalCurrentLiabilities', 0),
                    "longTermDebt": latest_bs.get('longTermDebt', 0),
                    "sharesDiluted": price_data.get('sharesOutstanding', 0), # Using sharesOutstanding as proxy
                },
                "ratios": {
                    "pe": ratios.get('peRatioTTM', 0),
                    "pb": ratios.get('priceToBookRatioTTM', 0),
                    "evEbit": ratios.get('enterpriseValueOverEBITDATTM', 0), # Using EV/EBITDA as proxy
                    "fcfYield": fcf_yield,
                    "roa": ratios.get('returnOnAssetsTTM', 0),
                    "roe": ratios.get('returnOnEquityTTM', 0),
                    "grossMargin": ratios.get('grossProfitMarginTTM', 0),
                    "operatingMargin": ratios.get('operatingIncomeRatioTTM', 0),
                },
            },
            "news": [], # Placeholder, to be filled by NewsService
            "raw_financials": financials # Pass raw data for scoring service
        }

        return report_data