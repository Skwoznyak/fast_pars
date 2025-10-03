# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Chromium и ChromeDriver из репозиториев Debian
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Создаём директорию для cookies и Excel файлов
RUN mkdir -p /app/data

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем приложение
# Render использует переменную окружения PORT
# Используем shell форму CMD для подстановки переменных
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
