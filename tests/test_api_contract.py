import unittest
from unittest.mock import patch
from app.main import create_app
from app.models.report import Report
import json

class TestApiContract(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.mock_report_data = {
            "ticker": "TEST",
            "asOf": "2023-01-01",
            "company": {
                "name": "Test Inc",
                "exchange": "NYSE",
                "industry": "Tech",
                "sector": "Software",
                "homepage": "http://test.com"
            },
            "scores": {
                "piotroskiF": 5,
                "valueInvestor": 50,
                "growthInvestor": 50
            },
            "explain": {
                "piotroski": "Bio text.",
                "value": "Value text.",
                "growth": "Growth text.",
                "cashCow": "Cash cow text."
            },
            "fundamentals": {
                "period": "ttm",
                "currency": "USD",
                "ttm": {
                    "revenue": 1e9, "netIncome": 1e8, "operatingCashFlow": 2e8,
                    "freeCashFlow": 1.5e8, "capex": 5e7, "ebit": 2.5e8,
                    "totalAssets": 2e9, "currentAssets": 1e9, "currentLiabilities": 5e8,
                    "longTermDebt": 3e8, "sharesDiluted": 1e8
                },
                "ratios": {
                    "pe": 20.0, "pb": 2.0, "evEbit": 15.0, "fcfYield": 0.05,
                    "roa": 0.05, "roe": 0.1, "grossMargin": 0.6, "operatingMargin": 0.25
                }
            },
            "news": [
                {"title": "Test News 1", "source": "Reuters", "publishedAt": "2023-01-01T12:00:00Z", "url": "http://news.com/1"}
            ]
        }

    @patch('app.routes._generate_report_data')
    def test_api_report_contract(self, mock_generate_data):
        """Test that the /api/report/<ticker> endpoint returns a valid Report object."""
        mock_generate_data.return_value = self.mock_report_data

        response = self.client.get('/api/report/TEST')
        self.assertEqual(response.status_code, 200)

        # Validate the response against the Pydantic model
        try:
            response_json = json.loads(response.data)
            Report(**response_json)
        except Exception as e:
            self.fail(f"API response did not match the Report model contract: {e}")

    @patch('app.routes._generate_report_data')
    def test_api_report_not_found(self, mock_generate_data):
        """Test the API's 404 response for an unknown ticker."""
        mock_generate_data.return_value = None

        response = self.client.get('/api/report/UNKNOWN')
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)

if __name__ == '__main__':
    unittest.main()