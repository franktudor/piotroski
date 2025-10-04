# Piotroski Investor Scores App

This is a Python Flask web application that provides a "Cash Cow" fundamental report for a given stock ticker. The report includes the Piotroski F-Score, a Value Investor Score, a Growth Investor Score, a brief company bio, and links to recent news articles.

The application is built using CrewAI to orchestrate data gathering and analysis, and it leverages a local Ollama instance for LLM-based text generation.

## Features

-   **Piotroski F-Score (0-9):** A comprehensive score based on a company's profitability, leverage, and operating efficiency.
-   **Value & Growth Investor Scores (0-100):** Composite scores based on various financial metrics (placeholders in the current version).
-   **Company Profile:** A brief, AI-generated biography of the company.
-   **"Cash Cow" Summary:** An AI-generated summary of the company's free cash flow strength.
-   **Recent News:** Links to recent articles from public RSS feeds.
-   **REST API:** A JSON endpoint for programmatic access to the report data.
-   **PDF Export:** The ability to download the report as a PDF document.

## Getting Started

### Prerequisites

-   Docker and Docker Compose
-   An API key from [Financial Modeling Prep (FMP)](https://site.financialmodelingprep.com/developer/docs).

### Installation and Running

1.  **Clone the repository:**
    ```sh
    git clone <repository_url>
    cd piotroski-investor-scores-app
    ```

2.  **Create an environment file:**
    Create a file named `.env` in the project root and add your FMP API key:
    ```
    FMP_API_KEY=your_fmp_api_key_here
    ```

3.  **Build and run the application using Docker Compose:**
    ```sh
    docker-compose up --build
    ```
    This command will build the Flask application container, pull the Redis and Ollama images, and start all the services. The web application will be available at `http://localhost:8000`.

4.  **Pull the LLM model:**
    Once the Ollama container is running, you'll need to pull the language model specified in `docker-compose.yml` (default is `llama3`).
    ```sh
    docker-compose exec ollama ollama pull llama3
    ```

## Usage

### Web Interface

-   Open your web browser and navigate to `http://localhost:8000`.
-   Enter a stock ticker (e.g., `AAPL`) in the input field and click "Analyze".
-   The application will display the full report. From the report page, you can download a PDF version.

### API Endpoint

The application provides a REST API for accessing the report data in JSON format.

-   **Endpoint:** `GET /api/report/<ticker>`
-   **Example:** `http://localhost:8000/api/report/AAPL`

The API will return a JSON object that conforms to the schema defined in `app/models/report.py`.

### Running Tests

To run the test suite, use the provided shell script, which sets the correct `PYTHONPATH`:
```sh
./run_tests.sh
```

## Project Structure
```
app/
  __init__.py
  main.py                # Flask factory
  routes.py              # /, /analyze, /api/report, /report/<ticker>.pdf
  services/
    data_adapter.py
    fmp_adapter.py
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
requirements.txt
run_tests.sh
```