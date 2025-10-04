import unittest
from app.services.score_service import ScoreService

class TestPiotroskiScore(unittest.TestCase):

    def setUp(self):
        self.score_service = ScoreService()
        self.mock_financials_good = {
            'income_statement': [
                {'netIncome': 100, 'grossProfitRatio': 0.5, 'revenue': 1000}, # latest
                {'netIncome': 80, 'grossProfitRatio': 0.4, 'revenue': 900}   # prior
            ],
            'balance_sheet': [
                {'totalAssets': 1000, 'longTermDebt': 100, 'totalCurrentAssets': 500, 'totalCurrentLiabilities': 200, 'commonStock': 100}, # latest
                {'totalAssets': 950, 'longTermDebt': 120, 'totalCurrentAssets': 450, 'totalCurrentLiabilities': 250, 'commonStock': 100}  # prior
            ],
            'cash_flow_statement': [
                {'operatingCashFlow': 120}, # latest
                {'operatingCashFlow': 110}  # prior
            ]
        }
        self.mock_financials_bad = {
            'income_statement': [
                {'netIncome': -50, 'grossProfitRatio': 0.3, 'revenue': 800}, # latest
                {'netIncome': 80, 'grossProfitRatio': 0.4, 'revenue': 900}   # prior
            ],
            'balance_sheet': [
                {'totalAssets': 1000, 'longTermDebt': 150, 'totalCurrentAssets': 400, 'totalCurrentLiabilities': 300, 'commonStock': 110}, # latest
                {'totalAssets': 950, 'longTermDebt': 120, 'totalCurrentAssets': 450, 'totalCurrentLiabilities': 250, 'commonStock': 100}  # prior
            ],
            'cash_flow_statement': [
                # Set CFO to be less than Net Income to fail the accruals test
                {'operatingCashFlow': -60}, # latest
                {'operatingCashFlow': 110}  # prior
            ]
        }

    def test_piotroski_perfect_score(self):
        """Test a scenario where all 9 criteria are met."""
        score, metrics = self.score_service.calculate_piotroski_f_score(self.mock_financials_good)
        self.assertEqual(score, 9)
        self.assertEqual(metrics['positive_roa'], 1)
        self.assertEqual(metrics['positive_cfo'], 1)
        self.assertEqual(metrics['delta_roa'], 1)
        self.assertEqual(metrics['accruals'], 1)
        self.assertEqual(metrics['delta_leverage'], 1)
        self.assertEqual(metrics['delta_current_ratio'], 1)
        self.assertEqual(metrics['no_new_shares'], 1)
        self.assertEqual(metrics['delta_gross_margin'], 1)
        self.assertEqual(metrics['delta_asset_turnover'], 1)

    def test_piotroski_zero_score(self):
        """Test a scenario where none of the 9 criteria are met."""
        score, metrics = self.score_service.calculate_piotroski_f_score(self.mock_financials_bad)
        self.assertEqual(score, 0)
        self.assertEqual(metrics['positive_roa'], 0)
        self.assertEqual(metrics['positive_cfo'], 0)
        self.assertEqual(metrics['delta_roa'], 0)
        self.assertEqual(metrics['accruals'], 0)
        self.assertEqual(metrics['delta_leverage'], 0)
        self.assertEqual(metrics['delta_current_ratio'], 0)
        self.assertEqual(metrics['no_new_shares'], 0)
        self.assertEqual(metrics['delta_gross_margin'], 0)
        self.assertEqual(metrics['delta_asset_turnover'], 0)

    def test_insufficient_data(self):
        """Test that the function handles insufficient data gracefully."""
        insufficient_data = {'income_statement': [{}]}
        score, metrics = self.score_service.calculate_piotroski_f_score(insufficient_data)
        self.assertEqual(score, 0)
        self.assertIn('error', metrics)

if __name__ == '__main__':
    unittest.main()