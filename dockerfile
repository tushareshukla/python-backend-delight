# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y wget gnupg ca-certificates && \
    apt-get install -y libnss3 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 libx11-xcb1 libxss1 libgtk-3-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install --with-deps

# Copy project files
COPY . .

# Expose the port FastAPI runs on
EXPOSE 3000

# Run the app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
