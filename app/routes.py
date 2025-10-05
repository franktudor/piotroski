from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.services.data_service import DataService
from app.services.fmp_adapter import FMPAdapter

bp = Blueprint('main', __name__)

# Initialize the adapter and the service
fmp_adapter = FMPAdapter()
data_service = DataService(adapter=fmp_adapter)

def _generate_report_data(ticker: str) -> dict | None:
    """
    Helper function to encapsulate data generation.
    This makes the routes cleaner and easier to test by mocking this function.
    """
    try:
        # Corrected the method name from get_data to get_full_report_data
        report_data = data_service.get_full_report_data(ticker)
        return report_data
    except Exception as e:
        # In a real app, you'd want to log this error.
        print(f"Error generating report data for {ticker}: {e}")
        return None

@bp.route('/', methods=['GET', 'POST'])
def index():
    """Renders the main page with the ticker submission form."""
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        if ticker:
            # Redirect to the HTML report page, not the API endpoint
            return redirect(url_for('main.report', ticker=ticker))
    return render_template('index.html')

@bp.route('/report/<ticker>')
def report(ticker):
    """Renders the HTML report for a given ticker."""
    report_data = _generate_report_data(ticker)
    if report_data:
        return render_template('report.html', report=report_data)
    else:
        return render_template('error.html', error=f"Could not generate a report for ticker: {ticker}")

@bp.route('/api/report/<ticker>', methods=['GET'])
def api_report(ticker):
    """API endpoint that returns the full report data as JSON."""
    report_data = _generate_report_data(ticker)
    if report_data:
        return jsonify(report_data)
    else:
        return jsonify({"error": f"Data for ticker '{ticker}' not found."}), 404