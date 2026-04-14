FROM python:3.10-slim
WORKDIR /app
# Системные зависимости для сборки некоторых библиотек
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn
COPY . .
# Сборка статики
RUN python manage.py collectstatic --noinput
