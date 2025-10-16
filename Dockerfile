# ---- base image
FROM python:3.11-slim

# OS bağımlılıkları gerekiyorsa buraya eklenir (gerekmedikçe boş bırak)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Önce sadece requirements'ı kopyala ve kur (cache için iyi)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Uygulamayı kopyala
COPY backend /app/backend
COPY main.py /app/main.py

# Railway PORT'u enjekte eder; default olarak 8000 dursun
ENV PORT=8000

# Uygulamayı başlat
CMD ["python", "/app/main.py"]
