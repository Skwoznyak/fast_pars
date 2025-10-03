# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для Firefox и Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    # Зависимости для Firefox
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Firefox
RUN wget -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xjf firefox.tar.bz2 -C /opt \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && rm firefox.tar.bz2

# Устанавливаем GeckoDriver (драйвер для Firefox)
RUN GECKO_VERSION=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d '"' -f 4) \
    && wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz" \
    && tar -xzf geckodriver-${GECKO_VERSION}-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/geckodriver \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-${GECKO_VERSION}-linux64.tar.gz

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
