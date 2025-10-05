# Use Debian bookworm for stable WeasyPrint deps
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libjpeg62-turbo \
    libffi8 \
    fonts-dejavu-core \
    shared-mime-info \
  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Flask port
EXPOSE 8000

# Env
ENV FLASK_APP=app.main:create_app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=8000 \
    PYTHONPATH=/app

# Run the app
CMD ["flask", "run"]
