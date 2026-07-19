FROM python:3.13-slim

# Install system dependencies: Tesseract OCR + build tools
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV TESSERACT_CMD=/usr/bin/tesseract

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /app/uploads

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
