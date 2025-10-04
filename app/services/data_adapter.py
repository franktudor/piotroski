class FundamentalsAdapter:
    def get_profile(self, ticker):
        raise NotImplementedError

    def get_prices(self, ticker):
        raise NotImplementedError

    def get_financials(self, ticker):
        raise NotImplementedError

    def get_ratios(self, ticker):
        raise NotImplementedError