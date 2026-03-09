FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

CMD gunicorn app:app --threads 4 --timeout 300 --bind 0.0.0.0:$PORT
