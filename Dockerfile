# Python tabanı
FROM python:3.11-slim

# Daha temiz log ve cache'siz pip
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Çalışma klasörü
WORKDIR /app

# Önce sadece gereksinimleri kopyala ve kur
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Sonra TÜM kodu kopyala (main.py kesin gelir)
COPY . /app

# Port ve başlatma
ENV PORT=8000
EXPOSE 8000
CMD ["python", "main.py"]
