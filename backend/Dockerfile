# Python taban imaj
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Gereksinimleri yükle
# requirements.txt dosyan backend klasöründeyse bu satırlar doğru:
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY backend/ ./

# Railway/Render gibi ortamlarda PORT değişkeni verilir
ENV PORT=8000

# Uygulaman başlatma komutu:
# "main:app" kısmını kendi FastAPI/Flask giriş noktanla eşleştir:
#   - FastAPI için genelde main.py içinde "app" nesnesi vardır → "main:app"
#   - Flask kullanıyorsan "app.py" içindeki "app" → "app:app"
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
