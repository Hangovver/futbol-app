FROM python:3.11-slim

# Sistem bağımlılıkları (gerekirse ekleyebiliriz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu
COPY . .

# Railway port değişkeni
ENV PORT=8000

# Uygulamayı başlat
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8000"]
