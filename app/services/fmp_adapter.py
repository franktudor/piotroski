import os
import requests
from app.services.data_adapter import FundamentalsAdapter

class FMPAdapter(FundamentalsAdapter):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP_API_KEY is required for the FMPAdapter.")
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def _get(self, path: str, params: dict = None) -> list | dict:
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from FMP: {e}")
            return {} # Return empty dict on error

    def get_profile(self, ticker: str) -> dict:
        data = self._get(f"/profile/{ticker}")
        if not data or not isinstance(data, list):
            return {}
        profile = data[0]
        return {
            "name": profile.get("companyName"),
            "exchange": profile.get("exchangeShortName"),
            "industry": profile.get("industry"),
            "sector": profile.get("sector"),
            "homepage": profile.get("website"),
        }

    def get_financials(self, ticker: str) -> dict:
        # Fetch annual statements for the last 5 years
        income_statement = self._get(f"/income-statement/{ticker}", {"limit": 5, "period": "annual"})
        balance_sheet = self._get(f"/balance-sheet-statement/{ticker}", {"limit": 5, "period": "annual"})
        cash_flow = self._get(f"/cash-flow-statement/{ticker}", {"limit": 5, "period": "annual"})

        return {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow_statement": cash_flow
        }

    def get_ratios(self, ticker: str) -> dict:
        # Fetch TTM ratios
        ratios_ttm = self._get(f"/ratios-ttm/{ticker}")
        if not ratios_ttm or not isinstance(ratios_ttm, list):
            return {}
        return ratios_ttm[0]

    def get_prices(self, ticker: str) -> dict:
        price_data = self._get(f"/quote/{ticker}")
        if not price_data or not isinstance(price_data, list):
            return {}
        return price_data[0]