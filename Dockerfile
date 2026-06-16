FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY run.py .

# هر دو فرمان را با هم اجرا می‌کنیم
CMD ["sh", "-c", "python run.py & python -c \"from app import app; app.run(host='0.0.0.0', port=5000)\""]
