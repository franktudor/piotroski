class ScoreService:
    def calculate_piotroski_f_score(self, financials: dict) -> tuple[int, dict]:
        """
        Calculates the Piotroski F-Score based on the provided financial statements.
        Returns a tuple containing the score and a dictionary of the individual metric scores.
        """
        score = 0
        metrics = {}

        # Ensure we have at least two years of data for comparison
        if len(financials.get('income_statement', [])) < 2 or \
           len(financials.get('balance_sheet', [])) < 2 or \
           len(financials.get('cash_flow_statement', [])) < 2:
            return 0, {"error": "Insufficient data for Piotroski F-Score calculation."}

        latest_is = financials['income_statement'][0]
        prior_is = financials['income_statement'][1]
        latest_bs = financials['balance_sheet'][0]
        prior_bs = financials['balance_sheet'][1]
        latest_cf = financials['cash_flow_statement'][0]
        prior_cf = financials['cash_flow_statement'][1]

        # 1. Profitability
        # Positive ROA
        net_income = latest_is.get('netIncome', 0)
        total_assets = latest_bs.get('totalAssets', 0)
        roa = net_income / total_assets if total_assets else 0
        metrics['positive_roa'] = 1 if roa > 0 else 0
        score += metrics['positive_roa']

        # Positive CFO
        cfo = latest_cf.get('operatingCashFlow', 0)
        metrics['positive_cfo'] = 1 if cfo > 0 else 0
        score += metrics['positive_cfo']

        # Change in ROA > 0
        prior_net_income = prior_is.get('netIncome', 0)
        prior_total_assets = prior_bs.get('totalAssets', 0)
        prior_roa = prior_net_income / prior_total_assets if prior_total_assets else 0
        metrics['delta_roa'] = 1 if roa > prior_roa else 0
        score += metrics['delta_roa']

        # Accruals (CFO > NI)
        metrics['accruals'] = 1 if cfo > net_income else 0
        score += metrics['accruals']

        # 2. Leverage/Liquidity
        # Change in Leverage <= 0
        leverage = latest_bs.get('longTermDebt', 0) / total_assets if total_assets else 0
        prior_leverage = prior_bs.get('longTermDebt', 0) / prior_total_assets if prior_total_assets else 0
        metrics['delta_leverage'] = 1 if leverage <= prior_leverage else 0
        score += metrics['delta_leverage']

        # Change in Current Ratio > 0
        current_assets = latest_bs.get('totalCurrentAssets', 0)
        current_liabilities = latest_bs.get('totalCurrentLiabilities', 1)
        current_ratio = current_assets / current_liabilities if current_liabilities else 0
        prior_current_assets = prior_bs.get('totalCurrentAssets', 0)
        prior_current_liabilities = prior_bs.get('totalCurrentLiabilities', 1)
        prior_current_ratio = prior_current_assets / prior_current_liabilities if prior_current_liabilities else 0
        metrics['delta_current_ratio'] = 1 if current_ratio > prior_current_ratio else 0
        score += metrics['delta_current_ratio']

        # No new shares issued
        shares_out = latest_bs.get('commonStock', 0)
        prior_shares_out = prior_bs.get('commonStock', 0)
        metrics['no_new_shares'] = 1 if shares_out <= prior_shares_out else 0
        score += metrics['no_new_shares']

        # 3. Operating Efficiency
        # Change in Gross Margin > 0
        gross_margin = latest_is.get('grossProfitRatio', 0)
        prior_gross_margin = prior_is.get('grossProfitRatio', 0)
        metrics['delta_gross_margin'] = 1 if gross_margin > prior_gross_margin else 0
        score += metrics['delta_gross_margin']

        # Change in Asset Turnover > 0
        revenue = latest_is.get('revenue', 0)
        asset_turnover = revenue / total_assets if total_assets else 0
        prior_revenue = prior_is.get('revenue', 0)
        prior_asset_turnover = prior_revenue / prior_total_assets if prior_total_assets else 0
        metrics['delta_asset_turnover'] = 1 if asset_turnover > prior_asset_turnover else 0
        score += metrics['delta_asset_turnover']

        return score, metrics

    def calculate_value_investor_score(self, financials, ratios):
        # Placeholder
        print("Calculating Value Investor Score")
        return 0, {}

    def calculate_growth_investor_score(self, financials, ratios):
        # Placeholder
        print("Calculating Growth Investor Score")
        return 0, {}